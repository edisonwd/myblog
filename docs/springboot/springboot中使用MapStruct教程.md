# springboot中使用MapStruct教程

在Spring Boot中使用MapStruct可以方便地实现对象之间的映射转换。MapStruct是一个代码生成器，它基于约定优于配置的原则，通过注解在编译时生成映射实现类，从而减少手动编写映射代码的工作量。

以下是使用MapStruct的基本步骤：

### 1. 添加依赖

在`pom.xml`中添加MapStruct的依赖和插件：

```xml

<properties>
    <org.mapstruct.version>1.5.5.Final</org.mapstruct.version>
</properties>

<dependencies>
    <!-- MapStruct核心依赖 -->
    <dependency>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct</artifactId>
        <version>${org.mapstruct.version}</version>
    </dependency>
</dependencies>

<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.8.1</version>
            <configuration>
                <annotationProcessorPaths>
                    <!-- MapStruct注解处理器 -->
                    <path>
                        <groupId>org.mapstruct</groupId>
                        <artifactId>mapstruct-processor</artifactId>
                        <version>${org.mapstruct.version}</version>
                    </path>
                    <!-- 如果使用Lombok，需同时添加 -->
                    <path>
                        <groupId>org.projectlombok</groupId>
                        <artifactId>lombok</artifactId>
                        <version>${lombok.version}</version>
                    </path>
                </annotationProcessorPaths>
            </configuration>
        </plugin>
    </plugins>
</build>
```

> 注意：如果你使用了Lombok，确保在注解处理器路径中同时添加MapStruct和Lombok，并且Lombok的版本需要正确指定。
> 
> 如果项目使用Lombok，确保MapStruct处理器在Lombok之后执行（顺序很重要）。

### 2. 创建映射接口

使用`@Mapper`注解定义一个接口，MapStruct会为该接口生成实现类。

例如，有两个类：`User`和`UserDTO`，需要相互转换。

```java
// 实体类
@Data // Lombok注解
public class User {
    private Long id;
    private String username;
    private String email;
    private Date registrationDate;
}
```

```java
// DTO类
@Data
public class UserDTO {
    private Long id;
    private String login;
    private String contactEmail;
    private String registrationDateStr; // 格式化的日期字符串
}
```

创建映射接口：

```java

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.factory.Mappers;

@Mapper
public interface UserMapper {

    UserMapper INSTANCE = Mappers.getMapper(UserMapper.class);

    @Mapping(source = "username", target = "name")
    @Mapping(source = "email", target = "emailAddress")
    UserDTO userToUserDTO(User user);

    @Mapping(source = "name", target = "username")
    @Mapping(source = "emailAddress", target = "email")
    User userDTOToUser(UserDTO userDTO);

}

```

- `@Mapper`：标记该接口为映射接口，MapStruct会为其生成实现类。

- `@Mapping`：用于指定字段映射，当源对象和目标对象的字段名不一致时使用。`source`指定源对象的字段，`target`指定目标对象的字段。

- 接口中定义了一个实例`INSTANCE`，通过`Mappers.getMapper`获取映射器实例。但在Spring中，我们可以将映射器作为Spring Bean注入，所以也可以不用这种方式（后面会说明如何与Spring集成）。

### 3. 与Spring集成

为了让MapStruct生成的映射器成为Spring Bean，可以在`@Mapper`注解中添加`componentModel = "spring"`。

修改映射接口：

```java

import org.mapstruct.Mapper;

import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface UserMapper {

    @Mapping(source = "username", target = "name")
    @Mapping(source = "email", target = "emailAddress")
    UserDTO userToUserDTO(User user);

    @Mapping(source = "name", target = "username")
    @Mapping(source = "emailAddress", target = "email")
    User userDTOToUser(UserDTO userDTO);

}

```

这样，MapStruct生成的实现类会带有`@Component`注解，因此可以通过Spring的依赖注入来使用：

```java

@Service
public class UserService {

    private final UserMapper userMapper;

    public UserService(UserMapper userMapper) {
        this.userMapper = userMapper;
    }

    public UserDTO getUserDTO(User user) {
        return userMapper.userToUserDTO(user);
    }

}

```

### 4. 使用 Mapper 进行转换

#### 方式一：Spring 依赖注入
```java
@Service
public class UserService {

    @Autowired
    private UserMapper userMapper; // 自动注入

    public UserDTO processUser(UserVO userVO) {
        return userMapper.voToDto(userVO); // 转换 VO→DTO
    }
}
```

#### 方式二：直接使用实例（非 Spring 管理）（推荐）
```java
UserVO vo = new UserVO("Tom", 25, "tom@example.com");
UserDTO dto = UserMapper.INSTANCE.voToDto(vo); // 通过静态实例转换
```

