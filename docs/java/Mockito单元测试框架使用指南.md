# Mockito单元测试框架使用指南

Mockito 是一个流行的 Java 单元测试模拟框架，用于创建和配置模拟对象（mock objects）。它能够帮助你在测试中隔离外部依赖，使得测试更加专注于被测试类的行为。以下是一个关于 Mockito 使用的基本介绍：
## Mockito 使用指南
### 1. 添加依赖
首先，需要在项目中添加 Mockito 的依赖。以 Maven 为例：
```xml
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <version>5.11.0</version> <!-- 请使用最新版本 -->
    <scope>test</scope>
</dependency>
```
### 2. 基本用法
Mockito 的核心功能包括：创建模拟对象、设置模拟行为、验证交互。
#### 创建模拟对象
使用 `Mockito.mock()` 方法或 `@Mock` 注解来创建模拟对象。
**使用 `mock()` 方法：**
```java
import static org.mockito.Mockito.*;
List<String> mockedList = mock(List.class);
```
**使用 `@Mock` 注解：**
在测试类上使用 `@ExtendWith(MockitoExtension.class)`（JUnit 5）或 `@RunWith(MockitoJUnitRunner.class)`（JUnit 4），然后使用 `@Mock` 注解字段。
```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
@ExtendWith(MockitoExtension.class)
public class MockitoTest {
    @Mock
    List<String> mockedList;
}
```
#### 设置模拟行为
使用 `when(...).thenReturn(...)` 来指定当模拟对象的方法被调用时返回什么值。
```java
when(mockedList.get(0)).thenReturn("first");
```
也可以设置抛出异常：
```java
when(mockedList.get(1)).thenThrow(new RuntimeException());
```
#### 验证交互
验证模拟对象的方法是否被调用，以及调用的参数、次数等。
```java
mockedList.add("one");
mockedList.add("two");
// 验证 mockedList 的 add 方法被调用两次，参数分别为 "one" 和 "two"
verify(mockedList, times(2)).add(anyString());
verify(mockedList).add("one");
verify(mockedList).add("two");
// 验证 get(0) 被调用一次
verify(mockedList).get(0);
```
### 3. 参数匹配器
Mockito 提供参数匹配器（如 `any()`, `eq()` 等）来更灵活地匹配参数。
```java
// 当调用 add 方法时，无论参数是什么，都返回 true
when(mockedList.add(anyString())).thenReturn(true);
// 验证 add 方法被调用，参数为 "someString"
verify(mockedList).add(eq("someString"));
```
### 4. 验证调用顺序
可以使用 `InOrder` 来验证多个模拟对象的调用顺序。
```java
InOrder inOrder = inOrder(mockedList);
inOrder.verify(mockedList).add("first");
inOrder.verify(mockedList).add("second");
```
### 5. 存根连续调用（Stubbing Consecutive Calls）
对于同一个方法调用，可以设置连续的不同行为。
```java
when(mockedList.get(anyInt()))
    .thenReturn("first")
    .thenReturn("second")
    .thenThrow(new RuntimeException());
// 第一次调用返回 "first"
System.out.println(mockedList.get(0)); // "first"
// 第二次调用返回 "second"
System.out.println(mockedList.get(0)); // "second"
// 第三次调用抛出异常
System.out.println(mockedList.get(0)); // 抛出 RuntimeException
```
### 6. 参数捕获
使用 `ArgumentCaptor` 来捕获方法调用的参数，以便进行进一步断言。
```java
ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
verify(mockedList).add(captor.capture());
assertEquals("capturedValue", captor.getValue());
```
### 7. 部分模拟（Spy）
`Spy` 是对真实对象的包装，默认会调用真实方法，但你可以选择性地对某些方法进行模拟。
```java
List<String> realList = new ArrayList<>();
List<String> spiedList = spy(realList);
// 可以设置某些方法的行为
doReturn("mockValue").when(spiedList).get(0);
// 其他方法会调用真实对象的方法
spiedList.add("realValue");
assertEquals(1, spiedList.size());
```
### 8. 重置模拟对象
通常不建议在测试中重置模拟对象，因为这可能意味着测试不够独立。但在某些情况下，可以使用 `reset()` 方法：
```java
reset(mockedList);
```
### 9. 行为驱动开发（BDD）风格
Mockito 支持 BDD 风格的 API，使用 `given(...).willReturn(...)` 等。
```java
import static org.mockito.BDDMockito.*;
given(mockedList.get(0)).willReturn("first");
```
### 10. 注意事项
- 不要模拟不可靠的对象（如值对象）。
- 避免过度使用模拟，尽量使用真实对象（如使用内存数据库代替模拟数据库）。
- 每个测试应该只测试一件事情，验证的交互也应该尽量简洁。


