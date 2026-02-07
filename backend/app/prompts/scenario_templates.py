"""
Scenario Generation Prompt Templates

Provides templates for generating realistic ransomware breach scenarios
based on organization profile (size, industry, data sensitivity).
"""

# Main scenario generation template
SCENARIO_GENERATION_TEMPLATE = """Generate a realistic ransomware breach scenario for a cybersecurity training simulation.

ORGANIZATION PROFILE:
- Size: {org_size}
- Industry: {industry}
- Data Sensitivity Level: {data_sensitivity}

REQUIREMENTS:
Create a detailed, realistic scenario that includes:

1. BREACH NARRATIVE:
   - Entry vector (how attackers got in - be specific: phishing email with malicious attachment, compromised RDP, supply chain, zero-day exploit, etc.)
   - Attack timeline (when attack started, when encryption occurred, when discovered)
   - Attacker dwell time before encryption

2. TECHNICAL IMPACT:
   - Systems encrypted (servers, workstations, specific applications)
   - Backup status (encrypted, offline, compromised)
   - Network scope (single site, multi-site, cloud affected)

3. DATA AT RISK:
   - Types of data exfiltrated (be specific to industry)
   - Volume estimates
   - Regulatory implications (HIPAA, PCI-DSS, GDPR, etc. as applicable)

4. BUSINESS IMPACT:
   - Operations affected
   - Revenue impact
   - Customer/patient/client exposure

5. RANSOM DEMAND:
   - Initial amount in USD (realistic for org size)
   - Payment deadline
   - Threat actor's stated consequences

REALISTIC PRICING GUIDELINES:
- SMB (< 500 employees): $50,000 - $500,000
- Mid-market (500-5000 employees): $500,000 - $5,000,000
- Enterprise (5000+ employees): $5,000,000 - $50,000,000

Adjust based on:
- Industry (healthcare, finance, critical infrastructure = higher)
- Data sensitivity (critical = higher)
- Public company status (higher)

Respond with ONLY valid JSON matching this structure:
{{
    "breach_narrative": {{
        "entry_vector": "string - specific attack method",
        "attack_timeline": {{
            "initial_access": "date/time description",
            "lateral_movement": "date/time description",
            "data_exfiltration": "date/time description",
            "encryption_triggered": "date/time description",
            "discovered_by_victim": "date/time description"
        }},
        "attacker_dwell_time_days": number
    }},
    "systems_affected": [
        "list of specific systems/servers encrypted"
    ],
    "backup_status": "string - status of backups",
    "data_at_risk": [
        "list of specific data types stolen"
    ],
    "data_volume_estimate": "string - estimated size",
    "regulatory_implications": [
        "list of relevant regulations"
    ],
    "business_impact": {{
        "operations_down": "string - description",
        "estimated_daily_revenue_loss": number,
        "customer_exposure_count": number
    }},
    "ransom_amount": number,
    "payment_deadline_hours": number,
    "threat_actor_ultimatum": "string - what happens if they don't pay"
}}
"""

