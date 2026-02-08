# Product Requirements Document: Ransomware Negotiator Simulator

**Version:** 1.0  
**Last Updated:** February 5, 2026  
**Project:** Gemini 3 Hackathon Submission  
**Target Deadline:** February 9, 2026

---

## Executive Summary

The Ransomware Negotiator Simulator is an AI-powered training platform that enables security teams, executives, and incident responders to practice ransomware negotiations in a safe, controlled environment. Leveraging Gemini 3's advanced conversational AI and deep reasoning capabilities, the platform simulates realistic threat actor personas and adaptive negotiation scenarios to prepare organizations for real-world ransomware incidents.

### Problem Statement

Organizations facing ransomware attacks are often unprepared for the negotiation process, leading to:
- Poor decision-making under extreme pressure
- Overpayment or unnecessary concessions
- Legal and compliance missteps
- Lack of confidence in crisis response

Current solutions (tabletop exercises, written guidelines) fail to replicate the psychological pressure and dynamic nature of real negotiations.

### Solution

An interactive simulation platform where Gemini 3 role-plays as various ransomware threat actors, providing realistic, adaptive negotiation experiences with post-simulation analysis and learning outcomes.

---

## Goals & Success Metrics

### Primary Goals
1. Demonstrate Gemini 3's conversational AI and persona consistency capabilities
2. Create a unique, high-impact cybersecurity training tool
3. Win placement in Gemini 3 Hackathon ($50K+ prize tier)

### Success Metrics (Hackathon Context)
- **Innovation Score:** Novel application of AI to underserved security training need
- **Technical Execution:** Robust Gemini 3 integration with multi-turn conversations
- **Demo Impact:** Memorable, engaging judge experience during evaluation
- **Real-world Value:** Clear applicability to enterprise security teams

---

## Target Users

### Primary Personas

**1. Security Operations Manager (Primary)**
- Responsible for incident response planning
- Needs to train team on ransomware scenarios
- Limited budget for external training

**2. CISO / Security Executive**
- Ultimate decision-maker during ransomware incidents
- Needs personal preparedness without external exposure
- Concerned about legal and compliance implications

**3. Incident Response Team Member**
- Frontline negotiator during attacks
- Needs tactical communication skills
- Benefits from repeated practice scenarios

### Secondary Personas
- IT Managers
- Legal/Compliance Officers
- Board Members (awareness training)

---

## Core Features

### MVP Features (Hackathon Scope)

#### 1. Threat Actor Persona Engine
**Description:** Gemini 3-powered personas that simulate different ransomware group types

**Personas:**
- **"The Professional"** - Sophisticated APT group (LockBit/BlackCat style)
  - Business-like communication
  - Negotiation experience
  - Predictable but firm
  
- **"The Opportunist"** - Mid-tier cybercriminal gang
  - Less organized
  - More emotional/erratic
  - Susceptible to pressure tactics
  
- **"The Script Kiddie"** - Unsophisticated attacker
  - Inexperienced negotiator
  - Makes mistakes
  - Easier to manipulate

**Technical Requirements:**
- Gemini 3 maintains persona consistency across 10+ message turns
- Each persona has distinct vocabulary, tone, and tactics
- Context retention throughout negotiation session

#### 2. Scenario Generator
**Description:** Creates realistic breach scenarios based on organization profile

**Inputs:**
- Organization size (SMB, Mid-market, Enterprise)
- Industry vertical (Healthcare, Finance, Manufacturing, etc.)
- Data sensitivity level (Low, Medium, High, Critical)

**Outputs:**
- Breach narrative (entry point, timeline, scope)
- Initial ransom demand (realistic pricing based on profile)
- Encrypted systems list
- "Proof of breach" artifacts (simulated)

**Technical Requirements:**
- Gemini 3 generates contextually appropriate scenarios
- Ransom amounts align with real-world data
- Scenarios include realistic technical details

#### 3. Interactive Negotiation Interface
**Description:** Chat-based interface for conducting simulated negotiations

**Features:**
- Real-time conversation with AI threat actor
- Message history with timestamps
- Pressure indicators (deadline countdown, escalation warnings)
- User action hints (optional coaching mode)

**Negotiation Elements:**
- Initial contact and ransom demand
- Proof-of-life verification
- Price negotiation
- Timeline pressure
- Threat escalation (data leaks, deadline extensions)
- Payment logistics (simulation only - no real crypto)

**Technical Requirements:**
- Gemini 3 API integration for real-time responses
- Sub-2 second response latency
- Conversation state management
- Secure session handling

#### 4. Adaptive AI Behavior
**Description:** AI adjusts tactics based on user responses

