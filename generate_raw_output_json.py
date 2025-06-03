import json
import time
from extract_data import extract_information_fast
from clean_data import DocumentProcessor
from imports import Client
from collections import defaultdict

import json
import re

def deal_response(response):
    try:
        result = json.loads(response)
    except Exception:
        json_str = re.search(r'```json\n([\s\S]*?)\n```', response) 
        if json_str:
            clean_json_str = json_str.group(1)  
            result = json.loads(clean_json_str)
        else:
            raise ValueError("AI输出无法解析为JSON")
    return result


def use_ai_get_mid_output(full_text, client: Client, client_config: dict):

    prompt = (
        "你是医疗培训数据提取专家，请根据原始文档内容严格填充以下JSON模板。要求：\n"
        "\n"
        "### 核心规则\n"
        "1. **原文提取**：仅使用文档中明确存在的信息，禁止编造内容\n"
        "2. **字段保留**：维持所有现有字段名称和结构，无对应内容则留空字符串(\"\")\n"
        "3. **输出格式**：输出待填充JSON模板，不要有任何无关字符。\n"
        "4. **文档类型**：根据文档名判断该文档是否与“考核”、“培训”相关\n"
        "5. **格式规范**：\n"
        "   - 时间格式 → \"YYYY年MM月DD日\" 或 \"YYYY-MM-DD\"\n"
        "   - 百分数 → \"XX.X%\"（如\"92.2%\"）\n"
        "   - 数值 → 保留整数（如\"804\"）或1位小数（如\"37.5\"）\n"
        "   - 时间段 → 带单位（如\"30分钟\"）\n"
        "   - 修饰性定语 → 请保留（如\"全科室医护人员\"）\n"
        "\n"
        "### 待填充JSON模板\n"
        "[\n"
        "  {\n"
        "    \"培训组织概况\": {\n"
        "      \"培训时间\": \"\",\n"
        "      \"培训主题\": \"\",\n"
        "      \"组织部门\": \"\",\n"
        "      \"培训对象\": \"\",\n"
        "      \"授课专家\": \"\",\n"  
        "      \"培训形式\": \"\",\n"
        "      \"培训目的\": \"\",\n"
        "      \"线下培训\": \"\",\n"
        "      \"线上培训\": \"\"\n"
        "    }\n"
        "  },\n"
        "  {\n"
        "    \"培训内容\": {\n"
        "      \"核心模块1\": \"\",\n"
        "      \"核心模块2\": \"\",\n"
        "      \"核心模块3\": \"\",\n"
        "      \"核心模块4\": \"\"\n"
        "    }\n"
        "  },\n"
        "  {\n"
        "    \"培训参与情况和分析\": {\n"
        "      \"应参加人数\": \"\",\n"
        "      \"实际参与人数\": \"\",\n" 
        "      \"覆盖正式护士人次\": \"\",\n" 
        "      \"覆盖实习护士人次\": \"\",\n" 
        "      \"缺勤人数\": \"\",\n"
        "      \"线上参训率\": \"\",\n"
        "      \"线下参训率\": \"\",\n"
        "      \"整体参训率\": \"\",\n"
        "      \"关键岗位及完成率\": \"\",\n"
        "      \"线上课程学习平均用时\": \"\",\n"
        "      \"正确率均值\": \"\",\n"
        "      \"受训者看法\": \"\",\n"
        "      \"存在问题\": \"\",\n"
        "      \"整改措施\": \"\",\n"
        "    }\n"
        "  },\n"
        "  {\n"
        "    \"考核内容\": {\n"
        "      \"考核时间\": \"\",\n"
        "      \"考核地点\": \"\"\n"
        "      \"考核类型\": \"\",\n"
        "      \"考核内容和要求\": \"\"\n"
        "    }\n"
        "  },\n"
        "  {\n"
        "    \"考核结果\": {\n"
        "      \"理论考试参与人数\": \"\",\n"
        "      \"理论考试参考率\": \"\",\n"
        "      \"理论考试平均成绩\": \"\",\n"
        "      \"操作评估合格率\": \"\",\n"
        "      \"最终通过率\": \"\",\n"
        "      \"不及格人数\": \"\",\n"
        "    }\n"
        "  },\n"
        "  {\n"
        "    \"考核问题和分析\": {\n"
        "      \"考核类型及存在问题\": \"\",\n"
        "      \"不及格主要原因\": \"\"\n"
        "      \"整改措施\": \"\",\n"
        "    }\n"
        "  },\n"
        "]\n"
        "\n"
        "### 特殊字段说明\n"
        "- \"培训时间\"：提取连续时间段（如\"2025年5月10日至5月25日\"）\n"
        "- \"参训率/通过率\"：需计算时保留1位小数（如\"92.2%\"）\n"
        "\n"
        "### 原始文档\n"
        f"{full_text}\n"
    )


    # prompt = (
    #     "你是医疗培训数据提取专家，请根据原始文档内容严格为每个章节提取可能的key条目,不需要填充value。要求：\n"
    #     "\n"
    #     "### 核心规则\n"
    #     "1. **原文提取**：仅使用文档中明确存在的信息，禁止编造内容\n"
    #     "2. **字段保留**：维持所有现有字段名称和结构，无对应内容则留空字符串(\"\")\n"
    #     "3. **输出格式**：输出待填充JSON模板，不要有任何无关字符。需要考虑到所有value都是字符串形式，不能有列表。\n"
    #     "4. **考核 or 培训**：请根据文档标题判断这是关于考核还是培训，或者两者都有的文档。\n"
    #     "\n"
    #     "### 待填充JSON模板\n"
    #     "[\n"
    #     "  {\n"
    #     "    \"培训组织概况\": {\n"
    #     "    }\n"
    #     "  },\n"
    #     "  {\n"
    #     "    \"培训内容\": {\n"
    #     "    }\n"
    #     "  },\n"
    #     "  {\n"
    #     "    \"培训参与情况\": {\n"
    #     "    }\n"
    #     "  },\n"
    #     "  {\n"    
    #     "    \"培训分析和问题\": {\n"
    #     "    },\n"
    #     "  {\n"
    #     "    \"考核内容\": {\n"
    #     "    }\n"
    #     "  },\n"
    #     "  {\n"
    #     "    \"考核结果\": {\n"
    #     "    }\n"
    #     "  },\n"
    #     "  {\n"
    #     "    \"考核分析和问题\": {\n"
    #     "    }\n"
    #     "  }\n"
    #     "]\n"
    #     "### 原始文档\n"
    #     f"{full_text}\n"
    # )
    response = client.chat(prompt, **client_config)
    # print(f'response=\n{response}\n-------------------\n')
    result=deal_response(response)
    return result


