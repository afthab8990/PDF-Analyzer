import os
import shutil
import warnings
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import Tool, initialize_agent
from langchain_community.tools import DuckDuckGoSearchResults

warnings.filterwarnings("ignore")
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


index_name = "pdf-index"
# index_name = "new-index"

document_content_description = "Uploaded Data"

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3, max_tokens=250)

# Setting prompt
system_prompt = (
    "You're an assistant for Question Answering tasks. "
    "Use the retrieved context or online tools to answer the question. "
    "If you don't know the answer, use the search_tool for web searching. "
    "Answer in 3 sentences max.\n\n{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])
question_answer_chain = create_stuff_documents_chain(llm, prompt)

metadata_field_info = [
    AttributeInfo(name="source", description="Source of the document", type="string"),
    AttributeInfo(name="title", description="Title of the document", type="string"),
    AttributeInfo(name="author", description="Author of the document", type="string"),
    AttributeInfo(name="document_type", description="Type of document, e.g., CV, Report", type="string"),
]



text_splitter = RecursiveCharacterTextSplitter(chunk_size=500)
retriever = None 

# pdf tool
def pdf_tool_func(input_text: str) -> str:
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    result = rag_chain.invoke({"input": input_text})
    return result["answer"]

# web search
search_tool = DuckDuckGoSearchResults()
tools = [
    Tool(name="PDF_QA", func=pdf_tool_func, description="Answer questions based on uploaded PDFs."),
    Tool(name="WebSearch", func=search_tool.run, description="Search the web for real-time information."),
]

# agent
agent_executor = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
)

# on startup
@app.on_event("startup")
def startup_event():
    global retriever
    try:
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=embeddings
        )
        retriever = SelfQueryRetriever.from_llm(
            llm,
            vectorstore,
            document_content_description,
            metadata_field_info,
            verbose=True
        )
        print("Retriever initialized successfully.")
    except Exception as e:
        print(f"Error initializing retriever: {e}")


# upload
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        loader = PyPDFLoader(file_path)
        docs = loader.load()
        docs = text_splitter.split_documents(docs)

        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=embeddings
        )
        vectorstore.add_documents(docs)

        return {"message": f"File '{file.filename}' uploaded and indexed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Schema
class QueryRequest(BaseModel):
    query: str

# ask endpnt
@app.post("/ask")
async def ask_question(request: QueryRequest):
    if retriever is None:
        raise HTTPException(status_code=400, detail="Retriever is not initialized. Upload a document first.")

    try:
        result = agent_executor.invoke({"input": request.query})
        return {"answer": result["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))