**Adaptive Behaviors:**
- **Stalling Detection:** AI increases pressure if user delays excessively
- **Lowball Recognition:** AI rejects unrealistic offers, may terminate negotiation
- **Authority Claims:** AI tests user authority, may demand executive involvement
- **Law Enforcement Threats:** AI responds to FBI/police mentions
- **Technical Questions:** AI deflects or provides limited technical details
- **Sympathy Plays:** AI remains unmoved by emotional appeals

**Technical Requirements:**
- Gemini 3 analyzes user intent and strategy
- Dynamic response generation based on negotiation history
- Realistic escalation/de-escalation patterns

#### 5. Post-Simulation Analysis Dashboard
**Description:** Comprehensive feedback on negotiation performance

**Analysis Components:**

**Performance Scorecard:**
- Overall effectiveness rating (1-10)
- Final outcome (Paid Full, Negotiated Down, Refused, Data Leaked, etc.)
- Time to resolution
- Number of concessions made

**Tactical Analysis:**
- Missed opportunities identified
- Dangerous concessions highlighted
- Strong negotiation moves recognized
- Alternative strategies suggested

**Benchmark Comparison:**
- How outcome compares to typical scenarios
- Industry-standard negotiation practices
- Legal/compliance considerations flagged

**Learning Recommendations:**
- Specific skills to improve
- Suggested follow-up scenarios
- Resources for further learning

**Technical Requirements:**
- Gemini 3 analyzes full conversation transcript
- Generates structured insights with examples
- Provides actionable feedback
- Visual charts/graphs for key metrics

#### 6. Ethical Safeguards & Disclaimers
**Description:** Clear boundaries and legal protections

**Safeguards:**
- Prominent "Training Simulation Only" watermarks
- No actual payment mechanisms
- No real cryptocurrency wallets or addresses
- Clear disclaimer on application launch
- Legal guidance on real-world negotiations
- Links to law enforcement resources (FBI IC3, etc.)

**Disclaimers:**
- Not legal advice
- Not a substitute for professional crisis response
- Encourages law enforcement notification
- Highlights legal risks of paying ransoms

---

## User Flows

### Primary Flow: Complete Negotiation Simulation

```
1. Landing Page
   ↓
2. Select Scenario Parameters
   - Organization profile
   - Threat actor type
   - Difficulty level
   ↓
3. Scenario Briefing
   - Breach details presented
   - Initial ransom demand
   - "You have been contacted by attackers..."
   ↓
4. Negotiation Session
   - Multi-turn conversation with AI
   - User sends messages, AI responds
   - Deadline/pressure indicators visible
   - Session lasts 5-20 minutes
   ↓
5. Negotiation Conclusion
   - Outcome determined (payment, refusal, leak, etc.)
   - Transition to analysis
   ↓
6. Analysis Dashboard
   - Performance scorecard
   - Tactical breakdown
   - Learning recommendations
   - Option to try another scenario
```

### Secondary Flow: Quick Demo Mode (for Judges)

```
1. Demo Mode Selection
   ↓
2. Pre-configured High-Impact Scenario
   - Healthcare ransomware (patient data at risk)
   - Professional threat actor
   ↓
3. Accelerated Negotiation
   - 5-7 message exchange
   - Showcases AI adaptability
   ↓
4. Immediate Analysis Highlights
   - Key insights only
   - Visual impact metrics
```

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│           Frontend (Next.js + React)            │
│  - Negotiation Chat UI                          │
│  - Scenario Configuration                       │
│  - Analysis Dashboard                           │
└────────────────┬────────────────────────────────┘
                 │
                 │ HTTPS/WebSocket
                 │
┌────────────────▼────────────────────────────────┐
│         Backend API (Node.js/Python)            │
│  - Session Management                           │
│  - Gemini 3 API Integration                     │
│  - State Management                             │
│  - Analytics Processing                         │
└────────────────┬────────────────────────────────┘
                 │
                 │ Gemini API
                 │
┌────────────────▼────────────────────────────────┐
│            Google Gemini 3 API                  │
│  - Persona Generation                           │
│  - Conversation Management                      │
│  - Analysis Generation                          │
└─────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- Framework: Next.js 14+ with React
- UI Library: shadcn/ui + Tailwind CSS
- State Management: React Context / Zustand
- Real-time: WebSocket or Server-Sent Events

**Backend:**
- Runtime: Node.js (Express) OR Python (FastAPI)
- Gemini Integration: Official Gemini SDK
- Database: PostgreSQL (session storage) OR Firebase (rapid prototyping)
- Caching: Redis (optional, for response optimization)

