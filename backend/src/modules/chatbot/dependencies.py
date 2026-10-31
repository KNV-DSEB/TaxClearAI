from src.core.rate_limit import reset_rate_limit_state as _reset_rate_limit_state


def reset_rate_limit_state() -> None:
    """Clear local limiter state for tests."""
    _reset_rate_limit_state("chatbot")
