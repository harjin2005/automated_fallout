import requests
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Trigger AI content generation for all GhostDraft deliverables via API'

    def handle(self, *args, **kwargs):
        url = getattr(settings, "AI_GENERATION_API_URL", "http://localhost:8000/api/generate-ai/")
        try:
            response = requests.post(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.stdout.write(self.style.SUCCESS(f"AI generation successful: {data.get('message')}"))
                else:
                    self.stdout.write(self.style.ERROR(f"AI generation failed: {data}"))
            else:
                self.stdout.write(self.style.ERROR(f"Request failed with status {response.status_code}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during AI generation: {str(e)}"))
