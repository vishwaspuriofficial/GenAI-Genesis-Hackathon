import os
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader

dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 初始化 ChatGoogleGenerativeAI 模型
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GEMINI_API_KEY)

loader = PyPDFLoader("files/data1.pdf")
documents = loader.load()

# 使用 LangChain 的 invoke 方法进行调用
response = llm.invoke("Say hello?")

# 打印响应
print(response.content)

print(documents)

import json
json.dump([d.__dict__ for d in documents], open("files/data1.json", "w"), indent=4)