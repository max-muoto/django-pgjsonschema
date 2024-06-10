from typing import Annotated

import pydantic
from django.db import models

from pgjsonschema import Validator


class User(pydantic.BaseModel):
    """Pydantic model for testing the JSONField validation."""

    username: str
    email: str


class UsersRoot(pydantic.RootModel):
    root: dict[str, User]


class FakeModel(models.Model):
    """Model for testing the JSONField validation with `annotated`."""

    unannotated_json_field = models.JSONField()
    user: Annotated[models.JSONField[dict[str, str]], User] = models.JSONField()
    names_to_users: Annotated[
        models.JSONField[dict[str, dict[str, str]]], UsersRoot
    ] = models.JSONField()


class Payment(models.Model):
    user: Validator[dict[str, str]] = models.JSONField()
    # Raw dump of the user data as a string.
    user_dump: Validator[str] = models.JSONField()
    # Numeric or `None` value.
    amount: Validator[float | None] = models.JSONField()
    # List of strings.
    items: Validator[list[str]] = models.JSONField()
    # List of numbers.
    prices: Validator[list[float]] = models.JSONField()
    # List of numbers or `None` values.
    nullable_prices: Validator[list[float | None]] = models.JSONField()
