# Generated by Django 5.2.4 on 2025-08-01 05:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incident_response', '0004_alter_deliverable_deliverable_format_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='estimated_hours',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='action',
            name='priority',
            field=models.CharField(default='Medium', max_length=20),
        ),
        migrations.AddField(
            model_name='incident',
            name='status',
            field=models.CharField(default='PLAN_GENERATION', max_length=50),
        ),
        migrations.CreateModel(
            name='ActionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_name', models.CharField(max_length=200)),
                ('strategy', models.TextField()),
                ('timeline', models.CharField(max_length=100)),
                ('risk_level', models.CharField(choices=[('LOW', 'Low Risk'), ('MEDIUM', 'Medium Risk'), ('HIGH', 'High Risk')], default='MEDIUM', max_length=20)),
                ('confidence_score', models.CharField(choices=[('HIGH', 'High (85-95%)'), ('MEDIUM', 'Medium (70-84%)'), ('LOW', 'Low (60-69%)')], default='MEDIUM', max_length=20)),
                ('estimated_hours', models.IntegerField(default=2)),
                ('resource_requirements', models.TextField(blank=True)),
                ('success_criteria', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('GENERATED', 'AI Generated'), ('SELECTED', 'User Selected'), ('REJECTED', 'Rejected')], default='GENERATED', max_length=20)),
                ('is_selected', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_plans', to='incident_response.incident')),
            ],
            options={
                'ordering': ['-confidence_score', 'risk_level'],
            },
        ),
        migrations.AddField(
            model_name='action',
            name='action_plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='incident_response.actionplan'),
        ),
    ]
