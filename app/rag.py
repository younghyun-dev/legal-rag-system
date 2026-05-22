from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

import os
from langchain_community.document_loaders import PyPDFLoader

docs = []

data_path = "app/data"

for file in os.listdir(data_path):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(data_path, file)

        print(f"불러오는 중: {file}")

        loader = PyPDFLoader(pdf_path)
        pdf_docs = loader.load()

        docs.extend(pdf_docs)

print(f"총 페이지 수: {len(docs)}")

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
    # 질문별 검색 키워드
    if "연차" in question:
        must_keywords = ["연차"]
        prefer_keywords = ["제60조", "연차유급휴가", "연차 유급휴가"]
    elif "육아휴직" in question:
        must_keywords = ["육아휴직"]
        prefer_keywords = ["제19조", "남녀고용평등"]
    elif "퇴직금" in question:
        must_keywords = ["퇴직금"]
        prefer_keywords = ["퇴직급여", "퇴직연금"]
    elif "개인정보" in question:
        must_keywords = ["개인정보"]
        prefer_keywords = ["처리", "보관", "파기"]
    elif "중대재해" in question:
        must_keywords = ["중대재해"]
        prefer_keywords = ["경영책임자", "안전보건"]
    elif "최저임금" in question:
        must_keywords = ["최저임금"]
        prefer_keywords = []
    else:
        must_keywords = question.split()
        prefer_keywords = []

    scored_results = []

    for doc in splits:
        raw_content = doc.page_content
        content = raw_content.replace(" ", "").replace("\n", "")
        source = doc.metadata.get("source", "")

        # 1. 목차/색인 페이지 제외
        # 제60조 같은 단어가 있어도 "제48조 제49조 제50조..."처럼 조문 목록만 있는 페이지는 제외
        if (
            "제48조" in content
            and "제49조" in content
            and "제50조" in content
            and "제51조" in content
            and "제52조" in content
        ):
            continue

        # 2. 너무 짧거나 제목/목차 느낌 강한 페이지 제외
        if len(content) < 200:
            continue

        score = 0

        # 3. 필수 키워드 점수
        for kw in must_keywords:
            if kw.replace(" ", "") in content:
                score += 100

        # 4. 선호 키워드 점수
        for kw in prefer_keywords:
            if kw.replace(" ", "") in content:
                score += 80

        # 5. 문서명 가산점
        if "연차" in question and "근로기준법" in source:
            score += 50
        if "육아휴직" in question and "남녀고용평등" in source:
            score += 50
        if "퇴직금" in question and "퇴직급여" in source:
            score += 50
        if "개인정보" in question and "개인정보" in source:
            score += 50
        if "중대재해" in question and "중대재해" in source:
            score += 50

        # 6. 정확한 조문 제목 가산점
        if "연차" in question and "제60조(연차" in content:
            score += 300
        if "육아휴직" in question and "제19조(육아휴직" in content:
            score += 300

        if score > 0:
            scored_results.append((score, doc))

    scored_results.sort(key=lambda x: x[0], reverse=True)

    if scored_results:
        return [doc for score, doc in scored_results[:3]]

    return vectorstore.similarity_search(question, k=3)