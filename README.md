# 🧠 LangChain Agent API with MongoDB & Gemini

A FastAPI-based backend for a **web research assistant** powered by **LangChain**, **Google Gemini**, and **Tavily Search**, with **MongoDB**-based session persistence.

> 🚀 Built for applications that require contextual, session-aware, and tool-augmented AI conversations.

---

## 📦 Features

* ✅ Conversational memory stored in MongoDB
* 🔍 Real-time web search using Tavily API
* 🤖 Gemini 2.5-powered agent via LangChain
* 🌐 CORS-enabled FastAPI endpoints
* 🧠 Context injection using system prompts
* 🛠 Tool calling agent execution via LangChain
* 🧪 Health check and session management

---

## 🔧 Environment Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install fastapi uvicorn python-dotenv \
    langchain langchain-community \
    langchain-google-genai langchain-mongodb \
    tavily-python
```

### 2. Set Environment Variables

Create a `.env` file:

```env
TAVILY_API_KEY=your_tavily_api_key
GOOGLE_API_KEY=your_google_api_key
MONGODB_URI=mongodb://localhost:27017
DB_NAME=chat_db
COLLECTION_NAME=chat_histories
```

---

## ▶️ Running the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

---

## 🧪 API Endpoints

### `POST /set_context`

Set initial context for a session. Creates a new session if `session_id` is not provided.

**Request:**

```json
{
  "context": {
    "user": "Ali",
    "topic": "machine learning"
  },
  "session_id": "optional-session-id"
}
```

**Response:**

```json
{
  "session_id": "generated-or-supplied-id",
  "status": "context_set"
}
```

---

### `POST /chat`

Send a message to the agent and get a response based on the current session.

**Request:**

```json
{
  "message": "What is LangChain?",
  "session_id": "your-session-id"
}
```

**Response:**

```json
{
  "response": "LangChain is a framework for...",
  "session_id": "your-session-id",
  "history": [
    { "role": "user", "content": "What is LangChain?" },
    { "role": "assistant", "content": "LangChain is a framework for..." }
  ]
}
```

---

### `GET /history/{session_id}`

Fetch the full message history for a given session.

**Response:**

```json
{
  "session_id": "abc-123",
  "history": [
    { "role": "system", "content": "Additional context..." },
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

---

### `GET /health`

Performs a health check including database connection.

**Response:**

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 📚 Project Structure

```
├── main.py              # Main FastAPI app
├── .env                 # API keys and configuration
├── requirements.txt     # Python dependencies
└── README.md            # You're here!
```

---

## 🛡️ Tech Stack

* **FastAPI** — Python web framework
* **LangChain** — LLM orchestration
* **Gemini 2.5** — Google Generative AI model
* **Tavily API** — Web search results
* **MongoDB** — Message history storage
* **Uvicorn** — ASGI server

---

## 🧠 Agent Logic

* Uses `ChatGoogleGenerativeAI` from LangChain
* Prompt template includes system message + message history + scratchpad
* Augmented with `TavilySearchResults` tool for live search
* Stateful using `MongoDBChatMessageHistory`

---

## 📌 TODO / Improvements

* [ ] Add user authentication
* [ ] Rate limiting and session expiry
* [ ] Frontend UI (React or Next.js)
* [ ] Advanced context injection (memory summarization)

