from functools import lru_cache

from django.conf import settings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai.chat_models import ChatOpenAI
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient(settings.MONGO_URI)
database = client[settings.VECTOR_DB_NAME]
vectors_collection = database[settings.VECTOR_COLLECTION_NAME]


@lru_cache(maxsize=1)
def get_llm():
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        openai_api_base=settings.LLM_API_BASE,
    )


@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceBgeEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


@lru_cache(maxsize=1)
def get_vector_store():
    embeddings = get_embeddings()
    return MongoDBAtlasVectorSearch(
        embedding=embeddings,
        collection=vectors_collection,
        index_name="default",
        relevance_score_fn="cosine",
    )
