# python 使用正则表达式从json字符串中取出特定字段的值

> 孤独中，你可以获得一切，除了品格。—— 司汤达《红与黑》

# 一. 概述

最近在使用爬虫抓取一些数据，从获取到的 `html` 文本中无法直接通过 `xpath` 解析出对应的数据，需要从 `js` 脚本中解析一些类似于 `json` 的数据，数据格式如下：

```js
<script src="//mat1.gtimg.com/pingjs/ext2020/configF2017/5df6e3b3.js" charset="utf-8"></script>
<script src="//mat1.gtimg.com/pingjs/ext2020/configF2017/5a978a31.js" charset="utf-8"></script>
<script>window.conf_dcom = apub_5a978a31 </script><!--[if !IE]>|xGv00|61438c491c69d576aec9846de884f28b<![endif]-->
<!--[if !IE]>|xGv00|038d6e161753081e56c192d04873c65c<![endif]-->
    <script>window.DATA = {
		"article_id": "20210808A034KU",
		"article_type": "0",
		"title": "突发！上海出台房贷重磅新规！你的贷款额度标准可能要变了",
		"abstract": null,
		"catalog1": "house",
		"catalog2": "house_zhengce",
		"media": "中国证券报",
		"media_id": "1368",
		"pubtime": "2021-08-08 13:45:25",
		"comment_id": "7221092095",
		"tags": "银行,上海,房贷,贷款,上海市房管局,二手房",
		"political": 0,
		"artTemplate": null,
		"FztCompetition": null,
		"FCompetitionName": null,
		"is_deleted": 0,
		"cms_id": "20210808A034KU00",
		"videoArr": []
}
      
    </script>
  </head>


```

# 二、通过正则表达式提取指定字段的值

需要将上面文本中指定的字段的值解析出来

分析字符串的结构可以看出需要匹配内容的结构为：`"key": "(.*)"`

下面自己定义一个函数来实现此需求：

```python
import re

def find_value_by_regex(key, text):
    """
    通过正则表达式提取json指定字段的值
    :param key: 字段名称
    :param text: 要提取的文本
    :return: 字段对应的值，不存在则返回空字符串
    """
    regex = r'"key": "(.*)"'.replace("key", key)
    match = re.compile(regex).findall(text)
    val = ''
    if match:
        val = match[0]
    return val


if __name__ == "__main__":
    text = '''
         {
                "article_id": "20210808A034KU",
                "article_type": "0",
                "title": "突发！上海出台房贷重磅新规！你的贷款额度标准可能要变了",
                "abstract": null,
                "catalog1": "house",
                "catalog2": "house_zhengce",
                "media": "中国证券报",
                "media_id": "1368",
                "pubtime": "2021-08-08 13:45:25",
                "comment_id": "7221092095",
                "tags": "银行,上海,房贷,贷款,上海市房管局,二手房",
                "political": 0,
                "artTemplate": null,
                "FztCompetition": null,
                "FCompetitionName": null,
                "is_deleted": 0,
                "cms_id": "20210808A034KU00",
                "videoArr": []
        }

    '''
    title = find_value_by_regex("title", text)
    pubtime = find_value_by_regex("pubtime", text)
    print(title)
    print(pubtime)

```

输出结果如下：

```python
突发！上海出台房贷重磅新规！你的贷款额度标准可能要变了
2021-08-08 13:45:25
```

上面定义的方法已经解决了这个需求，接下来将提取一些爬取网页的工具方法方便复用，详细代码如下所示：

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
import requests
import urllib3


def get_random_agent():
    """
    随机获取 agent
    :return:
    """
    agent_list = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]
    agent = random.choice(agent_list)
    return agent


def get_headers():
    """
    发送HTTP请求时的HEAD信息
    :return:
    """
    headers = {
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': get_random_agent()
    }
    return headers


def get_html(url):
    """
    通过 url 获取网页 html 文本 
    :param url: 
    :return: 
    """
    # 设置禁用 https 警告
    urllib3.disable_warnings()
    response = requests.get(url, headers=get_headers(), verify=False)
    get_encoding = response.apparent_encoding  # 获取编码

    response.encoding = get_encoding
    return response.text

