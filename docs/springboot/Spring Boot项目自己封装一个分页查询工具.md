
# Spring Boot项目自己封装一个分页查询工具
在Spring Boot项目中使用MyBatis进行分页查询，通常有两种主流方式：

1. 使用MyBatis内置的RowBounds进行内存分页（不推荐，数据量大时性能差）

2. 使用分页插件，如PageHelper

## 使用PageHelper可能遇到的一些问题

PageHelper 是一个非常流行的 MyBatis 分页插件，但它也有一些潜在的缺点和需要注意的地方。以下是在使用 PageHelper 时可能遇到的一些问题：
1. **线程安全问题**

- **问题描述**：`PageHelper.startPage()` 方法使用了 `ThreadLocal` 来保存分页参数。如果在同一个线程中多次调用 `startPage()` 而没有及时清理（比如在 finally 块中调用 `PageHelper.clearPage()`），或者线程被复用（如线程池场景），可能导致分页参数混乱。

2. **对复杂 SQL 的支持有限**

- **问题描述**：PageHelper 通过拦截 SQL 并重写来实现分页。对于特别复杂的 SQL（例如包含多个嵌套子查询、UNION 等），自动生成的 count 查询语句可能会出错，导致分页结果不正确。

3. **性能问题**

- **Count 查询效率**：默认情况下，PageHelper 会执行一个 count 查询获取总记录数。如果表数据量非常大（上千万），这个 count 操作可能很慢（尤其是没有合适索引时）。

4. **与其它拦截器冲突**

- **问题描述**：如果项目中同时使用了多个 MyBatis 拦截器（如数据权限拦截器、加解密拦截器等），拦截器的执行顺序可能影响 PageHelper 的正常工作（因为分页依赖于改写 SQL）。确保 PageHelper 是最后一个执行的拦截器（可以通过调整拦截器添加顺序实现）。

5. **对异步/多线程支持不友好**

- **问题描述**：由于依赖 `ThreadLocal`，如果在异步任务（如 `@Async`）或多线程环境中使用 PageHelper，分页参数可能无法正确传递到子线程。

6. **返回对象过于臃肿**

- **问题描述**：`PageInfo` 对象包含大量分页信息（如总页数、导航页码列表等），但实际业务中可能只需要部分字段（如当前页数据、总记录数）。

7. **设计耦合**

- **问题描述**：分页逻辑侵入业务代码（Service 层中显式调用 `PageHelper.startPage()`），违反了分层设计的纯粹性。

> 建议：PageHelper 适合中小型项目的快速开发，但在高并发、大数据量、复杂SQL场景下需谨慎使用，必要时采用更可控的分页方案。


## 自定义分页查询工具
我们可以在Spring Boot项目中不使用PageHelper，而是自己封装一个分页查询工具。主要思路如下：

1. 定义一个分页请求参数类，包含页码和每页数量。

2. 定义一个分页结果类，包含数据列表、总记录数、总页数、当前页码、每页数量等信息。

3. 定义一个分页查询工具：先查询总数，再查询当前页数据，然后封装成分页结果对象。

4. 使用MyBatis Dynamic SQL自定义复杂分页查询逻辑：一个用于查询符合条件的总记录数，一个用于查询当前页的数据（使用数据库的分页语法，如MySQL的LIMIT）。

下面我们一步步实现：

步骤1：创建分页请求参数类（PageRequest）

步骤2：创建分页结果类（PageResult）

步骤3：创建分页查询工具（PaginationUtils）

步骤4：在Mapper接口中使用MyBatis Dynamic SQL自定义复杂分页查询逻辑

步骤5：在Service层调用Mapper的两个方法，并封装PageResult

步骤6：在Controller中接收分页参数，调用Service方法

## 分页查询具体代码实现

### 1. 分页请求参数类（PageRequest）：

