"""
Test Token Management System
Demonstrates model selection logic and cost calculation
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.token_manager import TokenManager


def test_complexity_estimation():
    """Test complexity scoring"""
    print("\n" + "="*60)
    print("TEST 1: Query Complexity Estimation")
    print("="*60)
    
    tm = TokenManager()
    
    test_queries = [
        ("Là gì audit?", "Very simple"),
        ("Quy trình audit của công ty như thế nào?", "Simple"),
        ("Phân tích chi tiết các bước thực hiện audit, các vấn đề thường gặp, và cách khắc phục?", "Advanced"),
        ("Tại sao audit quan trọng? Lợi ích kinh tế? So sánh với kiểm toán?", "Very complex"),
    ]
    
    for query, expected in test_queries:
        complexity = tm.estimate_complexity(query)
        print(f"\nQuery: {query[:60]}...")
        print(f"Expected: {expected} | Got complexity: {complexity}/10")


def test_model_selection():
    """Test smart model selection"""
    print("\n" + "="*60)
    print("TEST 2: Smart Model Selection")
    print("="*60)
    
    tm = TokenManager()
    
    test_queries = [
        "Là gì?",
        "Giải thích quy trình",
        "Phân tích chi tiết, so sánh ưu nhược điểm",
        "Tại sao lại như vậy? Làm sao cải thiện? Phương pháp nào tốt nhất?",
    ]
    
    for query in test_queries:
        model, reason = tm.select_model(query)
        complexity = tm.estimate_complexity(query)
        print(f"\nQuery: {query}")
        print(f"Complexity: {complexity}/10")
        print(f"Model: {model}")
        print(f"Reason: {reason}")


def test_cost_calculation():
    """Test cost calculation for different models"""
    print("\n" + "="*60)
    print("TEST 3: Cost Calculation")
    print("="*60)
    
    tm = TokenManager()
    
    scenarios = [
        ("Flash Lite", "gemini-1.5-flash", 500, 100),
        ("Flash Lite", "gemini-1.5-flash", 2000, 300),
        ("Flash 2.0", "gemini-2.0-flash", 2000, 300),
        ("Pro", "gemini-1.5-pro", 3000, 1000),
        ("Pro", "gemini-1.5-pro", 5000, 2000),
    ]
    
    print("\n{:<20} {:<12} {:<12} {:<12} {:<12}".format(
        "Model", "Input", "Output", "Total", "Cost USD"))
    print("-" * 70)
    
    for name, model, input_tokens, output_tokens in scenarios:
        cost = tm.calculate_cost(model, input_tokens, output_tokens)
        total = input_tokens + output_tokens
        print("{:<20} {:<12,} {:<12,} {:<12,} ${:<12.8f}".format(
            name, input_tokens, output_tokens, total, cost))


def test_session_logging():
    """Test session logging and statistics"""
    print("\n" + "="*60)
    print("TEST 4: Session Logging & Stats")
    print("="*60)
    
    tm = TokenManager()
    
    # Simulate 5 queries
    queries = [
        ("Là gì audit?", "gemini-1.5-flash", 400, 80),
        ("Quy trình audit?", "gemini-2.0-flash", 1500, 250),
        ("Phân tích chi tiết", "gemini-2.0-flash", 2000, 400),
        ("So sánh audit và kiểm toán", "gemini-1.5-pro", 2500, 800),
        ("Cách cải thiện?", "gemini-2.0-flash", 1800, 300),
    ]
    
    for query, model, input_tk, output_tk in queries:
        tm.log_query(
            query=query,
            model_used=model,
            prompt_tokens=input_tk,
            output_tokens=output_tk,
            answer_preview="Câu trả lời mẫu..."
        )
        print(f"✓ Logged: {query[:40]}... ({model})")
    
    # Print summary
    tm.print_session_summary()


def test_cost_comparison():
    """Compare cost between Flash Lite vs Pro"""
    print("\n" + "="*60)
    print("TEST 5: Cost Comparison (Flash Lite vs Pro)")
    print("="*60)
    
    tm = TokenManager()
    
    # Simulate 100 queries
    flash_lite_cost = 0
    pro_cost = 0
    
    for i in range(100):
        # Flash Lite: 1000 input, 200 output
        flash_lite_cost += tm.calculate_cost("gemini-1.5-flash", 1000, 200)
        # Pro: same tokens
        pro_cost += tm.calculate_cost("gemini-1.5-pro", 1000, 200)
    
    print(f"\n100 queries, each: 1000 input + 200 output tokens")
    print(f"Flash Lite Cost: ${flash_lite_cost:.4f}")
    print(f"Pro Cost: ${pro_cost:.4f}")
    print(f"Difference: ${pro_cost - flash_lite_cost:.4f}")
    print(f"Pro is {pro_cost/flash_lite_cost:.1f}x more expensive")
    print(f"\n✅ Smart model selection can save {((pro_cost - flash_lite_cost)/pro_cost * 100):.1f}% on average")


if __name__ == "__main__":
    test_complexity_estimation()
    test_model_selection()
    test_cost_calculation()
    test_session_logging()
    test_cost_comparison()
    
    print("\n" + "="*60)
    print("✅ All token management tests completed!")
    print("="*60)
