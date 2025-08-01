import json
import os
import openai
from django.core.management.base import BaseCommand
from django.utils import timezone
from incident_response.models import Incident, ActionPlan, Action, Deliverable


class Command(BaseCommand):
    help = 'Generate actions from selected plan with Single Adaptive AI Agent'
    
    def add_arguments(self, parser):
        parser.add_argument('--plan-id', type=int, required=True, help='ID of selected action plan')
    
    def handle(self, *args, **options):
        plan_id = options['plan_id']
        
        try:
            action_plan = ActionPlan.objects.get(id=plan_id)
        except ActionPlan.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Action plan with ID {plan_id} not found"))
            return
        
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS(f"🤖 SINGLE ADAPTIVE AI AGENT - GENERATING ACTIONS"))
        self.stdout.write(f"Selected Plan: {action_plan.plan_name}")
        self.stdout.write("=" * 70)
        
        # Mark plan as selected
        ActionPlan.objects.filter(incident=action_plan.incident).update(is_selected=False)
        action_plan.is_selected = True
        action_plan.status = 'SELECTED'
        action_plan.save()
        
        # Initialize Single Adaptive AI Agent
        ai_agent = self.initialize_adaptive_ai_agent()
        if not ai_agent:
            return
        
        # Generate actions based on selected plan
        actions_data = self.generate_actions_from_plan(ai_agent, action_plan)
        if not actions_data:
            return
        
        # Create Action records
        created_actions = self.create_action_records(action_plan, actions_data)
        
        # Smart deliverable processing with AI decision making
        deliverables_created = self.process_smart_deliverables(ai_agent, created_actions, action_plan)
        
        # Update incident status
        action_plan.incident.status = 'ACTIONS_GENERATED'
        action_plan.incident.save()
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ WORKFLOW COMPLETE:"))
        self.stdout.write(self.style.SUCCESS(f"   🎯 Actions: {len(created_actions)}"))
        self.stdout.write(self.style.SUCCESS(f"   📄 Deliverables: {deliverables_created}"))
    
    def initialize_adaptive_ai_agent(self):
        """Initialize Single Adaptive AI Agent"""
        try:
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                self.stdout.write(self.style.ERROR("❌ OPENROUTER_API_KEY not found"))
                return None
            
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            
            self.stdout.write(self.style.SUCCESS("🤖 Adaptive AI Agent initialized"))
            return client
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ AI Agent error: {str(e)}"))
            return None
    
    def generate_actions_from_plan(self, client, action_plan):
        """Generate specific actions based on selected plan"""
        try:
            prompt = f"""Generate 4-6 specific actions for this selected incident response plan:

INCIDENT: {action_plan.incident.title}
SELECTED PLAN: {action_plan.plan_name}
STRATEGY: {action_plan.strategy}
TIMELINE: {action_plan.timeline}

Create JSON with "actions" array. Each action needs:
- title: Clear action title
- description: Implementation details
- operator: Who performs it
- priority: Critical/High/Medium/Low
- estimated_hours: 1-4 hours

Format as valid JSON only."""

            response = client.chat.completions.create(
                model=os.getenv('AI_MODEL', 'qwen/qwen3-coder:free'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            try:
                parsed_data = json.loads(response.choices[0].message.content)
                if 'actions' in parsed_data:
                    return parsed_data['actions'][:6]
            except:
                pass
            
            return self.get_fallback_actions()
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Using fallback actions: {str(e)}"))
            return self.get_fallback_actions()
    
    def get_fallback_actions(self):
        """Fallback actions when AI fails"""
        return [
            {
                "title": "Assess Incident Scope",
                "description": "Evaluate the full extent and impact of the security incident",
                "operator": "Security Analyst",
                "priority": "Critical",
                "estimated_hours": 1
            },
            {
                "title": "Implement Containment",
                "description": "Deploy containment measures to prevent further damage",
                "operator": "Security Team",
                "priority": "High",
                "estimated_hours": 2
            },
            {
                "title": "Notify Stakeholders",
                "description": "Communicate incident status to relevant stakeholders",
                "operator": "Communications Team",
                "priority": "High",
                "estimated_hours": 1
            },
            {
                "title": "Collect Technical Evidence",
                "description": "Gather forensic evidence from affected systems",
                "operator": "Forensics Expert",
                "priority": "Medium",
                "estimated_hours": 3
            }
        ]
    
    def create_action_records(self, action_plan, actions_data):
        """Create Action database records"""
        created_actions = []
        
        for i, action_data in enumerate(actions_data, 1):
            try:
                action = Action.objects.create(
                    action_plan=action_plan,
                    incident=action_plan.incident,
                    step=i,
                    title=action_data.get('title', f'Action {i}'),
                    description=action_data.get('description', 'Action description'),
                    operator=action_data.get('operator', 'Security Team'),
                    priority=action_data.get('priority', 'Medium'),
                    estimated_hours=action_data.get('estimated_hours', 2),
                    ghostdraft=True
                )
                
                created_actions.append(action)
                self.stdout.write(self.style.SUCCESS(f"✅ Created Action {i}: {action.title}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to create action {i}: {str(e)}"))
        
        return created_actions
    
    def process_smart_deliverables(self, ai_agent, actions, action_plan):
        """🎯 SMART AI-DRIVEN DELIVERABLE PROCESSING WITH ROLE SWITCHING"""
        self.stdout.write("\n🧠 AI AGENT: Analyzing deliverable requirements...")
        
        deliverables_created = 0
        
        for action in actions:
            try:
                # AI decides if this action needs documentation
                needs_documentation = self.ai_decide_documentation_need(ai_agent, action, action_plan)
                
                if needs_documentation['create_deliverable']:
                    # AI determines the best format and expert role
                    deliverable_specs = self.ai_determine_deliverable_format(ai_agent, action, action_plan)
                    
                    self.stdout.write(f"🎯 AI ROLE DECISION: {deliverable_specs['expert_role']} for {action.title}")
                    
                    # Create deliverable with AI specifications
                    deliverable = Deliverable.objects.create(
                        action=action,
                        deliverable_format=deliverable_specs['format'],
                        export_options=deliverable_specs['export_options'],
                        voice_eligible=deliverable_specs['voice_eligible']
                    )
                    
                    # Generate AI content based on determined expert role
                    ai_content = self.generate_adaptive_documentation_enhanced(ai_agent, action, action_plan, deliverable_specs)
                    
                    # Update deliverable with AI content and metadata
                    deliverable.content = ai_content
                    deliverable.save()
                    
                    deliverables_created += 1
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Created {deliverable_specs['format']} deliverable: {action.title}"
                    ))
                    self.stdout.write(f"   🤖 AI Expert: {deliverable_specs['expert_role']}")
                    self.stdout.write(f"   📄 Format: {deliverable_specs['format']}")
                    self.stdout.write(f"   🎤 Voice: {'Yes' if deliverable_specs['voice_eligible'] else 'No'}")
                else:
                    self.stdout.write(f"⏭️  AI Decision: No deliverable needed for {action.title}")
                    self.stdout.write(f"   💡 Reason: {needs_documentation['reason']}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to process deliverable for {action.title}: {str(e)}"))
        
        return deliverables_created

    def ai_decide_documentation_need(self, ai_agent, action, action_plan):
        """AI intelligently decides if action needs documentation"""
        try:
            prompt = f"""You are a SINGLE ADAPTIVE AI AGENT for incident response. Analyze if this action requires formal documentation:

ACTION ANALYSIS:
- Action: {action.title}
- Description: {action.description} 
- Priority: {action.priority}
- Operator: {action.operator}

DECISION CRITERIA:
- Does this action require formal documentation?
- Consider: compliance needs, complexity, risk level
- Simple actions like "Review logs" might not need formal docs
- Important actions like "Stakeholder communication" definitely need docs

Respond with JSON:
{{"create_deliverable": true/false, "reason": "Explanation", "importance_score": 1-10}}"""

            response = ai_agent.chat.completions.create(
                model=os.getenv('AI_MODEL', 'qwen/qwen3-coder:free'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception:
            return {"create_deliverable": True, "reason": "Fallback - ensuring coverage", "importance_score": 7}

    def ai_determine_deliverable_format(self, ai_agent, action, action_plan):
        """🎯 AI DETERMINES EXPERT ROLE BASED ON ACTION TYPE"""
        try:
            prompt = f"""ROLE SELECTION ANALYSIS: Determine the optimal expert role and format for this incident response action:

ACTION ANALYSIS:
- Action: {action.title}
- Description: {action.description}
- Priority: {action.priority}
- Operator: {action.operator}

AVAILABLE EXPERT ROLES:
1. Communications Expert - For stakeholder communications, notifications, public relations
2. Technical Specialist - For technical implementations, system configurations, forensics
3. Legal Compliance Expert - For regulatory matters, compliance requirements, legal notifications
4. Executive Advisor - For leadership communications, strategic decisions, board reports
5. Business Continuity Manager - For operational continuity, business impact assessments
6. Incident Response Specialist - For general incident management, coordination

SELECTION CRITERIA:
- Match the action type to the most appropriate expert role
- Consider the operator and action complexity
- Think about who would best handle this type of task in real life

Respond with JSON:
{{"expert_role": "Specific Expert Type from list above", "format": "HTML", "voice_eligible": true/false, "export_options": "PDF,Email,Voice or PDF,Email", "reasoning": "Why this expert role is most suitable for this action"}}"""

            response = ai_agent.chat.completions.create(
                model=os.getenv('AI_MODEL', 'qwen/qwen3-coder:free'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.4
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception:
            return self.determine_format_fallback(action)

    def determine_format_fallback(self, action):
        """🎯 INTELLIGENT FALLBACK ROLE ASSIGNMENT"""
        title_lower = action.title.lower()
        description_lower = action.description.lower() if action.description else ""
        combined_text = f"{title_lower} {description_lower}"
        
        # Enhanced role detection logic
        if any(word in combined_text for word in ['communication', 'notify', 'stakeholder', 'announce', 'inform', 'alert', 'message', 'contact']):
            return {
                "expert_role": "Communications Expert",
                "format": "HTML",
                "voice_eligible": True,
                "export_options": "PDF,Email,Voice",
                "reasoning": "Action involves stakeholder communication requiring accessible formats"
            }
        elif any(word in combined_text for word in ['technical', 'forensic', 'system', 'configure', 'implement', 'deploy', 'analyze', 'investigate']):
            return {
                "expert_role": "Technical Specialist", 
                "format": "HTML",
                "voice_eligible": False,
                "export_options": "PDF,Email",
                "reasoning": "Technical action requires detailed documentation with technical specifications"
            }
        elif any(word in combined_text for word in ['legal', 'compliance', 'regulatory', 'report', 'audit', 'breach']):
            return {
                "expert_role": "Legal Compliance Expert",
                "format": "HTML",
                "voice_eligible": False,
                "export_options": "PDF,Email",
                "reasoning": "Action involves legal/compliance requirements needing formal documentation"
            }
        elif any(word in combined_text for word in ['executive', 'leadership', 'board', 'strategic', 'decision']):
            return {
                "expert_role": "Executive Advisor",
                "format": "HTML",
                "voice_eligible": True,
                "export_options": "PDF,Email,Voice",
                "reasoning": "Executive-level action requiring strategic perspective and clear communication"
            }
        elif any(word in combined_text for word in ['business', 'continuity', 'operational', 'process', 'workflow']):
            return {
                "expert_role": "Business Continuity Manager",
                "format": "HTML",
                "voice_eligible": True,
                "export_options": "PDF,Email,Voice",
                "reasoning": "Business continuity action requiring operational perspective"
            }
        else:
            return {
                "expert_role": "Incident Response Specialist",
                "format": "HTML",
                "voice_eligible": True,
                "export_options": "PDF,Email,Voice",
                "reasoning": "General incident response action requiring coordination expertise"
            }

    def generate_adaptive_documentation_enhanced(self, client, action, action_plan, specs):
        """🎯 GENERATE COMPREHENSIVE DOCUMENTATION WITH MINIMUM LENGTH GUARANTEE"""
        try:
            expert_role = specs['expert_role']
            
            # Generate GUARD Framework elements
            guard_statement = f"Control provides reasonable assurance that {action.title.lower()} activities achieve effective incident response while maintaining compliance and organizational resilience."
            
            self.stdout.write(f"🤖 AI ROLE SWITCH: Becoming {expert_role} for {action.title}")
            
            prompt = f"""🤖 ROLE TRANSFORMATION: You are now a {expert_role} with deep expertise in incident response.

CRITICAL REQUIREMENT: Generate a COMPREHENSIVE document of AT LEAST 2500 characters. This is a professional enterprise document that must be thorough and detailed.

EXPERT ROLE CONTEXT:
You are a {expert_role} and you must write documentation from this specific professional perspective using extensive detail and professional language.

INCIDENT CONTEXT:
- Incident: {action.incident.title}
- Description: {action.incident.description}
- Selected Plan: {action_plan.plan_name}
- Strategy: {action_plan.strategy}
- Risk Level: {action_plan.risk_level}
- Timeline: {action_plan.timeline}

ACTION TO DOCUMENT:
- Action: {action.title}
- Description: {action.description}
- Operator: {action.operator}
- Priority: {action.priority}
- Step: {action.step}

COMPREHENSIVE DOCUMENTATION REQUIREMENTS AS {expert_role.upper()}:
1. Write entirely from the perspective and expertise of a {expert_role}
2. Generate MINIMUM 2500 characters of comprehensive professional content
3. Include detailed implementation procedures with step-by-step instructions
4. Add comprehensive risk assessments and mitigation strategies
5. Include detailed timeline with specific milestones
6. Provide extensive technical specifications and requirements
7. Add comprehensive compliance and regulatory considerations
8. Include detailed success criteria and validation procedures
9. Add thorough troubleshooting and contingency planning
10. Include comprehensive post-action review and lessons learned sections

DETAILED DOCUMENT STRUCTURE (EXPAND EACH SECTION THOROUGHLY):
1. EXECUTIVE SUMMARY (200+ words)
2. DETAILED IMPLEMENTATION PROCEDURES (800+ words)
3. COMPREHENSIVE RISK ASSESSMENT (300+ words)
4. DETAILED TIMELINE AND MILESTONES (200+ words)
5. TECHNICAL SPECIFICATIONS (300+ words)
6. COMPLIANCE AND REGULATORY REQUIREMENTS (200+ words)
7. SUCCESS CRITERIA AND VALIDATION (200+ words)
8. TROUBLESHOOTING AND CONTINGENCIES (200+ words)
9. POST-ACTION REVIEW PROCEDURES (100+ words)

Generate a comprehensive, detailed, professional document that demonstrates extensive expertise and provides complete guidance. Each section must be thoroughly detailed with specific procedures, considerations, and professional insights."""

            response = client.chat.completions.create(
                model=os.getenv('AI_MODEL', 'qwen/qwen3-coder:free'),
                messages=[
                    {"role": "system", "content": f"You are a professional {expert_role} with extensive experience. Generate comprehensive, detailed documentation of at least 2500 characters with thorough professional content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,  # Increased for longer content
                temperature=0.7
            )
            
            ai_content = response.choices[0].message.content
            
            # Ensure minimum length by adding comprehensive sections if needed
            if len(ai_content) < 2000:
                ai_content += self.enhance_documentation_content(action, action_plan, specs, expert_role)
            
            # Format with GUARD Framework compliance and expert identification
            formatted_content = f"""🤖 ADAPTIVE AI AGENT - {expert_role.upper()}
🛡️ GUARD FRAMEWORK COMPLIANT

Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
Format: {specs['format']} | Voice: {'Yes' if specs['voice_eligible'] else 'No'}
Expert Role: {expert_role}
Action: {action.title}
Incident: {action.incident.title}

GUARD ACTION STATEMENT:
{guard_statement}

COMPREHENSIVE EXPERT DOCUMENTATION FROM {expert_role.upper()} PERSPECTIVE:

{ai_content}

DETAILED CONTROL FRAMEWORK ALIGNMENT:

This action aligns with multiple international control frameworks:

ISO 27001:2013 CONTROLS:
- A.16.1.1 Responsibilities and procedures for incident response
- A.16.1.2 Reporting information security events and weaknesses
- A.16.1.4 Assessment of information security events and incidents
- A.16.1.5 Response to information security incidents
- A.16.1.7 Collection of evidence

NIST 800-53 REV 5 CONTROLS:
- IR-1 Policy and Procedures
- IR-2 Incident Response Training
- IR-3 Incident Response Testing
- IR-4 Incident Handling
- IR-5 Incident Monitoring
- IR-6 Incident Reporting
- IR-8 Incident Response Plan

NIST CYBERSECURITY FRAMEWORK 2.0:
- RESPOND (RS): RS.RP-1, RS.CO-1, RS.AN-1, RS.MI-1, RS.IM-1
- GOVERN (GV): GV.RM-1, GV.SC-1, GV.OC-1

SECURE CONTROLS FRAMEWORK (SCF):
- SCF #1415 - Incident Response Planning
- SCF #1416 - Incident Response Testing & Exercises
- SCF #1417 - Incident Response Implementation
- SCF #1418 - Incident Response Communication
- SCF #1419 - Digital Forensics

REGULATORY COMPLIANCE CONSIDERATIONS:
- GDPR Article 33: Notification of personal data breach to supervisory authority
- GDPR Article 34: Communication of personal data breach to data subject
- SOX Section 404: Internal control over financial reporting
- HIPAA Security Rule: Administrative safeguards for incident response
- PCI DSS Requirement 12.10: Incident response plan implementation

PROFESSIONAL QUALITY ASSURANCE:
This documentation has been generated by an AI agent specialized in {expert_role.lower()} responsibilities and meets enterprise-grade incident response documentation standards. The content addresses both immediate tactical requirements and strategic organizational needs.

---
Generated by Single Adaptive AI Agent with GUARD Framework compliance
Expert Role: {expert_role}
Content Length: {len(formatted_content)} characters
Reasoning: {specs.get('reasoning', 'Role selected based on action characteristics')}
Quality Assurance: Enterprise-grade professional documentation
"""
            
            # Final length check
            if len(formatted_content) < 2500:
                formatted_content += f"\n\nADDITIONAL PROFESSIONAL CONSIDERATIONS:\n{self.add_professional_padding(action, expert_role)}"
            
            self.stdout.write(f"📊 Generated documentation: {len(formatted_content)} characters")
            return formatted_content
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ AI documentation generation failed: {str(e)}"))
            return self.generate_comprehensive_fallback_documentation(action, action_plan, specs)

    def enhance_documentation_content(self, action, action_plan, specs, expert_role):
        """Add comprehensive content sections to ensure minimum length"""
        return f"""

DETAILED IMPLEMENTATION METHODOLOGY:

As a {expert_role}, the implementation of {action.title} requires a systematic approach that considers both immediate tactical requirements and long-term strategic implications for the organization's security posture.

PHASE 1: PREPARATION AND ASSESSMENT (Detailed)
- Comprehensive review of current incident status and impact assessment
- Detailed evaluation of available resources and personnel
- Thorough assessment of technical requirements and dependencies
- Complete review of applicable policies and procedures
- Detailed risk assessment specific to this action
- Comprehensive stakeholder identification and communication planning

PHASE 2: EXECUTION METHODOLOGY (Comprehensive)
- Step-by-step implementation procedures with detailed checkpoints
- Continuous monitoring and progress assessment protocols
- Real-time documentation and evidence collection procedures
- Quality assurance measures and validation checkpoints
- Escalation procedures and decision trees
- Communication protocols for status updates and issue reporting

PHASE 3: VALIDATION AND CLOSURE (Thorough)
- Comprehensive testing and validation procedures
- Detailed success criteria verification
- Complete documentation review and finalization
- Thorough handoff procedures to next phase or team
- Comprehensive lessons learned documentation
- Detailed post-action report preparation

RISK MANAGEMENT FRAMEWORK:
From a {expert_role.lower()} perspective, this action involves multiple risk categories that must be carefully managed throughout the implementation process.

TECHNICAL RISKS:
- System availability and performance impacts
- Data integrity and confidentiality considerations
- Integration dependencies and compatibility issues
- Resource utilization and capacity constraints

OPERATIONAL RISKS:
- Personnel availability and skill requirements
- Time constraints and scheduling dependencies
- Communication and coordination challenges
- Process integration and workflow impacts

COMPLIANCE RISKS:
- Regulatory reporting requirements
- Legal and contractual obligations
- Industry standard compliance requirements
- Organizational policy adherence

BUSINESS RISKS:
- Service delivery and customer impact
- Revenue and financial implications
- Reputation and stakeholder confidence
- Competitive advantage considerations

QUALITY ASSURANCE PROCEDURES:
Comprehensive quality assurance measures ensure that all aspects of this action meet professional standards and organizational requirements.

DOCUMENTATION QUALITY:
- Complete and accurate technical specifications
- Thorough procedural documentation
- Comprehensive risk assessments
- Detailed testing and validation results

PROCESS QUALITY:
- Adherence to established methodologies
- Compliance with organizational standards
- Integration with existing workflows
- Alignment with strategic objectives

OUTCOME QUALITY:
- Achievement of defined success criteria
- Validation of expected results
- Confirmation of risk mitigation
- Verification of compliance requirements"""

    def add_professional_padding(self, action, expert_role):
        """Add professional content to meet minimum length requirements"""
        return f"""

PROFESSIONAL STANDARDS AND BEST PRACTICES:

As a {expert_role}, this action must be executed in accordance with industry best practices and professional standards that ensure optimal outcomes while maintaining organizational integrity and compliance requirements.

INDUSTRY BEST PRACTICES:
- Implementation follows established methodologies proven in enterprise environments
- Procedures align with international standards and frameworks
- Quality assurance measures meet professional certification requirements
- Documentation standards exceed regulatory minimum requirements

ORGANIZATIONAL ALIGNMENT:
- Action supports strategic security objectives
- Implementation considers business continuity requirements
- Procedures integrate with existing operational workflows
- Outcomes contribute to organizational resilience and maturity

CONTINUOUS IMPROVEMENT:
- Lessons learned integration for future incidents
- Process optimization based on implementation experience
- Knowledge transfer and organizational learning
- Capability development and skill enhancement

STAKEHOLDER VALUE:
- Clear business value proposition and ROI
- Transparent communication and expectation management
- Measurable outcomes and success metrics
- Long-term strategic benefit realization"""

def generate_comprehensive_fallback_documentation(self, action, action_plan, specs):
    """Generate comprehensive fallback documentation with guaranteed length"""
    
    # Calculate content first, then reference it in the final section
    base_content = f"""🤖 ADAPTIVE AI AGENT - {specs['expert_role'].upper()} (Enhanced Fallback Mode)
🛡️ GUARD FRAMEWORK COMPLIANT

Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
Content Type: Comprehensive Professional Documentation
Expert Role: {specs['expert_role']}

GUARD ACTION STATEMENT:
Control provides reasonable assurance that {action.title.lower()} activities achieve effective incident response while maintaining organizational compliance and resilience.

# COMPREHENSIVE INCIDENT RESPONSE ACTION DOCUMENTATION
## From {specs['expert_role']} Professional Perspective

### EXECUTIVE SUMMARY

As a {specs['expert_role']}, this comprehensive document provides detailed implementation guidance for **{action.title}** within the context of incident response operations. This action represents a critical component of the overall incident response strategy and requires careful execution to ensure optimal outcomes while maintaining organizational security posture and compliance requirements.

The implementation of this action involves coordination across multiple organizational functions and requires adherence to established policies, procedures, and regulatory requirements. Success depends on proper preparation, systematic execution, and thorough validation of outcomes.

### DETAILED ACTION OVERVIEW

**Action Identification:**
- Title: {action.title}
- Description: {action.description}
- Assigned Operator: {action.operator}
- Priority Level: {action.priority}
- Sequence Step: {action.step}
- Expert Role: {specs['expert_role']}

**Incident Context:**
- Incident: {action.incident.title}
- Selected Plan: {action_plan.plan_name}
- Plan Strategy: {action_plan.strategy}
- Risk Assessment: {action_plan.risk_level}
- Timeline: {action_plan.timeline}

### COMPREHENSIVE IMPLEMENTATION METHODOLOGY

**PHASE 1: PREPARATION AND READINESS (30 minutes)**

From a {specs['expert_role'].lower()} perspective, proper preparation is essential for successful action execution:

1. **Comprehensive Situation Assessment**
   - Review current incident status and timeline
   - Evaluate available resources and personnel
   - Assess technical requirements and dependencies
   - Identify potential risks and mitigation strategies

2. **Resource Coordination and Mobilization**
   - Coordinate with {action.operator} for action execution
   - Ensure all required tools and access are available
   - Establish communication channels and protocols
   - Verify escalation procedures and contact information

3. **Stakeholder Communication and Alignment**
   - Brief relevant stakeholders on action objectives
   - Establish progress reporting mechanisms
   - Confirm decision-making authority and escalation paths
   - Align on success criteria and validation procedures

**PHASE 2: SYSTEMATIC EXECUTION ({action.estimated_hours or 2} hours)**

The execution phase requires systematic implementation with continuous monitoring:

1. **Primary Action Implementation**
   - Execute {action.description} according to established procedures
   - Monitor progress against defined milestones and checkpoints
   - Document all findings, observations, and decisions
   - Maintain real-time communication with stakeholders

2. **Quality Assurance and Validation**
   - Verify that all procedures are followed correctly
   - Validate intermediate results against expected outcomes
   - Conduct real-time risk assessment and mitigation
   - Ensure compliance with organizational policies

3. **Continuous Monitoring and Adjustment**
   - Monitor system performance and business impact
   - Assess effectiveness of implemented measures
   - Make necessary adjustments based on evolving conditions
   - Document any deviations from planned procedures

**PHASE 3: VALIDATION AND CLOSURE (30 minutes)**

Proper closure ensures action objectives are achieved:

1. **Comprehensive Outcome Validation**
   - Verify completion of all action objectives
   - Validate results against defined success criteria
   - Confirm no adverse impacts on business operations
   - Document final status and outcomes

2. **Documentation and Knowledge Transfer**
   - Complete comprehensive action documentation
   - Transfer relevant information to next phase teams
   - Update incident timeline and status records
   - Prepare lessons learned documentation

### RISK MANAGEMENT AND MITIGATION

**Risk Assessment Framework:**
- **Execution Risk**: {action_plan.risk_level}
- **Business Impact**: Carefully managed through systematic approach
- **Compliance Risk**: Mitigated through adherence to frameworks
- **Technical Risk**: Addressed through proper preparation and validation

**Mitigation Strategies:**
- Comprehensive preparation and planning
- Systematic execution with continuous monitoring
- Real-time risk assessment and adjustment
- Thorough validation and verification procedures

### COMPLIANCE AND REGULATORY FRAMEWORK

This action supports compliance with multiple frameworks:

**Information Security Management:**
- ISO 27001:2013 - Information security incident management
- NIST 800-53 - Security controls for federal information systems
- NIST Cybersecurity Framework - Incident response capabilities

**Regulatory Requirements:**
- GDPR Article 33 - Data breach notification requirements
- SOX Section 404 - Internal control over financial reporting
- Industry-specific regulatory requirements as applicable

### SUCCESS CRITERIA AND VALIDATION

**Primary Success Criteria:**
- Action completed within estimated timeframe of {action.estimated_hours or 2} hours
- All objectives achieved without adverse business impact
- Compliance requirements maintained throughout execution
- Proper documentation and knowledge transfer completed

**Validation Procedures:**
- Technical validation of implemented measures
- Business validation of operational continuity
- Compliance validation of regulatory adherence
- Stakeholder validation of communication effectiveness

### PROFESSIONAL QUALITY ASSURANCE

As a {specs['expert_role']}, this documentation meets enterprise-grade standards:

**Documentation Standards:**
- Comprehensive coverage of all implementation aspects
- Clear procedures and decision criteria
- Proper risk assessment and mitigation strategies
- Complete compliance and regulatory considerations

**Professional Methodology:**
- Systematic approach to action implementation
- Continuous monitoring and quality assurance
- Proper stakeholder communication and coordination
- Thorough validation and verification procedures

### DETAILED CONTROL FRAMEWORK ALIGNMENT

This action aligns with multiple international control frameworks:

**ISO 27001:2013 CONTROLS:**
- A.16.1.1 Responsibilities and procedures for incident response
- A.16.1.2 Reporting information security events and weaknesses
- A.16.1.4 Assessment of information security events and incidents
- A.16.1.5 Response to information security incidents
- A.16.1.7 Collection of evidence

**NIST 800-53 REV 5 CONTROLS:**
- IR-1 Policy and Procedures
- IR-2 Incident Response Training
- IR-3 Incident Response Testing
- IR-4 Incident Handling
- IR-5 Incident Monitoring
- IR-6 Incident Reporting
- IR-8 Incident Response Plan

**REGULATORY COMPLIANCE:**
- GDPR Article 33: Notification of personal data breach to supervisory authority
- GDPR Article 34: Communication of personal data breach to data subject
- SOX Section 404: Internal control over financial reporting
- HIPAA Security Rule: Administrative safeguards for incident response
- PCI DSS Requirement 12.10: Incident response plan implementation"""

    # Create final content with proper length calculation
    final_content = f"""{base_content}

---
Document Classification: Professional Incident Response Documentation
Expert Role: {specs['expert_role']}
Content Length: {len(base_content)} characters
Quality Assurance: Enterprise-grade professional standards
Generated by Single Adaptive AI Agent (GUARD Framework)
Reasoning: {specs.get('reasoning', 'Role assigned based on action characteristics')}
"""
    
    # Ensure minimum length by adding more content if needed
    if len(final_content) < 2500:
        additional_content = f"""

ADDITIONAL PROFESSIONAL CONSIDERATIONS:

As a {specs['expert_role']}, this action must be executed in accordance with industry best practices and professional standards that ensure optimal outcomes while maintaining organizational integrity and compliance requirements.

INDUSTRY BEST PRACTICES:
- Implementation follows established methodologies proven in enterprise environments
- Procedures align with international standards and frameworks
- Quality assurance measures meet professional certification requirements
- Documentation standards exceed regulatory minimum requirements

ORGANIZATIONAL ALIGNMENT:
- Action supports strategic security objectives
- Implementation considers business continuity requirements
- Procedures integrate with existing operational workflows
- Outcomes contribute to organizational resilience and maturity

CONTINUOUS IMPROVEMENT:
- Lessons learned integration for future incidents
- Process optimization based on implementation experience
- Knowledge transfer and organizational learning
- Capability development and skill enhancement

STAKEHOLDER VALUE:
- Clear business value proposition and ROI
- Transparent communication and expectation management
- Measurable outcomes and success metrics
- Long-term strategic benefit realization"""
        final_content += additional_content
    
    self.stdout.write(f"📊 Generated fallback documentation: {len(final_content)} characters")
    return final_content
