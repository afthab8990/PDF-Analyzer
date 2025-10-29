# AI-Powered PDF Question Answering Agent 🤖📄

This is a FastAPI + LangChain-based project that allows users to upload PDF documents and ask questions about their content. The system also includes a web search tool (DuckDuckGo) for out-of-context queries using Gemini 2.0.

---

## 🚀 Features

- Upload PDF documents and index them using Pinecone vector database
- Retrieve relevant chunks using semantic search
- Answer questions using Gemini 2.0 Flash (Google Generative AI)
- Use DuckDuckGo web search for real-time info (e.g., "What's the weather?")
- Zero-shot agent-based decision routing with tools

---

## 🧠 Tech Stack

| Layer         | Tech                                |
|--------------|-------------------------------------|
| Backend       | FastAPI, Python                     |
| AI/LLM        | LangChain, Google Gemini (Chat & Embedding) |
| Vector Store  | Pinecone                            |
| Tools         | DuckDuckGoSearchResults             |
| Document Load | PyPDFLoader                         |
| Dev Tools     | dotenv, Pydantic, Uvicorn           |

---

### How to run

on the terminal enable the virtual enviroment using 
```bash
env/Scripts/activate
```
Then open the pdf_agent directory and run
```bash
uvicorn tester:app --reload    
```

Open terminal in the bot-app folder and run
```bash
npm install
npm run dev
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

```


