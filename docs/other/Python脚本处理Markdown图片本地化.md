# Python脚本处理Markdown图片本地化

## 需求描述

使用python写一个方法实现将markdown文件中的图片路径保存到以markdown文件命名的目录中，并且将markdown文件中远程图片地址替换为本地图片地址。

## 需求分析

**根据需求描述，需要完成以下任务：**
1. 解析Markdown文件，提取其中的图片链接（可能是远程URL，也可能是本地路径，但我们主要关注远程URL，因为本地路径可能已经是我们想要的）。
2. 将远程图片下载到本地，保存到一个以Markdown文件命名的目录中（例如，如果Markdown文件名为"example.md"，则创建"example"目录）。
3. 将Markdown文件中的远程图片地址替换为本地图片地址（即刚刚下载保存的图片的相对路径或绝对路径？这里我们一般使用相对路径，以便于移动整个目录时仍能访问）。
   
**代码实现步骤：**

1. 读取Markdown文件内容。
2. 使用正则表达式匹配Markdown中的图片语法（如`![alt](url)`）。
3. 对于匹配到的每一个图片URL：
    a. 如果URL是远程的（以http或https开头），则下载图片到本地目录（以Markdown文件名命名的目录）。
    b. 如果是本地路径，我们可以选择跳过，或者也将其复制到目标目录？根据需求，这里主要是处理远程图片，所以跳过本地路径。
4. 将下载后的图片本地路径（相对于Markdown文件的路径）替换到原Markdown文本中。
5. 将修改后的Markdown内容写回原文件或新文件，可以提供选项来控制是否覆盖原文件。
   
注意：需要处理网络请求和文件操作，因此需要引入相关库。
具体实现：
   - 使用os模块处理路径和目录。
   - 使用re模块匹配图片链接。
   - 使用requests下载图片（注意处理异常）。

另外，为了避免重复下载同一个远程图片（如果同一图片在文件中多次使用），我们可以考虑缓存已下载的图片，但也可以每次遇到都重新下载（为了简单，我们每次遇到都下载，但这样效率低，所以我们用字典缓存已下载的URL对应的本地路径）。

但是注意：同一个URL可能在不同位置需要不同的文件名？或者我们可以用URL的哈希来命名？但这样可能不便于管理。我们也可以使用原图片文件名（从URL中提取）并保存到本地目录。如果文件名重复，我们可以添加后缀。

步骤细化：

1. 解析Markdown文件路径，得到文件所在目录、文件名（不含扩展名）等。
2. 创建以Markdown文件名（不含扩展名）命名的目录，位于Markdown文件同一目录下。
3. 读取Markdown内容。
4. 使用正则表达式找到所有图片链接。
5. 遍历每个匹配到的图片链接，对于远程URL：
    - 从URL中提取文件名（如果URL末尾有文件名，则使用；否则，根据内容类型生成文件名，但为了简单，我们可以用URL的哈希值作为文件名，并加上扩展名，但扩展名需要从Content-Type获取，如果没有则用默认.jpg）。
    - 下载图片到创建的目录中。
    - 记录下载后的本地相对路径（相对于Markdown文件的路径，例如："./markdown文件名目录/image.jpg"）。
    - 将原Markdown中的这个URL替换为本地路径。
6. 将替换后的内容写回Markdown文件。

## 代码实现
1. 定义函数：`def convert_markdown_images(md_file_path, overwrite=False):`
     其中，`overwrite`参数用于控制是否覆盖原文件。如果不覆盖，则生成新文件，比如在原文件名后加“_local.md”。
2. 创建目标图片目录：
    ```python
     base_name = os.path.basename(md_file_path)  # 例如：'example.md'
     dir_name = os.path.splitext(base_name)[0]  # 例如：'example'
     parent_dir = os.path.dirname(md_file_path)
     image_dir = os.path.join(parent_dir, dir_name)  # 图片存储目录
     # 如果目录不存在，则创建。
    ```
3. 读取Markdown文件内容。
4. 正则匹配：`pattern = r'!\[(.*?)\]\((.*?)\)'`
    注意：这个正则表达式可能匹配到多个，我们使用findall。
5. 遍历所有匹配，对于每个匹配，alt_text是第一个分组，url是第二个分组。
    如果url以http://或https://开头，则是远程图片。
    下载图片，并保存到image_dir目录下。
    下载时，我们尝试从url中获取文件名：使用`url.split('/')[-1]`，然后去掉可能包含的查询参数（用?分割取第一部分）。
    如果文件名没有扩展名，那么我们从`Content-Type`中获取扩展名（例如image/jpeg则扩展名为.jpg）。
    如果文件名已经存在，为了避免覆盖，为了简单，我们使用一个函数来生成唯一的文件名。