```java

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Pattern;


import java.util.List;
import java.util.Set;

/**
 * 分页请求参数封装类
 */


public class PageRequest {

    /**
     * 默认第一页
     */
    public static final int DEFAULT_PAGE_NUM = 1;

    /**
     * 默认每页10条
     */
    public static final int DEFAULT_PAGE_SIZE = 10;

    /**
     * 默认排序方向 - 升序
     */
    public static final String DEFAULT_ORDER = "desc";

    /**
     * 最大允许的每页记录数
     */
    public static final int MAX_PAGE_SIZE = 1000;

    /**
     * 当前页码（从1开始）
     */
    @Min(value = 1, message = "页码不能小于1")
    private int pageNum = DEFAULT_PAGE_NUM;

    /**
     * 每页记录数
     */
    @Min(value = 1, message = "每页数量不能小于1")
    @Max(value = MAX_PAGE_SIZE, message = "每页数量不能超过" + MAX_PAGE_SIZE)
    private int pageSize = DEFAULT_PAGE_SIZE;

    /**
     * 排序字段
     */
    private String sort;

    /**
     * 排序方向
     * asc: 升序
     * desc: 降序
     */
    @Pattern(regexp = "asc|desc", message = "排序方向必须是asc或desc")
    private String order = DEFAULT_ORDER;

    // 无参构造器
    public PageRequest() {
    }

    /**
     * 带页码和每页数量的构造器
     *
     * @param pageNum  当前页码
     * @param pageSize 每页数量
     */
    public PageRequest(int pageNum, int pageSize) {
        this.pageNum = pageNum;
        this.pageSize = pageSize;
    }

    /**
     * 带所有参数的构造器
     *
     * @param pageNum  当前页码
     * @param pageSize 每页数量
     * @param sort     排序字段
     * @param order    排序方向
     */
    public PageRequest(int pageNum, int pageSize, String sort, String order) {
        this.pageNum = pageNum;
        this.pageSize = pageSize;
        this.sort = sort;
        this.order = order;
    }

    /**
     * 计算偏移量（用于数据库分页查询）
     *
     * @return 当前页的起始位置
     */
    public int getOffset() {
        return (pageNum - 1) * pageSize;
    }

    /**
     * 验证排序字段是否在允许的列表中
     *
     * @param allowedFields 允许的排序字段集合
     * @return 如果排序字段有效返回true，否则返回false
     */
    public boolean isSortValid(Set<String> allowedFields) {
        if (sort == null || sort.isEmpty()) {
            return true;
        }
        return allowedFields.contains(sort);
    }

    /**
     * 验证排序字段是否在允许的列表中，无效时抛出异常
     *
     * @param allowedFields 允许的排序字段集合
     * @param errorMessage  错误信息
     * @throws IllegalArgumentException 如果排序字段无效
     */
    public void validateSort(List<String> allowedFields, String errorMessage) {
        if (sort != null && !sort.isEmpty() && !allowedFields.contains(sort)) {
            throw new IllegalArgumentException(errorMessage);
        }
    }

    public int getPageNum() {
        return pageNum;
    }

    public void setPageNum(int pageNum) {
        this.pageNum = pageNum;
    }

    public int getPageSize() {
        return pageSize;
    }

    public void setPageSize(int pageSize) {
        this.pageSize = pageSize;
    }

    public String getSort() {
        return sort;
    }

    public void setSort(String sort) {
        this.sort = sort;
    }

    public String getOrder() {
        return order;
    }

    public void setOrder(String order) {
        this.order = order;
    }
}

```

### 2. 分页结果类（PageResult）：

