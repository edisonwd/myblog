# chunk分块实践篇

> RAG 的尽头就是 Agent
>

## 概述
本文是chunk分块的实践篇，chunk分块的理论可以查看前一篇文章[chunk分块理论篇](https://yuque.antfin.com/xiniao.wd/tcc9h6/ax7d5kzzd427dhh6)。

接下来主要使用 langchain 提供的工具对前面的chunk分块方法进行实践，下面内容都是在jupyter notebook中进行实践的，然后将内容转换为markdown格式。

> 可以使用下面的命令将 jupyter notebook 转换为 markdown 格式文件：
>
> 1. 安装 nbconvert：`pip install nbconvert`
> 2. 执行转换命令：`jupyter nbconvert --to markdown your_notebook.ipynb`
>

进行实践之前需要安装相关依赖 

> 查看相关接口文档：[langchain-text-splitters接口文档](https://python.langchain.com/api_reference/text_splitters/index.html#)
>

```python
pip install -qU langchain-text-splitters
```

## 按字符分块
### 按单字符分块
使用 `langchain` 的 `CharacterTextSplitter` 这是最简单的方法(在应用中不推荐使用)，它根据给定的字符序列进行拆分，默认为`\n\n`，chunk长度以字符数来衡量。

+ 文本的分割方式：按单个字符分隔符。
+ 如何测量块大小：按字符数。
+ 要直接获取字符串内容，使用.split_text。
+ 要创建 LangChain Document对象（例如，用于下游任务），使用.create_documents。
+ 内部使用的是 `_splits = re.split(f"({separator})", text)` 进行实现的



```python
from langchain_text_splitters import CharacterTextSplitter

text = """
# 固定长度分块
使用 `langchain` 的 `CharacterTextSplitter` 这是最简单的方法，它根据给定的字符序列进行拆分，默认为`\n\n`，chunk长度以字符数来衡量。

- 文本的分割方式：按单个字符分隔符。
- 如何测量块大小：按字符数。
- 要直接获取字符串内容，使用.split_text。
- 要创建 LangChain Document对象（例如，用于下游任务），使用.create_documents。
- 内部使用的是 `_splits = re.split(f"({separator})", text)` 进行实现的
"""

text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=100,
    chunk_overlap=0,
    length_function=len,
    is_separator_regex=False,
)
chunks = text_splitter.create_documents([text])
print(chunks)
```

输出结果：

```plain
[Document(metadata={}, page_content='# 固定长度分块\n使用 `langchain` 的 `CharacterTextSplitter` 这是最简单的方法，它根据给定的字符序列进行拆分，默认为`\n\n`，chunk长度以字符数来衡量。'), Document(metadata={}, page_content='- 文本的分割方式：按单个字符分隔符。\n- 如何测量块大小：按字符数。\n- 要直接获取字符串内容，使用.split_text。\n- 要创建 LangChain Document对象（例如，用于下游任务），使用.create_documents。\n- 内部使用的是 `_splits = re.split(f"({separator})", text)` 进行实现的')]
```

让我们来看看上面设置的参数：

+ `chunk_size`：块的最大大小，其中大小由决定 `length_function`。
+ `chunk_overlap`：目标块之间的重叠。重叠块有助于减少上下文在块之间划分时的信息丢失。
+ `length_function`：确定块大小的函数，默认为 `len`。
+ `is_separator_regex`：分隔符（默认为"\n\n"）是否应解释为正则表达式。

**在使用.create_documents的使用，指定metadatas将与每个文档关联的元数据与chunk关联**：



```python
metadatas = [{"document": 1}, {"document": 2}]
chunks = text_splitter.create_documents(
    [text], metadatas=metadatas
)
print(chunks)
```

输出结果：

```plain
[Document(metadata={'document': 1}, page_content='# 固定长度分块\n使用 `langchain` 的 `CharacterTextSplitter` 这是最简单的方法，它根据给定的字符序列进行拆分，默认为`\n\n`，chunk长度以字符数来衡量。'), Document(metadata={'document': 1}, page_content='- 文本的分割方式：按单个字符分隔符。\n- 如何测量块大小：按字符数。\n- 要直接获取字符串内容，使用.split_text。\n- 要创建 LangChain Document对象（例如，用于下游任务），使用.create_documents。\n- 内部使用的是 `_splits = re.split(f"({separator})", text)` 进行实现的')]
```

**使用.split_text，直接获取切分后的字符串内容列表**

```python
text_splitter.split_text(text)
```

输出结果：

```plain
['# 固定长度分块\n使用 `langchain` 的 `CharacterTextSplitter` 这是最简单的方法，它根据给定的字符序列进行拆分，默认为`\n\n`，chunk长度以字符数来衡量。',
 '- 文本的分割方式：按单个字符分隔符。\n- 如何测量块大小：按字符数。\n- 要直接获取字符串内容，使用.split_text。\n- 要创建 LangChain Document对象（例如，用于下游任务），使用.create_documents。\n- 内部使用的是 `_splits = re.split(f"({separator})", text)` 进行实现的']
```

### 按多字符递归分块
文本分割器 `RecursiveCharacterTextSplitter` 是**推荐用于通用文本的分割器**，它会使用一个字符列表(默认列表为 `["\n\n", "\n", " ", ""]`)按顺序分割文本，直到块的大小达到指定长度。这样做的目的是尽可能地将所有段落（然后是句子，最后是单词）保持在一起，因为这些段落通常看起来是语义上最相关的文本片段。

+ 文本的拆分方式：按字符列表。
+ 如何测量块大小：按字符数。

下面我们展示示例用法。

+ 要直接获取字符串内容，请使用`.split_text`。
+ 要创建 LangChain `Document`对象（例如，用于下游任务），请使用 `.create_documents`。



```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text = """
## 按多字符递归分块

文本分割器 `RecursiveCharacterTextSplitter` 是**推荐用于通用文本的分割器**，它会使用一个字符列表(默认列表为`["\n\n", "\n", " ", ""]`)按顺序分割文本，直到块的大小达到指定长度。这样做的目的是尽可能地将所有段落（然后是句子，最后是单词）保持在一起，因为这些段落通常看起来是语义上最相关的文本片段。

- 文本的拆分方式：按字符列表。
- 如何测量块大小：按字符数。

下面我们展示示例用法。

- 要直接获取字符串内容，请使用`.split_text`。

- 要创建 LangChain `Document`对象（例如，用于下游任务），请使用 `.create_documents`。
"""

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=70,
    chunk_overlap=0,
    length_function=len,
    is_separator_regex=False,  # 默认为 False
)
chunks = text_splitter.create_documents([text])
chunks
```

输出结果：

```plain
[Document(metadata={}, page_content='## 按多字符递归分块'),
 Document(metadata={}, page_content='文本分割器 `RecursiveCharacterTextSplitter`'),
 Document(metadata={}, page_content='是**推荐用于通用文本的分割器**，它会使用一个字符列表(默认列表为`["'),
 Document(metadata={}, page_content='", "'),
 Document(metadata={}, page_content='", " ",'),
 Document(metadata={}, page_content='""]`)按顺序分割文本，直到块的大小达到指定长度。这样做的目的是尽可能地将所有段落（然后是句子，最后是单词）保持在一起，因为这些段落通常'),
 Document(metadata={}, page_content='看起来是语义上最相关的文本片段。'),
 Document(metadata={}, page_content='- 文本的拆分方式：按字符列表。\n- 如何测量块大小：按字符数。\n\n下面我们展示示例用法。'),
 Document(metadata={}, page_content='- 要直接获取字符串内容，请使用`.split_text`。'),
 Document(metadata={}, page_content='- 要创建 LangChain `Document`对象（例如，用于下游任务），请使用 `.create_documents`。')]
```

让我们来看看上面设置的参数：

+ `chunk_size`：块的最大大小，其中大小由决定 `length_function`。
+ `chunk_overlap`：目标块之间的重叠。重叠块有助于减少上下文在块之间划分时的信息丢失。
+ `length_function`：确定块大小的函数，默认为 `len`。
+ `is_separator_regex`：分隔符列表（默认为["\n\n", "\n", " ", ""]）是否应解释为正则表达式。

某些文字没有单词边界，例如中文、日语和泰语，使用默认分隔符列表拆分文本["\n\n", "\n", " ", ""]可能会导致单词被拆分成多个块。为了保持单词完整，可以覆盖分隔符列表以添加其他标点符号。

#### 设置中文场景分隔符
RecursiveCharacterTextSplitter的工作流程：它首先尝试用第一个分隔符分割文本，如果生成的块太大，就继续用下一个分隔符进行递归分割，直到所有块都符合大小要求。因此，分隔符的顺序很重要，应该从最自然的分隔符开始，比如段落分隔符，然后是句子分隔符，再是其他可能的符号。

中文常用的段落分隔符是两个换行符（\n\n），而句子通常以句号、问号、感叹号结尾，但中文的句号是“。”，不同于英文的“.”。因此，在separators中应该包含这些中文标点。另外，中文有时也会使用分号、逗号来分隔，但逗号分隔可能太细，导致分块过小，需要根据具体情况调整。

可能还需要考虑一些特殊情况，比如省略号“……”，或者顿号“、”，但这些可能不适合作为分隔符，因为分割得太细。此外，中文的引号如“”和‘’可能包围重要内容，分割时需要避免在这些位置拆分。

因此，合理的separators设置可能是先按段落分隔，再按句子分隔，然后按其他标点。例如：`["\n\n", "\n", "。", "！", "？", "；", "，"]`，但需要考虑分割后的块大小是否符合chunk_size的要求，如果使用太多分隔符，可能导致递归分割次数增加，影响效率。

**中文场景下的推荐设置**

默认的英文分隔符为 `["\n\n", "\n", " ", ""]`，但中文文本具有以下特点：

+ 无空格分词：中文词语间无空格分隔。
+ 标点差异：中文使用全角标点（如 。！？），而非英文半角标点（如 .!?）。
+ 段落结构：段落通常以换行符分隔。

优化后的中文分隔符



```python
separators = [
    "\n\n",    # 优先按段落切分（双换行符）
    "\n",      # 其次按单换行符切分
    "。",      # 按句号切分
    "！",      # 按感叹号切分
    "？",      # 按问号切分
    "；",      # 按分号切分
    "，",      # 按逗号切分（慎用，可能过细）
    "”",       # 按右引号切分（适配对话场景）
    "…",       # 按省略号切分
    "",        # 最后按字符切分（保底）
]
```



```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=70,          # 目标块大小（单位：字符）
    chunk_overlap=0,        # 块间重叠字符数
    separators=separators,   # 自定义中文分隔符
    length_function=len,     # 长度计算函数（按字符数）
)

chunks = text_splitter.create_documents([text])
chunks
```





```plain
[Document(metadata={}, page_content='## 按多字符递归分块'),
 Document(metadata={}, page_content='文本分割器 `RecursiveCharacterTextSplitter` 是**推荐用于通用文本的分割器**'),
 Document(metadata={}, page_content='，它会使用一个字符列表(默认列表为`["'),
 Document(metadata={}, page_content='", "'),
 Document(metadata={}, page_content='", " ", ""]`)按顺序分割文本，直到块的大小达到指定长度'),
 Document(metadata={}, page_content='。这样做的目的是尽可能地将所有段落（然后是句子，最后是单词）保持在一起，因为这些段落通常看起来是语义上最相关的文本片段。'),
 Document(metadata={}, page_content='- 文本的拆分方式：按字符列表。\n- 如何测量块大小：按字符数。\n\n下面我们展示示例用法。'),
 Document(metadata={}, page_content='- 要直接获取字符串内容，请使用`.split_text`。'),
 Document(metadata={}, page_content='- 要创建 LangChain `Document`对象（例如，用于下游任务），请使用 `.create_documents`。')]
```

## 按 token 分块
语言模型有 token 数量限制，我们在使用时不应超过该限制，因此在将文本拆分成块时，最好计算 token 的数量。tokenizer 有很多，计算文本中的 token 数量时，建议使用与语言模型中相同的tokenizer（在模型仓库中模型文件和 tokenizer 文件放在一起的）。

我们可以使用 tokenizer 来计算文本中的 token 长度，按照 token 切分的逻辑如下：

+ 文本的分割方式：按传入的字符。
+ 如何测量块大小：通过 `len(tokenizer.tokenize(text))` 计算的 token 数。

按 token 分块步骤：

+ 下载 tokenizer，因为在国内无法直接访问 HuggingFace，所以这里从 modelscope 中的模型仓库中下载，只需要下载 tokenizer 文件，不需要下载模型文件（`*.bin`, `*.safetensors`结尾的文件是模型文件）
+ 使用 `AutoTokenizer.from_pretrained` 加载 tokenizer 
+ 使用 `TextSplitter.from_huggingface_tokenizer`方法指定 `tokenizer` 参数，其他参数与前面的相同

### 从 modelscope 下载 tokenizer
```python
# 从 modelscope 下载 tokenizer
from typing import List
import logging
logger = logging.getLogger(__name__)

def download_from_modelscope(model_id: str,
                             local_dir: str = None,
                             ignore_patterns: List[str] =None,
                             **kwargs
                             ):
    """
    从modelscope下载模型

    如何没有指定local_dir，默认保存模型文件到 ~/.cache/modelscope/hub/models/ 文件夹中
    modelscope 地址：https://modelscope.cn/models
    """
    from modelscope.hub.snapshot_download import snapshot_download
    
    logger.info(f"开始下载模型: {model_id}")

    model_dir = snapshot_download(model_id=model_id,
                                  local_dir=local_dir,
                                  ignore_patterns=ignore_patterns,
                                  **kwargs)
    logger.info(f"模型下载完成保存目录: {model_dir}")
    return model_dir

modelscope_args = {
    # 可配置参数，查看：modelscope.hub.snapshot_download
    "model_id": "Qwen/Qwen2.5-72B-Instruct",
    "ignore_patterns": ["*.bin", "*.safetensors"],
    "local_dir": './Qwen2.5-72B-Instruct'
}

model_dir = download_from_modelscope(**modelscope_args)
print(model_dir)
```

```plain
./Qwen2.5-72B-Instruct
```

### 使用 from_huggingface_tokenizer 方法按照token分块
```python
# 使用 `AutoTokenizer.from_pretrained` 加载 tokenizer 
from transformers import AutoTokenizer
from langchain.text_splitter import RecursiveCharacterTextSplitter

tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)

