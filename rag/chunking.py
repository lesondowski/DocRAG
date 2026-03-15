#Chunking Strategy Implementation

from tokenizer import Tokenizer

class Chunker:
    def __init__(self, chunk_size=500, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap
#        self.max_tokens = max_tokens ( Có thể thêm vào sau tùy vào việc điều chỉnh kết quả của chunking)
        self.tokenizer = Tokenizer()


    def chunk_text(self, text):
        tokens = self.tokenizer.encode(text)
        chunks = []

        start = 0

        while start < len(tokens):

            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            start += self.chunk_size - self.overlap

        return chunks
    


