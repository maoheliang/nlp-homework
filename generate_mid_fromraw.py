import json

# ========== 读取原始 JSON ========== #
with open("C:\\A课程作业\\nlp\\nlp-homework-main\\input\\1_raw_add_reason\\raw_output_word.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

output_json = {}

# ========== 1. 培训组织概况 ========== #
org_info = raw_data[0]["培训组织概况"]
output_json["orgOverview"] = {
    "section": "培训组织概况",
    "fields": [{"label": k, "value": v} for k, v in org_info.items()]
}

# ========== 2. 培训内容 → 嵌套结构 ========== #
content_items = raw_data[1]["培训内容"]
nested_content = [
    {
        "item": {
            "contents": [{"text": "培训内容包含以下四大核心模块："}]
        },
        "level": 0
    }
]
for v in content_items.values():
    nested_content.append({
        "item": {
            "contents": [{"text": f"• {v}；"}]
        },
        "level": 1
    })
output_json["trainingContent"] = nested_content

# ========== 3. 培训参与情况 ========== #
participation_info = raw_data[2]["培训参与情况和分析"]
output_json["trainingParticipation"] = {
    "section": "培训参与情况和分析",
    "fields": [{"label": k, "value": v} for k, v in participation_info.items()]
}

# ========== 4. 考核内容、结果、自动分析 ========== #
assessment_detail = raw_data[3]["考核内容"]
assessment_result = raw_data[4]["考核结果"]
assessment_analysis = raw_data[5]["考核问题和分析"]

output_json["assessmentDetail"] = {
    "section": "考核内容",
    "fields": [{"label": k, "value": v} for k, v in assessment_detail.items()]
}

output_json["assessmentChart"] = {
    "section": "考核结果",
    "metrics": [{"label": k, "value": v} for k, v in assessment_result.items()]
}


# ========== 4+. 考核情况分析（鱼骨图） ========== #
# 自动从多个字段中提取“存在问题”->“总结” 和 “原因分析” → 鱼骨图结构
def extract_fishbone_components(*sections):
    main_problem_parts = []  # 存放两个总结拼接
    causes = []

    for section in sections:
        if not isinstance(section, dict):
            continue

        # 收集“存在问题”中的“总结”
        problem_dict = section.get("存在问题", {})
        if isinstance(problem_dict, dict):
            summary = problem_dict.get("总结", "").strip()
            if summary:
                main_problem_parts.append(summary)

        # 收集“原因分析”部分
        reasons = section.get("原因分析", {})
        if isinstance(reasons, dict):
            for cat, detail in reasons.items():
                detail_list = detail if isinstance(detail, list) else [detail]
                causes.append({
                    "category": cat,
                    "details": [d.strip() for d in detail_list if isinstance(d, str) and d.strip()]
                })

    return {
        "section": "培训及考核情况分析（鱼骨图）",
        "mainProblem": "；".join(main_problem_parts),
        "causes": causes
    }

# 示例调用（你应该在你的主函数里使用这一句）
output_json["assessmentAnalysis"] = extract_fishbone_components(
    raw_data[2].get("培训参与情况和分析", {}),
    raw_data[5].get("考核问题和分析", {})
)

# ========== 5. 各科室参与与考核统计 Sheet 拆分 ========== #
if len(raw_data) > 6 and "手卫生培训各科室参与与考核情况统计" in raw_data[6]:
    sheet_info = raw_data[6]["手卫生培训各科室参与与考核情况统计"]
    if "Sheet1" in sheet_info:
        sheet_data = sheet_info["Sheet1"]

        columns = [key for key in sheet_data[0].keys() if key != "科室名称"]
        for i, field in enumerate(columns):
            col_key = f"col_{i+1}"
            unit = "%" if any("率" in field or "%" in str(row.get(field, "")) for row in sheet_data) else "人"
            data_list = []
            for row in sheet_data:
                if row["科室名称"] == "合计":
                    continue
                raw_value = row.get(field, "")
                if isinstance(raw_value, str) and "%" in raw_value:
                    try:
                        value = float(raw_value.replace("%", ""))
                    except:
                        value = raw_value
                elif isinstance(raw_value, str) and raw_value.isdigit():
                    value = int(raw_value)
                else:
                    try:
                        value = float(raw_value)
                    except:
                        value = raw_value
                data_list.append({"name": row["科室名称"], "value": value})
            output_json[col_key] = {
                "unit": unit,
                "name": field,
                "data": data_list
            }


# ========== 6. 读取并处理 conclusion.json ========== #
import re

with open("C:\\A课程作业\\nlp\\nlp-homework-main\\input\\conclusion_word.json", "r", encoding="utf-8") as f:
    conclusion = json.load(f)

summary_text = conclusion.get("总结", "")
suggestions = conclusion.get("建议", [])

# 自动提取建议编号（例如 1、2、3）及其对应内容
suggestion_dict = {}
pattern = r"^(\d+)[、.](.+)"

for item in suggestions:
    match = re.match(pattern, item.strip())
    if match:
        idx = int(match.group(1))
        text = match.group(2).strip()
        suggestion_dict[idx] = text
    else:
        # 非标准格式建议直接按顺序编号添加
        suggestion_dict[len(suggestion_dict) + 1] = item.strip()

# 构造 steps（按编号排序）
steps = []
for idx in sorted(suggestion_dict.keys()):
    steps.append({
        "id": f"rec_{idx}",
        "label": "建议内容",
        "value": suggestion_dict[idx]
    })

output_json["conclusionSummary"] = {
    "title": "总结与改进建议",
    "summary": {
        "section": "总结",
        "content": summary_text
    },
    "rectificationFlow": {
        "section": "建议",
        "steps": steps
    }
}

# ========== 写入结构化 JSON 文件 ========== #
with open("C:\\A课程作业\\nlp\\nlp-homework-main\\input\\1_raw_add_reason\\mid_output_word.json", "w", encoding="utf-8") as f:
    json.dump(output_json, f, ensure_ascii=False, indent=2)

print("json 已生成")
