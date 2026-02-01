from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import HumanMessage
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from rag import main
import chainlit as cl
from chainlit.types import ThreadDict
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from user import engine, login_user

Session = sessionmaker(bind=engine)

DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "test"


@cl.on_chat_start
async def on_chat_start():
    app_user = cl.user_session.get("user")
    app = await main()
    cl.user_session.set("app", app)
    await cl.Message(content=f"Hello {app_user.identifier}, I'm ready to help!").send()

@cl.data_layer
def data_layer():
    return SQLAlchemyDataLayer(
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    user = login_user(username, password)
    if user:
        return cl.User(identifier=user.username , display_name=user.username, metadata={"email": user.email, "first_name": user.first_name, "last_name": user.last_name , "age": user.age})
    else:
        return None

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    app = await main()
    cl.user_session.set("app", app)


@cl.on_message
async def on_message(message: cl.Message):
    def get_latest_file(directory, extension = "pdf"):
        dir_path = Path(directory)
        files = dir_path.glob(f"*.{extension}")
        
        try:
            latest_file = max(files, key=lambda f: f.stat().st_mtime)
            return latest_file
        except ValueError:
            return None
    result = get_latest_file(f".files/{cl.context.session.id}")
    msg = cl.Message(content="")
    app = cl.user_session.get("app")
    app_user = cl.user_session.get("user")
    config = {"configurable": {"thread_id": cl.context.session.thread_id} , "user_id" : app_user.id}
    input_data = {"messages": [HumanMessage(content=message.content)],'documents':[],'file_path':str(result) if result else ''}
    
    chunks = app.astream(
        input_data,
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler(stream_final_answer=True)],**config),
        stream_mode="messages"
    )

    async for chunk, metadata in chunks:
        cl.logger.info(f"Chunk received: {chunk} with metadata: {metadata}")
        if chunk.content and metadata["langgraph_node"] == "LLM":
            await msg.stream_token(chunk.content)       
    await msg.update()

if __name__ == "__main__":
    import sys
    import subprocess
    subprocess.run(
            [sys.executable, "-m", "chainlit", "run", "chainlit_test.py", "-w" ], 
            cwd="/home/jimmy/Documents/my_langchain_experiments/medibot"
        )