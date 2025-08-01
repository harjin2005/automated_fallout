from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from .models import Incident, ActionPlan, Action, Deliverable, AIAgentStatus

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('title', 'description')
    readonly_fields = ('timestamp',)

@admin.register(ActionPlan)
class ActionPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan_name', 'incident', 'risk_level', 'confidence_score', 'is_selected', 'status')
    list_filter = ('risk_level', 'confidence_score', 'status', 'is_selected')
    search_fields = ('plan_name', 'strategy', 'incident__title')
    list_editable = ('is_selected',)  
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('incident', 'plan_name', 'strategy', 'timeline')
        }),
        ('Assessment', {
            'fields': ('risk_level', 'confidence_score', 'estimated_hours')
        }),
        ('Resources & Success', {
            'fields': ('resource_requirements', 'success_criteria')
        }),
        ('Status', {
            'fields': ('status', 'is_selected', 'created_at')
        }),
    )

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('step', 'title', 'incident', 'action_plan', 'operator', 'priority', 'ghostdraft')
    list_filter = ('priority', 'ghostdraft', 'incident', 'action_plan')
    search_fields = ('title', 'description', 'operator')

@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'deliverable_format', 'voice_eligible', 'content_preview', 'download_link')
    list_filter = ('deliverable_format', 'voice_eligible')
    search_fields = ('action__title',)
    readonly_fields = ('download_link',)
    
    def content_preview(self, obj):
        """Show content preview"""
        if obj.content:
            preview = obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
            return preview
        return "No content"
    content_preview.short_description = "Content Preview"
    
    def download_link(self, obj):
        """Add download link in the admin interface"""
        if obj.content:
            url = reverse('admin:download_deliverable', args=[obj.pk])
            return format_html('<a href="{}">📄 Download Documentation</a>', url)
        return "No content available"
    download_link.short_description = "Download"
    
    def get_urls(self):
        """Add custom URL for downloading"""
        urls = super().get_urls()
        custom_urls = [
            path('<int:deliverable_id>/download/', 
                 self.admin_site.admin_view(self.download_deliverable), 
                 name='download_deliverable'),
        ]
        return custom_urls + urls
    
    def download_deliverable(self, request, deliverable_id):
        """Custom view to download deliverable as PDF"""
        try:
            deliverable = Deliverable.objects.get(id=deliverable_id)
            
            response = HttpResponse(content_type='application/pdf')
            filename = f"deliverable_{deliverable.action.title.replace(' ', '_')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            
            y_position = 750
            p.drawString(50, y_position, f"🤖 ADAPTIVE AI DOCUMENTATION")
            y_position -= 20
            p.drawString(50, y_position, f"Action: {deliverable.action.title}")
            y_position -= 15
            p.drawString(50, y_position, f"Incident: {deliverable.action.incident.title}")
            y_position -= 30
            
            content_lines = deliverable.content.split('\n')
            for line in content_lines:
                if y_position < 50:
                    p.showPage()
                    y_position = 750
                # Handle long lines and special characters
                clean_line = line.replace('🤖', 'AI').replace('🛡️', '').replace('✅', '*')
                p.drawString(50, y_position, clean_line[:80])
                y_position -= 12
            
            p.save()
            buffer.seek(0)
            response.write(buffer.getvalue())
            buffer.close()
            
            return response
            
        except Deliverable.DoesNotExist:
            return HttpResponse("Deliverable not found", status=404)

@admin.register(AIAgentStatus)
class AIAgentStatusAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'incident', 
        'current_expertise', 
        'confidence_score', 
        'status_message_short', 
        'started_at', 
        'completed_at',
        'duration'
    )
    list_filter = (
        'current_expertise',
        'confidence_score',
        'started_at',
        'completed_at',
        ('incident', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'current_expertise',
        'status_message',
        'decision_reasoning',
        'incident__title'
    )
    readonly_fields = ('started_at', 'duration')
    raw_id_fields = ('incident', 'action')
    
    fieldsets = (
        ('AI Agent Information', {
            'fields': ('incident', 'action', 'current_expertise')
        }),
        ('Status & Progress', {
            'fields': ('status_message', 'confidence_score', 'decision_reasoning')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration'),
            'classes': ('collapse',)
        }),
    )
    
    def status_message_short(self, obj):
        """Display truncated status message"""
        return obj.status_message[:80] + "..." if len(obj.status_message) > 80 else obj.status_message
    status_message_short.short_description = "Status Message"
    
    def duration(self, obj):
        """Calculate duration if completed"""
        if obj.completed_at and obj.started_at:
            delta = obj.completed_at - obj.started_at
            total_seconds = int(delta.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            return f"{minutes}m {seconds}s"
        return "In Progress" if obj.started_at else "Not Started"
    duration.short_description = "Duration"
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related('incident', 'action')
