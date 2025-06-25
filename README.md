# myblog
记录一些学习笔记 :smile:

本博客使用 [MkDocs](https://github.com/mkdocs/mkdocs) 生成
> MkDocs是一个快速、简单、华丽的静态站点生成器，用于构建项目留档。文档源文件是用Markdown编写的，并使用单个YAML配置文件进行配置。它旨在易于使用，可以通过第三方主题、插件和Markdown扩展进行扩展。


## 前言

> 纸上得来终觉浅，绝知此事要躬行

在网上看到很多大佬的优秀博客，从他们的文章中学到了很多，特别是看到博主的自我介绍以及博文列表，不得不称赞“真的太优秀了”，想到了那句：比你优秀的人比你还努力，难免产生焦虑情绪，但是对于有积极心理的人，也许就不能称之为焦虑，而是打了一针鸡血。就目前对我来说还是比较积极的，依然对技术还保持着热情，所以心里默默对自己说：应该向这些优秀的大佬学习，养成写博客的习惯，将自己学习的知识记录下来。

说实话就个人而言并不擅长写文章，是那种高考作文都写不满 800 字的人，不期待自己能写出多么优秀的文章，只希望尽自己最大的努力将写的内容尽可能描述清楚。

## 本地使用Mkdocs生成博客

### 使用uv创建python虚拟环境

```bash
uv venv
source .venv/bin/activate
```
> 使用 uv 创建python虚拟环境时指定虚拟环境目录和python版本：
> `uv venv .venv --python 3.12`

### 安装 Mkdocs

```bash
uv pip install mkdocs
```

### 创建项目(可选)
当前项目已经创建，可以跳过该步骤，直接进入项目目录
```bash
mkdocs new myblog
cd myblog
```

### 启动服务
```bash
mkdocs serve
```

### 安装mkdocs-material主题
> [mkdocs-material](https://github.com/squidfunk/mkdocs-material)是一个Material Design风格的主题

```bash
uv pip install mkdocs-material
```

使用`mkdocs-material`主题配置支持`mermaid`流程图，在`mkdocs.yml`中添加以下配置：
> 参考文档：https://squidfunk.github.io/mkdocs-material/reference/diagrams/
```yaml
theme:
  name: material
  features:
    - content.code.copy
    - content.tabs.link
markdown_extensions:
   - pymdownx.superfences:
        custom_fences:
           - name: mermaid
             class: mermaid
             format: !!python/name:pymdownx.superfences.fence_code_format
```


## 使用python脚本生成导航目录
我们需要读取原始的`mkdocs.yml`文件，然后修改其中的nav部分，其他部分保持不变。

使用python脚本生成导航目录包含两个部分：

1. 生成导航列表的函数（递归）
2. 使用ruamel.yaml替换原YAML中的nav部分

> 注意：我们假设docs目录为当前目录下的`docs`文件夹。

### 生成导航列表的函数（递归）
我们需要根据一个文件夹的目录结构生成MkDocs的导航列表（nav）。假设我们有一个docs目录，其中包含了所有的Markdown文件（.md）以及子文件夹。

要求：

1. 导航列表应该反映目录结构，即子文件夹的内容应该嵌套在文件夹名称下。

2. 只包含Markdown文件（.md）和文件夹（如果文件夹中有Markdown文件，则保留该文件夹）。

3. 忽略空文件夹。

4. 忽略非Markdown文件（例如图片等）。

5. 文件夹和文件的顺序可以按照文件系统顺序（或者按名称排序，这里我们按字母顺序排序）。

6. 注意：MkDocs要求nav中的每个条目要么是字符串（表示单个页面），要么是字典（键为标题，值为页面路径或嵌套列表）。

实现思路：

我们可以使用递归函数遍历目录，为每个目录生成一个字典（键为目录名，值为该目录下的文件列表和子目录列表），而文件则直接生成其相对于docs目录的路径（不带扩展名？但是MkDocs要求带扩展名）。

但是注意：MkDocs的nav配置中，页面路径是相对于docs目录的，且需要包含扩展名（除非配置了扩展名隐藏）。另外，文件夹的名称应该作为导航的标题。

步骤：

1. 定义根目录（例如'docs'）。

2. 递归遍历目录，构建嵌套的列表结构。

3. 对于每个目录，先收集所有.md文件（不包括README.md？或者包括，但通常我们可能希望将README.md作为目录的索引页，这里我们按照普通文件处理）。

4. 对于每个子目录，如果非空（包含.md文件或包含.md文件的子目录），则将其作为一个嵌套的字典项。

> 注意：MkDocs要求索引页通常是index.md，但我们的文件可能是任意的。所以这里我们不特别处理索引页，而是按照普通文件处理。

### 使用`ruamel.yaml`库替换原YAML中的nav部分

由于yaml文件中包含自定义的标签（如`!!python/name:...`），为了避免解析问题，我们可以采用以下策略：

1. 使用`ruamel.yaml`库，因为它可以保留注释和自定义标签。

2. 如果我们使用`PyYAML`，需要特别处理自定义标签（但`PyYAML`遇到自定义标签`!!python/name:...`会报错）。

因此，这里我们使用`ruamel.yaml`，因为它能够更好地处理yaml文件的保留格式（包括注释、顺序等）以及自定义标签。

更新 `mkdocs.yml` 文件中的 `nav` 部分步骤：

1. 安装`ruamel.yaml`（如果未安装）：`pip install ruamel.yaml`

2. 读取yaml文件

3. 修改nav部分（替换为一个新的导航结构）

4. 将修改后的内容写回文件

以下是一个完整的 Python 脚本，可以根据文件夹目录结构自动生成 MkDocs 的导航列表（nav），同时保持 YAML 文件中的其他内容不变，并正确处理特殊标签：

```python
import os
import ruamel.yaml
from pathlib import Path
from collections import OrderedDict

def generate_nav_from_directory(docs_dir='docs', ignore_dirs=None):
    """
    根据文件夹目录生成 MkDocs 导航列表
    
    参数:
    docs_dir: MkDocs 文档目录 (默认 'docs')
    ignore_dirs: 要忽略的目录列表
    
    返回:
    嵌套的导航列表结构
    """
    if ignore_dirs is None:
        ignore_dirs = ['.git', '.github', '.vscode', 'assets', 'images', 'js', 'css']
    
    nav = []
    docs_path = Path(docs_dir)
    
    def process_directory(directory, rel_path=''):
        """递归处理目录结构"""
        items = []
        
        # 获取目录下所有条目并排序
        entries = sorted(os.listdir(directory), key=lambda x: x.lower())
        
        # 优先处理索引文件
        index_files = ['index.md', 'README.md']
        for index_file in index_files:
            index_path = directory / index_file
            if index_path.exists() and index_path.is_file():
                # 相对路径处理
                rel_file_path = (rel_path + '/' + index_file).lstrip('/')
                items.append({index_file[:-3]: rel_file_path})
                break
        
        # 处理其他条目
        for entry in entries:
            entry_path = directory / entry
            
            # 跳过忽略目录和隐藏文件
            if entry in ignore_dirs or entry.startswith('.') or entry in index_files:
                continue
                
            # 处理 Markdown 文件
            if entry_path.is_file() and entry.endswith('.md'):
                # 相对路径处理
                rel_file_path = (rel_path + '/' + entry).lstrip('/')
                title = entry[:-3]  # 移除 .md 扩展名
                items.append({title: rel_file_path})
            
            # 处理子目录
            elif entry_path.is_dir():
                # 递归获取子目录内容
                sub_items = process_directory(
                    entry_path, 
                    f"{rel_path}/{entry}" if rel_path else entry
                )
                
                # 只添加包含有效内容的目录
                if sub_items:
                    # 使用目录名作为标题，但可以自定义处理
                    dir_title = entry.replace('_', ' ').title()
                    items.append({dir_title: sub_items})
        
        return items
    
    nav = process_directory(docs_path)
    return nav

def update_mkdocs_nav(yaml_file='mkdocs.yml', new_nav=None):
    """更新 mkdocs.yml 文件中的 nav 部分"""
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    
    # 读取原始 YAML 文件
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.load(f)
    
    # 更新 nav 部分
    if new_nav is not None:
        data['nav'] = new_nav
    
    # 写回修改后的 YAML
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

if __name__ == "__main__":
    # 配置参数
    DOCS_DIR = 'docs'  # MkDocs 文档目录
    MKDOCS_FILE = 'mkdocs.yml'  # MkDocs 配置文件
    
    # 生成导航结构
    nav_structure = generate_nav_from_directory(DOCS_DIR)
    
    print("生成的导航结构:")
    print(nav_structure)
    
    # 更新 mkdocs.yml 文件
    update_mkdocs_nav(MKDOCS_FILE, nav_structure)
    print(f"\n成功更新 {MKDOCS_FILE} 中的导航部分!")
```

### 使用说明

1. **安装依赖**：
   ```bash
   pip install ruamel.yaml
   ```

2. **配置参数**：
   - `DOCS_DIR`: 你的 Markdown 文件存放目录（默认 'docs'）
   - `MKDOCS_FILE`: mkdocs.yml 文件路径（默认 'mkdocs.yml'）

3. **运行脚本**：
   ```bash
   python generate_nav.py
   ```
   使用uv运行：
   ```bash
   uv run generate_nav.py
   ```

### 功能特点

1. **智能目录处理**：
   - 自动识别 `index.md` 和 `README.md` 作为目录入口
   - 忽略常见非内容目录（.git, assets, images 等）
   - 自动跳过隐藏文件和目录
   - 保留原始文件名作为标题，但可自定义格式化

2. **递归目录遍历**：
   - 自动处理任意深度的子目录
   - 生成嵌套的导航结构
   - 空目录自动跳过

3. **特殊字符处理**：
   - 正确处理中文文件名和路径
   - 保留 YAML 特殊标签（如 `!!python/name:`）
   - 保持原始 YAML 文件的格式和注释

4. **自定义选项**：
   - 可配置忽略目录列表
   - 可自定义目录标题格式化规则
   - 可调整排序规则（当前按字母顺序）

### 生成导航示例

假设目录结构如下：
```
docs/
├── index.md
├── 介绍.md
├── 开发指南/
│   ├── 安装.md
│   ├── 配置.md
│   └── 高级技巧.md
└── API参考/
    ├── 核心API.md
    └── 扩展API.md
```

生成的导航结构：
```yaml
nav:
  - index: index.md
  - 介绍: 介绍.md
  - 开发指南:
      - 安装: 开发指南/安装.md
      - 配置: 开发指南/配置.md
      - 高级技巧: 开发指南/高级技巧.md
  - API参考:
      - 核心API: API参考/核心API.md
      - 扩展API: API参考/扩展API.md
```

### 自定义选项

如果需要修改目录标题的显示方式（例如去除数字前缀），可以在 `generate_nav_from_directory` 函数中添加标题处理逻辑：

```python
# 在 process_directory 函数中添加标题处理
def process_directory(directory, rel_path=''):
    # ...
    for entry in entries:
        # ...
        if entry_path.is_file() and entry.endswith('.md'):
            rel_file_path = (rel_path + '/' + entry).lstrip('/')
            title = entry[:-3]
            
            # 自定义标题处理：移除数字前缀
            if ' ' in title:
                title = title.split(' ', 1)[1]
            
            items.append({title: rel_file_path})
        # ...
```

这个脚本会保持原始 YAML 文件中的所有其他配置（包括主题设置、扩展插件、自定义标签等），只更新 `nav` 部分，非常适合自动化文档部署流程。

## github博客生成说明

直接在 GitHub 仓库中通过 [GitHub Actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions) 创建自定义持续部署 (CD) 工作流程，**实现代码提交后自动构建网站**，配置步骤如下：

> workflow是一个可配置的自动化过程，将运行一个或多个作业。workflow由代码仓库中的YAML文件定义，并将在代码仓库中的事件触发时运行，或者可以手动触发。
> workflow在代码仓库的`.github/workflow`目录中定义。一个存储库可以有多个工作流，每个工作流都可以执行一组不同的任务。
> 
> mkdocs 部署到github pages 参考文档：
> https://www.mkdocs.org/user-guide/deploying-your-docs/
> 
1. 在代码仓库的`.github/workflow`目录中定义一个`yaml`文件，内容如下：
```yaml
name: ci 
on:
  push:
    branches:
      - main
permissions:
  contents: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Configure Git Credentials
        run: |
          git config user.name github-actions[bot]
          git config user.email 41898282+github-actions[bot]@users.noreply.github.com
      - uses: actions/setup-python@v5
        with:
          python-version: 3.x
      - run: echo "cache_id=$(date --utc '+%V')" >> $GITHUB_ENV
      - run: pip install pyyaml
      - run: python gen_mkdocs_nav.py
      - uses: actions/cache@v4
        with:
          key: mkdocs-material-${{ env.cache_id }}
          path: .cache 
          restore-keys: |
            mkdocs-material-
      - run: pip install mkdocs-material 
      - run: mkdocs gh-deploy --force

```
