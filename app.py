import chainlit as cl
from  groq_trial2 import ask_hr_bot


@cl.on_chat_start
async def start():
    await cl.Message(
        content=(
            "👋 **Welcome to the Expert HR Assistant**\n\n"
            "Ask questions about employees, experience, departments, "
            "joining dates, exits, or HR insights.\n\n"
            "💡 _Examples:_\n"
            "- Who joined in 2022?\n"
            "- Show employees with more than 5 years of experience\n"
            "- List inactive employees"
        )
    ).send()


@cl.on_message
async def handle_message(message: cl.Message):
    user_question = message.content

    thinking = cl.Message(content="🤔 Thinking...")
    await thinking.send()

    try:
        result = ask_hr_bot(user_question)

        answer = result["answer"]
        sql = result["sql"]
        tokens = result["tokens"]

        # Main Answer
        await cl.Message(
            content=f"### 🤖 Answer\n{answer}"
        ).send()

        # SQL (Collapsible)
        await cl.Message(
            content=f"```sql\n{sql}\n```",
            author="🧠 Generated SQL"
        ).send()

        # Token Usage (Collapsible style)
        await cl.Message(
            content=(
                "### 📊 Token Usage\n"
                f"- **SQL Generation:** {tokens['sql_generation']}\n"
                f"- **Answer Generation:** {tokens['answer_generation']}\n"
                f"- **Grand Total:** **{tokens['grand_total']} tokens**"
            ),
            author="📈 System"
        ).send()

    except Exception as e:
        await cl.Message(
            content=f"❌ **Error:** {str(e)}"
        ).send()
