import json
import typing
from typing import (
    Any,
    NamedTuple,
    TypeVar,
)

import pgtrigger
import pydantic
from django.db import models

import pgjsonschema
from pgjsonschema.types import JSONType

M = TypeVar("M", bound=models.Model)
T = TypeVar("T", bound=JSONType)


class ValidatedField(NamedTuple):
    """Field that's being validated."""

    django_field: models.JSONField
    validated_type: type[pydantic.BaseModel | pydantic.RootModel[Any]] | JSONType


def _generate_validation_trigger(fields: list[ValidatedField]) -> pgtrigger.Trigger:
    """Generates a trigger that validates the JSON fields of a Django model.

    Args:
        field: The JSONField to validate.
        json_type: The type of the JSON field to validate.
            This can be a Pydantic model or any valid JSON type.

    Returns:
        The trigger that validates the JSON field.
    """
    sql = ""
    for field in fields:
        adapter = pydantic.TypeAdapter(field.validated_type)
        schema = json.dumps(adapter.json_schema()).replace("'", "''")
        field_name = field.django_field.attname
        sql += f"""
            IF NOT validate_json(NEW."{field_name}", '{schema}'::json) THEN
                RAISE EXCEPTION 'The JSON field % must match the schema % but does not.', '{field_name}', '{schema}';
            END IF;
        """
    sql += "RETURN NEW;"
    trigger = pgtrigger.Trigger(
        name="validate_json_fields",
        operation=pgtrigger.Insert | pgtrigger.Update,
        when=pgtrigger.Before,
        func=sql,
    )
    return trigger


def install(model: type[M]) -> None:
    """Installl validation triggers on a Django model to ensure JSONField data is valid.

    Adding this decorator will install a trigger on your model using `django-pgtrigger` that will
    validate all JSONFields on your model annotated with the schema for the annotated Pydantic model.

    Args:
        model: The Django model to install the validation triggers on.

    Raises:
        TypeError: If the JSON type for a JSONField is not a Pydantic model
            when using `Annotated` as the method of specifying the type to validate
            against.
    """
    annotations = typing.get_type_hints(model, include_extras=True)
    fields_to_validate: list[ValidatedField] = []
    for field in model._meta.fields:
        # We support two types of annotations: `Annotated` and `Validator`.
        is_json_field = isinstance(field, models.JSONField)
        annotation = annotations.get(field.name)
        if is_json_field and annotation and hasattr(annotation, "__metadata__"):
            # Grab the annotated Pydantic model to use for the actual runtime validation.
            pydantic_model = annotations[field.name].__metadata__[0]
            if not issubclass(pydantic_model, pydantic.BaseModel | pydantic.RootModel):
                raise TypeError(
                    f"The JSON type for {field.name} must be a Pydantic model."
                )
            fields_to_validate.append(ValidatedField(field, pydantic_model))
        elif (
            is_json_field
            and annotation
            and issubclass(
                typing.get_origin(annotation),
                pgjsonschema.Validator,  # type: ignore
            )
        ):
            validation_type = typing.get_args(annotation)[0]
            fields_to_validate.append(ValidatedField(field, validation_type))

    if fields_to_validate:
        trigger = _generate_validation_trigger(fields_to_validate)
        pgtrigger.register(trigger)(model)