# Industry-specific context additions
INDUSTRY_CONTEXT = {
    "healthcare": """
HEALTHCARE-SPECIFIC CONSIDERATIONS:
- Patient health records (PHI) under HIPAA
- Life-safety systems (if hospital)
- Medical device connectivity
- Emergency room/critical care impact
- Patient diversion to other facilities
- Prescription systems and pharmacy
- Insurance/billing systems
- Research data and clinical trials
""",
    "finance": """
FINANCIAL SERVICES-SPECIFIC CONSIDERATIONS:
- Customer financial records
- Trading systems and market data
- Regulatory compliance (SOX, PCI-DSS, GLBA)
- Wire transfer capabilities
- Customer account access
- Audit trails and transaction records
- Integration with payment networks
- Reputation and customer trust
""",
    "manufacturing": """
MANUFACTURING-SPECIFIC CONSIDERATIONS:
- Production line control systems (OT/ICS)
- Supply chain integration
- Quality control systems
- Inventory management
- Customer orders and fulfillment
- Proprietary designs/IP
- Safety systems
- Just-in-time delivery impacts
""",
    "retail": """
RETAIL-SPECIFIC CONSIDERATIONS:
- Point-of-sale systems
- Customer payment data (PCI-DSS)
- Inventory and warehouse systems
- E-commerce platform
- Customer loyalty programs
- Supply chain/vendor portals
- Seasonal timing impact
- Brand reputation
""",
    "technology": """
TECHNOLOGY-SPECIFIC CONSIDERATIONS:
- Source code repositories
- Customer data and credentials
- SaaS platform availability
- API and integration dependencies
- Intellectual property
- Development environments
- Customer-facing services SLAs
- Third-party security implications
""",
    "education": """
EDUCATION-SPECIFIC CONSIDERATIONS:
- Student records (FERPA)
- Research data and grants
- Online learning platforms
- Financial aid systems
- Alumni and donor databases
- Academic calendar timing
- Faculty and staff data
- Campus operations
""",
    "government": """
GOVERNMENT-SPECIFIC CONSIDERATIONS:
- Citizen personal data
- Public service continuity
- Law enforcement data
- Regulatory/licensing systems
- Inter-agency dependencies
- Public transparency requirements
- Political/media scrutiny
- National security implications
""",
    "legal": """
LEGAL SERVICES-SPECIFIC CONSIDERATIONS:
- Attorney-client privileged information
- Active case files
- Client confidential documents
- Court filing deadlines
- Trust accounts
- Regulatory bar requirements
- Client trust and reputation
- Opposing counsel implications
""",
}

# Difficulty modifiers
DIFFICULTY_MODIFIERS = {
    "easy": """
DIFFICULTY: EASY (Training Level)
- Threat actor is less sophisticated
- More time to respond
- Lower ransom demand
- More negotiation flexibility
- Clearer communication from attacker
""",
    "realistic": """
DIFFICULTY: REALISTIC (Standard)
- Threat actor is experienced
- Standard timeframes
- Market-rate ransom demand
- Typical negotiation dynamics
- Professional but firm attacker
""",
    "expert": """
DIFFICULTY: EXPERT (Advanced)
- Highly sophisticated threat actor
- Compressed timelines
- Premium ransom demand
- Aggressive negotiation tactics
- Multi-channel pressure (data leak threats, media)
""",
}

# Quick scenario templates for demo mode
DEMO_SCENARIOS = {
    "healthcare_critical": {
        "org_size": "mid-market",
        "industry": "healthcare",
        "data_sensitivity": "critical",
        "preset_narrative": "Regional hospital network hit by ransomware with patient data exfiltration",
    },
    "finance_sensitive": {
        "org_size": "enterprise",
        "industry": "finance",
        "data_sensitivity": "high",
        "preset_narrative": "Investment firm targeted with customer financial records at risk",
    },
    "manufacturing_standard": {
        "org_size": "mid-market",
        "industry": "manufacturing",
        "data_sensitivity": "medium",
        "preset_narrative": "Automotive parts supplier with production shutdown",
    },
}


def get_scenario_prompt(
    org_size: str,
    industry: str,
    data_sensitivity: str,
    difficulty: str = "realistic",
) -> str:
    """
    Build complete scenario generation prompt

    Args:
        org_size: Organization size (smb, mid-market, enterprise)
        industry: Industry vertical
        data_sensitivity: Data sensitivity level (low, medium, high, critical)
        difficulty: Scenario difficulty (easy, realistic, expert)

    Returns:
        Complete prompt string for scenario generation
    """
    # Start with base template
    prompt = SCENARIO_GENERATION_TEMPLATE.format(
        org_size=org_size,
        industry=industry,
        data_sensitivity=data_sensitivity,
    )

    # Add industry context if available
    industry_lower = industry.lower()
    if industry_lower in INDUSTRY_CONTEXT:
        prompt += f"\n{INDUSTRY_CONTEXT[industry_lower]}"

    # Add difficulty modifier
    difficulty_lower = difficulty.lower()
    if difficulty_lower in DIFFICULTY_MODIFIERS:
        prompt += f"\n{DIFFICULTY_MODIFIERS[difficulty_lower]}"

    return prompt
