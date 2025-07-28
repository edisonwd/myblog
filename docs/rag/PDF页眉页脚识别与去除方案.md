# PDF页眉页脚识别与去除方案

最近在优化RAG应用，发现在转换PDF文件为 markdown 格式时发现有很多页眉页脚被包含在了正文中，为了避免页眉页脚的影响，查阅了相关资料，实现了一个PDF文档页眉页脚识别与去除的方案，在这里分享一下。

> 关于如何使用多模态模型[Nanonets-OCR-s](https://modelscope.cn/models/nanonets/Nanonets-OCR-s)将PDF文件转化为 markdown 格式文件，将在下一篇文章中进行介绍，请继续关注。

**接下来将使用PyMuPDF（fitz）库实现，因为它可以处理文本和图像，并且可以编辑PDF。**

本文从如下几个方面进行介绍：
- PyMuPDF旧版本使用fitz原因分析
- 理解PyMuPDF中bbox坐标系
- 使用PyMuPD编辑PDF文件内容
- PDF文件页眉和页脚识别
- PDF文件页眉和页脚去除


## PyMuPDF旧版本使用fitz原因分析
PyMuPDF是一个用于处理PDF文件的Python库，它实际上是基于MuPDF的封装。在旧版本中，导入这个库时使用的名称是`fitz`，也就是通过`import fitz`，而不是`import pymupdf`。这可能会让我们感到困惑，因为通常我们期望导入的模块名与安装的包名一致。

**原因如下：**
1. **历史原因**：PyMuPDF最初是作为MuPDF的Python绑定而开发的。MuPDF是一个轻量级的PDF、XPS和电子书查看器，由Artifex Software开发和维护。MuPDF的核心渲染库叫做Fitz，这个名称来源于Marcel Duchamp的虚构人物“Fitz”，也是MuPDF项目最初代码库的代号。
2. **保持向后兼容性**：尽管现在官方推荐使用`pymupdf`作为包名（通过`pip install pymupdf`安装），但为了保持旧代码的兼容性，导入名称仍然保留为`fitz`。这样，那些使用旧版本编写的代码无需修改导入语句。
3. **避免冲突**：使用不同的导入名也可以避免与其他可能的同名包冲突。

示例代码：
```python
import fitz  # 这就是PyMuPDF
doc = fitz.open("example.pdf")
for page in doc:
    text = page.get_text()
    print(text)
```
因此，即使安装了`pymupdf`，仍然可以使用`import fitz`来导入它。这是该库的一个特点。
> 注意：在极少数情况下，如果你同时安装了另一个名为`fitz`的包，可能会引起冲突。但在大多数情况下，`fitz`这个名称是专为PyMuPDF保留的。


**为什么推荐使用 `import pymupdf` 而不是 `import fitz`？**

1. **一致性**：在最新版本的 PyMuPDF 中，官方已经建议使用 `import pymupdf` 来提高代码的可读性和一致性。

2. **向后兼容性**：虽然 `import fitz` 在很多地方仍然能工作，但随着库的更新，未来版本的 PyMuPDF 很可能会更强调 `import pymupdf`，这也有助于避免未来出现弃用 `fitz` 的情况。

3. **代码清晰**：直接使用 `PyMuPDF` 作为库的导入，可以帮助其他开发者更容易理解代码，因为 `PyMuPDF` 更具描述性，表明这是一个用于操作 PDF 文档的库。


**总结**：PyMuPDF使用`fitz`作为导入名，主要是由于历史原因（底层引擎名称）和保持向后兼容性。如果你在写新代码或更新现有代码，**建议使用**：

```python
import pymupdf
```

这样会让你的代码更具兼容性和可读性，同时避免未来版本更新时出现问题。

## 理解PyMuPDF中bbox坐标系

在PDF中，**Bounding Box（bbox）** 表示一个矩形区域，用于定义页面元素（如文本、图像或注释）的位置和范围，理解bbox的坐标系对于处理PDF内容至关重要。
实际上，PyMuPDF（基于MuPDF）使用了一个统一的坐标系，其**原点在页面的左上角，Y轴向下为正方向**。这与PDF的原生坐标系（左下角原点，Y轴向上）不同，但与图像坐标系一致。以下是详细分析：
### 1. **MuPDF的通用坐标系**
MuPDF作为一个多格式文档库，为所有支持的文档类型（包括PDF、图像等）定义了一个**统一的坐标系**：
- **原点 `(0, 0)`**：位于页面的**左上角**。
- **Y轴方向**：**向下**为正（与图像坐标系相同）。
- **单位**：使用**点（Point）**（1/72英寸）作为基本单位（对于PDF），对于图像则使用像素。

> 1点(point) = 1/72英寸 ≈ 0.3528毫米


MuPDF的统一坐标系使得处理不同格式时无需切换坐标系逻辑，有如下优势：

1. **格式一致性**：用相同逻辑处理PDF/XPS/ePub/CBZ等10+格式

2. **图像兼容**：图像作为"单页文档"自然适配系统

3. **渲染优化**：避免重复坐标转换，提升性能

4. **开发者友好**：只需学习一套坐标规则

### 2. **PDF原生坐标系 vs. MuPDF坐标系**
- **PDF原生坐标系**（存储格式）：
  - 原点：左下角
  - Y轴：向上为正
  - 矩形边界框表示为 `[x0, y0, x1, y1]`
    - **(x0, y0)** = 左下角坐标
    - **(x1, y1)** = 右上角坐标

PDF原生坐标系可视化理解
```text
Y轴 ↑ (向上增加)
   ↑
   |   (x0,y1) +-----------------+ (x1,y1)
   |           |                 |
   |           |      PDF页面    |
   |           |                 |
   |   (x0,y0) +-----------------+ (x1,y0)
   +------------------------------------→ X轴 (向右增加)
 (0,0) - 左下角原点
```

- **MuPDF内部坐标系**（处理时）：
  - 原点：左上角
  - Y轴：向下为正
  - 矩形边界框表示为 `[x0, y0, x1, y1]`
    - **(x0, y0)** = 左上角坐标
    - **(x1, y1)** = 右下角坐标

MuPDF/PyMuPDF坐标系可视化理解
```text
 (0,0) - 左上角原点
   +------------------------------------→ X轴 (向右增加)
   |   (x0,y0) +-----------------+ (x1,y0)
   |           |                 |
   |           |     文档页面    |
   |           |                 |
   |   (x0,y1) +-----------------+ (x1,y1)
   ↓
Y轴 ↓ (向下增加)
```
**与PDF原生坐标系和图像坐标系的比较**

| **特性**         | **PDF原生坐标系** | **PyMuPDF (MuPDF) 坐标系** | **图像坐标系**    |
| ---------------- | ----------------- | -------------------------- | ----------------- |
| **原点**         | 左下角            | 页面左上角                 | 图像左上角        |
| **Y轴方向**      | 向上 ↑ 为正       | 向下 ↓为正                 | 向下 ↓为正        |
| **单位**         | 点 (Point)        | 点（PDF）或像素（图像）    | 像素              |
| **典型使用场景** | PDF文件存储       | PDF文本/图形提取           | 屏幕显示/图像处理 |


**关键结论**：PyMuPDF返回的坐标与图像坐标系在方向上完全一致（原点左上角，Y向下），但单位可能不同（PDF用点，图像用像素）。


当MuPDF加载PDF页面时，它会**自动进行坐标系转换**：
  1. 将原点从左下角平移到左上角。
  2. 反转Y轴方向（乘以变换矩阵 `[1, 0, 0, -1, 0, page_height]`）。

这样，在MuPDF中处理的PDF页面坐标就与图像坐标系对齐了。

### 3. **PyMuPDF的坐标系使用**
PyMuPDF作为MuPDF的Python绑定，直接暴露了MuPDF的坐标系：
- **所有返回的坐标**（如`page.get_text("dict")`中的`bbox`、`page.search_for()`的结果）都使用**左上角原点，Y轴向下**。
- **渲染图像**（`page.get_pixmap()`）时，输出的像素图也使用相同的坐标系（无需额外转换）。

**示例代码验证：**
```python
import pymupdf
doc = pymupdf.open("example.pdf")
page = doc[0]
# 获取页面尺寸（单位为点）
page_rect = page.rect
print("Page rectangle (top-left origin):", page_rect)  # 格式: (x0, y0, x1, y1), 其中y0=0, y1=页面高度
# 获取第一个文本块的bbox
text_blocks = page.get_text("blocks")
if text_blocks:
    block = text_blocks[0]
    print("Text block bbox (top-left based):", block)
    # 此时block的y0是距离页面顶部的距离，y1是向下延伸的距离
```

### 4. **常见误区澄清**
- **误区1**：PyMuPDF返回PDF原生坐标。  
  **纠正**：PyMuPDF返回的是转换后的坐标（左上角原点，Y向下），与MuPDF一致。
  
- **误区2**：渲染图像需要手动翻转Y轴。  
  **纠正**：`page.get_pixmap()`输出的图像坐标系与PyMuPDF内部坐标系一致，无需额外翻转。
### 5. **总结**
- **PyMuPDF坐标系**：统一使用**左上角原点，Y轴向下**（与图像坐标系方向相同）。
- **与PDF原生坐标关系**：加载时自动转换（Y轴翻转 + 原点平移）。
- **实践建议**：
  - 处理PyMuPDF坐标时，直接按左上角参考即可。
  - 仅在与其他工具交互（要求PDF原生坐标）时才需要转换。
  - 渲染图像时，使用`pymupdf.Matrix`处理缩放，坐标系已对齐。

## 使用PyMuPD编辑PDF文件内容
### add_redact_annot 方法的使用
在PyMuPDF中，`add_redact_annot`方法用于在PDF页面上创建“涂红”（redaction）注释。涂红注释通常用于标记需要删除或隐藏的内容。但是，仅仅添加涂红注释并不会立即删除内容，还需要调用`apply_redactions`方法来实际执行删除操作。涂红操作会永久删除指定区域内的内容（文本和图像），并用指定的颜色（默认是白色）填充该区域。
通过结合 add_redact_annot 的精准区域标记和 apply_redactions 的灵活删除策略，可高效实现 PDF 内容的安全擦除与替换。

下面是关于`add_redact_annot`方法的详细说明和使用步骤：
**方法签名**

```python
add_redact_annot(quad, text=None, fontname=None, fontsize=11, align=TEXT_ALIGN_LEFT, fill=(1, 1, 1), text_color=(0, 0, 0), cross_out=True)
```
**参数说明**
- **quad**: 指定要删除的矩形区域。可以是矩形（rect_like，由左上角和右下角坐标定义）或四边形（quad_like，由四个点定义）。如果是四边形，将取其外接矩形。
- **text**: (可选) 在应用红批注后，在矩形区域中放置的新文本。如果不提供，则区域将被填充颜色（默认白色）而没有文本。
- **fontname**: 用于新文本的字体。只支持CJK和PDF基础14种字体（如"Helvetica", "Times-Roman"等）。如果不提供，将使用默认字体（通常是Helvetica）。
- **fontsize**: 新文本的字体大小。默认11。如果文本太长，会尝试缩小字体（最小到4）以适应。如果仍然放不下，则不会添加文本。
- **align**: 文本的水平对齐方式（例如TEXT_ALIGN_LEFT, TEXT_ALIGN_CENTER, TEXT_ALIGN_RIGHT等）。垂直方向大致居中。
- **fill**: 应用红批注后矩形的填充颜色。默认是白色(1,1,1)。如果指定为False，则没有填充（透明）。
- **text_color**: 新文本的颜色，默认黑色(0,0,0)。
- **cross_out**: 是否在红批注矩形上画两条对角线（默认为True，即画对角线）。


### apply_redactions方法的使用
在添加完所有红批注后，调用apply_redactions方法来实际执行删除操作。
**方法签名**

```python
apply_redactions(images=PDF_REDACT_IMAGE_PIXELS | 2, graphics=PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED | 2, text=PDF_REDACT_TEXT_REMOVE | 0)
```
参数说明：
- **images**: 控制如何处理与红批注重叠的图像。默认值2（PDF_REDACT_IMAGE_PIXELS）表示将重叠的像素变为空白（即用白色覆盖）。其他选项：0（忽略图像），1（完全删除重叠的图像），3（仅删除可见的图像）。
- **graphics**: 控制如何处理与红批注重叠的矢量图形。默认值2（PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED）表示删除任何有重叠的矢量图形。其他选项：0（忽略），1（仅删除完全包含在红批注内的矢量图形）。
- **text**: 控制如何处理重叠的文本。默认值0（PDF_REDACT_TEXT_REMOVE）表示删除所有边界框与红批注矩形重叠的字符。设置为1（PDF_REDACT_TEXT_NONE）则保留文本（但这样不符合数据保护目的，慎用）。

> 注意：apply_redactions返回一个布尔值，表示是否处理了至少一个红批注。

### 示例代码
以下示例演示如何删除一页中的页眉和页脚，**步骤如下：**
1. 打开PDF文档，选择要处理的页面。
2. 定义涂红区域（一个或多个矩形）。
3. 为每个区域调用`add_redact_annot`方法添加涂红注释。
4. 调用页面的`apply_redactions()`方法应用涂红操作。此操作会删除区域内的内容，并用指定颜色填充（如果没有指定文本，则只填充颜色；如果指定了文本，则还会在区域中绘制文本）。
5. 保存文档。

```python
import fitz  # PyMuPDF
# 打开PDF文档
doc = fitz.open("input.pdf")
page = doc[0]  # 第一页
# 假设页眉在页面顶部50个点的高度，页脚在页面底部50个点的高度
page_rect = page.rect
header_rect = fitz.Rect(0, 0, page_rect.width, 50)   # 页眉区域
footer_rect = fitz.Rect(0, page_rect.height - 50, page_rect.width, page_rect.height)  # 页脚区域
# 添加涂红注释（不显示覆盖文本，仅用白色填充）
page.add_redact_annot(header_rect)
page.add_redact_annot(footer_rect)
# 应用涂红操作
page.apply_redactions()
# 保存文档
doc.save("output.pdf")
doc.close()
```
### 注意事项
1. **区域重叠**：如果涂红区域有重叠，`apply_redactions`方法会合并重叠的区域。
2. **内容删除**：涂红操作会永久删除区域内的所有内容（包括文本和图像），所以在操作前最好备份原文档。
3. **文本覆盖**：如果需要在涂红区域上显示替代文本（例如"[REDACTED]"），可以设置`text`参数。
4. **颜色设置**：默认填充颜色是白色，但可以通过`fill`参数更改。例如，用红色填充并显示白色文字：
   ```python
   page.add_redact_annot(rect, text="REDACTED", fill=(1, 0, 0), text_color=(1,1,1))
   ```
5. **性能**：对每一页的涂红操作都是独立的。如果文档有多页，需要逐页处理。


## PDF文件页眉和页脚识别

### 页眉和页脚自动检测思路分析
自动识别页眉和页脚的位置是一个挑战。我们可以假设：
   - 页眉通常位于每一页的顶部（比如从上到下0到50像素的区域），页脚位于底部（比如从页面高度-50到页面高度）。
   - 但是，不同的PDF页眉页脚位置可能不同，所以我们可能需要用户指定区域，或者通过分析多个页面来动态确定。
 为了简化，我们可以设计如下：
  方案1：用户提供页眉和页脚的区域坐标（相对于每一页）。
  方案2：自动检测：通过分析第一页（或几页）的顶部和底部区域，提取重复出现的文本（或对象）来识别页眉页脚。但注意，页眉页脚可能包含页码，页码是变化的。

自动检测思路：
   - 提取每一页的顶部区域（比如前10%高度）和底部区域（后10%高度）的文本和图像。
   - 对于文本，我们可以比较不同页面的这些区域，找出重复出现的文本（忽略页码等变化部分）。
   - 我们可以通过计算多个页面顶部和底部区域的相似性，确定一个固定的区域（即每页都有的部分）。我们假设页眉页脚在每一页的位置和大小是固定的。
  
然而，在实践中，我们可能不需要保留页眉页脚中的变化部分（如页码），而是希望去除整个区域。所以，我们可以让用户指定一个固定的区域（比如从顶部0到50像素，底部从页面高度-50到页面高度），然后覆盖这个区域。

这里，我们提供一个折中的方案：
- 函数1：通过手动指定区域去除页眉页脚。
- 函数2：自动检测页眉页脚区域（通过比较第一页和后续几页的顶部和底部区域，找出共同的元素，然后确定一个边界框）。但是，这种方法可能不准确，特别是当页眉页脚内容变化较大时。

**具体实现**
1. 手动模式：
输入：`pdf_path, output_path, header_bbox（页眉区域，例如(0,0, page_width, 50)）, footer_bbox（页脚区域，例如(0, page_height-50, page_width, page_height)）`
1. 自动检测模式（尝试基于文本重复性）：
  步骤：
   1. 选择前n页（例如5页）进行分析。
   2. 提取每一页顶部区域（比如0到100点）的文本块（使用`page.get_text("dict")`或`page.get_text("blocks")`）和底部区域（page_height-100到page_height）的文本块。
   3. 找出这些区域中重复出现的文本（忽略数字、日期等可能变化的内容）或者图像（图像可以通过比较图像的哈希值或直接比较像素数据，但比较复杂，这里先只考虑文本）。
   4. 根据这些重复出现的文本块的位置，确定一个共同的边界框（比如取所有页面上该文本块的最小外接矩形）。
   5. 如果找不到重复的文本，则可能需要用户手动指定。

**自动检测模式基本思路：**
我们尝试通过文本块来检测。我们使用`page.get_text("blocks")`，它会返回文本块的列表，每个块是一个元组：`(x0,y0,x1,y1, "text", block_no, block_type)`
   1. 分析前n页，收集每一页顶部区域（比如0到100像素）的所有文本块。
   2. 然后，比较不同页面的这些文本块，如果多个页面在相同位置（比如y坐标相差不超过5像素）有文本块，并且文本内容相同（或者相似），那么认为这是页眉。
   3. 页眉可能包含日期、页码等变化的内容，所以直接比较文本内容可能找不到完全相同的。因此可以通过正则表达式过滤掉包含页码的文本，然后判断文本的重复性。
页脚同理

**确定页眉页脚区域具体方法：**
对于顶部区域，我们记录每一页的顶部文本块的边界（y0,y1）的区间。然后，我们找出在多页中都有文本块重叠的y区间。

我们取每一页顶部区域文本块的最大y1（即该页页眉的底部边界），然后取这些y1的最小值（即所有页中最靠上的页眉底部边界）作为页眉区域的y1。
同样，取每一页底部区域文本块的最小y0（即该页页脚的顶部边界），然后取这些y0的最大值（即所有页中最靠下的页脚顶部边界）作为页脚区域的y0。

为什么这样？
因为页眉应该尽可能靠近顶部，所以每一页的页眉底部边界应该比较小（即离顶部近）。我们取最小的y1（即所有页眉底部边界中最靠上的那个）作为页眉区域的底部，这样就不会包含后面页面的可能更大的页眉区域（可能是标题）。
同样，页脚应该尽可能靠近底部，所以每一页的页脚顶部边界应该比较大（离底部近）。我们取最大的y0（即所有页脚顶部边界中最靠下的那个）作为页脚区域的顶部。

- 对于页眉：
  `header_y1 = min( [该页顶部区域所有文本块的最大y1] for 每一页 )`   # 注意：如果一页有多个文本块，我们取该页顶部区域所有文本块的最大y1（即该页页眉区域的最下沿）
    但是，我们可能希望页眉区域是从0到header_y1（这个header_y1是前面计算的最小值）。这样，页眉区域就覆盖了所有页的页眉内容（因为每一页的页眉底部边界都不会超过这个header_y1？不对，我们取的是所有页中页眉底部边界的最小值，那么有些页的页眉可能超过这个高度？但是，我们要求的是共同区域，所以这样取可能漏掉一些页的页眉内容？）
  另一种思路：我们取每一页顶部区域文本块的最大y1，然后取这些y1的最大值（即最靠下的那个）作为header_y1。这样能覆盖所有页的页眉，但可能会把一些非页眉的内容包括进来（比如某一页顶部有个标题）。
  因此，我们采用以下折中：
  我们要求页眉区域的高度不能超过50像素，所以：
  - `header_y0 = 0`
  - `header_y1 = min( max( [该页顶部区域所有文本块的最大y1] for 每一页 ), 50)`
  这样，如果所有页的页眉底部边界最大值不超过50，我们就用这个最大值；如果超过50，我们就用50。这样避免包含过长的标题。
- 同样，对于页脚：
  - `footer_y0 = max( min( [该页底部区域所有文本块的最小y0] for 每一页 ), page_height-50)`
  - `footer_y1 = page_height`
 
> 注意：自动检测可能不准确，所以最好提供手动模式。
> 
### 代码实现自动检测函数
下面是一个使用 PyMuPDF 实现自动检测页眉页脚区域的方案。该方案基于前面的思路：分析前 n 页的顶部和底部区域，找出重复出现的文本块位置，从而确定页眉页脚区域。

```python

import re
import pymupdf  # PyMuPDF
import numpy as np
from collections import defaultdict


def auto_detect_header_footer_regions(pdf_path,
                                      sample_pages: int = 6,
                                      top_margin: int = 100,
                                      bottom_margin: int = 100,
                                      min_overlap: float = 0.8,
                                      min_occurrence: int = 2,
                                      default_region: int = 80):
    """
    自动检测PDF文档的页眉和页脚区域
    
    参数:
        doc: 打开的PyMuPDF文档对象
        sample_pages: 分析的样本页数
        top_margin: 顶部区域高度(像素)
        bottom_margin: 底部区域高度(像素)
        min_overlap: 位置重叠阈值(0-1)
        min_occurrence: 文本块在多页中出现的最小次数
        default_region: 默认区域高度(像素)
    
    返回:
        header_rect: 页眉区域矩形 (pymupdf.Rect)
        footer_rect: 页脚区域矩形 (pymupdf.Rect)
    """

    doc = pymupdf.open(pdf_path)
    # 存储所有页面的顶部和底部文本块
    top_blocks = defaultdict(list)
    bottom_blocks = defaultdict(list)

    # 存储所有页面的高度
    page_heights = []

    # 分析样本页面
    num_pages = min(sample_pages, len(doc))
    for page_num in range(num_pages):
        page = doc.load_page(page_num)
        page_rect = page.rect
        page_heights.append(page_rect.height)

        # 定义顶部和底部区域
        top_zone = pymupdf.Rect(0, 0, page_rect.width, top_margin)
        bottom_zone = pymupdf.Rect(0, page_rect.height - bottom_margin,
                                   page_rect.width, page_rect.height)

        # 获取页面文本块
        blocks = page.get_text("blocks")

        # 收集顶部区域文本块
        for block in blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            block_rect = pymupdf.Rect(x0, y0, x1, y1)

            # 检查是否在顶部区域
            if block_rect.intersects(top_zone):
                # 规范化位置 (相对位置)
                norm_y = (y0 + y1) / 2 / page_rect.height
                top_blocks[page_num].append((norm_y, text.strip(), block_rect))

        # 收集底部区域文本块
        for block in blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            block_rect = pymupdf.Rect(x0, y0, x1, y1)

            # 检查是否在底部区域
            if block_rect.intersects(bottom_zone):
                # 规范化位置 (相对位置)
                norm_y = (y0 + y1) / 2 / page_rect.height
                bottom_blocks[page_num].append((norm_y, text.strip(), block_rect))

    # 计算平均页面高度
    avg_height = np.mean(page_heights) if page_heights else 0

    # 检测页眉区域
    header_candidates = detect_common_region(top_blocks, min_occurrence, min_overlap)
    header_rect = pymupdf.Rect(0, 0, 0, 0)

    if header_candidates:
        # 设置页眉区域矩形 min( max( [page_top_blocks_max_y1] ), 50 )
        header_y1 = min(max(cand[2] for cand in header_candidates), default_region)
        header_rect = pymupdf.Rect(0, 0, page_rect.width, header_y1)

    # 检测页脚区域
    footer_candidates = detect_common_region(bottom_blocks, min_occurrence, min_overlap)
    footer_rect = pymupdf.Rect(0, 0, 0, 0)

    if footer_candidates:
        # 计算页脚区域的Y范围  max( min( [page_bottom_blocks_min_y0] ), page_height-50 )
        footer_y0 = max(min(cand[1] for cand in footer_candidates), avg_height - default_region)
        # 设置页脚区域矩形
        footer_rect = pymupdf.Rect(0, footer_y0, page_rect.width, page_rect.height)

    return header_rect, footer_rect


def detect_common_region(blocks_dict, min_occurrence: int, min_overlap: float):
    """
    检测多个页面中共同出现的文本块区域
    
    参数:
        blocks_dict: 页面文本块字典 {page_num: [(norm_y, text, rect)]}
        min_occurrence: 在多页中出现的最小次数
        min_overlap: 位置重叠阈值
    
    返回:
        候选区域列表 [(norm_y, min_y, max_y, text)]
    """
    # 按Y位置聚类文本块
    position_clusters = defaultdict(list)

    # 收集所有文本块位置
    for page_blocks in blocks_dict.values():
        for norm_y, text, rect in page_blocks:
            # 跳过空文本
            if not text:
                continue
            position_clusters[round(norm_y, 3)].append((norm_y, text, rect))

    # 合并位置相近的聚类
    merged_clusters = []
    positions = sorted(position_clusters.keys())
    current_cluster = []

    for pos in positions:
        if not current_cluster:
            current_cluster = position_clusters[pos]
            continue

        # 检查位置是否接近
        last_pos = current_cluster[-1][0]
        if abs(pos - last_pos) <= 0.01:  # 约1%页面高度的差异
            current_cluster.extend(position_clusters[pos])
        else:
            merged_clusters.append(current_cluster)
            current_cluster = position_clusters[pos]

    if current_cluster:
        merged_clusters.append(current_cluster)

    # 找出在多页中出现的区域
    candidates = []
    for cluster in merged_clusters:
        # 跳过出现次数不足的区域
        if len(cluster) < min_occurrence:
            continue

        # 计算位置范围
        min_y = min(rect.y0 for _, _, rect in cluster)
        max_y = max(rect.y1 for _, _, rect in cluster)
        texts = [text for _, text, _ in cluster]

        # 计算平均位置
        avg_y = np.mean([y for y, _, _ in cluster])

        # 计算文本相似度
        common_text = find_common_text(texts, min_overlap)
        if common_text:
            candidates.append((avg_y, min_y, max_y, common_text))

    return candidates


def find_common_text(texts, min_overlap=0.8):
    """
    在一组文本中找出共同的部分
    
    参数:
        texts: 文本列表
        min_overlap: 最小重叠比例
    
    返回:
        共同文本或None
    """
    if not texts:
        return None
    # 移除页码
    texts = [extract_and_remove_page_number(text) for text in texts]
    # 如果页码只是数字，移除页码后文本相同，则认为文本重复
    if len(set(texts)) == 1:
        return f'有重复内容: {set(texts)}'

    # 使用最长文本作为参考
    reference = max(texts, key=len)
    common_chars = list(reference)

    # 检查每个位置在所有文本中是否相同
    for text in texts:
        if text == reference:
            continue

        # 逐字符比较
        for i, char in enumerate(common_chars):
            if i >= len(text) or text[i] != char:
                common_chars[i] = None

    # 构建共同文本
    result = []
    current_segment = []

    for char in common_chars:
        if char is not None:
            current_segment.append(char)
        elif current_segment:
            result.append(''.join(current_segment))
            current_segment = []

    if current_segment:
        result.append(''.join(current_segment))

    common_text = ' '.join(result).strip()

    # 检查是否满足最小重叠要求
    if common_text and len(common_text) / len(reference) >= min_overlap:
        return common_text

    return None


def extract_and_remove_page_number(text):
    """
    从文本中识别并分离页码
    """
    # 常见页码模式
    patterns = [
        r'\b(\d{1,4})\b',  # 简单数字: 1, 23, 456
        r'[-–—]\s*(\d+)\s*[-–—]',  # 装饰页码: - 1 -, –2–
        r'Page\s*(\d+)\s*of\s*\d+',  # Page 1 of 10
        r'第\s*(\d+)\s*页',  # 中文: 第1页
        r'\b([ivxlcdm]+)\b',  # 罗马数字: i, ii, iii
        r'(\d+)\s*/\s*\d+'  # 分数形式: 1/10
    ]

    page_number = ""
    cleaned_text = text

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            page_number = match.group(1)
            # 移除匹配到的整个模式（而不仅仅是数字），以清除分隔符
            cleaned_text = cleaned_text.replace(match.group(0), '').strip()
            break  # 找到一个就停止

    return cleaned_text


def visualize_regions(pdf_path, out_path, header_rect, footer_rect):
    """
    可视化页眉和页脚区域

    参数:
        pdf_path: PDF文件路径
        out_path: 输出文件路径
        header_rect: 页眉区域矩形 (pymupdf.Rect)
        footer_rect: 页脚区域矩形 (pymupdf.Rect)
    """
    if out_path is None:
        out_path = pdf_path.replace('.pdf', '_visual.pdf')
    doc = pymupdf.open(pdf_path)
    header_rect = pymupdf.Rect(header_rect)
    footer_rect = pymupdf.Rect(footer_rect)
    for page in doc:
        if header_rect.height:
            page.add_rect_annot(header_rect)
        if footer_rect.height:
            page.add_rect_annot(footer_rect)

    doc.save(out_path)
    print(f"Visualization saved to {out_path}")
    doc.close()


# 使用示例
if __name__ == "__main__":
    pdf_file = "/Users/xiniao/Downloads/FATF-ME-FATF&MONEYVAL-IL-MER-4-0-201812.pdf"

    # 提取页眉页脚
    headers, footers = auto_detect_header_footer_regions(pdf_file)
    print(f"Header region: {headers}")
    print(f"Footer region: {footers}")
    visualize_regions(pdf_file, None, headers, footers)

```

### 核心算法说明

1. **自动检测区域流程**：
   - 分析前 n 页（默认为5页）的顶部和底部区域
   - 收集这些区域中的所有文本块及其位置
   - 使用规范化位置（相对于页面高度的比例）来处理不同大小的页面
   - 聚类相似位置的文本块
   - 找出在多页中重复出现的区域

2. **文本块聚类**：
   - 按垂直位置聚类文本块（使用四舍五入到小数点后3位的位置）
   - 合并位置相近的聚类（<1%页面高度的差异）
   - 保留在多页中出现的聚类（默认至少2页）

3. **共同文本提取**：
   - 使用最长文本作为参考
   - 逐字符比较找出共同部分
   - 只保留重叠比例超过阈值（默认50%）的文本 （难点，因为存在页码等变化内容，如何正确识别页眉页脚区域）

4. **区域确定**：
   - **页眉区域**：
      - `header_y0 = 0`
      - `header_y1 = min( max( [该页顶部区域所有文本块的最大y1] for 每一页 ), 50)` 
      注意：这里我们取每一页顶部文本块的最大y1，然后取这些y1的最大值（即最靠下的那个），再和50取最小
     这样，如果某一页的页眉底部边界在40，另一页在45，我们取45，但不超过50。这样能覆盖这两页的页眉。
   - **页脚区域**：
      - `footer_y0 = max( min( [该页底部区域所有文本块的最小y0] for 每一页 ), page_height-50)`
      - `footer_y1 = page_height`
      这里我们取每一页底部文本块的最小y0，然后取这些y0的最小值（即最靠上的那个），再和page_height-50取最大

### 高级特性

1. **自适应页面大小**：
   - 使用规范化位置（位置/页面高度）处理不同大小的页面
   - 提取时根据当前页面高度调整区域

2. **智能文本分析**：
   - 找出文本中的共同部分，忽略变化内容（如页码）
   - 使用重叠比例阈值过滤噪声

3. **参数可配置**：
   - `sample_pages`：控制分析的样本页数
   - `top_margin`/`bottom_margin`：定义初始检测区域
   - `min_occurrence`：设置区域在多页中出现的最小次数
   - `min_overlap`：设置文本相似度阈值


### 使用建议

1. **处理复杂文档**：
   ```python
   # 对于大型文档增加样本页数
   headers, footers = extract_header_footer_with_auto_detection(pdf_file, sample_pages=10)
   
   # 对于特殊布局调整区域大小
   headers, footers = extract_header_footer_with_auto_detection(
       pdf_file, 
       top_margin=150,  # 扩大顶部区域
       bottom_margin=120  # 扩大底部区域
   )
   ```

2. **处理奇偶页不同的文档**：
   ```python
   # 分别处理奇偶页
   even_headers = []
   odd_headers = []
   
   for i, header in enumerate(headers):
       if i % 2 == 0:  # 偶数页
           even_headers.append(header)
       else:  # 奇数页
           odd_headers.append(header)
   ```

3. **可视化检测结果**：
   ```python
    def visualize_regions(pdf_path, out_path, header_rect, footer_rect):
        """
        可视化页眉和页脚区域

        参数:
            pdf_path: PDF文件路径
            out_path: 输出文件路径
            header_rect: 页眉区域矩形 (pymupdf.Rect)
            footer_rect: 页脚区域矩形 (pymupdf.Rect)
        """
        if out_path is None:
            out_path = pdf_path.replace('.pdf', '_visual.pdf')
        doc = pymupdf.open(pdf_path)
        header_rect = pymupdf.Rect(header_rect)
        footer_rect = pymupdf.Rect(footer_rect)
        for page in doc:
            if header_rect.height:
                page.add_rect_annot(header_rect)
            if footer_rect.height:
                page.add_rect_annot(footer_rect)

        doc.save(out_path)
        print(f"Visualization saved to {out_path}")
        doc.close()
   ```

4. **处理扫描文档**：
   ```python
   # OCR预处理函数（需安装pytesseract）
   def ocr_page(page):
       import pytesseract
       from PIL import Image
       
       pix = page.get_pixmap(dpi=200)
       img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
       return pytesseract.image_to_string(img)
   
   # 在提取前添加OCR处理
   doc = fitz.open(pdf_path)
   page = doc.load_page(0)
   if not page.get_text("text"):  # 检查是否有文本层
       ocr_text = ocr_page(page)
       # 将OCR结果添加到页面（伪代码）
   ```

### 注意事项

1. **页面大小变化**：
   - 算法使用规范化位置处理不同大小的页面
   - 对于页面大小变化较大的文档，结果可能不准确

2. **复杂布局**：
   - 对于多栏布局或复杂页眉页脚，可能需要调整参数
   - 首页和章节页可能需要特殊处理

3. **性能考虑**：
   - 分析大量页面可能影响性能
   - 对于大型文档，建议设置合理的sample_pages值

4. **特殊内容**：
   - 水印或装饰性元素可能被误识别为页眉页脚
   - 表格跨页的表头可能被误识别为页眉

此实现提供了自动检测页眉页脚的强大工具，但实际应用中可能需要根据具体文档特征调整参数。对于关键任务，建议添加人工审核环节验证检测结果。


## PDF文件页眉页脚去除

### 去除PDF页眉页脚分析
我们需要一个使用Python的解决方案，能够识别并去除PDF的页眉和页脚。考虑到PDF可能是文本型或扫描图像型，我们将采取以下步骤：
 1. 对于文本型PDF：我们可以直接通过定位页眉页脚区域（通常位于页面顶部和底部）的文本或对象，然后删除或覆盖它们。
 2. 对于扫描图像型PDF：我们可能需要先进行OCR识别，但这样比较复杂。另一种简单的方法是使用白色矩形覆盖页眉页脚区域（前提是页眉页脚的位置固定）。

> 考虑到复杂性，我们可能只处理文本型PDF，并且假设页眉页脚是文本。


另外，我们可以提供第三种方法：覆盖法（用白色矩形覆盖），这种方法对于扫描件也适用。

在手动模式中，我们可以选择使用覆盖法（用白色矩形）或者使用redaction（删除文本）。对于扫描件，redaction可能不起作用，因为扫描件中的“文本”实际上是图像。因此，我们统一使用覆盖法（即画白色矩形）来同时支持文本型和扫描件。

注意：使用绘图函数会添加新的内容，覆盖原有内容。
示例代码（手动模式）：
  ```python
  import fitz
  def remove_header_footer_manual(pdf_path, output_path, header_rect=None, footer_rect=None):
      doc = fitz.open(pdf_path)
      for page in doc:
          # 获取页面的边界框
          page_rect = page.rect
          # 创建白色矩形覆盖页眉
          if header_rect is not None:
              # 确保header_rect是fitz.Rect类型
              if not isinstance(header_rect, fitz.Rect):
                  header_rect = fitz.Rect(header_rect)
              # 绘制一个白色矩形
              page.draw_rect(header_rect, color=(1,1,1), fill=(1,1,1), overlay=True)
          # 创建白色矩形覆盖页脚
          if footer_rect is not None:
              if not isinstance(footer_rect, fitz.Rect):
                  footer_rect = fitz.Rect(footer_rect)
              page.draw_rect(footer_rect, color=(1,1,1), fill=(1,1,1), overlay=True)
      doc.save(output_path)
  ```

### 代码实现
以下是使用Python实现PDF页眉页脚识别与去除的完整解决方案，结合了文本定位、区域检测：

```python
import re
import pymupdf  # PyMuPDF
import numpy as np
from collections import defaultdict


def auto_detect_header_footer_regions(pdf_path,
                                      sample_pages: int = 6,
                                      header_margin: int = 100,
                                      footer_margin: int = 100,
                                      min_overlap: float = 0.5,
                                      min_occurrence: int = 2,
                                      default_region: int = 90):
    """
    自动检测PDF文档的页眉和页脚区域

    参数:
        doc: 打开的PyMuPDF文档对象
        sample_pages: 分析的样本页数
        header_margin: 顶部区域高度(像素)
        footer_margin: 底部区域高度(像素)
        min_overlap: 内容重叠阈值(0-1)
        min_occurrence: 文本块在多页中出现的最小次数
        default_region: 默认区域高度(像素)

    返回:
        header_rect: 页眉区域矩形 (pymupdf.Rect)
        footer_rect: 页脚区域矩形 (pymupdf.Rect)
    """

    doc = pymupdf.open(pdf_path)
    # 存储所有页面的顶部和底部文本块
    top_blocks = defaultdict(list)
    bottom_blocks = defaultdict(list)

    # 存储所有页面的高度
    page_heights = []

    # 分析样本页面
    num_pages = min(sample_pages, len(doc))
    # 如果没有页面，返回空矩形
    if num_pages == 0:
        return pymupdf.Rect(0, 0, 0, 0), pymupdf.Rect(0, 0, 0, 0)

    for page_num in range(num_pages):
        page = doc.load_page(page_num)
        page_rect = page.rect
        page_heights.append(page_rect.height)

        # 定义顶部和底部区域
        top_zone = pymupdf.Rect(0, 0, page_rect.width, header_margin)
        bottom_zone = pymupdf.Rect(0, page_rect.height - footer_margin,
                                   page_rect.width, page_rect.height)

        # 获取页面文本块
        blocks = page.get_text("blocks")

        # 收集顶部区域文本块
        for block in blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            block_rect = pymupdf.Rect(x0, y0, x1, y1)

            # 检查是否在顶部区域
            if block_rect.intersects(top_zone):
                # 规范化位置 (相对位置)
                norm_y = (y0 + y1) / 2 / page_rect.height
                top_blocks[page_num].append((norm_y, text.strip(), block_rect))

        # 收集底部区域文本块
        for block in blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            block_rect = pymupdf.Rect(x0, y0, x1, y1)

            # 检查是否在底部区域
            if block_rect.intersects(bottom_zone):
                # 规范化位置 (相对位置)
                norm_y = (y0 + y1) / 2 / page_rect.height
                bottom_blocks[page_num].append((norm_y, text.strip(), block_rect))

    # 计算平均页面高度
    avg_height = np.mean(page_heights) if page_heights else 0

    # 检测页眉区域
    header_candidates = detect_common_region(top_blocks, min_occurrence, min_overlap)
    header_rect = pymupdf.Rect(0, 0, 0, 0)

    if header_candidates:
        # 设置页眉区域矩形 min( max( [page_top_blocks_max_y1] ), 50 )
        header_y1 = min(max(cand[2] for cand in header_candidates), default_region)
        header_rect = pymupdf.Rect(0, 0, page_rect.width, header_y1)

    # 检测页脚区域
    footer_candidates = detect_common_region(bottom_blocks, min_occurrence, min_overlap)
    footer_rect = pymupdf.Rect(0, 0, 0, 0)

    if footer_candidates:
        # 计算页脚区域的Y范围  max( min( [page_bottom_blocks_min_y0] ), page_height-50 )
        footer_y0 = max(min(cand[1] for cand in footer_candidates), avg_height - default_region)
        # 设置页脚区域矩形
        footer_rect = pymupdf.Rect(0, footer_y0, page_rect.width, page_rect.height)

    return header_rect, footer_rect


def detect_common_region(blocks_dict, min_occurrence: int, min_overlap: float):
    """
    检测多个页面中共同出现的文本块区域

    参数:
        blocks_dict: 页面文本块字典 {page_num: [(norm_y, text, rect)]}
        min_occurrence: 在多页中出现的最小次数
        min_overlap: 位置重叠阈值

    返回:
        候选区域列表 [(norm_y, min_y, max_y, text)]
    """
    # 按Y位置聚类文本块
    position_clusters = defaultdict(list)

    # 收集所有文本块位置
    for page_blocks in blocks_dict.values():
        for norm_y, text, rect in page_blocks:
            # 跳过空文本
            if not text:
                continue
            position_clusters[round(norm_y, 3)].append((norm_y, text, rect))

    # 合并位置相近的聚类
    merged_clusters = []
    positions = sorted(position_clusters.keys())
    current_cluster = []

    for pos in positions:
        if not current_cluster:
            current_cluster = position_clusters[pos]
            continue

        # 检查位置是否接近
        last_pos = current_cluster[-1][0]
        if abs(pos - last_pos) <= 0.01:  # 约1%页面高度的差异
            current_cluster.extend(position_clusters[pos])
        else:
            merged_clusters.append(current_cluster)
            current_cluster = position_clusters[pos]

    if current_cluster:
        merged_clusters.append(current_cluster)

    # 找出在多页中出现的区域
    candidates = []
    for cluster in merged_clusters:
        # 跳过出现次数不足的区域
        if len(cluster) < min_occurrence:
            continue

        # 计算位置范围
        min_y = min(rect.y0 for _, _, rect in cluster)
        max_y = max(rect.y1 for _, _, rect in cluster)
        texts = [text for _, text, _ in cluster]

        # 计算平均位置
        avg_y = np.mean([y for y, _, _ in cluster])

        # 计算文本相似度
        common_text = find_common_text(texts, min_occurrence, min_overlap)
        if common_text:
            candidates.append((avg_y, min_y, max_y, common_text))

    return candidates


def longest_common_substring(strs: list[str]):
    """
    找出字符串列表中最长的公共子串。

    参数:
    strs: 字符串列表，例如 ["flower", "flow", "flight"]

    返回:
    最长的公共子串，如果没有则返回空字符串。
    """
    if not strs:
        return ""
    if len(strs) == 1:
        return strs[0]

    # 找到最短字符串
    min_str = min(strs, key=len)
    min_len = len(min_str)

    # 从最长长度开始，逐步减小长度
    for length in range(min_len, 0, -1):
        # 遍历每个起始位置
        for start in range(0, min_len - length + 1):
            substr = min_str[start:start + length]
            # 检查子串是否在所有字符串中
            if all(substr in s for s in strs):
                return substr

    return ""  # 无公共子串


def find_common_text(texts, min_occurrence=3, min_overlap=0.5):
    """
    在一组文本中找出共同的部分

    参数:
        texts: 文本列表
        min_overlap: 最小重叠比例

    返回:
        共同文本或None
    """
    if not texts:
        return None

    # 使用最长文本作为参考
    reference = max(texts, key=len)
    common_text = longest_common_substring(texts)

    overlap_rate = len(common_text) / len(reference)
    # 检查是否满足最小重叠要求
    if common_text and overlap_rate >= min_overlap:
        return common_text

    # 移除页码
    clean_texts = [extract_and_remove_page_number(text) for text in texts]
    # 如果有min_occurrence个以上的文本重复，则认为是重复的
    count_text = defaultdict(int)
    for text in clean_texts:
        count_text[text] += 1

    for text, count in count_text.items():
        if count >= min_occurrence:
            return text

    return None


def extract_and_remove_page_number(text):
    """
    从文本中识别并分离页码
    """
    # 常见页码模式
    patterns = [
        r'\b(\d{1,4})\b',  # 简单数字: 1, 23, 456
        r'[-–—]\s*(\d+)\s*[-–—]',  # 装饰页码: - 1 -, –2–
        r'Page\s*(\d+)\s*of\s*\d+',  # Page 1 of 10
        r'第\s*(\d+)\s*页',  # 中文: 第1页
        r'\b([ivxlcdm]+)\b',  # 罗马数字: i, ii, iii
        r'(\d+)\s*/\s*\d+'  # 分数形式: 1/10
    ]
    # text去除特殊字符
    text = re.sub(r'[^\w\s]', '', text)
    # text去除数字
    text = re.sub(r'\d+', '', text)
    page_number = ""
    cleaned_text = text

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            page_number = match.group(1)
            # 移除匹配到的整个模式（而不仅仅是数字），以清除分隔符
            cleaned_text = cleaned_text.replace(match.group(0), '').strip()
            break  # 找到一个就停止

    return cleaned_text


def visualize_regions(pdf_path, out_path, header_rect, footer_rect):
    """
    可视化页眉和页脚区域

    参数:
        pdf_path: PDF文件路径
        out_path: 输出文件路径
        header_rect: 页眉区域矩形 (pymupdf.Rect)
        footer_rect: 页脚区域矩形 (pymupdf.Rect)
    """
    if out_path is None:
        out_path = pdf_path.replace('.pdf', '_visual.pdf')
    doc = pymupdf.open(pdf_path)
    header_rect = pymupdf.Rect(header_rect)
    footer_rect = pymupdf.Rect(footer_rect)
    for page in doc:
        if header_rect.height:
            page.add_rect_annot(header_rect)
        if footer_rect.height:
            page.add_rect_annot(footer_rect)

    doc.save(out_path)
    print(f"Visualization saved to {out_path}")
    doc.close()


def remove_pdf_header_footer(pdf_path, output_path,
                             header_margin=50, footer_margin=50,
                             auto_detect=True,
                             header_rect=None, footer_rect=None,
                             min_overlap=0.5,
                             remove_mode='redact'):
    """
    PDF页眉页脚识别与去除工具

    参数:
    input_path: 输入PDF路径
    output_path: 输出PDF路径
    header_margin: 页眉检测区域高度(像素)距离顶部
    footer_margin: 页脚检测区域高度(像素)距离底部
    auto_detect: 是否自动检测页眉页脚区域
    header_rect: 手动指定的页眉区域(x0, y0, x1, y1)
    footer_rect: 手动指定的页脚区域(x0, y0, x1, y1)
    min_overlap: 内容重叠阈值(0-1)
    remove_mode: 去除模式('redact'删除内容, 'cover'白块覆盖)
    """

    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)

    # 如果没有手动指定区域，自动检测
    if auto_detect and (header_rect is None or footer_rect is None):
        print(f"开始自动检测页眉页脚区域...")
        header_rect, footer_rect = auto_detect_header_footer_regions(pdf_path=pdf_path,
                                                                     header_margin=header_margin,
                                                                     footer_margin=footer_margin,
                                                                     min_overlap=min_overlap
                                                                     )
        print(f"自动检测完成!")
        print(f"Header region: {header_rect}")
        print(f"Footer region: {footer_rect}")

    # 处理所有页面
    for page_num in range(total_pages):
        page = doc[page_num]

        if remove_mode == 'redact':
            # 使用红action删除内容
            if header_rect:
                page.add_redact_annot(header_rect)
            if footer_rect:
                page.add_redact_annot(footer_rect)
            page.apply_redactions()
        else:
            # 使用白块覆盖
            if header_rect:
                draw_white_rectangle(page, header_rect)
            if footer_rect:
                draw_white_rectangle(page, footer_rect)

    # 保存处理后的PDF
    doc.save(output_path)
    doc.close()
    print(f"处理完成! 输出文件: {output_path}")


def draw_white_rectangle(page, rect):
    """
    绘制白色矩形覆盖区域
    """
    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)


def main():
    # 使用示例
    input_pdf = "/Users/xiniao/Downloads/FATF-ME-FATF-TR-MER-4-0-201912.pdf"
    output_pdf = "output.pdf"
    # 自动检测页眉页脚区域
    header_rect, footer_rect = auto_detect_header_footer_regions(input_pdf)
    print(f"Header region: {header_rect}")
    print(f"Footer region: {footer_rect}")
    # 可视化页眉页脚区域
    visualize_regions(input_pdf, output_pdf.replace('.pdf', '_visual.pdf'), header_rect, footer_rect)

    # 去除页眉页脚
    remove_pdf_header_footer(input_pdf, output_pdf, header_rect=header_rect, footer_rect=footer_rect)


if __name__ == "__main__":
    main()

```
### 解决方案特点

1. **智能区域检测**
   - 文本分析：识别页眉页脚区域的文本块
   - 多页采样：分析多个页面确定稳定区域
   - 敏感度控制：可调整检测准确度
   - 可视化：提供区域可视化工具

2. **两种去除模式**
   - **Redact模式**：直接删除文本内容（适合文本型PDF）
   - **Cover模式**：用白色矩形覆盖（适合扫描件/图像型PDF）

3. **灵活的调用方式**
   - 全自动检测：`remove_pdf_header_footer(input_pdf, output_pdf)`
   - 手动指定区域：提供header_rect和footer_rect参数
   - 混合模式：自动检测+手动调整

### 使用示例：

```python
# 基本用法（全自动检测）
remove_pdf_header_footer("input.pdf", "output.pdf")

# 指定区域模式
remove_pdf_header_footer(
    "input.pdf", 
    "output.pdf",
    auto_detect=False,
    header_rect=(50, 50, 550, 70),  # (x0, y0, x1, y1)
    footer_rect=(50, 770, 550, 790)
)

# 图像覆盖模式（适合扫描件）
remove_pdf_header_footer(
    "scanned.pdf", 
    "cleaned.pdf",
    header_rect=(50, 50, 550, 70),  # (x0, y0, x1, y1)
    footer_rect=(50, 770, 550, 790)
    remove_mode='cover'
)

# 调整检测敏感度
remove_pdf_header_footer(
    "complex.pdf", 
    "processed.pdf",
    min_overlap=0.3  # 降低重复内容检测敏感度应对复杂布局
)


# 使用示例
input_pdf = "input.pdf"
output_pdf = "output.pdf"
# 自动检测页眉页脚区域
header_rect, footer_rect = auto_detect_header_footer_regions(input_pdf)
print(f"Header region: {header_rect}")
print(f"Footer region: {footer_rect}")
# 可视化页眉页脚区域
visualize_regions(input_pdf, output_pdf.replace('.pdf', '_visual.pdf'), header_rect, footer_rect)

# 去除页眉页脚
remove_pdf_header_footer(input_pdf, output_pdf, header_rect=header_rect, footer_rect=footer_rect)

```

### 效果演示
#### 示例一
下面看一个比较复杂的页眉页脚识别的例子

| **类型**               | **第三页示例**                                    | **第四页示例**                                    |
| ---------------------- | ------------------------------------------------- | ------------------------------------------------- |
| **原PDF页脚**          | ![1.jpg](./image/PDF页眉页脚识别与去除方案/1.jpg) | ![2.jpg](./image/PDF页眉页脚识别与去除方案/2.jpg) |
| **自动检测的页脚区域** | ![3.jpg](./image/PDF页眉页脚识别与去除方案/3.jpg) | ![4.jpg](./image/PDF页眉页脚识别与去除方案/4.jpg) |
| **去除页脚后的效果**   | ![5.jpg](./image/PDF页眉页脚识别与去除方案/5.jpg) | ![6.jpg](./image/PDF页眉页脚识别与去除方案/6.jpg) |


可以看到，页脚的区域比较复杂，包含了页码，不同页面的页脚内容也不同（页码所在的位置不是固定的）。

#### 示例二

| **类型** | **原PDF页脚**                                     | **自动检测的页脚区域**                            | **去除页脚后的效果**                              |
| -------- | ------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------- |
| **示例** | ![7.jpg](./image/PDF页眉页脚识别与去除方案/7.jpg) | ![8.jpg](./image/PDF页眉页脚识别与去除方案/8.jpg) | ![9.jpg](./image/PDF页眉页脚识别与去除方案/9.jpg) |





### 技术说明：

1. **安装依赖**：
   ```bash
   pip install PyMuPDF 
   ```

2. **处理流程**：
   1. 分析PDF页面结构
   2. 检测页眉页脚区域（文本+图像分析）
   3. 应用区域删除或覆盖
   4. 保存处理后的PDF

3. **适用场景**：
   - 学术论文格式整理
   - 商业报告标准化
   - 文档数字化处理
   - PDF批量处理自动化

此解决方案能有效处理大多数页眉页脚场景，包括动态页码、公司logo等复杂元素，通过调整参数可适应不同PDF格式需求。



## 参考文档
1. [PyMuPDF基本使用官方教程](https://pymupdf.readthedocs.io/en/latest/tutorial.html)
2. [理解PDF边界框(bbox)的坐标系](https://pymupdf.readthedocs.io/en/latest/app3.html#coordinates)
3. [编辑PDF中的内容](https://pymupdf.readthedocs.io/en/latest/the-basics.html#redacting-content-from-a-pdf)
