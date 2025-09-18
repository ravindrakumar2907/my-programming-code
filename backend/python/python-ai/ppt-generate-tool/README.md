# CREWAI DuckDuckGo Multi-Agent Research App

## Overview
A Flask app using CREWAI framework to perform multi-agent research workflow:
- Uses DuckDuckGo search via custom CREWAI Tool
- Expands, summarizes, and generates PPT from research
- Session-based chat + Bootstrap UI

## Setup

1. Create and activate Python venv:
python3 -m venv venv
source venv/bin/activate



2. Install dependencies:
pip3 install -r requirements.txt




3. Optional: Create `.env` file with keys (for any Gemini/Perplexity LLM usage):
GEMINI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
SECRET_KEY=any_secret_value


4. Run the app:
python3 app.py



5. Navigate Open [http://localhost:5000](http://localhost:5000)

## Usage

- Enter research query and chat naturally.
- Results show on right, chat history on left.
- Download generated PPT after summary.

## Extensibility

- Add more CrewAI tools and agents in `crewai_workflow.py`.
- Swap LLM with Gemini or Perplexity by setting keys in `.env`.
- Extend PPT tool for richer slide generation.

---

## License & Credits

Uses:
- [CREWAI Framework](https://www.crewai.com)
- [duckduckgo_search](https://github.com/deedy5/duckduckgo-search)
- [python-pptx](https://python-pptx.readthedocs.io)
- Bootstrap 5 UI


## Instructions
Clone or download all files into one folder

Create outputs folder in the project root (for PPT)

Install requirements & run using python app.py

Add any API keys to .env if using Gemini or Perplexity LLM.

