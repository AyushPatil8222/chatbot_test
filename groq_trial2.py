import pymssql
import re
import json
from datetime import date, datetime
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

FORBIDDEN_SQL_PATTERN = r"\b(insert|update|delete|drop|alter|truncate|exec|merge|create)\b"

client = Groq(api_key=GROQ_API_KEY)

def groq_call(prompt, temperature=0):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a precise enterprise HR assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def get_connection():
    return pymssql.connect(
        server=DB_SERVER,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        timeout=30
    )

def load_schema():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """)
    schema = {}
    for table, column in cursor.fetchall():
        schema.setdefault(table, []).append(column)
    conn.close()
    return schema

def sanitize_sql(sql: str) -> str:
    sql = re.sub(r"```sql|```", "", sql, flags=re.IGNORECASE)
    sql = sql.replace("`", "").strip()
    return sql

def validate_sql(sql: str):
    sql_lower = sql.lower().strip()
    if not sql_lower.startswith("select"):
        raise ValueError("Only SELECT queries allowed")
    if re.search(FORBIDDEN_SQL_PATTERN, sql_lower):
        raise ValueError("Unsafe SQL detected")

def generate_sql(question: str, schema: dict) -> str:
    schema_text = "\n".join(f"{table}({', '.join(cols)})" for table, cols in schema.items())
    prompt = f"""
You are an expert SQL Server developer.
Database Schema:
{schema_text}
User Question:
{question}
Return ONLY the raw SQL.
"""
    raw_sql = groq_call(prompt, temperature=0)
    sql = sanitize_sql(raw_sql)
    validate_sql(sql)
    return sql

def execute_sql(sql: str):
    validate_sql(sql)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]

def calculate_experience(joining_date):
    if not joining_date:
        return "N/A"
    if isinstance(joining_date, datetime):
        joining_date = joining_date.date()
    today = date.today()
    delta = today - joining_date
    years = delta.days // 365
    months = (delta.days % 365) // 30
    return f"{years} years {months} months"

def generate_answer(question: str, data: list):
    prompt = f"""
You are a senior HR assistant.
Question:
{question}
Database Result:
{json.dumps(data, default=str)}
Rules:
- Give concise, human-readable answers
- If multiple rows, use numbered list
"""
    return groq_call(prompt)

def ask_hr_bot(question: str):
    schema = load_schema()
    sql = generate_sql(question, schema)
    data = execute_sql(sql)
    answer = generate_answer(question, data)
    return {
        "sql": sql,
        "answer": answer,
        "raw_data": data
    }
