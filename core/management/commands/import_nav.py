from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Deprecated: NavItem has been removed. This command is no longer available."

    def add_arguments(self, parser) -> None:  # type: ignore[override]
        # Keep signature for backward compatibility but no args are needed.
        return

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "import_nav has been removed. Navigation is now managed by static templates."
            )
        )
        self.stdout.write("No action taken.")