def parse_output_extract(content):
    file_blocks = re.split(r'====文件名：', content)
    tabel_json = []
    text_data = []

    for block in file_blocks:
        if not block.strip():
            continue
        file_match = re.match(r'([^\n]+)====\n\n信息类型: ([^\n]+)\n内容：(.*)', block, re.DOTALL)
        if not file_match:
            continue
        file_name, info_type, file_content = file_match.groups()
        file_name = file_name.strip()
        info_type = info_type.strip()
        file_content = file_content.strip()

        if info_type.lower() == "table":
            # 提取表名
            table_title = re.sub(r'^.*/', '', file_name).replace('.xlsx', '')
            # 提取sheet名
            sheet_match = re.search(r'Sheet:\s*([^\n]+)', file_content)
            sheet_name = sheet_match.group(1).strip() if sheet_match else "Sheet1"
            # 提取表格内容
            table_lines = file_content.split('\n')
            # 找到表头行
            for idx, line in enumerate(table_lines):
                if line.startswith('科室名称'):
                    header = [h.strip() for h in line.split(',')]
                    data_lines = table_lines[idx+1:]
                    break
            else:
                continue  # 没有表头，跳过

            table_data = []
            for row in data_lines:
                if not row.strip() or row.startswith('合计'):
                    continue
                values = [v.strip() for v in row.split(',')]
                if len(values) != len(header):
                    continue
                row_dict = dict(zip(header, values))
                table_data.append(row_dict)
            tabel_json.append({
                table_title: {
                    f"{sheet_name}": table_data
                }
            })
        else:
            text_data.append(f"====文件名：{file_name}====\n\n信息类型: {info_type}\n内容：{file_content}")

    return tabel_json, text_data

def use_ai_get_conclusion(full_text, client: Client, client_config: dict):
    concluseion_prompt = (
        "你是一个医疗领域的专家，请根据文档信息进行简短总结并给出分点的建议。如果原文档中有总结和建议，请合并\n"
        "### 核心规则\n"
        "1. **总结**：只能使用文字描述，不要太冗长，精炼的概括。\n"
        "2. **建议**：你的建议和原文档中的建议一共保持在2-5条。\n"
        "输出格式：严格使用以下JSON格式：\n"
        "{\n"
        "  \"总结\": \n"
        "  \"建议\": [\n"
        "      \"1、 ...,\"\n"
        "      \"2、 ...,\"\n"
        "      ...\n"
        "   ]\n"
        "}\n"
        "原始文档内容如下：\n"
        f"{full_text}\n"

    )

    response = client.chat(concluseion_prompt, **client_config)
    # print(response)
    result=deal_response(response)
    with open('conclusion.json','w',encoding='utf=8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)


if __name__ == "__main__":
    start_time=time.time()
    processor = DocumentProcessor()
    processor.process_file("./data/2025年5月护理部理论知识培训.docx")
    # processor.process_file("./data/2025年5月手卫生执行专项培训与评估总结.pdf")
    # processor.process_file("./data/手卫生培训各科室参与与考核情况统计.xlsx")
    user_prompt =  "生成护理部理论知识培训报告"
    # user_prompt = "生成5月手卫生培训与专项考核报告"
    extract_data = extract_information_fast(processor.get_data(), user_prompt, threshold=0.3)

    api_key="your-api-key"
    base_url="https://api.deepseek.com"
    client = Client(api_key, base_url)
    client_config = {"model": "deepseek-chat"}


    # 提取并处理表格
    table_data,full_text= parse_output_extract(extract_data)

    raw_output = use_ai_get_mid_output(full_text, client, client_config)
    
    raw_output.extend(table_data)
    with open('raw_output_word.json','w',encoding='utf-8') as f:
        json.dump(raw_output,f,ensure_ascii=False,indent=2)
    # ai生成总结和建议
    use_ai_get_conclusion(extract_data, client, client_config)

    end_time=time.time()
    running_time=end_time-start_time
    print(f"build raw output using {running_time:.2f}s.")

