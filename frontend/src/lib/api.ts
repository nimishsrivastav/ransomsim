/**
 * API Client for RansomSim: AI‑Driven Ransomware Negotiation Training Backend
 */

import type {
  Scenario,
  ScenarioCreateRequest,
  StartNegotiationRequest,
  StartNegotiationResponse,
  SendMessageRequest,
  SendMessageResponse,
  ConversationHistoryResponse,
  Analysis,
  HealthResponse,
  APIError,
} from '@/types';

// API base URL - uses environment variable or defaults to localhost
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1 = `${API_BASE_URL}/api/v1`;

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_V1}${endpoint}`;

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = 'Unknown error';
    try {
      const errorData: APIError = await response.json();
      errorDetail = errorData.detail || errorDetail;
    } catch {
      errorDetail = response.statusText;
    }
    throw new ApiError(
      `API Error: ${response.status}`,
      response.status,
      errorDetail
    );
  }

  return response.json();
}

// ============================================================================
// Health Endpoints
// ============================================================================

/**
 * Check API health status
 */
export async function checkHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>('/health/');
}

/**
 * Check detailed health including Gemini connectivity
 */
export async function checkDetailedHealth(): Promise<HealthResponse & { services: Record<string, boolean> }> {
  return apiFetch('/health/detailed');
}

// ============================================================================
// Scenario Endpoints
// ============================================================================

/**
 * Generate a new ransomware scenario
 */
export async function generateScenario(
  request: ScenarioCreateRequest
): Promise<Scenario> {
  return apiFetch<Scenario>('/scenarios/generate', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Get an existing scenario by ID
 */
export async function getScenario(scenarioId: string): Promise<Scenario> {
  return apiFetch<Scenario>(`/scenarios/${scenarioId}`);
}

// ============================================================================
// Negotiation Endpoints
// ============================================================================

/**
 * Start a new negotiation session
 */
export async function startNegotiation(
  request: StartNegotiationRequest
): Promise<StartNegotiationResponse> {
  return apiFetch<StartNegotiationResponse>('/negotiations/start', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Send a message in an active negotiation
 */
export async function sendMessage(
  sessionId: string,
  request: SendMessageRequest,
  clientToken?: string
): Promise<SendMessageResponse> {
  const headers: HeadersInit = {};
  if (clientToken) {
    headers['X-Client-Token'] = clientToken;
  }
  return apiFetch<SendMessageResponse>(`/negotiations/${sessionId}/message`, {
    method: 'POST',
    headers,
    body: JSON.stringify(request),
  });
}

/**
 * Get full conversation history for a session
 */
export async function getConversationHistory(
  sessionId: string
): Promise<ConversationHistoryResponse> {
  return apiFetch<ConversationHistoryResponse>(`/negotiations/${sessionId}/history`);
}

/**
 * Mark a negotiation session as complete
 */
export async function completeNegotiation(
  sessionId: string,
  outcome?: string
): Promise<{ session_id: string; status: string }> {
  return apiFetch(`/negotiations/${sessionId}/complete`, {
    method: 'POST',
    body: JSON.stringify({ outcome }),
  });
}

// ============================================================================
// Analysis Endpoints
// ============================================================================

/**
 * Generate analysis for a completed session
 */
export async function generateAnalysis(sessionId: string): Promise<Analysis> {
  return apiFetch<Analysis>(`/analysis/${sessionId}`, {
    method: 'POST',
  });
}

/**
 * Get cached analysis for a session
 */
export async function getAnalysis(sessionId: string): Promise<Analysis> {
  return apiFetch<Analysis>(`/analysis/${sessionId}`);
}

// ============================================================================
// WebSocket Connection
// ============================================================================

/**
 * Create WebSocket connection for real-time chat
 * (Optional - for streaming responses)
 */
export function createNegotiationWebSocket(
  sessionId: string,
  onMessage: (data: SendMessageResponse) => void,
  onError?: (error: Event) => void,
  onClose?: () => void
): WebSocket {
  const wsUrl = API_BASE_URL.replace('http', 'ws');
  const ws = new WebSocket(`${wsUrl}/api/v1/negotiations/${sessionId}/ws`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error('Failed to parse WebSocket message:', e);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    onError?.(error);
  };

  ws.onclose = () => {
    console.log('WebSocket closed');
    onClose?.();
  };

  return ws;
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Format ransom amount for display
 */
export function formatRansom(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format timestamp for display
 */
export function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Calculate time remaining until deadline
 */
export function getTimeRemaining(deadline: string): {
  hours: number;
  minutes: number;
  expired: boolean;
} {
  const now = new Date();
  const deadlineDate = new Date(deadline);
  const diff = deadlineDate.getTime() - now.getTime();

  if (diff <= 0) {
    return { hours: 0, minutes: 0, expired: true };
  }

  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  return { hours, minutes, expired: false };
}