```java

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.stream.Collectors;


public class PageResult<T> {

    private final int pageNum;        // 当前页码
    private final int pageSize;        // 每页数量
    private final long total;      // 总记录数
    private final int totalPage;       // 总页数
    private final List<T> data;    // 当前页数据
    private final String sort;     // 排序字段
    private final String order;    // 排序方向

    /**
     * 构造函数
     *
     * @param pageRequest 分页请求
     * @param total       总记录数
     * @param data        当前页数据
     */
    public PageResult(PageRequest pageRequest, long total, List<T> data) {
        this.pageNum = pageRequest.getPageNum();
        this.pageSize = pageRequest.getPageSize();
        this.sort = pageRequest.getSort();
        this.order = pageRequest.getOrder();
        this.total = total;
        this.totalPage = calculateTotalPage(total, pageRequest.getPageSize());
        this.data = data;
    }

    /**
     * 构造函数
     *
     * @param pageNum  当前页码
     * @param pageSize  每页数量
     * @param total 总记录数
     * @param data  当前页数据
     * @param sort  排序字段
     * @param order 排序方向
     */
    public PageResult(int pageNum, int pageSize, long total, List<T> data, String sort, String order) {
        this.pageNum = pageNum;
        this.pageSize = pageSize;
        this.total = total;
        this.data = data != null ? data : Collections.emptyList();
        this.sort = sort;
        this.order = order;

        // 计算总页数
        this.totalPage = calculateTotalPage(total, pageSize);
    }

    /**
     * 计算总页数
     *
     * @param total 总记录数
     * @param size  每页数量
     * @return 总页数
     */
    private int calculateTotalPage(long total, int size) {
        if (size <= 0) return 0;
        return (int) Math.ceil((double) total / size);
    }


    // ================ 实用静态方法 ================ //

    /**
     * 创建空的分页结果
     *
     * @param <T> 数据类型
     * @return 空的分页结果
     */
    public static <T> PageResult<T> empty() {
        return new PageResult<>(1, 0, 0, Collections.emptyList(), null, null);
    }

    /**
     * 基于 PageRequest 创建空的分页结果
     *
     * @param pageRequest 分页请求
     * @param <T>         数据类型
     * @return 空的分页结果
     */
    public static <T> PageResult<T> empty(PageRequest pageRequest) {
        return new PageResult<>(
                pageRequest.getPageNum(),
                pageRequest.getPageSize(),
                0,
                Collections.emptyList(),
                pageRequest.getSort(),
                pageRequest.getOrder()
        );
    }

    /**
     * 创建单页结果（适用于数据量小的情况）
     *
     * @param data 所有数据
     * @param <T>  数据类型
     * @return 单页结果
     */
    public static <T> PageResult<T> singlePage(List<T> data) {
        long total = data != null ? data.size() : 0;
        return new PageResult<>(1, (int) total, total, data, null, null);
    }

    /**
     * 创建分页结果（基于 PageRequest）
     *
     * @param pageRequest 分页请求
     * @param total       总记录数
     * @param data        当前页数据
     * @param <T>         数据类型
     * @return 分页结果
     */
    public static <T> PageResult<T> of(PageRequest pageRequest, long total, List<T> data) {
        return new PageResult<>(
                pageRequest.getPageNum(),
                pageRequest.getPageSize(),
                total,
                data,
                pageRequest.getSort(),
                pageRequest.getOrder()
        );
    }

    /**
     * 转换分页结果的数据类型
     *
     * @param source 源分页结果
     * @param mapper 数据转换函数
     * @param <T>    源数据类型
     * @param <R>    目标数据类型
     * @return 转换后的分页结果
     */
    public static <T, R> PageResult<R> map(PageResult<T> source, Function<T, R> mapper) {
        if (source == null || mapper == null) {
            throw new IllegalArgumentException("Source and mapper must not be null");
        }

        List<R> mappedData = source.getData().stream()
                .map(mapper)
                .collect(Collectors.toList());

        return new PageResult<>(
                source.getPageNum(),
                source.getPageSize(),
                source.getTotal(),
                mappedData,
                source.getSort(),
                source.getOrder()
        );
    }

    /**
     * 合并两个分页结果（适用于并行查询场景）
     *
     * @param result1  第一个分页结果
     * @param result2  第二个分页结果
     * @param combiner 数据合并函数
     * @param <T>      第一个结果的数据类型
     * @param <U>      第二个结果的数据类型
     * @param <R>      合并后的数据类型
     * @return 合并后的分页结果
     */
    public static <T, U, R> PageResult<R> combine(
            PageResult<T> result1,
            PageResult<U> result2,
            BiFunction<T, U, R> combiner) {

        // 验证分页信息是否一致
        if (result1.getPageNum() != result2.getPageNum() ||
                result1.getPageSize() != result2.getPageSize() ||
                result1.getTotal() != result2.getTotal()) {
            throw new IllegalArgumentException("Page results are not compatible for combination");
        }

        // 验证数据数量是否一致
        if (result1.getData().size() != result2.getData().size()) {
            throw new IllegalArgumentException("Data lists have different sizes");
        }

        // 合并数据
        List<R> combinedData = new ArrayList<>();
        for (int i = 0; i < result1.getData().size(); i++) {
            R combined = combiner.apply(
                    result1.getData().get(i),
                    result2.getData().get(i)
            );
            combinedData.add(combined);
        }

        return new PageResult<>(
                result1.getPageNum(),
                result1.getPageSize(),
                result1.getTotal(),
                combinedData,
                result1.getSort(),
                result1.getOrder()
        );
    }

    public int getPageNum() {
        return pageNum;
    }

    public int getPageSize() {
        return pageSize;
    }

    public long getTotal() {
        return total;
    }

    public int getTotalPage() {
        return totalPage;
    }

    public List<T> getData() {
        return data;
    }

    public String getSort() {
        return sort;
    }

    public String getOrder() {
        return order;
    }
}


```

