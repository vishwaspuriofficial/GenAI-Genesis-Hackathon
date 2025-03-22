import os
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 初始化 ChatGoogleGenerativeAI 模型
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GEMINI_API_KEY)

# 使用 LangChain 的 invoke 方法进行调用
response = llm.invoke("Say hello?")

# 打印响应
print(response.content)
