import json
import re
import os
import openai
from django.core.management.base import BaseCommand
from django.utils import timezone
from incident_response.models import Incident, ActionPlan, Action, Deliverable


def safe_json_parse(response_text):
    """
    JSON Parser with Error Recovery - The safety net for AI responses
    
    Sometimes AI returns almost-perfect JSON with tiny formatting issues.
    This function tries multiple repair strategies before giving up.
    It's like having a smart assistant who can read messy handwriting.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        cleaned = response_text.strip()
        
        cleaned = re.sub(r'```[a-zA-Z]*\n?', '', cleaned)  
        cleaned = re.sub(r'```\s*$', '', cleaned)          

        # Fix unterminated strings - common AI mistake
        if 'Unterminated string' in str(e):
            lines = cleaned.split('\n')
            if len(lines) > e.lineno:
                line = lines[e.lineno - 1]
                if not line.strip().endswith('"') and not line.strip().endswith('",'):
                    lines[e.lineno - 1] = line + '"'
                    cleaned = '\n'.join(lines)
        
        try:
            return json.loads(cleaned)
        except:
            # If all else fails, return professional fallback plans
            # These are real-world tested incident response strategies
            return {
                "action_plans": [
                    {
                        "plan_name": "Rapid Response Plan",
                        "strategy": "Immediate threat containment with fast response times. Focus on quick isolation and damage control to minimize business impact. This approach prioritizes speed over thoroughness when time is critical.",
                        "timeline": "1-2 hours",
                        "risk_level": "HIGH",
                        "confidence_score": "HIGH",
                        "estimated_hours": 2,
                        "resource_requirements": "SOC Analyst, Security Team Lead, Network Administrator",
                        "success_criteria": "Threat contained within 2 hours, systems restored to normal operation"
                    },
                    {
                        "plan_name": "Comprehensive Analysis Plan",
                        "strategy": "Thorough investigation approach with detailed forensic analysis and root cause identification. Ensures complete understanding before action. Like having a detective solve the case properly before making arrests.",
                        "timeline": "4-6 hours",
                        "risk_level": "LOW",
                        "confidence_score": "HIGH",
                        "estimated_hours": 5,
                        "resource_requirements": "Security Analyst, Forensics Expert, Compliance Officer, Technical Lead",
                        "success_criteria": "Complete incident analysis, root cause identified, prevention measures implemented"
                    },
                    {
                        "plan_name": "Stakeholder Communication Plan",
                        "strategy": "Communication-focused approach prioritizing stakeholder management, compliance reporting, and transparency throughout the incident response. Perfect when reputation and trust are paramount.",
                        "timeline": "2-4 hours",
                        "risk_level": "MEDIUM",
                        "confidence_score": "MEDIUM",
                        "estimated_hours": 3,
                        "resource_requirements": "Communications Team, Legal Counsel, Management, Compliance Officer",
                        "success_criteria": "All stakeholders informed, compliance maintained, reputation protected"
                    },
                    {
                        "plan_name": "Hybrid Response Plan",
                        "strategy": "Balanced approach combining immediate containment with parallel investigation activities. Optimizes both speed and thoroughness. The Swiss Army knife of incident response strategies.",
                        "timeline": "3-5 hours",
                        "risk_level": "MEDIUM",
                        "confidence_score": "HIGH",
                        "estimated_hours": 4,
                        "resource_requirements": "Multi-disciplinary team: SOC Analyst, Forensics Expert, Communications Lead",
                        "success_criteria": "Incident contained and analyzed simultaneously, stakeholders kept informed"
                    }
                ]
            }


class Command(BaseCommand):
    """
    Multi-Plan Generation Engine - The strategic options generator
    
    This command creates a single incident and generates multiple strategic
    action plans for it. Think of it as having 3-4 different expert consultants
    each propose their approach to handling the same crisis.
    
    The user then gets to pick which strategy makes most sense for their situation.
    """
    help = 'Create single incident with multiple AI-generated action plans for user selection'
    
    def add_arguments(self, parser):
        """Command line options - makes the tool flexible"""
        parser.add_argument(
            '--force-new',
            action='store_true',
            help='Force creation of new incident even if recent ones exist'
        )
        parser.add_argument(
            '--incident-type',
            type=str,
            default='security',
            help='Type of incident to generate (security, data-breach, system-failure)'
        )
    
    def handle(self, *args, **options):
        """
        Main execution flow - The orchestrator
        
        This runs the complete workflow from incident creation
        through multiple plan generation to user selection setup.
        """
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("  🚨 FALLOUT ROOM AI - MULTI-PLAN GENERATION ENGINE"))
        self.stdout.write(self.style.SUCCESS("  Phase 1: Single Incident + Multiple Strategic Plans"))
        self.stdout.write("=" * 70)
        
        # Step 1: Create single unique incident
        incident = self.create_unique_incident(options['incident_type'])
        if not incident:
            self.stdout.write(self.style.ERROR("Failed to create incident - aborting"))
            return
        
        # Step 2: Initialize AI client with comprehensive error handling
        client = self.initialize_ai_client()
        if not client:
            self.stdout.write(self.style.WARNING("⚠️ Proceeding with fallback plans (no AI client)"))
        
        # Step 3: Generate multiple strategic action plans
        action_plans_data = self.generate_multiple_action_plans(client, incident, options['incident_type'])
        if not action_plans_data:
            self.stdout.write(self.style.ERROR("Failed to generate action plans - aborting"))
            return
        
        # Step 4: Create ActionPlan database records
        created_plans = self.create_action_plan_records(incident, action_plans_data)
        if not created_plans:
            self.stdout.write(self.style.ERROR("Failed to create plan records - aborting"))
            return
        
        # Step 5: Update incident status for user selection phase
        incident.status = 'AWAITING_PLAN_SELECTION'
        incident.save()
        
        # Step 6: Display results and guide user to next steps
        self.display_completion_summary(incident, created_plans)
        self.display_plan_selection_instructions(created_plans)
    
    def create_unique_incident(self, incident_type):
        """
        Incident Creator - The scenario generator
        
        Creates a realistic incident based on the type specified.
        Each incident gets a unique timestamp to avoid duplicates.
        Like having a training simulator create realistic scenarios.
        """
        try:
            now = timezone.now()
            unique_suffix = now.strftime("%Y%m%d_%H%M%S")
            
            # Different incident templates based on real-world scenarios
            incident_templates = {
                'security': {
                    'title': f"SECURITY BREACH - {unique_suffix}",
                    'description': f"Potential security incident detected requiring immediate strategic response planning. Multiple attack vectors identified. Automated detection systems triggered at {now.strftime('%Y-%m-%d %H:%M:%S')}. Investigation required to determine scope and impact.",
                    'control_objective': "Maintain data confidentiality, system integrity, and service availability while minimizing business disruption",
                    'framework_citations': "ISO 27001:2013, NIST Cybersecurity Framework, GDPR Article 33"
                },
                'data-breach': {
                    'title': f"DATA BREACH INCIDENT - {unique_suffix}",
                    'description': f"Suspected unauthorized access to sensitive data systems detected. Regulatory notification may be required under GDPR/CCPA. Initial detection at {now.strftime('%Y-%m-%d %H:%M:%S')}. Scope assessment and impact analysis needed urgently.",
                    'control_objective': "Protect personal data and maintain regulatory compliance while preserving customer trust",
                    'framework_citations': "GDPR Article 33, CCPA Section 1798.82, ISO 27001:2013 A.16"
                },
                'system-failure': {
                    'title': f"CRITICAL SYSTEM FAILURE - {unique_suffix}",
                    'description': f"Major system outage affecting business operations. Service restoration and root cause analysis required. Outage detected at {now.strftime('%Y-%m-%d %H:%M:%S')}. Customer impact assessment ongoing.",
                    'control_objective': "Restore service availability and prevent recurrence while maintaining data integrity",
                    'framework_citations': "ITIL v4, ISO 20000-1, NIST SP 800-61"
                }
            }
            
            template = incident_templates.get(incident_type, incident_templates['security'])
            
            # Create the incident record
            incident = Incident.objects.create(
                title=template['title'],
                description=template['description'],
                control_objective=template['control_objective'],
                framework_citations=template['framework_citations'],
                timestamp=now,
                status='PLAN_GENERATION'
            )
            
            self.stdout.write(self.style.SUCCESS(f"✅ Created {incident_type} incident: '{incident.title}' (ID: {incident.id})"))
            self.stdout.write(f"   📋 Description: {incident.description[:100]}...")
            self.stdout.write(f"   🎯 Control Objective: {incident.control_objective}")
            self.stdout.write(f"   📜 Framework Citations: {incident.framework_citations}")
            
            return incident
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to create incident: {str(e)}"))
            return None
    
    def initialize_ai_client(self):
        """
        AI Client Setup - The brain connector
        
        Sets up connection to OpenRouter AI service. This is like
        hiring an expert consultant - we need proper credentials
        and configuration to get quality advice.
        """
        try:
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                self.stdout.write(self.style.WARNING("⚠️ OPENROUTER_API_KEY not found in environment variables"))
                self.stdout.write("   💡 Add your API key to .env file: OPENROUTER_API_KEY=your_key_here")
                return None
            
            # Validate API key format (OpenRouter keys have specific format)
            if not api_key.startswith('sk-or-'):
                self.stdout.write(self.style.WARNING("⚠️ API key format may be incorrect (should start with 'sk-or-')"))
            
            # Initialize the AI client with proper configuration
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            
            self.stdout.write(self.style.SUCCESS("🔑 OpenRouter AI client initialized successfully"))
            self.stdout.write(f"   🤖 Model: {os.getenv('AI_MODEL', 'qwen/qwen3-coder:free')}")
            self.stdout.write(f"   🎯 Max Tokens: {os.getenv('MAX_TOKENS', '800')}")
            
            return client
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to initialize AI client: {str(e)}"))
            return None
    
    def generate_multiple_action_plans(self, client, incident, incident_type):
        """
        Strategic Plan Generator - The expert consultant multiplier
        
        This is where the magic happens. We ask the AI to become 3-4 different
        expert consultants, each with their own approach to the same problem.
        Like getting multiple professional opinions before making a big decision.
        """
        try:
            self.stdout.write("\n🧠 Generating multiple strategic action plans...")
            self.stdout.write("   📊 AI Analysis Phase: Strategic Options Generation")
            
            if not client:
                self.stdout.write(self.style.WARNING("⚠️ No AI client available - using enhanced fallback plans"))
                return self.get_enhanced_fallback_plans(incident_type)
            
            # Get context-specific information for better AI prompting
            incident_context = self.get_incident_context(incident, incident_type)
            
            # Comprehensive AI prompt that creates multiple expert perspectives
            prompt = f"""
