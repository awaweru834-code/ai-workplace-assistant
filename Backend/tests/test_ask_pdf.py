"""
test_ask_pdf.py — Integration tests for /ask-pdf endpoints.
Both Groq and Pinecone are fully mocked.
"""

from unittest.mock import MagicMock, patch

import pytest
from tests.conftest import auth_headers


def _mock_groq_response(content="According to the HR policy…"):
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


def _mock_pinecone(matches=None):
    """
    Returns a mock Pinecone class whose Index.query returns `matches`.
    Also mocks inference.embed to return a dummy vector.
    """
    if matches is None:
        # One relevant match above the 0.60 threshold
        match = MagicMock()
        match.score = 0.85
        match.metadata = {"text": "Employees get 20 vacation days.", "source": "handbook.pdf"}
        matches = [match]

    query_result = MagicMock()
    query_result.matches = matches

    embed_result = MagicMock()
    embed_result.__getitem__ = lambda self, idx: MagicMock(values=[0.1] * 1024)

    pc_instance = MagicMock()
    pc_instance.Index.return_value.query.return_value = query_result
    pc_instance.inference.embed.return_value = embed_result

    pc_cls = MagicMock(return_value=pc_instance)
    return pc_cls


class TestAskPdf:
    @patch("services.rag_service.Groq")
    @patch("services.rag_service.Pinecone", new_callable=_mock_pinecone)
    def test_ask_returns_reply(self, mock_pinecone_cls, mock_groq_cls, client):
        mock_groq_cls.return_value.chat.completions.create.return_value = (
            _mock_groq_response("You get 20 vacation days per year.")
        )
        headers = auth_headers(client)
        resp = client.post("/ask-pdf/", json={"message": "How many vacation days?"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["content"] == "You get 20 vacation days per year."
        assert data["role"] == "assistant"

    @patch("services.rag_service.Groq")
    @patch("services.rag_service.Pinecone", new_callable=_mock_pinecone)
    def test_ask_persists_messages(self, mock_pinecone_cls, mock_groq_cls, client):
        mock_groq_cls.return_value.chat.completions.create.return_value = (
            _mock_groq_response("Answer from policy.")
        )
        headers = auth_headers(client)
        client.post("/ask-pdf/", json={"message": "What is the leave policy?"}, headers=headers)
        hist = client.get("/ask-pdf/history", headers=headers).json()
        roles = [m["role"] for m in hist]
        assert "user" in roles
        assert "assistant" in roles

    def test_ask_unauthenticated(self, client):
        resp = client.post("/ask-pdf/", json={"message": "Hello"})
        assert resp.status_code == 401

    @patch("services.rag_service.Groq")
    @patch("services.rag_service.Pinecone", new_callable=_mock_pinecone)
    def test_ask_service_error_returns_502(self, mock_pinecone_cls, mock_groq_cls, client):
        mock_groq_cls.return_value.chat.completions.create.side_effect = RuntimeError("Groq down")
        headers = auth_headers(client)
        resp = client.post("/ask-pdf/", json={"message": "Hello"}, headers=headers)
        assert resp.status_code == 502


class TestAskPdfHistory:
    def test_history_empty_initially(self, client):
        headers = auth_headers(client)
        resp = client.get("/ask-pdf/history", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_history_unauthenticated(self, client):
        resp = client.get("/ask-pdf/history")
        assert resp.status_code == 401
