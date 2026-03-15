import tiktoken

### LLM đếm token chứ không đếm ký tự.
### Ta sử dụng tokenizer tương thích với các model hiện đại.

class Tokenizer: 
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def encode(self, text):
        return self.encoding.encode(text)
    
    def decode(self, tokens):
        return self.encoding.decode(tokens)
    
    def count_tokens(self, text):
        return len(self.encode(text))








