from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool, BaseTool
from langchain.agents import Tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyMuPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
import os
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv
load_dotenv()
from langchain.agents import initialize_agent


from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("GROQ_API_KEY"),
)

search_tool = GoogleSerperAPIWrapper(api_key=os.getenv("SERPER_API_KEY"))
@tool
def google_search(text: str) -> str:
    """
    Searches Google for the given text.
    Args:
        text (str): The text to search for.
    Returns:
        str: The search results.
    """
    return search_tool.run(text)
    
google_search_tool = Tool(
     name="Google Search",
     func=google_search,
     description="Search Google for real-time information."
)

@tool
def calculator(inputs: str):
    """
    Performs basic arithmetic calculations. Input should be a mathematical expression.

    Args:
        inputs (str): The text to evaluate the expression.

    Returns:
        str: The calculated results.
    """
    try:
        return str(eval(inputs))  # Simple arithmetic operation
    except Exception as e:
        return f"Error: {e}"

calculator_tool = Tool(
    name="Calculator",
    func=calculator,
    description="Performs basic arithmetic calculations. Input should be a mathematical expression."
)

tools = [google_search_tool, calculator_tool]

memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=3,
    return_messages=True
)

# conversational_agent = initialize_agent(
#     agent='chat-conversational-react-description',
#     tools=tools,
#     llm=llm,
#     verbose=True,
#     max_iterations=3,
#     early_stopping_method='generate',
#     memory=memory
# )

connection = "postgresql+psycopg2://vectordb:root@localhost:5432/vectordb"  # Uses psycopg3!
collection_name = "mini"

def load_document(file_path):
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    return documents


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
# texts = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")



vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

print("-------------------------------------====================")

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



documents = load_document('vector.pdf')

store_into_vdb(documents)


prompt = PromptTemplate.from_template(
      """You are my helpful AI Assistent
      Strictly answer based on the given docs {docs}. 
      if the query contain aithmetic expression, say 'This is airthmetic.' .
      OR If the context does not provide an answer, say 'I don't know.' .
      Do not generate answers from general knowledge.
      The user query is {user_input}
      """
)

def get_response_from_llm(docs, user_input):
    message = prompt.format(docs=docs, user_input=user_input)
    response = llm.invoke(message)
    response_content = response.content


    if response_content.strip() == "I don't know.":
        # Use the google_search_tool if the response is "I don't know."
        search_results = google_search_tool.func(user_input)
        return f"AI Response: {response_content}\n\nGoogle Search Results: {search_results}"
    elif response_content.strip() == "This is arithmetic.":
        print(123)
        # Use the google_search_tool if the response is "I don't know."
        search_results = calculator_tool.func(user_input)
        return f"AI Response: {response_content}\n\nAirthmetic operation: {search_results}"
    
    return response_content


while True:
    user_prompts = input("Enter query:")

    results = vector_store.similarity_search(query="influence, or attempt to solicit, induce or influence, any employee or independent contractor of the Company who",k=1)
    docs = ""
    for doc in results:
        docs+=f"{doc.page_content} [{doc.metadata}]"

    # print(docs)

    print(get_response_from_llm(docs, user_prompts))