6. 下载图片并保存到本地文件，同时记录本地相对路径（相对于Markdown文件）。
    相对路径：例如，如果Markdown文件在`parent_dir`，图片在`parent_dir/dir_name`，那么相对路径就是`./dir_name/filename.jpg`
7. 替换原字符串中的url为这个相对路径。
8. 注意：同一个url在文件中出现多次，我们可以只下载一次，然后多次替换。所以我们可以用一个字典来缓存url到本地路径的映射。
9.  将修改后的内容写回文件（覆盖原文件或新文件）。
10. 异常处理：下载图片时可能失败，可以选择跳过并打印警告。

以下是一个Python脚本，用于处理Markdown文件中的远程图片，将其下载到本地目录并替换链接，并支持从命令行接收Markdown文件路径进行转换：

```python
import os
import re
import requests
import uuid
import argparse
import sys
import glob
from pathlib import Path
from urllib.parse import urlparse

def process_markdown_images(md_file_path, overwrite=True):
    """
    处理Markdown文件中的远程图片：
    1. 创建与Markdown文件同名的目录
    2. 下载所有远程图片到该目录
    3. 替换Markdown中的图片链接为本地相对路径
    
    :param md_file_path: Markdown文件路径
    :param overwrite: 是否覆盖原始文件
    :return: (下载的图片数量, 输出文件路径)
    """
    # 验证文件是否存在且为.md文件
    if not os.path.isfile(md_file_path):
        raise FileNotFoundError(f"文件不存在: {md_file_path}")
    
    if not md_file_path.lower().endswith(('.md', '.markdown')):
        raise ValueError(f"不是Markdown文件: {md_file_path}")
    
    # 读取Markdown内容
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建图片存储目录
    base_name = Path(md_file_path).stem
    parent_dir = Path(md_file_path).parent
    image_dir = parent_dir / base_name
    image_dir.mkdir(exist_ok=True)
    
    # 查找所有图片标记
    pattern = r'!\[(.*?)\]\((.*?)\)'
    matches = re.findall(pattern, content)
    
    # 用于跟踪已下载图片避免重复下载
    downloaded = {}
    
    # 处理每个匹配项
    def replace_match(match):
        alt_text = match.group(1)
        img_url = match.group(2).strip()  # 去除可能的空格
        
        # 跳过非HTTP链接和空链接
        if not (img_url.startswith('http') and img_url):
            return match.group(0)
        
        # 检查是否已下载
        if img_url in downloaded:
            return f'![{alt_text}]({downloaded[img_url]})'
        
        try:
            # 下载图片
            response = requests.get(img_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 获取文件扩展名
            content_type = response.headers.get('content-type', '')
            ext = '.jpg'  # 默认值
            if 'image/' in content_type:
                ext = '.' + content_type.split('/')[-1]
                # 处理特殊扩展名
                if ext == '.jpeg':
                    ext = '.jpg'
                elif ext == '.svg+xml':
                    ext = '.svg'
            
            # 生成唯一文件名
            img_name = f"{uuid.uuid4().hex[:8]}{ext}"
            img_path = image_dir / img_name
            rel_path = f"{base_name}/{img_name}"
            
            # 保存图片
            with open(img_path, 'wb') as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)
            
            # 记录已下载图片
            downloaded[img_url] = rel_path
            return f'![{alt_text}]({rel_path})'
        
        except Exception as e:
            print(f"警告: 下载失败 [{img_url}] - {str(e)}")
            return match.group(0)
    
    # 替换所有远程图片链接
    new_content = re.sub(pattern, replace_match, content)
    
    # 确定输出文件路径
    if overwrite:
        output_path = md_file_path
    else:
        # 添加后缀 "_local" 到文件名
        path_obj = Path(md_file_path)
        output_path = path_obj.with_name(f"{path_obj.stem}_local{path_obj.suffix}")
    
    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return len(downloaded), output_path

def expand_file_patterns(patterns, recursive=False):
    """扩展文件模式为实际文件列表"""
    files = []
    for pattern in patterns:
        # 处理目录
        if os.path.isdir(pattern):
            files.extend(glob.glob(os.path.join(pattern, '*.md')))
            files.extend(glob.glob(os.path.join(pattern, '*.markdown')))
            if recursive:
                for root, dirs, filenames in os.walk(pattern):
                    files.extend(glob.glob(os.path.join(root, '*.md')))
                    files.extend(glob.glob(os.path.join(root, '*.markdown')))
        # 处理通配符
        else:
            expanded = glob.glob(pattern, recursive=recursive)
            if not expanded:
                # 如果没有匹配项，尝试添加通配符
                if not pattern.endswith('*'):
                    expanded = glob.glob(pattern + '*', recursive=recursive)
                # 如果还是没有匹配项，尝试作为文件处理
                if not expanded and os.path.isfile(pattern):
                    expanded = [pattern]
            files.extend(expanded)
    
    # 去重并过滤非Markdown文件
    unique_files = set()
    for file in files:
        if os.path.isfile(file) and file.lower().endswith(('.md', '.markdown')):
            unique_files.add(os.path.abspath(file))
    
    return sorted(unique_files)

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(
        description='将Markdown中的远程图片下载到本地并替换链接',
        epilog='示例:\n'
               '  处理单个文件: python md_image_localizer.py doc.md\n'
               '  处理多个文件: python md_image_localizer.py doc1.md doc2.md\n'
               '  处理目录: python md_image_localizer.py docs/\n'
               '  使用通配符: python md_image_localizer.py "*.md" "chapter_*/*.md"'
    )
    parser.add_argument(
        'paths', 
        nargs='+',
        help='要处理的Markdown文件路径、目录或通配符模式'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细处理信息'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='递归处理目录中的Markdown文件'
    )
    parser.add_argument(
        '--no-overwrite',
        action='store_true',
        help='不覆盖原始文件，生成新文件（添加"_local"后缀）'
    )
    
    args = parser.parse_args()
    
    # 扩展文件列表
    files_to_process = expand_file_patterns(args.paths, args.recursive)
    
    if not files_to_process:
        print("错误: 没有找到可处理的Markdown文件", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"找到 {len(files_to_process)} 个Markdown文件:")
        for i, file in enumerate(files_to_process, 1):
            print(f"  {i}. {file}")
    
    # 处理每个文件
    total_images = 0
    processed_files = 0
    
    for file_path in files_to_process:
        try:
            if args.verbose:
                print(f"\n正在处理: {file_path}")
                print(f"  覆盖模式: {'是' if not args.no_overwrite else '否'}")
            
            count, output_path = process_markdown_images(
                file_path, 
                overwrite=not args.no_overwrite
            )
            total_images += count
            processed_files += 1
            
            if args.verbose:
                print(f"  下载了 {count} 张图片")
                print(f"  输出文件: {output_path}")
            else:
                print(f"处理完成: {output_path} (下载 {count} 张图片)")
        
        except Exception as e:
            print(f"错误: 处理文件 {file_path} 失败 - {str(e)}", file=sys.stderr)
    
    # 输出总结
    print("\n处理完成!")
    print(f"已处理文件: {processed_files}/{len(files_to_process)}")
    print(f"总下载图片: {total_images} 张")
    if args.no_overwrite:
        print("注意: 原始文件未修改，已生成新文件（添加了'_local'后缀）")

if __name__ == "__main__":
    main()
```