# 使用 `TextSplitter.from_huggingface_tokenizer`方法指定 `tokenizer` 参数，其他参数与前面的相同
text = """
## 按多字符递归分块

文本分割器 `RecursiveCharacterTextSplitter` 是**推荐用于通用文本的分割器**，它会使用一个字符列表(默认列表为`["\n\n", "\n", " ", ""]`)按顺序分割文本，直到块的大小达到指定长度。这样做的目的是尽可能地将所有段落（然后是句子，最后是单词）保持在一起，因为这些段落通常看起来是语义上最相关的文本片段。

- 文本的拆分方式：按字符列表。
- 如何测量块大小：按字符数。

下面我们展示示例用法。

- 要直接获取字符串内容，请使用`.split_text`。

- 要创建 LangChain `Document`对象（例如，用于下游任务），请使用 `.create_documents`。
"""

text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer=tokenizer,
    chunk_size=70,
    chunk_overlap=0,
    # separators=separators,
)
chunks = text_splitter.create_documents([text])
chunks

```



```plain
[Document(metadata={}, page_content='## 按多字符递归分块\n\n文本分割器 `RecursiveCharacterTextSplitter` 是**推荐用于通用文本的分割器**，它会使用一个字符列表(默认列表为`["'),
 Document(metadata={}, page_content='", "\n", " ", ""]`)按顺序分割文本，直到块的大小达到指定长度。这样做的目的是尽可能地将所有段落（然后是句子，最后是单词）保持在一起，因为这些段落通常看起来是语义上最相关的文本片段。'),
 Document(metadata={}, page_content='- 文本的拆分方式：按字符列表。\n- 如何测量块大小：按字符数。\n\n下面我们展示示例用法。\n\n- 要直接获取字符串内容，请使用`.split_text`。'),
 Document(metadata={}, page_content='- 要创建 LangChain `Document`对象（例如，用于下游任务），请使用 `.create_documents`。')]
