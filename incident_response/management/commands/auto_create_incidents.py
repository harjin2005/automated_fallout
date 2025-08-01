from django.core.management.base import BaseCommand
from incident_response.models import Incident
from django.utils import timezone  # ✅ Use timezone-aware datetime

class Command(BaseCommand):
    help = 'Automatically creates a new incident for testing automation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-new',
            action='store_true',
            help='Force creation of new incident (default behavior)',
        )

    def handle(self, *args, **kwargs):
        # Generate unique timestamp-based title
        now = timezone.now()  # ✅ Use timezone-aware datetime
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        title = f"AUTOMATED: Security Incident - {timestamp}"
        description = f"This incident was created automatically on {now.strftime('%Y-%m-%d %H:%M:%S')} through automated management command."

        try:
            incident = Incident.objects.create(
                title=title,
                description=description,
                timestamp=now  # ✅ Use timezone-aware datetime
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Created NEW incident: '{incident.title}' (ID: {incident.id})"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"📋 Incident ready for action plan generation and AI processing"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Failed to create incident: {str(e)}"
                )
            )
            raise
