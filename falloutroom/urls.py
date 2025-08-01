from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("""
    <h1>🛡️ Fallout Room Crisis Response System</h1>
    <p><a href="/admin/">Admin Panel</a></p>
    <p><a href="/api/">API Root</a></p>
    <p><a href="/api/incidents/">Incidents API</a></p>
    """)

urlpatterns = [
    path('', home_view, name='home'),  # Add this line
    path('admin/', admin.site.urls),
    path('api/', include('incident_response.urls')),
]