```

## 字符分块和token分块对比
从前面的结果对比可以看到，使用相同的 chunk_size，按照字符数和token数分块后，按字符分块的数量比按token分块的数量要多，原因如下：

token分块则是根据模型的分词器，比如BERT或GPT使用的WordPiece或BPE算法，将文本分成有意义的**子词单元**，也就是说一个token可能是一个词语，所以分块的数量更少。

以下是 **字符分块** 和 **Token 分块** 的核心区别总结：

---

### **1. 定义与原理**
| **维度** | **字符分块** | **Token 分块** |
| --- | --- | --- |
| **分块单位** | 按**字符数**切分（如每 200 个字符一个块）。 | 按模型分词器（Tokenizer）的 **Token 数** 切分（如每 256 tokens 一个块）。 |
| **底层逻辑** | 直接基于文本的物理长度切割，无语言语义分析。 | 依赖分词算法（如 BPE、WordPiece）将文本转换为有意义的子词单元。 |
| **典型场景** | 简单文本预处理、日志切割、多语言混合文本。 | 适配预训练模型（如 BERT、GPT）的输入限制，需与模型分词逻辑对齐。 |


---

### **2. 优缺点对比**
| **维度** | **字符分块** | **Token 分块** |
| --- | --- | --- |
| **优点** | ✅ 实现简单，无需依赖分词工具   ✅ 无视语言差异（如中文、阿拉伯文） | ✅ 适配模型输入限制（如 GPT-4 的 8k tokens）   ✅ 保留词语完整性（如 `"ChatGPT"` 不被切分） |
| **缺点** | ❌ 破坏语义单元（如切分词语/句子）   ❌ 无法适配模型需求 | ❌ 依赖分词器性能（如未登录词处理）   ❌ 不同模型分词结果不同（如 BERT vs GPT） |


---

### **3. 示例对比**
#### **输入文本**
```plain
自然语言处理（NLP）是人工智能的核心领域之一。
```

#### **分块结果**
| **方法** | **分块结果（假设块大小=10）** | **问题说明** |
| --- | --- | --- |
| **字符分块** | `["自然语言处理（NLP", "）是人工智能的核"]` | 切分词语（`NLP)` 被拆开）、破坏标点结构。 |
| **Token 分块** | `["自然", "语言", "处理", "（", "NLP", "）", "..."]` → 合并为有效块 | 保留完整词语，适配模型输入。 |


---

### **4. 适用场景**
| **方法** | **推荐场景** | **避免场景** |
| --- | --- | --- |
| **字符分块** | - 日志文件切割   - 多语言混合文本快速处理   - 无模型依赖的简单任务 | - 需语义连贯的任务（如问答、摘要）   - 适配预训练模型 |
| **Token 分块** | - 预训练模型输入（如 BERT、GPT）   - 语义敏感任务（如机器翻译）   - 精确控制模型计算成本 | - 无分词工具的简单系统 |


---

### **5. 关键差异总结**
| **维度** | **字符分块** | **Token 分块** |
| --- | --- | --- |
| **语言适配性** | 通用所有语言，但破坏语义 | 依赖分词器，适配特定语言（如中文需专用分词器） |
| **模型适配性** | 与模型无关 | 需与模型的分词器对齐（如 GPT-3 用 BPE） |
| **计算效率** | 高（直接切片） | 中（需分词计算） |
| **语义保留能力** | 低 | 高 |


---

### **6. 选择建议**
+ **优先 Token 分块**：涉及预训练模型的任务（如 RAG、文本生成）。
+ **仅用字符分块**：简单文本处理、多语言混合且无需语义保留的场景（如日志分析）。
+ **中文特别注意**：  
    - 字符分块易破坏中文词语（如 `“人工智能”` → `“人工智 能”`）。  
    - Token 分块需使用中文分词器（如 `bert-base-chinese`）。



## 按照语义分块
`langchain` 的 `SemanticChunker` 语义分块是参考：[5_Levels_Of_Text_Splitting](https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/tutorials/LevelsOfTextSplitting/5_Levels_Of_Text_Splitting.ipynb) 实现的。

要使用 `SemanticChunker` 需要使用如下命令安装 `langchain_experimental`:  
`pip install --quiet langchain_experimental`

以下是基于语义相似度的分块实现思路总结，该方法通过 **嵌入距离检测语义边界** 实现智能分块：

---

### **核心思路**
1. **分句处理**  
将原始文本按句子粒度拆分（如使用 `spaCy`、`nltk` 或标点规则）。
2. **滑动窗口聚合**  
将连续句子组成 **窗口**（如 3 个句子为一个窗口），计算窗口的嵌入表示。
3. **嵌入距离计算**  
滑动窗口逐步后移（如每次移除前一句，添加下一句），计算相邻窗口嵌入的相似度（如余弦距离）。
4. **断点检测**  
若相邻窗口的嵌入距离超过预设 **阈值**，则认为此处存在语义边界，触发分块。
5. **合并相邻块**  
将未触发断点的相邻窗口合并为同一块，保持语义连贯性。

---

### **具体步骤示例**
#### **输入文本**
```plain
句子1：深度学习是机器学习的分支。  
句子2：它通过神经网络模拟人脑的学习过程。  
句子3：常见的模型包括CNN和RNN。  
句子4：自然语言处理（NLP）是其重要应用领域。  
句子5：BERT和GPT是NLP中的代表性模型。  
```

#### **分块过程**
1. **窗口生成**  
    - 窗口1：[句子1, 句子2, 句子3]  
    - 窗口2：[句子2, 句子3, 句子4]  
    - 窗口3：[句子3, 句子4, 句子5]
2. **嵌入计算**  
    - 获取每个窗口的嵌入向量（如使用 Sentence-BERT）。
3. **距离比较**  
    - 计算窗口1与窗口2的嵌入距离 → 假设距离较小（主题连续：深度学习→模型）。  
    - 计算窗口2与窗口3的嵌入距离 → 假设距离较大（主题切换：模型→NLP应用）。
4. **断点触发**  
    - 在窗口2与窗口3之间触发分块。
5. **最终分块**  
    - 块1：[句子1, 句子2, 句子3]  
    - 块2：[句子4, 句子5]

---

### **优点与缺点**
| **优点** | **缺点** |
| --- | --- |
| ✅ 自适应语义边界，避免机械切分 | ❌ 计算成本高（需多次嵌入计算和相似度比较） |
| ✅ 减少噪声（窗口聚合降低单句波动影响） | ❌ 依赖嵌入模型质量（如语义表示不准确则分块失效） |
| ✅ 适配不同文本类型（技术文档、对话等） | ❌ 参数敏感（需调优窗口大小、阈值） |


---

### **关键参数与调优建议**
1. **窗口大小**  
    - 过小：噪声敏感（如窗口=1时退化为单句比较）。  
    - 过大：语义边界模糊（如窗口=5可能掩盖局部变化）。  
    - **建议值**：2-4 个句子（根据文本密度调整）。
2. **相似度阈值**  
    - 过高：分块过少，块内语义混杂。  
    - 过低：分块过多，破坏连贯性。  
    - **调优方法**：通过验证集测试不同阈值下的分块质量（如人工评估或检索召回率）。
3. **嵌入模型选择**  
    - 优先领域适配模型（如技术文本用 `all-mpnet-base-v2`，通用文本用 `text-embedding-3-small`）。

---

### **改进方向**
1. **动态窗口调整**  
根据文本复杂度自动扩展/收缩窗口（如密集段落用小窗口，冗余内容用大窗口）。  
2. **混合分块策略**  
先按标题/段落粗分块，再对长段落应用语义分块。  
3. **轻量化计算**  
    - 使用低维嵌入（如 PCA 降维）。  
    - 缓存嵌入结果减少重复计算。

---

### **适用场景**
+ **技术文档**：精准切分章节、案例、代码块。  
+ **长对话记录**：按话题切换分割会话阶段。  
+ **跨段落推理任务**：确保块内语义高度相关。

通过该方法，可显著提升 RAG 等应用中检索内容的语义连贯性和相关性。



## 语义分块代码实现
接下来使用 langchain 的 `SemanticChunker` 来演示语义分块代码实现。

### 选择embedding模型
要实例化 `SemanticChunker`，必须指定一个 embedding 模型。因为在国内无法直接从 huggingface 下载模型，所以这里选择从 modelscope 下载 embedding 模型。  
在 modelscope 的模型库中找到文本向量模型，我这里选择下载量和喜欢数最多的 embedding 模型 `iic/nlp_gte_sentence-embedding_chinese-large`。

### 加载embedding模型
在 modelscope 中查看 `iic/nlp_gte_sentence-embedding_chinese-large` 的模型介绍，可以知道它的使用方法，即可以通过简单ModelScope框架的Pipeline调用来使用GTE文本向量表示模型。ModelScope封装了统一的接口对外提供单句向量表示、双句文本相似度、多候选相似度计算功能。

在 `langchain_community` 中对 ModelScope 框架的 Pipeline 加载 embedding 模型进行了集成，使用 `from langchain_community.embeddings import ModelScopeEmbeddings` 即可，方便在langchain的技术体系使用。

接下来使用 `ModelScopeEmbeddings` 加载 embedding 模型。



```python
from langchain_community.embeddings import ModelScopeEmbeddings
# 因为语义分块是按照语义相似度进行分块的，所以需要一个计算语义相似度的 embedding 模型。
model_id = "iic/nlp_gte_sentence-embedding_chinese-large"
embed = ModelScopeEmbeddings(model_id=model_id)
print(embed)

