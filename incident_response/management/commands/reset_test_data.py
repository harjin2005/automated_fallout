from django.core.management.base import BaseCommand
from incident_response.models import Incident, Action, Deliverable

class Command(BaseCommand):
    help = 'Clears deliverable content for re-running tests or demos.'

    def handle(self, *args, **kwargs):
        # Clear deliverable content only (keeps structure intact)
        updated = Deliverable.objects.update(content='')
        self.stdout.write(self.style.SUCCESS(f"Cleared content for {updated} deliverables."))
        
        # Optional: Uncomment below to delete all test data completely
        # Deliverable.objects.all().delete()
        # Action.objects.all().delete() 
        # Incident.objects.all().delete()
        # self.stdout.write(self.style.SUCCESS("Deleted all test incidents, actions, and deliverables."))