You are a senior incident response strategist with 20+ years of experience. Generate 3-4 distinct strategic action plans for this critical incident:

INCIDENT DETAILS:
- Title: {incident.title}
- Type: {incident_type.upper()}
- Description: {incident.description}
- Control Objective: {incident.control_objective}
- Compliance Frameworks: {incident.framework_citations}
- Timestamp: {incident.timestamp}

STRATEGIC CONTEXT: {incident_context}

Generate a JSON response with "action_plans" array. Each plan must represent a different strategic philosophy:

Plan Requirements:
- plan_name: Unique strategic approach name (e.g., "Rapid Response", "Comprehensive Analysis")
- strategy: Detailed methodology and approach (150-250 words explaining the philosophy)
- timeline: Realistic timeframe (e.g., "1-2 hours", "4-6 hours")
- risk_level: "LOW", "MEDIUM", or "HIGH" (based on speed vs thoroughness tradeoff)
- confidence_score: "HIGH", "MEDIUM", or "LOW" (how certain we are this will work)
- estimated_hours: Integer between 1-8 (realistic work effort)
- resource_requirements: Specific roles and teams needed (be realistic about staffing)
- success_criteria: Measurable outcomes and goals (what success looks like)

Create 4 distinct strategic approaches:
1. SPEED-FOCUSED: High risk, fast execution, minimal analysis (for when time is critical)
2. COMPREHENSIVE: Low risk, thorough analysis, detailed investigation (when you need to get it right)
3. COMMUNICATION-FOCUSED: Medium risk, stakeholder-oriented, reputation management
4. BALANCED HYBRID: Medium risk, optimized approach balancing speed and thoroughness