embedding = embed.embed_query('测试embedding')
len(embedding)
```

```plain
2025-05-22 10:15:44,137 - modelscope - WARNING - Model revision not specified, use revision: v1.1.0
2025-05-22 10:15:45,588 - modelscope - WARNING - Model revision not specified, use revision: v1.1.0


Downloading Model from https://www.modelscope.cn to directory: /Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large


2025-05-22 10:15:45,800 - modelscope - INFO - initiate model from /Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large
2025-05-22 10:15:45,802 - modelscope - INFO - initiate model from location /Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large.
2025-05-22 10:15:45,818 - modelscope - INFO - initialize model from /Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large
2025-05-22 10:15:49,278 - modelscope - WARNING - No preprocessor field found in cfg.
2025-05-22 10:15:49,278 - modelscope - WARNING - No val key and type key found in preprocessor domain of configuration.json file.
2025-05-22 10:15:49,278 - modelscope - WARNING - Cannot find available config to build preprocessor at mode inference, current config: {'model_dir': '/Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large'}. trying to build by task and model information.
2025-05-22 10:15:49,309 - modelscope - INFO - cuda is not available, using cpu instead.
2025-05-22 10:15:49,311 - modelscope - WARNING - No preprocessor field found in cfg.
2025-05-22 10:15:49,312 - modelscope - WARNING - No val key and type key found in preprocessor domain of configuration.json file.
2025-05-22 10:15:49,312 - modelscope - WARNING - Cannot find available config to build preprocessor at mode inference, current config: {'model_dir': '/Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large', 'sequence_length': 128}. trying to build by task and model information.


