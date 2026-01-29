# main.py
import datetime
from crewai import Crew, Task
from agents.query_parser_agent import query_parser_agent
from agents.flight_search_agent import flight_search_agent
from agents.summarization_agent import summarization_agent
from tools.kayak_tool import generate_kayak_url_tool
from tools.browser_tool import search_flights

# -----------------------
# Step 1: User Input (only change here)
# -----------------------
user_query = input("Please enter your flight query (e.g., 'LA to Boston on 22 January 2026'): ")

# -----------------------
# Step 2: Parse Query Task
# -----------------------
parse_task = Task(
    description=f"Parse this query: {user_query}",
    expected_output="origin, destination, date",
    agent=query_parser_agent,
)

# -----------------------
# Step 3: Generate Kayak URL Task
# -----------------------
generate_url_task = Task(
    description="Generate a Kayak URL for the flight search",
    expected_output="url",
    agent=flight_search_agent,
    tools=[generate_kayak_url_tool],
    input_variables=lambda output: {
        "origin": output['origin'],
        "destination": output['destination'],
        "date": output['date']
    }
)

# -----------------------
# Step 4: Search Flights Task
# -----------------------
search_task = Task(
    description="Search flights on Kayak using the URL",
    expected_output="A list of 5 flight options with airline, price, duration, and stops",
    agent=flight_search_agent,
    tools=[search_flights],
    input_variables=lambda output: {
        # Append timestamp to make URL unique and avoid Crew input reuse errors
        "url": f"{output['url']}?uid={datetime.datetime.now().timestamp()}"
    }
)

# -----------------------
# Step 5: Summarization Task
# -----------------------
summary_task = Task(
    description="Summarize the flight options in a clear, user-friendly way",
    expected_output="A concise summary comparing all flight options",
    agent=summarization_agent,
)

# -----------------------
# Step 6: Create Crew
# -----------------------
crew = Crew(
    agents=[query_parser_agent, flight_search_agent, summarization_agent],
    tasks=[parse_task, generate_url_task, search_task, summary_task],
    verbose=True
)

# -----------------------
# Step 7: Run Crew
# -----------------------
result = crew.kickoff()
print(result)
