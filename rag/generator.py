import os
import json
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()

class Generator:

    def __init__(self, model_name="gemini-2.5-flash-lite"):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

        # Load prompt
        try:
            with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            print("Warning: prompts/system_prompt.txt not found.")
            self.system_prompt = "You are a helpful assistant."

    def generate(self, question, context, model_name=None):
        """
        Generate response with token tracking.
        
        Args:
            question: User question
            context: Retrieved context from RAG
            model_name: Optional override for model selection
            
        Returns:
            (result_dict, token_info_dict)
        """
        if model_name:
            self.model_name = model_name
            
        prompt = f"""{self.system_prompt}

        Ngữ cảnh:
        {context}

        Câu hỏi:
        {question}
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        
        # Extract token usage from response
        token_info = {
            "model": self.model_name,
            "prompt_tokens": 0,
            "response_tokens": 0,
            "total_tokens": 0
        }
        
        # Try to get usage_metadata from response
        if hasattr(response, 'usage_metadata'):
            metadata = response.usage_metadata
            token_info["prompt_tokens"] = metadata.prompt_token_count if hasattr(metadata, 'prompt_token_count') else 0
            token_info["response_tokens"] = metadata.candidates_token_count if hasattr(metadata, 'candidates_token_count') else 0
            token_info["total_tokens"] = token_info["prompt_tokens"] + token_info["response_tokens"]

        try:
            result = json.loads(response.text)
            return result, token_info
        except:
            return {"answer": "Tôi không thể tạo câu trả lời dựa trên thông tin có sẵn.", "citations": []}, token_info