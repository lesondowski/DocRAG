from rag.tokenizer import Tokenizer
import re
import ast
from typing import List
from rag.embedding import GeminiEmbedder  # Assuming you have this

class Chunker:
    def __init__(self, chunk_size=400, overlap=100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.tokenizer = Tokenizer()
        self.embedder = GeminiEmbedder()  # For semantic chunking

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

    def auto_detect_strategy(self, text: str) -> str:
        """
        Automatically detect the best chunking strategy based on content analysis.
        
        Returns:
            'function' if Python code
            'structure' if document with headings/paragraphs
            'semantic' if long text with sentences
            'text' as fallback
        """
        # Check if it's Python code
        try:
            ast.parse(text)
            # If parsing succeeds and has functions/classes, it's code
            tree = ast.parse(text)
            has_functions = any(isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) 
                              for node in ast.walk(tree))
            if has_functions:
                return 'function'
        except SyntaxError:
            pass  # Not Python code
        
        # Check for structured document (headings)
        heading_count = len(re.findall(r'\n#{1,6}\s', text))
        if heading_count > 2:  # Multiple headings
            return 'structure'
        
        # Check for paragraphs (multiple double newlines)
        paragraph_count = len(re.findall(r'\n\n+', text))
        if paragraph_count > 3:  # Multiple paragraphs
            return 'structure'
        
        # Check for long text with sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) > 10 and len(text) > 1000:  # Long text with many sentences
            return 'semantic'
        
        # Default to basic text chunking
        return 'text'
        """
        Structure-aware chunking: Split text based on document structure like headings, paragraphs.
        Uses regex to detect headings (# ## ###) and paragraphs.
        """
        # Split by headings and paragraphs
        sections = re.split(r'(\n#{1,6}\s.*?\n|\n\n)', text)
        chunks = []
        current_chunk = ""
        
        for section in sections:
            if len(current_chunk) + len(section) > self.chunk_size * 4:  # Rough estimate
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = section
                else:
                    chunks.append(section.strip())
            else:
                current_chunk += section
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def chunk_semantic(self, text: str) -> List[str]:
        """
        Semantic chunking: Split text into semantically coherent chunks using embeddings.
        Uses sentence similarity to find natural breaks.
        """
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            raise ImportError("sklearn and numpy are required for semantic chunking. Install with: pip install scikit-learn numpy")
        
        # First, split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) < 2:
            return [text]
        
        # Embed sentences
        embeddings = [self.embedder.embed_text(sent) for sent in sentences]
        
        # Calculate similarities
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
            similarities.append(sim)
        
        # Find low similarity points as break points
        threshold = np.mean(similarities) - np.std(similarities)  # Simple threshold
        chunks = []
        current_chunk = sentences[0]
        
        for i, sent in enumerate(sentences[1:], 1):
            if similarities[i-1] < threshold:
                chunks.append(current_chunk)
                current_chunk = sent
            else:
                current_chunk += " " + sent
        
        chunks.append(current_chunk)
        return chunks

    def chunk_function_api(self, code: str) -> List[str]:
        """
        Function / API block chunking: For Python code, split by functions, classes, etc.
        """
        try:
            tree = ast.parse(code)
            chunks = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    # Extract the code block for this function/class
                    start_line = node.lineno - 1
                    end_line = getattr(node, 'end_lineno', start_line + 1) - 1
                    lines = code.split('\n')
                    block = '\n'.join(lines[start_line:end_line + 1])
                    chunks.append(block)
            
            if not chunks:
                # If no functions, return whole code
                chunks = [code]
            
            return chunks
        except SyntaxError:
            # If not valid Python, fall back to text chunking
            return self.chunk_text(code)
    


