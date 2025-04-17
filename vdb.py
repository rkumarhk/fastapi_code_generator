from langchain_postgres import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

connection = "postgresql+psycopg2://vectordb:root@localhost:5432/vectordb"  # Uses psycopg3!
collection_name = "mini"

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")



vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)


def store_into_vectordb(splitted_texts):
    documents = []
    ids = []
    for i, text in enumerate(splitted_texts):
        ids.append(i)
        documents.append(Document(page_content=text.page_content))
    vector_store.add_documents(documents=documents, ids=ids)



def store_into_vdb(docs):
    texts = text_splitter.split_documents(docs)
    store_into_vectordb(texts)