### 5. 高级功能示例

有时，对象之间的映射并不是简单的字段拷贝，可能需要进行一些转换。MapStruct允许在映射方法中调用其他映射方法，也可以使用表达式。





#### (1) 集合映射
自动映射集合，MapStruct会自动生成循环遍历并调用单个对象映射方法的代码。

```java
@Mapper(componentModel = "spring")
public interface UserMapper {
    List<UserDTO> usersToUserDTOs(List<User> users); // 自动遍历转换
}
```

#### (2) 忽略字段
```java
@Mapping(target = "id", ignore = true) // 忽略id字段
UserDTO toDtoWithoutId(User user);
```

#### (3) 表达式计算
使用`@Mapping`注解的`expression`属性可以编写表达式：
```java
@Mapping(target = "fullInfo", 
         expression = "java(user.getUsername() + \" (\" + user.getEmail() + \")\")")
UserDTO toDetailedDto(User user);
```


#### （4）自定义转换方法

可以在映射接口中定义默认方法来实现自定义转换逻辑：

```java

@Mapper(componentModel = "spring")
public interface UserMapper {

    // ... 其他映射
    default String someCustomMethod(SomeType value) {
        // 自定义转换逻辑
        return value.toString();
    }
}

```


#### （5）更新现有对象

有时我们希望更新一个已存在的目标对象，而不是创建新的实例。可以使用`@MappingTarget`注解来标记目标对象：

```java

@Mapping(source = "username", target = "name")
@Mapping(source = "email", target = "emailAddress")
void updateUserDTOFromUser(User user, @MappingTarget UserDTO userDTO);

```

这个方法将根据源对象`User`更新已存在的`UserDTO`对象。




## 使用mapstruct实现多个参数转换

在MapStruct中，如果需要将多个参数（例如两个或多个对象）合并转换成一个DTO对象，可以通过在Mapper接口中定义方法来实现。以下是一个示例：

假设我们有两个源对象：`UserVO` 和 `AddressVO`，需要将它们合并成一个`UserDTO`对象。

### 1. 定义源对象和目标对象

```java

// UserVO.java
public class UserVO {

    private String username;
    private Integer age;

    // getters and setters

}

// AddressVO.java

public class AddressVO {

    private String city;
    private String street;

    // getters and setters

}

// UserDTO.java

public class UserDTO {

    private String name;
    private int age;
    private String city;
    private String street;

    // getters and setters

}

```

### 2. 创建Mapper接口

在Mapper接口中，定义一个方法，该方法接受多个参数（这里为`UserVO`和`AddressVO`）并返回`UserDTO`。

```java

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Mappings;
import org.mapstruct.factory.Mappers;

@Mapper(componentModel = "spring")
public interface UserMapper {

    UserMapper INSTANCE = Mappers.getMapper(UserMapper.class);

    @Mappings({
        @Mapping(source = "userVO.username", target = "name"),
        @Mapping(source = "userVO.age", target = "age"),
        @Mapping(source = "addressVO.city", target = "city"),
        @Mapping(source = "addressVO.street", target = "street")
    })
    UserDTO toUserDTO(UserVO userVO, AddressVO addressVO);

}

```

### 3. 使用Mapper

在Service中，你可以注入这个Mapper（如果使用Spring）或者使用静态实例来转换。

```java

@Service
public class UserService {

    @Autowired
    private UserMapper userMapper; // 使用Spring注入

    public UserDTO getUserInfo(UserVO userVO, AddressVO addressVO) {

        return userMapper.toUserDTO(userVO, addressVO);

    }

}

```

或者不使用Spring：

```java

UserVO userVO = new UserVO("Tom", 25);
AddressVO addressVO = new AddressVO("New York", "5th Avenue");
UserDTO dto = UserMapper.INSTANCE.toUserDTO(userVO, addressVO);
```

### 4. 处理参数为null的情况

MapStruct在生成的方法中会检查每个源对象是否为null。如果某个源对象为null，那么该对象对应的属性在目标对象中将被设置为null（或默认值）。如果你希望有更严格的控制，可以在方法内部进行非空检查（例如在自定义方法中），或者使用MapStruct的`@Context`参数传递上下文（但这里不适用）。

### 5. 自定义转换逻辑

如果转换过程中需要一些自定义逻辑，可以在Mapper接口中定义默认方法或者使用`@AfterMapping`注解。

#### 使用默认方法

```java

@Mapper(componentModel = "spring")
public interface UserMapper {

    default UserDTO toUserDTO(UserVO userVO, AddressVO addressVO) {

        if (userVO == null && addressVO == null) {
            return null;
        }
        UserDTO userDTO = new UserDTO();
        if (userVO != null) {
            userDTO.setName(userVO.getUsername());
            userDTO.setAge(userVO.getAge());
        }
        if (addressVO != null) {
            userDTO.setCity(addressVO.getCity());
            userDTO.setStreet(addressVO.getStreet());
        }
        return userDTO;

    }

}

```