## 使用示例

1. **默认行为（覆盖原始文件）**：
   ```bash
   python md_image_localizer.py document.md
   ```

2. **保留原始文件（生成新文件）**：
   ```bash
   python md_image_localizer.py document.md --no-overwrite
   # 生成 document_local.md
   ```

3. **批量处理并保留原始文件**：
   ```bash
   python md_image_localizer.py *.md --no-overwrite
   # 为每个.md文件生成对应的_local.md文件
   ```

4. **结合其他选项**：
   ```bash
   python md_image_localizer.py docs/ -r --no-overwrite -v
   # 递归处理docs目录，保留原始文件，显示详细信息
   ```


**输出示例（使用 `--no-overwrite`）：**

```
找到 2 个Markdown文件:
  1. /projects/docs/chapter1.md
  2. /projects/docs/chapter2.md

正在处理: /projects/docs/chapter1.md
  覆盖模式: 否
  下载了 3 张图片
  输出文件: /projects/docs/chapter1_local.md

正在处理: /projects/docs/chapter2.md
  覆盖模式: 否
  下载了 5 张图片
  输出文件: /projects/docs/chapter2_local.md

处理完成!
已处理文件: 2/2
总下载图片: 8 张
注意: 原始文件未修改，已生成新文件（添加了'_local'后缀）
```
