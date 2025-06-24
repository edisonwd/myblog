# myblog
记录一些学习笔记

## 前言

> 纸上得来终觉浅，绝知此事要躬行

在网上看到很多大佬的优秀博客，从他们的文章中学到了很多，特别是看到博主的自我介绍以及博文列表，不得不称赞“真的太优秀了”，想到了那句：比你优秀的人比你还努力，难免产生焦虑情绪，但是对于有积极心理的人，也许就不能称之为焦虑，而是打了一针鸡血。就目前对我来说还是比较积极的，依然对技术还保持着热情，所以心里默默对自己说：应该向这些优秀的大佬学习，养成写博客的习惯，将自己学习的知识记录下来。

说实话就个人而言并不擅长写文章，是那种高考作文都写不满 800 字的人，不期待自己能写出多么优秀的文章，只希望尽自己最大的努力将写的内容尽可能描述清楚。


## 博客生成说明

本博客使用 [MkDocs](https://github.com/mkdocs/mkdocs) 生成
> MkDocs是一个快速、简单、华丽的静态站点生成器，用于构建项目留档。文档源文件是用Markdown编写的，并使用单个YAML配置文件进行配置。它旨在易于使用，可以通过第三方主题、插件和Markdown扩展进行扩展。
>

直接在 GitHub 仓库中通过 [GitHub Actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions) 创建自定义持续部署 (CD) 工作流程，**实现代码提交后自动构建网站**，配置步骤如下：

> workflow是一个可配置的自动化过程，将运行一个或多个作业。workflow由代码仓库中的YAML文件定义，并将在代码仓库中的事件触发时运行，或者可以手动触发。
> workflow在代码仓库的`.github/workflow`目录中定义。一个存储库可以有多个工作流，每个工作流都可以执行一组不同的任务。


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

2. 为了自动根据代码的目录结构生成mkdocs中的导航目录结构，定义了一个 python 文件 `gen_mkdocs_nav.py` 代码如下：
```python
import yaml
from pathlib import Path


ignore_path = ['image']

def generate_nav_structure_recursive(path: Path, indent_level: int=0):
    nav_structure = ""
    indent = "  " * indent_level

    for file_path in path.iterdir():
        if file_path.name in ignore_path:
            continue
        if file_path.is_dir():
            # 判断文件夹是否为空
            if not any(file_path.iterdir()):
                print(f"跳过空文件夹: {file_path.name}")
                continue
            nav_structure += f"{indent}- {file_path.name}:\n"
            nav_structure += generate_nav_structure_recursive(file_path, indent_level + 1)
        elif file_path.is_file():
            # 获取文件相对于基础目录的相对路径
            relative_path = file_path.relative_to(directory)
            if file_path.name == 'index.md':
                nav_structure += f"{indent}- 首页: {relative_path}\n"
            else:
                nav_structure += f"{indent}- {relative_path}\n"

    return nav_structure

def generate_nav_structure(directory: str):
    root_path = Path(directory)
    return generate_nav_structure_recursive(root_path, 1)



def update_yaml_file(file_path, target_key, new_value):
    """
    读取YAML文件，替换指定键的值，并覆盖原文件
    :param file_path: YAML文件路径
    :param target_key: 需要替换的键名
    :param new_value: 新的值
    """
    # 读取YAML文件
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)  # 安全加载避免潜在风险

    # 修改值
    data[target_key] = new_value
    
    # 覆盖写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True, sort_keys=False)



def yaml_to_dict(yaml_str: str) -> dict:
    """
    将YAML字符串转换为Python字典
    :param yaml_str: 符合YAML格式的字符串
    :return: 转换后的字典对象
    """
    try:
        return yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        raise ValueError(f"YAML解析失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"转换发生意外错误: {str(e)}")


def move_with_order(lst, target_order):
    # 按 target_order 的顺序收集元素
    moved = []
    for target in target_order:
        moved.extend([x for x in lst if isinstance(x, dict) and x.get(target)])
    # 剩余元素保持原顺序
    remaining = [x for x in lst if x not in moved]
    return moved + remaining


# 示例目录
directory = "./docs"
nav_structure = generate_nav_structure(directory)

nav_list = yaml_to_dict(nav_structure)
# 首页放在列表开头
nav_list = move_with_order(nav_list, ['首页'])
# 更新导航
update_yaml_file('./mkdocs.yml', 'nav', nav_list)
print('更新导航成功')
```
