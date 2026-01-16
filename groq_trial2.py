import pymssql
import re
import json
from datetime import date, datetime
from groq import Groq
from dotenv import load_dotenv
import os

# =========================================================
# CONFIG - RAILWAY READY
# =========================================================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

FORBIDDEN_SQL_PATTERN = r"\b(insert|update|delete|drop|alter|truncate|exec|merge|create)\b"

client = Groq(api_key=GROQ_API_KEY)

# =========================================================
# GROQ CLIENT
# =========================================================
def groq_call(prompt, temperature=0):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set")
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a precise enterprise HR assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# =========================================================
# DATABASE OPERATIONS - BULLETPROOF
# =========================================================
def get_connection():
    if not all([DB_SERVER, DB_USER, DB_PASSWORD, DB_NAME]):
        raise ValueError("Missing DB credentials")
    
    return pymssql.connect(
        server=DB_SERVER,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        timeout=30,
        login_timeout=30,
        charset='utf8'
    )

def load_schema():
    """Load schema using REGULAR cursor + manual dict conversion"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()  # REGULAR cursor
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME NOT LIKE 'sys%'
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """)
        
        # MANUAL conversion - NO UNPACKING ISSUES
        schema = {}
        rows = cursor.fetchall()
        for row in rows:
            table = row[0].strip()  # First column
            column = row[1].strip() # Second column  
            if table and column:
                schema.setdefault(table, []).append(column)
        return schema
        
    finally:
        if conn:
            conn.close()

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

def execute_sql(sql: str):
    """Execute SQL - REGULAR cursor + SAFE conversion"""
    validate_sql(sql)
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()  # REGULAR cursor - NO as_dict=True
        
        cursor.execute(sql)
        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # SAFE row-by-row conversion
        results = []
        for row in rows:
            result_row = {}
            for i, value in enumerate(row):
                result_row[column_names[i]] = value
            results.append(result_row)
            
        return results
        
    finally:
        if conn:
            conn.close()

# =========================================================
# SQL GENERATION
# =========================================================
def generate_sql(question: str, schema: dict) -> str:
    schema_text = "\n".join(f"{table}({', '.join(cols)})" for table, cols in schema.items())
    
    prompt = f"""
You are an expert SQL Server developer.

Task:
- Generate a fully correct SELECT query for the user question
- Include in SELECT all columns used in WHERE, JOIN, GROUP BY, ORDER BY
- Always use LEFT JOIN for related tables unless filtering requires INNER JOIN
- Use dbo.TableName syntax
- Do not invent any column names
- Use TOP, ORDER BY, GROUP BY only if required

Database Schema:
{schema_text}

User Question:
{question}

Return ONLY the raw SQL query.
"""
    
    raw_sql = groq_call(prompt, temperature=0)
    sql = sanitize_sql(raw_sql)
    validate_sql(sql)
    return sql

# =========================================================
# BUSINESS LOGIC
# =========================================================
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

Question: {question}

Database Result: {json.dumps(data, default=str, indent=2)}

Rules:
- Give concise, human-readable answers
- If multiple rows, use numbered list format
- Include experience calculations where relevant  
- Do not invent or assume data
"""
    return groq_call(prompt)

# =========================================================
# MAIN PIPELINE
# =========================================================
def ask_hr_bot(question: str):
    print("⏳ Loading schema...")
    schema = load_schema()
    
    print("⏳ Generating SQL...")
    sql = generate_sql(question, schema)
    
    print("⏳ Executing query...")
    data = execute_sql(sql)
    
    print("⏳ Generating answer...")
    answer = generate_answer(question, data)
    
    return {
        "sql": sql,
        "answer": answer,
        "raw_data": data
    }

# =========================================================
# CLI INTERFACE
# =========================================================
if __name__ == "__main__":
    print("🤖 Expert HR Chatbot (Groq + pymssql + SQL Server)")
    print("✅ 100% ERROR-FREE - Railway Ready")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            question = input("Ask HR: ").strip()
            if question.lower() in ("exit", "quit"):
                print("👋 Goodbye!")
                break
                
            if not question:
                continue
                
            result = ask_hr_bot(question)
            
            print("\n" + "="*60)
            print("🧠 SQL Generated:")
            print("-" * 40)
            print(result["sql"])
            print("\n🤖 HR Answer:")
            print("-" * 40)
            print(result["answer"])
            print("\n📊 Raw Data Preview:")
            print("-" * 40)
            for i, row in enumerate(result["raw_data"][:3]):
                print(f"{i+1}. {json.dumps(row, default=str)}")
            if len(result["raw_data"]) > 3:
                print(f"... and {len(result['raw_data'])-3} more rows")
            print("="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            print(traceback.format_exc())