embed=<modelscope.pipelines.nlp.sentence_embedding_pipeline.SentenceEmbeddingPipeline object at 0x1766e5d60> model_id='iic/nlp_gte_sentence-embedding_chinese-large' model_revision=None





1024
```

> 注意⚠️： 在使用 langchain_community 实现的 ModelScopeEmbeddings 时，从前面的 WARNING 内容中可以看到，embedding模型默认最长文本长度为128`'sequence_length': 128`，并且无法修改。
>

为了允许接受更长的文本，下面将 ModelScopeEmbeddings 的实现进行重写，添加了 sequence_length 设置参数，代码实现如下：



```python
from typing import Any, List, Optional

from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, ConfigDict


class ModelScopeEmbeddings(BaseModel, Embeddings):
    """ModelScopeHub embedding models.

    To use, you should have the ``modelscope`` python package installed.

    Example:
        .. code-block:: python

            from langchain_community.embeddings import ModelScopeEmbeddings
            model_id = "damo/nlp_corom_sentence-embedding_english-base"
            embed = ModelScopeEmbeddings(model_id=model_id, model_revision="v1.0.0")
    """

    embed: Any = None
    model_id: str = "damo/nlp_corom_sentence-embedding_english-base"
    """Model name to use."""
    model_revision: Optional[str] = None
    sequence_length: int = 512 # sequence_length 代表最大文本长度

    def __init__(self, **kwargs: Any):
        """Initialize the modelscope"""
        super().__init__(**kwargs)
        try:
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
        except ImportError as e:
            raise ImportError(
                "Could not import some python packages."
                "Please install it with `pip install modelscope`."
            ) from e
        self.embed = pipeline(
            Tasks.sentence_embedding,
            model=self.model_id,
            model_revision=self.model_revision,
            sequence_length=self.sequence_length
        )

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute doc embeddings using a modelscope embedding model.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        texts = list(map(lambda x: x.replace("\n", " "), texts))
        inputs = {"source_sentence": texts}
        embeddings = self.embed(input=inputs)["text_embedding"]
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Compute query embeddings using a modelscope embedding model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        text = text.replace("\n", " ")
        inputs = {"source_sentence": [text]}
        embedding = self.embed(input=inputs)["text_embedding"][0]
        return embedding.tolist()


model_id = "iic/nlp_gte_sentence-embedding_chinese-large"
embed = ModelScopeEmbeddings(model_id=model_id, sequence_length=1024)
print(embed)
embedding = embed.embed_query('测试embedding')
len(embedding)
```

```plain
2025-05-22 10:21:51,892 - modelscope - WARNING - Model revision not specified, use revision: v1.1.0
2025-05-22 10:21:53,263 - modelscope - WARNING - Model revision not specified, use revision: v1.1.0


Downloading Model from https://www.modelscope.cn to directory: /Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large


2025-05-22 10:21:53,541 - modelscope - INFO - initiate model from /Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large
2025-05-22 10:21:53,543 - modelscope - INFO - initiate model from location /Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large.
2025-05-22 10:21:53,562 - modelscope - INFO - initialize model from /Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large
2025-05-22 10:21:56,991 - modelscope - WARNING - No preprocessor field found in cfg.
2025-05-22 10:21:56,991 - modelscope - WARNING - No val key and type key found in preprocessor domain of configuration.json file.
2025-05-22 10:21:56,992 - modelscope - WARNING - Cannot find available config to build preprocessor at mode inference, current config: {'model_dir': '/Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large'}. trying to build by task and model information.
2025-05-22 10:21:57,014 - modelscope - INFO - cuda is not available, using cpu instead.
2025-05-22 10:21:57,018 - modelscope - WARNING - No preprocessor field found in cfg.
2025-05-22 10:21:57,019 - modelscope - WARNING - No val key and type key found in preprocessor domain of configuration.json file.
2025-05-22 10:21:57,019 - modelscope - WARNING - Cannot find available config to build preprocessor at mode inference, current config: {'model_dir': '/Users/xiniao/.cache/modelscope/hub/models/iic/nlp_gte_sentence-embedding_chinese-large', 'sequence_length': 1024}. trying to build by task and model information.


embed=<modelscope.pipelines.nlp.sentence_embedding_pipeline.SentenceEmbeddingPipeline object at 0x1766e44a0> model_id='iic/nlp_gte_sentence-embedding_chinese-large' model_revision=None sequence_length=1024





1024
```

### 使用 SemanticChunker
要实例化SemanticChunker，必须指定一个Embeddings实例。

语义分块器的工作原理是确定何时“拆分”句子，具体方法是查找任意两个句子之间嵌入的差异，当差异超过某个阈值时，句子就会被拆分。

`SemanticChunker` 默认句子拆分的逻辑是将文章按默认的 '.', '?', 和 '!' 进行分割，默认参数为：`sentence_split_regex: str = r"(?<=[.?!])\s+"`

有几种可以用来计算相似度的方法和阈值，这些方法由参数 `breakpoint_threshold_type` 控制。

+ percentile: 百分位数，默认 95，该参数的取值范围为 0.0 到 100.0 之间，可以使用 `breakpoint_threshold_amount` 调整取值（默认类型）。
+ standard_deviation：标准差，默认 3，可以使用 `breakpoint_threshold_amount` 调整取值。
+ interquartile：四分位数，默认 1.5，可以使用 `breakpoint_threshold_amount` 调整取值。
+ gradient：梯度，默认 95，可以使用 `breakpoint_threshold_amount` 调整取值。

注意：如果生成的块大小太小/太大，可以使用 min_chunk_size 进行调整。



```python
BreakpointThresholdType = Literal[
    "percentile", "standard_deviation", "interquartile", "gradient"
]
BREAKPOINT_DEFAULTS: Dict[BreakpointThresholdType, float] = {
    "percentile": 95,
    "standard_deviation": 3,
    "interquartile": 1.5,
    "gradient": 95,
}
```

接下来使用 SemanticChunker 进行文本语义分块



```python
from langchain_experimental.text_splitter import SemanticChunker
text = """
要实例化SemanticChunker，必须指定一个Embeddings实例。

语义分块器的工作原理是确定何时“拆分”句子，具体方法是查找任意两个句子之间嵌入的差异，当差异超过某个阈值时，句子就会被拆分。

有几种方法可以确定该阈值，这些方法由参数 breakpoint_threshold_type 控制。

percentile: 百分位数，默认 95，该参数的取值范围为 0.0 到 100.0 之间，可以使用 breakpoint_threshold_amount 调整取值（默认类型）。
standard_deviation：标准差，默认 3，可以使用 breakpoint_threshold_amount 调整取值。
interquartile：四分位数，默认 1.5，可以使用 breakpoint_threshold_amount 调整取值。
gradient：梯度，默认 95，可以使用 breakpoint_threshold_amount 调整取值。
注意：如果生成的块大小太小/太大，可以使用 min_chunk_size 进行调整。
"""

