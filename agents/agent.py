import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()


class Agent:

    def __init__(self, tool_registry):

        api_key = os.getenv("GEMINI_API_KEY")

        self.client = genai.Client(api_key=api_key)

        self.tools = tool_registry

    def think(self, question, scratchpad):

        tool_list = self.tools.list_tools()

        prompt = f"""
You are an autonomous AI agent.

You can use tools.

Available tools:
{tool_list}

Use the following format:

Thought: reasoning
Action: tool_name
Action Input: input
Observation: result

Question: {question}

{scratchpad}

Thought:
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text