### 3. 创建分页查询工具（PaginationUtils）

```java

import java.util.List;
import java.util.function.Supplier;

public class PaginationUtils {

    /**
     * 执行分页查询（使用PageRequest对象）
     *
     * @param pageRequest   分页请求（包含页码、大小、排序等信息）
     * @param countFunction 查询总数的函数
     * @param dataFunction  查询数据的函数
     * @return 分页结果
     */
    public static <T> PageResult<T> paginate(PageRequest pageRequest,
                                             Supplier<Long> countFunction,
                                             Supplier<List<T>> dataFunction) {
        // 查询总数
        long total = countFunction.get();

        // 如果没有数据，直接返回空结果
        if (total == 0) {
            return PageResult.empty(pageRequest);
        }

        // 查询当前页数据
        List<T> data = dataFunction.get();

        return new PageResult<>(pageRequest, total, data);
    }
}

```

### 4. Mapper接口示例（使用MyBatis Dynamic SQL）：

当进行JOIN或复杂子查询时，查询结果通常涉及多个实体，因此需要自定义结果映射。MyBatis Dynamic SQL本身不处理结果映射，你需要：

- **使用注解**：在Mapper接口的方法上使用`@Results`和`@Result`注解定义映射关系。

- **使用XML**：在Mapper XML文件中定义`<resultMap>`。

例如，对于规则和规则版本(一对多)的JOIN查询，结果封装到一个DTO（Data Transfer Object）中：

```java
import java.util.Date;

public class RuleWithLatestVersionDTO {
    private Long id;
    private String ruleId;
    private String name;
    private String domain;
    private Integer latestVersion;
    private String versionName;
    private String versionStatus;
    private Date versionModifiedDate;

    // getters and setters

}

```
在 Mapper接口结果映射配置如下：
```java

import com.example.demo.model.dto.response.RuleWithLatestVersionDTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Result;
import org.apache.ibatis.annotations.Results;
import org.apache.ibatis.annotations.SelectProvider;
import org.mybatis.dynamic.sql.select.render.SelectStatementProvider;
import org.mybatis.dynamic.sql.util.SqlProviderAdapter;
import org.mybatis.dynamic.sql.util.mybatis3.CommonCountMapper;

import java.util.List;

@Mapper
public interface RuleCustomMapper extends CommonCountMapper {


    // 使用@Result注解处理多表字段
    @SelectProvider(type = SqlProviderAdapter.class, method = "select")
    @Results({
            @Result(column = "id", property = "id"),
            @Result(column = "ruleId", property = "ruleId"),
            @Result(column = "name", property = "name"),
            @Result(column = "domain", property = "domain"),
            @Result(column = "latestVersion", property = "latestVersion"),
            @Result(column = "versionName", property = "versionName"),
            @Result(column = "versionStatus", property = "versionStatus"),
            @Result(column = "versionModifiedDate", property = "versionModifiedDate"),
    })
    List<RuleWithLatestVersionDTO> findByCondition(SelectStatementProvider selectStatement);
}

```


### 5. MyBatis Dynamic SQL处理复杂JOIN和子查询：
**告别繁琐的 XML 和 OGNL**:

- **痛点**： 传统的 MyBatis XML Mapper 文件虽然功能强大，但编写和阅读动态 SQL（使用 `<if>`, `<choose>`, `<when>`, `<otherwise>`, `<foreach>` 等标签）在复杂场景下会变得冗长、嵌套深、可读性下降，且需要掌握 OGNL 表达式。在 Java 和 XML 之间切换也影响开发效率。

- **解决**： Dynamic SQL 将 SQL 构建逻辑完全移回 Java 代码中，利用 Java 语言的流程控制 (if/else, 循环) 和强大的 IDE 支持（代码补全、重构、导航），开发体验更流畅、更现代。