```





# 三. python的re模块总结

使用爬虫爬取网页数据的过程中，需要利用各种工具解析网页中的数据，比如：`etree`，`BeautifulSoup`，`scrapy` 等工具，但是功能最强大的还是正则表达式，下面将对 python 的 re 模块方法做一个总结。

`Python` 通过 `re` 模块提供对正则表达式的支持。使用 `re` 的一般步骤是：

1. 使用 `re.compile(正则表达式)` 将正则表达式的字符串形式编译为`Pattern`实例
2. 使用`Pattern`实例提供的方法处理文本并获得匹配结果（一个`Match`实例）
3. 使用`Match`实例获得信息，进行其他的操作

一个简单的例子：

```python
# -*- coding: utf-8 -*-
import re

if __name__ == '__main__':
    # 将正则表达式编译成Pattern对象
    pattern = re.compile(r'hello')

    # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
    match = pattern.match('hello world!')

    if match:
        # 使用Match获得分组信息
        print(match.group()) # 输出结果：hello
        
```

> 使用原生字符串定义正则表达式可以方便的解决转义字符的问题
>
> 原生字符串的定义方式为：`r''`
>
> 有了原生字符串，不需要手动添加转义符号，它会自动转义，写出来的表达式也更直观。

## 1. 使用 re

**re.compile(strPattern[, flag]):** 

这个方法是Pattern类的工厂方法，用于将字符串形式的正则表达式编译为Pattern对象。

第一个参数：正则表达式字符串

第二个参数（可选）：是匹配模式，取值可以使用按位或运算符'|'表示同时生效，比如 `re.I | re.M`。

可选值如下：

- `re.I(re.IGNORECASE)`: 忽略大小写（括号内是完整写法，下同）
- `M(MULTILINE)`: 多行模式，改变'^'和'$'的行为
- `S(DOTALL)`: 点任意匹配模式，改变'.'的行为
- `L(LOCALE)`: 使预定字符类 \w \W \b \B \s \S 取决于当前区域设定
- `U(UNICODE)`: 使预定字符类 \w \W \b \B \s \S \d \D 取决于unicode定义的字符属性

- `X(VERBOSE)`: 详细模式。这个模式下正则表达式可以是多行，忽略空白字符，并可以加入注释。以下两个正则表达式是等价的：

  ```python
  a = re.compile(r"""\d +  # the integral part
                     \.    # the decimal point
                     \d *  # some fractional digits""", re.X)
  b = re.compile(r"\d+\.\d*")
  ```



`re` 提供了众多模块方法用于完成正则表达式的功能。这些方法可以使用`Pattern`实例的相应方法替代，唯一的好处是少写一行`re.compile()`代码，但同时也无法复用编译后的`Pattern`对象。这些方法将在Pattern类的实例方法部分一起介绍。如上面这个例子可以简写为：

```python
m = re.match(r'hello', 'hello world!')
print m.group()
```



## 2. 使用 Pattern

`Pattern` 对象是一个编译好的正则表达式，通过 `Pattern` 提供的一系列方法可以对文本进行匹配查找。

`Pattern` 对象不能直接实例化，必须使用 `re.compile()` 来获取。

### 2.1 Pattern 对象的属性

`Pattern` 提供了几个可读属性用于获取表达式的相关信息：

1. **pattern**: 编译时用的表达式字符串。

2. **flags**: 编译时用的匹配模式，数字形式。

3. **groups**: 表达式中分组的数量。

4. **groupindex**: 以表达式中有别名的组的别名为键、以该组对应的编号为值的字典，没有别名的组不包含在内。

```python
# -*- coding: utf-8 -*-
import re

if __name__ == '__main__':
    text = 'hello world'
    p = re.compile(r'(\w+) (\w+)(?P<sign>.*)', re.DOTALL)

    print("p.pattern:", p.pattern)
    print("p.flags:", p.flags)
    print("p.groups:", p.groups)
    print("p.groupindex:", p.groupindex)
