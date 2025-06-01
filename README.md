## 文档处理与数据抽取工具

### 📦 Python 包安装

请确保安装以下依赖：

```bash
pip install pandas pdfplumber python-docx python-pptx pytesseract openpyxl jieba openai requests beautifulsoup4
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

#### 使用网络检索获取数据

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

## 生成中间json文件
**代码位置：** `generate_mid_fromraw.py`
**输出文件位置：** `output/mid_output_from_raw.json`
### json结构说明
- `text`: 培训情况概览（其中"trainingcontent"设计为嵌套结构）
- `trainingresult`: 考核情况（其中"testingcontent"可用于生成培训考核情况分析鱼骨图）
- `col_1--col_8`: 各科室的培训、考核详细数据



