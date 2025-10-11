# python中ThreadPoolExecutor运行原理解析


`ThreadPoolExecutor` 是 `Python` 中用于创建和管理线程池的类，它基于 `concurrent.futures` 模块。下面我们通过分析源码来介绍其运行原理。

```python
# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Implements ThreadPoolExecutor."""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

from concurrent.futures import _base
import itertools
import queue
import threading
import types
import weakref
import os


_threads_queues = weakref.WeakKeyDictionary()
_shutdown = False
# Lock that ensures that new workers are not created while the interpreter is
# shutting down. Must be held while mutating _threads_queues and _shutdown.
_global_shutdown_lock = threading.Lock()

def _python_exit():
    global _shutdown
    with _global_shutdown_lock:
        _shutdown = True
    items = list(_threads_queues.items())
    for t, q in items:
        q.put(None)
    for t, q in items:
        t.join()

# Register for `_python_exit()` to be called just before joining all
# non-daemon threads. This is used instead of `atexit.register()` for
# compatibility with subinterpreters, which no longer support daemon threads.
# See bpo-39812 for context.
threading._register_atexit(_python_exit)

# At fork, reinitialize the `_global_shutdown_lock` lock in the child process
if hasattr(os, 'register_at_fork'):
    os.register_at_fork(before=_global_shutdown_lock.acquire,
                        after_in_child=_global_shutdown_lock._at_fork_reinit,
                        after_in_parent=_global_shutdown_lock.release)


class _WorkItem(object):
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return

        try:
            result = self.fn(*self.args, **self.kwargs)
        except BaseException as exc:
            self.future.set_exception(exc)
            # Break a reference cycle with the exception 'exc'
            self = None
        else:
            self.future.set_result(result)

    __class_getitem__ = classmethod(types.GenericAlias)


def _worker(executor_reference, work_queue, initializer, initargs):
    if initializer is not None:
        try:
            initializer(*initargs)
        except BaseException:
            _base.LOGGER.critical('Exception in initializer:', exc_info=True)
            executor = executor_reference()
            if executor is not None:
                executor._initializer_failed()
            return
    try:
        while True:
            work_item = work_queue.get(block=True)
            if work_item is not None:
                work_item.run()
                # Delete references to object. See issue16284
                del work_item

                # attempt to increment idle count
                executor = executor_reference()
                if executor is not None:
                    executor._idle_semaphore.release()
                del executor
                continue

            executor = executor_reference()
            # Exit if:
            #   - The interpreter is shutting down OR
            #   - The executor that owns the worker has been collected OR
            #   - The executor that owns the worker has been shutdown.
            if _shutdown or executor is None or executor._shutdown:
                # Flag the executor as shutting down as early as possible if it
                # is not gc-ed yet.
                if executor is not None:
                    executor._shutdown = True
                # Notice other workers
                work_queue.put(None)
                return
            del executor
    except BaseException:
        _base.LOGGER.critical('Exception in worker', exc_info=True)


class BrokenThreadPool(_base.BrokenExecutor):
    """
    Raised when a worker thread in a ThreadPoolExecutor failed initializing.
    """


class ThreadPoolExecutor(_base.Executor):

    # Used to assign unique thread names when thread_name_prefix is not supplied.
    _counter = itertools.count().__next__

    def __init__(self, max_workers=None, thread_name_prefix='',
                 initializer=None, initargs=()):
        """Initializes a new ThreadPoolExecutor instance.

        Args:
            max_workers: The maximum number of threads that can be used to
                execute the given calls.
            thread_name_prefix: An optional name prefix to give our threads.
            initializer: A callable used to initialize worker threads.
            initargs: A tuple of arguments to pass to the initializer.
        """
        if max_workers is None:
            # ThreadPoolExecutor is often used to:
            # * CPU bound task which releases GIL
            # * I/O bound task (which releases GIL, of course)
            #
            # We use cpu_count + 4 for both types of tasks.
            # But we limit it to 32 to avoid consuming surprisingly large resource
            # on many core machine.
            max_workers = min(32, (os.cpu_count() or 1) + 4)
        if max_workers <= 0:
            raise ValueError("max_workers must be greater than 0")

        if initializer is not None and not callable(initializer):
            raise TypeError("initializer must be a callable")

        self._max_workers = max_workers
        self._work_queue = queue.SimpleQueue()
        self._idle_semaphore = threading.Semaphore(0)
        self._threads = set()
        self._broken = False
        self._shutdown = False
        self._shutdown_lock = threading.Lock()
        self._thread_name_prefix = (thread_name_prefix or
                                    ("ThreadPoolExecutor-%d" % self._counter()))
        self._initializer = initializer
        self._initargs = initargs

    def submit(self, fn, /, *args, **kwargs):
        with self._shutdown_lock, _global_shutdown_lock:
            if self._broken:
                raise BrokenThreadPool(self._broken)

            if self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')
            if _shutdown:
                raise RuntimeError('cannot schedule new futures after '
                                   'interpreter shutdown')

            f = _base.Future()
            w = _WorkItem(f, fn, args, kwargs)

            self._work_queue.put(w)
            self._adjust_thread_count()
            return f
    submit.__doc__ = _base.Executor.submit.__doc__

    def _adjust_thread_count(self):
        # if idle threads are available, don't spin new threads
        if self._idle_semaphore.acquire(timeout=0):
            return

        # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        def weakref_cb(_, q=self._work_queue):
            q.put(None)

        num_threads = len(self._threads)
        if num_threads < self._max_workers:
            thread_name = '%s_%d' % (self._thread_name_prefix or self,
                                     num_threads)
            t = threading.Thread(name=thread_name, target=_worker,
                                 args=(weakref.ref(self, weakref_cb),
                                       self._work_queue,
                                       self._initializer,
                                       self._initargs))
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue

    def _initializer_failed(self):
        with self._shutdown_lock:
            self._broken = ('A thread initializer failed, the thread pool '
                            'is not usable anymore')
            # Drain work queue and mark pending futures failed
            while True:
                try:
                    work_item = self._work_queue.get_nowait()
                except queue.Empty:
                    break
                if work_item is not None:
                    work_item.future.set_exception(BrokenThreadPool(self._broken))

    def shutdown(self, wait=True, *, cancel_futures=False):
        with self._shutdown_lock:
            self._shutdown = True
            if cancel_futures:
                # Drain all work items from the queue, and then cancel their
                # associated futures.
                while True:
                    try:
                        work_item = self._work_queue.get_nowait()
                    except queue.Empty:
                        break
                    if work_item is not None:
                        work_item.future.cancel()

            # Send a wake-up to prevent threads calling
            # _work_queue.get(block=True) from permanently blocking.
            self._work_queue.put(None)
        if wait:
            for t in self._threads:
                t.join()
    shutdown.__doc__ = _base.Executor.shutdown.__doc__

```



