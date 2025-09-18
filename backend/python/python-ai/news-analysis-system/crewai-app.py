
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool, DuckDuckGoSearchTool
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Set environment variable for API (using a free/local model)
# You can use Ollama locally or any other free LLM provider
os.environ["OPENAI_API_KEY"] = "your-api-key-or-use-ollama"

# Initialize the search tool (DuckDuckGo doesn't require API key)
search_tool = DuckDuckGoSearchTool()

# Custom tool for formatting news results
@tool("format_news_results")
def format_news_results(raw_results: str) -> str:
    """
    Format raw search results into a structured news format
    """
    # This tool processes the raw search results and formats them nicely
    formatted_results = f"""
    📰 **LATEST NEWS SUMMARY**
    Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    {raw_results}
    
    ---
    News compiled using CrewAI with DuckDuckGo Search
    """
    return formatted_results

# Define the News Research Agent
news_researcher = Agent(
    role='Senior News Researcher',
    goal='Find and analyze the 5 most recent and relevant news articles',
    backstory="""
    You are an experienced news researcher with a keen eye for identifying 
    breaking news and trending topics. You excel at finding credible sources 
    and summarizing complex information into digestible insights.
    """,
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    temperature=0.3  # Lower temperature for more focused, factual responses
)

# Define the News Editor Agent
news_editor = Agent(
    role='Professional News Editor',
    goal='Curate and format news articles into a professional summary',
    backstory="""
    You are a professional news editor with years of experience in 
    journalism. You specialize in creating well-structured, engaging 
    news summaries that are both informative and easy to read.
    """,
    verbose=True,
    allow_delegation=False,
    tools=[format_news_results],
    temperature=0.4  # Slightly higher temperature for better formatting creativity
)

# Define Tasks
research_task = Task(
    description="""
    Search for the 5 latest news articles from today. Focus on:
    1. Breaking news and current events
    2. Technology and business news
    3. World news and politics
    4. Health and science developments
    5. Any trending topics
    
    For each news item, include:
    - Headline
    - Brief summary (2-3 sentences)
    - Source
    - Approximate time/date if available
    
    Make sure the news is recent (within the last 24-48 hours).
    """,
    expected_output="A list of 5 recent news articles with headlines, summaries, and sources",
    agent=news_researcher
)

editing_task = Task(
    description="""
    Take the researched news articles and format them into a professional 
    news digest. Structure it as:
    
    1. **Headline**: [Clear, engaging headline]
    2. **Summary**: [2-3 sentence summary]
    3. **Source**: [News source]
    4. **Category**: [News category like Tech, Politics, Health, etc.]
    
    Number each news item (1-5) and ensure consistent formatting.
    Add a brief introduction paragraph about today's top news highlights.
    """,
    expected_output="A professionally formatted news digest with 5 news articles",
    agent=news_editor,
    context=[research_task]  # This task depends on the research task
)

# Create the Crew
news_crew = Crew(
    agents=[news_researcher, news_editor],
    tasks=[research_task, editing_task],
    process=Process.sequential,  # Tasks execute one after another
    verbose=2  # Maximum verbosity for detailed output
)

# Function to run the news search
def get_latest_news():
    """
    Execute the CrewAI workflow to get latest news
    """
    print("🚀 Starting CrewAI News Search...")
    print("=" * 50)
    
    try:
        # Execute the crew
        result = news_crew.kickoff()
        return result
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return None

# Main execution
if __name__ == "__main__":
    print("📰 CrewAI News Search Application")
    print("Using DuckDuckGo Search (No API Key Required)")
    print("=" * 60)
    
    # Get the latest news
    news_digest = get_latest_news()
    
    if news_digest:
        print("\n" + "=" * 60)
        print("📋 FINAL NEWS DIGEST")
        print("=" * 60)
        print(news_digest)
        
        # Optionally save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"news_digest_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(news_digest))
            print(f"\n💾 News digest saved to: {filename}")
        except Exception as e:
            print(f"❌ Could not save file: {str(e)}")
    
    else:
        print("❌ Failed to generate news digest")

# Additional utility functions
def search_specific_topic(topic: str):
    """
    Search for news on a specific topic
    """
    # Create a custom task for specific topic
    specific_research_task = Task(
        description=f"""
        Search for the latest news specifically about: {topic}
        
        Find 5 recent articles related to this topic and include:
        - Headline
        - Brief summary
        - Source
        - Relevance to the topic
        """,
        expected_output=f"5 recent news articles about {topic}",
        agent=news_researcher
    )
    
    # Create temporary crew for this specific search
    topic_crew = Crew(
        agents=[news_researcher, news_editor],
        tasks=[specific_research_task, editing_task],
        process=Process.sequential,
        verbose=1
    )
    
    return topic_crew.kickoff()

# Example usage for specific topics
def demo_specific_search():
    """
    Demonstrate searching for specific topics
    """
    topics = ["artificial intelligence", "climate change", "cryptocurrency"]
    
    for topic in topics:
        print(f"\n🔍 Searching for news about: {topic}")
        print("-" * 40)
        result = search_specific_topic(topic)
        print(result)
        print("\n")

# Configuration options
class NewsConfig:
    """
    Configuration class for the news application
    """
    def __init__(self):
        self.max_news_items = 5
        self.search_language = "en"
        self.search_region = "us-en"  # DuckDuckGo region
        self.temperature_researcher = 0.3
        self.temperature_editor = 0.4
        self.verbose_level = 2
    
    def update_agent_temperatures(self, research_temp: float, editor_temp: float):
        """Update temperature settings for agents"""
        self.temperature_researcher = research_temp
        self.temperature_editor = editor_temp
        
        # Update existing agents
        news_researcher.temperature = research_temp
        news_editor.temperature = editor_temp

# Usage examples
if __name__ == "__main__":
    # Basic news search
    print("Running basic news search...")
    get_latest_news()
    
    # Uncomment to test specific topic search
    # print("\nRunning specific topic searches...")
    # demo_specific_search()