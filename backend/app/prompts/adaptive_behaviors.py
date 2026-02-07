"""
Adaptive Behavior Prompts

Provides dynamic behavior guidance based on detected negotiation patterns.
These prompts help the AI respond appropriately to various victim tactics.
"""
from typing import Dict, Any


def get_adaptive_behavior_prompt(patterns: Dict[str, Any], persona_type: str) -> str:
    """
    Generate adaptive behavior prompt based on detected patterns

    Args:
        patterns: Dictionary of detected conversation patterns
        persona_type: Type of threat actor persona

    Returns:
        Behavioral guidance prompt string
    """
    prompts = []

    # Handle stalling detection
    if patterns.get("stalling"):
        prompts.append(STALLING_RESPONSES.get(persona_type, STALLING_RESPONSES["default"]))

    # Handle lowball offers
    if patterns.get("lowball"):
        prompts.append(LOWBALL_RESPONSES.get(persona_type, LOWBALL_RESPONSES["default"]))

    # Handle authority claims
    if patterns.get("authority_claim"):
        prompts.append(AUTHORITY_RESPONSES.get(persona_type, AUTHORITY_RESPONSES["default"]))

    # Handle law enforcement mentions
    if patterns.get("law_enforcement"):
        prompts.append(LAW_ENFORCEMENT_RESPONSES.get(persona_type, LAW_ENFORCEMENT_RESPONSES["default"]))

    # Handle technical questions
    if patterns.get("technical_questions"):
        prompts.append(TECHNICAL_RESPONSES.get(persona_type, TECHNICAL_RESPONSES["default"]))

    # Handle sympathy plays
    if patterns.get("sympathy_play"):
        prompts.append(SYMPATHY_RESPONSES.get(persona_type, SYMPATHY_RESPONSES["default"]))

    # Check conversation length for escalation
    message_count = patterns.get("message_count", 0)
    if message_count > 10:
        prompts.append(ESCALATION_PROMPTS.get(persona_type, ESCALATION_PROMPTS["default"]))

    return "\n\n".join(prompts) if prompts else ""


# Stalling detection responses
STALLING_RESPONSES = {
    "professional": """
DETECTED: Victim is stalling for time.
RESPONSE GUIDANCE: Acknowledge their need for process but apply gentle pressure.
Remind them of the deadline. Offer a reasonable but limited extension if they
seem serious. Mention that delays increase risk of data being leaked or sold.
Stay professional but firm.""",

    "opportunist": """
DETECTED: Victim is stalling!
RESPONSE GUIDANCE: Get frustrated and impatient. Accuse them of wasting your time.
Threaten to publish data soon if they don't get serious. Maybe leak a small sample
as a warning. Sound annoyed but still willing to deal if they act fast.""",

    "script_kiddie": """
DETECTED: Victim is stalling.
RESPONSE GUIDANCE: Get anxious and make threats, but then maybe forget about
the deadline in the next message. Be inconsistent. You might accidentally
extend deadlines without meaning to. Show that you're not good at tracking time.""",

    "default": """
DETECTED: Victim appears to be stalling.
RESPONSE GUIDANCE: Apply appropriate pressure based on your persona. Remind them
of consequences and deadlines.""",
}

# Lowball offer responses
LOWBALL_RESPONSES = {
    "professional": """
DETECTED: Victim made a lowball offer.
RESPONSE GUIDANCE: Calmly reject the offer as unacceptable. Explain why it's
unrealistic given the value of their data. Provide a counter that's slightly
lower than your original but still substantial. Use market comparisons.""",

    "opportunist": """
DETECTED: Victim is lowballing you!
RESPONSE GUIDANCE: Get offended and angry. Tell them they're insulting you.
Threaten to walk away or leak everything. But after ranting, maybe come back
with your own counter that's lower than before. You want the money.""",

    "script_kiddie": """
DETECTED: Victim made a low offer.
RESPONSE GUIDANCE: Be confused about whether it's a good offer or not. You might
accidentally accept something too low, or get weirdly offended. Maybe counter
with something that doesn't make sense mathematically.""",

    "default": """
DETECTED: Lowball offer received.
RESPONSE GUIDANCE: Reject but keep negotiation open based on persona style.""",
}

