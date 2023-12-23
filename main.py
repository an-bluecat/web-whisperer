from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import ChromaVectorStore
from llama_index import VectorStoreIndex, SimpleDirectoryReader
import chromadb
from llama_index import download_loader
from dotenv import load_dotenv, find_dotenv


import os
from dotenv import load_dotenv
import openai

load_dotenv()  # This loads the environment variables from .env

# Now you can access the environment variable as usual
# openai_api_key = os.environ.get("OPENAI_API_KEY")

openai.api_key = os.environ.get("OPENAI_API_KEY")
UnstructuredURLLoader = download_loader("UnstructuredURLLoader")

urls = [
    "https://docs.splunk.com/Documentation/SplunkCloud/9.1.2308/ReleaseNotes/EdgeProcessor",
    #  "https://www.understandingwar.org/backgrounder/russian-offensive-campaign-assessment-february-9-2023",
]

loader = UnstructuredURLLoader(
    urls=urls, continue_on_failure=False, headers={"User-Agent": "value"})
# loader.load()


# load some documents
# documents = SimpleDirectoryReader("./data").load_data()
documents = loader.load_data()
print(documents)
# initialize client, setting path to save data
db = chromadb.PersistentClient(path="./chroma_db")

# create collection
chroma_collection = db.get_or_create_collection("quickstart")

# assign chroma as the vector_store to the context
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# create your index
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

# create a query engine and query
query_engine = index.as_query_engine()
response = query_engine.query("what's is edge processor?")
print(response)
