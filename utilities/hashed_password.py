"""Utilities fo app"""
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """Will return hashed password.

    Args:
        password (str)

    Returns:
        str: Hashed password.
    """
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """Verify the password given by the user.

    Args:
        password (str)
        hashed_pass (str)

    Returns:
        bool: if password is same it will return true.
    """
    return password_context.verify(password, hashed_pass)
