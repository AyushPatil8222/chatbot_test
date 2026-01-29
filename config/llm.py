from crewai import LLM

llm = LLM(
    model="ollama/deepseek-r1:7b",
    temperature=0.1
)
