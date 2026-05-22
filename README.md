# Legal RAG System

법률 PDF 문서를 검색하여 질문에 대한 답변을 제공하는 RAG 기반 AI 시스템입니다.

## 프로젝트 소개

근로기준법, 개인정보보호법, 산업안전보건법 등 다양한 법률 PDF를 검색하여 관련 내용을 제공합니다.

FastAPI + LangChain + LangGraph + ChromaDB 기반으로 제작했습니다.

---

## 기술 스택

- Python
- FastAPI
- LangChain
- LangGraph
- ChromaDB
- HuggingFace Embedding
- Docker
- GitHub

---

## 주요 기능

- 다중 PDF 자동 로딩
- 1000페이지 이상 문서 검색
- Hybrid Search
- 출처 및 페이지 반환
- 법률별 답변 템플릿 제공

---

## API 예시

질문:

```json
{
  "question": "연차유급휴가는 언제 발생하나요?"
}
```

응답:

```json
{
  "answer": "연차유급휴가는 근로기준법 제60조에 따라 발생합니다."
}
```