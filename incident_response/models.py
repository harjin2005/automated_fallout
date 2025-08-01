import uuid
from django.db import models
from django.utils import timezone

class Incident(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    control_objective = models.TextField(blank=True, null=True, default='')
    framework_citations = models.TextField(blank=True, null=True, default='')
    status = models.CharField(max_length=50, default='PLAN_GENERATION')  # ✅ NEW
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return self.title

class ActionPlan(models.Model):
    CONFIDENCE_CHOICES = [
        ('HIGH', 'High (85-95%)'),
        ('MEDIUM', 'Medium (70-84%)'),
        ('LOW', 'Low (60-69%)'),
    ]
    
    RISK_CHOICES = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
    ]
    
    STATUS_CHOICES = [
        ('GENERATED', 'AI Generated'),
        ('SELECTED', 'User Selected'),
        ('REJECTED', 'Rejected'),
    ]
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='action_plans')
    plan_name = models.CharField(max_length=200)
    strategy = models.TextField()
    timeline = models.CharField(max_length=100) 
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default='MEDIUM')
    confidence_score = models.CharField(max_length=20, choices=CONFIDENCE_CHOICES, default='MEDIUM')
    estimated_hours = models.IntegerField(default=2)
    resource_requirements = models.TextField(blank=True)
    success_criteria = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='GENERATED')
    is_selected = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-confidence_score', 'risk_level']
    
    def __str__(self):
        return f"{self.plan_name} - {self.incident.title}"

class Action(models.Model):
    action_plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE, related_name='actions', null=True, blank=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='actions')  # for backwards compatibility
    step = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    operator = models.CharField(max_length=255)
    priority = models.CharField(max_length=20, default='Medium')
    estimated_hours = models.IntegerField(blank=True, null=True)
    ghostdraft = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['step']
    
    def __str__(self):
        return f"Step {self.step}: {self.title}"

class Deliverable(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name='deliverables')
    deliverable_format = models.CharField(max_length=50, default='HTML')
    content = models.TextField(blank=True)
    export_options = models.CharField(max_length=255, blank=True, default='PDF,Email')
    voice_eligible = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Deliverable for {self.action.title}"

class AIAgentStatus(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE, null=True, blank=True)
    current_expertise = models.CharField(max_length=200)
    status_message = models.TextField()
    decision_reasoning = models.TextField()
    confidence_score = models.FloatField(default=0.0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"AI Agent: {self.current_expertise} - {self.status_message[:50]}"
