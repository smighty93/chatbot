from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def load_vectorstore():
    docs = []
    folder = "Data/extracted"

    for file in os.listdir(folder):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join(folder, file))
            docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=80
    )

    split_docs = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    return FAISS.from_documents(split_docs, embeddings)

# 🔥 Initialize once
vectorstore = load_vectorstore()

# 🔥 THIS IS WHAT YOUR APP NEEDS
def retrieve_context(query):
    results = vectorstore.similarity_search(query, k=4)
    return "\n\n".join([r.page_content for r in results])