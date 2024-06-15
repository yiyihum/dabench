import os
import json
import pandas as pd
import re

def clean_action_detail(detail):
    # 确认 detail 是字符串类型, 如果不是则转换为字符串
    if not isinstance(detail, str):
        detail = str(detail)
    # 使用正则表达式去掉没有含义的信息
    cleaned_detail = re.sub(r'[\\"]|\n', '', detail)
    return cleaned_detail

# 定义目录路径
input_dir = 'dabench\\benchmark\\results'
output_dir = 'dabench\\benchmark\\results\\results_analysis'

# 如果输出目录不存在，则创建
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 遍历 results 目录下的所有 JSON 文件
for filename in os.listdir(input_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(input_dir, filename)
        
        # 读取 JSON 文件
        with open(filepath, 'r') as file:
            data = json.load(file)

        # 初始化结果字典
        results_dict = {}

        # 遍历每一个example
        for example in data['results']:
            example_id = example['id']
            actions = example['actions']
            previous_action = None  # 存储前一个操作的类型
            
            # 初始化当前ID的步骤列表
            steps = []
            
            for action in actions:
                action_type = action[0]
                action_detail = clean_action_detail(action[1])  # 使用清理函数过滤不合理的字符
                action_result = action[2]

                if action_type == "Bash":
                    # 先拆分 '|'和'&&' 前后的部分
                    parts = re.split(r'\|\||&&', action_detail)

                    # 创建一个空列表来存储每个部分的第一个单词
                    commands = []
                    unique_commands = set()  # 使用集合来追踪已添加的单词

                    # 遍历每个部分，提取第一个单词
                    for part in parts:
                        words = part.strip().split()
                        if len(words) > 0:
                            first_word = words[0]
                        else:
                            first_word = part.strip()

                        # 确保非空且不重复
                        if first_word and first_word not in unique_commands:
                            commands.append(first_word)
                            unique_commands.add(first_word)

                    # 用 '+' 连接所有的第一个单词组成最终的command
                    command = '+'.join(commands)

                    if previous_action is not None and previous_action[0] == "Bash" and previous_action[2] == "error message":
                        step = f"Bash-debug-{command}"
                    else:
                        step = f"Bash-new-{command}"

                elif action_type == "Python":
                    if previous_action is None or previous_action[0] != "Python":
                        step = "Python-new"
                    elif previous_action[0] == "Python" and previous_action[2] == "error message":
                        step = "Python-debug"
                    elif previous_action[0] == "Python" and action_result != "execution succeeded":
                        step = "Python-new"
                    else:
                        step = "Python"
                        
                elif action_type == "SQL":
                    # 尝试对 command 进行分割
                    command_parts = action_detail.split()

                    # 如果能够分割并且分割后有多个部分，则取第一个部分，否则保存完整 command
                    if len(command_parts) > 1:
                        command = command_parts[0]
                    else:
                        command = action_detail

                    if previous_action is None or previous_action[0] != "SQL":
                        step = f"SQL-new-{command}"
                    elif previous_action[0] == "SQL" and previous_action[2] != "error message":
                        step = f"SQL-new-{command}"
                    elif previous_action[0] == "SQL" and previous_action[2] == "error message":
                        step = f"SQL-debug-{command}"
                    else:
                        step = "SQL"
                elif action_result == "action parse failed":
                    step = "failParse"
                else:
                    step = action_type  # 其他类型保持原样
                
                # 将步骤添加到当前ID的步骤列表
                steps.append(step)
                
                # 更新前一步操作
                previous_action = action
            
            # 将ID和步骤列表添加到结果字典
            results_dict[example_id] = steps

        # 构建DataFrame
        df = pd.DataFrame.from_dict(results_dict, orient='index')

        # 写入步骤统计结果到CSV文件
        base_filename = os.path.splitext(filename)[0]
        output_filename = base_filename.replace('results', 'actions') + '_actions.csv'
        output_filepath = os.path.join(output_dir, output_filename)
            
        df.to_csv(output_filepath, index=True)

        print(f"Processed {filepath} and saved to {output_filepath}")

import os
import pandas as pd

# 定义目录路径
input_dir = 'dabench\\benchmark\\results\\results_analysis'

# 遍历文件夹下所有的CSV文件
for filename in os.listdir(input_dir):
    if filename.endswith('.csv'):
        filepath = os.path.join(input_dir, filename)
        print(f"Found CSV file: {filepath}")

        # 读取 CSV 文件
        df = pd.read_csv(filepath)

        # 定义清洗函数
        def clean_text(text):
            if pd.notnull(text):
                
                # 删除 ';' 及其之后的部分
                if ';' in text:
                    text = text.split(';')[0]
                # 删除 ')' 及其之后的部分
                if ')' in text:
                    text = text.split(')')[0]
                # 删除所有的单引号
                text = text.replace("'", "")
            return text

        # 应用清洗函数到每一个步骤列，跳过第一列 (id)  *)
        for col in df.columns[1:]:  
            df[col] = df[col].apply(clean_text)

        # 将清洗后的数据保存回源文件
        df.to_csv(filepath, index=False)

        print(f"Processed {filepath} and saved changes back to the source file")