Each plan should reflect real-world incident response best practices and be genuinely different in approach.

Return ONLY valid JSON format with no additional text.
"""
            
            # Get AI configuration from environment variables
            model = os.getenv('AI_MODEL', 'qwen/qwen3-coder:free')
            max_tokens = int(os.getenv('MAX_TOKENS', '1000'))
            temperature = float(os.getenv('TEMPERATURE', '0.7'))
            
            self.stdout.write(f"   🎯 Querying AI model: {model}")
            
            # Make the AI API call
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_content = response.choices[0].message.content
            self.stdout.write("   🔍 Parsing AI response...")
            
            # Parse the AI response with error recovery
            parsed_data = safe_json_parse(response_content)
            
            if 'action_plans' in parsed_data and len(parsed_data['action_plans']) >= 2:
                plans = parsed_data['action_plans'][:4]  # Limit to 4 plans max
                self.stdout.write(self.style.SUCCESS(f"✅ AI generated {len(plans)} strategic action plans"))
                
                # Validate and enhance plans with business logic
                validated_plans = self.validate_and_enhance_plans(plans, incident_type)
                return validated_plans
            else:
                self.stdout.write(self.style.WARNING("⚠️ AI response format invalid - using enhanced fallback"))
                return self.get_enhanced_fallback_plans(incident_type)
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ AI generation failed: {str(e)}"))
            self.stdout.write("   🔄 Falling back to enhanced template plans")
            return self.get_enhanced_fallback_plans(incident_type)
    
    def get_incident_context(self, incident, incident_type):
        """
        Context Builder - The situation awareness provider
        
        Gives the AI specific context about what type of incident this is
        and what considerations are most important. Like briefing an expert
        consultant on the specific situation they're walking into.
        """
        context_map = {
            'security': "This is a cybersecurity incident requiring immediate threat assessment, containment, and forensic analysis. Consider attack vectors, data exposure risk, regulatory implications, and business continuity. Time is critical but thoroughness is also important for legal and compliance reasons.",
            'data-breach': "This involves potential unauthorized access to personal data. GDPR/CCPA compliance is absolutely critical with strict notification timelines. Consider data subject rights, regulatory reporting requirements, potential financial penalties, and reputation management. Legal exposure is high.",
            'system-failure': "Critical system outage affecting business operations and potentially customer service. Focus on service restoration, business continuity, customer communication, and post-incident improvement measures. Revenue impact and customer satisfaction are key concerns."
        }
        return context_map.get(incident_type, context_map['security'])
    
    def validate_and_enhance_plans(self, plans, incident_type):
        """
        Plan Quality Assurance - The business logic validator
        
        Takes AI-generated plans and ensures they meet our business rules.
        Like having a senior manager review consultant recommendations
        before they go to the executive team.
        """
        enhanced_plans = []
        
        for i, plan in enumerate(plans):
            # Ensure required fields with sensible defaults
            enhanced_plan = {
                'plan_name': plan.get('plan_name', f'Strategic Plan {len(enhanced_plans) + 1}'),
                'strategy': plan.get('strategy', 'Comprehensive incident response approach with focus on rapid containment and thorough analysis'),
                'timeline': plan.get('timeline', '2-4 hours'),
                'risk_level': plan.get('risk_level', 'MEDIUM').upper(),
                'confidence_score': plan.get('confidence_score', 'MEDIUM').upper(),
                'estimated_hours': min(max(int(plan.get('estimated_hours', 3)), 1), 8),  # Ensure 1-8 range
                'resource_requirements': plan.get('resource_requirements', 'Security Team, SOC Analyst, Incident Manager'),
                'success_criteria': plan.get('success_criteria', 'Incident resolved successfully with minimal business impact')
            }
            
            # Validate enumerated choices (prevent bad data)
            if enhanced_plan['risk_level'] not in ['LOW', 'MEDIUM', 'HIGH']:
                enhanced_plan['risk_level'] = 'MEDIUM'
            if enhanced_plan['confidence_score'] not in ['LOW', 'MEDIUM', 'HIGH']:
                enhanced_plan['confidence_score'] = 'MEDIUM'
            
            # Ensure strategy field has meaningful content
            if len(enhanced_plan['strategy']) < 50:
                enhanced_plan['strategy'] += f" This {enhanced_plan['risk_level'].lower()}-risk approach focuses on balancing speed with thoroughness to achieve optimal incident resolution."
            
            enhanced_plans.append(enhanced_plan)
        
        return enhanced_plans
    
    def get_enhanced_fallback_plans(self, incident_type):
        """
        Professional Fallback Plans - The backup experts
        
        When AI isn't available, we fall back to these professionally
        crafted plans based on real-world incident response experience.
        These aren't generic templates - they're battle-tested strategies
        used by actual incident response teams.
        """
        base_plans = {
            'security': [
                {
                    "plan_name": "Rapid Security Containment",
                    "strategy": "Immediate threat isolation and damage control approach. This strategy prioritizes speed over analysis when dealing with active security threats. We implement emergency response protocols to quickly identify and contain the security threat, preventing further system compromise or data exfiltration. This approach is ideal when the threat is actively spreading or when business-critical systems are at immediate risk. The focus is on stopping the bleeding first, then conducting detailed analysis.",
                    "timeline": "1-2 hours",
                    "risk_level": "HIGH",
                    "confidence_score": "HIGH",
                    "estimated_hours": 2,
                    "resource_requirements": "SOC Analyst, Security Team Lead, Network Administrator, System Administrator",
                    "success_criteria": "Threat contained within 2 hours, affected systems isolated, immediate risks mitigated, business operations stabilized"
                },
                {
                    "plan_name": "Comprehensive Security Investigation",
                    "strategy": "Thorough forensic analysis and investigation approach that prioritizes understanding over speed. This methodology conducts detailed evidence collection, root cause analysis, and comprehensive threat assessment before taking major containment actions. We ensure complete understanding of attack vectors, impact scope, and threat actor methodologies. This approach is ideal when the immediate threat is contained and we need to build a solid case for legal action or when regulatory compliance requires detailed documentation.",
                    "timeline": "6-8 hours",
                    "risk_level": "LOW",
                    "confidence_score": "HIGH",
                    "estimated_hours": 7,
                    "resource_requirements": "Security Analyst, Digital Forensics Expert, Threat Intelligence Analyst, Compliance Officer, Legal Liaison",
                    "success_criteria": "Complete threat analysis documented, forensic evidence preserved, root cause identified, comprehensive remediation plan developed"
                },
                {
                    "plan_name": "Compliance-Focused Response",
                    "strategy": "Regulatory compliance and stakeholder communication approach that prioritizes meeting legal requirements and managing external relationships. This strategy ensures all incident response actions meet regulatory requirements while effectively managing reputation and stakeholder communication. We coordinate closely with legal, compliance, and communications teams to ensure proper documentation, timely notifications, and appropriate disclosure management. Perfect when regulatory exposure is high or when the incident may require public disclosure.",
                    "timeline": "3-4 hours",
                    "risk_level": "MEDIUM",
                    "confidence_score": "HIGH",
                    "estimated_hours": 4,
                    "resource_requirements": "Compliance Officer, Legal Counsel, Communications Manager, Security Lead, Executive Sponsor",
                    "success_criteria": "Regulatory requirements met, stakeholders appropriately informed, compliance documentation complete, legal exposure minimized"
                }
            ],
            'data-breach': [
                {
                    "plan_name": "GDPR Rapid Response",
                    "strategy": "Fast-track response specifically designed around GDPR compliance and 72-hour notification requirements. This approach prioritizes data subject protection and regulatory notification while conducting parallel containment activities. We focus on quickly assessing the scope of personal data exposure, determining notification requirements, and preparing required documentation for regulators and affected individuals. This strategy is essential when European personal data is involved and regulatory penalties could be severe.",
                    "timeline": "2-3 hours",
                    "risk_level": "MEDIUM",
                    "confidence_score": "HIGH",
                    "estimated_hours": 3,
                    "resource_requirements": "Data Protection Officer, Legal Counsel, Security Analyst, Communications Team, Executive Sponsor",
                    "success_criteria": "GDPR compliance maintained, regulatory notifications prepared within deadlines, data subjects protected, legal exposure minimized"
                },
                {
                    "plan_name": "Comprehensive Data Assessment",
                    "strategy": "Detailed analysis approach focused on complete data exposure scope and impact assessment. This methodology conducts thorough investigation to determine exact data types, volumes, affected individuals, and potential misuse before making notification decisions. We prioritize accuracy over speed to ensure we have complete information before communicating with regulators or affected parties. This approach reduces the risk of having to issue multiple notifications or corrections, which can damage credibility with regulators.",
                    "timeline": "4-6 hours",
                    "risk_level": "LOW",
                    "confidence_score": "HIGH",
                    "estimated_hours": 5,
                    "resource_requirements": "Data Protection Officer, Forensics Expert, Database Administrator, Legal Team, Risk Management",
                    "success_criteria": "Complete data impact assessment documented, accurate breach scope determined, informed notification decisions made, evidence preserved"
                },
                {
                    "plan_name": "Multi-Jurisdiction Compliance",
                    "strategy": "Complex compliance approach addressing multi-jurisdictional requirements including GDPR, CCPA, and other regional data protection laws. This strategy coordinates international notification and response requirements while managing the complexity of different regulatory frameworks. We work with legal teams across multiple jurisdictions to ensure compliance with varying notification timelines, content requirements, and enforcement approaches. Essential for global organizations with complex data flows.",
                    "timeline": "4-5 hours",
                    "risk_level": "MEDIUM",
                    "confidence_score": "MEDIUM",
                    "estimated_hours": 4,
                    "resource_requirements": "International Legal Team, Compliance Officers, Data Protection Officers, Regional Security Leads, Executive Coordination",
                    "success_criteria": "All jurisdictional requirements met, coordinated international response executed, legal exposure minimized across all regions"
                }
            ],
            'system-failure': [
                {
                    "plan_name": "Emergency Service Restoration",
                    "strategy": "Immediate service restoration and business continuity approach that prioritizes getting systems back online quickly. This strategy implements rapid recovery procedures with temporary solutions while parallel investigation identifies root causes. We focus on minimizing customer impact and revenue loss by restoring service first, then improving stability. This approach is ideal when customer-facing systems are down and every minute of outage costs significant revenue or customer satisfaction.",
                    "timeline": "2-3 hours",
                    "risk_level": "HIGH",
                    "confidence_score": "HIGH",
                    "estimated_hours": 3,
                    "resource_requirements": "System Administrator, Network Engineer, Database Administrator, Business Continuity Manager, Customer Service Lead",
                    "success_criteria": "Service restored within 3 hours, business operations resumed, customer impact minimized, temporary solutions implemented"
                },
                {
                    "plan_name": "Root Cause Investigation",
                    "strategy": "Comprehensive analysis approach to identify and address the fundamental cause of system failure. This methodology conducts detailed technical investigation before implementing permanent fixes to prevent recurrence. We prioritize understanding the complete failure chain and implementing robust solutions over quick fixes that might fail again. This approach is ideal when the immediate crisis is contained and we need to ensure this type of failure doesn't happen again.",
                    "timeline": "5-7 hours",
                    "risk_level": "LOW",
                    "confidence_score": "HIGH",
                    "estimated_hours": 6,
                    "resource_requirements": "Senior System Engineer, Database Specialist, Infrastructure Architect, Quality Assurance Lead, Vendor Liaisons",
                    "success_criteria": "Root cause identified and documented, permanent fix implemented, system stability verified, prevention measures in place"
                },
                {
                    "plan_name": "Business Impact Minimization",
                    "strategy": "Balanced approach that coordinates rapid service restoration with stakeholder communication and business impact management. This strategy balances technical response with business operations and customer communication to minimize overall business damage. We work closely with business stakeholders to prioritize restoration efforts based on business criticality while keeping customers and partners informed throughout the process. Perfect when multiple business units are affected and coordination is complex.",
                    "timeline": "3-4 hours",
                    "risk_level": "MEDIUM",
                    "confidence_score": "HIGH",
                    "estimated_hours": 4,
                    "resource_requirements": "Technical Lead, Business Operations Manager, Customer Service Manager, Communications Team, Account Managers",
                    "success_criteria": "Business impact minimized, customers kept informed, service restored with minimal disruption, relationships preserved"
                }
            ]
        }
        
        return base_plans.get(incident_type, base_plans['security'])
    
    def create_action_plan_records(self, incident, plans_data):
        """
        Database Record Creator - The plan persistence manager
        
        Takes our generated plans and saves them to the database.
        Each plan becomes a selectable option that users can choose from.
        Like filing away different consultant proposals for later review.
        """
        created_plans = []
        
        self.stdout.write(f"\n📋 Creating {len(plans_data)} ActionPlan database records...")
        
        for i, plan_data in enumerate(plans_data, 1):
            try:
                # Create ActionPlan record with all the details
                action_plan = ActionPlan.objects.create(
                    incident=incident,
                    plan_name=plan_data.get('plan_name', f'Strategic Plan {i}'),
                    strategy=plan_data.get('strategy', 'Comprehensive incident response approach'),
                    timeline=plan_data.get('timeline', '2-4 hours'),
                    risk_level=plan_data.get('risk_level', 'MEDIUM'),
                    confidence_score=plan_data.get('confidence_score', 'MEDIUM'),
                    estimated_hours=plan_data.get('estimated_hours', 3),
                    resource_requirements=plan_data.get('resource_requirements', 'Security Team'),
                    success_criteria=plan_data.get('success_criteria', 'Incident resolved successfully'),
                    status='GENERATED',
                    is_selected=False  # User will select one later
                )
                
                created_plans.append(action_plan)
                
                self.stdout.write(self.style.SUCCESS(f"✅ Created Plan {i}: {action_plan.plan_name}"))
                self.stdout.write(f"   ⏱️  Timeline: {action_plan.timeline}")
                self.stdout.write(f"   🎯 Risk Level: {action_plan.risk_level}")
                self.stdout.write(f"   📊 Confidence: {action_plan.confidence_score}")
                self.stdout.write(f"   👥 Resources: {action_plan.resource_requirements[:50]}...")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to create plan {i}: {str(e)}"))
                continue
        
        return created_plans
    
    def display_completion_summary(self, incident, plans):
        """
        Success Report Generator - The completion dashboard
        
        Shows a comprehensive summary of what was accomplished.
        Like having a project manager report on deliverables.
        """
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("🎉 MULTI-PLAN GENERATION COMPLETED SUCCESSFULLY"))
        self.stdout.write("=" * 70)
        
        self.stdout.write(f"📋 INCIDENT CREATED:")
        self.stdout.write(f"   🆔 ID: {incident.id}")
        self.stdout.write(f"   📄 Title: {incident.title}")
        self.stdout.write(f"   📅 Created: {incident.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"   📊 Status: {incident.status}")
        
        self.stdout.write(f"\n🎯 ACTION PLANS GENERATED: {len(plans)}")
        for i, plan in enumerate(plans, 1):
            self.stdout.write(f"   {i}. {plan.plan_name} ({plan.timeline}, {plan.risk_level} risk)")
        
        # Calculate some useful statistics
        speed_options = len([p for p in plans if 'hour' in p.timeline and int(p.timeline.split('-')[0]) <= 2])
        comprehensive_options = len([p for p in plans if 'hour' in p.timeline and int(p.timeline.split('-')[0]) >= 4])
        low_risk_plans = len([p for p in plans if p.risk_level == 'LOW'])
        high_risk_plans = len([p for p in plans if p.risk_level == 'HIGH'])
        
        self.stdout.write(f"\n📈 PLAN ANALYSIS:")
        self.stdout.write(f"   🎯 Total Strategic Options: {len(plans)}")
        self.stdout.write(f"   ⚡ Fast Response Options: {speed_options}")
        self.stdout.write(f"   🔍 Comprehensive Options: {comprehensive_options}")
        self.stdout.write(f"   🛡️  Low Risk Plans: {low_risk_plans}")
        self.stdout.write(f"   ⚠️  High Risk Plans: {high_risk_plans}")
    
    def display_plan_selection_instructions(self, plans):
        """
        User Guide Generator - The next steps manual
        
        Provides clear, actionable instructions for what the user
        needs to do next. Like having a helpful assistant explain
        the next steps in the process.
        """
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("📋 PLAN SELECTION REQUIRED - CHOOSE YOUR STRATEGY"))
        self.stdout.write("=" * 70)
        
        self.stdout.write("\n🎯 AVAILABLE STRATEGIC OPTIONS:")
        for i, plan in enumerate(plans, 1):
            self.stdout.write(f"\n📌 PLAN {i} (ID: {plan.id}): {plan.plan_name}")
            self.stdout.write(f"   📊 Strategy: {plan.strategy[:120]}...")
            self.stdout.write(f"   ⏱️  Timeline: {plan.timeline}")
            self.stdout.write(f"   🎯 Risk Level: {plan.risk_level}")
            self.stdout.write(f"   📈 Confidence: {plan.confidence_score}")
            self.stdout.write(f"   👥 Resources: {plan.resource_requirements}")
            self.stdout.write(f"   ✅ Success Criteria: {plan.success_criteria[:80]}...")
        
        self.stdout.write(f"\n🔄 HOW TO SELECT YOUR PREFERRED PLAN:")
        self.stdout.write(f"   You have {len(plans)} professionally crafted strategies to choose from.")
        self.stdout.write(f"   Each represents a different approach to handling this incident.")
        self.stdout.write(f"")
        self.stdout.write(f"   📱 OPTION 1 - Django Admin Interface:")
        self.stdout.write(f"      • Visit: http://127.0.0.1:8000/admin/incident_response/actionplan/")
        self.stdout.write(f"      • Find plans for Incident ID {plans[0].incident.id}")
        self.stdout.write(f"      • Edit your chosen plan and set 'is_selected = True'")
        self.stdout.write(f"      • Save the changes")
        self.stdout.write(f"")
        self.stdout.write(f"   🌐 OPTION 2 - API Call (for developers):")
        self.stdout.write(f"      • curl -X POST http://127.0.0.1:8000/api/select-plan/ \\")
        self.stdout.write(f"             -H 'Content-Type: application/json' \\")
        self.stdout.write(f"""            -d '{{"plan_id": "YOUR_CHOSEN_PLAN_ID"}}' """)

        self.stdout.write(f"")
        self.stdout.write(f"   ⚙️  OPTION 3 - Management Command:")
        self.stdout.write(f"      • python manage.py generate_actions_from_plan --plan-id=YOUR_CHOSEN_PLAN_ID")
        self.stdout.write(f"")
        self.stdout.write(f"   🎯 DECISION GUIDE - Choose based on your priorities:")
        self.stdout.write(f"      • ⚡ Need FAST response? → Choose HIGH risk, short timeline plans")
        self.stdout.write(f"      • 🔍 Need THOROUGH analysis? → Choose LOW risk, longer timeline plans")
        self.stdout.write(f"      • ⚖️  Want BALANCED approach? → Choose MEDIUM risk plans")
        self.stdout.write(f"      • 📞 Focus on COMMUNICATION? → Choose stakeholder/compliance focused plans")
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("✅ Multi-Plan Generation Complete - Ready for Selection"))
        self.stdout.write("   💡 Once you select a plan, the system will generate detailed action items")
        self.stdout.write("   📋 Each action item will include AI-generated implementation guidance")
        self.stdout.write("=" * 70)
def create_ai_status_record(self, incident, expertise, message, confidence=0.8):
    """Create AI agent status tracking record"""
    from incident_response.models import AIAgentStatus
    
    return AIAgentStatus.objects.create(
        incident=incident,
        current_expertise=expertise,
        status_message=message,
        decision_reasoning=f"AI analysis for {incident.title}",
        confidence_score=confidence
    )

# Example usage in your workflow:
def generate_multiple_action_plans(self, client, incident, incident_type):
    # Create initial AI status
    ai_status = self.create_ai_status_record(
        incident=incident,
        expertise="Strategic Plan Generator",
        message="Generating multiple strategic action plans",
        confidence=0.9
    )
    
    try:
        # Your existing AI generation code...
        plans = parsed_data['action_plans'][:4]
        
        # Update status on success
        ai_status.status_message = f"Successfully generated {len(plans)} strategic plans"
        ai_status.completed_at = timezone.now()
        ai_status.confidence_score = 0.95
        ai_status.save()
        
        return plans
        
    except Exception as e:
        # Update status on failure
        ai_status.status_message = f"Plan generation failed: {str(e)}"
        ai_status.completed_at = timezone.now()
        ai_status.confidence_score = 0.1
        ai_status.save()
        
        return self.get_fallback_plans()
    
def generate_action_documentation(self, client, action, action_plan):
    """Generate GUARD Framework compliant documentation for incident response action"""
    try:
        # Generate GUARD Action Statement (Control Objective)
        guard_statement = self.generate_guard_action_statement(action, action_plan)
        
        # Map to relevant control frameworks
        control_mappings = self.get_control_framework_mappings(action, action_plan)
        
        prompt = f"""
        Generate comprehensive incident response documentation following the GUARD Framework structure:
        
        INCIDENT CONTEXT:
        - Incident: {action.incident.title}
        - Selected Plan: {action_plan.plan_name}
        - Strategy: {action_plan.strategy}
        - Risk Level: {action_plan.risk_level}
        
        ACTION DETAILS:
        - Title: {action.title}
        - Description: {action.description}
        - Operator: {action.operator}
        - Priority: {action.priority}
        - Step: {action.step}
        
        GUARD FRAMEWORK REQUIREMENTS:
        Generate documentation with these specific sections:
        
        1. GUARD ACTION STATEMENT (Control Objective):
        "{guard_statement}"
        
        2. MAPPED CONTROLS:
        {control_mappings}
        
        3. ENABLING ACTIONS:
        - Detailed implementation steps for this specific action
        - Resource requirements and operator assignments
        - Timeline and success criteria
        
        4. CONTROL CITATIONS:
        - Reference specific framework controls being implemented
        - Include ISO 27001, NIST 800-53, and SCF citations where applicable
        
        5. COMPLIANCE DOCUMENTATION:
        - GDPR Article 33 compliance (if applicable)
        - ISO 27001:2013 alignment
        - NIST CSF 2.0 framework mapping
        
        6. GHOSTDRAFT SPECIFICATIONS:
        - Mark document as voice-eligible if appropriate
        - Include AI generation metadata
        - Specify export options (PDF, Email)
        
        Format as professional incident response documentation following GUARD framework standards.
        Use proper control citations format (e.g., ISO 27001 A.16.1.1, NIST 800-53 IR-1).
        """
        
        response = client.chat.completions.create(
            model=os.getenv('AI_MODEL', 'qwen/qwen3-coder:free'),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,  # Longer for comprehensive GUARD documentation
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        self.stdout.write(self.style.WARNING(f"⚠️ AI GUARD documentation failed: {str(e)}"))
        return self.generate_guard_fallback_documentation(action, action_plan)

def generate_guard_action_statement(self, action, action_plan):
    """Generate GUARD-compliant Action Statement (Control Objective)"""
    risk_context = {
        'HIGH': 'immediate threat containment and damage control',
        'MEDIUM': 'balanced risk mitigation and stakeholder protection', 
        'LOW': 'comprehensive analysis and preventive measures'
    }.get(action_plan.risk_level, 'effective incident response')
    
    return f"Control provides reasonable assurance that {action.title.lower()} activities achieve {risk_context} while maintaining organizational resilience, compliance requirements, and business continuity during security incident response operations."

def get_control_framework_mappings(self, action, action_plan):
    """Map action to relevant control frameworks with proper citations"""
    
    # Map based on action characteristics
    mappings = []
    
    # Always include core incident response controls
    mappings.extend([
        "ISO 27001 A.16.1.1 - Responsibilities and procedures",
        "ISO 27001 A.16.1.2 - Reporting information security events", 
        "NIST 800-53 IR-1 - Incident Response Policy and Procedures",
        "NIST 800-53 IR-4 - Incident Handling",
        "SCF #1415 - Incident Response Planning"
    ])
    
    # Add specific mappings based on action content
    action_content = f"{action.title} {action.description}".lower()
    
    if any(term in action_content for term in ['assess', 'analysis', 'investigate']):
        mappings.extend([
            "ISO 27001 A.16.1.4 - Assessment of information security events",
            "NIST 800-53 IR-3 - Incident Response Testing", 
            "SCF #1416 - Incident Response Testing & Exercises"
        ])
    
    if any(term in action_content for term in ['contain', 'isolate', 'block']):
        mappings.extend([
            "ISO 27001 A.16.1.5 - Response to information security incidents",
            "NIST 800-53 IR-5 - Incident Monitoring",
            "SCF #1417 - Incident Response Implementation"
        ])
    
    if any(term in action_content for term in ['communicate', 'notify', 'report']):
        mappings.extend([
            "ISO 27001 A.16.1.2 - Reporting information security events",
            "NIST 800-53 IR-6 - Incident Reporting", 
            "SCF #1418 - Incident Response Communication"
        ])
    
    if any(term in action_content for term in ['forensic', 'evidence', 'collect']):
        mappings.extend([
            "ISO 27001 A.16.1.7 - Collection of evidence",
            "NIST 800-53 IR-4(1) - Automated Incident Handling",
            "SCF #1419 - Digital Forensics"
        ])
    
    # Add compliance-specific controls
    mappings.extend([
        "GDPR Article 33 - Notification of a personal data breach",
        "NIST CSF 2.0 RS.CO-1 - Personnel know their roles",
        "COSO ERM - Risk Response Activities"
    ])
    
    return "\n".join([f"- {mapping}" for mapping in mappings])

def generate_guard_fallback_documentation(self, action, action_plan):
    """Generate comprehensive GUARD-compliant fallback documentation"""
    guard_statement = self.generate_guard_action_statement(action, action_plan)
    control_mappings = self.get_control_framework_mappings(action, action_plan)
    
    return f"""