通过分析 `ThreadPoolExecutor` 的源码，接下来详细介绍线程池的运行原理：

## 核心组件
### 1. 工作项 (`_WorkItem`)
`_WorkItem` 类：封装了要执行的任务，包括一个 Future 对象、可调用对象 `fn` 以及其参数 `args` 和 `kwargs`。当运行 `run` 方法时，会调用 `fn` 并设置 Future 的结果或异常。

```python
class _WorkItem(object):
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.future.set_result(result)
        except BaseException as exc:
            self.future.set_exception(exc)
```

### 2. 工作线程 (`_worker`)
`_worker` 函数：是工作线程的主函数（**<font style="color:#DF2A3F;">实现了线程复用的机制</font>**），它从工作队列中获取任务并执行。在`_worker`函数中，有一个while循环，这个循环会一直从工作队列中获取任务（`work_queue.get(block=True)`），然后执行任务（`work_item.run()`）。当一个任务执行完毕后，它会继续获取下一个任务，直到获取到`None`（退出信号）或者出现异常。

所以，线程池中的每个线程一旦被创建，就会在这个循环中不断执行任务，而不是执行一个任务就退出。这就是线程复用的原理。

```python
def _worker(executor_reference, work_queue, initializer, initargs):
    try:
        while True:  # ⭐️ 关键：无限循环！
            work_item = work_queue.get(block=True)  # 阻塞等待任务，线程在此阻塞，不消耗CPU，有新任务时自动唤醒
            if work_item is not None:
                work_item.run()  # 执行任务
                del work_item
                
                # 标记线程为空闲状态
                executor = executor_reference()
                if executor is not None:
                    executor._idle_semaphore.release()  # ⭐️ 空闲信号量+1
                del executor
                continue  # ⭐️ 继续循环，等待下一个任务
            
            # 收到退出信号时的处理
            executor = executor_reference()
            if _shutdown or executor is None or executor._shutdown:
                if executor is not None:
                    executor._shutdown = True
                work_queue.put(None)  # 通知其他worker
                return  # ⭐️ 只有这里才会退出循环，线程结束
            del executor
    except BaseException:
        _base.LOGGER.critical('Exception in worker', exc_info=True)
```