#### 最佳实践
1. **3A原则**：
   - **Arrange**：初始化模拟对象和存根
   - **Act**：执行被测试方法
   - **Assert**：验证结果和交互

2. **避免过度模拟**：
   - 只模拟外部依赖（如数据库、网络服务）
   - 不要模拟值对象或工具类

3. **组合JUnit使用**：
```java
@ExtendWith(MockitoExtension.class) // JUnit 5
class ServiceTest {
    @Mock
    Database mockDB;
    
    @InjectMocks
    Service service; // 自动注入模拟对象

    @Test
    void testQuery() {
        when(mockDB.query(any())).thenReturn("result");
        String res = service.executeQuery("SELECT");
        assertEquals("result", res);
    }
}
```

---

#### 常见错误解决
- **`UnnecessaryStubbingException`**：移除未使用的存根
- **`ArgumentNotMatcherException`**：混合匹配器与具体值时，所有参数必须用匹配器：
  ```java
  // 错误示例
  when(mock.method(anyInt(), "value"))...
  
  // 正确写法
  when(mock.method(anyInt(), eq("value")))...
  ```

## 示例：一个完整的测试案例
我们通过一个具体的例子来介绍Mockito的使用。假设我们有一个简单的用户服务（UserService），它依赖于用户仓库（UserRepository）。我们将对UserService进行单元测试，并模拟UserRepository。
### 场景描述
- `UserService` 包含一个方法 `getUserEmail`，通过用户名获取用户邮箱。
- `UserRepository` 是一个数据访问接口，包含方法 `findUserByUsername`。
### 类定义
```java
// 用户实体
public class User {
    private String username;
    private String email;
    // 构造方法、getter和setter省略
}
// 用户仓库接口
public interface UserRepository {
    User findUserByUsername(String username);
}
// 用户服务
public class UserService {
    private UserRepository userRepository;
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    public String getUserEmail(String username) {
        User user = userRepository.findUserByUsername(username);
        if (user == null) {
            return null;
        }
        return user.getEmail();
    }
}
```
### 单元测试步骤
我们将使用Mockito来模拟UserRepository，并测试UserService的getUserEmail方法。
#### 1. 添加依赖
确保项目中已经添加了Mockito依赖（如之前所述）。
#### 2. 编写测试类
使用JUnit 5和Mockito扩展。
```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserRepository mockUserRepository;
    @InjectMocks
    private UserService userService;
    @Test
    void getUserEmail_UserExists_ReturnsEmail() {
        // Arrange: 设置模拟行为
        String username = "john_doe";
        String email = "john@example.com";
        User mockUser = new User();
        mockUser.setUsername(username);
        mockUser.setEmail(email);
        // 当调用mockUserRepository.findUserByUsername(username)时，返回mockUser
        when(mockUserRepository.findUserByUsername(username)).thenReturn(mockUser);
        // Act: 调用被测试方法
        String result = userService.getUserEmail(username);
        // Assert: 验证结果
        assertEquals(email, result);
        // 验证findUserByUsername被调用了一次，且参数是username
        verify(mockUserRepository, times(1)).findUserByUsername(username);
    }
    @Test
    void getUserEmail_UserNotExists_ReturnsNull() {
        // Arrange
        String username = "non_existing";
        when(mockUserRepository.findUserByUsername(username)).thenReturn(null);
        // Act
        String result = userService.getUserEmail(username);
        // Assert
        assertNull(result);
        // 验证调用
        verify(mockUserRepository, times(1)).findUserByUsername(username);
    }
    @Test
    void getUserEmail_ExceptionHandling() {
        // Arrange: 模拟抛出异常
        String username = "test";
        when(mockUserRepository.findUserByUsername(username))
                .thenThrow(new RuntimeException("Database error"));
        // Act & Assert: 验证是否抛出异常
        assertThrows(RuntimeException.class, () -> userService.getUserEmail(username));
    }
}
```
### 详细解释
#### 注解使用
- `@ExtendWith(MockitoExtension.class)`：启用Mockito对JUnit 5的支持。
- `@Mock`：创建一个模拟的UserRepository实例。
- `@InjectMocks`：创建UserService实例，并将模拟的UserRepository注入进去。
#### 测试方法1：`getUserEmail_UserExists_ReturnsEmail`
1. **Arrange**：设置模拟行为，当调用`mockUserRepository.findUserByUsername("john_doe")`时，返回一个预设的User对象。
2. **Act**：调用`userService.getUserEmail("john_doe")`。
3. **Assert**：
   - 验证返回的邮箱是否正确。
   - 使用`verify`检查`findUserByUsername`方法被调用了一次，并且参数是"john_doe"。