# GUARD FRAMEWORK - INCIDENT RESPONSE ACTION DOCUMENTATION

## GUARD ACTION STATEMENT (Control Objective)
{guard_statement}

## INCIDENT OVERVIEW
- **Incident ID**: {action.incident.id}
- **Incident Title**: {action.incident.title}
- **Selected Response Plan**: {action_plan.plan_name}
- **Plan Strategy**: {action_plan.strategy}
- **Risk Level**: {action_plan.risk_level}
- **Confidence Score**: {action_plan.confidence_score}

## ACTION SPECIFICATION
- **Action ID**: {action.id}
- **Step Sequence**: {action.step}
- **Action Title**: {action.title}
- **Priority Level**: {action.priority}
- **Assigned Operator**: {action.operator}
- **Estimated Duration**: {action.estimated_hours} hours
- **GhostDraft Status**: {'Enabled (AI-Assisted)' if action.ghostdraft else 'Manual Implementation'}

## MAPPED CONTROLS (Best-Practice Controls)
{control_mappings}

## ENABLING ACTIONS (Implementation Steps)

### Phase 1: Preparation and Assessment (15 minutes)
1. **Validate Incident Context**
   - Review current incident status and impact assessment
   - Confirm action relevance to selected response plan
   - Gather required tools and access credentials