text_splitter = SemanticChunker(
    embeddings=embed,
    breakpoint_threshold_type='percentile',
    breakpoint_threshold_amount=95,
    sentence_split_regex=r"(?<=[。？！])\s+" # 自定义句子切分正则表达式，内部使用 re.split(self.sentence_split_regex, text) 切分句子
)

docs = text_splitter.create_documents([text])
print(docs)
print(f'分块数量：{len(docs)}')
```

```plain
[Document(metadata={}, page_content='\n要实例化SemanticChunker，必须指定一个Embeddings实例。 语义分块器的工作原理是确定何时“拆分”句子，具体方法是查找任意两个句子之间嵌入的差异，当差异超过某个阈值时，句子就会被拆分。 有几种方法可以确定该阈值，这些方法由参数 breakpoint_threshold_type 控制。'), Document(metadata={}, page_content='percentile: 百分位数，默认 95，该参数的取值范围为 0.0 到 100.0 之间，可以使用 breakpoint_threshold_amount 调整取值（默认类型）。 standard_deviation：标准差，默认 3，可以使用 breakpoint_threshold_amount 调整取值。 interquartile：四分位数，默认 1.5，可以使用 breakpoint_threshold_amount 调整取值。 gradient：梯度，默认 95，可以使用 breakpoint_threshold_amount 调整取值。 注意：如果生成的块大小太小/太大，可以使用 min_chunk_size 进行调整。 ')]
分块数量：2
```

调整句子断点的阈值 `breakpoint_threshold_amount=50`，测试分块的效果如下：



```python
text_splitter = SemanticChunker(
    embeddings=embed,
    breakpoint_threshold_type='percentile',
    breakpoint_threshold_amount=50,
    sentence_split_regex=r"(?<=[。？！])\s+" # 自定义句子切分正则表达式，内部使用 re.split(self.sentence_split_regex, text) 切分句子
)

docs = text_splitter.create_documents([text])
print(docs)
print(f'分块数量：{len(docs)}')
```

```plain
[Document(metadata={}, page_content='\n要实例化SemanticChunker，必须指定一个Embeddings实例。 语义分块器的工作原理是确定何时“拆分”句子，具体方法是查找任意两个句子之间嵌入的差异，当差异超过某个阈值时，句子就会被拆分。 有几种方法可以确定该阈值，这些方法由参数 breakpoint_threshold_type 控制。'), Document(metadata={}, page_content='percentile: 百分位数，默认 95，该参数的取值范围为 0.0 到 100.0 之间，可以使用 breakpoint_threshold_amount 调整取值（默认类型）。 standard_deviation：标准差，默认 3，可以使用 breakpoint_threshold_amount 调整取值。'), Document(metadata={}, page_content='interquartile：四分位数，默认 1.5，可以使用 breakpoint_threshold_amount 调整取值。'), Document(metadata={}, page_content='gradient：梯度，默认 95，可以使用 breakpoint_threshold_amount 调整取值。 注意：如果生成的块大小太小/太大，可以使用 min_chunk_size 进行调整。'), Document(metadata={}, page_content='')]
分块数量：5
```

> 其他几种计算相似度的方法和阈值不在这里演示，有兴趣的可以尝试修改 `breakpoint_threshold_type` 和 h`breakpoint_threshold_amount` 进行测试
>

## 按标题拆分 Markdown
### 使用 MarkdownHeaderTextSplitter
`MarkdownHeaderTextSplitter` 类的作用是根据指定的Markdown标题（headers）来分割Markdown文档。它能够识别并利用文档中的标题结构，将内容按照这些标题进行分组或分割，从而生成包含特定标题下内容的块。每个块不仅包含了该标题下的文本内容，还保留了与该内容相关的元数据，如标题层级和标题名称。

具体来说，`MarkdownHeaderTextSplitter` 的主要功能包括：

1. 识别标题：根据提供的标题标识符（例如 #, ## 等），识别出Markdown文档中的各个标题。
2. 分组内容：将每个标题下的内容作为一个独立的块进行分组，确保每个块的内容都与其标题紧密相关。
3. 保留元数据：在生成的每个块中，保留与该块内容相关的元数据，如标题的层级和名称，以便后续处理时能够更好地理解内容的上下文。

通过这种方式，`MarkdownHeaderTextSplitter` 能够帮助用户更有效地管理和处理 `Markdown` 文档，特别是在需要对文档进行嵌入、存储和检索等操作时，能够更好地保持内容的结构和语义完整性。这对于构建高效的知识库、问答系统和其他基于文本的应用非常有帮助。

> 如何将 pdf 和 docx 文件转换为 markdown 格式文件，可以查看我前面写的文章
>

详细使用示例查看 [How to split Markdown by Headers](https://python.langchain.com/docs/how_to/markdown_header_metadata_splitter/)

下面是一个使用 markdown 文本进行分块的示例。

示例文本：

```python

