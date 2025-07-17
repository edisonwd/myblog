# Mockito的常见核心功能及最佳实践

Mockito 是一个流行的 Java 单元测试模拟框架，它的核心功能包括：**创建模拟对象、设置模拟行为、验证交互**。它能够帮助你在测试中隔离外部依赖，使得测试更加专注于被测试类的行为。以下是 Mockito 常见功能、注意事项和最佳实践：

## 一、核心功能概览
| **功能类别** | **关键方法** | **应用场景** | **示例** |
| --- | --- | --- | --- |
| **对象模拟** | `mock()`, `@Mock`, `@InjectMocks` | 创建外部依赖的模拟对象 | `List<String> mockList = mock(ArrayList.class)` |
| **行为模拟** | `when().thenReturn()`, `doReturn()` | 定义方法调用的返回值 | `when(mock.get(0)).thenReturn("value")` |
| **异常模拟** | `thenThrow()`, `doThrow()` | 测试异常处理逻辑 | `when(mock.save()).thenThrow(new DBException())` |
| **参数匹配器** | `any()`, `eq()`, `argThat()` | 灵活匹配方法参数 | `verify(mock).save(argThat(u -> u.age > 18))` |
| **调用验证** | `verify()`, `times()`, `never()` | 验证方法是否按预期调用 | `verify(mock, times(2)).update()` |
| **参数捕获** | `ArgumentCaptor` | 捕获方法调用参数进行断言 | 见下方详细说明 |
| **部分模拟(Spy)** | `spy()`, `@Spy` | 包装真实对象并覆盖特定方法 | `List spyList = spy(new ArrayList())` |
| **静态方法模拟** | `mockStatic()` (Mockito 3.4+) | 模拟静态方法调用 | `try (MockedStatic<Util> util = mockStatic(Util.class)) {...}` |
| **调用顺序验证** | `InOrder` | 验证多个调用的执行顺序 | 见下方详细说明 |


## 二、【重点】注意事项
**关键原则**：**只模拟外部依赖**（数据库、网络服务、文件系统等），对核心业务逻辑使用真实对象。

**典型测试结构**：

1. 创建模拟依赖
2. 设置模拟行为
3. 执行测试方法
4. 验证状态变化
5. 验证依赖交互

**静态模拟注意事项**

1. **线程安全**：静态模拟**不是线程安全**的，确保在单线程中使用
2. **性能影响**：静态模拟会修改类加载器，可能略微增加测试时间
3. **设计警告**：需大量静态模拟可能意味着代码需要重构（考虑依赖注入替代）
4. **作用域**：每个 `MockedStatic` 实例只影响其作用域内的调用
5. **重构代码：**静态方法模拟应作为**最后手段**，优先考虑重构代码

**黄金法则**：Mockito 应用于解决**外部依赖问题**，而非掩盖设计缺陷。当发现需要大量模拟才能测试时，应考虑重构代码：

+ 引入依赖注入
+ 遵循单一职责原则
+ 使用策略模式替换条件逻辑
+ 将静态工具类转换为可注入服务

## 三、【重点】Mockito 使用最佳实践
#### 1. 【重点】**明确测试目标，避免过度模拟**
+ **原则**：只模拟外部依赖（如数据库、网络服务），不要模拟被测对象（SUT）本身或其内部组件。
+ **示例**：

```java

@Mock 
private UserRepository userRepository; // 正确：模拟外部依赖
@InjectMocks 
private UserService userService; // 被测对象

@Mock 
private String userName; // 反例，错误：不要模拟值对象（如String, Integer）或被测对象
```

