# 概述

我们将在Spring Boot项目中集成MyBatis Generator，并配置其生成MyBatis Dynamic SQL风格的代码。
MyBatis Dynamic SQL是MyBatis 3的一个特性，它允许使用Java API构建动态SQL查询，避免编写XML或使用Example类。

> MyBatis Dynamic SQL 核心优势
>
> *   类型安全：所有列引用都是类型安全的
> *   流畅的API：链式调用构建查询
> *   动态SQL：自然处理条件逻辑
> *   无XML：避免XML配置的繁琐
> *   IDE支持：自动补全和类型检查

步骤概述：

1.  创建Spring Boot项目，添加必要的依赖（包括MyBatis Spring Boot Starter、数据库驱动、MyBatis Generator等）。

2.  配置MyBatis Generator（通过Maven插件方式）。

3.  编写generatorConfig.xml配置文件，指定生成Dynamic SQL风格的代码。

4.  运行MyBatis Generator生成代码。

5.  在Spring Boot中配置MyBatis，使用生成的Mapper。

# 详细步骤

## 一、创建Spring Boot项目并添加依赖

使用[Spring Initializr](https://start.spring.io/)创建一个新项目，选择以下依赖：

*   Spring Web (如果构建Web应用)

*   MyBatis Framework

*   MySQL Driver (以MySQL为例，或者根据你的数据库选择)

![image.png](https://p0-xtjj-private.juejin.cn/tos-cn-i-73owjymdk6/93c61e2cd0664acc960e4b835dc16922~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5oOc6bif:q75.awebp?policy=eyJ2bSI6MywidWlkIjoiMTAxOTk2NTU5OTEzNDY0OCJ9&rk3s=f64ab15b&x-orig-authkey=f32326d3454f2ac7e96d3d06cdbb035152127018&x-orig-expires=1751338184&x-orig-sign=hZOAN%2Fn%2BFkgBrVvPR9UnXiBDpA8%3D)

然后在pom.xml中添加MyBatis Generator Maven插件以及MyBatis Dynamic SQL依赖：

```xml

<dependencies>
    <!-- Spring Boot Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <!-- MyBatis Spring Boot Starter -->
    <dependency>
        <groupId>org.mybatis.spring.boot</groupId>
        <artifactId>mybatis-spring-boot-starter</artifactId>
        <version>3.0.3</version>
    </dependency>
    <!-- MySQL 驱动 -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <scope>runtime</scope>
    </dependency>
    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
    <!-- MyBatis Dynamic SQL -->
    <dependency>
        <groupId>org.mybatis.dynamic-sql</groupId>
        <artifactId>mybatis-dynamic-sql</artifactId>
        <version>1.5.0</version>
    </dependency>
</dependencies>

<build>
    <plugins>
        <!-- MyBatis Generator 插件 -->
        <plugin>
            <groupId>org.mybatis.generator</groupId>
            <artifactId>mybatis-generator-maven-plugin</artifactId>
            <version>1.4.2</version>
            <dependencies>
                <dependency>
                    <groupId>com.mysql</groupId>
                    <artifactId>mysql-connector-j</artifactId>
                    <version>8.0.33</version>
                </dependency>
                <!-- 支持生成 Dynamic SQL -->
                <dependency>
                    <groupId>org.mybatis.dynamic-sql</groupId>
                    <artifactId>mybatis-dynamic-sql</artifactId>
                    <version>1.5.0</version>
                </dependency>
            </dependencies>
            <configuration>
                <configurationFile>src/main/resources/generatorConfig.xml</configurationFile>
                <overwrite>true</overwrite>
                <verbose>true</verbose>
            </configuration>
        </plugin>
    </plugins>
</build>

```

## 二、编写generatorConfig.xml配置文件

在`src/main/resources`目录下创建`generatorConfig.xml`文件。我们需要配置生成Dynamic SQL风格的代码，这通过设置`targetRuntime="MyBatis3DynamicSql"`来实现。

示例配置：

```xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE generatorConfiguration
        PUBLIC "-//mybatis.org//DTD MyBatis Generator Configuration 1.0//EN"
        "https://mybatis.org/dtd/mybatis-generator-config_1_0.dtd">

<generatorConfiguration>
    <!-- 引入 application.properties 中的配置(可选) -->
    <properties resource="application.properties"/>

    <!-- 数据库驱动路径（如果未通过Maven依赖管理） -->
    <!-- <classPathEntry location="/path/to/mysql-connector-java-8.0.33.jar"/> -->

    <context id="mysql" targetRuntime="MyBatis3DynamicSql">
        <!-- 生成的Java文件编码 -->
        <property name="javaFileEncoding" value="UTF-8"/>

        <!-- 生成的Java文件的注释 -->
        <commentGenerator>
            <!-- 注释配置：不生成注释 -->
            <property name="suppressAllComments" value="true"/>
            <!-- 生成注释 -->
            <!--            <property name="addRemarkComments" value="true"/>-->
        </commentGenerator>
        <!-- 数据库连接信息 -->
        <jdbcConnection driverClass="${spring.datasource.driver-class-name}"
                        connectionURL="${spring.datasource.url}"
                        userId="${spring.datasource.username}"
                        password="${spring.datasource.password}">
        </jdbcConnection>
        <!-- Java模型生成配置 -->
        <javaModelGenerator targetPackage="com.example.demo.model.entity" targetProject="src/main/java">
            <property name="enableSubPackages" value="true"/>
            <property name="trimStrings" value="true"/>
        </javaModelGenerator>
        <!-- 注意：如果使用Dynamic SQL方式，不需要XML映射文件 -->
        <!-- 生成 SQL Map XML 文件的配置 -->
        <!--        <sqlMapGenerator targetPackage="mapper" targetProject="src/main/resources">-->
        <!--            <property name="enableSubPackages" value="true" />-->
        <!--        </sqlMapGenerator>-->
        <!-- Mapper接口生成配置 -->
        <javaClientGenerator type="ANNOTATEDMAPPER"
                             targetPackage="com.example.demo.repository.generated"
                             targetProject="src/main/java">
            <property name="enableSubPackages" value="true"/>
        </javaClientGenerator>
        <!-- 指定要生成的表 -->
        <table tableName="user" domainObjectName="User">
            <generatedKey column="id" sqlStatement="MySql" identity="true"/>
        </table>
        <table tableName="rule" domainObjectName="RuleEntity" mapperName="RuleMapper">
            <generatedKey column="id" sqlStatement="MySql" identity="true"/>
        </table>

        <table tableName="rule_version" domainObjectName="RuleVersionEntity" mapperName="RuleVersionMapper">
            <generatedKey column="id" sqlStatement="MySql" identity="true"/>
        </table>
        <!-- 生成所有表 -->
        <!--         <table tableName="%" />-->
    </context>
</generatorConfiguration>


```

注意：

1.  我们使用了`targetRuntime="MyBatis3DynamicSql"`，这会生成Dynamic SQL风格的代码。

2.  不需要配置`sqlMapGenerator`，因为Dynamic SQL不生成XML映射文件。

3.  `javaClientGenerator`的`type`设置为`ANNOTATEDMAPPER`，表示使用注解方式（实际上Dynamic SQL的Mapper接口是通过Java API构建的，由Dynamic SQL的运行时库提供支持）。

4.  在`jdbcConnection`中，我们使用了Spring Boot的`application.properties`中的数据库配置（通过`${}`占位符引用）。需要在`generatorConfig.xml`文件中配置 `<properties resource="application.properties"/>`，并且确保`application.properties`中有这些属性。

## 三、配置application.properties

在`src/main/resources/application.properties`中配置数据源：

```properties
spring.application.name=demo
server.port=8088
# 数据源配置
spring.datasource.url=jdbc:mysql://localhost:3306/mydatabase
spring.datasource.username=root
spring.datasource.password=mysecretpassword
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

```

## 四、运行MyBatis Generator生成代码

在项目根目录下运行命令：

```bash
mvn mybatis-generator:generate
```

或者在IDE中运行Maven插件的`mybatis-generator:generate`目标。

![image.png](https://p0-xtjj-private.juejin.cn/tos-cn-i-73owjymdk6/b27828e681894d53afce4b7dde0333ff~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5oOc6bif:q75.awebp?policy=eyJ2bSI6MywidWlkIjoiMTAxOTk2NTU5OTEzNDY0OCJ9&rk3s=f64ab15b&x-orig-authkey=f32326d3454f2ac7e96d3d06cdbb035152127018&x-orig-expires=1751338184&x-orig-sign=DK3g2dojYmX3AwZdWhWLVBhhrPc%3D)

生成的文件将包括：

1.  实体类（POJO）：在`com.example.demo.model.entity`包下。

2.  Mapper接口：在`com.example.demo.repository.generated`包下。注意，生成的Mapper接口会继承MyBatis Dynamic SQL提供的`MyBatis3Mapper`接口（比如`CommonCountMapper, CommonDeleteMapper, CommonUpdateMapper`），这些接口提供了一些基本的CRUD方法。

## 五、在Spring Boot中使用生成的Mapper

1.  在目录 `com.example.demo.config` 创建 `MyBatisConfig.java` 配置类：

```java
import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

@Configuration
@MapperScan("com.example.demo.repository")
public class MyBatisConfig {
    @Bean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        SqlSessionFactoryBean sessionFactory = new SqlSessionFactoryBean();
        sessionFactory.setDataSource(dataSource);
        sessionFactory.setTypeAliasesPackage("com.example.demo.model.entity");

        return sessionFactory.getObject();
    }

}

```

在Spring Boot项目中，使用`@MapperScan`注解可以方便地扫描并注册MyBatis的Mapper接口。这样，我们就不需要在每个Mapper接口上都添加`@Mapper`注解。

注意事项：

*   **`@MapperScan`与`@Mapper`**：如果使用了`@MapperScan`，则不需要在每个Mapper接口上再写`@Mapper`。但是，如果有些Mapper接口不在扫描路径下，那么仍然需要在该接口上使用`@Mapper`。

*   **包路径**：确保`@MapperScan`指定的包路径正确，否则Spring容器无法创建Mapper的Bean，导致注入失败。

*   **多模块项目**：如果项目有多个模块，并且Mapper接口分布在不同的模块中，确保这些模块的包路径都被扫描到。

2.  在Service中注入Mapper并使用：

```java

@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserMapper userMapper;
    
    // 创建用户
    public int createUser(User user) {
        return userMapper.insert(user);
    }
    
    // 根据ID获取用户
    public Optional<User> getUserById(Long id) {
        return userMapper.selectByPrimaryKey(id);
    }
    
    // 更新用户
    public int updateUser(User user) {
        return userMapper.updateByPrimaryKeySelective(user);
    }
    
    // 删除用户
    public int deleteUser(Long id) {
        return userMapper.deleteByPrimaryKey(id);
    }
    
    // 动态查询用户
    public List<User> findUsers(String username, Integer minAge, Integer maxAge) {
        return userMapper.select(c -> c
            .where(UserDynamicSqlSupport.username, isLikeIfPresent(username).map(s -> s + "%")
            .and(UserDynamicSqlSupport.age, isBetweenWhenPresent(minAge, maxAge))
            .orderBy(UserDynamicSqlSupport.createTime.descending())
            .build()
            .execute());
    }
    
    // 辅助方法：条件存在时使用 LIKE
    private Optional<Condition> isLikeIfPresent(String value) {
        return Optional.ofNullable(value)
            .filter(v -> !v.isEmpty())
            .map(v -> UserDynamicSqlSupport.username.like(v));
    }
    
    // 辅助方法：条件存在时使用 BETWEEN
    private Optional<BetweenCondition> isBetweenWhenPresent(Integer min, Integer max) {
        if (min != null && max != null) {
            return Optional.of(UserDynamicSqlSupport.age.between(min, max));
        }
        return Optional.empty();
    }
}

```

注意：上面的`user`是一个自动生成的表对应的对象（在UserMapper中有一个静态字段`user`，用于构建查询）。实际使用时，需要导入生成的Mapper和表对象。

例如，在UserService中导入：

```java

import static com.example.demo.mapper.UserDynamicSqlSupport.*;

import static org.mybatis.dynamic.sql.SqlBuilder.*;

```

3.  在controller中注入service并使用

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    
    private final UserService userService;
    
    @PostMapping
    public ResponseEntity<?> createUser(@RequestBody User user) {
        int result = userService.createUser(user);
        return result > 0 
            ? ResponseEntity.ok("User created")
            : ResponseEntity.badRequest().body("Create failed");
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return userService.getUserById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<?> updateUser(@PathVariable Long id, @RequestBody User user) {
        user.setId(id);
        int result = userService.updateUser(user);
        return result > 0 
            ? ResponseEntity.ok("User updated")
            : ResponseEntity.badRequest().body("Update failed");
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteUser(@PathVariable Long id) {
        int result = userService.deleteUser(id);
        return result > 0 
            ? ResponseEntity.ok("User deleted")
            : ResponseEntity.badRequest().body("Delete failed");
    }
    
    @GetMapping("/search")
    public List<User> searchUsers(
            @RequestParam(required = false) String username,
            @RequestParam(required = false) Integer minAge,
            @RequestParam(required = false) Integer maxAge) {
        
        return userService.findUsers(username, minAge, maxAge);
    }
}

```

## 六、MyBatis Dynamic SQL 生成代码的特点

1.  生成的Mapper接口包含的方法：

*   `insert`：插入记录

*   `insertMultiple`：批量插入

*   `insertSelective`：选择性插入（忽略null）

*   `selectByPrimaryKey`：根据主键查询

*   `select`：根据条件查询（可返回多条）

*   `selectOne`：根据条件查询一条

*   `update`：更新

*   `delete`：删除

*   等等

2.  同时会生成一个与表同名的辅助类（如`UserDynamicSqlSupport`），其中包含表的列定义，用于构建动态SQL。

3.  不需要XML映射文件，所有SQL通过Java API动态构建。

## 七、注意事项

1.  确保数据库表有主键，否则生成代码时可能会出现问题。

2.  如果表名或列名是SQL关键字，需要在配置中使用`<columnOverride>`或`<table>`的`delimitIdentifiers`属性处理。

3.  生成的代码可能会覆盖已有的文件，注意备份自定义代码（通常不要修改生成的代码，而是通过扩展方式）。

## 八、总结

本方案在 Spring Boot 中集成了 MyBatis Generator，并配置生成 MyBatis Dynamic SQL 风格的代码，具有以下特点：

1.  **代码简洁**：使用 Lombok 减少样板代码
2.  **类型安全**：Dynamic SQL 提供编译时检查
3.  **易于维护**：无需 XML 配置
4.  **动态查询**：灵活构建复杂查询
5.  **高效开发**：自动生成基础 CRUD 代码

通过这种方式，你可以专注于业务逻辑开发，而无需手动编写重复的数据访问层代码。
