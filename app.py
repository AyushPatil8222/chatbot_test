import chainlit as cl
from groq_trial2 import ask_hr_bot

@cl.on_chat_start
async def start():
    await cl.Message(
        content=(
            "🤖 **HR Intelligence Assistant**\n\n"
            "Ask HR questions in natural language:\n"
            "- Employees with more than 5 years experience\n"
            "- List active employees by department\n"
            "- Recently joined employees\n\n"
            "_Only safe, read-only SQL queries executed._"
        ),
        author="HR Bot"
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    question = message.content.strip()
    
    if not question:
        await cl.Message("❌ Please enter a valid question.").send()
        return
    
    thinking = cl.Message(content="⏳ Thinking like an HR expert...")
    await thinking.send()
    
    try:
        result = ask_hr_bot(question)
        
        await cl.Message(
            content=f"🤖 **Answer**\n\n{result['answer']}",
            author="HR Bot"
        ).send()
        
        await cl.Message(
            content=f"```sql\n{result['sql']}\n```",
            author="Generated SQL"
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ **Error:** {str(e)}"
        ).send()
