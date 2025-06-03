import json
import plotly.graph_objects as go
from jinja2 import Template

# 读取 JSON 数据
# jsonfile = "mid_output.json"
jsonfile = "mid_output_from_raw_v2.json"
with open(jsonfile, "r", encoding="utf-8") as f:
    data = json.load(f)

# 图表 1：参训人数柱状图
departments = [item["name"] for item in data["joinWard"]["data"]]
join_values = [item["value"] for item in data["joinWard"]["data"]]
bar_chart = go.Figure(data=[
    go.Bar(name='参训人数', x=departments, y=join_values, marker_color='rgb(52, 152, 219)')
])
bar_chart.update_layout(
    title={'text': '各科室参与培训人数', 'x': 0.5, 'xanchor': 'center'},
    xaxis_title='科室', yaxis_title='人数'
)

# 图表 2：问题分析饼图
problem_labels = [item["name"] for item in data["trainingQuestion"]["data"]]
problem_values = [item["proportion"] for item in data["trainingQuestion"]["data"]]
pie_chart = go.Figure(data=[
    go.Pie(labels=problem_labels, values=problem_values, hole=0.3)
])
pie_chart.update_layout(
    title={'text': '培训存在问题分析', 'x': 0.5, 'xanchor': 'center'}
)

# 转换为 HTML 片段
bar_html = bar_chart.to_html(include_plotlyjs=False, full_html=False)
pie_html = pie_chart.to_html(include_plotlyjs=False, full_html=False)

# HTML 模板（含样式美化）
html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>护理部培训可视化报告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: "Segoe UI", sans-serif; margin: 40px; background: #f8f9fa; color: #2c3e50; }
        h1, h2 { color: #2c3e50; }
        .section { margin-bottom: 50px; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }

        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #ccc; padding: 10px; text-align: center; }
        th { background-color: #e9f2fb; font-weight: bold; }

        p { line-height: 1.6; }

        .chart-box { margin: 0 auto; max-width: 800px; }
    </style>
</head>
<body>
    <h1>护理部培训可视化报告（2025年5月）</h1>

    <div class="section">
        <h2>一、培训情况总览</h2>
        <table>
            <tr><th>项目</th><th>数据</th></tr>
            <tr><td>培训类型</td><td>{{ trainingType }}</td></tr>
            <tr><td>培训时间</td><td>{{ time_range }}</td></tr>
            <tr><td>主讲人</td><td>{{ speaker }}</td></tr>
            <tr><td>学时/学分</td><td>{{ speaker_credit }}</td></tr>
            <tr><td>培训对象</td><td>{{ remark }}</td></tr>
            <tr><td>培训形式</td><td>{{ line }}</td></tr>
            <tr><td>参训人数</td><td>{{ join }}</td></tr>
            <tr><td>缺勤人数</td><td>{{ nojoin }}</td></tr>
            <tr><td>参训率</td><td>{{ rate }}%</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>二、各科室参与情况</h2>
        <div class="chart-box">
            {{ bar_chart | safe }}
        </div>
    </div>

    <div class="section">
        <h2>三、培训存在问题</h2>
        <div class="chart-box">
            {{ pie_chart | safe }}
        </div>
    </div>

    <div class="section">
        <h2>四、总结&建议</h2>
        <p>{{ evaluation }}</p>
    </div>

    # <div class="section">
    #     <h2>五、存在问题总结</h2>
    #     <p>{{ problem }}</p>
    # </div>

    # <div class="section">
    #     <h2>六、改进建议措施</h2>
    #     <p>{{ improvement }}</p>
    </div>
</body>
</html>
"""

# 渲染 HTML
template = Template(html_template)
rendered_html = template.render(
    trainingType=data["trainingContents"]["trainingTypeName"],
    speaker=data["trainingContents"]["trainingSpeaker"],
    speaker_credit=data["trainingContents"]["speakerCreditStr"],
    remark=data["trainingContents"]["trainingRemark"],
    line=data["trainingContents"]["trainingLineName"],
    time_range=data["trainingContents"]["sessionStr"]["items"][0]["item"]["contents"][0]["text"],
    join=data["trainingContents"]["joinTrainingNum"],
    nojoin=data["trainingContents"]["noJoinNum"],
    rate=data["trainingContents"]["joinRate"],
    bar_chart=bar_html,
    pie_chart=pie_html,
    evaluation=data["rectificationFlow"],
    problem=data["existQuestion"],
    improvement=data["improvementMeasures"]
)

output = jsonfile[:-4] + ".html"
# 写入输出 HTML 文件
with open(output, "w", encoding="utf-8") as f:
    f.write(rendered_html)

print(f"✅ 报表已生成：{output}")
