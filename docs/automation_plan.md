# Fallout Room Automation Plan

## Overview

This document describes the automation workflow for Fallout Room—how incidents, actions, and deliverables are generated, and how AI content is filled using OpenRouter.

---

## Management Commands

- `auto_create_incidents`: Automatically creates a new incident with default values if not already present.
- `auto_create_actions_deliverables`: For the latest incident, auto-generates actions (steps) and deliverables (documents) using predefined templates.
- `trigger_ai_generation`: Fills blank deliverables linked to “ghostdraft” actions using OpenRouter AI.

---

## How to Run the Full Automation Workflow

1. Open CMD in the project directory.
2. Run the batch file:
    ```
    full_automation.bat
    ```
    This:
    - Creates an incident (if not already present)
    - Adds actions and deliverables
    - Triggers OpenRouter AI to generate draft documents

3. Review results in Django admin:
    - Check “Incidents”, then related “Actions” and “Deliverables” for AI-generated content.

---

## API Key and Security

- Your OpenRouter API Key is stored in the `.env` file in the project root:
    ```
    OPENROUTER_API_KEY=YOUR_KEY_HERE
    ```
- **Never commit the `.env` file to public code repositories.** Change keys here if they need to be rotated.

---

## Updating or Adding Templates

- To modify what actions or deliverables are generated, edit the `actions_data` list in `auto_create_actions_deliverables.py`.
- To update or extend prompt instructions for AI, modify the prompt in `views.py` under the `generate_ai` function.

---

## Manual Steps

- To reset or create new test data, clear or delete actions/deliverables in Django admin, or use a future `reset_test_data` command.
- To trigger automation on a schedule, use Windows Task Scheduler or (optionally) Apache Airflow.

---

## For Developers

- For any new integrations, document the API endpoints and update this file.
- Keep this documentation up-to-date for team, client, and audit readiness.

---

_Last updated: July 30, 2025_

# Fallout Room - Professional Incident Response Automation

## ✅ COMPLETED FEATURES

### Core Automation
- **Automated Incident Creation**: Creates incidents with proper control objectives and framework citations
- **Advanced Action Plan Generation**: 5 detailed action plans with timelines, resources, and compliance mapping
- **AI-Powered Document Generation**: Professional-grade deliverables using OpenRouter AI
- **PDF Export**: Download any deliverable as formatted PDF document
- **One-Click Automation**: Complete workflow via batch script or API call

### Action Plans Include:
1. **Customer Notification & Communication** (GDPR compliant)
2. **Regulatory Filing & Compliance Response** (SEC, GDPR)
3. **Technical Containment & Forensics** (ISO 27035, NIST)
4. **Executive Leadership & Board Communication** (SOX compliance)
5. **Business Continuity & Recovery Planning** (ISO 22301)

## 🚀 HOW TO USE

### Method 1: Batch Script
full_automation.bat

text

### Method 2: API Call (for frontend integration)
POST /api/trigger-automation/

text

### Method 3: Individual Commands
python manage.py auto_create_incidents
python manage.py auto_create_actions_deliverables
python manage.py trigger_ai_generation

text

## 📥 DOWNLOAD DOCUMENTS

Access via: `/api/download-pdf/{deliverable_id}/`

## 🎯 BUSINESS VALUE

- **Time Savings**: Reduces incident response setup from hours to minutes
- **Compliance**: Built-in GDPR, ISO, NIST, SOX framework mapping  
- **Quality**: AI-generated professional documentation
- **Auditability**: Complete trail of actions and decisions
- **Scalability**: Template-driven approach for consistent responses

## 🔧 TECHNICAL STACK

- **Backend**: Django 5.2, Django REST Framework
- **AI**: OpenRouter (GPT-3.5-turbo)
- **Database**: SQLite (dev), PostgreSQL ready
- **Export**: ReportLab PDF generation
- **Deployment**: PythonAnywhere ready

---
*Last updated: July 30, 2025 - Production Ready*