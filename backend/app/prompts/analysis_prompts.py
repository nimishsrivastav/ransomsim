"""
Analysis Generation Prompt Templates
"""

ANALYSIS_PROMPT_TEMPLATE = """Analyze this ransomware negotiation training session and provide comprehensive feedback.

{transcript}

SESSION METADATA:
- Total Messages: {total_messages}
- Duration: {duration_minutes} minutes
- Outcome: {outcome}

Your task is to provide detailed, constructive feedback as if you were an expert crisis negotiation trainer reviewing a student's performance.

ANALYSIS REQUIREMENTS:

1. PERFORMANCE SCORE (0-10):
   - Evaluate overall negotiation effectiveness
   - Consider tactics, timing, communication, and outcome
   - Be honest but constructive

2. KEY MISTAKES (3-5 specific errors):
   - What did the negotiator do wrong?
   - Why was it a mistake?
   - What were the consequences?
   - What should they have done instead?

3. SUCCESSFUL TACTICS (2-4 things done well):
   - What worked well?
   - What was the positive impact?

4. TACTICAL INSIGHTS (5-8 detailed observations):
   - Reference specific messages by number
   - Identify missed opportunities
   - Highlight dangerous concessions
   - Note effective pressure management
   - Each should include: message number, type (mistake/success/opportunity), analysis, improvement suggestion

5. RECOMMENDATIONS (3-5 prioritized learning points):
   - Specific skills to develop
   - Why these skills matter
   - Priority level for each

6. BENCHMARK COMPARISON:
   - Estimate how this outcome compares to typical scenarios
   - Average payment percentage (of initial demand)
   - Average time to resolution

IMPORTANT:
- Be specific - reference actual messages
- Be constructive - focus on learning
- Be realistic - compare to real-world ransomware negotiations
- Consider the threat actor's persona and tactics
- Evaluate both what was said AND what wasn't said

Respond with ONLY valid JSON matching the schema. No explanations outside the JSON.
"""