在`_worker`中，当一个任务执行完毕后，会调用`executor._idle_semaphore.release()`来增加信号量，表示有一个线程空闲了。而当提交任务时，在`_adjust_thread_count`中，会尝试获取信号量（即消耗一个空闲线程）来避免创建新线程。如果获取成功，说明有空闲线程，那么就不创建新线程，因为空闲线程会去处理队列中的任务。

所以，线程复用的机制可以总结为：

1. 工作线程被创建后，进入一个循环，不断从工作队列中取任务执行。
2. 当任务到达时，空闲线程（正在等待队列的线程）会获取到任务并执行。
3. 线程执行完任务后，不会退出，而是继续等待下一个任务，等待任务时不消耗CPU，避免了忙等待。
4. 通过信号量机制，线程池在提交任务时优先使用空闲线程，避免不必要的线程创建。

这样，线程池通过维护一定数量的线程，让它们重复使用来执行多个任务，从而避免了频繁创建和销毁线程的开销。

## 线程池运行原理
### 1. 初始化
初始化：创建 `ThreadPoolExecutor` 实例时，可以指定最大线程数 `max_workers`、线程名前缀 `thread_name_prefix`、初始化器 `initializer` 和初始化参数 `initargs`。如果没有指定 `max_workers`，则默认使用 `min(32, (os.cpu_count() or 1) + 4)`。

```python
def __init__(self, max_workers=None, thread_name_prefix='', initializer=None, initargs=()):
    # 自动计算最大线程数
    if max_workers is None:
        max_workers = min(32, (os.cpu_count() or 1) + 4)
    
    self._max_workers = max_workers
    self._work_queue = queue.SimpleQueue()  # 任务队列，无界先进先出队列
    self._idle_semaphore = threading.Semaphore(0)  # 空闲线程信号量，默认为0表示没有空闲线程，需要创建新线程
    self._threads = set()  # 工作线程集合
    self._shutdown = False
```

### 2. 任务提交流程
提交任务：当调用 `submit` 方法时，会创建一个 `_WorkItem` 对象，并将其放入工作队列 `_work_queue` 中。然后，调用 `_adjust_thread_count` 方法来调整线程数量。

```python
def submit(self, fn, /, *args, **kwargs):
    with self._shutdown_lock, _global_shutdown_lock:
        # 创建Future和工作项
        f = _base.Future()
        w = _WorkItem(f, fn, args, kwargs)
        
        self._work_queue.put(w)  # 任务入队
        self._adjust_thread_count()  # 调整线程数量
        return f
```

### 3. 动态线程管理
1. 线程创建：`_adjust_thread_count` 方法负责创建新的线程。它通过检查空闲信号量（`_idle_semaphore`）和当前线程数来决定是否创建新线程。如果没有空闲线程，并且当前线程数小于最大线程数，则创建新线程。
    - 空闲信号量：当一个线程完成一个任务后，会释放一个空闲信号量（在`_worker`函数中实现）。在获取新任务时，会先尝试获取空闲信号量，如果获取成功，则表示有空闲线程，不需要创建新线程。
2. 工作线程的主循环：在 `_worker` 函数中，线程不断从工作队列中获取任务。如果获取到 `None`，则退出循环。否则，执行任务的 `run` 方法。
    - 当线程获取到一个任务并执行后，会释放一个空闲信号量（通过 `executor._idle_semaphore.release()`）。
3. 线程的退出：当工作队列获取到 `None` 时，线程会检查退出条件（解释器关闭、Executor 被垃圾回收或 Executor 已关闭）。如果满足退出条件，则线程退出。

