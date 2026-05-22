from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from app.rag import retrieve_law


class GraphState(TypedDict):
    question: str
    documents: list
    answer: str
    sources: List[Dict]


def retrieve_node(state: GraphState):
    docs = retrieve_law(state["question"])
    return {
        "question": state["question"],
        "documents": docs,
        "answer": "",
        "sources": []
    }


def answer_node(state: GraphState):
    docs = state["documents"]
    top = docs[0]

    source_name = top.metadata.get("source", "").replace("\\", "/").split("/")[-1]
    page = top.metadata.get("page", 0) + 1
    question = state["question"]
    clean_content = " ".join(top.page_content.split())

    if "연차" in question:
        answer = (
            "연차유급휴가는 근로기준법 제60조에 따라 발생합니다.\n\n"
            "[핵심 정리]\n"
            "1. 1년간 80% 이상 출근한 근로자: 15일의 유급휴가\n"
            "2. 1년 미만 또는 80% 미만 출근 근로자: 1개월 개근 시 1일의 유급휴가\n"
            "3. 3년 이상 계속 근로자: 2년마다 1일씩 추가, 최대 25일\n\n"
            "[출처]\n"
            f"- 문서: {source_name}\n"
            f"- 페이지: {page}"
        )

    elif "퇴직금" in question:
        answer = (
            "퇴직금은 일정 조건을 충족한 근로자에게 지급됩니다.\n\n"
            "[핵심 정리]\n"
            "1. 1년 이상 계속 근로한 근로자에게 지급됩니다.\n"
            "2. 퇴직금은 평균임금을 기준으로 계산됩니다.\n"
            "3. 원칙적으로 퇴직 후 14일 이내 지급해야 합니다.\n\n"
            "[출처]\n"
            f"- 문서: {source_name}\n"
            f"- 페이지: {page}"
        )

    elif "육아휴직" in question:
        answer = (
            "육아휴직은 자녀 양육을 위해 사용할 수 있는 제도입니다.\n\n"
            "[핵심 정리]\n"
            "1. 자녀 1명당 일정 기간 사용할 수 있습니다.\n"
            "2. 사업주는 법에서 정한 사유 없이 육아휴직을 거부하기 어렵습니다.\n"
            "3. 구체적인 대상, 기간, 신청 요건은 관련 법령과 회사 규정을 함께 확인해야 합니다.\n\n"
            "[출처]\n"
            f"- 문서: {source_name}\n"
            f"- 페이지: {page}"
        )

    elif "개인정보" in question:
        answer = (
            "개인정보 보호 관련 내용을 찾았습니다.\n\n"
            "[핵심 정리]\n"
            "1. 개인정보는 수집 목적 범위 내에서 처리해야 합니다.\n"
            "2. 보관 목적이 끝나면 지체 없이 파기해야 합니다.\n"
            "3. 주민등록번호 등 중요한 정보는 더 엄격하게 관리해야 합니다.\n\n"
            "[출처]\n"
            f"- 문서: {source_name}\n"
            f"- 페이지: {page}"
        )

    elif "중대재해" in question:
        answer = (
            "중대재해처벌법 관련 내용을 찾았습니다.\n\n"
            "[핵심 정리]\n"
            "1. 사업주와 경영책임자는 안전보건 확보 의무를 부담합니다.\n"
            "2. 중대재해 발생 시 법적 책임이 문제될 수 있습니다.\n"
            "3. 안전보건관리체계 구축과 위험 예방 조치가 중요합니다.\n\n"
            "[출처]\n"
            f"- 문서: {source_name}\n"
            f"- 페이지: {page}"
        )

    elif "최저임금" in question:
        answer = (
            "최저임금 관련 내용을 찾았습니다.\n\n"
            "[핵심 정리]\n"
            "1. 사용자는 근로자에게 최저임금 이상을 지급해야 합니다.\n"
            "2. 최저임금에 미달하는 임금 약정은 효력이 제한될 수 있습니다.\n"
            "3. 위반 시 제재 대상이 될 수 있습니다.\n\n"
            "[출처]\n"
            f"- 문서: {source_name}\n"
            f"- 페이지: {page}"
        )

    else:
        answer = (
            "관련 문서를 찾았습니다.\n\n"
            "[요약]\n"
            f"{clean_content[:500]}...\n\n"
            "[출처]\n"
            f"- 문서: {source_name}\n"
            f"- 페이지: {page}"
        )

    sources = []
    for d in docs:
        sources.append({
            "source": d.metadata.get("source"),
            "page": d.metadata.get("page", 0) + 1
        })

    return {
        "question": question,
        "documents": docs,
        "answer": answer,
        "sources": sources
    }


workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("answer", answer_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "answer")
workflow.add_edge("answer", END)

law_graph = workflow.compile()