"""
Token Management & Cost Optimization Module
Tracks token usage, calculates API costs, and recommends model selection.

Pricing (as of 2024):
- Gemini-1.5-Flash (Lite): 0.075/1M input, 0.3/1M output (cheapest, fastest)
- Gemini-2.5-Flash-Lite: 0.075/1M input, 0.3/1M output
- Gemini-2.0-Flash: 0.1/1M input, 0.4/1M output
- Gemini-1.5-Pro: 2.5/1M input, 7.5/1M output (most capable)
"""

import json
from datetime import datetime
from pathlib import Path


class TokenManager:
    """Manages token counting, cost calculation, and model selection"""
    
    # Pricing (per million tokens)
    PRICING = {
        "gemini-1.5-flash": {"input": 0.075, "output": 0.3},
        "gemini-2.5-flash-lite": {"input": 0.075, "output": 0.3},
        "gemini-2.0-flash": {"input": 0.1, "output": 0.4},
        "gemini-1.5-pro": {"input": 2.5, "output": 7.5},
    }
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.session_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "total_queries": 0,
            "model_usage": {},
            "queries": []
        }
    
    def count_tokens(self, text):
        """
        Rough estimation of token count (tiktoken estimation)
        More accurate: use Google's tokenizer if available
        """
        # Rough heuristic: 1 token ≈ 4 characters for English
        return max(1, len(text) // 4)
    
    def estimate_complexity(self, query):
        """
        Estimate query complexity (1-10) based on:
        - Query length
        - Keywords indicating complexity
        - Number of conditions
        """
        complexity = 1
        
        # Length-based
        if len(query) > 100:
            complexity += 2
        if len(query) > 200:
            complexity += 2
        
        # Keyword-based
        complex_keywords = [
            "phân tích", "so sánh", "giải thích", "tại sao", "làm sao",
            "chi tiết", "toàn bộ", "tổng hợp", "cách", "quy trình"
        ]
        query_lower = query.lower()
        for keyword in complex_keywords:
            if keyword in query_lower:
                complexity += 2
        
        # Multiple questions
        if "?" in query and query.count("?") > 1:
            complexity += 2
        
        return min(10, complexity)
    
    def select_model(self, query):
        """
        Smart model selection based on query complexity and cost-benefit
        
        Returns: (model_name, reason)
        """
        complexity = self.estimate_complexity(query)
        
        if complexity <= 3:
            # Simple questions: use Flash Lite (cheapest)
            return "gemini-2.5-flash-lite", f"Complexity {complexity}: Flash Lite (cost-optimized)"
        elif complexity <= 7:
            # Medium questions: use Flash 2.0 (balanced)
            return "gemini-2.0-flash", f"Complexity {complexity}: Flash 2.0 (balanced)"
        else:
            # Complex reasoning: use Pro (best quality)
            return "gemini-1.5-pro", f"Complexity {complexity}: Pro (best quality)"
    
    def calculate_cost(self, model_name, input_tokens, output_tokens):
        """Calculate cost in USD for given token counts"""
        if model_name not in self.PRICING:
            return 0.0
        
        pricing = self.PRICING[model_name]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return round(input_cost + output_cost, 8)
    
    def log_query(self, query, model_used, prompt_tokens, output_tokens, answer_preview):
        """Log query usage to session and file"""
        cost = self.calculate_cost(model_used, prompt_tokens, output_tokens)
        
        query_log = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:100],  # First 100 chars
            "complexity": self.estimate_complexity(query),
            "model": model_used,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "total_tokens": prompt_tokens + output_tokens,
            "cost_usd": cost,
            "answer_preview": answer_preview[:50]
        }
        
        # Update session stats
        self.session_stats["total_tokens"] += prompt_tokens + output_tokens
        self.session_stats["total_cost"] += cost
        self.session_stats["total_queries"] += 1
        
        if model_used not in self.session_stats["model_usage"]:
            self.session_stats["model_usage"][model_used] = {
                "count": 0,
                "tokens": 0,
                "cost": 0.0
            }
        
        self.session_stats["model_usage"][model_used]["count"] += 1
        self.session_stats["model_usage"][model_used]["tokens"] += prompt_tokens + output_tokens
        self.session_stats["model_usage"][model_used]["cost"] += cost
        
        self.session_stats["queries"].append(query_log)
        
        return query_log
    
    def print_session_summary(self):
        """Print current session statistics"""
        if self.session_stats["total_queries"] == 0:
            print("\n[TOKEN MANAGER] No queries logged yet.")
            return
        
        print("\n" + "="*60)
        print("TOKEN MANAGEMENT SUMMARY")
        print("="*60)
        print(f"Total Queries: {self.session_stats['total_queries']}")
        print(f"Total Tokens Used: {self.session_stats['total_tokens']:,}")
        print(f"Total Cost: ${self.session_stats['total_cost']:.6f}")
        print(f"Avg Cost/Query: ${self.session_stats['total_cost']/max(1, self.session_stats['total_queries']):.6f}")
        
        print("\nModel Usage Breakdown:")
        for model, stats in self.session_stats["model_usage"].items():
            print(f"  {model}:")
            print(f"    - Queries: {stats['count']}")
            print(f"    - Tokens: {stats['tokens']:,}")
            print(f"    - Cost: ${stats['cost']:.6f}")
        
        print("="*60 + "\n")
    
    def save_session_log(self, session_name="session"):
        """Save session statistics to JSON file"""
        log_file = self.log_dir / f"{session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.session_stats, f, indent=2, ensure_ascii=False)
        
        print(f"\n[LOG] Session saved to {log_file}")
        return log_file
