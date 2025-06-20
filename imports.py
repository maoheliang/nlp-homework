from openai import OpenAI
import jieba
from jieba import analyse
import jieba.posseg as pseg
import re
import pandas as pd
from copy import deepcopy
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np
import hnswlib
import json
import time
from typing import Union, Tuple, List


class Client:
    def __init__(self, api_key, base_url="https://api.chatanywhere.tech/v1"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )       

    def chat(self, prompt: str, model="deepseek-v3"):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content