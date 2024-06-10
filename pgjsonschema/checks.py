from typing import Any

from django.conf import settings
from django.core import checks


@checks.register(checks.Tags.compatibility)
def check_pgtrigger_installed(app_configs: Any, **kwargs: Any) -> list[checks.Error]:
    errors: list[checks.Error] = []

    if "pgtrigger" not in settings.INSTALLED_APPS:
        errors.append(
            checks.Error(
                'Add "pgtrigger" to settings.INSTALLED_APPS to use django-pghistory.',
                id="pghistory.E001",
            )
        )

    return errors
