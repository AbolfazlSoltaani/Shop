import json

from sqlalchemy.orm import Session
import openai
from db import SessionLocal, ChatSession, ChatMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to start a new chat session or retrieve an existing one
def get_or_create_session(db: Session, user_id: str) -> ChatSession:
    session = db.query(ChatSession).filter(ChatSession.user_id == user_id).first()
    if not session:
        session = ChatSession(user_id=user_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


# Function to store messages in the database
def store_message(db: Session, session_id: int, sender: str, content: str) -> None:
    message = ChatMessage(session_id=session_id, sender=sender, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)


# Main function to handle chat and call OpenAI API
async def chat_with_openai(request: dict, db: Session):
    user_id = request["user_id"]
    user_message = request["message"]

    # Retrieve or create a new chat session
    session = get_or_create_session(db, user_id)

    # Store the user's message in the session
    store_message(db, session.id, "user", user_message)

    # Prepare the conversation history
    messages = [{"role": "user", "content": user_message}]
    for message in session.messages:
        messages.append({"role": message.sender, "content": message.content})

    # Define the function to be called by OpenAI
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_products",
                "description": "Search for products based on a query and optional filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query, e.g., 'laptop'.",
                        },
                        "filters": {
                            "type": "string",
                            "description": "Optional filters for the search, e.g., 'price>1000'.",
                        },
                    },
                    "required": ["query", "filters"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
    ]

    # Call OpenAI API with the current chat history
    response = openai.chat.completions.create(
        messages=messages,
        tools=tools,
        model="gpt-3.5-turbo",
    )

    if response.choices[0].finish_reason == "tool_calls":
        function_args_str = response.choices[0].message.tool_calls[0].function.arguments
        function_args = json.loads(function_args_str)
        return {"query": function_args.get("query"), "searchParams": function_args}

    else:
        openai_message = response.choices[0].message.content
        store_message(db, session.id, "assistant", openai_message)
        return {"response": openai_message}
