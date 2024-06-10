# django-pgjsonschema

`django-pgjsonschema` is a library designed to help you efficiently validate Postgres JSON fields on your Django models using [Pydantic](https://docs.pydantic.dev/latest/) and [pl/rust](https://plrust.io/).

## Quick Start

To get started, define a Pydantic model that represents the schema you want to validate your JSON field against:

```python
import pydantic


class MySchema(pydantic.BaseModel):
    name: str
    age: int
```

Now, simply add a type annotation with `pgjsonschema.Validator` to your models' JSON field.

```python
from django.db import models

from pgjsonschema import Validator

class MyModel(models.Model):
    data: Validator[MySchema] = models.JSONField()
```

Or, provide an arbitrary Python type, assuming it represents a valid JSON structure:

```python
from typing import Any
from django.db import models

from pgjsonschema import Validator

class MyModel(models.Model):
    data: Validator[dict[str, Any]] = models.JSONField()
```

Adding this annotation will install a trigger on your Django model that will validate against the schema at the database level. This is done using [django-pgtrigger](https://github.com/Opus10/django-pgtrigger), another Opus 10 library used to manage the installation of Postgres triggers in Django applications. The installed trigger is built on [pl/rust](https://github.com/tcdi/plrust), which is a required Postgres extension for `django-pgjsonschema`.

## Compatibility

`django-pgjsonschema` is compatible with Python 3.11 - 3.12, Django 3.2 - 5.0, Psycopg 2 - 3, and Postgres 12 - 16.

## Installation

Install `django-pgjsonschema` with:

    pip3 install django-pgjsonschema

After this, add `pgjsonschema` and `pgtrigger` to the `INSTALLED_APPS` setting of your Django project.

Additionally, you will need to install the `pl/rust` extension in your Postgres database. You can follow the installation instructions [here](https://plrust.io/install-prerequisites.html). pl/rust is a trusted procedural language, which allows you to write Postgres functions in Rust. We utilize to ensure efficent and performant validation of JSON fields, miniimally impacting your database write performance.

## Primary Authors

- [Max Muoto](https://github.com/max-muoto)
