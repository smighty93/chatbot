from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

def ask_llm(prompt):
    return llm.invoke(prompt)