import json

from sqlalchemy import Column, MetaData, Table, create_engine, Text, TIMESTAMP, func
from app.config import get_settings

config = get_settings()

pg_username = config.PG_USER
pg_password = config.PG_PASSWORD
pg_port = config.PG_PORT
pg_db = config.PG_DB

DATABASE_URL = f"postgresql+psycopg2://{pg_username}:{pg_password}@localhost:{pg_port}/{pg_db}"

engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()

chat_info = Table("chat_info", metadata, autoload_with=engine)

# 데이터 삽입, 수정
def upsert_chat(user_id: str, chat_id: str, messages: list[dict]):
    with engine.connect() as conn:
        messages_str = json.dumps(messages)

        existing_chat = conn.execute(chat_info.select().where(chat_info.c.chat_id == chat_id)).fetchone()
        if existing_chat:
            update_query = (
                chat_info.update()
                .where(chat_info.c.chat_id == chat_id)
                .values(messages=messages_str,
                        created_at=func.now())
            )
            conn.execute(update_query)
            conn.commit()
            print(f"기존 chat_id '{chat_id}'의 messages가 업데이트되었습니다!")
        else:
            # 새로운 행 삽입
            insert_query = chat_info.insert().values(
                user_id=user_id,
                chat_id=chat_id,
                messages=messages_str
            )
            conn.execute(insert_query)
            conn.commit()
            print("새로운 데이터가 삽입되었습니다!")


# 데이터 조회
def get_chats(user_id: str, chat_id: str):
    with engine.connect() as conn:
        select_query = chat_info.select().where(
            chat_info.c.user_id==user_id,
            chat_info.c.chat_id==chat_id
        )
        result = conn.execute(select_query)

        for rows in result:
            messages = json.loads(rows.messages)
            print(f"User ID: {rows.user_id}, Chat ID: {rows.chat_id}, Messages: {messages}, Created At: {rows.created_at}")


# 실행
if __name__ == "__main__":
    upsert_chat("test_user_id2", "test_chat_id2", [{"role": "user", "message": "너눈 누구냐냐!"}, {"role": "assistant", "message": "안녕하세요, 무엇을 도와드릴까요?"}])
    get_chats("test_user_id2", "test_chat_id2")