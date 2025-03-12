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
directory = ".\\docs"
nav_structure = generate_nav_structure(directory)

nav_list = yaml_to_dict(nav_structure)
# 首页放在列表开头
nav_list = move_with_order(nav_list, ['首页'])
# 更新导航
update_yaml_file('.\\mkdocs.yml', 'nav', nav_list)
print('更新导航成功')
