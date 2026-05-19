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

    answer = f"""
근로기준법에서 관련 내용을 찾았습니다.

핵심 내용:
{top.page_content[:600]}

출처:
- 문서: {top.metadata.get("source")}
- 페이지: {top.metadata.get("page", 0) + 1}
"""

    sources = []

    for d in docs:
        sources.append({
            "source": d.metadata.get("source"),
            "page": d.metadata.get("page", 0) + 1
        })

    return {
        "question": state["question"],
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