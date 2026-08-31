"""
test_hr_chat.py — Integration tests for /hr-chat endpoints.
Groq is fully mocked so no network calls are made.
"""

from unittest.mock import MagicMock, patch

import pytest
from tests.conftest import auth_headers


def _mock_groq_response(content="Here is your HR answer."):
    """Build a minimal Groq response mock."""
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


class TestHrChat:
    @patch("services.hr_chat_service.Groq")
    def test_chat_returns_reply(self, mock_groq_cls, client):
        mock_groq_cls.return_value.chat.completions.create.return_value = (
            _mock_groq_response("Your vacation policy is 20 days.")
        )
        headers = auth_headers(client)
        resp = client.post("/hr-chat/", json={"message": "How many vacation days do I get?"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["content"] == "Your vacation policy is 20 days."
        assert data["role"] == "assistant"

    @patch("services.hr_chat_service.Groq")
    def test_chat_persists_messages(self, mock_groq_cls, client):
        mock_groq_cls.return_value.chat.completions.create.return_value = (
            _mock_groq_response("Parental leave is 12 weeks.")
        )
        headers = auth_headers(client)
        client.post("/hr-chat/", json={"message": "What is the parental leave policy?"}, headers=headers)
        hist = client.get("/hr-chat/history", headers=headers).json()
        roles = [m["role"] for m in hist]
        assert "user" in roles
        assert "assistant" in roles

    def test_chat_unauthenticated(self, client):
        resp = client.post("/hr-chat/", json={"message": "Hello"})
        assert resp.status_code == 401

    @patch("services.hr_chat_service.Groq")
    def test_chat_service_error_returns_502(self, mock_groq_cls, client):
        mock_groq_cls.return_value.chat.completions.create.side_effect = RuntimeError("Groq down")
        headers = auth_headers(client)
        resp = client.post("/hr-chat/", json={"message": "Hello"}, headers=headers)
        assert resp.status_code == 502


class TestHrChatHistory:
    @patch("services.hr_chat_service.Groq")
    def test_history_empty_initially(self, mock_groq_cls, client):
        headers = auth_headers(client)
        resp = client.get("/hr-chat/history", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    @patch("services.hr_chat_service.Groq")
    def test_history_ordered_asc(self, mock_groq_cls, client):
        mock_groq_cls.return_value.chat.completions.create.side_effect = [
            _mock_groq_response("Answer 1"),
            _mock_groq_response("Answer 2"),
        ]
        headers = auth_headers(client)
        client.post("/hr-chat/", json={"message": "First question"}, headers=headers)
        client.post("/hr-chat/", json={"message": "Second question"}, headers=headers)
        hist = client.get("/hr-chat/history", headers=headers).json()
        user_msgs = [m["content"] for m in hist if m["role"] == "user"]
        assert user_msgs[0] == "First question"
        assert user_msgs[1] == "Second question"

    def test_history_unauthenticated(self, client):
        resp = client.get("/hr-chat/history")
        assert resp.status_code == 401

    @patch("services.hr_chat_service.Groq")
    def test_history_isolated_per_user(self, mock_groq_cls, client):
        """Messages from user A must not appear in user B's history."""
        mock_groq_cls.return_value.chat.completions.create.return_value = (
            _mock_groq_response("Only for alice.")
        )
        headers_a = auth_headers(client, username="alice")
        headers_b = auth_headers(client, username="bob", password="bobpass")
        client.post("/hr-chat/", json={"message": "Alice's private question"}, headers=headers_a)
        hist_b = client.get("/hr-chat/history", headers=headers_b).json()
        assert all("alice" not in m["content"].lower() for m in hist_b)
