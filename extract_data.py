from imports import *
from clean_data import *

def extract_information(data:  pd.DataFrame, user_prompt: str, client: Client, client_config: dict) -> str:
    """
    提取信息
    :param data: 原始数据
    :param user_prompt: 用户要求
    :param client: 聊天客户端
    :param client_config: 聊天客户端配置
    :return: 抽取后的信息
    """

    # 定义提示信息
    prompt = """下面是多个文档的原始信息，请提取与用户要求相关的信息。
请注意你不需要做任何改写和整理，只需要在原始信息上进行抽取即可。
你还必须保留原文的文件名、信息类型和内容等格式。
如果文档内容与用户要求无关，请删除该文档信息。
"""
    # 初始化原始数据
    original_data  = ""
    # 按文件名分组
    grouped_data = data.groupby("filename")
    # 遍历分组后的数据
    for filename, group in grouped_data:
        # 添加文件名
        original_data += f"====文件名：{filename}====\n\n"
        # 遍历每个文件中的数据
        for index, row in group.iterrows():
            # 添加信息类型和内容
            original_data += f"信息类型: {row['content_type'].strip()}\n"
            original_data += f"内容：{row['content'].strip()}\n\n"
    # 将原始数据添加到提示信息中
    prompt += original_data
    # 添加用户要求
    prompt += f"\n\n用户要求如下：\n{user_prompt}"
    # 调用聊天客户端获取响应
    response = client.chat(prompt, **client_config)
    # 返回响应
    return response

def extract_information_fast(data:  pd.DataFrame, user_prompt: str, threshold=0.5)-> str:
    """
    提取信息
    :param data: 原始数据
    :param user_prompt: 用户要求
    :param threshold: 阈值
    :return: 抽取后的信息
    """

    def compute_ngram_overlap_score(query, doc, process_func="cut"):

        # 使用jieba分词
        q_tokens = list(jieba.cut(query))
        if process_func == "cut":
            d_tokens = list(jieba.cut(doc))
        elif process_func == "extract_tags":
            # 使用jieba提取关键词
            d_tokens = analyse.extract_tags(doc, topK=20, withWeight=False, allowPOS=('ns', 'n', 'vn', 'v', 'nt', 'nr'))
        else:
            raise ValueError(f"Unsupported process_func: {process_func}")

        # 将分词结果转换为集合
        q_tokens = set(q_tokens)
        d_tokens = set(d_tokens)    
        if not q_tokens:
            return 0.0
        # 计算交集的长度与query长度的比值
        return len(q_tokens & d_tokens) / len(q_tokens)

    # 初始化抽取后的信息列表
    extract_data_list  = []
    # 按文件名分组
    grouped_data = data.groupby("filename")
    for filename, group in grouped_data:
        # 初始化原始数据
        original_data = f"====文件名：{filename}====\n\n"
        # 计算文件名与query的相似度
        score1 = compute_ngram_overlap_score(user_prompt, filename, process_func="cut")
        score2 = 0
        score_data = ""
        for index, row in group.iterrows():
            if row['order_index'] == 0:
                # 计算第一行内容的相似度
                score2 = compute_ngram_overlap_score(user_prompt, row['content'].strip().split("\n")[0], process_func="cut")
                # 将第一行内容后面的内容拼接起来
                joined_content = '\n'.join(row['content'].strip().split('\n')[1:])
                score_data += f"内容：{joined_content}\n\n"
            else:
                score_data += f"内容：{row['content'].strip()}\n\n"
            # 添加原始数据
            original_data += f"信息类型: {row['content_type'].strip()}\n"
            original_data += f"内容：{row['content'].strip()}\n\n"            
        # 计算score_data与query的相似度
        score3=compute_ngram_overlap_score(user_prompt, score_data, process_func="extract_tags")
        # 如果相似度大于阈值，则添加到抽取后的信息列表中
        if max(score1, score2, score3) > threshold:
            extract_data_list.append(original_data)
    # 将抽取后的信息列表拼接成字符串返回
    return "\n\n".join(extract_data_list)

def extract_information_net(user_prompt: str, api_key: str, top_k: int = 3, max_len: int = 5000) -> str:
    """
    联网检索信息并整理为统一格式
    :param user_prompt: 用户问题或需求
    :param api_key: SerpAPI 密钥
    :param top_k: 返回的网页数量
    :param max_len: 每个网页内容的最大长度
    :return: 整理后的字符串信息
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    # Step 1: 通过 SerpAPI 搜索，拉取 top_k * 3 条数据以保证过滤后足够
    search_url = "https://serpapi.com/search"
    params = {
        "q": user_prompt,
        "api_key": api_key,
        "engine": "google",
        "num": top_k * 3,
    }

    try:
        resp = requests.get(search_url, params=params, headers=headers, timeout=10)
        results = resp.json().get("organic_results", [])
    except Exception as e:
        return f"[错误] 无法访问 SerpAPI：{e}"

    # Step 2: 提取前 top_k 个有效链接（不包含广告）
    links = []
    for r in results:
        if "link" in r:
            links.append(r["link"])
        if len(links) >= top_k:
            break

    if not links:
        return "[警告] 未找到任何有效的搜索链接。"

    # Step 3: 抓取网页内容
    output = []
    for url in links:
        try:
            page = requests.get(url, headers=headers, timeout=10)
            page.encoding = page.apparent_encoding
            soup = BeautifulSoup(page.text, "html.parser")
            paragraphs = soup.find_all("p")
            content = "\n".join(p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 60)
            content = content.strip()[:max_len]  # 可按需调整长度限制
            if content and len(content) > 100:
                formatted = f"===={url}====\n信息类型：网络数据\n内容：\n{content}\n"
                output.append(formatted)
        except Exception as e:
            print(f"[跳过] 抓取失败：{url} 错误：{e}")
            continue

    return "\n\n".join(output) if output else "未能检索到有用信息。"

if __name__ == "__main__":



    processor = DocumentProcessor(use_retriever=True, device="cuda:0")
    processor.process_file("./data/2025年5月护理部理论知识培训.docx")
    processor.process_file("./data/2025年5月手卫生执行专项培训与评估总结.pdf")
    processor.process_file("./data/手卫生培训各科室参与与考核情况统计.xlsx")
    processor.process_file("./data/2025年第一季度中国新能源汽车市场分析报告.docx")

    # api_key=""
    # base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    # api_key=""
    # base_url="https://api.chatanywhere.tech/v1"
    # client = Client(api_key, base_url)
    # user_prompt = "生成手卫生培训考核方式报告"
    # client_config = {
    #     "model": "deepseek-v3",
    # }
    # response=extract_information(processor.get_data(),user_prompt, client, client_config)
    # print(response)


    # user_prompt = "生成2025年5月份护理部的理论知识培训报告"
    # extract_data = extract_information_fast(processor.get_data(), user_prompt, threshold=0.3)
    # print(extract_data)

    # user_prompt = "生成今年第一季度新能源汽车市场报告"
    # serp_api_key = ""
    # extract_data = extract_information_net(user_prompt, serp_api_key, top_k=2, max_len=5000)
    # print(extract_data)

    # user_prompt = "生成2025年5月份护理部的理论知识培训报告"
    user_prompt = "生成今年第一季度新能源汽车市场报告"
    extract_data = processor.retriever.search_by_threshold(user_prompt, threshold=0.55, return_scores=False)
    # extract_data = processor.retriever.search(user_prompt,top_k=2, return_scores=True)
    print(extract_data)