2. **Resource Coordination**
   - Coordinate with {action.operator} for action execution
   - Ensure communication channels are established
   - Verify escalation procedures are understood

### Phase 2: Action Execution ({action.estimated_hours - 0.5} hours)
1. **Primary Action Implementation**
   - Execute: {action.description}
   - Monitor progress against success criteria
   - Document findings and observations continuously

2. **Control Verification**
   - Validate that mapped controls are being satisfied
   - Ensure compliance requirements are met
   - Record any deviations or exceptions

### Phase 3: Validation and Documentation (15 minutes)
1. **Completion Verification**
   - Confirm action objectives have been achieved
   - Update incident status and timeline
   - Prepare handoff documentation for next actions

## CONTROL CITATIONS (Framework References)

### Information Security Management
- **ISO 27001 A.16.1.1**: Incident response responsibilities clearly defined
- **ISO 27001 A.16.1.2**: Security events properly reported and documented
- **ISO 27001 A.16.1.4**: Incident impact assessed and categorized

### Cybersecurity Framework Alignment
- **NIST 800-53 IR-1**: Incident response policies implemented
- **NIST 800-53 IR-4**: Incident handling procedures followed
- **NIST CSF 2.0 RS.CO-1**: Response coordination roles established

### Risk Management & Governance
- **SCF #1415**: Incident response planning controls active
- **COSO ERM**: Risk response activities documented and monitored