```python
def _adjust_thread_count(self):
    # 如果有空闲线程，不创建新线程
    if self._idle_semaphore.acquire(timeout=0):
        return
    
    # 创建新工作线程
    if len(self._threads) < self._max_workers:
        thread_name = '%s_%d' % (self._thread_name_prefix, num_threads)
        t = threading.Thread(name=thread_name, target=_worker,
                             args=(weakref.ref(self, weakref_cb),
                                   self._work_queue,
                                   self._initializer,
                                   self._initargs))
        t.start()
        self._threads.add(t)
        _threads_queues[t] = self._work_queue  # 全局注册
```

## 关键机制
### 1. 任务调度
+ 使用 `queue.SimpleQueue` 作为任务队列，线程安全
+ <font style="color:rgb(15, 17, 21);">所有线程共享同一个任务队列</font>
+ 工作线程阻塞在 `work_queue.get(block=True)` 等待任务，线程在队列空时处于休眠状态
+ 提交任务时立即返回 Future 对象

### 2. 线程生命周期管理
+ **懒加载**：线程在需要时创建，不超过 `max_workers`
+ **空闲管理**：通过信号量跟踪空闲线程
+ **优雅关闭**：向队列发送 `None` 作为退出信号

### 3. 资源清理
调用 `shutdown` 方法可以关闭线程池。它首先设置 `_shutdown` 为 `True`，然后根据 `cancel_futures` 参数决定是否取消队列中的任务。最后，向工作队列中放入与线程数量相同的 `None` 值，以唤醒所有线程并让它们退出。如果 `wait` 参数为 `True`，则等待所有线程结束。

```python
def shutdown(self, wait=True, *, cancel_futures=False):
    with self._shutdown_lock:
        self._shutdown = True
        if cancel_futures:
            # 取消未开始的任务
            while True:
                try:
                    work_item = self._work_queue.get_nowait()
                    if work_item is not None:
                        work_item.future.cancel()
                except queue.Empty:
                    break
        # 通知所有线程退出
        self._work_queue.put(None)
    if wait:
        for t in self._threads:
            t.join()  # 等待线程结束
```

### 4. 全局关闭协调
+ 使用 `_global_shutdown_lock` 来确保在解释器关闭时不会创建新的线程。
+ 通过 `threading._register_atexit` 注册 `_python_exit` 函数，在解释器退出时通知所有线程退出。

```python
def _python_exit():
    global _shutdown
    with _global_shutdown_lock:
        _shutdown = True
    items = list(_threads_queues.items())
    for t, q in items:
        q.put(None)
    for t, q in items:
        t.join()

# Register for `_python_exit()` to be called just before joining all
# non-daemon threads. This is used instead of `atexit.register()` for
# compatibility with subinterpreters, which no longer support daemon threads.
# See bpo-39812 for context.
threading._register_atexit(_python_exit)
```

### 5.异常处理
+ 如果线程初始化器（`initializer`）抛出异常，则线程池会被标记为损坏（`_broken`），并且所有等待中的任务都会收到 `BrokenThreadPool` 异常。
+ 工作线程中的异常会被捕获并记录，但不会影响其他线程。

## <font style="color:rgb(15, 17, 21);">实际执行流程示例</font>
<font style="color:rgb(15, 17, 21);">假设</font><font style="color:rgb(15, 17, 21);"> </font>`max_workers=2`<font style="color:rgb(15, 17, 21);">：</font>

1. **<font style="color:rgb(15, 17, 21);">提交第一个任务</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">→ 创建线程1 → 线程1开始执行任务</font>
2. **<font style="color:rgb(15, 17, 21);">提交第二个任务</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">→ 创建线程2 → 线程2开始执行任务</font>
3. **<font style="color:rgb(15, 17, 21);">提交第三个任务</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">→ 放入队列 → 线程1或2完成当前任务后从队列获取并执行</font>
4. **<font style="color:rgb(15, 17, 21);">持续提交任务</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">→ 线程1和线程2轮流从队列获取任务执行</font>
5. **<font style="color:rgb(15, 17, 21);">任务提交完毕</font>**<font style="color:rgb(15, 17, 21);"> → 线程1和线程2在 </font>`work_queue.get()`<font style="color:rgb(15, 17, 21);"> 处阻塞等待新任务</font>