比如有如下的一个sql语句，获取满足条件的规则及其最新版本信息：

```sql
SELECT ruleTable.id AS id, ruleTable.rule_id AS ruleId, ruleTable.name AS name, ruleTable.domain AS domain, max_version AS latestVersion
	, ruleVersionTable.name AS versionName, ruleVersionTable.status AS versionStatus, ruleVersionTable.gmt_modified AS versionModifiedDate
FROM rule ruleTable
	JOIN rule_version ruleVersionTable ON ruleTable.rule_id = ruleVersionTable.rule_id
	JOIN (
		SELECT ruleVersionTable.rule_id AS rule_uuid, MAX(ruleVersionTable.version) AS max_version
		FROM rule_version ruleVersionTable
		WHERE ruleVersionTable.id > #{parameters.p1,jdbcType=BIGINT}
		GROUP BY ruleVersionTable.rule_id
	) max_ver
	ON ruleVersionTable.rule_id = max_ver.rule_uuid
		AND ruleVersionTable.version = max_ver.max_version
WHERE ruleTable.id > #{parameters.p2,jdbcType=BIGINT}
	AND ruleTable.name LIKE #{parameters.p3,jdbcType=VARCHAR}
ORDER BY ruleVersionTable.id
LIMIT #{parameters.p5}, #{parameters.p4}
```
使用 MyBatis Dynamic SQL 实现如下【**处理复杂JOIN和子查询**】：

