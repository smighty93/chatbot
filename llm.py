from langchain_community.llms import Ollama

llm = Ollama(model="tinyllama")

def ask_llm(prompt):
    return llm.invoke(prompt)