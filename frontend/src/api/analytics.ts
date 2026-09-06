import { fetchApi } from './client';

export type AnalyticsIntent =
  | 'DOCUMENT_COUNT'
  | 'DOCUMENT_BREAKDOWN'
  | 'DOCUMENT_DATE_RANGE'
  | 'DOCUMENT_STATUS_ANALYSIS'
  | 'STORAGE_ANALYSIS'
  | 'EXPIRATION_ANALYSIS'
  | 'REMINDER_ANALYSIS'
  | 'CRICKET_BATTING_ANALYSIS'
  | 'CRICKET_BOWLING_ANALYSIS'
  | 'CRICKET_MATCH_ANALYSIS'
  | 'UNSUPPORTED';

export interface DateRangeFilter {
  start_date?: string;
  end_date?: string;
  timeframe_label?: string;
}

export interface AnalyticsQueryRequest {
  query: string;
  intent?: AnalyticsIntent;
  date_range?: DateRangeFilter;
  filters?: Record<string, unknown>;
}

export interface AnalyticsResult {
  query: string;
  intent: AnalyticsIntent;
  metric: string;
  filters: Record<string, unknown>;
  group_by?: string | null;
  date_range?: Record<string, unknown> | null;
  data: Array<Record<string, unknown>>;
  total?: number | null;
  unit?: string | null;
  generated_at: string;
  execution_time_ms: number;
}

export interface AnalyticsQueryResponse {
  query: string;
  intent: AnalyticsIntent;
  metric: string;
  structured_result: AnalyticsResult;
  answer: string;
  model_info?: Record<string, unknown> | null;
  execution_time_ms: number;
}

export async function queryAnalytics(request: AnalyticsQueryRequest): Promise<AnalyticsQueryResponse> {
  return fetchApi<AnalyticsQueryResponse>('/analytics/query', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}