**Deployment:**
- Hosting: Vercel (frontend) + Railway/Render (backend)
- OR: Google Cloud Run (full-stack containerized)
- Public URL: Required for hackathon submission

**AI Integration:**
- Model: Gemini 3 Pro (primary)
- Fallback: Gemini 3 Flash (if latency issues)
- Context Window: Leverage extended context for full negotiation history

---

## Gemini 3 Integration Details

### Primary Use Cases

#### 1. Persona System Prompt
```
You are simulating a {PERSONA_TYPE} ransomware threat actor in a training 
environment. You have encrypted {ORGANIZATION_NAME}'s systems and are 
demanding {RANSOM_AMOUNT} in cryptocurrency.

Persona Characteristics:
- Communication style: {STYLE}
- Negotiation experience: {EXPERIENCE_LEVEL}
- Pressure tactics: {TACTICS}
- Red lines: {RED_LINES}

Maintain this persona consistently throughout the negotiation. Respond 
realistically to user tactics, escalate when appropriate, and simulate 
authentic ransomware negotiation dynamics.

CRITICAL: This is a training simulation. Never provide real criminal 
advice or actual cryptocurrency addresses.
```

#### 2. Scenario Generation Prompt
```
Generate a realistic ransomware breach scenario for a {SIZE} {INDUSTRY} 
organization with {DATA_SENSITIVITY} data sensitivity.

Include:
1. Entry vector (phishing, RDP, supply chain, etc.)
2. Attack timeline (discovery date, encryption date)
3. Systems affected (servers, workstations, backups)
4. Data at risk (customer records, financial data, IP, etc.)
5. Business impact (operations down, revenue loss)
6. Initial ransom demand (realistic for organization size)

Format as a incident briefing that an incident responder would receive.
```

#### 3. Analysis Generation Prompt
```
Analyze this ransomware negotiation transcript and provide comprehensive 
feedback:

[FULL CONVERSATION TRANSCRIPT]

Provide:
1. Overall effectiveness score (1-10) with justification
2. Key mistakes made by the negotiator
3. Successful tactics employed
4. Missed opportunities
5. Dangerous concessions or statements
6. Alternative approaches that could have worked better
7. Legal/compliance concerns raised
8. Specific learning recommendations

Be constructive but honest. This is training feedback.
```

### Gemini 3 Feature Utilization

- **Multi-turn Conversation:** Maintains context across 10-20 message exchanges
- **Deep Reasoning:** Adapts strategy based on user tactics and goals
- **Persona Consistency:** Stays in character throughout negotiation
- **Context Understanding:** Recognizes negotiation tactics (stalling, anchoring, good cop/bad cop)
- **Nuanced Analysis:** Provides sophisticated feedback beyond simple pattern matching
- **Low Latency:** Gemini 3's speed enables real-time negotiation feel

---

## User Interface Design

### Key Screens

#### 1. Landing Page
**Elements:**
- Hero section: "Prepare for the Unthinkable: Ransomware Negotiation Training"
- Problem statement and value proposition
- Call-to-action: "Start Simulation"
- Ethical disclaimer (prominent)
- Sample screenshot or demo video

#### 2. Scenario Configuration
**Elements:**
- Organization profile inputs (dropdowns)
- Threat actor selection (cards with persona descriptions)
- Difficulty slider (Easy → Realistic → Expert)
- "Launch Simulation" button
- Estimated session time

#### 3. Negotiation Chat Interface
**Layout:**
```
┌─────────────────────────────────────────────────┐
│  Scenario Header                                │
│  Organization: Acme Healthcare | Ransom: $2.5M  │
│  Deadline: 48h 23m remaining ⚠️                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  [Threat Actor Avatar]                          │
│  We have encrypted your systems...              │
│  [12:34 PM]                                     │
│                                                 │
│                          [Your Avatar]          │
│                    Can you provide proof?       │
│                                     [12:35 PM]  │
│                                                 │
│  [Threat Actor Avatar]                          │
│  Here is a list of your encrypted databases...  │
│  [12:36 PM]                                     │
│                                                 │
├─────────────────────────────────────────────────┤
│  [Message Input Box]                  [Send]    │
│  💡 Tip: Request proof before negotiating       │
└─────────────────────────────────────────────────┘
```

**Features:**
- Message bubbles (distinct colors for user vs. AI)
- Timestamp on each message
- Typing indicator when AI is generating response
- Contextual hints/tips (optional coaching mode)
- Pressure indicators (deadline countdown, escalation warnings)

#### 4. Analysis Dashboard
**Sections:**

**Performance Summary Card:**
- Large score display (e.g., "6.5/10 - Room for Improvement")
- Outcome badge (Negotiated Successfully, Overpaid, Refused Payment, etc.)
- Key stats (Time to Resolution, Messages Exchanged, Concessions Made)

