from typing import TypedDict, List, Dict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from app.rag import retrieve_law


# .env 파일에서 OPENAI_API_KEY 불러오기
load_dotenv()

# GPT 모델 설정
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


class GraphState(TypedDict):
    question: str
    documents: list
    answer: str
    sources: List[Dict]


def retrieve_node(state: GraphState):
    """사용자 질문과 관련된 법률 문서를 검색하는 단계"""
    docs = retrieve_law(state["question"])

    return {
        "question": state["question"],
        "documents": docs,
        "answer": "",
        "sources": []
    }


def answer_node(state: GraphState):
    """검색된 문서를 바탕으로 GPT가 답변을 생성하는 단계"""
    question = state["question"]
    docs = state["documents"]

    # 검색된 문서 내용 합치기
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # 출처 정보 정리
    sources = []
    for doc in docs:
        source_name = doc.metadata.get("source", "").replace("\\", "/").split("/")[-1]
        page = doc.metadata.get("page", 0) + 1

        sources.append({
            "source": source_name,
            "page": page
        })

    # GPT에게 보낼 프롬프트
    prompt = f"""
당신은 법률 문서를 바탕으로 답변하는 AI입니다.

사용자 질문:
{question}

참고 법률 문서:
{context}

답변 작성 규칙:
1. 반드시 참고 법률 문서 내용을 기반으로 답변하세요.
2. 참고 문서에 없는 내용은 추측하지 마세요.
3. 일반인이 이해하기 쉽게 설명하세요.
4. 답변은 [핵심 답변], [근거], [출처] 형식으로 작성하세요.

출처 정보:
{sources}

답변:
"""

    response = llm.invoke(prompt)
    answer = response.content

    return {
        "question": question,
        "documents": docs,
        "answer": answer,
        "sources": sources
    }


# LangGraph 워크플로우 구성
workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("answer", answer_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "answer")
workflow.add_edge("answer", END)

law_graph = workflow.compile()