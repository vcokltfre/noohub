from .auth import Authenticator as _Auth
from .spec import Noofile

Authenticator = _Auth()

__all__ = (
    "Authenticator",
    "Noofile",
)
