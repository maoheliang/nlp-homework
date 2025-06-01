import json
import re
from typing import List, Dict


def try_parse(val: str):
    """转换数值字符串为 float/int，否则返回原始字符串"""
    try:
        val = val.replace("%", "")
        if "." in val:
            return float(val)
        return int(val)
    except:
        return val.strip()


def process_intro_text(raw_text: str) -> Dict:
    """处理“培训概述与组织情况”的 original_text 为嵌套结构"""
    first_paragraph = raw_text.strip().split("\n")[0]

    summary_text = ""
    form_text = ""
    target_text = ""

    date_match = re.search(r"(\d{4}年\d{1,2}月)", first_paragraph)
    topic_match = re.search(r"开展了[“\"]?(.*?)[”\"]?专项培训", first_paragraph)
    if date_match and topic_match:
        summary_text = f"{date_match.group(1)} {topic_match.group(1)}专项培训 总览"

    form_match = re.search(r"培训形式为[“\"]?(.*?)[”\"]?[，。]", first_paragraph)
    if form_match:
        form_text = f"形式：{form_match.group(1).strip()}"

    target_match = re.search(r"面向(.*?人员)[，。]", first_paragraph)
    if target_match:
        target_text = f"对象：{target_match.group(1).strip()}"

    intro_contents = []
    if summary_text:
        intro_contents.append({"text": summary_text})
    if form_text:
        intro_contents.append({"text": form_text})
    if target_text:
        intro_contents.append({"text": target_text})

    structured = {"items": []}

    if intro_contents:
        structured["items"].append({
            "level": 0,
            "item": {"contents": intro_contents}
        })

    structured["items"].append({
        "level": 0,
        "item": {"contents": [{"text": "四大核心模块"}]}
    })

    module_matches = re.findall(r"•\s*(.*?)；", raw_text)
    for module in module_matches:
        structured["items"].append({
            "level": 1,
            "item": {"contents": [{"text": module.strip()}]}
        })

    structured["items"].append({
        "level": 0,
        "item": {"contents": [{"text": "培训组织与参训情况"}]}
    })

    time_match = re.search(r"培训时间安排为\s*([0-9年月日至]+)", raw_text)
    if time_match:
        structured["items"].append({
            "level": 1,
            "item": {"contents": [{"text": f"时间：{time_match.group(1).strip()}"}]}
        })

    if "培训组织与参训情况：" in raw_text:
        logistics_matches = re.findall(r"•\s*(.*?)；", raw_text.split("培训组织与参训情况：")[-1])
        for item in logistics_matches:
            structured["items"].append({
                "level": 1,
                "item": {"contents": [{"text": item.strip()}]}
            })

    return structured


def process_training_text(text: str) -> Dict:
    """处理“考核与评估结果”的 original_text 为鱼骨结构"""
    fishbone = {
        "effect": "培训考核情况分析",
        "causes": []
    }

    people_details = []
    match = re.search(r"参考率[:：]([\d.]+)%", text)
    if match:
        rate = float(match.group(1))
        people_details.append(f"参与率为{rate}%")
        if rate < 100:
            people_details.append("参与率未达到100%")
    if people_details:
        fishbone["causes"].append({
            "category": "人",
            "details": people_details
        })

    material_details = []
    problem_match = re.search(r"存在部分(“.*?”(?:“.*?”)*)等问题", text)
    if problem_match:
        material_details.append(f"存在{problem_match.group(1)}等问题")
    if material_details:
        fishbone["causes"].append({
            "category": "料",
            "details": material_details
        })

    method_details = []
    if "流程遗漏" in text or "动作不规范" in text:
        method_details.append("流程遗漏或动作不规范")
    if method_details:
        fishbone["causes"].append({
            "category": "法",
            "details": method_details
        })

    return fishbone


def table_to_json_columns(table_data):
    headers = table_data[0].split(",")
    rows = [row.split(",") for row in table_data[1:]]
    columns = list(zip(*rows))
    result = {}
    for i in range(1, len(headers)):
        column_key = f"col_{i}"
        original_name = headers[i].strip()
        result[column_key] = {
            "unit": "人" if "人数" in original_name or "人次" in original_name else "%",
            "name": original_name,
            "data": [{"name": columns[0][j].strip(), "value": try_parse(columns[i][j])}
                     for j in range(len(columns[i]))]
        }
    return result


def convert_raw_json(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    output_json = {}

    for entry in raw_data:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        original_text = entry.get("original_text", "")

        if title == "培训概述与组织情况":
            output_json["text"] = {
                "summary": summary,
                "testingingcontent": process_intro_text(original_text)
            }

        elif title == "考核与评估结果":
            output_json["trainingresult"] = {
                "request": summary,
                "items": entry.get("items", []),
                "trainingcontent": process_training_text(original_text)
            }

        elif title == "各科室参与与考核情况":
            table_lines = [line.strip() for line in original_text.split("\n") if line.strip()]
            table_rows = table_lines[1:]  # 跳过第一行
            output_json.update(table_to_json_columns(table_rows))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, ensure_ascii=False, indent=2)


# === 示例运行 ===
input_file = "raw_output.json"
output_file = "mid_output_from_raw.json"
convert_raw_json(input_file, output_file)