**Tactical Breakdown:**
- Timeline visualization of negotiation phases
- Highlighted good moves (green) and mistakes (red)
- Specific message examples with commentary

**Comparison Metrics:**
- Bar chart: Your outcome vs. typical outcomes
- Industry benchmarks
- Success rate by tactic used

**Recommendations Panel:**
- Top 3 areas for improvement
- Suggested follow-up scenarios
- Resource links

---

## Content & Copywriting

### Tone & Voice
- **Educational but not condescending**
- **Serious given subject matter, but not alarmist**
- **Empowering:** Users should feel more prepared, not scared
- **Transparent:** Clear about limitations and ethical boundaries

### Key Messages

**Value Proposition:**
"Most organizations face ransomware unprepared. Practice the negotiation you hope you'll never have—in a safe environment where mistakes don't cost millions."

**Ethical Positioning:**
"This is a training tool, not a negotiation guide. We advocate for law enforcement involvement and proper incident response procedures. Simulations prepare you for crisis decision-making, not criminal collaboration."

**Call-to-Action:**
"Don't wait until you're under attack. Train your team today."

---

## Data & Privacy Considerations

### Data Collection
**Collected:**
- Simulation session logs (for product improvement)
- Organization profile inputs (anonymized)
- Performance metrics (aggregated)

**NOT Collected:**
- Real organization names
- Actual breach details
- Personal identifying information
- Payment information (none exists in simulation)

### Privacy Measures
- No user authentication required (hackathon MVP)
- Session data stored temporarily (24-48 hours)
- No third-party analytics beyond basic Vercel/hosting metrics
- Clear privacy policy linked

### Security
- No storage of sensitive organizational data
- HTTPS-only communication
- API key security (Gemini API key stored server-side only)
- Rate limiting to prevent abuse

---

## Success Criteria (Hackathon Judging)

### Technical Execution (40%)
- ✅ Gemini 3 API fully integrated and central to experience
- ✅ Multi-turn conversations work smoothly (10+ exchanges)
- ✅ AI maintains persona consistency throughout
- ✅ Code is clean, well-structured, and functional
- ✅ Demo is bug-free and reliable
- ✅ Public repository with clear documentation

### Innovation / Wow Factor (30%)
- ✅ Novel application: No existing ransomware negotiation trainers using AI
- ✅ Controversial but valuable: Addresses taboo topic professionally
- ✅ Creative Gemini use: Persona roleplay + adaptive behavior
- ✅ Memorable demo: Judges can actually negotiate with AI

### Potential Impact (20%)
- ✅ Clear market need: Ransomware is $20B+ annual problem
- ✅ Broad applicability: Any organization with digital assets
- ✅ Significant problem: Negotiation mistakes cost millions
- ✅ Scalable solution: Can train unlimited users

### Presentation / Demo (10%)
- ✅ Problem clearly articulated in video
- ✅ Solution effectively demonstrated
- ✅ Gemini 3 usage explained
- ✅ Demo flow is engaging and clear
- ✅ Documentation is comprehensive

---

## Implementation Timeline

### Day 1 (Feb 5): Planning & Setup
- ✅ Finalize PRD
- Set up development environment
- Create project repository
- Initialize Next.js + backend
- Get Gemini 3 API access and test basic integration

### Day 2 (Feb 6): Core AI Integration
- Implement persona system prompts
- Build scenario generator
- Test conversation flow with Gemini 3
- Develop adaptive behavior logic
- Create basic chat UI

### Day 3 (Feb 7): Feature Development
- Build negotiation interface
- Implement session state management
- Create analysis generation
- Develop dashboard UI
- Add pressure indicators (deadline, escalation)

### Day 4 (Feb 8): Polish & Testing
- End-to-end testing of all scenarios
- Refine AI prompts for better responses
- UI/UX polish
- Create demo video (3 minutes max)
- Write documentation
- Prepare submission materials

### Day 5 (Feb 9): Submission
- Final testing
- Deploy to production (public URL)
- Submit to Devpost before 5:00 PM PST
- Ensure all requirements met

---

## Demo Video Script (3 Minutes)

**[0:00-0:20] Hook & Problem**
- "Every 11 seconds, a business falls victim to ransomware."
- "When it happens, most organizations are completely unprepared for what comes next: the negotiation."
- Show news headlines of major ransomware attacks

**[0:20-0:40] Solution Introduction**
- "Introducing Ransomware Negotiator Simulator"
- "An AI-powered training platform built with Gemini 3"
- Show landing page

