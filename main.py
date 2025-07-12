from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder  # Added this import
import uvicorn
import uuid  # Added this import
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
import os
from dotenv import load_dotenv

load_dotenv()

# Environment variables
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "chat_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "chat_histories")

# FastAPI app
app = FastAPI(
    title="LangChain Agent API with MongoDB",
    description="API for a web research assistant with conversation persistence",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # For continuing existing conversations

class ChatResponse(BaseModel):
    response: str
    session_id: str
    history: List[dict]

# Initialize the agent
def create_search_agent():
    search = TavilySearchResults()
    tools = [search]
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful web research assistant. 
        Use the provided tools to search for up-to-date information when needed. 
        Be concise but thorough in your responses."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

agent = create_search_agent()

def get_message_history(session_id: str) -> MongoDBChatMessageHistory:
    return MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=MONGO_URI,
        database_name=DB_NAME,
        collection_name=COLLECTION_NAME,
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Generate a session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get message history from MongoDB
        message_history = get_message_history(session_id)
        
        # Get agent response
        response = agent.invoke({
            "input": request.message,
            "chat_history": message_history.messages
        })
        
        # Add messages to history
        message_history.add_user_message(request.message)
        message_history.add_ai_message(response['output'])
        
        # Format history for response
        formatted_history = []
        for msg in message_history.messages:
            if isinstance(msg, HumanMessage):
                formatted_history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted_history.append({"role": "assistant", "content": msg.content})
        
        return ChatResponse(
            response=response['output'],
            session_id=session_id,
            history=formatted_history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    try:
        message_history = get_message_history(session_id)
        formatted_history = []
        for msg in message_history.messages:
            if isinstance(msg, HumanMessage):
                formatted_history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted_history.append({"role": "assistant", "content": msg.content})
        return {"session_id": session_id, "history": formatted_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        # Simple check to verify MongoDB connection
        test_history = get_message_history("health_check")
        test_history.add_user_message("ping")
        test_history.clear()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "healthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000,host="0.0.0.0")