import json
import jieba.analyse
import spacy
import hanlp
import time
from extract_data import extract_information_fast
from clean_data import DocumentProcessor
from imports import Client

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
    # prompt = (
    #     "你是数据提取助手。请根据下列原始文档内容，严格按照以下JSON模板填充数据，并满足以下要求：\n"
    #     "\n"
    #     "1. 数据提取规则：\n"
    #     "   - 只能提取原文中明确存在的信息，禁止自行生成内容\n"
    #     "   - 若字段无对应内容则保持空值（\"\"）\n"
    #     "   - 时间格式统一为\"YYYY-MM-DD\"\n"
    #     "   - 百分比统一为\"XX%\"\n"
    #     "   - 数值保留两位小数（如\"85.50\"）\n"
    #     "\n"
    #     "2. 格式要求：\n"
    #     "   - 严格保持提供的JSON结构，不得修改字段名称和层级\n"
    #     "   - 所有字符串值必须用双引号包裹\n"
    #     "   - 遇到表格数据保持原格式：(sheet)文件名/\n内容(/sheet)\n"
    #     "\n"
    #     "3. 特殊字段处理：\n"
    #     "   - \"培训时间\"：提取原文中的时间段或日期\n"
    #     "   - \"组织者\"：提取主办单位/部门名称\n"
    #     "   - \"参考率\"：计算为\"实际参考人数/应考人数\"\n"
    #     "   - \"存在问题\"：只提取具体描述\n"
    #     "\n"
    #     "4. 输出要求：\n"
    #     "   - 返回完整填充后的JSON\n"
    #     "\n"
    #     "待填充的JSON模板：\n"
    #     "{\n"
    #     "  \"orgOverview\": {\n"
    #     "    \"section\": \"培训组织概况\",\n"
    #     "    \"fields\": [\n"
    #     "      {\"label\": \"培训时间\", \"value\": \"\"},\n"
    #     "      {\"label\": \"培训主题\", \"value\": \"\"},\n"
    #     "      {\"label\": \"组织者\", \"value\": \"\"},\n"
    #     "      {\"label\": \"参与人\", \"value\": \"\"},\n"
    #     "      {\"label\": \"培训形式\", \"value\": \"\"},\n"
    #     "      {\"label\": \"培训目的\", \"value\": \"\"},\n"
    #     "      {\"label\": \"线下集中授课\", \"value\": \"\"},\n"
    #     "      {\"label\": \"线上打卡学习\", \"value\": \"\"}\n"
    #     "    ]\n"
    #     "  },\n"
    #     "  \"trainingContent\": [\n"
    #     "    {\n"
    #     "      \"item\": {\n"
    #     "        \"contents\": [\n"
    #     "          {\"text\": \"培训内容包含以下四大核心模块：\"}\n"
    #     "        ]\n"
    #     "      },\n"
    #     "      \"level\": 0\n"
    #     "    },\n"
    #     "    {\n"
    #     "      \"item\": {\n"
    #     "        \"contents\": [\n"
    #     "          {\"text\": \"\"}\n"
    #     "        ]\n"
    #     "      },\n"
    #     "      \"level\": 1\n"
    #     "    },\n"
    #     "    {\n"
    #     "      \"item\": {\n"
    #     "        \"contents\": [\n"
    #     "          {\"text\": \"\"}\n"
    #     "        ]\n"
    #     "      },\n"
    #     "      \"level\": 1\n"
    #     "    },\n"
    #     "    {\n"
    #     "      \"item\": {\n"
    #     "        \"contents\": [\n"
    #     "          {\"text\": \"\"}\n"
    #     "        ]\n"
    #     "      },\n"
    #     "      \"level\": 1\n"
    #     "    },\n"
    #     "    {\n"
    #     "      \"item\": {\n"
    #     "        \"contents\": [\n"
    #     "          {\"text\": \"\"}\n"
    #     "        ]\n"
    #     "      },\n"
    #     "      \"level\": 1\n"
    #     "    }\n"
    #     "  ],\n"
    #     "  \"trainingParticipation\": {\n"
    #     "    \"section\": \"培训参与情况\",\n"
    #     "    \"fields\": [\n"
    #     "      {\"label\": \"应参加培训人员总计\", \"value\": \"\"},\n"
    #     "      {\"label\": \"实际参与人数\", \"value\": \"\"},\n"
    #     "      {\"label\": \"缺勤人数\", \"value\": \"\"},\n"
    #     "      {\"label\": \"整体参训率\", \"value\": \"\"},\n"
    #     "      {\"label\": \"关键岗位及完成率\", \"value\": \"\"},\n"
    #     "      {\"label\": \"未完成学习任务部门\", \"value\": \"\"},\n"
    #     "      {\"label\": \"线上课程学习平均用时\", \"value\": \"\"},\n"
    #     "      {\"label\": \"正确率均值\", \"value\": \"\"}\n"
    #     "    ]\n"
    #     "  },\n"
    #     "  \"assessmentDetail\": {\n"
    #     "    \"section\": \"考核内容\",\n"
    #     "    \"fields\": [\n"
    #     "      {\"label\": \"理论考试\", \"value\": \"\"},\n"
    #     "      {\"label\": \"现场操作考核\", \"value\": \"\"}\n"
    #     "    ]\n"
    #     "  },\n"
    #     "  \"assessmentChart\": {\n"
    #     "    \"section\": \"考核结果\",\n"
    #     "    \"metrics\": [\n"
    #     "      {\"label\": \"理论考试参与人数\", \"value\": \"\"},\n"
    #     "      {\"label\": \"参考率\", \"value\": \"\"},\n"
    #     "      {\"label\": \"理论考试平均成绩\", \"value\": \"\"},\n"
    #     "      {\"label\": \"操作评估合格率\", \"value\": \"\"},\n"
    #     "      {\"label\": \"操作评估存在问题\", \"value\": \"\"},\n"
    #     "      {\"label\": \"最终通过率\", \"value\": \"\"},\n"
    #     "      {\"label\": \"不及格人数\", \"value\": \"\"},\n"
    #     "      {\"label\": \"不及格主要原因\", \"value\": \"\"}\n"
    #     "    ]\n"
    #     "  },\n"
    #     "  \"assessmentAnalysis\": {\n"
    #     "    \"section\": \"考核情况分析（鱼骨图）\",\n"
    #     "    \"mainProblem\": \"\",\n"
    #     "    \"causes\": [\n"
    #     "      {\n"
    #     "        \"category\": \"操作评估存在问题\",\n"
    #     "        \"details\": [\"问题1\", \"问题2\"]\n"
    #     "      },\n"
    #     "      {\n"
    #     "        \"category\": \"不及格主要原因\",\n"
    #     "        \"details\": [\"\"]\n"
    #     "      }\n"
    #     "    ]\n"
    #     "  },\n"
    #     "  \"rectificationFlow\": {\n"
    #     "    \"section\": \"总结与建议\",\n"
    #     "    \"steps\": []\n"
    #     "  }\n"
    #     "}\n"
    #     "\n"
    #     "原始文档内容如下：\n"
    #     f"{full_text}\n"
    # )

    prompt = (
        "你是医疗培训数据提取专家，请根据原始文档内容严格填充以下JSON模板。要求：\n"
        "\n"
        "### 核心规则\n"
        "1. **原文提取**：仅使用文档中明确存在的信息，禁止编造内容\n"
        "2. **字段保留**：维持所有现有字段名称和结构，无对应内容则留空字符串(\"\")\n"
        "3. **输出格式**：输出待填充JSON模板，不要有任何无关字符。\n"
        "4. **格式规范**：\n"
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
        "      \"组织者\": \"\",\n"
        "      \"参与人\": \"\",\n"
        "      \"培训形式\": \"\",\n"
        "      \"培训目的\": \"\",\n"
        "      \"线下集中授课\": \"\",\n"
        "      \"线上打卡学习\": \"\"\n"
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
        "    \"培训参与情况\": {\n"
        "      \"应参加培训人员总计\": \"\",\n"
        "      \"实际参与人数\": \"\",\n"
        "      \"缺勤人数\": \"\",\n"
        "      \"整体参训率\": \"\",\n"
        "      \"关键岗位及完成率\": \"\",\n"
        "      \"未完成学习任务部门\": \"\",\n"
        "      \"未完成学习原因\": \"\",\n"   
        "      \"线上课程学习平均用时\": \"\",\n"
        "      \"正确率均值\": \"\"\n"
        "    }\n"
        "  },\n"
        "  {\n"
        "    \"考核内容\": {\n"
        "      \"理论考试\": \"\",\n"
        "      \"现场操作考核\": \"\"\n"
        "    }\n"
        "  },\n"
        "  {\n"
        "    \"考核结果\": {\n"
        "      \"理论考试参与人数\": \"\",\n"
        "      \"参考率\": \"\",\n"
        "      \"理论考试平均成绩\": \"\",\n"
        "      \"操作评估合格率\": \"\",\n"
        "      \"操作评估存在问题\": \"\",\n"
        "      \"最终通过率\": \"\",\n"
        "      \"不及格人数\": \"\",\n"
        "      \"不及格主要原因\": \"\"\n"
        "    }\n"
        "  },\n"
        "  {\n"
        "    \"考核分析\": {\n"
        "      \"最终通过率\": \"\",\n"
        "      \"不及格人数\": \"\",\n"
        "      \"主要问题\": \"\"\n"
        "    }\n"
        "  },\n"
        "  {\n"
        "    \"总结与建议\": {}\n"
        "  },\n"
        "  {\n"
        "    \"手卫生培训各科室参与与考核情况统计\": {\n"
        "      \"Sheet1\": [\n"
        "        {\n"
        "          \"科室名称\": \"\",\n"
        "          \"应参训人数\": \"\",\n"
        "          \"实参训人数\": \"\",\n"
        "          \"缺勤人数\": \"\",\n"
        "          \"参训率\": \"\",\n"
        "          \"理论考试参考人数\": \"\",\n"
        "          \"理论通过人数\": \"\",\n"
        "          \"操作考核通过人数\": \"\",\n"
        "          \"总体通过率\": \"\"\n"
        "        }\n"
        "      ]\n"
        "    }\n"
        "  }\n"
        "]\n"
        "\n"
        "### 特殊字段说明\n"
        "- \"培训时间\"：提取连续时间段（如\"2025年5月10日至5月25日\"）\n"
        "- \"参训率/通过率\"：需计算时保留1位小数（如\"92.2%\"）\n"
        "- \"Sheet1\"：表格数据按科室逐行填充，科室顺序保持原文顺序\n"
        "\n"
        "### 原始文档\n"
        f"{full_text}\n"
    )
    response = client.chat(prompt, **client_config)
    print(response)
    result=deal_response(response)
    

    with open('raw_output2.json','w',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)


