from crewai.tools import BaseTool

class GenerateKayakURLTool(BaseTool):
    name: str = "Generate Kayak URL"
    description: str = "Generate a Kayak flight search URL."

    def _run(self, origin: str, destination: str, date: str) -> str:
        # Replace spaces with hyphens for URLs
        origin_clean = origin.replace(" ", "-")
        destination_clean = destination.replace(" ", "-")
        return f"https://www.kayak.com/flights/{origin_clean}-{destination_clean}/{date}"

# Tool instance
generate_kayak_url_tool = GenerateKayakURLTool()
