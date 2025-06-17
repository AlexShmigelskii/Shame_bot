from openai import AsyncOpenAI
import json
import sqlite3
from datetime import datetime, timedelta
from secret import OPENAI_API_KEY, GPT_MODEL, GPT_PROMPT_PATH, MAX_CONTEXT_MESSAGES

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

def get_system_prompt():
    """Читает системный промпт из файла"""
    try:
        with open(GPT_PROMPT_PATH, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return "Ты — эксперт по ресторанам Москвы. Рекомендуй заведения по категории и району."

def init_context_db():
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()
    
    # Создаем таблицу для хранения контекста диалогов
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_contexts
                    (user_id INTEGER,
                     message_role TEXT,
                     message_content TEXT,
                     timestamp DATETIME,
                     PRIMARY KEY (user_id, timestamp))''')
    
    # Индекс для быстрого поиска по user_id и timestamp
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_context_user_time ON chat_contexts(user_id, timestamp)')
    
    conn.commit()
    conn.close()

async def get_chat_context(user_id: int) -> list:
    """Получает последние сообщения контекста для пользователя"""
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()
    
    # Удаляем старые сообщения (старше 24 часов)
    cursor.execute('''DELETE FROM chat_contexts 
                     WHERE timestamp < ?''', 
                     (datetime.now() - timedelta(hours=24),))
    
    # Получаем последние сообщения
    cursor.execute('''SELECT message_role, message_content 
                     FROM chat_contexts 
                     WHERE user_id = ? 
                     ORDER BY timestamp DESC 
                     LIMIT ?''', 
                     (user_id, MAX_CONTEXT_MESSAGES))
    
    messages = [{"role": role, "content": content} 
               for role, content in cursor.fetchall()]
    
    conn.commit()
    conn.close()
    
    # Добавляем системный промпт в начало
    messages.insert(0, {"role": "system", "content": get_system_prompt()})
    
    return messages

async def save_chat_context(user_id: int, role: str, content: str):
    """Сохраняет новое сообщение в контекст"""
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO chat_contexts (user_id, message_role, message_content, timestamp)
                     VALUES (?, ?, ?, ?)''',
                     (user_id, role, content, datetime.now()))
    
    conn.commit()
    conn.close()

async def get_gpt_recommendations(establishments: list, category: str, cuisine: str, user_id: int) -> list[str]:
    """Отправляет список заведений ИИ для сортировки и возвращает отсортированный список названий."""
    places_json = json.dumps(establishments, ensure_ascii=False)
    user_message = (
        f'Отсортируй этот список заведений: {places_json}\n'
        f'Фильтры: Категория - "{category}", Кухня - "{cuisine}".\n'
        f'Верни только JSON-массив отсортированных названий.'
    )
    messages = await get_chat_context(user_id)
    messages.append({"role": "user", "content": user_message})
    try:
        response = await client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=1500,
        )
        response_text = response.choices[0].message.content
        await save_chat_context(user_id, "user", user_message)
        await save_chat_context(user_id, "assistant", response_text)
        try:
            sorted_names = json.loads(response_text)
            if not isinstance(sorted_names, list):
                # Если ответ не список, возвращаем исходный порядок
                return [p['name'] for p in establishments]
            return sorted_names
        except (json.JSONDecodeError, TypeError):
             # В случае ошибки парсинга или если ответ не JSON, возвращаем исходный порядок
            return [p['name'] for p in establishments]
    except Exception:
        # В случае ошибки API, возвращаем исходный порядок
        return [p['name'] for p in establishments] 