def use_ai_get_conclusion(full_text, client: Client, client_config: dict):
    concluseion_prompt = (
        "你是一个医疗领域的专家，请根据文档信息进行简短总结并给出分点的建议。\n"
        "\n"
        "章节划分： 划分为培训组织概况（培训时间、培训类型、组织者、参与人、时间、地点、主题、目的等），培训内容（方针，总体形式，具体条目），培训参与情况(培训内容完成情况、出勤、效果)，考核内容（具体条目、总体方向、标准），考核结果（参与情况、成绩），考核分析（问题、原因），总结与建议（活动总结、后续安排、活动意义、效果、活动不足）这7个章节。如果没有则空缺\n"
        "如果遇到.xlxs文件(或者信息类型为table)，则以这样的格式输出：(sheet)文件名/\n内容(/sheet)"
        "输出格式：严格使用以下JSON格式：\n"
        "{\n"
        "  \"总结\": \n"
        "  \"建议\": [\n"
        "      1、 ...,\n"
        "      2、 ...,\n"
        "      ...\n"
        "   ]\n"
        "}\n"
        "\n"
        "原始文档内容如下：\n"
        f"{full_text}\n"
    )

    response = client.chat(concluseion_prompt, **client_config)
    result=deal_response(response)
    # print(result)
    with open('conclusion.json','w',encoding='utf=8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)


if __name__ == "__main__":
    start_time=time.time()
    processor = DocumentProcessor()
    processor.process_file("./data/2025年5月护理部理论知识培训.docx")
    processor.process_file("./data/2025年5月手卫生执行专项培训与评估总结.pdf")
    processor.process_file("./data/手卫生培训各科室参与与考核情况统计.xlsx")
    user_prompt =  "生成手卫生培训考核方式报告"
    extract_data = extract_information_fast(processor.get_data(), user_prompt, threshold=0.3)

    api_key="your-api-key"
    base_url="https://api.deepseek.com"
    client = Client(api_key, base_url)
    client_config = {"model": "deepseek-chat"}

    full_text = extract_data

    sections = use_ai_get_mid_output(full_text, client, client_config)
    use_ai_get_conclusion(full_text, client, client_config)

    end_time=time.time()
    running_time=end_time-start_time
    print(f"build raw output using {running_time:.2f}s.")

