import os
import re
import json
import dotenv
import asyncio
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI

# 加载 API Key
dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 初始化 Gemini 模型
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GEMINI_API_KEY)

# 加载 PDF 文件并提取内容
def load_documents(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return [doc.page_content for doc in documents]

# 摘要并提取 JSON
def clean_json_text(text: str) -> str:
    return re.sub(r"```(?:json)?", "", text).strip()

async def summarize(text: str):
    prompt = f"""
Extract a list of important items from the following text. Return ONLY valid JSON.
Each item should at least include `name` and `date`. Other fields are optional.

Text:
\"\"\"
{text}
\"\"\"
"""
    response = ""
    async for chunk in llm.astream(prompt):
        response += chunk.content

    try:
        cleaned = clean_json_text(response)
        parsed = json.loads(cleaned)
        filtered = [item for item in parsed if "name" in item and "date" in item]
        return filtered
    except json.JSONDecodeError as e:
        print("❌ JSON 解析失败，原始输出：\n", response)
        return []

# 主函数
async def main():
    documents = load_documents("data1.pdf")

    all_items = []
    for doc in documents:
        items = await summarize(doc)
        all_items.extend(items)

    # 保存到 JSON 文件
    with open("data2.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(main())