## 工作流程总结
1. **提交任务** → 创建 Future 和 WorkItem → 任务入队
2. **线程管理** → 检查空闲线程 → 必要时创建新线程
3. **任务执行** → 工作线程获取任务 → 执行函数 → 设置 Future 结果
4. **资源回收** → 任务完成释放资源 → 空闲计数更新
5. **关闭过程** → 设置关闭标志 → 发送退出信号 → 等待线程结束

这种设计实现了高效的线程复用、动态资源管理和优雅的关闭机制。



## ThreadPoolExecutor使用的最佳实践
> **注意：由于GIL的存在，CPU密集型任务在Python中使用多线程并不会提高性能，因此ThreadPoolExecutor更适合I/O密集型任务。**
>



在Python中使用`ThreadPoolExecutor`时，遵循一些最佳实践可以确保代码高效、可靠且易于维护。以下是一些关键的最佳实践：

1. **使用上下文管理器（with语句）**：确保线程池在使用后正确关闭，即使发生异常也能正确清理资源。
2. **合理设置线程数量**：默认情况下，`ThreadPoolExecutor`会根据需要创建线程，但你可以通过`max_workers`参数控制最大线程数。根据任务类型（I/O密集型或CPU密集型）调整线程数。
3. **处理异常**：使用`Future`对象时，务必处理可能出现的异常，避免异常被忽略。
4. **避免长时间阻塞主线程**：使用`as_completed`或`wait`等方法来获取已完成的任务结果，避免不必要的等待。
5. **使用**`map`方法简化代码：当需要为多个参数调用同一个函数时，使用`map`方法可以简化代码（但注意map会按照输入顺序返回结果，而as_completed按照完成顺序返回）。
6. **注意任务之间的独立性**：确保提交的任务是相互独立的，避免竞争条件或依赖关系，否则可能需要使用锁机制，但这会增加复杂性并降低性能。
7. **使用`thread_name_prefix`进行调试**：为线程设置名称前缀，便于调试和日志记录。
8. **考虑使用**`initializer`和`initargs`：如果每个线程需要执行一些初始化操作（如设置数据库连接），可以使用初始器。
9. **避免在任务中修改全局状态**：尽量使任务函数无状态，使用线程局部变量来存储每个线程的状态，如果必须修改共享数据，使用适当的同步机制。
10. **谨慎使用**`shutdown`中的`cancel_futures`：在Python 3.9及以上版本，可以在关闭时取消所有未开始的任务，但要注意已经开始的任务会继续执行。

以下是使用`ThreadPoolExecutor`的最佳实践代码示例，详细演示了上述要点：