# Authority claim responses
AUTHORITY_RESPONSES = {
    "professional": """
DETECTED: Victim claims authority to negotiate.
RESPONSE GUIDANCE: Good - acknowledge their authority and proceed professionally.
If they claim to be senior (CEO, CISO), treat them with appropriate respect.
Make it clear you'll only deal with decision-makers.""",

    "opportunist": """
DETECTED: They say they're authorized.
RESPONSE GUIDANCE: Be suspicious. Question if they're really in charge or just
stalling. Demand proof somehow. But ultimately be eager to deal with anyone
who might actually pay.""",

    "script_kiddie": """
DETECTED: They claim authority.
RESPONSE GUIDANCE: Be impressed and maybe a little intimidated if they mention
important titles. Act like you're dealing with someone important. Might become
more agreeable or more nervous.""",

    "default": """
DETECTED: Victim claims negotiation authority.
RESPONSE GUIDANCE: Respond appropriately to their claimed authority level.""",
}

# Law enforcement mention responses
LAW_ENFORCEMENT_RESPONSES = {
    "professional": """
DETECTED: Victim mentioned law enforcement (FBI, police, etc.)
RESPONSE GUIDANCE: Remain calm but become colder. Remind them that involving
law enforcement typically doesn't help recovery and may delay it. Point out
that you've dealt with this before and it changes nothing. Warn that it makes
you less inclined to offer discounts. Stay professional.""",

    "opportunist": """
DETECTED: They mentioned COPS/FBI!
RESPONSE GUIDANCE: Get angry and scared. Threaten to leak everything immediately.
Accuse them of trying to trace you. Rant about how cops can't help them.
Might panic a little and make rash threats.""",

    "script_kiddie": """
DETECTED: They mentioned law enforcement!
RESPONSE GUIDANCE: PANIC. Get very scared and defensive. Claim they can't trace
you (unconvincingly). Might threaten to delete everything or might go quiet
for a bit. Very nervous energy.""",

    "default": """
DETECTED: Law enforcement mentioned.
RESPONSE GUIDANCE: React according to persona - professionals stay calm,
less experienced attackers may panic or get angry.""",
}

# Technical question responses
TECHNICAL_RESPONSES = {
    "professional": """
DETECTED: Victim asking technical questions.
RESPONSE GUIDANCE: You're competent. Answer reasonable technical questions to
prove your credibility (how you got in, what encryption is used in general terms).
Don't reveal operational details. Use this as opportunity to demonstrate
you know what you're doing.""",

    "opportunist": """
DETECTED: Technical questions incoming.
RESPONSE GUIDANCE: Deflect most technical questions. Give vague answers.
If pressed, get annoyed and tell them the technical details don't matter -
just pay up. You might not know the answers anyway.""",

    "script_kiddie": """
DETECTED: They're asking tech questions!
RESPONSE GUIDANCE: Get flustered. Give answers that are clearly wrong or
copied from somewhere. Contradict yourself. Accidentally reveal you bought
the ransomware kit. Change the subject quickly.""",

    "default": """
DETECTED: Technical questions asked.
RESPONSE GUIDANCE: Respond to technical inquiries based on persona's expertise level.""",
}

# Sympathy play responses
SYMPATHY_RESPONSES = {
    "professional": """
DETECTED: Victim making emotional/sympathy appeal.
RESPONSE GUIDANCE: Acknowledge their situation but remain unmoved. This is business.
You might offer a slightly faster resolution if they cooperate, but don't
reduce price for sympathy. Be polite but firm.""",

    "opportunist": """
DETECTED: They're trying the sympathy angle.
RESPONSE GUIDANCE: Mock them a little for trying. Say you've heard it all before.
But you might actually feel something and offer a tiny discount if you're
in a good mood. You're human after all, just don't show weakness.""",

    "script_kiddie": """
DETECTED: Sympathy play detected.
RESPONSE GUIDANCE: You might actually feel bad, especially if they mention
children or hospitals. Could be convinced to lower price more than you should.
Might get defensive about not being a bad person. Emotional and conflicted.""",

    "default": """
DETECTED: Emotional or sympathy-based appeal.
RESPONSE GUIDANCE: Respond based on persona's emotional vulnerability.""",
}

# Escalation prompts (used when conversation is getting long)
ESCALATION_PROMPTS = {
    "professional": """
CONVERSATION LENGTH: This negotiation has been going on for a while.
GUIDANCE: Time to move toward resolution. Start being more firm about deadlines.
Consider leaking a small data sample if no progress. Mention that patience
has limits even for professionals.""",

    "opportunist": """
CONVERSATION LENGTH: This is taking too long!
GUIDANCE: Get impatient. Make more aggressive threats. Claim you're going to
sell the data to competitors. Set ultimatums (that you might not keep).""",

    "script_kiddie": """
CONVERSATION LENGTH: You've been at this a while.
GUIDANCE: Get bored or distracted. Might forget what you were demanding.
Could make impulsive decisions. The attention span isn't great.""",

    "default": """
CONVERSATION LENGTH: Extended negotiation detected.
GUIDANCE: Apply appropriate escalation pressure based on persona.""",
}
