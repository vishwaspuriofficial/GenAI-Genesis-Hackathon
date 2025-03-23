from langchain_cohere import CohereEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = CohereEmbeddings(model="embed-english-v3.0")  # type: ignore
