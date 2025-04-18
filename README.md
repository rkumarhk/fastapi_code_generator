# 🚀 FastAPI Project Generator

## Overview
An intelligent FastAPI project generator that transforms Software Requirements Specifications (SRS) into production-ready project structures using AI-powered analysis and LangGraph workflows.

## ✨ Key Features
- 📄 **Automated Project Generation**: Convert SRS documents into fully structured FastAPI projects
- 🎯 **Scalable Architecture**: Built with FastAPI for high performance and scalability
- 🧠 **AI-Powered**: Utilizes LangGraph for intelligent code generation and project structuring
- 🔄 **Iterative Refinement**: Continuous improvement through feedback loops

## 🛠 Tech Stack
- **Python**: 3.11+
- **FastAPI**: Modern, high-performance web framework
- **LangGraph**: Advanced language processing and project generation
- **Groq**: AI model integration for code generation

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Git
- PostgreSQL (optional)

### 🔧 Installation

1. **Clone the repository**
```bash
git clone https://github.com/rkumarhk/fastapi_code_generator
cd fastapi_code_generator
```

2. **Set up virtual environment**
```bash
# Windows
python -m venv my-env
my-env\Scripts\activate

# Linux/macOS
python -m venv my-env
source my-env/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 🚀 Running the Server
```bash
uvicorn main:app --reload --port 8000
```

## 📖 Usage

### Generate Project from SRS
1. Prepare your SRS document in `.docx` format
2. Use the API endpoint to generate your project:
```bash
curl -X POST "http://localhost:8000/upload/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_srs.docx"
```

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🙏 Acknowledgments
- FastAPI community
- LangGraph developers
- Groq API team

---
<div align="center">
Made with ❤️ by Rohit Kumar
</div>
