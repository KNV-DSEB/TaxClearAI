import secrets

import pytest

from src.core.security import hash_password, verify_password


def test_password_hash_is_salted_and_verifies_without_plaintext_storage():
    password = secrets.token_urlsafe(20)
    hashed = hash_password(password)
    assert password not in hashed
    assert verify_password(password, hashed)
    assert not verify_password(secrets.token_urlsafe(20), hashed)


def test_multibyte_password_over_bcrypt_limit_is_rejected_without_truncation():
    with pytest.raises(ValueError):
        hash_password("ấ" * 25)
