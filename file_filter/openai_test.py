import os
import getpass
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4o-mini", model_provider="openai")


async def main():
    async for chunk in model.astream("Hello please introduce yourself"):
        print(chunk.content, end="")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())