#### 使用@AfterMapping

如果你希望部分使用MapStruct的自动映射，部分自定义，可以结合使用`@MappingTarget`和`@AfterMapping`。

```java

import org.mapstruct.AfterMapping;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.Mappings;
import org.mapstruct.factory.Mappers;

@Mapper(componentModel = "spring")
public abstract class UserMapper {

    public abstract UserDTO toUserDTO(UserVO userVO, AddressVO addressVO);

    @AfterMapping
    protected void afterMapping(UserVO userVO, AddressVO addressVO, @MappingTarget UserDTO userDTO) {
        // 可以在这里添加一些额外的设置
        if (userVO != null && addressVO != null) {
            userDTO.setFullAddress(addressVO.getCity() + ", " + addressVO.getStreet());
        }

    }

}

```


> 注意：使用`@AfterMapping`时，Mapper类必须是抽象类（`abstract class`），因为MapStruct会生成其子类。

### 6. 多个源对象中字段名冲突

如果多个源对象中有相同名称的属性（比如两个对象都有`id`），那么在映射到目标对象时，需要通过`@Mapping`注解明确指定来源。

例如：

```java

@Mappings({
    @Mapping(source = "userVO.id", target = "userId"),
    @Mapping(source = "addressVO.id", target = "addressId")
})
UserDTO toUserDTO(UserVO userVO, AddressVO addressVO);

```

### 7. 总结

通过上述方法，MapStruct可以轻松处理多个源对象转换成一个目标对象的情况。你只需要在Mapper接口中定义对应的方法，并使用`@Mapping`注解指定每个字段的来源（注意要指定是哪个参数的属性）。如果转换逻辑复杂，还可以使用自定义方法或`@AfterMapping`注解进行补充。

## 6. 编译项目

完成上述步骤后，编译项目（如执行`mvn clean compile`），MapStruct会在`target/generated-sources/annotations`目录下生成映射接口的实现类。


## 7. 常见问题解决
### ❌ 问题：编译后找不到Mapper实现类
- **原因**：注解处理器未正确配置。
- **解决**：
  1. 检查`pom.xml`中的`mapstruct-processor`依赖。
  2. 执行Maven命令：`mvn clean compile`（实现类会在`target/generated-sources/annotations/`下生成）。

### ❌ 问题：Lombok和MapStruct冲突
- **现象**：编译时字段为`null`。
- **解决**：
  1. 确保注解处理器顺序：Lombok在前，MapStruct在后。
  2. 在IDE中启用注解处理（IntelliJ：`Settings > Build > Compiler > Annotation Processors`）。

---

## 8. 最佳实践
1. **保持Mapper单一职责**：每个Mapper只处理一组相关对象的转换。
2. **单元测试**：为Mapper编写测试验证转换逻辑。
3. **使用`componentModel = "spring"`**：方便依赖注入。
4. **复杂逻辑拆分**：将自定义方法提取到工具类中。


## mapstruct原理解析

MapStruct 是一个基于注解的 Java 对象映射框架，它通过在编译时生成映射实现类，避免了运行时的反射开销，从而提供了高性能的对象转换。下面我们来详细解析 MapStruct 的工作原理。

### 核心原理

MapStruct 的核心思想是：**在编译阶段通过注解处理器（Annotation Processor）生成映射接口的实现类**。这些实现类包含了具体的字段赋值代码，因此运行期间直接调用这些实现类，无需反射，效率极高。

### 工作流程

1. **定义映射接口**：

开发者定义一个接口，并使用 MapStruct 提供的注解（如 `@Mapper`、`@Mapping` 等）来描述对象之间的映射规则。

2. **编译时处理**：

在编译阶段，MapStruct 的注解处理器会扫描所有带有 `@Mapper` 注解的接口，并根据注解信息生成该接口的实现类。生成的类位于项目的 `target/generated-sources/annotations` 目录（Maven 项目）中。

3. **生成实现类**：

生成的实现类中，每个映射方法都是具体的 Java 代码，例如：

```java

public class UserMapperImpl implements UserMapper {

@Override

public UserDTO userToUserDTO(User user) {

if (user == null) {

return null;

}

UserDTO userDTO = new UserDTO();

userDTO.setLogin(user.getUsername());

userDTO.setContactEmail(user.getEmail());

// 其他字段转换

return userDTO;

}

}

```

4. **运行时使用**：

