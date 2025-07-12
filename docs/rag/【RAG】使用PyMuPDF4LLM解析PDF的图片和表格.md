# 【RAG】使用PyMuPDF4LLM解析PDF的图片和表格
## 概述
最近在做RAG相关的应用，需要对PDF文件进行解析处理，最开始使用`PyPDF2`，该工具只能从PDF文件中提取纯文本且没有格式。很多的PDF文件中包含图片和表格，需要将图片和表格都提取出来，并且需要保留PDF文件的文本格式。通过查阅相关文档，找到一个开源工具 [pymupdf4llm](https://github.com/pymupdf/RAG/tree/main/pymupdf4llm)，这个包使用 `PyMuPDF` 将PDF的页面转换为Markdown格式的文本，并且支持表格和图片抽取。

本文从下面几个方面进行介绍：

+ 介绍 `pymupdf4llm` 的使用，并且给出相关的使用示例。
+ 介绍自己封装的工具，能够将PDF（在线/本地）文件转换为markdown文件，并且将PDF中解析出的图片上传到OSS中。该工具也可以作为markdown文件的本地图片转在线图片的工具。

通过本文的学习，你将有如下收获：

+ 了解 `pymupdf4llm`的基本使用。
+ 了解如何将PDF（在线/本地）文件转换为markdown文件，并且将PDF中解析出的图片上传到OSS中。



## PyMuPDF4LLM介绍
PyMuPDF4LLM 是一个强大的工具，用于从 PDF 文件中提取数据，支持将文本、表格、图像和矢量图形转换为 Markdown 格式，并且可以与 LlamaIndex、langchain 集成，适用于 LLM 相关工作。

### PyMuPDF4LLM特点
+ **PyMuPDF4LLM 是一个灵活、快速的工具**，能够胜任各种 PDF 数据提取任务，特别适合大型语言模型（LLM）和知识检索系统的数据准备工作。
+ **提取的数据格式多样**，包括 Markdown、图像、表格和元数据，这些格式对于 LLM 的微调和知识检索系统的构建至关重要。
+ **PyMuPDF4LLM 能够高质量提取**，无论是文本的结构化提取、特定页面的数据提取，还是复杂的表格和图像的高质量提取。
+ **PyMuPDF4LLM 对于 NLP 任务尤其有用**，因为它能够保留文本的上下文和单词级别的信息，这对于模型的性能至关重要。

### PyMuPDF4LLM的API
接口文档： [PyMuPDF4LLM API](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html#pymupdf4llm-api)

在 **PyMuPDF4LLM**中最重要的一个方法是 `to_markdown`，该方法各参数的解释如下：

```python
def to_markdown(
    doc: pymupdf.Document | str, 
    *, 
    pages: list | range | None = None, 
    hdr_info: Any = None, 
    write_images: bool = False, 
    embed_images: bool = False, 
    dpi: int = 150, 
    image_path='', 
    image_format='png', 
    image_size_limit=0.05, 
    force_text=True, 
    margins=(0, 50, 0, 50), 
    page_chunks: bool = False, 
    page_width: float = 612, 
    page_height: float = None, 
    table_strategy='lines_strict', 
    graphics_limit: int = None, 
    ignore_code: bool = False, 
    extract_words: bool = False, 
    show_progress: bool = True
) -> str | list[dict]:
```

参数说明：

+ **doc (Document, str)**: 文件，可以指定为文件路径字符串或 PyMuPDF Document（通过 `pymupdf.open` 创建）。为了使用 `pathlib.Path` 规范、Python 文件对象、内存中的文档等，必须使用 PyMuPDF Document。
+ **pages (list)**: 可选，要处理的页面（注意：指定的是从0开始的页码）。如果省略，则处理所有页面。
+ **hdr_info**: 可选。如果你希望提供自己的标题检测逻辑，可以使用此参数。这可以是一个可调用对象或具有 `get_header_id` 方法的对象。它必须接受一个文本片段（包含在 `extractDICT()` 中的字典）和一个关键字参数 `page`（页面对象），并返回一个字符串，该字符串可以为空或最多包含6个 `#` 字符后跟一个空格。如果省略，将对整个文档进行扫描以找到最常见的字体大小，并根据它们推导出标题级别。要完全避免这种行为，可以指定 `hdr_info=lambda s, page=None: ""` 或 `hdr_info=False`。
+ **write_images (bool)**: 当遇到图像或矢量图形时，会从相应的页面区域创建图像并存储在指定的文件夹中。Markdown 将引用指向这些图像的链接。任何包含在这些区域中的文本将不会包含在文本输出中（但会作为图像的一部分出现），因此如果文档中有文本写在全页图像上，请确保将此参数设置为 `False`。
+ **embed_images (bool)**: 类似于 `write_images`，但图像将以 base64 编码的形式嵌入到 Markdown 文本中。该参数会忽略 `write_images` 和 `image_path`，这可能会大幅增加 Markdown 文本的大小。
+ **image_size_limit (float)**: 必须是一个小于1的正数。如果图像的宽度或高度小于页面宽度或高度的 `image_size_limit` 倍，则忽略该图像。例如默认值 0.05 意味着要提取图像的宽度和高度必须大于页面宽度和高度的 5%。
+ **dpi (int)**: 指定所需的图像分辨率（每英寸点数）。仅在 `write_images=True` 时相关，默认值为 150。
+ **image_path (str)**: 存储图像的文件夹。仅在 `write_images=True` 时生效，默认是脚本目录的路径。
+ **image_format (str)**: 通过其扩展名指定所需的图像格式。默认是 "png"（便携式网络图形），另一个流行的格式可能是 "jpg"，可能的值包括所有支持的输出格式。
+ **force_text (bool)**: 即使有重叠的图像/图形，也生成文本输出。此文本将在相应图像之后出现，如果 `write_images=True`，此参数可以设置为 `False` 以抑制图像上的重复文本。
+ **margins (float, list)**: 
    - 一个浮点数或包含 2 或 4 个浮点数的序列，指定页面边界。只有在边界内的对象才会被考虑用于输出。
    - `margin=f` 生成 `(f, f, f, f)`，表示 (左, 上, 右, 下) 边界。
    - `(top, bottom)` 生成 `(0, top, 0, bottom)`。
    - 要始终读取完整页面，使用 `margins=0`。
+ **page_chunks (bool)**: 如果为 `True`，输出将是一个包含 `Document.page_count` 个字典的列表（每个页面一个字典）。每个字典的结构如下：
    - `"metadata"` - 包含文档元数据 `Document.metadata` 的字典，附加了额外的键 `"file_path"`（文件名）、`"page_count"`（文档中的页数）和 `"page_number"`（1-based 页码）。
    - `"toc_items"` - 指向此页面的目录项列表。每个项的格式为 `[lvl, title, pagenumber]`，其中 `lvl` 是层次级别，`title` 是字符串，`pagenumber` 是 1-based 页码。
    - `"tables"` - 页面上的表格列表。每个项是一个字典，包含键 `"bbox"`（表格在页面上的位置，格式为 `pymupdf.Rect` 的元组）、`"row_count"` 和 `"col_count"`。
    - `"images"` - 页面上的图像列表。这是页面方法 `Page.get_image_info()` 返回的副本。
    - `"graphics"` - 页面上的矢量图形矩形列表。这是页面方法 `Page.cluster_drawings()` 返回的边界框列表。
    - `"text"` - 页面内容的 Markdown 文本。
    - `"words"` - 如果使用了 `extract_words=True`，则包含此键。其值是一个列表，包含由 PyMuPDF 的 `Page` 方法 `get_text("words")` 返回的元组 `(x0, y0, x1, y1, "wordstring", bno, lno, wno)`。这些元组的顺序与 Markdown 文本字符串中提取的文本顺序相同，对于表格中的文本也是如此，单词按表格行单元格的顺序提取。
+ **page_width (float)**: 指定所需的页面宽度。对于固定页面宽度的文档（如 PDF、XPS 等），此参数将被忽略。对于可流动的文档（如电子书、办公文档或文本文件），这些文档没有固定的页面尺寸，默认假设为 Letter 格式的宽度（612）和“无限”的页面高度。这意味着整个文档被视为一个大页面。
+ **page_height (float)**: 指定所需的页面高度。相关性见 `page_width` 参数，如果使用默认值 `None`，文档将被视为一个大页面，宽度为 `page_width`。因此在这种情况下，不会出现 Markdown 页面分隔符（除了最后一个），或者只返回一个页面块。
+ **table_strategy (str)**: 表格检测策略。默认值为 `"lines_strict"`，忽略背景颜色。在某些情况下，其他策略可能更成功，例如 `"lines"` 使用所有矢量图形对象进行检测。
+ **graphics_limit (int)**: 用于限制处理过多的矢量图形元素。通常，科学文档或使用图形命令模拟文本的页面可能包含成千上万的这些对象。由于矢量图形主要用于表格检测，分析此类页面可能导致过长的运行时间。你可以通过设置 `graphics_limit=5000` 或更小的值来排除问题页面。相应的页面将被忽略，并在输出文本中用一条消息行表示。
+ **ignore_code (bool)**: 如果为 `True`，则等宽文本不会收到特殊的格式处理，代码块将不再生成。如果使用了 `extract_words=True`，此值将被设置为 `True`。
+ **extract_words (bool)**: 如果为 `True`，则强制 `page_chunks=True` 并在每个页面字典中添加 `"words"` 键。其值是由 PyMuPDF 的 `Page` 方法 `get_text("words")` 返回的单词列表。这些单词的顺序与提取的文本相同。
+ **show_progress (bool)**: 如果为 `True`（默认值），则在页面转换为 Markdown 时显示基于文本的进度条。进度条看起来类似于以下形式：

返回值：

+ 要么是所选文档页面的组合文本字符串，要么是一个字典列表。

### PyMuPDF4LLM实战
首先使用 pip 安装 PyMuPDF4LLM：

```shell
pip install pymupdf4llm
```

#### 用例 1：基本 Markdown 提取
你有一份 PDF 文件，但只想得到简洁、Markdown 友好格式的内容。PyMuPDF4LLM 可以提取带有标题、列表和其他格式的文本，使其易于使用。

```python
import pymupdf4llm

# Extract PDF content as Markdown
md_text = pymupdf4llm.to_markdown("INVAR-RAG.pdf")
print(md_text[:500])  # Print first 500 characters

```

在这个例子中，我使用 PyMuPDF4LLM 将一篇研究论文的内容提取为 Markdown 格式。

> 为什么是 Markdown格式？因为它是微调模型的理想选择，因为它保留了结构和格式，这对于从 LLM 生成连贯的响应至关重要。
>

#### 用例 2：提取特定页面
有时只需要文档的一部分，也许只是用于训练的特定内容，使用 PyMuPDF4LLM 可以精确地确定要提取哪些页面，从而节省时间和资源。

```python
import pymupdf4llm

# Extract PDF content as Markdown
md_text = pymupdf4llm.to_markdown("INVAR-RAG.pdf", pages=[3, 9])
print(md_text[:500])  # Print first 500 characters
```

这一功能在处理海量文件时尤其有用，例如提取特定的章节或部分可以方便地只对最相关的信息进行 LLM 训练。



#### 用例 3：图片提取
与文本一起提取图像经常被忽视，但却非常重要，尤其是对于包含数字、图表的文档，PyMuPDF4LLM 可以方便地处理它。

```python
md_text_images = pymupdf4llm.to_markdown(doc="INVAR-RAG.pdf",
                                         pages=[3, 9]
                                         page_chunks=True,
                                         write_images=True,
                                         image_path="images",
                                         image_format="jpg",
                                         dpi=200)
print(md_text_images[0]['images'])  # Print image information from the first chunk
```

#### 用例 4：表格提取
表格很难在不丢失格式的情况下从 PDF 中提取出来，虽然PyMuPDF4LLM 能优雅地处理这一问题，确保表格干净整洁，但是不能够保证准确提取表格格式和数据。

```python
import pymupdf4llm


md_text_tables = pymupdf4llm.to_markdown(doc="INVAR-RAG.pdf",
                                         pages=[6],  # Specify pages containing tables
                                         )
print(md_text_tables)
```

#### 用例 5：将 Markdown 保存到文件中
提取数据后将其保存为便于再次访问或共享的markdown格式。

```python
import pymupdf4llm
from pathlib import Path

# Extract PDF content as Markdown
md_text = pymupdf4llm.to_markdown("INVAR-RAG.pdf")

Path("output.md").write_bytes(md_text.encode())
print("Markdown saved to output.md")
```

将提取的数据存储在 Markdown 中可以方便地进行管理和查看，尤其是在 LLM 微调以及知识库准备数据使用。  


## PDF图片和表格解析工具
接下来介绍一下使用 pymupdf4llm 封装的工具

功能描述：将本地或者在线的pdf文件转换为markdown格式，并且将pdf文件中提取的图片上传到oss中。

要实现上述功能，可以按照以下步骤进行：

1. **读取pdf文件**：如果为本地文件则直接读取，如果是远程文件则下载到本地再读取。
2. **转换为Markdown文件**：使用 pymupdf4llm 将 pdf 文件转换为 Markdown 文件。
3. **解析Markdown文件图片路径**：使用正则表达式解析出图片路径。
4. **上传图片到OSS**：判断图片路径是否为本地路径，如果是本地路径，则将图片上传到阿里云OSS。
5. **更新Markdown内容**：将Markdown文件中的本地图片路径替换为OSS上的URL。
6. **保存更新后的Markdown文件**。

下面是一个完整的示例代码，展示了如何实现上述步骤：

## 代码实现
```python
import oss2
import os
import re
import requests
import hashlib

import pymupdf4llm
from enum import Enum
from tempfile import TemporaryDirectory
from typing import Optional, Dict
from pathlib import Path
from urllib.parse import urlparse

# 阿里云OSS配置
ACCESS_KEY_ID = 'xxxx'
ACCESS_KEY_SECRET = 'xxxx'
BUCKET_NAME = 'xxxx'
# 填写Bucket所在地域对应的Endpoint。
ENDPOINT = "cn-hangzhou.alipay.aliyun-inc.com"
# 填写Endpoint对应的Region信息，例如cn-hangzhou。注意，v4签名下，必须填写该参数
REGION = "cn-hangzhou"

# 设置到环境变量中
os.environ['OSS_ACCESS_KEY_ID'] = ACCESS_KEY_ID
os.environ['OSS_ACCESS_KEY_SECRET'] = ACCESS_KEY_SECRET
os.environ['OSS_ENDPOINT'] = ENDPOINT
os.environ['OSS_BUCKET_NAME'] = BUCKET_NAME
os.environ['OSS_REGION'] = REGION

# oss url expires: 过期时间（单位：秒），链接在当前时间再过expires秒后过期
oss_url_expires = 60 * 60 * 24 * 365


class UploadMode(Enum):
    """Upload mode."""
    # 上传所有图片
    ALL = "all"
    # 本地图片上传
    LOCAL = "local"


def is_valid_url(url: str) -> bool:
    """
    检查URL是否有效
    :param url: URL
    :return: 是否有效
    """
    """Check if the url is valid."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def handle_remote_file(file_path: str, temp_dir: TemporaryDirectory, headers: Optional[Dict] = None):
    """
    处理远程文件
    :param file_path: 文件路径
    :param temp_dir: 临时目录
    :param headers: 请求头
    :return: 文件路径
    """
    # If the file is a web path, download it to a temporary file, and use that
    if not os.path.isfile(file_path) and is_valid_url(file_path):
        web_path = file_path
        r = requests.get(web_path, headers=headers)
        if r.status_code != 200:
            raise ValueError(
                "Check the url of your file; returned status code %s"
                % r.status_code
            )
        _, suffix = os.path.splitext(file_path)
        suffix = suffix.split("?")[0]
        # 使用MD5算法
        md5_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        temp_pdf = os.path.join(temp_dir.name, f"tmp_{md5_hash}{suffix}")
        with open(temp_pdf, mode="wb") as f:
            f.write(r.content)
        file_path = str(temp_pdf)
    elif not os.path.isfile(file_path):
        raise ValueError("File path %s is not a valid file or url" % file_path)

    return file_path


def get_bucket():
    """
    获取OSS Bucket对象
    :return: OSS Bucket对象
    """
    # 从环境变量中获取ACCESS_KEY_ID
    access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
    # 从环境变量中获取ACCESS_KEY_SECRET
    access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
    # 从环境变量中获取ENDPOINT
    endpoint = os.getenv('OSS_ENDPOINT')
    # 从环境变量中获取BUCKET_NAME
    bucket_name = os.getenv('OSS_BUCKET_NAME')
    # 从环境变量中获取REGION
    region = os.getenv('OSS_REGION')

    if not access_key_id:
        raise ValueError("OSS_ACCESS_KEY_ID must be set as an environment variable.")
    if not access_key_secret:
        raise ValueError("OSS_ACCESS_KEY_SECRET must be set as an environment variable.")
    if not endpoint:
        raise ValueError("OSS_ENDPOINT must be set as an environment variable.")
    if not bucket_name:
        raise ValueError("OSS_BUCKET_NAME must be set as an environment variable.")

    auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    return oss2.Bucket(auth=auth, endpoint=ENDPOINT, bucket_name=BUCKET_NAME, region=region)


def upload_to_oss(file_path: str, bucket: oss2.Bucket):
    """
    上传文件到OSS并返回URL
    :param file_path: 文件路径
    :param bucket: OSS Bucket对象
    :return: 预览URL
    """
    # 判断文件是否存在
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None

    # 解析文件名和扩展名
    filename, ext = os.path.splitext(os.path.basename(file_path))
    # 构造OSS文件名，确保不重复
    oss_filename = f"{filename}{ext}"
    # 上传文件到OSS
    with open(file_path, 'rb') as data:
        result = bucket.put_object(oss_filename, data)
        if result.status == 200:
            print(f"File {file_path} uploaded successfully to OSS as {oss_filename}")
            preview_url = bucket.sign_url('GET', oss_filename, oss_url_expires)
            return preview_url
    return file_path


def get_image_path(image_path: str,
                   mode: UploadMode,
                   md_file_path: str,
                   temp_dir: TemporaryDirectory):
    """
    获取图片的绝对路径
    :param image_path: 图片路径
    :param mode: 图片上传模式，默认为UploadMode.LOCAL（仅本地图片）
    :param md_file_path: Markdown文件路径
    :param temp_dir: 临时目录对象，用于保存远程图片
    """
    # 检查是否为远程图片
    if mode == UploadMode.ALL:
        # 将远程图片保存到本地并返回本地路径
        image_path = handle_remote_file(image_path, temp_dir)
        return image_path

    # 检查是否为相对路径
    if not os.path.isabs(image_path):
        # 获取Markdown文件所在的目录
        base_dir = os.path.dirname(md_file_path)
        image_path = os.path.join(base_dir, image_path)

    return image_path


def get_new_image_path(match: tuple,
                       bucket: oss2.Bucket,
                       mode: UploadMode,
                       md_file_path: str,
                       temp_dir: TemporaryDirectory):
    """
    根据匹配的图片路径和模式，获取新的图片路径
    :param match: 匹配的图片路径元组（alt_text, image_path）
    :param bucket: OSS Bucket对象
    :param mode: 图片上传模式，默认为UploadMode.LOCAL（仅本地图片）
    :param md_file_path: Markdown文件路径
    :param temp_dir: 临时目录对象，用于保存远程图片
    """
    alt_text, image_path = match
    # 获取图片的绝对路径
    image_path = get_image_path(image_path=image_path, mode=mode, md_file_path=md_file_path, temp_dir=temp_dir)

    # 上传图片到OSS并获取URL
    oss_url = upload_to_oss(image_path, bucket)

    if alt_text:
        new_image_path = f"![{alt_text}]({oss_url})"
    else:
        # 解析图片文件名和扩展名
        filename = os.path.basename(image_path)
        new_image_path = f"![{filename}]({oss_url})"

    return new_image_path


def replace_local_images_with_oss_url(md_file_path: str,
                                      temp_dir: TemporaryDirectory,
                                      mode: UploadMode = UploadMode.LOCAL,
                                      bucket: oss2.Bucket = None, ):
    """
    替换Markdown文件中的本地图片路径为OSS URL
    :param md_file_path: Markdown文件路径
    :param temp_dir: 临时目录对象，用于保存远程图片
    :param mode: 图片上传模式，默认为UploadMode.LOCAL（仅本地图片）
    :param bucket: OSS Bucket对象，如果已提供则直接使用，否则会创建一个新的Bucket对象
    """
    if not md_file_path.endswith('.md'):
        print(f"Skipping non-Markdown file: {md_file_path}")
        return

    with open(md_file_path, 'r', encoding='utf-8') as md_file:
        content = md_file.read()

    if not bucket:
        bucket = get_bucket()

    print(f'开始替换图片: {md_file_path}')
    # 匹配Markdown文件中的图片路径
    pattern = r'!\[(.*?)\]\((.*?)\)'
    matches = re.findall(pattern, content)
    print(f'匹配到 {len(matches)} 张图片')

    replace_num = 0
    new_content = content
    # 上传并替换图片
    for match in matches:
        alt_text, image_path = match
        old_image_path = f"![{alt_text}]({image_path})"

        new_image_path = get_new_image_path(match=match,
                                            bucket=bucket,
                                            mode=mode,
                                            md_file_path=md_file_path,
                                            temp_dir=temp_dir)

        if new_image_path:
            print(f"Replacing {old_image_path} with {new_image_path}")
            new_content = new_content.replace(old_image_path, new_image_path)
            replace_num += 1
    # 写回Markdown文件
    with open(md_file_path, 'w') as file:
        file.write(new_content)
    print(f"替换完成，共替换 {replace_num} 张图片")
    return replace_num


def replace_local_images_with_oss_url_from_folder(folder_path: str,
                                                  mode: UploadMode = UploadMode.LOCAL,
                                                  bucket: oss2.Bucket = None):
    """替换Markdown文件夹中的本地图片路径为OSS URL"""
    if not bucket:
        bucket = get_bucket()
    # 创建临时文件夹
    temp_dir = TemporaryDirectory()
    # 遍历Markdown文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                md_file_path = os.path.join(root, file)
                replace_local_images_with_oss_url(md_file_path=md_file_path, mode=mode, bucket=bucket,
                                                  temp_dir=temp_dir)


def pdf_to_markdown(file_path: str,
                    temp_dir: TemporaryDirectory,
                    md_file_path: str = None,
                    image_path: str = None,
                    is_upload_images: bool = True,
                    write_images: bool = True,
                    image_format: str = "png",
                    dpi: int = 200):
    file_path = handle_remote_file(file_path, temp_dir=temp_dir)

    # if not file_path.endswith(".pdf"):
    #     raise ValueError(f"文件格式不正确，仅支持pdf格式, 当前文件格式为{file_path}")

    if md_file_path is None:
        # 解析文件名和扩展名
        filename, ext = os.path.splitext(os.path.basename(file_path))
        md_file_path = os.path.join(temp_dir.name, f"{filename}.md")

    if image_path is None:
        image_path = os.path.join(os.path.dirname(md_file_path), f"images")

    # 读取PDF文件
    md_text = pymupdf4llm.to_markdown(doc=file_path,
                                      write_images=write_images,
                                      image_path=image_path,
                                      image_format=image_format,
                                      dpi=dpi,
                                      )

    # 写入Markdown文件
    Path(md_file_path).write_bytes(md_text.encode())
    print(f"Markdown文件已生成: {md_file_path}")
    # 上传图片到OSS并获取URL
    if is_upload_images:
        print(f"开始上传图片到OSS: {md_file_path}")
        replace_local_images_with_oss_url(md_file_path, temp_dir)
        print(f"上传图片后的Markdown文件已生成: {md_file_path}")
    return md_file_path


# 使用示例
if __name__ == "__main__":
    # 创建临时文件夹
    temp_dir2 = TemporaryDirectory()
    file_path2 = "https://arxiv.org/pdf/2411.07396"
    md_file_path2 = pdf_to_markdown(file_path2, temp_dir2)
    with open(md_file_path2, 'r', encoding='utf-8') as file:
        content2 = file.read()

    with open('test.md', 'w', encoding='utf-8') as file:
        file.write(content2)

```

## 效果演示
### 在线PDF文件转换
接下来使用上面的代码演示如何将 [arxiv](https://arxiv.org/) 中的论文直接转换为 markdown 格式，并且转换后的图片上传到oss中。

随便找一篇论文即可，示例代码如下：

```python
# 使用示例
if __name__ == "__main__":
    # 创建临时文件夹，代码运行结束会自动删除临时文件和其中的所有内容
    temp_dir2 = TemporaryDirectory()
    file_path2 = "https://arxiv.org/pdf/2411.07396"
    md_file_path2 = pdf_to_markdown(file_path2, temp_dir2)
    with open(md_file_path2, 'r', encoding='utf-8') as file:
        content2 = file.read()

    with open('test.md', 'w', encoding='utf-8') as file:
        file.write(content2)
```
| [查看原文](https://arxiv.org/pdf/2411.07396)                                                                                  | 转换后的 markdown                                                                                                             |
| ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| ![](使用PyMuPDF4LLM解析PDF的图片和表格/ef61dfb4.png) | ![](使用PyMuPDF4LLM解析PDF的图片和表格/b9fdcaa9.png) |



### 本地PDF文件转换
接下来介绍一下本地PDF文件的转换效果，在找一篇论文下载到本地，示例代码如下：

```python
# 使用示例
if __name__ == "__main__":
    # 创建临时文件夹，代码运行结束会自动删除临时文件和其中的所有内容
    temp_dir2 = TemporaryDirectory()
    file_path2 = "/Users/xiniao/Downloads/2411.07264v1.pdf"
    md_file_path2 = pdf_to_markdown(file_path2, temp_dir2)
    with open(md_file_path2, 'r', encoding='utf-8') as file:
        content2 = file.read()

    with open('test.md', 'w', encoding='utf-8') as file:
        file.write(content2)
```

| [查看原文](https://arxiv.org/pdf/2411.07264) | 查看转换后的 markdown文件 |
| --------------------------------------------------------------------------------------------------- | ------------------------- |
|      ![](使用PyMuPDF4LLM解析PDF的图片和表格/511f97f6.png)                                                                                               |           ![](使用PyMuPDF4LLM解析PDF的图片和表格/76651d12.png)                |



## 集成langchain
可以使用下面的代码集成pymupdf4llm到langchain中：

```python
import os
import re
from typing import Optional, Dict, Any, List

import oss2
import pymupdf4llm
from langchain_community.document_loaders.pdf import BasePDFLoader
from langchain_core.documents import Document
from langchain_core.documents.base import Blob
from langchain_text_splitters import MarkdownTextSplitter


class PyMuPDF4llmLoader(BasePDFLoader):
    """Load `PDF` files using `PyMuPDF`."""

    def __init__(
            self,
            file_path: str,
            *,
            headers: Optional[Dict] = None,
            extract_images: bool = False,
            upload_images: bool = False,
            bucket: oss2.Bucket = None,
            oss_url_expires: int = 60 * 60 * 24,
            **kwargs: Any,
    ) -> None:

        try:
            import pymupdf4llm  # noqa:F401
        except ImportError:
            raise ImportError(
                "pymupdf4llm package not found, please install it with "
                "`pip install pymupdf4llm`"
            )

        """Initialize with a file path."""
        super().__init__(file_path, headers=headers)
        self.extract_images = extract_images
        if upload_images and bucket is None:
            raise ValueError("upload_images is True but bucket is None")
        if upload_images and oss_url_expires <= 0:
            raise ValueError("oss_url_expires must be greater than 0")
        self.upload_images = upload_images
        self.bucket = bucket
        self.oss_url_expires = oss_url_expires
        self.kwargs = kwargs

    def load(self) -> List[Document]:

        if self.web_path:
            blob = Blob.from_data(open(self.file_path, "rb").read(), path=self.web_path)  # type: ignore[attr-defined]
        else:
            blob = Blob.from_path(self.file_path)  # type: ignore[attr-defined]
        return self.parse(blob)

    def parse(self, blob: Blob) -> List[Document]:
        """Parse a PDF file into a list of documents.

        If `blob` is a directory, this will load all PDF files within it.
        """
        image_path = os.path.join(os.path.dirname(self.file_path), f"images")

        # 读取PDF文件
        pages = pymupdf4llm.to_markdown(doc=self.file_path,
                                        write_images=self.extract_images,
                                        image_path=image_path,
                                        page_chunks=True,
                                        **self.kwargs
                                        )
        if isinstance(pages, list):
            # 创建Document对象
            docs = []
            for i, page in enumerate(pages):
                metadata = {
                    "file_path": blob.path,
                    "page": page.get('metadata').get('page'),
                    "total_pages": page.get('metadata').get('page_count'),
                }
                page_content = page.get("text")
                if self.upload_images:
                    page_content = self._replace_local_images_with_oss_url(page_content)

                doc = Document(page_content=page_content, metadata=metadata)
                docs.append(doc)

            return docs

    def _replace_local_images_with_oss_url(self, content: str):
        """
        替换Markdown文件中的本地图片路径为OSS URL
        """
        # 匹配Markdown文件中的图片路径
        pattern = r'!\[(.*?)\]\((.*?)\)'
        matches = re.findall(pattern, content)
        print(f'匹配到 {len(matches)} 张图片')

        replace_num = 0
        new_content = content
        # 上传并替换图片
        for alt_text, image_path in matches:
            old_image_path = f"![{alt_text}]({image_path})"

            image_oss_url = self._upload_to_oss(image_path, self.bucket)

            # 替换图片路径
            if image_oss_url:
                new_image_path = f"![{alt_text}]({image_oss_url})"

                new_content = new_content.replace(old_image_path, new_image_path)
                replace_num += 1
                print(f"Replacing {old_image_path} with {new_image_path}")

        print(f"替换完成，共替换 {replace_num} 张图片")
        return new_content

    def _upload_to_oss(self, file_path: str, bucket: oss2.Bucket):
        """
        上传文件到OSS并返回URL
        :param file_path: 文件路径
        :param bucket: OSS Bucket对象
        :return: 预览URL
        """
        # 判断文件是否存在
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return None

        # 解析文件名和扩展名
        filename, ext = os.path.splitext(os.path.basename(file_path))
        # 构造OSS文件名，确保不重复
        oss_filename = f"{filename}{ext}"
        # 上传文件到OSS
        with open(file_path, 'rb') as data:
            result = bucket.put_object(oss_filename, data)
            if result.status == 200:
                print(f"File {file_path} uploaded successfully to OSS as {oss_filename}")
                preview_url = bucket.sign_url('GET', oss_filename, self.oss_url_expires)
                return preview_url
        return file_path


if __name__ == '__main__':
    file_path = "https://arxiv.org/pdf/2411.07264"
    from pdf_test import get_bucket
    loader = PyMuPDF4llmLoader(file_path=file_path, extract_images=True, upload_images=True, bucket=get_bucket())
    splitter = MarkdownTextSplitter(chunk_size=400, chunk_overlap=0, add_start_index=True)

    docs = loader.load_and_split(text_splitter=splitter)
    print(len(docs))
    for doc in docs:
        print(doc)

```



## 结论
从前面的演示中可以看到 pymupdf4llm 能够提取图片的信息，但是提取的图片的位置与原文不一致，对于大部分场景任然是有效的，因为它的转换效率较高（不需要GPU）。如果使用OCR或者多模态大模型提取PDF文件中的图片和文字准确率会高很多，但是存在成本较高和效率低的问题。



参考文档

1. [https://readmedium.com/why-pymupdf4llm-is-the-best-tool-for-extracting-data-from-pdfs-even-if-you-didnt-know-you-needed-7bff75313691](https://readmedium.com/why-pymupdf4llm-is-the-best-tool-for-extracting-data-from-pdfs-even-if-you-didnt-know-you-needed-7bff75313691)
3. [https://pymupdf.readthedocs.io/en/latest/pymupdf4llm](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/#)
4. [https://github.com/pymupdf/RAG/tree/main/pymupdf4llm](https://github.com/pymupdf/RAG/tree/main/pymupdf4llm)