#### 2. 【重点】**优先使用注解简化设置**
+ **实践**：使用 `@Mock` 和 `@InjectMocks` 注解配合初始化方式（如在测试类上使用 `@ExtendWith(MockitoExtension.class)`（JUnit 5）或 `@RunWith(MockitoJUnitRunner.class)`（JUnit 4））减少样板代码。
+ **示例**（JUnit 5）：

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock 
    private UserRepository userRepository;
    @InjectMocks 
    private UserService userService;
    // 测试方法...
}
```

#### 3. 【推荐】**BDD（行为驱动开发）风格编写测试**
+ **实践**：Mockito支持BDD风格的API，即 `given(...).willReturn(...)`等，这可以让测试代码更符合 `Given-When-Then` 结构，使用 `given`、`when`、`then` 结构提升可读性。
+ **示例**：

```java
@Test
void getUserById_shouldReturnUser() {
    // Given
    User expectedUser = new User("Alice");
    given(userRepository.findById("alice_id")).willReturn(expectedUser);
    // When
    User actualUser = userService.getUserById("alice_id");
    // Then
    assertEquals(expectedUser, actualUser);
}
```

#### 4. **精确Stubbing，避免模糊匹配**
+ **原则**：尽量使用具体的参数值，避免过度使用 `any()` 等匹配器，除非确实需要灵活性。
+ **示例**：

```java
// 正例：精确参数
given(userRepository.findById("alice_id")).willReturn(alice);
// 反例：模糊匹配（可能掩盖问题）
given(userRepository.findById(anyString())).willReturn(alice); // 任何ID都返回Alice，可能不真实
```

#### 5. **验证交互时注重核心逻辑**
+ **原则**：只验证与测试目标直接相关的交互，避免过度验证（如内部工具方法）。
+ **示例**：

```java
// 正例：验证核心方法被调用
verify(userRepository).findById("alice_id");
// 反例：过度验证（如验证日志记录）
verify(logService).logAccess("alice_id"); // 除非这是测试目标，否则不要验证
```

#### 6. 【重点】**谨慎使用Spy**
+ **原则**：优先使用 `mock`，仅在需要部分模拟时使用 `spy`（如测试遗留代码）。注意 `spy` 会调用真实方法，可能导致异常。
+ **正确使用Spy**：

```java
List<String> list = new ArrayList<>();
List<String> spyList = spy(list);
// 正确：使用doReturn避免调用真实方法
doReturn(100).when(spyList).size();
// 错误：直接when(spyList.size())会调用真实方法（此时size()=0）
when(spyList.size()).thenReturn(100); // 抛出IndexOutOfBoundsException
```

#### 7. **异常测试标准化**
+ **实践**：明确区分Stubbing异常和验证异常。
+ **示例**：

```java
@Test
void updateUser_shouldThrowWhenUserNotFound() {
    // Stubbing：模拟异常
    given(userRepository.findById("unknown_id")).willThrow(new UserNotFoundException());
    // 验证异常
    assertThrows(UserNotFoundException.class, () -> userService.updateUser("unknown_id", new UserData()));
    // 可选：验证交互
    verify(userRepository, never()).save(any());
}
```

#### 8. **避免使用**`verifyNoMoreInteractions`
+ **原因**：过度使用会导致测试脆弱（对无关交互敏感）。替代方案：只验证必要的交互。
+ **例外**：在需要严格验证无多余调用时（如协议要求），可谨慎使用。

#### 9. 【重点】**及时清理资源（按需）**
+ **场景**：使用 `MockedStatic`（Mockito 3.4+）或需要重置mock时。
+ **示例**（静态模拟）：

```java
@Test
void testStaticMethod() {
    try (MockedStatic<MyUtils> utils = mockStatic(MyUtils.class)) {
        utils.when(MyUtils::generateId).thenReturn("fixed-id");
        // 测试代码...
    } // 自动关闭，解除静态模拟
}
```

#### 10. **保持测试独立性和可读性**
+ **命名**：测试方法名明确表达意图（如 `getUserById_whenNotFound_throwsException`）。
+ **单一职责**：每个测试只验证一个行为。
+ **避免依赖**：不要依赖测试执行顺序，每个测试独立初始化mock。

## 四、总结：核心原则
+ **避免过度模拟**：
    - 只模拟外部依赖（如数据库、网络服务）
    - 不要模拟值对象（如String/Integer）或工具类
+ **3A原则**：
    - **Arrange**：初始化模拟对象和存根
    - **Act**：执行被测试方法
    - **Assert**：验证结果和交互
+ **KISS原则**：优先选择简单方案（如纯Mockito），避免复杂技巧（如PowerMock）。
+ **聚焦业务价值**：测试应验证业务逻辑，而不是框架使用。
+ **重构优先**：当测试难以编写时，首先考虑重构代码（如依赖注入、接口分离）。  
这些实践覆盖了大部分日常测试场景，遵循它们可以显著提升测试质量。记住，好的测试应该像文档一样清晰表达代码的预期行为。

## 五、资源推荐
1. [官方文档](https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html) - 最新API参考
2. [Mockito Cookbook](https://www.baeldung.com/mockito-series) - 实用技巧合集
3. [测试驱动开发(TDD)实践指南](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
4. [Effective Unit Testing](https://github.com/GunterMueller/Books-3/blob/master/Effective%20Unit%20Testing.pdf)- Lasse Koskela著


