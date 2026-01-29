# app.py
import datetime
import chainlit as cl
from crewai import Crew, Task

from agents.query_parser_agent import query_parser_agent
from agents.flight_search_agent import flight_search_agent
from agents.summarization_agent import summarization_agent

from tools.kayak_tool import generate_kayak_url_tool
from tools.browser_tool import search_flights


# ---------------------------------------------------------
# App Start
# ---------------------------------------------------------
@cl.on_chat_start
async def start():
    # Sidebar content
    await cl.Message(
        content="""
### 🧩 Browserbase Configuration
[Get your API key](https://www.browserbase.com)

Enter your Browserbase API key below.
""",
        author="system",
    ).send()

    # Main header
    await cl.Message(
        content="""
## ✈️ **FlightFinder Pro**
Powered by **Browserbase** and **CrewAI**
---
""",
    ).send()

    # Search UI (form-like)
    await cl.Message(
        content="""
### 🔍 Search for Flights

**Origin City**  
`SF`

**Destination City**  
`New York`

**Departure Date**  
`2026-01-22`

➡️ Type your query like:  
`SF to New York on 22 January 2026`
""",
    ).send()


# ---------------------------------------------------------
# Handle User Input
# ---------------------------------------------------------
@cl.on_message
async def handle_message(message: cl.Message):
    user_query = message.content.strip()

    # -----------------------
    # Task 1: Parse Query
    # -----------------------
    with cl.Step("🧠 Parsing flight query"):
        parse_task = Task(
            description=f"Parse this query: {user_query}",
            expected_output="origin, destination, date",
            agent=query_parser_agent,
        )

    # -----------------------
    # Task 2: Generate URL
    # -----------------------
    with cl.Step("🔗 Generating Kayak URL"):
        generate_url_task = Task(
            description="Generate a Kayak URL for the flight search",
            expected_output="url",
            agent=flight_search_agent,
            tools=[generate_kayak_url_tool],
            input_variables=lambda output: {
                "origin": output["origin"],
                "destination": output["destination"],
                "date": output["date"],
            },
        )

    # -----------------------
    # Task 3: Search Flights
    # -----------------------
    with cl.Step("🔍 Searching flights"):
        search_task = Task(
            description="Search flights on Kayak using the URL",
            expected_output="5 flight options",
            agent=flight_search_agent,
            tools=[search_flights],
            input_variables=lambda output: {
                "url": f"{output['url']}?uid={datetime.datetime.now().timestamp()}"
            },
        )

    # -----------------------
    # Task 4: Summarize
    # -----------------------
    with cl.Step("📝 Summarizing results"):
        summary_task = Task(
            description="Summarize flight options clearly",
            expected_output="User-friendly comparison",
            agent=summarization_agent,
        )

    # -----------------------
    # Run Crew
    # -----------------------
    crew = Crew(
        agents=[
            query_parser_agent,
            flight_search_agent,
            summarization_agent,
        ],
        tasks=[
            parse_task,
            generate_url_task,
            search_task,
            summary_task,
        ],
        verbose=True,
    )

    with cl.Step("🚀 Running FlightFinder Pro"):
        result = crew.kickoff()

    await cl.Message(
        content=f"""
### ✅ Best Flight Options

{result}

---
**About FlightFinder Pro**  
This application uses AI agents to search flights and find the best deals for you.
"""
    ).send()
