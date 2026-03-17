import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class Generator:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

        # Load system prompt
        with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def generate(self, question, context):

        prompt = f"""
        {self.system_prompt}

        Sử dụng ngữ cảnh sau để trả lời câu hỏi.

        Ngữ cảnh:
        {context}

        Câu hỏi:
        {question}

        Trả về kết quả dưới dạng JSON với cấu trúc:
        {{
            "answer": "Câu trả lời chi tiết",
            "citations": ["Nguồn 1", "Nguồn 2"]
        }}
        """

        response = self.client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        try:
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            return {"answer": response.text, "citations": []}