```java

import com.example.demo.common.model.page.PageRequest;
import com.example.demo.model.query.RuleQueryCondition;
import com.example.demo.repository.generated.RuleEntityDynamicSqlSupport;
import com.example.demo.repository.generated.RuleVersionEntityDynamicSqlSupport;


import org.mybatis.dynamic.sql.SortSpecification;
import org.mybatis.dynamic.sql.SqlColumn;
import org.mybatis.dynamic.sql.SqlTable;
import org.mybatis.dynamic.sql.select.ColumnSortSpecification;
import org.mybatis.dynamic.sql.select.QueryExpressionDSL;
import org.mybatis.dynamic.sql.select.SelectModel;
import org.mybatis.dynamic.sql.select.render.SelectStatementProvider;
import org.mybatis.dynamic.sql.render.RenderingStrategies;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.sql.JDBCType;

import static org.mybatis.dynamic.sql.SqlBuilder.*;

@Component
public class RuleQueryBuilder {
    private final RuleVersionEntityDynamicSqlSupport.RuleVersionEntity ruleVersionDO = RuleVersionEntityDynamicSqlSupport.ruleVersionEntity;
    private final RuleEntityDynamicSqlSupport.RuleEntity ruleDO = RuleEntityDynamicSqlSupport.ruleEntity;

    // 数据查询
    public SelectStatementProvider buildDataQuery(RuleQueryCondition queryCondition, PageRequest pageRequest) {

        // 1. 创建派生表的别名和列定义
        // 子查询的表别名
        String subQueryTable = "max_ver";
        SqlTable maxVerTable = SqlTable.of(subQueryTable);
        SqlColumn<String> maxVerRuleUuid = SqlColumn.of("rule_uuid", maxVerTable, JDBCType.VARCHAR);
        SqlColumn<Integer> maxVerMaxVersion = SqlColumn.of("max_version", maxVerTable, JDBCType.INTEGER);
        // 动态构建排序
        List<SortSpecification> sortSpecs = new ArrayList<>();
        SortSpecification sortSpecification = buildSortSpecification(pageRequest.getSort(), pageRequest.getOrder());
        if (sortSpecification != null) {
            sortSpecs.add(sortSpecification);
        }

        // 2.构建子查询
        QueryExpressionDSL<SelectModel>.GroupByFinisher maxVersionSubQuery = buildMaxVersionSubQuery(queryCondition);

        // 3. 主查询：关联规则表、版本表和最大版本子查询
        return select(
                ruleDO.id.as("id"),
                ruleDO.ruleId.as("ruleId"),
                ruleDO.name.as("name"),
                ruleDO.domain.as("domain"),
                maxVerMaxVersion.as("latestVersion"),
                ruleVersionDO.name.as("versionName"),
                ruleVersionDO.status.as("versionStatus"),
                ruleVersionDO.gmtModified.as("versionModifiedDate")
        )
                .from(ruleDO, "ruleDO")
                .join(ruleVersionDO, "ruleVersionDO")
                .on(ruleDO.ruleId, equalTo(ruleVersionDO.ruleId))
                .join(maxVersionSubQuery, subQueryTable)
                .on(ruleVersionDO.ruleId, equalTo(maxVerRuleUuid.qualifiedWith(subQueryTable)))
                .and(ruleVersionDO.version, equalTo(maxVerMaxVersion.qualifiedWith(subQueryTable)))
                .where(ruleDO.id, isGreaterThan(0L))
                .and(ruleDO.tenantId, isEqualToWhenPresent(queryCondition.getTenantId()))
                .and(ruleDO.ruleId, isLikeWhenPresent(wrapLike(queryCondition.getRuleId())))
                .and(ruleDO.name, isLikeWhenPresent(wrapLike(queryCondition.getName())))
                .and(ruleDO.creator, isLikeWhenPresent(wrapLike(queryCondition.getCreateBy())))
                .and(ruleDO.type, isEqualToWhenPresent(queryCondition.getType()))
                .and(ruleDO.domain, isEqualToWhenPresent(queryCondition.getDomain()))
                .and(ruleDO.description, isLikeWhenPresent(wrapLike(queryCondition.getDescription())))
                .orderBy(sortSpecs.toArray(new SortSpecification[0]))
                .limit(pageRequest.getPageSize())
                .offset(pageRequest.getOffset())
                .build()
                .render(RenderingStrategies.MYBATIS3);

    }

    // 总数查询
    public SelectStatementProvider buildCountQuery(RuleQueryCondition queryCondition) {
        // 1. 创建派生表的别名和列定义

        String subQueryTable = "max_ver";
        SqlTable maxVerTable = SqlTable.of(subQueryTable);
        SqlColumn<String> maxVerRuleUuid = SqlColumn.of("rule_uuid", maxVerTable, JDBCType.VARCHAR);
        SqlColumn<Integer> maxVerMaxVersion = SqlColumn.of("max_version", maxVerTable, JDBCType.INTEGER);
        // 2. 构建子查询
        QueryExpressionDSL<SelectModel>.GroupByFinisher maxVersionSubQuery = buildMaxVersionSubQuery(queryCondition);

        // 3. 主查询：关联规则表、版本表和最大版本子查询
        return select(count())
                .from(ruleDO, "ruleDO")
                .join(ruleVersionDO, "ruleVersionDO")
                .on(ruleDO.ruleId, equalTo(ruleVersionDO.ruleId))
                .join(maxVersionSubQuery, subQueryTable)
                .on(ruleVersionDO.ruleId, equalTo(maxVerRuleUuid.qualifiedWith(subQueryTable)))
                .and(ruleVersionDO.version, equalTo(maxVerMaxVersion.qualifiedWith(subQueryTable)))
                .where(ruleVersionDO.id, isGreaterThan(0L))  // 确保where条件有值
                .and(ruleDO.tenantId, isEqualToWhenPresent(queryCondition.getTenantId()))
                .and(ruleDO.ruleId, isLikeWhenPresent(wrapLike(queryCondition.getRuleId())))
                .and(ruleDO.name, isLikeWhenPresent(wrapLike(queryCondition.getName())))
                .and(ruleDO.creator, isLikeWhenPresent(wrapLike(queryCondition.getCreateBy())))
                .and(ruleDO.type, isEqualToWhenPresent(queryCondition.getType()))
                .and(ruleDO.domain, isEqualToWhenPresent(queryCondition.getDomain()))
                .and(ruleDO.description, isLikeWhenPresent(wrapLike(queryCondition.getDescription())))
                .build()
                .render(RenderingStrategies.MYBATIS3);
    }

    // 公共方法：构建最大版本子查询
    private QueryExpressionDSL<SelectModel>.GroupByFinisher buildMaxVersionSubQuery(RuleQueryCondition queryCondition) {
        return select(
                ruleVersionDO.ruleId.as("rule_uuid"),
                max(ruleVersionDO.version).as("max_version"))
                .from(ruleVersionDO)
                .where(ruleVersionDO.id, isGreaterThan(0L))
                .and(ruleVersionDO.modifier, isLikeWhenPresent(wrapLike(queryCondition.getUpdateBy())))
                .and(ruleVersionDO.gmtCreate, isGreaterThanOrEqualToWhenPresent(queryCondition.getGmtCreateFrom()))
                .and(ruleVersionDO.gmtCreate, isLessThanOrEqualToWhenPresent(queryCondition.getGmtCreateTo()))
                .and(ruleVersionDO.gmtModified, isGreaterThanOrEqualToWhenPresent(queryCondition.getGmtModifiedFrom()))
                .and(ruleVersionDO.gmtModified, isLessThanOrEqualToWhenPresent(queryCondition.getGmtModifiedTo()))
                .and(ruleVersionDO.description, isLikeWhenPresent(wrapLike(queryCondition.getRuleVersionDesc())))
                .and(ruleVersionDO.name, isLikeWhenPresent(wrapLike(queryCondition.getRuleVersionName())))
                .and(ruleVersionDO.status, isEqualToWhenPresent(queryCondition.getStatus()))

                .groupBy(ruleVersionDO.ruleId);
    }

    private SortSpecification buildSortSpecification(String field, String order) {
        if (field == null) {
            return new ColumnSortSpecification("ruleVersionDO", ruleVersionDO.id);
        }
        ColumnSortSpecification columnSortSpecification;
        switch (field) {
            case "gmtCreate" ->
                    columnSortSpecification = new ColumnSortSpecification("ruleVersionDO", ruleVersionDO.gmtCreate);
            case "gmtModified" ->
                    columnSortSpecification = new ColumnSortSpecification("ruleVersionDO", ruleVersionDO.gmtModified);
            // 其他字段...
            // 默认排序逻辑
            default -> columnSortSpecification = new ColumnSortSpecification("ruleVersionDO", ruleVersionDO.id);
        }

        return "asc".equalsIgnoreCase(order) ? columnSortSpecification : columnSortSpecification.descending();
    }


    private String wrapLike(String value) {
        return value != null ? "%" + value + "%" : null;
    }

}

```
传统 mapper.xml（XML 动态 SQL）

