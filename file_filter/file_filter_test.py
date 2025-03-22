import os
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# initialize ChatGoogleGenerativeAI model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GEMINI_API_KEY)

# invoke using LangChain's invoke method
async def main():
	async for chunk in llm.astream("How does AI work?"):
		print(chunk.content, end="")


if __name__ == '__main__':
	import asyncio
	asyncio.run(main())