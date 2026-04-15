// Types mirroring api/models/events.py and api/models/responses.py

export type SessionStatus =
  | 'created'
  | 'active'
  | 'clarification_needed'
  | 'completed'
  | 'failed'
  | 'expired';

export type MessageKind =
  | 'Human'
  | 'AI'
  | 'Tool'
  | 'ToolCall'
  | 'ClarifyWithUser'
  | 'ResearchQuestion'
  | 'System'
  | 'Other';

export type AgentName = 'scope' | 'supervisor' | 'research' | 'writer' | 'unknown';

export type EventType =
  | 'session_created'
  | 'session_started'
  | 'scope_start'
  | 'scope_clarification'
  | 'scope_brief'
  | 'supervisor_start'
  | 'supervisor_thinking'
  | 'supervisor_delegation'
  | 'research_start'
  | 'research_tool_call'
  | 'research_tool_output'
  | 'research_complete'
  | 'compression'
  | 'writer_start'
  | 'writer_complete'
  | 'final_report'
  | 'clarification_needed'
  | 'error'
  | 'user_message';

export interface ResearchEvent {
  event_type: EventType;
  session_id: string;
  title: string;
  content: string;
  metadata?: Record<string, unknown> | null;
  is_intermediate: boolean;
  timestamp: number;

  // Per-message metadata
  message_type?: MessageKind | null;
  message_subtype?: string | null;
  agent?: AgentName | null;
  tool_name?: string | null;
  tool_args?: Record<string, unknown> | null;
  tool_call_id?: string | null;
}

export interface WebSocketMessage {
  type: 'connected' | 'event' | 'error' | 'status' | 'complete' | 'ping';
  data: Record<string, unknown> & Partial<ResearchEvent>;
}

export interface Session {
  id: string;
  thread_id: string;
  status: SessionStatus;
  initial_query: string;
  clarification_response: string | null;
  research_brief: string | null;
  final_report: string | null;
  created_at: string;
  updated_at: string | null;
  completed_at: string | null;
  max_iterations: number;
  max_concurrent_researchers: number;
  user_name?: string | null;
  user_email?: string | null;
}

export type ApiKeysMap = Record<string, string>;

export interface CreateSessionRequest {
  query: string;
  max_iterations?: number;
  max_concurrent_researchers?: number;
  models?: Record<string, string>;
  api_keys?: ApiKeysMap;
  user_name?: string;
  user_email?: string;
}

export interface ModelInfo {
  name: string;
  label: string;
  provider: string;
  api_key_env: string;
}

export interface ModelsCatalogResponse {
  models: ModelInfo[];
  defaults: Record<string, string>;
  roles: string[];
}

export interface CreateSessionResponse {
  session: Session;
  websocket_url: string;
}

export interface StartResearchResponse {
  status: string;
  session_id: string;
  message: string;
}

export interface SessionListResponse {
  sessions: Session[];
  total: number;
  limit: number;
  offset: number;
}

export interface PersistedMessage {
  id: number;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown> | null;
}