```xml
<!-- 1. 定义查询语句 -->
<select id="selectRulesWithLatestVersion" resultType="RuleWithLatestVersionDTO">
  SELECT 
    ruleTable.id AS id,
    ruleTable.rule_id AS ruleId,
    ruleTable.name AS name,
    ruleTable.domain AS domain,
    max_ver.max_version AS latestVersion,
    ruleVersionTable.name AS versionName,
    ruleVersionTable.status AS versionStatus,
    ruleVersionTable.gmt_modified AS versionModifiedDate
  FROM rule ruleTable
  JOIN rule_version ruleVersionTable 
    ON ruleTable.rule_id = ruleVersionTable.rule_id
  JOIN (
    SELECT 
      rule_id AS rule_uuid, 
      MAX(version) AS max_version
    FROM rule_version
    <where>
      <if test="p1 != null">
        AND id > #{p1}
      </if>
    </where>
    GROUP BY rule_id
  ) max_ver 
    ON ruleVersionTable.rule_id = max_ver.rule_uuid
    AND ruleVersionTable.version = max_ver.max_version
  <where>
    <if test="p2 != null">
      AND ruleTable.id > #{p2}
    </if>
    <if test="p3 != null">
      AND ruleTable.name LIKE CONCAT('%', #{p3}, '%')
    </if>
  </where>
  ORDER BY ruleVersionTable.id
  LIMIT #{p5}, #{p4}
</select>

<!-- 2. Mapper 接口 -->
public interface RuleMapper {
    List<RuleWithLatestVersionDTO> selectRulesWithLatestVersion(
        @Param("p1") Long p1, 
        @Param("p2") Long p2,
        @Param("p3") String namePattern,
        @Param("p4") Integer pageSize,
        @Param("p5") Integer offset);
}

```

