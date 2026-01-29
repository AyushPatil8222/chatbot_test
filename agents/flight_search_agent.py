from crewai import Agent

flight_search_agent = Agent(
    role="Flight Search Agent",
    goal="Generate a Kayak URL and extract the top 5 flights using available tools",
    backstory="Expert at using Kayak and extracting flight info",
    llm="ollama/deepseek-r1:7b",
    verbose=True
)
