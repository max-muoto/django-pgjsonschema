from pgjsonschema.core import Validator
from pgjsonschema.version import __version__


def _monkeypatch_jsonfield() -> None:
    """Monkeypatches JSONField to avoid complaining if its used as a generic."""

    from django.db import models

    models.JSONField.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls)  # type: ignore


_monkeypatch_jsonfield()

__all__ = ["Validator", "__version__"]
