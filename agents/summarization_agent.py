from crewai import Agent

summarization_agent = Agent(
    role="Summarization Agent",
    goal="Summarize flight options in a clear, user-friendly way",
    backstory="Travel assistant",
    llm="ollama/deepseek-r1:latest",
    verbose=True
)
