# 使用Nanonets-OCR-s模型实现PDF文件转markdown

最近看到在 huggingface 看到一个模型 [Nanonets-OCR-s](https://huggingface.co/nanonets/Nanonets-OCR-s)，从它的介绍中了解到，这个模型是一个先进的图像转 Markdown OCR 模型，其功能远超传统的文本提取。为了验证该模型的效果，打算使用该模型实现了一个 PDF 文件转 Markdown 的功能，本文主要将验证的过程记录下来。通过本文的内容你将了解如下内容

- Nanonets-OCR-s模型基本介绍
- 如何下载Nanonets-OCR-s模型
- 如何使用vllm启动Nanonets-OCR-s模型
- 如何实现PDF文件转Markdown的功能

在继续本文的内容之前，首先看一下使用该模型将 PDF 文件转换为 Markdown 文件的效果。
这里使用 [Attention Is All You Need](https://arxiv.org/pdf/1706.03762) 论文的PDF文件进行测试，转换为markdown文件，效果如下：


| 特性     | 转换效果                                                            |
| -------- | ------------------------------------------------------------------- |
| 识别水印 | ![1.jpg](./image/使用Nanonets-OCR-s模型实现PDF文件转markdown/1.jpg) |
| 识别页码 | ![1.jpg](./image/使用Nanonets-OCR-s模型实现PDF文件转markdown/2.jpg) |
| 识别公式 | ![1.jpg](./image/使用Nanonets-OCR-s模型实现PDF文件转markdown/3.jpg) |
| 识别表格 | ![1.jpg](./image/使用Nanonets-OCR-s模型实现PDF文件转markdown/4.jpg) |
| 识别表格 | ![1.jpg](./image/使用Nanonets-OCR-s模型实现PDF文件转markdown/5.jpg) |
| 识别图片内容 | ![1.jpg](./image/使用Nanonets-OCR-s模型实现PDF文件转markdown/6.jpg) |

从前面的效果可以看到， Nanonets-OCR-s 模型能够识别出 PDF 文件中的水印、公式、表格、图片内容等信息，并且将这些信息转换为 Markdown 格式。但是在识别复杂表格时，有部分表格的内容位置识别错误。

## Nanonets-OCR-s模型介绍

### 产品核心
**Nanonets-OCR-s**——图像转Markdown OCR模型，突破传统文本提取局限，具备**语义理解和结构化输出能力**。

### 传统OCR痛点
- 仅提取纯文本，忽略水印/签名/页码等元素
- 无法处理图像、表格、公式等复杂结构
- 输出缺乏上下文，难以直接用于下游任务

### 核心突破
**语义化标记输出**：理解文档结构与上下文（表格/公式/图像/水印/复选框等），生成可直接被大模型处理的Markdown。


### 六大核心能力
1. **LaTeX公式识别**  
   - 数学公式自动转LaTeX语法（行内/独立公式）
2. **智能图像描述**  
   - 用`<img>`标签描述图像内容/风格/上下文（支持图表/二维码等）
3. **签名检测隔离**  
   - 通过`<signature>`标签分离签名（关键法律/商业用途）
4. **水印提取**  
   - 用`<watermark>`标签提取水印文本
5. **复选框处理**  
   - 将复选框转为Unicode符号（`<checkbox>`标签标记状态）
6. **复杂表格提取**  
   - 表格转Markdown/HTML格式（保留结构）

### 技术细节
- **训练数据**：25万+页文档（研究论文/财务/法律/医疗/税务表单等）
- **数据组成**：合成数据预训练 + 人工标注数据微调
- **基础模型**：基于**Qwen2.5-VL-3B**视觉语言模型优化

### 局限性
- ❌ 不支持手写文本识别
- ⚠️ 可能产生内容幻觉（hallucination）


### 应用场景
| 领域       | 价值                    |
| ---------- | ----------------------- |
| 学术研究   | 论文公式/表格数字化     |
| 法律金融   | 合同签名/财务表格提取   |
| 医疗制药   | 医疗表单复选框/文本识别 |
| 企业级应用 | 报告转可搜索的知识库    |

### 产品定位
**解决LLM时代的核心瓶颈**：将非结构化文档转化为富含上下文的清洁Markdown数据，打通AI自动化关键链路。

参考文档 [Nanonets OCR Small](https://nanonets.com/research/nanonets-ocr-s/)

## 下载Nanonets-OCR-s模型
使用下面的代码从 modelscope 下载[Nanonets-OCR-s](https://modelscope.cn/models/nanonets/Nanonets-OCR-s)模型：

在下载前，请先通过如下命令安装ModelScope
```shell
pip install modelscope
```
使用下面的python代码下载模型到指定的目录中：
```python
    #模型下载
    from modelscope import snapshot_download
    model_dir = snapshot_download('nanonets/Nanonets-OCR-s', local_dir='./model')
    print(model_dir)
```

## 安装相关依赖

使用下面的命令安装相关依赖：
```bash
pip install PyMuPDF vllm litellm
```
依赖说明：
- `PyMuPDF`：用于将 PDF 文件转换为图片
- `vllm`：用于启动模型，提供 OpenAI 的 Completions API兼容的 HTTP 服务接口
- `litellm`：用于调用模型


## 使用vllm启动模型 
使用下面的命令启动模型
```bash
vllm serve ./Nanonets-OCR-s/ --served-model-name openai/Nanonets-OCR-s --chat-template ./template_dse_qwen2_vl.jinja
```
参数说明：
- `--served-model-name`：指定模型名称，用于后续调用
- `--chat-template`：指定chat模板文件路径，vLLM 社区为热门模型提供了一套聊天模板，可以在[example目录](https://github.com/vllm-project/vllm/tree/main/examples)下找到它们。

vLLM 提供了一个 HTTP 服务器，实现了 OpenAI 的 Completions API、Chat API 等，此功能允许使用 HTTP 客户端提供模型并与模型交互。


## 代码实现

下面的代码实现了将 PDF 文件转换为 Markdown 文件的功能。

```python
# -*- encoding: utf-8 -*-
import pymupdf  # PyMuPDF
import os
from PIL import Image

import litellm
import base64


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_image_encoding_type(image_path: str) -> str:
    if image_path.endswith(".png"):
        return "data:image/png;base64"
    elif image_path.endswith(".jpg") or image_path.endswith(".jpeg"):
        return "data:image/jpeg;base64"
    else:
        raise ValueError(f"Unsupported image format: {image_path}")


def covert_image_to_markdown(image_path):
    print(f'开始处理图片: {image_path}')
    img_base64 = encode_image(image_path)
    image_encoding_type = get_image_encoding_type(image_path)
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"{image_encoding_type},{img_base64}"},
                },
                {
                    "type": "text",
                    "text": "Extract the text from the above document as if you were reading it naturally. Return the tables in html format. Return the equations in LaTeX representation. If there is an image in the document and image caption is not present, add a small description of the image inside the <img></img> tag; otherwise, add the image caption inside <img></img>. Watermarks should be wrapped in brackets. Ex: <watermark>OFFICIAL COPY</watermark>. Page numbers should be wrapped in brackets. Ex: <page_number>14</page_number> or <page_number>9/22</page_number>. Prefer using ☐ and ☑ for check boxes.",
                },
            ],
        }
    ]
    # hosted_vllm is prefix key word and necessary
    response = litellm.completion(
        model="hosted_vllm/openai/Nanonets-OCR-s", # pass the vllm model name
        messages=messages,
        api_base="http://localhost:8000/v1",
        temperature=0.0,
        max_tokens=15000)

    return response["choices"][0]["message"]["content"]

def pdf_to_images(pdf_path, output_folder, image_format='png', zoom=2):
    """
    将PDF每页转换为单独的图片

    参数:
        pdf_path: PDF文件路径
        output_folder: 输出图片的文件夹
        image_format: 图片格式 ('PNG' 或 'JPEG')
        zoom: 缩放因子(提高分辨率)，默认2=2倍
    """
    # 确保输出目录存在
    os.makedirs(output_folder, exist_ok=True)

    # 打开PDF文件
    pdf_document = pymupdf.open(pdf_path)
    page_image_paths = []
    # 遍历每一页
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)

        # 创建缩放矩阵提高分辨率
        matrix = pymupdf.Matrix(zoom, zoom)

        # 渲染页面为图像 (pix对象)
        pix = page.get_pixmap(matrix=matrix)

        # 转换为PIL Image对象以便处理
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        # 构建输出路径
        output_path = os.path.join(output_folder, f"page_{page_num+1}.{image_format.lower()}")

        # 保存图像
        img.save(output_path, format=image_format)
        page_image_paths.append(output_path)
        print(f"已保存: {output_path}")


    print(f"\n转换完成! 共转换 {len(pdf_document)} 页。")
    pdf_document.close()
    return page_image_paths



# 使用示例
if __name__ == "__main__":
    import time
    from pathlib import Path
    # 配置参数
    pdf_file = "Attention-Is-All-You-Need.pdf"  # 替换为你的PDF文件路径
    output_dir = "output_images"  # 输出文件夹

    file_name = Path(pdf_file).stem
    # 调用转换函数
    page_image_paths = pdf_to_images(pdf_path=pdf_file, output_folder=output_dir)
    # page_image_paths = ['output_images2/page_9.png']
    print(page_image_paths)
    markdown_contents = []
    for page_image_path in page_image_paths:
        md_content = covert_image_to_markdown(page_image_path)
        print(md_content)
        time.sleep(5)
        markdown_contents.append(md_content)
    # 将markdown内容写入文件
    output_path = f'{file_name}.md'
    with open(output_path, "w") as f:
        f.write("\n\n".join(markdown_contents))

    print(f"Markdown内容已保存到{output_path}")

```

## 问题记录
### 使用 vllm 启动模型失败

#### 1. CUDA 版本不匹配

**启动命令**

```shell
vllm serve ./Nanonets-OCR-s
```
**报错信息**

```shell
RuntimeError: CUDA error: no kernel image is available for execution on the device
```

**原因分析**

我们遇到了一个CUDA错误：`no kernel image is available for execution on the device`。这个错误通常表示当前设备（GPU）没有可用的内核镜像。这可能是由于以下几种原因：
1. **CUDA架构不匹配**：你编译的PyTorch（或其他框架）版本不支持你的GPU架构。例如，你的GPU是较新的架构（如Ampere，计算能力8.0以上），但安装的PyTorch版本是在该架构发布之前编译的，因此不包含针对该架构的内核。
2. **安装的PyTorch版本不支持GPU**：你可能安装了CPU版本的PyTorch。
3. **CUDA工具包版本不匹配**：你的CUDA工具包版本与PyTorch编译时使用的版本不匹配。
4. **驱动程序过旧**：GPU驱动程序版本太旧，不支持当前CUDA版本。

**解决步骤**
1. 确认GPU型号和计算能力
首先，确定你的GPU型号和计算能力（Compute Capability）。可以通过以下命令查看（需要安装NVIDIA驱动）：
```bash
nvidia-smi
```
然后，根据型号查找计算能力（例如，RTX 30系列通常是Ampere架构，计算能力8.0+）。

2. 确认PyTorch安装版本
在Python中运行：
```python
import torch
print(torch.__version__)
print(torch.version.cuda)  # 查看PyTorch编译时使用的CUDA版本
print(torch.cuda.is_available())  # 检查CUDA是否可用
print(torch.cuda.get_device_name(0))  # 获取GPU设备名称
print(torch.cuda.get_device_capability(0))  # 获取计算能力，如(8,0)
```

3. 检查PyTorch是否支持你的GPU架构
访问[PyTorch官方网站](https://pytorch.org/get-started/previous-versions/)，查看你安装的PyTorch版本所支持的CUDA版本以及对应的架构。


根据上述信息，采取以下措施：
- **情况1：PyTorch不支持你的GPU架构**
  例如，你的GPU计算能力是8.0（Ampere架构），而安装的PyTorch版本（如1.7.0）是在Ampere发布之前编译的，因此没有包含针对sm_80的内核。
  **解决方法**：安装支持你GPU架构的PyTorch版本。通常，PyTorch 1.8.0及以上版本支持Ampere架构（sm_80及以上）。建议安装最新版本的PyTorch。

  先安装 vllm 较新版本
  ```bash
  pip install vllm -U
  ```
  因为 vllm 依赖的 torch 版本需要较高，使用pip安装你的GPU架构对应的PyTorch（根据官网命令，例如）：
  ```bash
  pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```
  > 注意：这里使用CUDA 11.8，请根据你的环境选择合适的CUDA版本。
- **情况2：安装了CPU版本的PyTorch**
  如果`torch.cuda.is_available()`返回False，并且你确定有GPU，那么可能是安装了CPU版本。
  **解决方法**：卸载当前PyTorch，并安装支持GPU的版本。
- **情况3：CUDA工具包版本与驱动不匹配**
  运行`nvidia-smi`查看驱动支持的CUDA版本（右上角显示的是驱动支持的最高CUDA版本）。然后确保安装的PyTorch所依赖的CUDA工具包版本不超过这个版本。例如，如果你的驱动支持最高CUDA 11.7，那么你应该安装CUDA 11.7及以下版本的PyTorch。
- **情况4：更新NVIDIA驱动**
  如果驱动太旧，可能需要更新驱动。访问NVIDIA官网下载并安装最新驱动。

**总结**
最常见的解决方法是安装与你的GPU架构兼容的PyTorch版本。确保安装的PyTorch版本支持你的GPU计算能力，并且CUDA工具包版本与驱动兼容。
如果你已经安装了最新版本的PyTorch但仍然遇到此问题，请检查PyTorch是否是从官方渠道下载的预编译版本（通常支持较广泛的架构），或者尝试使用不同CUDA版本的PyTorch（如从CUDA11.1切换到CUDA11.3等）。
希望这些步骤能帮助你解决问题！

#### 2. transformers版本不支持

**报错信息如下**
```shell
ValueError: Model architectures ['Qwen2_5_VLForConditionalGeneration'] are not supported for now
```
**解决方法**
升级transformers版本
```shell
pip install transformers==4.50.2
```
参考解决文档：https://github.com/vllm-project/vllm/issues/12502

#### 3. 没有chat template
**报错信息如下**
```shell
BadRequestError: Error code: 400 - {'object': 'error', 'message': 'As of transformers v4.44, default chat template is no longer allowed, so you must provide a chat template if the tokenizer does not define one. None', 'type': 'BadRequestError', 'param': None, 'code': 400}
```

**解决方法**
使用 vllm 启动模型时通过 `--chat-template` 参数指定聊天模版
```shell
vllm serve <model> --chat-template ./path-to-chat-template.jinja
```
vLLM 社区为热门模型提供了一套聊天模板，可以在[example目录](https://github.com/vllm-project/vllm/tree/main/examples)下找到它们。


参考解决文档：
1. https://github.com/vllm-project/vllm/issues/17977
2. https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#chat-template_1


#### 4. pandas 版本不兼容
**报错信息如下**
```shell
  File "/opt/conda/lib/python3.10/site-packages/pandas/util/_decorators.py", line 14, in <module>
    from pandas._libs.properties import cache_readonly
  File "/opt/conda/lib/python3.10/site-packages/pandas/_libs/__init__.py", line 13, in <module>
    from pandas._libs.interval import Interval
  File "pandas/_libs/interval.pyx", line 1, in init pandas._libs.interval
ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```
**解决方法**
升级 pandas 版本
```shell
pip install pandas -U 
```




## 参考文档
1. [Nanonets OCR 模型介绍](https://nanonets.com/research/nanonets-ocr-s/)
2. [从modelscope下载模型](https://modelscope.cn/models/nanonets/Nanonets-OCR-s)
3. [使用 vllm 提供openai兼容的接口](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html)
4. [使用docext实现pdf转markdown](https://github.com/NanoNets/docext/blob/main/PDF2MD_README.md)
5. [安装pytorch版本参考](https://pytorch.org/get-started/previous-versions/)
