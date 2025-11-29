# coding: utf-8
"""示例：使用 API 调用 Kimi 模型。"""
import os
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),  # 请确保设置了环境变量
    base_url="https://api.moonshot.cn/v1"
)

# 发起聊天完成请求
try:
    response = client.chat.completions.create(
        model="kimi-latest",
        messages=[
  {
    "role": "system",
    "content": "（使用中文交流）自我介绍下."
  }
],
        temperature=0.3,
        max_tokens=1024,
        top_p=1,
        stream=False
    )
    
    # 处理响应
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"请求失败: {e}")