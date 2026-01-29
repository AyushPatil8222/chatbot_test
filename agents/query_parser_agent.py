from crewai import Agent

query_parser_agent = Agent(
    role="Query Parser",
    goal="Extract structured flight search info from a user query",
    backstory="Expert at parsing travel queries into origin, destination, and date",
    llm="ollama/deepseek-r1:latest",
    verbose=True
)
