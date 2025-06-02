import json

# ========== 读取原始 JSON ==========
with open("./output/raw_output(1).json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

output_json = {}

# ========== 1. 培训组织概况 ==========
org_info = raw_data[0]["培训组织概况"]
output_json["orgOverview"] = {
    "section": "培训组织概况",
    "fields": [{"label": k, "value": v} for k, v in org_info.items()]
}

# ========== 2. 培训内容 → 嵌套结构 ==========
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

# ========== 3. 培训参与情况 ==========
participation_info = raw_data[2]["培训参与情况"]
output_json["trainingParticipation"] = {
    "section": "培训参与情况",
    "fields": [{"label": k, "value": v} for k, v in participation_info.items()]
}

# ========== 4. 考核内容、结果、自动分析 ==========
assessment_detail = raw_data[3]["考核内容"]
assessment_result = raw_data[4]["考核结果"]
assessment_analysis = raw_data[5]["考核分析"]

output_json["assessmentDetail"] = {
    "section": "考核内容",
    "fields": [{"label": k, "value": v} for k, v in assessment_detail.items()]
}

output_json["assessmentChart"] = {
    "section": "考核结果",
    "metrics": [{"label": k, "value": v} for k, v in assessment_result.items()]
}

# ✅ 自动提取“鱼骨图”根因字段
cause_keys = ["操作评估存在问题", "不及格主要原因"]
auto_causes = []
for key in cause_keys:
    if key in assessment_result:
        value = assessment_result[key]
        details = value.split("、") if "、" in value else [value]
        auto_causes.append({
            "category": key,
            "details": details
        })

output_json["assessmentAnalysis"] = {
    "section": "考核情况分析（鱼骨图）",
    "mainProblem": assessment_analysis.get("主要问题", ""),
    "causes": auto_causes
}

output_json["rectificationFlow"] = {
    "section": "总结与建议",
    "steps": []  # 可扩展为自动生成流程图步骤
}

# ========== 5. 各科室参与与考核统计 Sheet 拆分 ==========
sheet_data = raw_data[7]["手卫生培训各科室参与与考核情况统计"]["Sheet1"]

# 自动提取所有统计字段
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
            value = float(raw_value.replace("%", ""))
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

# ========== 写入为结构化 JSON 文件 ==========
with open("mid_output_from_raw_v2.json", "w", encoding="utf-8") as f:
    json.dump(output_json, f, ensure_ascii=False, indent=2)

print("mid_output_from_raw_v2.json 已生成")
