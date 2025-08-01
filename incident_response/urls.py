from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('incidents', views.IncidentViewSet)
router.register('actions', views.ActionViewSet)
router.register('deliverables', views.DeliverableViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-ai/', views.generate_ai, name='generate-ai'),
    path('download-pdf/<int:deliverable_id>/', views.download_deliverable_pdf, name='download_pdf'),
    path('download-all-pdfs/', views.download_all_pdfs, name='download_all_pdfs'),
    path('trigger-automation/', views.trigger_full_automation, name='trigger_automation'),
    path('editor/<int:deliverable_id>/', views.document_editor, name='document_editor'),
    # COMMENT OUT THESE PROBLEMATIC LINES:
    # path('ai-format-selector/<int:deliverable_id>/', views.ai_format_selector, name='ai_format_selector'),
    # path('export-deliverable/<int:deliverable_id>/<str:format_type>/', views.export_deliverable_format, name='export_deliverable_format'),
    path('save-document/<int:deliverable_id>/', views.save_document_content, name='save_document'),
    path('generate-ai-adaptive/', views.generate_ai_with_adaptive_agent, name='generate-ai-adaptive'),
    path('scheduled-automation/', views.trigger_scheduled_automation_enhanced, name='scheduled_automation'),   
    path('ai-document-review/', views.ai_document_review, name='ai_document_review'),
    path('auto-enhance-documents/', views.auto_enhance_documents, name='auto_enhance_documents'),
    path('ai-action-prioritization/', views.ai_action_prioritization, name='ai_action_prioritization'),
    # path('optimize-workflow/', views.optimize_workflow, name='optimize_workflow'),
    path('ai-decision-support/', views.ai_decision_support, name='ai_decision_support'),
    path('predictive-analytics/', views.predictive_analytics, name='predictive_analytics'),
    path('escalation-triggers/', views.automated_escalation_triggers, name='escalation_triggers'),
    path('real-time-metrics/', views.real_time_metrics, name='real_time_metrics'),
    path('system-health/', views.system_health_check, name='system_health'),
    path('activity-feed/', views.live_activity_feed, name='activity_feed'),
    path('create-alert/', views.create_alert, name='create_alert'),
    path('system-status/', views.system_health_check, name='system_status'),    
     path('ai-agent-status/', views.ai_agent_status, name='ai_agent_status'),
    path('ai-agent-status/<int:incident_id>/', views.ai_agent_status, name='ai_agent_status_by_incident'),      
    path('generate-guard-documentation/', views.generate_guard_compliant_documentation, name='generate_guard_documentation'),
    path('guard-framework-status/', views.guard_framework_status, name='guard_framework_status'),
]


