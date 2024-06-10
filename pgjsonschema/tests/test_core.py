import pytest
from django import db
from django.db import transaction

from pgjsonschema.tests.models import FakeModel, Payment


@pytest.fixture()
def test_model() -> FakeModel:
    user = {"username": "doe", "email": "doe@gmail.com"}
    return FakeModel(
        unannotated_json_field={"key": "value"},
        user=user,
        names_to_users={"Jane Doe": user, "John Doe": user},
    )


@pytest.mark.django_db()
def test_basic_validation(test_model: FakeModel):
    """Test basic validation of a JSONField, that uses a standard Pydantic model."""
    test_model.save()
    test_model.user = "string"  # type: ignore
    with pytest.raises(db.InternalError), transaction.atomic():
        test_model.save()

    # Test case where the schema is partially correct.
    test_model.user = {"username": 1, "email": "doe2@gmail.com"}  # type: ignore
    with pytest.raises(db.InternalError):
        test_model.save()


@pytest.mark.django_db()
def test_root_model_validation(test_model: FakeModel):
    """Test validation of a JSONField, that uses a root model for its validation."""
    test_model.save()

    # Modify the schema so that it's now incorrect.
    test_model.names_to_users["John Doe"]["username"] = 1  # type: ignore
    with pytest.raises(db.InternalError):
        test_model.save()


@pytest.mark.django_db()
def test_arbritrary_json_validation():
    """Test validation of a JSONField, that uses a non-Pydantic model for its validation."""
    payment = Payment(
        user={"username": "doe"},
        user_dump="string",
        amount=1,
        items=["item"],
        prices=[1],
        nullable_prices=[1, None],
    )
    payment.save()

    payment.user = {"username": 1}  # type: ignore
    with pytest.raises(db.InternalError), transaction.atomic():
        payment.save()
    payment.user = {"username": "doe"}

    payment.user_dump = 1  # type: ignore
    with pytest.raises(db.InternalError), transaction.atomic():
        payment.save()
    payment.user_dump = "string"

    payment.amount = "string"  # type: ignore
    with pytest.raises(db.InternalError), transaction.atomic():
        payment.save()
    payment.amount = 1

    payment.items = ["items", None]  # type: ignore
    with pytest.raises(db.InternalError), transaction.atomic():
        payment.save()
    payment.items = ["item"]

    payment.prices = [1, "string"]  # type: ignore
    with pytest.raises(db.InternalError):
        payment.save()
