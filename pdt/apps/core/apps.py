from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self) -> None:
        from django.db.models.signals import post_delete, post_save

        from .glossary import invalidate_glossary_cache
        from .models import GlossaryTerm

        post_save.connect(invalidate_glossary_cache, sender=GlossaryTerm)
        post_delete.connect(invalidate_glossary_cache, sender=GlossaryTerm)
