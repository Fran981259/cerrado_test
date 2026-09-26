"""Tests for bounded LLM provider failover."""


def test_llm_client_fails_over_to_next_provider(monkeypatch):
    from app.llm_client import LLMClient, LLMUnavailableError

    monkeypatch.setenv("LLM_FALLBACK_CHAIN", "gemini,groq")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    monkeypatch.setenv("GROQ_API_KEY", "groq-key")

    def complete_provider(self, *_args):
        if self.provider == "gemini":
            raise LLMUnavailableError("rate limited")
        return "secondary response"

    monkeypatch.setattr(LLMClient, "_complete_provider", complete_provider)
    client = LLMClient(provider="gemini")
    assert client.complete("hello") == "secondary response"
