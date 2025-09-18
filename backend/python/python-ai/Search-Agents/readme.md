How to Get an EXA API Key (for EXASearchTool)
Go to the EXA website:
https://exa.ai

Sign Up/Create an Account:

Click on "Sign Up" or "Try API for free".

Follow the registration steps using your email or GitHub/Google account.

Access the API Key:

Once logged in, go to the Dashboard.

Look for sections like “API Keys”, "Get Started", or "API Playground".

Copy your EXA_API_KEY.

Free Credits:

You typically get free credits or quota to use for development and testing. (Check their documentation/dashboard for quota info.)

Set your key in your environment:

In your terminal or .env file, add:


EXA_API_KEY=your_exa_api_key_here

pip install 'crewai[tools]'


Use in Python as:
import os
from crewai_tools import EXASearchTool

os.environ["EXA_API_KEY"] = "your_exa_api_key"
search_tool = EXASearchTool()


Links:
https://docs.crewai.com/tools/search-research/exasearchtool
https://exa.ai/
https://docs.exa.ai/
https://docs.exa.ai/reference/crewai