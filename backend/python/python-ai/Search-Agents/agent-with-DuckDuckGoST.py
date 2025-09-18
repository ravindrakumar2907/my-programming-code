import os
from crewai import tools
#from langchain_community.tools import DuckDuckGoSearchRun
import os
from typing import List, Dict, Any, Union
from crewai import Agent, Task, Crew, Process, LLM
from ddgs import DDGS
from pptx import Presentation
from pptx.util import Pt
from config import Config

@tool("DuckDuckGoSearch")
def search_tool(query: str):
    """Searches the web for information on a given topic."""
    return DuckDuckGoSearchRun().run(query)

# Define your agents
# The researcher agent is given access to the search tool
researcher = Agent(
    role='Senior Research Analyst',
    goal='Uncover new and interesting developments in a specific field.',
    backstory=(
        "You are a Senior Research Analyst with a talent for digging up "
        "the most relevant and up-to-date information on any topic. "
        "Your insights are sharp and your data is always accurate."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[search_tool]
)

writer = Agent(
    role='Tech Content Writer',
    goal='Create a concise and engaging summary from research findings.',
    backstory=(
        "You are a skilled Tech Content Writer, able to take complex research "
        "and distill it into a simple, easy-to-read summary for a blog post. "
        "You have a knack for making technical topics accessible."
    ),
    verbose=True,
    allow_delegation=True
)

# Define the tasks for the agents
research_task = Task(
    description=(
        "Search the internet for the latest advancements in AI and robotics. "
        "Focus on breakthroughs in the last 6 months. "
        "Your final report must be a detailed summary of at least 3 key findings."
    ),
    expected_output='A detailed report with at least three key AI/robotics advancements.',
    agent=researcher
)

writing_task = Task(
    description=(
        "Using the research findings provided by the Senior Research Analyst, "
        "write a short, engaging, and easy-to-understand blog post. "
        "The blog post should be at least 3 paragraphs long."
    ),
    expected_output='A 3-paragraph blog post summarizing the research findings.',
    agent=writer
)

# Instantiate the crew with a sequential process
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    verbose=2, # You can set this to 1 or 2 for more detailed logs
    process=Process.sequential
)

# Kick off the crew's work
result = crew.kickoff()

# Print the final output
print("######################")
print("Here is the final result:")
print(result)