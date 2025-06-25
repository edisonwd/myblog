import os
import ruamel.yaml
from pathlib import Path


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
        ignore_dirs = ['.git', '.github', '.vscode', 'assets', 'images', 'js', 'css', 'javascripts', 'stylesheets']

    docs_path = Path(docs_dir)

    def process_directory(directory, rel_path=''):
        """递归处理目录结构"""
        items = []

        # 获取目录下所有条目并排序
        entries = sorted(os.listdir(directory), key=lambda x: x.lower())

        # 优先处理索引文件
        index_files = ['index.md']
        for index_file in index_files:
            index_path = directory / index_file
            if index_path.exists() and index_path.is_file():
                # 相对路径处理
                rel_file_path = (rel_path + '/' + index_file).lstrip('/')
                items.append({"首页": rel_file_path})
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
