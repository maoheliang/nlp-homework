import json
import jieba.analyse
import spacy
import hanlp
import time
# from transformers import pipeline
from extract_data import extract_information_fast
from clean_data import DocumentProcessor
from imports import Client

def deal_response(response):
    try:
        result = json.loads(response)

    except Exception:
        import re
        json_str = re.search(r'\{[\s\S]*\}', response)
        if json_str:
            result = json.loads(json_str.group())
        else:
            raise ValueError("AI输出无法解析为JSON")
    return result 

def use_ai_get_raw_output(full_text, client: Client, client_config: dict):
    prompt = (
        "你是报告自动生成助手。请根据下列原始文档内容，自动划分合理的章节结构，并满足以下要求：\n"
        "\n"
        "章节划分： 划分为培训组织概况（培训时间、培训类型、组织者、参与人、时间、地点、主题、目的等），培训内容（方针，总体形式，具体条目），培训参与情况(培训内容完成情况、出勤、效果)，考核内容（具体条目、总体方向、标准），考核结果（参与情况、成绩），考核分析（问题、原因），总结与建议（活动总结、后续安排、活动意义、效果、活动不足）这7个章节。如果没有则空缺\n"
        "如果遇到.xlxs文件(或者信息类型为table)，则以这样的格式输出：(sheet)文件名/\n内容(/sheet)"
        "输出格式：严格使用以下JSON格式：\n"
        "{\n"
        "  \"sections\": [\n"
        "    {\n"
        "      \"培训组织概况\":"
        "       {\n"
        "        \"context\":\"原文片段\""
        "       }\n" 
        "    },\n"
        "...\n"
        "  ]\n"
        "}\n"
        "\n"
        "原始文档内容如下：\n"
        f"{full_text}\n"
    )

    response = client.chat(prompt, **client_config)
    result=deal_response(response)

    # with open('output_ai.json','r') as f:
    #     result=json.load(f)
    ner_result=[]
    for section in result["sections"]:
        title=list(section.keys())[0]
        text=section[title]['context']
        ner_prompt = (
            "你是构建文档字典的助手。请根据下列原始文档内容，自动构建文档信息字典，并满足以下要求：\n"
            "\n"
            "提示:章节内容大概为,注意：这只是参考可以自行修改和增删！！！培训组织概况（培训时间、培训类型、组织者、参与人、时间、地点、主题、目的等），培训内容（总体形式，具体条目），培训参与情况(培训内容完成情况、出勤、效果)，考核 内容（具体条目、总体方向、标准），考核结果（参与情况、成绩），考核分析（问题、原因），总结与建议（活动总结、后续安排、活动意义、效果、活动不足）这些章节。如果 没有则空缺\n"
            "示例：培训时间：2025年3月1日；及格率：66%(key:value形式)"
            "如果遇到表格（格式为(sheet)...(/sheet)），无需添加其他内容，按照文件名和行组织即可"
            "输出格式：严格使用以下JSON格式：\n"
            "{\n"
            "  \"sections\": [\n"
            "    {\n"
            "      \"培训组织概况\":"
            "       {\n"
            "        \"key\":\"value\""
            "        \"key\":\"value\""
            "       }\n" 
            "    },\n"
            "...\n"
            "  ]\n"
            "}\n"
            "\n"
            f"章节为：{title}\n"
            "原始文档内容如下：\n"
            f"{text}\n"
        )
        response = client.chat(ner_prompt, **client_config)
        result=deal_response(response)
        # print(result['sections'])
        for res in result['sections']:
            ner_result.append(res)
    with open('raw_output(1）.json','w',encoding='utf-8') as f:
        json.dump(ner_result,f,ensure_ascii=False,indent=2)


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

    sections = use_ai_get_raw_output(full_text, client, client_config)
    use_ai_get_conclusion(full_text, client, client_config)

    end_time=time.time()
    running_time=end_time-start_time
    print(f"build raw output using {running_time:.2f}s.")