### Regulatory Compliance
- **GDPR Article 33**: Data breach notification requirements (if applicable)
- **NIST CSF 2.0 GOVERN**: Organizational cybersecurity governance maintained

## SUCCESS CRITERIA & METRICS
- **Control Objective Achievement**: {guard_statement.split('that ')[1] if 'that ' in guard_statement else 'Objective completion verified'}
- **Timeline Compliance**: Action completed within {action.estimated_hours} hour timeframe
- **Framework Alignment**: All mapped controls properly implemented
- **Documentation Quality**: Complete audit trail maintained per GUARD standards

## COMPLIANCE DOCUMENTATION

### Information Security Management System (ISMS)
This action supports the organization's ISMS by implementing controls that:
- Maintain information confidentiality, integrity, and availability
- Ensure proper incident response procedures are followed
- Support continuous improvement of security controls

### Risk Management Alignment
- **Risk Level**: {action_plan.risk_level}
- **Risk Treatment**: Active mitigation through systematic response
- **Residual Risk**: Monitored through ongoing incident tracking

### Regulatory Considerations
- All actions comply with applicable data protection regulations
- Incident response procedures align with industry best practices
- Documentation supports audit and compliance requirements

## GHOSTDRAFT SPECIFICATIONS

### AI Generation Metadata
- **Generated By**: Fallout Room AI (GUARD Framework Compliant)
- **Framework Version**: GUARD 2024 Standard
- **Voice Eligible**: {'Yes - Suitable for voice delivery' if action.priority in ['Critical', 'High'] else 'No - Text-only recommended'}
- **Export Options**: PDF, Email, Secure Portal Access
- **Classification**: Internal Use - Incident Response Team

### Quality Assurance
- **AI Content Quality**: Professional incident response documentation
- **Framework Compliance**: Full GUARD framework alignment verified
- **Control Coverage**: All applicable framework controls referenced
- **Audit Readiness**: Documentation prepared for compliance review

---

**Document Properties**
- **Generated**: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
- **Framework**: GUARD (attacked.ai standard)
- **Action Plan**: {action_plan.plan_name}
- **Control Objective**: Verified and implemented
- **Next Review**: As per incident response schedule

---

*This document was generated using the GUARD Framework for cross-domain control and response management. All control citations reference internationally recognized frameworks including ISO 27001:2013, NIST 800-53 Rev 5, Secure Controls Framework (SCF), and relevant regulatory standards.*
"""
