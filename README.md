# MediBot 

A sophisticated medical assistant application powered by LangChain, LangGraph, and advanced language models. MediBot provides intelligent medical information retrieval, analysis, and guidance through multiple pathways including Retrieval-Augmented Generation (RAG), web search, and conversational AI.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [API Overview](#api-overview)
- [Database](#database)

## Features

✨ **Core Capabilities:**

- **Intelligent Routing**: Automatically routes queries to the most appropriate processing pathway
- **Document Analysis**: Upload and analyze medical PDFs with semantic chunking and vector embeddings
- **Web Search**: Retrieve latest medical information and clinical guidelines from trusted sources
- **Conversational AI**: Direct medical question answering with trained medical knowledge
- **User Authentication**: Secure login and registration system with password hashing
- **Session Management**: Persistent chat history with Redis-backed checkpointing
- **Medical Gatekeeper**: Filters non-medical queries and maintains focus on medical topics

## Architecture

MediBot uses a **LangGraph state machine** architecture with the following workflow:

```
User Input
    ↓
[Retriever] - Load PDF files if provided
    ↓
[Router] - Intelligent decision engine
    ├→ [RAG] - Document-based retrieval
    ├→ [Search] - Web search via Tavily
    └→ [LLM] - Direct conversational response
    ↓
Output
```

### Key Components:

1. **State Management**: Tracks conversation flow, documents, retrieval status, and search history
2. **Router/Supervisor**: Determines optimal path based on query type and available resources
3. **RAG Pipeline**: Semantic chunking + vector embeddings + retrieval chains
4. **Search Module**: Tavily integration for real-time medical information
5. **Authentication Layer**: PostgreSQL-backed user management with bcrypt hashing
6. **Checkpointing**: Redis-based conversation persistence for session resumption

## Project Structure

```
medibot/
├── app.py                 # Core LangGraph application logic
├── chainlit-test.py       # Chainlit UI integration and routing
├── user.py               # User authentication and database models
├── register.py           # Streamlit registration UI
├── chainlit.md           # Welcome screen for Chainlit interface
└── README.md             # This file
```

### File Descriptions:

**app.py**
- Defines the `AgentState` TypedDict with conversation and document state
- Implements graph nodes: `retrieve`, `supervisor_router`, `process_uploaded_file`, `search`, `chatbot`
- Contains routing logic for medical vs non-medical queries
- Manages RAG pipeline with semantic chunking and Chroma vectorstore
- Handles web search via Tavily API

**chainlit-test.py**
- Chainlit framework integration
- User session management
- Password authentication callback
- File upload handling
- Message streaming and callback management
- Database thread cleanup

**user.py**
- SQLAlchemy ORM models for user management
- User registration with email validation
- Password hashing with bcrypt
- Login authentication
- PostgreSQL database engine configuration

**register.py**
- Streamlit UI for user registration and login
- Two-tab interface: Login and Register
- Form validation and error handling
- Integration with user authentication system

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Redis server (for session checkpointing)
- OpenAI API key
- Tavily API key (for web search)

## Installation

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd medibot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb test

# Ensure PostgreSQL is running
# The User model will auto-create tables on first run
```

### 3. Redis Setup

```bash
# Use Docker with Redis Stack
docker run -d --name redis-stack -p 6380:6379 -p 8002:8001 redis/redis-stack:latest

# Verify Redis is running on port 6380
redis-cli -p 6380 ping  # Should return PONG
```

Redis Stack includes Redis and RedisInsight (web UI available at `http://localhost:8002`)

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Tavily Search Configuration
TAVILY_API_KEY=your_tavily_api_key

# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test

# Redis Configuration
REDIS_URL=redis://localhost:6380
```

### Database Credentials (user.py)

The database credentials are currently hardcoded in `user.py` and `chainlit-test.py`:

```python
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "test"
```

**Security Note**: Consider moving these to environment variables in production.

## Usage

### Option 1: Run Chainlit Interface (Recommended)

```bash
# Terminal 1: Ensure Redis is running
redis-server

# Terminal 2: Run Chainlit
python chainlit-test.py
# Or directly:
chainlit run chainlit-test.py -w
```

Access at: `http://localhost:8000`

### Option 2: Streamlit Registration Interface

```bash
streamlit run register.py
```

Access at: `http://localhost:8501`

The Streamlit app provides registration and links to the Chainlit interface.

## How It Works

### User Query Flow:

1. **Authentication**: User logs in via password authentication
2. **File Upload** (Optional): Medical PDF files are uploaded and stored
3. **Retrieval Node**: PDFs are processed using:
   - PyPDFLoader for extraction
   - SemanticChunker for intelligent splitting
   - OpenAI embeddings for vectorization
   - Chroma vectorstore for retrieval
4. **Router Decision**: Query is evaluated for:
   - Medical relevance (out-of-scope filtering)
   - Document availability (RAG eligibility)
   - Previous search usage
   - Optimal pathway selection
5. **Processing**:
   - **RAG Path**: Retrieves relevant document chunks and generates answer
   - **Search Path**: Uses Tavily to find latest medical information
   - **LLM Path**: Answers from training data and context
6. **Response Streaming**: Answers are streamed token-by-token to user
7. **Session Persistence**: Conversation saved to Redis for history and resumption

### Router Logic:

```
Is Question Medical?
├─ No → Return "out_of_scope" refusal
└─ Yes → Check Available Resources
    ├─ Files Available & Not Yet Used → RAG
    ├─ Search Not Used Yet → Search
    └─ Otherwise → LLM Direct Answer
```

## API Overview

### Core Functions (app.py)

**`retrieve(state)`**
- Loads and processes PDF documents
- Creates semantic chunks
- Builds vector embeddings
- Returns retriever object

**`supervisor_router(state)`**
- Routes queries to appropriate handler
- Checks medical relevance
- Manages search and RAG usage tracking
- Returns Command directing to next node

**`process_uploaded_file(state)`**
- Executes RAG pipeline
- Retrieves relevant document context
- Generates document-grounded responses

**`search(state)`**
- Performs web search via Tavily
- Uses research agent for synthesis
- Returns structured findings

**`chatbot(state)`**
- Direct LLM-based responses
- Medical knowledge from training data
- Includes safety constraints

### Chainlit Callbacks (chainlit-test.py)

**`@cl.on_chat_start`**: Initialize app for new conversations

**`@cl.on_message`**: Handle incoming user messages

**`@cl.on_chat_end`**: Cleanup database threads

**`@cl.password_auth_callback`**: Authenticate users

**`@cl.on_chat_resume`**: Restore conversation state

## Database

### PostgreSQL Schema

**users table** (auto-created by SQLAlchemy)
- `id` (UUID): Primary key
- `identifier` (Text): Unique username
- `first_name`, `last_name` (String)
- `email` (String): Unique email
- `age` (Integer)
- `password` (String): bcrypt hashed
- `metadata` (JSONB): Additional user data
- `createdAt` (Text): Timestamp

**threads table** (Chainlit managed)
- Stores conversation sessions
- Indexed by `userId`, `userIdentifier`
- Cleanup removes orphaned threads

## Configuration Parameters

### LLM Model (app.py)
```python
llm = ChatOpenAI(model="gpt-4.1-nano-2025-04-14")
```

### Semantic Chunker Settings
```python
SemanticChunker(
    embedder, 
    breakpoint_threshold_type="standard_deviation",
    breakpoint_threshold_amount=1.5
)
```

### Tavily Search Configuration
```python
TavilySearch(
    search_depth='advanced',
    max_results=5,
    time_range='year'
)
```

## Troubleshooting

**Connection Refused - Redis**
```
Error: Connection refused on port 6380
Solution: Ensure Redis is running (redis-server or docker container)
```

**PostgreSQL Connection Error**
```
Error: Could not connect to database
Solution: Verify PostgreSQL is running and credentials in .env are correct
```

**File Not Found**
```
Error: File not found for PDF processing
Solution: Ensure PDF is uploaded to the correct .files/{session_id} directory
```

**OpenAI API Error**
```
Error: Invalid API key
Solution: Verify OPENAI_API_KEY is set correctly in .env
```

## License

This project is part of LangChain experiments. See LICENSE for details.

---

**Built with**: LangChain • LangGraph • Chainlit • Streamlit • PostgreSQL • Redis
