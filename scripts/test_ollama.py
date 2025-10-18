"""Test Ollama local LLM."""
from langchain_ollama import OllamaLLM

# Initialize Ollama
llm = OllamaLLM(model="llama3.2")

# Test it
response = llm.invoke("Explain machine learning in one sentence.")
print(response)

print("\n✅ Ollama is working!")