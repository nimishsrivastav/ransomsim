/**
 * Frontend Types - Matches backend API schemas
 */

// Organization profile enums
export type OrganizationSize = 'small' | 'medium' | 'large' | 'enterprise';
export type DataSensitivity = 'low' | 'medium' | 'high' | 'critical';
export type PersonaType = 'professional' | 'opportunist' | 'script_kiddie';

// Organization profile
export interface OrganizationProfile {
  size: OrganizationSize;
  industry: string;
  data_sensitivity: DataSensitivity;
}

// Scenario creation request
export interface ScenarioCreateRequest {
  organization: OrganizationProfile;
  persona_type: PersonaType;
  difficulty: number;
}

// Generated scenario
export interface Scenario {
  id: string;
  organization: OrganizationProfile;
  narrative: string;
  entry_vector: string;
  timeline: string;
  systems_affected: string[];
  data_at_risk: string[];
  ransom_amount: number;
  ransom_currency: string;
  deadline: string;
  created_at: string;
}

// Message types
export type MessageSender = 'user' | 'ai';

export interface Message {
  id: string;
  sender: MessageSender;
  content: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

// Negotiation session
export interface NegotiationSession {
  id: string;
  scenario_id?: string;
  persona_type: PersonaType;
  status: 'active' | 'completed' | 'expired';
  started_at: string;
  completed_at?: string;
  metadata: {
    pressure_level: number;
    concessions_made: number;
    user_tactics: string[];
  };
}

// Start negotiation request (matches backend NegotiationStart)
export interface StartNegotiationRequest {
  scenario_id: string;
  persona_type: PersonaType;
}

// Start negotiation response (matches backend NegotiationStartResponse)
export interface StartNegotiationResponse {
  session_id: string;
  initial_message: Message;
  deadline: string;
  client_token?: string;
}

// Send message request
export interface SendMessageRequest {
  content: string;
}

// Send message response (matches backend SendMessageResponse)
export interface SendMessageResponse {
  message_id: string;
  ai_response: Message;
  session_status: 'active' | 'completed' | 'expired';
  pressure_level: number;
}

// Conversation history response (matches backend ConversationHistory)
export interface ConversationHistoryResponse {
  session_id: string;
  messages: Message[];
  total_messages: number;
  session_status: 'active' | 'completed' | 'expired';
}

// Analysis types
export interface TacticalInsight {
  id: string;
  message_ref: string;
  insight_type: 'mistake' | 'success' | 'opportunity';
  analysis: string;
  improvement?: string;
}

export interface Mistake {
  description: string;
  severity: 'low' | 'medium' | 'high';
  consequence: string;
  better_approach: string;
}

export interface Success {
  description: string;
  impact: string;
  message_ref: string;
}

export interface Recommendation {
  skill: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
}

export interface BenchmarkData {
  user_payment: number;
  avg_payment: number;
  user_time: number;
  avg_time: number;
  user_concessions: number;
  avg_concessions: number;
}

export interface Analysis {
  session_id: string;
  performance_score: number;
  outcome: string;
  time_to_resolution: number;
  message_count: number;
  concessions_made: number;
  tactical_breakdown: TacticalInsight[];
  mistakes: Mistake[];
  successes: Success[];
  recommendations: Recommendation[];
  benchmarks: BenchmarkData;
  generated_at: string;
}

// Health check response
export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
  timestamp: string;
}

// API Error response
export interface APIError {
  detail: string;
  status_code?: number;
}

// Industry options for configuration
export const INDUSTRIES = [
  'Healthcare',
  'Finance',
  'Manufacturing',
  'Retail',
  'Technology',
  'Education',
  'Government',
  'Legal',
  'Energy',
  'Transportation',
] as const;

// Persona descriptions for UI
export const PERSONA_INFO: Record<PersonaType, { name: string; description: string; difficulty: string }> = {
  professional: {
    name: 'The Professional',
    description: 'Sophisticated APT group. Business-like, experienced, predictable but firm.',
    difficulty: 'Hard',
  },
  opportunist: {
    name: 'The Opportunist',
    description: 'Mid-tier gang. Emotional, erratic, susceptible to pressure tactics.',
    difficulty: 'Medium',
  },
  script_kiddie: {
    name: 'The Script Kiddie',
    description: 'Inexperienced attacker. Makes mistakes, easier to manipulate.',
    difficulty: 'Easy',
  },
};