```

输出结果如下：

```python
p.pattern: (\w+) (\w+)(?P<sign>.*)
p.flags: 48
p.groups: 3
p.groupindex: {'sign': 3}
```

### 2.2 Pattern 对象的方法

**1. match(string[, pos[, endpos]]) | re.match(pattern, string[, flags]):**

如果 *string* 的 **开始位置** 能够找到这个正则样式的任意个匹配，就返回一个相应的 `Match`对象。

如果匹配过程中`pattern`无法匹配，或者匹配未结束就已到达`endpos`，则返回`None`。

`pos` 和`endpos` 的默认值分别为 `0` 和 `len(string)`；

`re.match()` 无法指定这两个参数，参数`flags`用于编译`pattern`时指定匹配模式。

> 注意：这个方法并不是完全匹配。当pattern结束时若string还有剩余字符，仍然视为成功。想要完全匹配，可以在表达式末尾加上边界匹配符'$'。

**2. search(string[, pos[, endpos]]) | re.search(pattern, string[, flags]):**

这个方法用于查找字符串中可以匹配成功的子串。

从`string`的`pos`下标处起尝试匹配`pattern`，如果`pattern`结束时仍可匹配，则返回一个`Match`对象；

若无法匹配，则将`pos`加`1`后重新尝试匹配；直到`pos=endpos`时仍无法匹配则返回None。

`pos`和`endpos`的默认值分别为 `0` 和 `len(string)`；

`re.search()`无法指定这两个参数，参数`flags`用于编译`pattern`时指定匹配模式。

一个简单的例子：

```python
# -*- coding: utf-8 -*-
import re

if __name__ == '__main__':
    # 将正则表达式编译成Pattern对象
    pattern = re.compile(r'world')

    # 使用search()查找匹配的子串，不存在能匹配的子串时将返回None
    # 这个例子中使用match()无法成功匹配
    match = pattern.search('hello world!')

    if match:
        # 使用Match获得分组信息
        print(match.group()) # 输出结果：world
```

> 注意 match 方法 和 search 方法的区别

**3. split(string[, maxsplit]) | re.split(pattern, string[, maxsplit]):**

按照能够匹配的子串将string分割后返回列表。

`maxsplit` 用于指定最大分割次数，不指定将全部分割。

```python
# -*- coding: utf-8 -*-
import re

if __name__ == '__main__':
    p = re.compile(r'\d+')
    # 按照数字分隔字符串
    print(p.split('one1two2three3four4')) # 输出结果：['one', 'two', 'three', 'four', '']

```

**4. findall(string[, pos[, endpos]]) | re.findall(pattern, string[, flags]):**

搜索 string，以列表形式返回全部能匹配的子串。

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re

if __name__ == '__main__':
    p = re.compile(r'\d+')
    # 找到所有的数字，以列表的形式返回
    print(p.findall('one1two2three3four4')) # 输出结果：['1', '2', '3', '4']
```

**5. finditer(string[, pos[, endpos]]) | re.finditer(pattern, string[, flags]):**

搜索 string，返回一个顺序访问每一个匹配结果（`Match`对象）的迭代器。

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re

if __name__ == '__main__':
    p = re.compile(r'\d+')
    # 返回一个顺序访问每一个匹配结果（`Match`对象）的迭代器
    for m in p.finditer('one1two2three3four4'):
        print(m.group())  # 输出结果：1 2 3 4
```

**6. sub(repl, string[, count]) | re.sub(pattern, repl, string[, count]):**

使用 `repl` 替换 `string` 中每一个匹配的子串后返回替换后的字符串。
当 `repl` 是一个字符串时，可以使用 `\id` 或 `\g<id>` 、`\g<name>`引用分组，但不能使用编号0。
当 `repl` 是一个方法时，这个方法应当只接受一个参数（`Match`对象），并返回一个字符串用于替换（返回的字符串中不能再引用分组）。
count用于指定最多替换次数，不指定时全部替换。

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re

if __name__ == '__main__':
    p = re.compile(r'(\w+) (\w+)')
    s = 'i say, hello world!'

    print(p.sub(r'\1 \2 hi', s))  # 输出结果：i say hi, hello world hi!

    def func(m):
        return m.group(1).title() + ' ' + m.group(2).title()

    print(p.sub(func, s))  # 输出结果：I Say, Hello World!
```

**7. subn(repl, string[, count]) |re.sub(pattern, repl, string[, count]):**

subn() 方法与 sub() 方法的区别是返回结果不同：

subn() 方法返回的结果是一个元组：(替换后的字符串，替换次数)

sub() 方法返回的结果是一个字符串：替换后的字符串

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re

