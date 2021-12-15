# python实现掘金定时签到抽奖

# 一. 概述

这里记录一下使用 python 实现掘金定时签到抽奖。首先需要登录掘金，进入签到页面，按 `F12` 打开浏览器的调试面板，选择 `Network`，选择 `XHR`，然后按 `F5` 刷新页面，找到 `check_in_rules` 这个请求，获取签到请求接口的参数就可以了，如下图所示的页面：

![image-20211117190339381](https://gitee.com/peterwd/pic-oss/raw/master/image/202111171903095.png)

从上图中需要获取如下几个参数的内容：

- aid
- uuid
- _signature
- cookie



# 二. python 代码实现

创建一个 `juejin.py` 文件，输入如下内容，并且输入前面获取到的内容：

```python
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import time


# 填写对应参数的值
data = {
    'aid': 'xxx',
    'uuid': 'xxx',
    '_signature': 'xxx',
    'cookie': 'xxx'
}

header = {
    "cookie": data.get('cookie')
}


def sign_in():
    """
    请求签到接口
    :return: 
    """
    url = 'https://api.juejin.cn/growth_api/v1/check_in'
    r = requests.post(url, data, headers=header)
    print(r.text)


def draw():
    """
    签到后抽奖
    :return: 
    """
    urlD = 'https://api.juejin.cn/growth_api/v1/lottery/draw'
    dataD = {
        'aid': data.get('aid'),
        'uuid': data.get('uuid'),
    }
    r = requests.post(urlD, dataD, headers=header)
    print(r.text)


def job():
    """
    启动任务
    :return: 
    """
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sign_in()
    time.sleep(10)
    draw()


if __name__ == "__main__":
    # 每天早上六点半签到
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'cron', day_of_week='0-6', hour=6, minute=30)
    scheduler.start()


```

这个脚本中用到了 `Python` 定时库 `apscheduler`，可以通过如下命令安装：

```sh
pip install apscheduler
```

通过如下命令启动 python 脚本即可：

```sh
python juejin.py
```

在 linux 服务器中可以通过 nohup 命令在后台启动，如下所示：

```sh
nohup python juejin.py &
```



