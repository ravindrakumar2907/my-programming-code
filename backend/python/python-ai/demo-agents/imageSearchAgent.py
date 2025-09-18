import os
import textwrap
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import BaseModel, Field
from colorama import Fore, Back, Style, init
from crewai.tools import BaseTool
from duckduckgo_search import DDGS
from datetime import date
# Initialize colorama
init(autoreset=True)

# --- LLM Configuration ---
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

gemini_llm = LLM(
    model="gemini/gemini-1.5-flash",
    temperature=0.7 
)


# --- Custom DuckDuckGo Image Search Tool ---
class ImageSearchInput(BaseModel):
    query: str = Field(description="The query to search for images on DuckDuckGo.")

class DuckDuckGoImageTool(BaseTool):
    name: str = "DuckDuckGo Image Tool"
    description: str = "A tool to search for images on DuckDuckGo and return a single image link."
    args_schema: BaseModel = ImageSearchInput

    def _run(self, query: str) -> str:
        with DDGS() as ddgs:
            results = [r for r in ddgs.images(
                keywords=query,
                region='wt-wt',
                safesearch='moderate',
                size=None,
                color=None,
                type_image=None,
                layout=None,
                license_image=None
            )]
            if results and len(results) > 0:
                # Return the thumbnail URL of the first image result
                return results[0]['thumbnail']
            else:
                return "No image found."

duckduckgo_image_tool = DuckDuckGoImageTool()

# --- CrewAI Setup ---
def create_crew():
    image_finder = Agent(
        role="Image Finder",
        goal="Find a single image link from the internet based on a user's query.",
        backstory="An expert at quickly and efficiently finding relevant images using the DuckDuckGo search engine. " \
        "It is focused on returning only the image link having image-link=<link> as result.",
        llm=gemini_llm,
        verbose=True,
        tools=[duckduckgo_image_tool]
    )

    find_image_task = Task(
        description=(
            "Based on the user's request: '{image_request}', "
            "use the 'DuckDuckGo Image Tool' to find a single image URL."
        ),
        expected_output="A single, valid image URL.",
        agent=image_finder
    )

    crew = Crew(
        agents=[image_finder],
        tasks=[find_image_task],
        process=Process.sequential,
        verbose=True
    )

    return crew

def run_agent():
    """Prompts for initial input and kicks off the Crew."""
    image_request = input(Style.BRIGHT + Fore.WHITE + "What kind of image are you looking for? " + Style.RESET_ALL)
    
    image_crew = create_crew()
    result = image_crew.kickoff(inputs={'image_request': image_request})
    
    print("\n" + Style.BRIGHT + Back.CYAN + "--- Final Crew Output ---" + Style.RESET_ALL)
    print(result)

if __name__ == "__main__":
    run_agent()