#### 测试方法2：`getUserEmail_UserNotExists_ReturnsNull`
1. **Arrange**：设置模拟行为，当调用`findUserByUsername`时返回null（模拟用户不存在）。
2. **Act**：调用被测试方法。
3. **Assert**：验证返回结果为null，并验证方法调用。
#### 测试方法3：`getUserEmail_ExceptionHandling`
1. **Arrange**：设置模拟行为，当调用`findUserByUsername`时抛出异常（模拟数据库错误）。
2. **Act & Assert**：使用`assertThrows`验证调用被测试方法时抛出了异常。
### 高级使用示例：参数捕获
假设我们想要捕获传递给`findUserByUsername`方法的参数，可以这样做：
```java
@Test
void getUserEmail_ArgumentCapture() {
    String username = "john_doe";
    User mockUser = new User();
    mockUser.setEmail("john@example.com");
    when(mockUserRepository.findUserByUsername(username)).thenReturn(mockUser);
    // 执行方法
    userService.getUserEmail(username);
    // 创建参数捕获器
    ArgumentCaptor<String> usernameCaptor = ArgumentCaptor.forClass(String.class);
    verify(mockUserRepository).findUserByUsername(usernameCaptor.capture());
    // 获取捕获的参数值
    String capturedUsername = usernameCaptor.getValue();
    assertEquals(username, capturedUsername);
}
```
### 部分模拟（Spy）示例
如果我们需要测试一个类中的部分方法，而其他方法需要真实调用，可以使用Spy。
假设UserService中有一个内部方法，我们不想模拟，但想模拟依赖项：
```java
public class UserService {
    // ... 其他代码同上
    public String getUserEmailUpperCase(String username) {
        String email = getUserEmail(username);
        return email != null ? email.toUpperCase() : null;
    }
}
```
测试`getUserEmailUpperCase`方法，但只模拟`getUserEmail`方法（注意：这个例子可能不太符合实际，因为通常我们不会对同一个类中的方法进行模拟，这里仅演示Spy的用法）：
```java
@Test
void getUserEmailUpperCase_SpyExample() {
    // 注意：这里我们使用Spy包装真实的UserService对象，但需要确保依赖项已经被模拟
    UserService spyUserService = spy(userService);
    // 模拟getUserEmail方法
    doReturn("john@example.com").when(spyUserService).getUserEmail("john_doe");
    // 调用
    String result = spyUserService.getUserEmailUpperCase("john_doe");
    assertEquals("JOHN@EXAMPLE.COM", result);
}
```
注意：使用Spy时，如果模拟的方法有参数，需要确保传递的参数匹配，否则会调用真实方法。
## 总结
通过以上示例，我们展示了Mockito的核心功能：
- 创建模拟对象（`@Mock`）
- 设置模拟行为（`when().thenReturn()`）
- 验证交互（`verify()`）
- 参数捕获（`ArgumentCaptor`）
- 部分模拟（`spy`）
这些技术可以帮助我们编写隔离的、快速的单元测试，专注于被测试类的行为，而不受依赖项的制约。

以上是 Mockito 的基本使用介绍。Mockito 还有更多高级功能，如模拟静态方法、模拟构造函数等（需要 `mockito-inline` 依赖），具体可以参考 [Mockito 官方文档](https://site.mockito.org/)。


### 资源推荐
- [官方文档](https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html)
- [Mockito GitHub](https://github.com/mockito/mockito)
- 《Effective Unit Testing》by Lasse Koskela

> Mockito 能显著提升测试的隔离性和执行速度，是编写高质量单元测试的利器。掌握其核心用法后，可结合 PowerMock 处理静态方法/私有方法等复杂场景。