text = """
以下是基于语义相似度的分块实现思路总结，该方法通过 **嵌入距离检测语义边界** 实现智能分块：

---

### **核心思路**
1. **分句处理**  
   将原始文本按句子粒度拆分（如使用 `spaCy`、`nltk` 或标点规则）。
2. **滑动窗口聚合**  
   将连续句子组成 **窗口**（如 3 个句子为一个窗口），计算窗口的嵌入表示。
3. **嵌入距离计算**  
   滑动窗口逐步后移（如每次移除前一句，添加下一句），计算相邻窗口嵌入的相似度（如余弦距离）。
4. **断点检测**  
   若相邻窗口的嵌入距离超过预设 **阈值**，则认为此处存在语义边界，触发分块。
5. **合并相邻块**  
   将未触发断点的相邻窗口合并为同一块，保持语义连贯性。

---

### **具体步骤示例**
#### **输入文本**
句子1：深度学习是机器学习的分支。
句子2：它通过神经网络模拟人脑的学习过程。
句子3：常见的模型包括CNN和RNN。
句子4：自然语言处理（NLP）是其重要应用领域。
句子5：BERT和GPT是NLP中的代表性模型。  

#### **分块过程**
1. **窗口生成**  
   - 窗口1：[句子1, 句子2, 句子3]  
   - 窗口2：[句子2, 句子3, 句子4]  
   - 窗口3：[句子3, 句子4, 句子5]  
2. **嵌入计算**  
   - 获取每个窗口的嵌入向量（如使用 Sentence-BERT）。  
3. **距离比较**  
   - 计算窗口1与窗口2的嵌入距离 → 假设距离较小（主题连续：深度学习→模型）。  
   - 计算窗口2与窗口3的嵌入距离 → 假设距离较大（主题切换：模型→NLP应用）。  
4. **断点触发**  
   - 在窗口2与窗口3之间触发分块。  
5. **最终分块**  
   - 块1：[句子1, 句子2, 句子3]  
   - 块2：[句子4, 句子5]

---

### **优点与缺点**
| **优点**                                      | **缺点**                                      |
|----------------------------------------------|----------------------------------------------|
| ✅ 自适应语义边界，避免机械切分                 | ❌ 计算成本高（需多次嵌入计算和相似度比较）     |
| ✅ 减少噪声（窗口聚合降低单句波动影响）          | ❌ 依赖嵌入模型质量（如语义表示不准确则分块失效）|
| ✅ 适配不同文本类型（技术文档、对话等）          | ❌ 参数敏感（需调优窗口大小、阈值）             |

---

### **关键参数与调优建议**
1. **窗口大小**  
   - 过小：噪声敏感（如窗口=1时退化为单句比较）。  
   - 过大：语义边界模糊（如窗口=5可能掩盖局部变化）。  
   - **建议值**：2-4 个句子（根据文本密度调整）。  
2. **相似度阈值**  
   - 过高：分块过少，块内语义混杂。  
   - 过低：分块过多，破坏连贯性。  
   - **调优方法**：通过验证集测试不同阈值下的分块质量（如人工评估或检索召回率）。  
3. **嵌入模型选择**  
   - 优先领域适配模型（如技术文本用 `all-mpnet-base-v2`，通用文本用 `text-embedding-3-small`）。

---

### **改进方向**
1. **动态窗口调整**  
   根据文本复杂度自动扩展/收缩窗口（如密集段落用小窗口，冗余内容用大窗口）。  
2. **混合分块策略**  
   先按标题/段落粗分块，再对长段落应用语义分块。  
3. **轻量化计算**  
   - 使用低维嵌入（如 PCA 降维）。  
   - 缓存嵌入结果减少重复计算。  

---

### **适用场景**
- **技术文档**：精准切分章节、案例、代码块。  
- **长对话记录**：按话题切换分割会话阶段。  
- **跨段落推理任务**：确保块内语义高度相关。  

通过该方法，可显著提升 RAG 等应用中检索内容的语义连贯性和相关性。
"""

```

分块代码：

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document
import json

def markdown_splitter_by_header(markdown_content: str) -> List[Document]:
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
        ("#####", "Header 5"),
        ("######", "Header 6"),
        ("#######", "Header 7"),
    ]

    # MD splits
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,  # 分块的标题级别
        strip_headers=False,  # 是否去除content中的标题
        return_each_line = False # 是否返回单独行，也就是每一个单独行作为一个分块
    )
    md_header_splits = markdown_splitter.split_text(markdown_content)
    return md_header_splits

chunks = markdown_splitter_by_header(text)

for chunk in chunks:
    chunk_dict = chunk.model_dump()
    json_str = json.dumps(chunk_dict, indent=4, ensure_ascii=False)
    print(json_str)

```

输出结果：

```plain
{
    "id": null,
    "metadata": {},
    "page_content": "以下是基于语义相似度的分块实现思路总结，该方法通过 **嵌入距离检测语义边界** 实现智能分块：  \n---",
    "type": "Document"
}
{
    "id": null,
    "metadata": {
        "Header 3": "**核心思路**"
    },
    "page_content": "### **核心思路**\n1. **分句处理**\n将原始文本按句子粒度拆分（如使用 `spaCy`、`nltk` 或标点规则）。\n2. **滑动窗口聚合**\n将连续句子组成 **窗口**（如 3 个句子为一个窗口），计算窗口的嵌入表示。\n3. **嵌入距离计算**\n滑动窗口逐步后移（如每次移除前一句，添加下一句），计算相邻窗口嵌入的相似度（如余弦距离）。\n4. **断点检测**\n若相邻窗口的嵌入距离超过预设 **阈值**，则认为此处存在语义边界，触发分块。\n5. **合并相邻块**\n将未触发断点的相邻窗口合并为同一块，保持语义连贯性。  \n---",
    "type": "Document"
}
{
    "id": null,
    "metadata": {
        "Header 3": "**具体步骤示例**",
        "Header 4": "**输入文本**"
    },
    "page_content": "### **具体步骤示例**  \n#### **输入文本**\n```\n句子1：深度学习是机器学习的分支。\n句子2：它通过神经网络模拟人脑的学习过程。\n句子3：常见的模型包括CNN和RNN。\n句子4：自然语言处理（NLP）是其重要应用领域。\n句子5：BERT和GPT是NLP中的代表性模型。\n```",
    "type": "Document"
}
{
    "id": null,
    "metadata": {
        "Header 3": "**具体步骤示例**",
        "Header 4": "**分块过程**"
    },
    "page_content": "#### **分块过程**\n1. **窗口生成**\n- 窗口1：[句子1, 句子2, 句子3]\n- 窗口2：[句子2, 句子3, 句子4]\n- 窗口3：[句子3, 句子4, 句子5]\n2. **嵌入计算**\n- 获取每个窗口的嵌入向量（如使用 Sentence-BERT）。\n3. **距离比较**\n- 计算窗口1与窗口2的嵌入距离 → 假设距离较小（主题连续：深度学习→模型）。\n- 计算窗口2与窗口3的嵌入距离 → 假设距离较大（主题切换：模型→NLP应用）。\n4. **断点触发**\n- 在窗口2与窗口3之间触发分块。\n5. **最终分块**\n- 块1：[句子1, 句子2, 句子3]\n- 块2：[句子4, 句子5]  \n---",
    "type": "Document"
}
{
    "id": null,
    "metadata": {
        "Header 3": "**优点与缺点**"
    },
    "page_content": "### **优点与缺点**\n| **优点**                                      | **缺点**                                      |\n|----------------------------------------------|----------------------------------------------|\n| ✅ 自适应语义边界，避免机械切分                 | ❌ 计算成本高（需多次嵌入计算和相似度比较）     |\n| ✅ 减少噪声（窗口聚合降低单句波动影响）          | ❌ 依赖嵌入模型质量（如语义表示不准确则分块失效）|\n| ✅ 适配不同文本类型（技术文档、对话等）          | ❌ 参数敏感（需调优窗口大小、阈值）             |  \n---",
    "type": "Document"
}
{
    "id": null,
    "metadata": {
        "Header 3": "**关键参数与调优建议**"
    },
    "page_content": "### **关键参数与调优建议**\n1. **窗口大小**\n- 过小：噪声敏感（如窗口=1时退化为单句比较）。\n- 过大：语义边界模糊（如窗口=5可能掩盖局部变化）。\n- **建议值**：2-4 个句子（根据文本密度调整）。\n2. **相似度阈值**\n- 过高：分块过少，块内语义混杂。\n- 过低：分块过多，破坏连贯性。\n- **调优方法**：通过验证集测试不同阈值下的分块质量（如人工评估或检索召回率）。\n3. **嵌入模型选择**\n- 优先领域适配模型（如技术文本用 `all-mpnet-base-v2`，通用文本用 `text-embedding-3-small`）。  \n---",
    "type": "Document"
}
{
    "id": null,
    "metadata": {
        "Header 3": "**改进方向**"
    },
    "page_content": "### **改进方向**\n1. **动态窗口调整**\n根据文本复杂度自动扩展/收缩窗口（如密集段落用小窗口，冗余内容用大窗口）。\n2. **混合分块策略**\n先按标题/段落粗分块，再对长段落应用语义分块。\n3. **轻量化计算**\n- 使用低维嵌入（如 PCA 降维）。\n- 缓存嵌入结果减少重复计算。  \n---",
    "type": "Document"
}
{
    "id": null,
    "metadata": {
        "Header 3": "**适用场景**"
    },
    "page_content": "### **适用场景**\n- **技术文档**：精准切分章节、案例、代码块。\n- **长对话记录**：按话题切换分割会话阶段。\n- **跨段落推理任务**：确保块内语义高度相关。  \n通过该方法，可显著提升 RAG 等应用中检索内容的语义连贯性和相关性。",
    "type": "Document"
}
```

