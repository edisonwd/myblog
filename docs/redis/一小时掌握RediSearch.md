# 一小时掌握RediSearch

# 一、简介

RediSearch 提供了一种简单且高效的方式，可以基于任意字段（二级索引）对数据进行索引，并在已索引的数据集上执行搜索和聚合操作。
RediSearch主要提供了如下功能：
- 丰富的查询语言
- JSON 和哈希文档的增量索引
- 向量搜索
- 全文搜索
- 地理空间查询
- 聚合

在本教程中，你将学习如何使用 **redis-stack** 镜像来运行 [redisearch 模块](https://redis.io/docs/latest/develop/ai/search-and-query/)，该模块为 Redis 提供了索引和全文搜索等功能。


# 二、安装 RediSearch

有多种方式可以运行 RediSearch：

* 从 [源码](https://github.com/RediSearch/RediSearch) 构建并安装到现有的 Redis 实例中
* 使用 [Docker](https://hub.docker.com/r/redis/redis-stack)

我们现在使用 Docker 方式。
**1.1 安装docker**
如果你使用 mac 可以考虑使用 [Colima](https://github.com/abiosoft/colima) ， Colima 是一个开源的 Docker 容器运行时，旨在通过最小化设置运行容器和 Kubernetes。

在mac中安装 colima 命令：
```sh
brew install colima
```
安装成功后，启动 colima 命令如下：
```sh
colima start
```
**1.2 启动 Redis 实例**

执行下面的命令启动 redis-stack 容器
```shell
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

> 将在 `http://localhost:8001` 上启动 Redis Insight GUI
>

安装成功后我们可以通过 docker ps 命令查看容器的运行信息：

```shell
docker ps
```

使用下面的命令进入 docker 容器：

```shell
docker exec -it redis-stack bash
```

接着我们通过 redis-cli 连接测试使用 redis 服务：

```shell
redis-cli
```

现在你已经拥有了一个运行中的 Redis 实例，并且 RediSearch 模块已安装。接下来让我们开始探索它的基本功能。


# 三、创建索引

在创建索引之前，我们先来介绍数据集并插入一些数据。

## 示例数据集

在本项目中，我们将使用一个简单的电影数据集。目前所有记录均为英文内容。关于多语言支持的更多知识将在其他教程中介绍。

一部电影包含以下属性：

* **`movie_id`** ：电影的唯一 ID（数据库内部标识）
* **`title`** ：电影标题
* **`plot`** ：电影剧情简介
* **`genre`** ：电影类型（目前每部电影只包含一个类型）
* **`release_year`** ：上映年份（数值型）
* **`rating`** ：公众评分（数值）
* **`votes`** ：评分人数
* **`poster`** ：电影海报链接
* **`imdb_id`** ：该电影在 [IMDB](https://imdb.com) 数据库中的 ID

---

### 键名与数据结构

作为 Redis 开发者，在构建应用时首要考虑的问题之一是定义键名和数据结构（即数据建模）。

在 Redis 中定义键名的一种常见方式是使用特定的命名模式。例如，在本应用中，数据库可能涉及多种业务对象：电影、演员、剧院、用户等，我们可以采用如下命名模式：

* `业务对象:ID`

例如：
* `movie:001` 表示 ID 为 001 的电影
* `user:001` 表示 ID 为 001 的用户

对于电影信息，建议使用 Redis 的 [Hash](https://redis.io/topics/data-types#hashes) 数据结构。

**Redis Hash 允许将电影的所有属性组织为独立字段，这不仅便于管理，也使得 RediSearch 能够根据索引定义对这些字段进行索引。**

---

## 插入电影数据

现在让我们向数据库中添加一些数据，插入几部电影。你可以使用 `redis-cli` 或 [Redis Insight](https://redis.io/insight/) 工具完成操作。

> **如果使用 vs code 可以考虑使用插件 **[**Redis for VS Code**](https://marketplace.visualstudio.com/items?itemName=redis.redis-for-vscode)** 连接到 Redis 实例进行后续的操作**
>

连接到 Redis 实例后，运行以下命令：

```bash
> HSET movie:11002 title "Star Wars: Episode V - The Empire Strikes Back" plot "After the Rebels are brutally overpowered by the Empire on the ice planet Hoth, Luke Skywalker begins Jedi training with Yoda, while his friends are pursued by Darth Vader and a bounty hunter named Boba Fett all over the galaxy." release_year 1980 genre "Action" rating 8.7 votes 1127635 imdb_id tt0080684

> HSET movie:11003 title "The Godfather" plot "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son." release_year 1972 genre "Drama" rating 9.2 votes 1563839 imdb_id tt0068646

> HSET movie:11004 title "Heat" plot "A group of professional bank robbers start to feel the heat from police when they unknowingly leave a clue at their latest heist." release_year 1995 genre "Thriller" rating 8.2 votes 559490 imdb_id tt0113277

> HSET "movie:11005" title "Star Wars: Episode VI - Return of the Jedi" genre "Action" votes 906260 rating 8.3 release_year 1983  plot "The Rebels dispatch to Endor to destroy the second Empire's Death Star." ibmdb_id "tt0086190" 
```

现在可以通过电影 ID 获取其信息。例如，获取某部电影的标题和评分：

```bash
> HMGET movie:11002 title rating

1) "Star Wars: Episode V - The Empire Strikes Back"
2) "8.7"
```

> **中文在控制台无法正常显示，可以在 Redis Insight GUI 中查看，访问：http://localhost:8001**
>

你也可以通过以下命令增加电影评分：

```bash
> HINCRBYFLOAT movie:11002 rating 0.1
"8.8"
```

但如何根据“上映年份”、“评分”或“标题”来查询一部或多部电影呢？

一种方法是读取所有电影数据，逐一检查每个字段，然后返回符合条件的结果——显然，这是一种非常低效的做法。

传统上，Redis 开发者会手动使用 SET 或 SORTED SET 结构创建自定义的二级索引，指向原始的 Hash 数据。但这需要复杂的设计和实现。

而 RediSearch 模块正是为了解决这个问题而诞生的。

---

## RediSearch 与索引机制

RediSearch 极大地简化了这一过程，它提供了一种简单且自动的方式来为 Redis Hash 创建二级索引。（未来还将支持更多数据结构）

![Secondary Index](https://github.com/RediSearch/redisearch-getting-started/blob/master/docs/images/secondary-index.png?raw=true)

使用 RediSearch 时，若要基于某个字段进行查询，必须先对该字段建立索引。下面我们为电影数据索引以下字段：

* 标题（Title）
* 上映年份（Release Year）
* 评分（Rating）
* 类型（Genre）

创建索引时需要定义：

* 要索引的数据：所有键名以 `movie:` 开头的 *Hash*
* 要索引的字段及其类型（通过 Schema 定义）

> ⚠️ **警告：不要索引所有字段**
>
> 索引会占用内存空间，并且在主数据更新时也需要同步更新索引。因此，请谨慎设计索引，并根据实际需求保持其定义的最新状态。

---

### 创建索引
使用以下命令创建索引：

```plain
> FT.CREATE idx:movie ON hash PREFIX 1 "movie:" SCHEMA title TEXT SORTABLE release_year NUMERIC SORTABLE rating NUMERIC SORTABLE genre TAG SORTABLE
```

在执行命令之前，我们先详细解析这条命令：

+ `FT.CREATE`：根据指定规范创建索引。
+ `idx:movie`：索引的名称。索引名称将用于所有相关键名，建议保持简短。
+ `ON hash`：要索引的数据结构类型。_支持 hash 和 json 。_
+ `PREFIX 1 "movie:"`：需要被索引的键的前缀。这是一个列表，因为我们只想索引 `movie:*` 类型的键，所以数量为 1。如果你还想同时索引具有相同字段的 `tv_show:*` 键，可以写成：`PREFIX 2 "movie:" "tv_show:"`
+ `SCHEMA ...`：定义索引的模式，包括字段及其类型。如命令所示，我们使用了 TEXT（文本）、NUMERIC（数值）、TAG（标签）以及 SORTABLE（可排序）参数。

你可以在 [官方文档](https://redis.io/docs/latest/commands/ft.create/) 中了解更多关于 `FT.CREATE` 命令的信息。

你可以使用以下命令查看索引的详细信息：

```plain
> FT.INFO idx:movie
```


# 四、查询数据

数据库中已包含了几部电影和一个索引，现在可以执行一些查询操作了。


## 查询示例

### **示例：查找所有标题中包含 "`war`" 的电影**

```bash
> FT.SEARCH idx:movie "war"

1) (integer) 2
2) "movie:11005"
3)  1) "title"
    2) "Star Wars: Episode VI - Return of the Jedi"
    ...
   14) "tt0086190"
4) "movie:11002"
5)  1) "title"
    2) "Star Wars: Episode V - The Empire Strikes Back"
    ...
   13) "imdb_id"
   14) "tt0080684"
```

`FT.SEARCH` 命令返回一个结果列表，第一个值是匹配结果的数量，随后是具体的元素（键名与字段）。

你可以看到，尽管你只使用了“war”这个词，但系统仍然找到了 “Star Wars: Episode V - The Empire Strikes Back” 这部电影。这是因为标题字段被作为文本（TEXT）进行了索引，因此该字段在索引时经过了分词 和 [词干提取](https://redis.io/docs/latest/develop/ai/search-and-query/advanced-concepts/stemming/) 处理。

> <font style="color:rgb(51, 51, 51);">添加中文文档时，为索引器设置 LANGUAGE chinese 以正确标记术语。 如果您使用默认语言，则会根据标点符号和空格提取搜索词。 中文分词器使用分段算法（通过 </font>[Friso](https://github.com/lionsoul2014/friso)<font style="color:rgb(51, 51, 51);">），该算法对文本进行分段并根据预定义的字典进行检查。 有关详细信息，请参阅词干提取。</font>
>


稍后我们会更详细地介绍查询语法，进一步了解搜索功能。

你也可以使用 `RETURN` 参数限制返回的字段。例如，运行相同的查询但只返回标题和上映年份：

```bash
> FT.SEARCH idx:movie "war" RETURN 2 title release_year

1) (integer) 2
2) "movie:11005"
3) 1) "title"
   1) "Star Wars: Episode VI - Return of the Jedi"
   2) "release_year"
   3) "1983"
4) "movie:11002"
5) 1) "title"
   1) "Star Wars: Episode V - The Empire Strikes Back"
   2) "release_year"
   3) "1980"
```

这个查询没有指定具体字段，但仍能返回结果，因为 RediSearch 默认会在所有 `TEXT` 类型字段中进行搜索。当前索引中只有 `title` 是 `TEXT` 字段。稍后你会学习如何更新索引以添加更多字段。

如果需要在特定字段上查询，可以使用 `@field:` 语法，例如：

```bash
> FT.SEARCH idx:movie "@title:war" RETURN 2 title release_year
```

---

### **示例：查找包含 "`war`" 但不包含 "`jedi`" 的电影**

在查询中加入 `-jedi`（减号）表示排除包含 “jedi” 的结果。

```bash
> FT.SEARCH idx:movie "war -jedi" RETURN 2 title release_year

1) (integer) 1
2) "movie:11002"
3) 1) "title"
   2) "Star Wars: Episode V - The Empire Strikes Back"
   3) "release_year"
   4) "1980"
```

---

### **示例：使用模糊搜索查找拼写错误的 "`gdfather`"**

如你所见，“godfather” 被误写为 “gdfather”。但通过 [模糊匹配](https://oss.redislabs.com/redisearch/Query_Syntax/#fuzzy_matching) 仍然可以找到它。模糊匹配基于 [莱文斯坦距离（Levenshtein Distance）](https://zh.wikipedia.org/wiki/%E8%8E%B1%E6%96%87%E6%96%AF%E5%9D%A6%E8%B7%9D%E7%A6%BB) 实现。

> <font style="color:rgb(51, 51, 51);">莱文斯坦距离（Levenshtein distance）是编辑距离的一种，用于度量两个字符串通过插入、删除或替换操作转换为彼此所需的最少编辑次数</font>
>

```bash
> FT.SEARCH idx:movie " %gdfather% " RETURN 2 title release_year

1) (integer) 1
2) "movie:11003"
3) 1) "title"
   2) "The Godfather"
   3) "release_year"
   4) "1972"
```

注意：模糊匹配需用 `%` 包裹关键词。

---

### **示例：查找所有类型为 `Thriller` 的电影**

`genre` 字段是以 `TAG` 类型索引的，支持精确匹配查询。

查询 TAG 字段的语法为：`@字段名:{值}`

```bash
> FT.SEARCH idx:movie "@genre:{Thriller}" RETURN 2 title release_year

1) (integer) 1
2) "movie:11004"
3) 1) "title"
   2) "Heat"
   3) "release_year"
   4) "1995"
```

---

### **示例：查找所有类型为 `Thriller` 或 `Action` 的电影**

```bash
> FT.SEARCH idx:movie "@genre:{Thriller|Action}" RETURN 2 title release_year

1) (integer) 3
2) "movie:11004"
3) 1) "title"
   2) "Heat"
   3) "release_year"
   4) "1995"
4) "movie:11005"
5) 1) "title"
   2) "Star Wars: Episode VI - Return of the Jedi"
   3) "release_year"
   4) "1983"
6) "movie:11002"
7) 1) "title"
   2) "Star Wars: Episode V - The Empire Strikes Back"
   3) "release_year"
   4) "1980"
```

关于标签过滤器的更多信息，请参考 [官方文档](https://redis.io/docs/latest/develop/ai/search-and-query/advanced-concepts/query_syntax/#tag-filters)。

---

### **示例：查找类型为 `Thriller` 或 `Action` 且标题不含 `Jedi` 的电影**

```bash
> FT.SEARCH idx:movie "@genre:{Thriller|Action} @title:-jedi" RETURN 2 title release_year

1) (integer) 2
2) "movie:11004"
3) 1) "title"
   2) "Heat"
   3) "release_year"
   4) "1995"
4) "movie:11002"
5) 1) "title"
   2) "Star Wars: Episode V - The Empire Strikes Back"
   3) "release_year"
   4) "1980"
```

---

### **示例：查找 1970 到 1980 年之间（含）上映的所有电影**

`FT.SEARCH` 提供两种方式查询数值字段：

* 使用 `FILTER` 参数  
  或
* 在查询字符串中使用 `@field:[min max]` 语法

```bash
> FT.SEARCH idx:movie * FILTER release_year 1970 1980 RETURN 2 title release_year
```

或

```bash
> FT.SEARCH idx:movie "@release_year:[1970 1980]" RETURN 2 title release_year

1) (integer) 2
2) "movie:11003"
3) 1) "title"
   2) "The Godfather"
   3) "release_year"
   4) "1972"
4) "movie:11002"
5) 1) "title"
   2) "Star Wars: Episode V - The Empire Strikes Back"
   3) "release_year"
   4) "1980"
```

若要排除某个端点值，在数字前加 `( ` 即可。例如排除 1980 年：

```bash
> FT.SEARCH idx:movie "@release_year:[1970 (1980]" RETURN 2 title release_year
```

---

## 插入、更新、删除与过期文档

在本教程中，你已完成以下操作：

1. 创建了几部电影（作为 Redis Hash，我们称之为“文档”），键名为 `movie:*` 模式
2. 使用 `FT.CREATE` 命令创建了索引
3. 使用 `FT.SEARCH` 查询数据

当你创建索引时，通过 `idx:movie ON hash PREFIX 1 "movie:"` 参数，索引引擎会自动扫描所有现有匹配的键并建立索引。之后任何符合该模式的新数据也会被自动索引。

下面我们来验证这一点：先统计电影数量，添加一部新电影，再重新统计：

```bash
> FT.SEARCH idx:movie "*" LIMIT 0 0

1) (integer) 4

> HSET movie:11033 title "Tomorrow Never Dies" plot "James Bond sets out to stop a media mogul's plan to induce war between China and the U.K in order to obtain exclusive global media coverage." release_year 1997 genre "Action" rating 6.5 votes 177732 imdb_id tt0120347

> FT.SEARCH idx:movie "*" LIMIT 0 0

1) (integer) 5
```

新的电影已被自动索引。你可以在任意索引字段上进行搜索：

```bash
> FT.SEARCH idx:movie "never" RETURN 2 title release_year

1) (integer) 1
2) "movie:11033"
3) 1) "title"
   2) "Tomorrow Never Dies"
   3) "release_year"
   4) "1997"
```

现在我们**更新**其中一个字段，并搜索 `007`：

```bash
> HSET movie:11033 title "Tomorrow Never Dies - 007"

> FT.SEARCH idx:movie "007" RETURN 2 title release_year

1) (integer) 1
2) "movie:11033"
3) 1) "title"
   2) "Tomorrow Never Dies - 007"
   3) "release_year"
   4) "1997"
```

当删除一个 Hash 时，索引也会同步更新；同样地，当键过期（TTL）时，索引也会自动清理。

例如，设置这部詹姆斯·邦德电影在 20 秒后过期：

```bash
> EXPIRE "movie:11033" 20
```

你可以运行以下查询，20 秒后你会发现文档已消失，搜索不再返回结果，说明索引已同步更新：

```bash
> FT.SEARCH idx:movie "007" RETURN 2 title release_year

1) (integer) 0
```

> **注意**：当你将 Redis 用作主数据库时，通常不会依赖 TTL 来删除数据。但如果存储的数据是临时性的（例如作为其他数据源或 Web 服务的缓存层、用户会话内容等），则常被称为 “[瞬态搜索（Ephemeral Search）](https://redislabs.com/blog/the-case-for-ephemeral-search/)” 场景：轻量、快速且支持自动过期。

---

## 更多功能

关于索引和搜索，还有更多高级功能可在文档中查阅：

* [FT.SEARCH 命令](https://redis.io/commands/ft.search)
* [查询语法（Query Syntax）](https://redis.io/docs/latest/develop/ai/search-and-query/advanced-concepts/query_syntax/#basic-syntax)

接下来，我们将学习如何查看、修改和删除索引。

# 五、管理索引

## 列出并查看索引

`FT._LIST` 命令可以列出当前数据库中所有的 RediSearch 索引：

```
> FT._LIST
1) "idx:movie"
```

使用 `FT.INFO` 命令可以查看某个特定索引的详细信息：

```
> FT.INFO "idx:movie" 
 
 1) "index_name"
 2) "idx:movie"
 ...
 5) "index_definition"
 ...
 7) "fields"
 ...
9) "num_docs"
10) "4" 
...
```

返回结果包含索引名称、定义、字段列表、文档数量（本例中为 4）等元数据。

---

## 更新索引结构

在开发应用过程中，随着数据库中数据的增加，你可能需要为索引添加新的字段。此时可以使用 `FT.ALTER` 命令来修改现有索引。

例如，为电影索引添加 `plot`（剧情简介）字段：

```
> FT.ALTER idx:movie SCHEMA ADD plot TEXT WEIGHT 0.5
"OK"
```

其中 `WEIGHT` 表示该字段在计算搜索相关性得分时的重要性，是一个加权乘数（默认值为 1）。本例中将 `plot` 的权重设为 0.5，表示其重要性低于 `title`（标题）。

现在我们可以基于新加入索引的字段进行查询：

```
> FT.SEARCH idx:movie "empire @genre:{Action}" RETURN 2 title plot
```

这条查询会查找标题或剧情中包含 “empire” 且类型为 “Action” 的电影，并返回其标题和剧情内容。

---

## 删除索引

你可以使用 `FT.DROPINDEX` 命令删除一个索引：

```
> FT.DROPINDEX idx:movie

"OK"
```

**注意：删除索引不会影响已被索引的 Hash 数据本身**，也就是说，所有电影数据仍然保留在数据库中。

你可以通过以下命令验证数据是否仍在：

```
> SCAN 0 MATCH movie:*

1) "0"
2) 1) "movie:11002"
   2) "movie:11004"
   3) "movie:11003"
   4) "movie:11005"
```

如上所示，所有以 `movie:` 开头的键依然存在。

> 💡 提示：如果希望在删除索引的同时也删除对应的文档（Hash），可以在命令后加上 `DD` 参数：
>
> ```
> FT.DROPINDEX idx:movie DD
> ```

`DD` 表示 "Drop Documents"，执行后不仅会删除索引，还会清除所有被索引的 Redis 键。




# 六、示例数据集

在之前的步骤中，你只使用了少量电影数据。现在让我们导入更多数据：

* 更多的电影 —— 用于探索更多查询方式  
* 剧院信息 —— 用于探索 Redis 的地理空间（geospatial）功能  
* 用户数据 —— 用于进行聚合分析（aggregations）

---

## 数据集说明

### **电影（Movies）**

文件 [import_movies.redis](https://github.com/RediSearch/redisearch-getting-started/blob/master/sample-app/redisearch-docker/dataset/import_movies.redis) 是一个脚本，用于创建 922 个 Hash 结构。

电影的 Hash 包含以下字段：

* **`movie:id`** ：电影的唯一 ID，数据库内部标识（作为 Hash 的键名）
* **`title`** ：电影标题
* **`plot`** ：电影剧情简介
* **`genre`** ：电影类型，目前每部电影只有一个类型
* **`release_year`** ：电影上映年份（数值型）
* **`rating`** ：公众评分（数值）
* **`votes`** ：评分人数
* **`poster`** ：电影海报链接
* **`imdb_id`** ：该电影在 [IMDB](https://imdb.com) 数据库中的 ID

<details> 
  <summary>示例数据: <b>movie:343</b></summary>
  <table>
      <thead>
        <tr>
            <th>字段</th>
            <th>值</th>
        </tr>
    </thead>
  <tbody>
    <tr>
        <th>title</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        Spider-Man
        </td>
    </tr>
    <tr>
        <th>plot</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        当一个性格内向害羞的高中生被基因改造的蜘蛛咬伤后，他获得了类似蜘蛛的能力，并最终必须以超级英雄的身份对抗邪恶，尤其是在家庭遭遇悲剧之后。
        </td>
    </tr>
    <tr>
        <th>genre</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        Action
        </td>
    </tr>
    <tr>
        <th>release_year</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        2002
        </td>
    </tr>
    <tr>
        <th>rating</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        7.3
        </td>
    </tr>
    <tr>
        <th>votes</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        662219
        </td>
    </tr>
    <tr>
        <th>poster</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        https://m.media-amazon.com/images/M/MV5BZDEyN2NhMjgtMjdhNi00MmNlLWE5YTgtZGE4MzNjMTRlMGEwXkEyXkFqcGdeQXVyNDUyOTg3Njg@._V1_SX300.jpg
        </td>
    </tr>
    <tr>
        <th>imdb_id</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        tt0145487
        </td>
    </tr>
    <tbody>
  </table>
</details>

---

### **剧院（Theaters）**

文件 [import_theaters.redis](https://github.com/RediSearch/redisearch-getting-started/blob/master/sample-app/redisearch-docker/dataset/import_theaters.redis) 是一个脚本，用于创建 117 个 Hash（用于地理空间查询）。  
*注意：此数据集是纽约市的剧院列表，不全是电影院，但对本项目影响不大。*

剧院 Hash 包含以下字段：

* **`theater:id`** ：剧院的唯一 ID，数据库内部标识（作为 Hash 键名）
* **`name`** ：剧院名称
* **`address`** ：街道地址
* **`city`** ：城市（本数据集中所有剧院都在纽约）
* **`zip`** ：邮政编码
* **`phone`** ：联系电话
* **`url`** ：剧院网站 URL
* **`location`** ：包含 `经度,纬度` 的字符串，用于构建地理索引字段

<details> 
 <summary>示例数据: <b>theater:20</b></summary>
  <table>
      <thead>
        <tr>
            <th>字段</th>
            <th>值</th>
        </tr>
    </thead>
  <tbody>
    <tr>
        <th>name</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        Broadway Theatre
        </td>
    </tr>
    <tr>
        <th>address</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        1681 Broadway
        </td>
    </tr>
    <tr>
        <th>city</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        New York
        </td>
    </tr>
    <tr>
        <th>zip</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        10019
        </td>
    </tr>
    <tr>
        <th>phone</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        212 944-3700
        </td>
    </tr>
    <tr>
        <th>url</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        http://www.shubertorganization.com/theatres/broadway.asp
        </td>
    </tr>
    <tr>
        <th>location</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        -73.98335054631019,40.763270202723625
        </td>
    </tr>
    <tbody>
  </table>
</details>

---

### **用户（Users）**

文件 [import_users.redis](https://github.com/RediSearch/redisearch-getting-started/blob/master/sample-app/redisearch-docker/dataset/import_users.redis) 是一个脚本，用于创建 5996 个 Hash。

用户 Hash 包含以下字段：

* **`user:id`** ：用户的唯一 ID
* **`first_name`** ：名字
* **`last_name`** ：姓氏
* **`email`** ：邮箱地址
* **`gender`** ：性别（`female` / `male`）
* **`country`** ：国家名称
* **`country_code`** ：国家代码
* **`city`** ：所在城市
* **`longitude`** ：经度
* **`latitude`** ：纬度
* **`last_login`** ：上次登录时间，以 Unix 时间戳（Epoch 时间）表示
* **`ip_address`** ：IP 地址

<details> 
 <summary>示例数据: <b>user:3233</b></summary>
  <table>
      <thead>
        <tr>
            <th>字段</th>
            <th>值</th>
        </tr>
    </thead>
  <tbody>
    <tr>
        <th>first_name</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        Rosetta
        </td>
    </tr>
    <tr>
        <th>last_name</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        Olyff
        </td>
    </tr>
    <tr>
        <th>email</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        rolyff6g@163.com
        </td>
    </tr>
    <tr>
        <th>gender</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        female
        </td>
    </tr>
    <tr>
        <th>country</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        China
        </td>
    </tr>
    <tr>
        <th>country_code</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        CN
        </td>
    </tr>
    <tr>
        <th>city</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        Huangdao
        </td>
    </tr>
    <tr>
        <th>longitude</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        120.04619
        </td>
    </tr>
    <tr>
        <th>latitude</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        35.872664
        </td>
    </tr>
    <tr>
        <th>last_login</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        1570386621
        </td>
    </tr>
    <tr>
        <th>ip_address</th>
        <td style='font-family:monospace; font-size: 0.875em; "'>
        218.47.90.79
        </td>
    </tr>
    <tbody>
  </table>
</details>

---

## 导入电影、剧院和用户数据

在导入数据之前，请先清空数据库：

```
> FLUSHALL
```

最简单的导入方式是使用 `redis-cli` 执行以下终端命令：

```bash
$ redis-cli -h localhost -p 6379 < import_movies.redis

$ redis-cli -h localhost -p 6379 < import_theaters.redis

$ redis-cli -h localhost -p 6379 < import_users.redis
```

你可以使用 Redis Insight 或 `redis-cli` 查看数据内容：

```bash
> HMGET "movie:343" title release_year genre

1) "Spider-Man"
2) "2002"
3) "Action"

> HMGET "theater:20" name location
1) "Broadway Theatre"
2) "-73.98335054631019,40.763270202723625"

> HMGET "user:343" first_name last_name last_login
1) "Umeko"
2) "Castagno"
3) "1574769122"
```

你也可以使用 `DBSIZE` 命令查看当前数据库中的键数量。

---

## 创建索引

### **创建 `idx:movie` 索引：**

```bash
> FT.CREATE idx:movie ON hash PREFIX 1 "movie:" SCHEMA title TEXT SORTABLE plot TEXT WEIGHT 0.5 release_year NUMERIC SORTABLE rating NUMERIC SORTABLE votes NUMERIC SORTABLE genre TAG SORTABLE

"OK"
```

电影数据现已建立索引。你可以运行 `FT.INFO "idx:movie"` 命令并查看返回的 `num_docs` 值（应为 922）。

---

### **创建 `idx:theater` 索引：**

此索引主要用于展示 RediSearch 的地理空间查询能力。

此前我们创建过三种类型的索引字段：

* `Text`（文本）
* `Numeric`（数值）
* `Tag`（标签）

现在我们将引入第四种类型：`Geo`（地理坐标）

剧院数据中的 `location` 字段包含了经度和纬度信息，在索引中将这样使用：

```bash
> FT.CREATE idx:theater ON hash PREFIX 1 "theater:" SCHEMA name TEXT SORTABLE location GEO

"OK"
```

剧院数据也已建立索引。运行 `FT.INFO "idx:theater"` 可查看 `num_docs` 是否为 117。

---

### **创建 `idx:user` 索引：**

```bash
> FT.CREATE idx:user ON hash PREFIX 1 "user:" SCHEMA gender TAG country TAG SORTABLE last_login NUMERIC SORTABLE location GEO

"OK"
```

---

下一步：[查询电影数据库](007-query-movies.md)


# 七、查询电影数据集

如本教程前面所述，RediSearch 的目标之一是提供丰富的查询功能，例如：

* 简单和复杂的查询条件
* 排序（Sorting）
* 分页（Pagination）
* 计数（Counting）



## 条件查询（Conditions）

学习 RediSearch 查询能力的最佳方式是从了解各种条件选项开始。

<details> 
  <summary>
  <i><b>
  查找所有标题或剧情中包含“heat”或相关词汇的电影
  </b></i>
  </summary>

```
> FT.SEARCH "idx:movie" "heat" RETURN 2 title plot

1) (integer) 4
2) "movie:1141"
3) 1) "title"
   2) "Heat"
   3) "plot"
   4) "A group of professional bank robbers start to feel the heat from police when they unknowingly leave a clue at their latest heist."
4) "movie:818"
5) 1) "title"
   2) "California Heat"
   3) "plot"
   4) "A lifeguard bets he can be true to just one woman."
6) "movie:736"
7) 1) "title"
   2) "Chicago Justice"
   3) "plot"
   4) "The State's Attorney's dedicated team of prosecutors and investigators navigates heated city politics and controversy head-on,while fearlessly pursuing justice."
8) "movie:1109"
9) 1) "title"
   2) "Love & Hip Hop: Miami"
   3) "plot"
   4) "'Love and Hip Hop Miami' turns up the heat and doesn't hold back in making the 305 the place to be. Multi-platinum selling hip-hop legend Trick Daddy is back in the studio collaborating ..."
```

第一行返回匹配结果的数量（`4` 部电影），随后是具体的电影列表。

这个查询是一个“无字段限定”的查询，意味着查询引擎会：
* 在索引中的所有 `TEXT` 字段（`title` 和 `plot`）中搜索
* 搜索关键词 `heat` 及其词根相关的词（例如 `heated`），这就是为什么 `movie:736` 也会被返回（得益于 [词干提取](https://oss.redislabs.com/redisearch/Stemming/) 功能）
* 按评分（score）排序返回结果。注意：`title` 字段权重为 1.0，`plot` 权重为 0.5，因此当关键词出现在标题中时，得分更高。

---
</details>

<details> 
  <summary>
  <i><b>
    查找标题中包含“heat”或相关词汇的所有电影
  </b></i>
  </summary>

此时需要使用 `@title` 语法将条件限定在 `title` 字段上：

```
> FT.SEARCH "idx:movie" "@title:heat" RETURN 2 title plot
1) (integer) 2
2) "movie:1141"
3) 1) "title"
   2) "Heat"
   3) "plot"
   4) "A group of professional bank robbers start to feel the heat from police when they unknowingly leave a clue at their latest heist."
4) "movie:818"
5) 1) "title"
   2) "California Heat"
   3) "plot"
   4) "A lifeguard bets he can be true to just one woman."
```

这次只返回了 2 部电影。

---
</details>

<details> 
  <summary>
  <i><b>
  查找标题包含“heat”但不包含“california”的所有电影
  </b></i>
  </summary>

你需要将字段条件用括号括起来，并在 `california` 前加上 `-` 表示排除：

```
> FT.SEARCH "idx:movie" "@title:(heat -california)" RETURN 2 title plot
1) (integer) 1
2) "movie:1141"
3) 1) "title"
   2) "Heat"
   3) "plot"
   4) "A group of professional bank robbers start to feel the heat from police when they unknowingly leave a clue at their latest heist."
```

仅返回一部电影。

**注意**：如果不加 `( ... )`，`-california` 条件会被应用到所有文本字段上。

你可以通过以下两个查询验证区别：

```
> FT.SEARCH "idx:movie" "@title:(heat -woman)" RETURN 2 title plot
```

```
> FT.SEARCH "idx:movie" "@title:heat -woman" RETURN 2 title plot
```

你会发现第一个查询只在标题中排除含 “woman” 的电影，返回 “Heat” 和 “California Heat”；而第二个查询会排除任何字段（如 `plot`）中包含 “woman” 的电影，因此 “California Heat” 被排除。

---
</details>

<details> 
  <summary>
  <i><b>
  查找类型为 'Drama' 且标题包含 'heat' 的所有电影
  </b></i>
  </summary>

如前所述，电影索引包含：
* `title` 和 `plot` 作为 `TEXT` 类型
* `genre` 作为 `TAG` 类型

之前我们已经了解如何对 `TEXT` 字段设置条件。

[TAG](https://oss.redislabs.com/redisearch/Tags/) 类型略有不同：索引引擎 **不会进行词干提取**，必须完全匹配。

要对 TAG 字段设置条件，需使用 `@field:{value}` 语法，大括号 `{...}` 表示这是一个 TAG 查询：

```
>  FT.SEARCH "idx:movie" "@title:(heat) @genre:{Drama} " RETURN 3 title plot genre
1) (integer) 1
2) "movie:1141"
3) 1) "title"
   2) "Heat"
   3) "plot"
   4) "A group of professional bank robbers start to feel the heat from police when they unknowingly leave a clue at their latest heist."
   5) "genre"
   6) "Drama"
```

此查询对两个字段设置了条件，并对 `genre` 进行了精确匹配。

**TAG 字段适用于需要字符串精确匹配的场景。**

---
</details>

<details> 
  <summary>
  <i><b>
  查找类型为 'Drama' 或 'Comedy' 且标题包含 'heat' 的所有电影
  </b></i>
  </summary>

与前一个查询类似，可以使用 `|` 符号在 `{}` 内列出多个值表示“或”关系：

```
> FT.SEARCH "idx:movie" "@title:(heat)  @genre:{Drama|Comedy} " RETURN 3 title plot genre

1) (integer) 2
2) "movie:1141"
3) 1) "title"
   2) "Heat"
   3) "plot"
   4) "A group of professional bank robbers start to feel the heat from police when they unknowingly leave a clue at their latest heist."
   5) "genre"
   6) "Drama"
4) "movie:818"
5) 1) "title"
   2) "California Heat"
   3) "plot"
   4) "A lifeguard bets he can be true to just one woman."
   5) "genre"
   6) "Comedy"
```

你也可以把 `|` 放在整个条件之间，比如查找标题含 "heat"，或类型是 Drama 或 Comedy 的所有电影：

```
FT.SEARCH "idx:movie" "@title:(heat) | @genre:{Drama|Comedy} " RETURN 3 title plot genre
```

---
</details>

<details> 
  <summary>
  <i><b>查找类型为 'Mystery' 或 'Thriller'，且上映年份为 2014 或 2018 的所有电影</b></i>
  </summary>

这个查询引入了对数值字段（`release_year`）的查询。

与之前类似，使用 `@field:` 语法，但数值字段需要指定一个范围区间。

这里使用两个区间条件并用 `|`（OR）连接：

```
> FT.SEARCH "idx:movie" "@genre:{Mystery|Thriller} (@release_year:[2018 2018] | @release_year:[2014 2014] )"   RETURN 3 title release_year genre

1) (integer) 3
2) "movie:461"
3) 1) "title"
   2) "The Boat ()"
   3) "release_year"
   4) "2018"
   5) "genre"
   6) "Mystery"
4) "movie:65"
5) 1) "title"
   2) "The Loft"
   3) "release_year"
   4) "2014"
   5) "genre"
   6) "Mystery"
6) "movie:989"
7) 1) "title"
   2) "Los Angeles Overnight"
   3) "release_year"
   4) "2018"
   5) "genre"
   6) "Thriller"
```

---
</details>

## 小结

* **无字段查询**：作用于所有 `TEXT` 字段，支持词干扩展（stemming）
* **限定字段查询**：使用 `@field:` 语法
* **多条件组合**：默认是“与”（AND）关系；若需“或”（OR）关系，使用 `|` 符号

---

## 排序（Sort）

查询数据时常见的需求是对结果按特定字段排序，并进行分页浏览。

<details> 
  <summary>
  <i><b>查询所有 `Action` 类型的电影，按上映年份从最新到最旧排序</b></i>
  </summary>

```
> FT.SEARCH "idx:movie" "@genre:{Action}"  SORTBY release_year DESC RETURN 2 title release_year
 1) (integer) 186
 2) "movie:360"
 3) 1) "release_year"
    2) "2019"
    3) "title"
    4) "Spider-Man: Far from Home"
 ...
20) "movie:278"
21) 1) "release_year"
    2) "2016"
    3) "title"
    4) "Mechanic: Resurrection"
```

第一行返回匹配的文档数量（186 部）。

`FT.SEARCH` 默认返回前 10 条结果。下一查询将展示如何分页。

**注意**：`FT.SEARCH` 中只能使用一个 `SORTBY` 子句。如果想按多个字段排序（例如先按 `genre` 升序，再按 `release_year` 降序），需使用 `FT.AGGREGATE`，这将在下一部分介绍。

另外，用于 `SORTBY` 的字段必须在索引定义中标记为 `SORTABLE`。


</details>

---

## 分页（Paginate）

<details> 
  <summary>
  <i><b>查询所有 `Action` 类型的电影，按上映年份从最旧到最新排序，每批返回 100 部电影</b></i>
  </summary>

```
> FT.SEARCH "idx:movie" "@genre:{Action}" LIMIT 0 100  SORTBY release_year ASC RETURN 2 title release_year
  1) (integer) 186
  2) "movie:892"
  3) 1) "release_year"
     2) "1966"
     3) "title"
     4) "Texas,Adios"
...  
200) "movie:12"
201) 1) "release_year"
     2) "2014"
     3) "title"
     4) "Fury"
```

结果与前例相似：
* 共找到 186 部电影
* 第一部是最老的（1966 年）
* 批次中最晚的是 2014 年上映的

要获取下一批，请修改 `LIMIT` 参数：

```
> FT.SEARCH "idx:movie" "@genre:{Action}" LIMIT 100 200  SORTBY release_year ASC RETURN 2 title release_year
```

</details>

---

## 计数（Count）

<details> 
  <summary>
  <i><b>统计 'Action' 类型电影的数量</b></i>
  </summary>

根据之前的示例，使用 `LIMIT 0 0` 可以只返回匹配文档的数量，不返回实际数据：

```
> FT.SEARCH "idx:movie" "@genre:{Action}" LIMIT 0 0

1) (integer) 186
```

---
</details>

<details> 
  <summary>
  <i><b>统计 2017 年上映的 'Action' 类型电影数量</b></i>
  </summary>

同样使用 `LIMIT 0 0`：

```
> FT.SEARCH "idx:movie" "@genre:{Action}" FILTER release_year 2017 2017 LIMIT 0 0

1) (integer) 5
```

也可以使用以下语法：

```
> FT.SEARCH "idx:movie" "@genre:{Action} @release_year:[2017 2017]" LIMIT 0 0

1) (integer) 5
```

</details>

---

## 地理空间查询（Geospatial Queries）

<details> 
  <summary>
  <i><b>查找距离 MOMA 不足 400 米的所有剧院名称和地址</b></i>
  </summary>

假设你在位于 “11 W 53rd St, New York” 的现代艺术博物馆（MOMA），想查找周围 400 米内的所有剧院。

首先确定当前位置的经纬度：`-73.9798156,40.7614367`，然后执行以下查询：

```
> FT.SEARCH "idx:theater" "@location:[-73.9798156 40.7614367 400 m]" RETURN 2 name address

1) (integer) 5
 2) "theater:30"
 3) 1) "name"
    2) "Ed Sullivan Theater"
    3) "address"
    4) "1697 Broadway"
...
10) "theater:115"
11) 1) "name"
    2) "Winter Garden Theatre"
    3) "address"
    4) "1634 Broadway"
```


</details>


# 八、聚合查询（Aggregation）

除了像使用 `FT.SEARCH` 命令那样以文档列表的形式检索数据外，应用程序常见的另一个需求是进行“聚合”操作。

例如，在查看电影数据时，你可能希望按年份对电影数量进行分组，并从最新年份开始排序显示。

为此，RediSearch 提供了 `FT.AGGREGATE` 命令，它通过一个**数据处理流水线（pipeline）** 来描述聚合操作。

下面我们来看一些示例。

---

## 分组与排序（Group By & Sort By）

<details> 
  <summary>
  <i><b>
  按年份统计电影数量
  </b></i>
  </summary>

```
> FT.AGGREGATE "idx:movie" "*" GROUPBY 1 @release_year REDUCE COUNT 0 AS nb_of_movies

 1) (integer) 60
 2) 1) "release_year"
    2) "1964"
    3) "nb_of_movies"
    4) "9"
 ...   
 61) 1) "release_year"
    2) "2010"
    3) "nb_of_movies"
    4) "15"
```

此命令：
- 查询所有电影（`*`）
- 按 `release_year` 字段分组（`GROUPBY 1 @release_year`）
- 使用 `REDUCE COUNT 0` 统计每组的数量，并命名为 `nb_of_movies`

返回结果共 60 个不同的年份分组。

---
</details>

<details> 
  <summary>
  <i><b>
  按年份统计电影数量，从最新到最旧排序
  </b></i>
  </summary>

```
> FT.AGGREGATE "idx:movie" "*" GROUPBY 1 @release_year REDUCE COUNT 0 AS nb_of_movies SORTBY 2 @release_year DESC 

1) (integer) 60
 2) 1) "release_year"
    2) "2019"
    3) "nb_of_movies"
    4) "14"
 ...   
11) 1) "release_year"
    2) "2010"
    3) "nb_of_movies"
    4) "15"
```

在上一查询基础上添加了 `SORTBY @release_year DESC`，使结果按年份从新到旧排序。

---
</details>

<details> 
  <summary>
  <i><b>
  按类型统计电影数量、总评分人数和平均评分
  </b></i>
  </summary>

```
> FT.AGGREGATE idx:movie "*" GROUPBY 1 @genre REDUCE COUNT 0 AS nb_of_movies REDUCE SUM 1 votes AS nb_of_votes REDUCE AVG 1 rating AS avg_rating SORTBY 4 @avg_rating DESC @nb_of_votes DESC


 1) (integer) 26
 2) 1) "genre"
    2) "fantasy"
    3) "nb_of_movies"
    4) "1"
    5) "nb_of_votes"
    6) "1500090"
    7) "avg_rating"
    8) "8.8"
...
11) 1) "genre"
    2) "romance"
    3) "nb_of_movies"
    4) "2"
    5) "nb_of_votes"
    6) "746"
    7) "avg_rating"
    8) "6.65"
```

该查询：
- 按 `genre` 分组
- 计算每类电影数量（`COUNT`）
- 累加总评分人数（`SUM votes`）
- 计算平均评分（`AVG rating`）
- 最后按平均评分降序、总评分人数降序排序

---
</details>

<details> 
  <summary>
  <i><b>
  按国家统计女性用户数量，并从高到低排序
  </b></i>
  </summary>

```
> FT.AGGREGATE idx:user "@gender:{female}" GROUPBY 1 @country REDUCE COUNT 0 AS nb_of_users SORTBY 2 @nb_of_users DESC

 1) (integer) 193
 2) 1) "country"
    2) "china"
    3) "nb_of_users"
    4) "537"
...
11) 1) "country"
    2) "ukraine"
    3) "nb_of_users"
    4) "72"
```

此查询筛选出性别为女性的用户，按国家分组并统计人数，最后按数量降序排列。

---
</details>

---

## 应用函数（Apply Functions）

### 时间提取与转换

<details> 
  <summary>
  <i><b>
  按年月统计登录次数
  </b></i>
  </summary>

`idx:user` 索引中的 `last_login` 字段存储的是 Unix 时间戳（Epoch 时间）。

RediSearch 的聚合功能允许对每条记录应用变换操作，这通过 [APPLY](https://oss.redislabs.com/redisearch/Aggregations/#apply_expressions) 参数实现。

本例中，我们使用 [日期/时间函数](https://oss.redislabs.com/redisearch/Aggregations/#list_of_datetime_apply_functions) 从时间戳中提取年份和月份：

```
> FT.AGGREGATE idx:user * APPLY year(@last_login) AS year APPLY "monthofyear(@last_login) + 1" AS month GROUPBY 2 @year @month REDUCE count 0 AS num_login SORTBY 4 @year ASC @month ASC

 1) (integer) 13
 2) 1) "year"
    2) "2019"
    3) "month"
    4) "9"
    5) "num_login"
    6) "230"
...
14) 1) "year"
    2) "2020"
    3) "month"
    4) "9"
    5) "num_login"
    6) "271"
```

说明：
- `year(@last_login)`：提取年份
- `monthofyear(@last_login) + 1`：提取月份（注意：`monthofyear()` 返回 0–11，加 1 后变为 1–12）
- 按年和月分组，统计登录次数
- 按年升序、月升序排序

---
</details>

<details> 
  <summary>
  <i><b>
  按星期几统计登录次数
  </b></i>
  </summary>

利用日期时间函数也可以提取一周中的某天，来看看用户的登录行为在一周中是如何分布的：

```
> FT.AGGREGATE idx:user * APPLY "dayofweek(@last_login) +1" AS dayofweek GROUPBY 1 @dayofweek REDUCE count 0 AS num_login SORTBY 2 @dayofweek ASC

1) (integer) 7
2) 1) "dayofweek"
   2) "1"
   3) "num_login"
   4) "815"
...
8) 1) "dayofweek"
   2) "7"
   3) "num_login"
   4) "906"
```

这里 `dayofweek()` 返回 0（星期日）到 6（星期六），加 1 后变为 1 到 7，分别代表星期一至星期日（或自定义解释）。结果展示了每天的登录总数。

---
</details>

---

## 过滤（Filter）

在之前的例子中，我们使用了查询字符串参数来选择全部文档（`"*"`）或子集（如 `"@gender:{female}"`）。

此外，还可以使用 **谓词表达式（predicate expression）** 对聚合流水线中的中间结果进行过滤。这种过滤是在查询之后、基于当前流水线状态进行的，使用 [FILTER](https://oss.redislabs.com/redisearch/Aggregations/#filter_expressions) 参数实现。

<details> 
  <summary>
  <i><b>
  统计各国女性用户数量（排除中国），只保留超过 100 人的国家，并按数量从高到低排序
  </b></i>
  </summary>

```
> FT.AGGREGATE idx:user "@gender:{female}" GROUPBY 1 @country  REDUCE COUNT 0 AS nb_of_users  FILTER "@country!='china' && @nb_of_users > 100" SORTBY 2 @nb_of_users DESC

1) (integer) 163
2) 1) "country"
   2) "indonesia"
   3) "nb_of_users"
   4) "309"
...
6) 1) "country"
   2) "brazil"
   3) "nb_of_users"
   4) "108"
```

说明：
- 先筛选出女性用户
- 按国家分组并统计人数
- 使用 `FILTER` 排除中国且人数少于等于 100 的组
- 最后排序输出

---
</details>

<details> 
  <summary>
  <i><b>
  统计 2020 年每月的登录次数
  </b></i>
  </summary>

类似前面的查询，但增加对年份的过滤条件：

```
> FT.AGGREGATE idx:user * APPLY year(@last_login) AS year APPLY "monthofyear(@last_login) + 1" AS month GROUPBY 2 @year @month REDUCE count 0 AS num_login  FILTER "@year==2020" SORTBY 2 @month ASC

 1) (integer) 13
 2) 1) "year"
    2) "2020"
    3) "month"
    4) "1"
    5) "num_login"
    6) "520"
...
10) 1) "year"
    2) "2020"
    3) "month"
    4) "9"
    5) "num_login"
    6) "271"
```

使用 `FILTER "@year==2020"` 只保留年份为 2020 的分组，最终得到该年度各月的登录统计。

---
</details>

# 九、其他选项

## 使用过滤器创建索引

在前面的示例中，我们通过 `PREFIX` 来创建索引，即所有匹配指定类型和前缀的键都会被纳入索引。

此外，还可以使用 **过滤表达式（Filter）** 来创建索引。例如：仅对 1990 年到 2000 年之间（不含 2000 年）上映的 "Drama" 类型电影建立索引。

[`FILTER`](https://oss.redislabs.com/redisearch/Aggregations/#filter_expressions) 表达式使用的是 [聚合查询中的过滤语法](https://oss.redislabs.com/redisearch/Aggregations/#filter_expressions)。针对类型（genre）和上映年份（release_year），表达式如下：

* `FILTER "@genre=='Drama' && @release_year>=1990 && @release_year<2000"`

因此，创建索引的命令为：

```bash
FT.CREATE idx:drama ON Hash PREFIX 1 "movie:" FILTER "@genre=='Drama' && @release_year>=1990 && @release_year<2000" SCHEMA title TEXT SORTABLE release_year NUMERIC SORTABLE
```

你可以运行 `FT.INFO idx:drama` 命令来查看该索引的定义和统计信息。

### 注意事项：
* `PREFIX` 是必需的，不能省略。
* 在本应用中，这种索引并不特别有用，因为同样的数据也可以从 `idx:movie` 索引中查询得到。

你可以通过以下两个查询验证数据是否正确被索引，它们应返回相同数量的文档。

在 `idx:drama` 上执行：

```
> FT.SEARCH idx:drama "  @release_year:[1990 (2000]" LIMIT 0 0

1) (integer) 24
```

在 `idx:movie` 上执行：

```
> FT.SEARCH idx:movie "@genre:{Drama}  @release_year:[1990 (2000]" LIMIT 0 0

1) (integer) 24
```

两者均返回 24 部符合条件的电影，说明索引数据一致。


参考文档：
1. https://github.com/RediSearch/redisearch-getting-started