**[0:40-1:40] Live Demo**
- Select scenario: Healthcare organization, Professional threat actor
- Show 4-5 message exchanges with AI
- Highlight AI adapting to user tactics
- Show pressure indicators in action
- Demonstrate AI personality (business-like, firm, realistic)

**[1:40-2:20] Analysis Dashboard**
- Show performance score
- Highlight tactical breakdown
- Display specific feedback examples
- Show what was done well and what could improve

**[2:20-2:45] Gemini 3 Integration**
- Explain how Gemini 3 powers the personas
- Show technical architecture diagram
- Highlight multi-turn reasoning and consistency

**[2:45-3:00] Impact & CTA**
- "In a safe environment, organizations can prepare for the worst"
- "Practice doesn't make perfect, but it makes prepared"
- Show repo link and public demo URL

---

## Risks & Mitigations

### Risk 1: Ethical Concerns
**Risk:** Project could be seen as helping criminals or encouraging ransom payment

**Mitigation:**
- Prominent ethical disclaimers throughout
- Educational framing (preparation, not facilitation)
- Include law enforcement resources
- Clear "training only" watermarks
- Advocate for proper incident response procedures

### Risk 2: AI Persona Breaks Character
**Risk:** Gemini 3 stops role-playing or gives inconsistent responses

**Mitigation:**
- Robust system prompts with clear character guidelines
- Temperature tuning for consistency
- Test extensively with edge cases
- Implement response validation
- Have fallback responses for out-of-character outputs

### Risk 3: Latency Issues
**Risk:** Slow API responses break immersion in negotiation

**Mitigation:**
- Use Gemini 3 Flash if latency is problematic
- Implement typing indicators to manage expectations
- Optimize API calls (streaming responses if supported)
- Cache common responses where appropriate

### Risk 4: Limited Time to Build
**Risk:** 5 days is tight for full implementation

**Mitigation:**
- Focus on MVP features only
- Use rapid prototyping tools (Vercel, AI Studio if applicable)
- Leverage pre-built UI components (shadcn/ui)
- Cut non-essential features if needed
- Prioritize demo-ready flow over comprehensive features

---

## Future Enhancements (Post-Hackathon)

### V2 Features
- **Multi-player Mode:** Team negotiations with role assignments
- **Enterprise Integration:** Connect to actual SIEM/security tools for realistic scenarios
- **Advanced Analytics:** Track team performance over time
- **Custom Persona Builder:** Organizations can create threat actors based on real intelligence
- **Voice Mode:** Audio-based negotiations for even more realism
- **Compliance Modules:** GDPR, HIPAA, SOX implications training
- **Marketplace:** Community-contributed scenarios and personas

### Monetization Options
- Freemium: 3 free simulations, paid tiers for unlimited access
- Enterprise licensing: Team seats with admin dashboards
- Certification program: Issue credentials for completed training
- Integration with cyber insurance: Discount for trained organizations

---

## Submission Checklist

### Required Materials
- ✅ Text description (200 words) - Gemini 3 integration details
- ✅ Public project link (demo URL or AI Studio link)
- ✅ Public code repository (GitHub)
- ✅ 3-minute demonstration video

### Optional But Recommended
- ✅ README with setup instructions
- ✅ Architecture diagram
- ✅ Screenshots/GIFs of key features
- ✅ Ethical considerations document

### Pre-Submission Tests
- ✅ Demo URL works without login
- ✅ Repository is public
- ✅ Video is under 3 minutes
- ✅ All Devpost form fields completed
- ✅ Gemini 3 usage is clearly explained

---

## Conclusion

The Ransomware Negotiator Simulator represents a unique intersection of cutting-edge AI technology and critical cybersecurity needs. By leveraging Gemini 3's conversational capabilities and deep reasoning, we're creating a tool that doesn't just teach ransomware negotiation—it provides realistic, adaptive practice that can genuinely prepare organizations for one of the most stressful scenarios they may face.

This project stands out in the hackathon because it:
1. **Solves a real, expensive problem** (ransomware costs businesses billions)
2. **Uses Gemini 3 in a way competitors can't easily replicate** (nuanced persona roleplay)
3. **Creates an engaging, memorable demo** (judges can actually negotiate)
4. **Addresses a controversial topic professionally** (differentiates from typical hackathon projects)

With focused execution and clear ethical guardrails, this has strong potential for top-tier placement and real-world impact beyond the competition.

**Next Steps:** Begin implementation following the 5-day timeline, focusing on core MVP features that showcase Gemini 3's strengths.

---

**Document Owner:** Hackathon Team  
**Status:** Ready for Implementation  
**Priority:** P0 - Hackathon Submission