```python
import concurrent.futures
import threading
import time
import random

# 用于演示线程局部数据和初始化器
thread_local = threading.local()

def initializer_function(initial_data):
    """线程初始化器，每个线程启动时调用一次"""
    thread_local.counter = 0
    thread_local.initial_data = initial_data
    print(f"线程 {threading.current_thread().name} 初始化完成，初始数据: {initial_data}")

def io_bound_task(parameter):
    """
    模拟I/O密集型任务
    确保任务函数是线程安全的，或者使用适当的同步机制
    """
    try:
        # 使用线程局部数据
        thread_local.counter += 1

        # 模拟随机延迟（0.1-0.5秒）
        delay = random.uniform(0.1, 0.5)
        time.sleep(delay)

        # 模拟偶尔的异常
        if parameter % 7 == 0:  # 每7个任务模拟一个异常
            raise ValueError(f"参数 {parameter} 触发了模拟异常")

        # 模拟一些处理逻辑
        result = parameter * parameter
        thread_id = threading.current_thread().ident

        print(f"线程 {threading.current_thread().name} 处理参数 {parameter}, "
              f"局部计数器: {thread_local.counter}, 结果: {result}")

        return result

    except Exception as e:
        print(f"任务 {parameter} 执行失败: {e}")
        raise  # 重新抛出异常，让Future对象能够捕获

def process_completed_tasks(futures_dict):
    """处理已完成的任务，演示异常处理和结果收集"""
    completed_count = 0
    failed_count = 0

    for future in concurrent.futures.as_completed(futures_dict):
        parameter = futures_dict[future]

        try:
            result = future.result()
            print(f"任务完成: 参数 {parameter} -> 结果 {result}")
            completed_count += 1

        except Exception as e:
            print(f"任务失败: 参数 {parameter}, 错误: {e}")
            failed_count += 1

    return completed_count, failed_count

def demonstrate_thread_pool_best_practices():
    """演示ThreadPoolExecutor的最佳实践"""

    # 最佳实践1: 使用上下文管理器
    # 最佳实践2: 合理设置线程数量（这里设置为4，适合I/O密集型任务）
    # 最佳实践7: 设置线程名称前缀便于调试
    # 最佳实践8: 使用初始化器
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix="WorkerThread",
            initializer=initializer_function,
            initargs=("共享初始化数据",)
    ) as executor:

        print("=== 开始演示ThreadPoolExecutor最佳实践 ===\n")

        # 准备任务参数
        task_parameters = list(range(1, 21))  # 20个任务

        # 方法A: 使用submit提交单个任务
        print("1. 使用submit方法提交任务:")
        futures_dict = {}

        for param in task_parameters[:5]:  # 先提交5个任务演示
            future = executor.submit(io_bound_task, param)
            futures_dict[future] = param
            print(f"已提交任务: 参数 {param}")

        # 最佳实践4: 使用as_completed处理已完成任务
        print("\n2. 使用as_completed处理完成的任务:")
        completed, failed = process_completed_tasks(futures_dict)
        print(f"已完成: {completed}, 失败: {failed}")

        # 方法B: 使用map方法（最佳实践5）
        print("\n3. 使用map方法批量处理任务:")
        try:
            # map会保持输入顺序，但按完成顺序返回可能不是最优的
            results = list(executor.map(
                io_bound_task,
                task_parameters[5:15],  # 接下来的10个任务
                timeout=10  # 设置超时
            ))
            print(f"map方法成功处理 {len(results)} 个任务")

        except concurrent.futures.TimeoutError:
            print("任务执行超时!")
        except Exception as e:
            print(f"map执行过程中发生错误: {e}")

        # 方法C: 批量提交剩余任务
        print("\n4. 批量提交剩余任务并等待完成:")
        remaining_futures = {
            executor.submit(io_bound_task, param): param
            for param in task_parameters[15:]
        }

        completed, failed = process_completed_tasks(remaining_futures)
        print(f"最终统计 - 总计完成: {completed}, 失败: {failed}")

    print("\n=== 所有任务执行完成，线程池已自动关闭 ===")

def demonstrate_advanced_scenarios():
    """演示一些高级场景"""
    print("\n=== 高级场景演示 ===\n")

    # 场景：使用不同的异常处理策略
    def robust_task(x):
        try:
            if x % 3 == 0:
                raise RuntimeError(f"任务 {x} 的模拟错误")
            return x * 2
        except Exception as e:
            return f"错误: {e}"

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # 提交任务
        futures = [executor.submit(robust_task, i) for i in range(10)]

        # 收集结果，演示不同的异常处理方式
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=5)
                print(f"任务结果: {result}")
            except concurrent.futures.TimeoutError:
                print("任务超时")
            except Exception as e:
                print(f"任务执行异常: {e}")

if __name__ == "__main__":
    # 演示主要的最佳实践
    demonstrate_thread_pool_best_practices()

    # 演示高级场景
    demonstrate_advanced_scenarios()

    print("\n=== 所有演示完成 ===")
```



## <font style="color:rgb(15, 17, 21);">总结</font>
`ThreadPoolExecutor` 的线程复用是通过 **工作线程的无限循环 + 阻塞队列**实现的：

+ 线程不退出：工作线程创建后除非收到关闭信号，否则永不退出
+ 任务驱动：线程在队列处阻塞等待，有任务时才激活
+ 资源共享：所有线程共享同一个任务队列，实现负载均衡
+ 避免重复创建：通过信号量机制避免创建不必要的线程

`ThreadPoolExecutor` 通过**一个工作队列和一组工作线程**来实现线程池。任务被提交到工作队列，工作线程从队列中获取任务并执行。线程池根据任务数量动态调整线程数量，但不会超过最大线程数。当线程池关闭时，会通知所有线程退出，并可以根据需要取消未执行的任务。

这种设计使得 ThreadPoolExecutor 能够高效地管理线程并执行大量任务，同时避免了频繁创建和销毁线程的开销，实现了真正的线程复用。