if __name__ == '__main__':
    p = re.compile(r'(\w+) (\w+)')
    s = 'i say, hello world!'

    print(p.subn(r'\1 \2 hi', s))  # 输出结果：('i say hi, hello world hi!', 2)

    def func(m):
        return m.group(1).title() + ' ' + m.group(2).title()

    print(p.subn(func, s))  # 输出结果：('I Say, Hello World!', 2)
```



## 3. 使用 Match

Match对象是一次匹配的结果，包含了很多关于此次匹配的信息，可以使用Match提供的可读属性或方法来获取这些信息。

### 3.1 Match 对象的属性

1. **string**: 匹配时使用的文本。
2. **re**: 匹配时使用的Pattern对象。
3. **pos**: 文本中正则表达式开始搜索的索引。值与`Pattern.match()`和`Pattern.seach()`方法的同名参数相同。
4. **endpos**: 文本中正则表达式结束搜索的索引。值与`Pattern.match()`和`Pattern.seach()`方法的同名参数相同。
5. **lastindex**: 最后一个被捕获的分组的索引。如果没有被捕获的分组，将为None。
6. **lastgroup**: 最后一个被捕获的分组的别名。如果这个分组没有别名或者没有被捕获的分组，将为None。

```python
# -*- coding: utf-8 -*-
import re

if __name__ == '__main__':
    text = 'hello world'
    p = re.compile(r'(\w+) (\w+)(?P<sign>.*)', re.DOTALL)
    match = p.match(text)
    if match:
        print("match.re:", match.re)
        print("match.string:", match.string)
        print("match.endpos:", match.endpos)
        print("match.pos:", match.pos)
        print("match.lastgroup:", match.lastgroup)
        print("match.lastindex:", match.lastindex)
        
        
# 输出结果如下：
# match.re: re.compile('(\\w+) (\\w+)(?P<sign>.*)', re.DOTALL)
# match.string: hello world
# match.endpos: 11
# match.pos: 0
# match.lastgroup: sign
# match.lastindex: 3
```



### 3.2 Match 对象的方法

1. **group([group1, …]):**
   获得一个或多个分组截获的字符串，指定多个参数时将以元组形式返回。

   group()可以使用编号也可以使用别名；

   编号0代表整个匹配的子串；

   不填写参数时，返回group(0)；

   没有截获字符串的组返回None；

2. **groups([default]):**
   以元组形式返回全部分组截获的字符串，相当于调用group(1,2,…last)；

   default表示没有截获字符串的组以这个值替代，默认为None；

3. **groupdict([default]):
   **返回已有别名的组的别名为键、以该组截获的子串为值的字典，没有别名的组不包含在内。default含义同上。

4. **start([group]):**
   返回指定的组截获的子串在string中的起始索引（子串第一个字符的索引）。group默认值为0。

5. **end([group]):
   **返回指定的组截获的子串在string中的结束索引（子串最后一个字符的索引+1）。group默认值为0。

6. **span([group]):
   **返回(start(group), end(group))。

7. **expand(template):**
   将匹配到的分组代入template中然后返回。template中可以使用`\id`或`\g<id>`、`\g<name>`引用分组，但不能使用编号0。`\id`与`\g<id>`是等价的；但`\10`将被认为是第10个分组，如果你想表达`\1`之后是字符'0'，只能使用`\g<1>0`。

```python
# -*- coding: utf-8 -*-
import re

if __name__ == '__main__':
    import re
    m = re.match(r'(\w+) (\w+)(?P<sign>.*)', 'hello world!')
    print("m.group(1,2):", m.group(0, 1, 2, 3))
    print("m.groups():", m.groups())
    print("m.groupdict():", m.groupdict())
    print("m.start(2):", m.start(2))
    print("m.end(2):", m.end(2))
    print("m.span(2):", m.span(2))
    print(r"m.expand(r'\2 \1\3'):", m.expand(r'\2 \1\3'))


# 输出结果：
# m.group(1,2): ('hello world!', 'hello', 'world', '!')
# m.groups(): ('hello', 'world', '!')
# m.groupdict(): {'sign': '!'}
# m.start(2): 6
# m.end(2): 11
# m.span(2): (6, 11)
# m.expand(r'\2 \1\3'): world hello!
```



参考文章

[python  官方文档](https://docs.python.org/zh-cn/3.9/library/re.html)

https://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html

