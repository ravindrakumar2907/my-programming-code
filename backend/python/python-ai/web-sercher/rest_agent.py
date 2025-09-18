import os
import requests
from config import Config

class CrewAIAgent:
    def __init__(self):
        # Placeholder: extend for multi-tool agent/task setup
        self.gemini_api_key = Config.GEMINI_API_KEY
        self.perplexity_api_key = Config.PERPLEXITY_API_KEY

    def get_response(self, user_msg, history):
        """
        Decide which tool/agent to use (simple demo: keyword-based routing).
        """
        if "search" in user_msg.lower() or "internet" in user_msg.lower():
            tool_used = "internet_search"
            result = self.internet_search(user_msg)
        elif "summarize" in user_msg.lower() or "rewrite" in user_msg.lower():
            tool_used = "refactor"
            # Refactor last user or AI message
            last_message = history[-2]["message"] if len(history) > 1 else user_msg
            result = self.refactor_text(last_message)
        else:
            tool_used = "gemini_ai"
            result = self.gemini_reply(user_msg, history)
        return result, tool_used

    def gemini_reply(self, prompt, history):
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }]
        }
        params = {"key": self.gemini_api_key}
        try:
            response = requests.post(url, headers=headers, params=params, json=payload)
            data = response.json()
            # DEBUG: print(data)
            if "candidates" in data and data["candidates"]:
                return data["candidates"]["content"]["parts"]["text"]
            elif "error" in data:
                return f"[Gemini API Error] {data['error'].get('message', str(data['error']))}"
            else:
                return f"[Gemini Error] No candidates found. Raw response: {data}"
        except Exception as e:
            return f"[Gemini Exception] {e}"


    def internet_search(self, query):
        # Simple internet search stub (could use SerpAPI, Bing API, etc)
        # Here, just mock a generic result
        return f"Internet Search Result for: {query} (Demo - integrate with search API here)"

    def refactor_text(self, text):
        # Use Gemini or another service to paraphrase/summarize
        prompt = f"Please summarize or rewrite this text for clarity:\n{text}"
        return self.gemini_reply(prompt, [])

