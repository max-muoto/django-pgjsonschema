from django.apps import AppConfig, apps

from pgjsonschema import triggers


class StructuredJSONConfig(AppConfig):
    name = "pgjsonschema"

    def ready(self) -> None:
        """Install triggers on all models with JSONFields."""
        for app in apps.get_app_configs():
            for model in app.get_models():
                triggers.install(model)