在运行时，开发者只需要通过依赖注入（如 Spring 的 `@Autowired`）或者直接实例化 Mapper 接口，调用其方法即可完成对象转换。由于实现类是直接操作字段的，没有反射，所以性能接近手写代码。

### 关键注解解析

- **`@Mapper`**：标记一个接口为映射器接口。主要属性：

    - `componentModel`：指定生成的 Mapper 实现类的组件模型。常用值有：
    
    - `default`：不生成组件，需手动实例化。
    
    - `spring`：生成的实现类带有 `@Component` 注解，可被 Spring 容器管理。
    
    - `cdi`：使用 CDI（Contexts and Dependency Injection）。
    
    - `jsr330`：使用 JSR-330 规范（如 `@Named`）。

- **`@Mapping`**：用于方法或方法参数上，指定字段映射规则。主要属性：

    - `source`：源对象的字段名。
    
    - `target`：目标对象的字段名。
    
    - `ignore`：是否忽略该字段（默认 `false`）。
    
    - `expression`：使用表达式进行赋值（如 `java(...)`）。
    
    - `qualifiedByName`：指定自定义方法（通过 `@Named` 标记）进行转换。
    
    - `dateFormat`：日期格式转换（字符串与日期之间）。

- **`@Mappings`**：当需要多个 `@Mapping` 时，可用 `@Mappings` 包裹（Java 8+ 可使用重复注解）。

- **`@Named`**： 标记一个自定义方法，然后通过 `qualifiedByName` 引用。

- **`@AfterMapping` 和 `@BeforeMapping`**：在映射前后执行自定义方法。

### 映射规则

1. **自动映射**：

如果源对象和目标对象的字段名相同，MapStruct 会自动映射，无需额外配置。

2. **类型转换**：

- 基本类型和包装类型自动转换。

- 自动进行装箱和拆箱。

- 简单类型转换（如 `int` 转 `String`）会调用相应的转换方法（如 `String.valueOf()`）。

- 日期和字符串之间可通过 `dateFormat` 属性转换。

3. **嵌套对象映射**：

如果对象中包含其他对象，MapStruct 会尝试自动寻找对应的映射方法（在同一个 Mapper 或其他 Mapper 中）。

4. **集合映射**：

支持 `List`、`Set`、`Map` 等集合类型，会自动遍历并转换每个元素。

### 自定义映射方法

1. **在 Mapper 接口中定义默认方法**：

```java

@Mapper

public interface CarMapper {

default PersonDTO personToPersonDTO(Person person) {

// 自定义转换逻辑

}

}

```

2. **引用其他 Mapper**：

```java

@Mapper(uses = { AddressMapper.class })

public interface UserMapper {

// 会自动使用 AddressMapper 转换 Address 字段

}

```

### 为什么高性能？

- **编译时生成代码**：避免了运行时的反射，直接调用 setter/getter 方法。

- **无额外依赖**：生成的代码是纯 Java，不依赖任何第三方库。

- **可读性强**：生成的代码类似于手写代码，便于调试。

### 与其它映射框架对比

| 特性           | MapStruct       | ModelMapper     | Orika           | Dozer          |
|----------------|-----------------|-----------------|-----------------|----------------|
| 原理           | 编译时代码生成  | 运行时反射      | 运行时字节码生成 | 运行时反射     |
| 性能           | ⭐⭐⭐⭐⭐         | ⭐⭐             | ⭐⭐⭐⭐           | ⭐⭐            |
| 配置方式       | 注解/接口       | API/配置文件    | API/注解        | XML/注解       |
| 学习曲线       | 低              | 低              | 中              | 中             |
| 支持复杂映射   | 强              | 一般            | 强              | 强             |
| 编译时错误检查 | 有              | 无              | 无              | 无             |




## 9. 总结

MapStruct 通过编译时生成映射实现类，既保证了高性能，又提供了灵活的配置方式（注解）。它的设计哲学是“约定优于配置”，大部分简单映射可以零配置完成，复杂映射则通过注解精确控制。在 Spring Boot 项目中，结合 `componentModel = "spring"`，可以无缝集成到 Spring 容器中，大大简化了对象转换的代码。

因此，对于性能敏感或大型项目，MapStruct 是一个非常优秀的对象映射工具。


在Spring Boot中使用MapStruct的步骤：

1. 添加依赖和注解处理器。

2. 定义映射接口，使用`@Mapper(componentModel = "spring")`。

3. 在接口中定义映射方法，使用`@Mapping`注解配置字段映射。

4. 在需要的地方注入映射器并调用映射方法。

MapStruct大大简化了对象之间的转换代码，并且因为是在编译时生成代码，所以没有反射带来的性能损失。
通过以上步骤，你可以在Spring Boot中高效使用MapStruct实现对象转换，减少手动编码并提升可维护性。


