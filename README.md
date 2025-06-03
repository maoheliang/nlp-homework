## 文档处理与数据抽取工具

### 📦 Python 包安装

请确保安装以下依赖：

```bash
pip install pandas pdfplumber python-docx python-pptx pytesseract openpyxl jieba openai requests beautifulsoup4 sentence_transformers hnswlib
```
jieba推荐版本0.41.0

如果使用embedding模型并且使用GPU计算需要安装pytorch：
```bash
pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu124
```
---

### 🧹 文件处理和清洗

**模块位置：** `clean_data.DocumentProcessor`

#### 示例代码

```python
from clean_data import DocumentProcessor

processor = DocumentProcessor()

# 处理文件
processor.process_file("./data/2025年5月护理部理论知识培训.docx")

# 导出处理后的数据至 Excel
processor.export_data()  # 默认路径为 "./data/report.xlsx"

# 打印数据摘要
processor.print_data_summary(max_lines=10)  # max_lines=-1 表示显示全部

# 获取数据副本
data_copy = processor.get_data()

# 获取原始数据本体
data = processor.data

# 将所有数据处理为字符串输出
str_data = processor.get_str_data()
```

---

### 🔍 数据提取

**模块位置：** `extract_data`

#### 使用大模型（如 DeepSeek）进行精确抽取
结果很好，但是api的响应速度都偏慢，建议用快速的方法

```python
from extract_data import extract_information
from openai import OpenAI

api_key = ""
base_url = "https://api.chatanywhere.tech/v1"
client = Client(api_key, base_url)

client_config = {
    "model": "deepseek-v3",
}

user_prompt = "生成5月手卫生培训与专项考核报告"
response = extract_information(processor.get_data(), user_prompt, client, client_config)
```

- `data`: 数据本体，类型为 `pd.DataFrame`
- `user_prompt`: 用户提示语，类型为 `str`
- `client`: 接口客户端，类型为 `Client`，需要根据不同的供应商进行配置
- `client_config`: 客户端配置，类型为 `dict`

#### 使用 Jieba 进行粗粒度抽取

```python
from extract_data import extract_information_fast

user_prompt = "生成5月手卫生培训与专项考核报告"
response = extract_information_fast(processor.get_data(), user_prompt, threshold=0.3)  # 建议阈值为 0.3
```

- `processor.get_data()`: 数据副本，类型为 `pd.DataFrame`
- `user_prompt`: 用户提示语，类型为 `str`
- `threshold`: 相似度阈值，默认为 0.3

#### 使用嵌入模型检索提取
需在processor初始化时开启嵌入模型检索功能
```python
processor = DocumentProcessor(
    use_retriever=True, 
    model_name: str = "./models/bge-small-zh-v1.5", 
    device="cpu"
)
user_prompt = "生成2025年5月份护理部的理论知识培训报告"
extract_data = processor.retriever.search_by_threshold(user_prompt, threshold=0.55, return_scores=True)
extract_data = processor.retriever.search(user_prompt,top_k=2, return_scores=True)
```
- `use_retriever`默认为`False`
- `device`可指定GPU：`"cuda:0"`，需要安装pytorch
- `model_name`可指定模型路径，默认为 `"./models/bge-small-zh-v1.5"`，可以到[huggingface](https://huggingface.co/BAAI/bge-small-zh-v1.5)下载模型并放至相应位置
- `search_by_threshold`筛选出相关度超过阈值的所有文档信息，`threshold`为相似度阈值，推荐默认`0.55`，本项目推荐使用该方法
- `search`返回`top_k`个相关度最高的文档信息，适用于大量文档
- `return_scores`返回文档相关度分数，用于debug
  - 用于debug，默认关闭，直接返回字符串结果
  - 开启后返回`(文档信息字符串，相关度分数)`元组列表

#### 三种方法对比
---
|  | 大模型提取 | 关键词匹配提取 | 嵌入模型检索提取 |
|:-:|:-:|:-:|:-:|
|提取速度|慢|快|中等|
|提取结果|准确|一般|较准|
---

#### 使用网络检索获取额外数据

```python
from extract_data import extract_information_net

user_prompt = "生成今年第一季度新能源汽车市场报告"
serp_api_key = ""

extract_data = extract_information_net(user_prompt, serp_api_key, top_k=2, max_len=5000)
print(extract_data)
```
- `user_prompt`: 用户要求，类型为 `str`
- `serp_api_key`: 检索API密钥，类型为 `str`，可到[官网](https://serpapi.com/)注册订阅免费额度API
- `top_k`: 返回的检索结果网页数量，类型为 `int`
- `max_len`: 返回的每个网页检索结果最大长度，类型为 `int`

---


## 生成中间json文件（更新，以此版为准！！！）
**代码位置：** `generate_raw_json.py`(对输入的文档进行初步内容提取）
**输出文件位置：** `output/raw_output_pdf_and_xlsx.json.json`  `output/raw_output_word.json`

**代码位置：** `generate_mid_fromraw.py`（对output/raw_output(1）.json进行格式转换）
**输出文件位置：** `output/mid_output_pdf_and_xlsx.json`  `output/mid_output_word.json`（作业要求的中间json文件）

### json结构说明
- "orgOverview": 培训组织概况（可用作详情页展示）
- "trainingContent": 培训内容（采用嵌套结构，可用作树状图等制作）
- "trainingParticipation": 培训参与情况（可用作详情页、图表等制作）
- "assessmentDetail"：考核内容
- "assessmentChart"：考核结果
- "assessmentAnalysis"：考核情况分析（可用于根因分析鱼骨图制作）
- "col_1"-"col_8"：对应手卫生培训各科室参与与考核情况统计.xlsx中各科室的详细数据
- "conclusionSummary":总结与建议（可用作整改流程图制作)

