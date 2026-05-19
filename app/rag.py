from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

pdf_path = "app/data/근로기준법.pdf"

loader = PyPDFLoader(pdf_path)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

splits = text_splitter.split_documents(docs)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embedding_model
)

def retrieve_law(question: str):
    results = vectorstore.similarity_search(question, k=5)

    keyword = question.replace(" ", "")

    filtered_results = [
        r for r in results
        if keyword in r.page_content.replace(" ", "")
    ]

    if filtered_results:
        results = filtered_results[:3]
    else:
        results = results[:3]

    return results