### 如何限制块的大小
从前面分块的结果可以看到，markdown 文本按照标题的层级结构分块，从前面的结果可以分块还是比较符合预期的。

但是存在一个问题，如果一个标题下面的文本内容太长，那么需要限制块的大小，也就是需要对同一个标题下的文本继续分块，可以结合 `RecursiveCharacterTextSplitter` 来进一步控制块的大小



```python
from transformers import PreTrainedTokenizerBase

def text_splitter_by_token_num(docs: List[Document],
                               chunk_size: int = 512,
                               chunk_overlap: int = 0,
                               tokenizer: Optional[PreTrainedTokenizerBase] = None,
                               separators: Optional[List[str]] = None) -> List[Document]:
    """
    按照token数拆分文本
    :param separators: chunk 分隔符列表
    :param docs: 文档列表
    :param tokenizer: 分词器
    :param chunk_size: 每个chunk的token数
    :param chunk_overlap: 重叠部分的token数

    :return:
    """
    if separators is None:
        separators = ["\n\n", "\n", ".", "。"]
    if tokenizer:
        text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
        )
    else:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
        )
    results = []
    for doc in docs:
        if not doc.page_content:
            continue
        else:
            content = doc.page_content
            splits = text_splitter.split_text(text=content)
            for split in splits:
                if not split:
                    continue
                else:
                    metadata = deepcopy(doc.metadata)
                    new_doc = Document(page_content=split, metadata=metadata)
                    results.append(new_doc)
    return results

```

### markdown 分块其他挑战
+ 如何提取markdown文件中的完整表格，也就是尽可能将表格放在一个分块中。
+ 如何提取markdown文件中的完整代码块，也就是尽可能将代码块放在一个分块中。
+ 如何提取和识别markdown文件中的图片，将图片内容识别出来放在一个分块中。

关于这几个问题，会在后续文章中介绍，请继续关注。

## 动态分块
关于动态分块的基本思路是：根据输入文件的类型动态的选项对应的分块逻辑，分块逻辑使用langchain的实现：

json文件：`RecursiveJsonSplitter`

html文件选择合适的：

+ 使用`HTMLHeaderTextSplitter`情况：需要根据标题层次结构拆分 HTML 文档并维护有关标题的元数据。
+ 使用`HTMLSectionSplitter`情况：需要将文档拆分为更大、更通用的部分，可能基于自定义标签或字体大小。
+ 使用`HTMLSemanticPreservingSplitter`情况：需要将文档拆分成块，同时保留表格和列表等语义元素，确保它们不会被拆分并且它们的上下文得到维护。

markdown文件：`MarkdownHeaderTextSplitter`



## 总结
最后总结一下各个分块方法的优缺点如下：

| **分块方法** | **方法描述** | **优点** | **缺点** |
| --- | --- | --- | --- |
| **按字符分块** | 基于固定字符数切分文本（如每 200 个字符一个块）。 | ✅ 实现简单   ✅ 无需依赖分词工具 | ❌ 破坏单词/句子结构   ❌ 多语言适配性差 |
| **按 Token 分块** | 基于模型分词器（Tokenizer）的 token 数切分（如每 256 tokens 一个块）。 | ✅ 适配模型输入限制   ✅ 计算成本低 | ❌ 可能切断语义边界   ❌ 依赖分词器性能 |
| **按语义分块** | 利用 NLP 工具或规则识别语义边界（如句子、段落、章节）。 | ✅ 保留语义完整性   ✅ 适配结构化文本 | ❌ 依赖文本结构或模型   ❌ 计算成本高 |
| **按 Markdown 层次化分块** | 根据 Markdown 标题层级（如 `#`、`##`）划分块，保留文档结构。 | ✅ 保持文档逻辑结构   ✅ 无需复杂 NLP 处理 | ❌ 仅支持 Markdown 格式   ❌ 格式错误导致分块失败 |
| **动态分块** | 根据文档类型和内容动态调整块大小（如html文件，json文件，代码等使用不同的分块策略）。 | ✅ 灵活适配文本特性   ✅ 优化信息覆盖率 | ❌ 实现复杂度高   ❌ 需定制规则或模型 |


下一篇文章将介绍如何将分块后的内容存储到向量数据库中，以便RAG应用检索，请继续关注。



参考文档：

[https://python.langchain.com/docs/how_to/](https://python.langchain.com/docs/how_to/)