### 关键差异对比
| **特性**               | MyBatis Dynamic SQL                     | 传统 mapper.xml               |
|------------------------|-----------------------------------------|-------------------------------|
| **代码类型**           | Java 代码                               | XML 配置文件                  |
| **可读性**             | ⭐⭐⭐⭐ (强类型检查)               | ⭐⭐ (需切换文件查看)         |
| **编译时检查**         | ✅ 类型安全                             | ❌ 运行时发现错误             |
| **动态条件**           | 链式方法调用 (如 `.where(...)`)         | `<if>`/`<choose>` 标签        |
| **子查询支持**         | 通过 DSL 嵌套构建                       | 原生 SQL 写法                 |
| **分页控制**           | `.limit()`/`.offset()` 方法             | `LIMIT` 直接拼接              |
| **维护成本**           | 中 (需学习 DSL 语法)                    | 低 (SQL 原生写法)             |
| **适合场景**           | 复杂动态查询、高复用逻辑                | 简单查询、团队熟悉 XML 语法   |

> **推荐选择**：
> - 新项目推荐 **MyBatis Dynamic SQL**：类型安全 + 更好的重构能力
> - 遗留系统或简单查询可用 **mapper.xml**：降低学习成本



### 6. Service层：

```java

import com.example.demo.common.model.page.PageRequest;
import com.example.demo.common.model.page.PageResult;
import com.example.demo.common.model.page.PaginationUtils;
import com.example.demo.model.dto.response.RuleWithLatestVersionDTO;
import com.example.demo.model.query.RuleQueryCondition;
import com.example.demo.repository.custom.RuleCustomMapper;
import com.example.demo.repository.custom.builder.RuleQueryBuilder;
import com.example.demo.repository.generated.RuleMapper;
import com.example.demo.service.RuleService;


import org.mybatis.dynamic.sql.SqlColumn;
import org.mybatis.dynamic.sql.select.render.SelectStatementProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;


@Service
public class RuleServiceImpl implements RuleService {

    private final RuleCustomMapper ruleCustomMapper;

    private final RuleMapper ruleMapper;

    private final RuleQueryBuilder ruleQueryBuilder;

    @Autowired
    public RuleServiceImpl(RuleMapper ruleMapper, RuleCustomMapper ruleCustomMapper, RuleQueryBuilder ruleQueryBuilder) {
        this.ruleMapper = ruleMapper;
        this.ruleCustomMapper = ruleCustomMapper;
        this.ruleQueryBuilder = ruleQueryBuilder;
    }

    @Override
    public PageResult<RuleWithLatestVersionDTO> findByCondition(RuleQueryCondition condition, PageRequest pageRequest) {

        List<String> columNames = Arrays.stream(ruleMapper.selectList).map(c -> ((SqlColumn<?>) c).name()).toList();
        pageRequest.validateSort(columNames, "排序字段不合法");
        // 构建查询语句
        SelectStatementProvider selectStatementProvider = ruleQueryBuilder.buildDataQuery(condition, pageRequest);

        System.out.println(selectStatementProvider.getSelectStatement());

        // 构建总数查询语句
        SelectStatementProvider countQuery = ruleQueryBuilder.buildCountQuery(condition);
        System.out.println(countQuery.getSelectStatement());

        return PaginationUtils.paginate(pageRequest,
                () -> ruleMapper.count(countQuery),
                () -> ruleCustomMapper.findByCondition(selectStatementProvider));

    }

}

```

### 7. Controller层：

```java

package com.example.demo.controller;

import com.example.demo.common.model.page.PageResult;
import com.example.demo.common.model.response.Result;
import com.example.demo.model.dto.request.RuleQueryPageRequest;
import com.example.demo.model.dto.response.RuleWithLatestVersionDTO;
import com.example.demo.service.RuleService;


import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequestMapping("/api")
@Validated
public class RuleController {

    private final RuleService ruleService;

    @Autowired
    public RuleController(RuleService ruleService) {
        this.ruleService = ruleService;
    }


    @PostMapping("/rule")
    public Result<PageResult<RuleWithLatestVersionDTO>> queryRule(@Valid @RequestBody RuleQueryPageRequest request) {

        PageResult<RuleWithLatestVersionDTO> pageResult = ruleService.findByCondition(request.getQueryCondition(), request.getPageRequest());

        return Result.success(pageResult);
    }
}


```


## 总结

自己封装分页查询虽然代码量稍多，但可控性强，避免了PageHelper的线程安全问题，适合对分页有定制需求或高并发场景。
