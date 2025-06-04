import json
import plotly.graph_objects as go
from jinja2 import Template
import os

# HTML 模板（含样式美化）
html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>可视化报告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="fishbone1.0/require/jquery-1.11.1.min.js"></script>
    <script src="fishbone1.0/FishBone.js"></script>
    <link rel="stylesheet" type="text/css" href="fishbone1.0/css/base.css">
    <script type="module">
    {% raw %}
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: true });
        {% endraw %}
    </script>
    <style>
        *{
          box-sizing:border-box;
        }
        #bone-container {
          width: 100%;
          height: 400px;
        }
        body { font-family: "Segoe UI", sans-serif; margin: 40px; background: #f8f9fa; color: #2c3e50; }
        h1, h2 { color: #2c3e50; }

        .section { margin-bottom: 50px; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }

        table { width: 60%; border-collapse: collapse; margin-top: 15px; margin: 0 auto;}
        th, td { border: 1px solid #ccc; padding: 10px; text-align: center; }
        th { background-color: #e9f2fb; font-weight: bold; }

        p { line-height: 1.6; }

        .chart-box { max-width: 1400px; margin: 0 auto;  }
        .mermaid {
            margin: 0 auto; 
            max-width: 800px; 
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            white-space: pre-wrap;
        }
        .quote-block {
            background: #f9f9f9;
            border-left: 5px solid #3498db;
            width: 95%;
            padding: 15px;
            margin-top: 30px;
            margin-bottom: 30px;
            color: #333;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <h1>可视化报告（2025年5月）</h1>

    <div class="section">
    <!-- %%ORG_OVERVIEW_TABLE%% -->
        
    </div>
    <!-- %%ORG_OVERVIEW_CHART%% -->
    

    <div class="section">
    <h2>{{ idx1 }}、总结&建议</h2>
     <p style="width: 95%">{{ evaluation }}</p>
    <div class="quote-block">
        
       
        <p>1.{{ advice1 }}</p>
        <p>2.{{ advice2 }}</p>
        <p>3.{{ advice3 }}</p>
    </div>
    </div>
    <div class="section">
        <h2>{{ idx2 }}、流程图</h2>
        <div class="mermaid">
            {{ mermaid_code }}
        </div>
    </div>
    <div class="section">
        <h2>{{ idx3 }}、鱼骨图</h2>
        <div id="bone-container"></div>
    </div>
    <script>
    $(document).ready(function () {
      const width = $('#bone-container').innerWidth();
      const height = $('#bone-container').innerHeight();
        $("#bone-container").FishBone({
            jsonData: testFishData,
            canvasSize: [width,height],
            showToolbar: true,
        });
    });
</script>
    
</body>
</html>
"""

# 读取 JSON 数据
# jsonfile = "mid_output.json"
# jsonfile = "mid_output_from_raw_v2.json"
# jsonfile = "mid_output_pdf_and_xlsx.json"
jsonfile = "mid_output_word.json"
with open(jsonfile, "r", encoding="utf-8") as f:
    data = json.load(f)

if "col_2" in data.keys() and "col_3" in data.keys():
    num = 4
# 图表 1：参训人数柱状图
    departments = [item["name"] for item in data["col_2"]["data"]]
    join_values = [item["value"] for item in data["col_2"]["data"]]
    nojoin_values = [item["value"] for item in data["col_3"]["data"]]
    bar_chart = go.Figure(data=[
        go.Bar(name='参训人数', x=departments, y=join_values, marker_color='rgb(52, 152, 219)'),
        go.Bar(name='缺勤人数', x=departments, y=nojoin_values, marker_color='rgb(52, 152, 29)')
    ])
    bar_chart.update_layout(
        title={'text': '各科室参与培训情况', 'x': 0.5, 'xanchor': 'center'},
        barmode='stack',
        xaxis_title='科室', yaxis_title='人数', width=1400
    )

    # 图表 2：问题分析饼图
    problem_labels = [item["name"] for item in data["col_3"]["data"]]
    problem_values = [item["value"] for item in data["col_3"]["data"]]
    problem = data["col_3"]["name"]
    pie_chart = go.Figure(data=[
        go.Pie(labels=problem_labels, values=problem_values, hole=0.3)
    ])
    pie_chart.update_layout(
        title={'text': problem, 'x': 0.5, 'xanchor': 'center'}
    )

    # 转换为 HTML 片段
    bar_html = bar_chart.to_html(include_plotlyjs=False, full_html=False)
    pie_html = pie_chart.to_html(include_plotlyjs=False, full_html=False)
    train_table = """
    <table border="1" cellspacing="0" cellpadding="5" style="margin-top: 40px;">\n
    
    """
    train_table += """<tr><th>指标</th><th>数据</th></tr>
    <caption style="caption-side: top; font-weight: bold; font-size: 18px; margin-bottom: 10px;">
    培训总体情况
  </caption>"""
    t = data["trainingParticipation"]["fields"]
    def render_value(value):
        if isinstance(value, str):
            return value.strip() if value.strip() else '/'
        elif isinstance(value, dict):
            parts = []
            for k, v in value.items():
                parts.append(f'<p><strong>{k}：</strong></p>')
                if isinstance(v, list):
                    parts.append('<ul>')
                    for item in v:
                        parts.append(f'<p>{item}</p>')
                    parts.append('</ul>')
                elif isinstance(v, str):
                    parts.append(f'<p>{v}</p>')
            return "\n".join(parts)
        else:
            return '/'

    for field in t:
        label = field["label"]
        value_html = render_value(field["value"])
        train_table += f"<tr><td>{label}</td><td>{value_html}</td></tr>\n"

    train_table += '</table>'
    h = """<div class="section">
        <h2>二、{{ caption2 }}</h2>
        <div class="chart-box">
            {{ bar_chart | safe }}
        </div>
        <!-- %%ORG_OVERVIEW_TRAIN%% -->
    </div>

    <div class="section">
        <h2>三、{{ problem }}</h2>
        <div class="chart-box">
            {{ pie_chart | safe }}
        </div>
    </div>"""
    h = h.replace("<!-- %%ORG_OVERVIEW_TRAIN%% -->", train_table)
    html_template = html_template.replace("<!-- %%ORG_OVERVIEW_CHART%% -->",h)
    
else:
    bar_html, pie_html, problem = None, None, None
    num = 3
    train_table = """
    <table border="1" cellspacing="0" cellpadding="5">\n
    
    """
    train_table += """<tr><th>指标</th><th>数据</th></tr>
    <caption style="caption-side: top; font-weight: bold; font-size: 18px; margin-bottom: 10px;">
    培训总体情况
  </caption>"""
    t = data["trainingParticipation"]["fields"]
    def render_value(value):
        if isinstance(value, str):
            return value.strip() if value.strip() else '/'
        elif isinstance(value, dict):
            parts = []
            for k, v in value.items():
                parts.append(f'<p><strong>{k}：</strong></p>')
                if isinstance(v, list):
                    parts.append('<ul>')
                    for item in v:
                        parts.append(f'<p>{item}</p>')
                    parts.append('</ul>')
                elif isinstance(v, str):
                    parts.append(f'<p>{v}</p>')
            return "\n".join(parts)
        else:
            return '/'

    for field in t:
        label = field["label"]
        value_html = render_value(field["value"])
        train_table += f"<tr><td>{label}</td><td>{value_html}</td></tr>\n"

    train_table += '</table>'
    # for item in t:
    #     label = item["label"]
    #     if label in ["存在问题", "原因分析", "整改措施"]:
    #         value = item["value"] if item["value"] else "/"

    #     else:
    #         value = item["value"] if item["value"] else "/"
    #         train_table += f"<tr><td>{label}</td><td>{value}</td></tr>\n"

    # train_table += "</table>"
    h = """<div class="section">
        <h2>二、{{ caption2 }}</h2>
        
        <!-- %%ORG_OVERVIEW_TRAIN%% -->
    </div>"""
    h = h.replace("<!-- %%ORG_OVERVIEW_TRAIN%% -->", train_table)
    html_template = html_template.replace("<!-- %%ORG_OVERVIEW_CHART%% -->",h)

def generate_mermaid_graph(data):
    overview = {item['label']: item['value'] for item in data['orgOverview']['fields']}
    participation = {item['label']: item['value'] for item in data['trainingParticipation']['fields']}
    metrics = {item['label']: item['value'] for item in data['assessmentChart']['metrics']}
    rect_steps = data['conclusionSummary']['rectificationFlow']['steps']

    def get_safe(value):
        return value if value else "N/A"

    # 提取“存在问题”字段（字符串或对象）
    problem_info = participation.get("存在问题", "无")
    if isinstance(problem_info, dict):
        summary = problem_info.get("总结", "")
        details = problem_info.get("具体问题", [])
        detail_text = "\\n".join(details)
        problem_text = f"{summary}\\n{detail_text}" if details else summary
    else:
        problem_text = get_safe(problem_info)

    step_nodes = ''
    last_step = 'J'
    for index, step in enumerate(rect_steps):
        node_id = f"R{index + 1}"
        step_nodes += f'\n  {last_step} --> {node_id}["{get_safe(step["value"])}"]'
        last_step = node_id

    mermaid_text = f"""
        graph TD
        A[启动专项培训\\n{get_safe(overview.get("培训主题"))}] --> B[组织部门: {get_safe(overview.get("组织部门"))}]
        B --> C[培训形式: {get_safe(overview.get("培训形式"))}]
        C --> D[培训内容实施]
        D --> E[整体参训率: {get_safe(participation.get("整体参训率"))}]
        E --> F[理论考试平均成绩: {get_safe(metrics.get("理论考试平均成绩"))}]
        F --> G[操作合格率: {get_safe(metrics.get("操作评估合格率"))}]
        G --> H{{是否达标}}
        H -- 是 --> I[最终通过率: {get_safe(metrics.get("最终通过率"))}]
        H -- 否 --> J[问题分析: {problem_text}]
        I --> K[总结与持续改进]{step_nodes}
    """
    return mermaid_text.strip()

mermaid_code = generate_mermaid_graph(data)
overview = data["orgOverview"]
section_title = overview["section"]
fields = overview["fields"]
html_table = f'<h2>一、{section_title}</h2>\n<table border="1" cellspacing="0" cellpadding="5">\n'
html_table += "<tr><th>项目</th><th>内容</th></tr>\n"

for item in fields:
    label = item["label"]
    value = item["value"] if item["value"] else "/"
    html_table += f"<tr><td>{label}</td><td>{value}</td></tr>\n"

html_table += "</table>"

final_html = html_template.replace("<!-- %%ORG_OVERVIEW_TABLE%% -->", html_table)
chinese_nums = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']


# 构建鱼骨图数据
def generate_fishbone_data(data):
    fishbone_data = []

    # 主问题作为鱼骨图的主干
    main_problem = data["assessmentAnalysis"]["mainProblem"]

    # 创建主干节点
    main_node = {
        "id": "1",
        "fid": "0",
        "name": main_problem,
        "fontColor": "",
        "lineColor": "",
        "children": []
    }

    # 添加各个类别作为鱼骨的主要分支
    for idx, cause in enumerate(data["assessmentAnalysis"]["causes"], 1):
        category = cause["category"]
        category_id = f"100{idx}"

        # 创建分类节点
        category_node = {
            "id": category_id,
            "fid": "1",
            "name": category,
            "fontColor": "",
            "lineColor": "",
            "children": []
        }

        # 添加每个类别下的详细原因
        for detail_idx, detail in enumerate(cause["details"], 1):
            detail_id = f"{category_id}{detail_idx}" + str(hash(detail) % 10000)

            # 创建详细原因节点
            detail_node = {
                "id": detail_id,
                "fid": category_id,
                "name": detail,
                "fontColor": "",
                "lineColor": "",
                "children": []
            }

            # 将详细原因添加到对应类别下
            category_node["children"].append(detail_node)

        # 将类别添加到主干下
        main_node["children"].append(category_node)

    # 添加主干到鱼骨图数据中
    fishbone_data.append(main_node)

    return fishbone_data

# 生成鱼骨图数据
fishbone_data = generate_fishbone_data(data)

# 将鱼骨图数据添加到HTML模板
fishbone_data_js = f"var testFishData = {json.dumps(fishbone_data, ensure_ascii=False, indent=2)};"
# print(fishbone_data_js,'====fishbone_data_js')
# 在渲染HTML之前添加鱼骨图数据到final_html而不是html_template
final_html = final_html.replace("</head>", f"<script>{fishbone_data_js}</script>\n</head>")
# 渲染 HTML
template = Template(final_html)
rendered_html = template.render(
    caption1=data['orgOverview']['section'],
    caption2=data['trainingParticipation']['section'],
    bar_chart=bar_html,
    pie_chart=pie_html,
    evaluation=data["conclusionSummary"]['summary']['content'],
    problem=problem,
    advice1=data['conclusionSummary']['rectificationFlow']['steps'][0]['value'],
    advice2=data['conclusionSummary']['rectificationFlow']['steps'][1]['value'],
    advice3=data['conclusionSummary']['rectificationFlow']['steps'][2]['value'],
    mermaid_code=mermaid_code,
    idx1=chinese_nums[num],
    idx2=chinese_nums[num+1],
    idx3=chinese_nums[num+2],
)

output = jsonfile[:-4] + "html"
# 写入输出 HTML 文件
with open(output, "w", encoding="utf-8") as f:
    f.write(rendered_html)

print(f"✅ 报表已生成：{output}")
