from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
)

import pydantic

from pgjsonschema.types import JSONType

T = TypeVar("T")
J = TypeVar("J", bound=JSONType | pydantic.BaseModel)


if TYPE_CHECKING:
    # Validator will be recognized by type-checkers as `models.JSONField` with a generic parameter.
    from django.db import models

    Validator = models.JSONField[T]
else:

    class Validator(Generic[J]):
        """Validate against an arbitrary JSON type or Pydantic model.

        When this annotation is used, a Postgres trigger will be installed on the model that ensures the JSONField
        data is valid and aligns with the schema of the Pydantic model or the JSON type hint.

        Examples:
            If you want to validate against a Pydantic model, you can simply pass in the model as a generic parameter.
            >>> import pgjsonschema
            ... class Payment(models.Model):
            ...     user: pgjsonschema.Validator[User] = models.JSONField()


            The same goes for arbitrary JSON types.
            >>> import pgjsonschema
            ... class Payment(models.Model):
            ...     user: pgjsonschema.Validator[dict[str, str]] = models.JSONField()

            Pydantic root models are also supported.
            >>> import pgjsonschema
            ... class UsersRoot(pydantic.RootModel):
            ...     root: dict[str, User]

            ... class Item(models.Model):
            ...     emails_to_users: pgjsonschema.Validator[UsersRoot] = models.JSONField()
        """
