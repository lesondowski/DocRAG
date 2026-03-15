import re
# Gemini Cookbook best practices

def clean_text(text):

    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text