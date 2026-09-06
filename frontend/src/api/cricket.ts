import { fetchApi } from './client'

export interface CricketDetectionResponse {
  document_id: string
  is_scorecard: boolean
  confidence: number
  signals: string[]
  detected_teams: string[]
  summary: string
}

export interface CricketBattingPerformance {
  id: string
  player_name: string
  runs: number
  balls: number
  fours: number
  sixes: number
  strike_rate?: number | null
  dismissal?: string | null
  batting_position?: number | null
  source_page?: number | null
  source_text?: string | null
}

export interface CricketBowlingPerformance {
  id: string
  player_name: string
  overs: number
  maidens: number
  runs_conceded: number
  wickets: number
  economy?: number | null
  wides?: number | null
  no_balls?: number | null
  source_page?: number | null
  source_text?: string | null
}

export interface CricketExtras {
  wides: number
  no_balls: number
  byes: number
  leg_byes: number
  penalty: number
  total: number
}

export interface CricketInnings {
  id: string
  innings_number: number
  team: string
  total_runs: number
  wickets: number
  overs: number
  run_rate?: number | null
  extras: CricketExtras
  batting_performances: CricketBattingPerformance[]
  bowling_performances: CricketBowlingPerformance[]
}

export interface CricketValidation {
  is_valid: boolean
  warnings: string[]
  errors: string[]
}

export interface CricketMatch {
  id: string
  document_id: string
  team_1: string
  team_2: string
  venue?: string | null
  city?: string | null
  match_date?: string | null
  tournament?: string | null
  match_number?: string | null
  format?: string | null
  toss_winner?: string | null
  toss_decision?: string | null
  winner?: string | null
  result_text?: string | null
  player_of_match?: string | null
  innings: CricketInnings[]
  validation?: CricketValidation | null
  created_at: string
  updated_at: string
}

export interface CricketTopPerformer {
  player_name: string
  team: string
  metric_label: string
  metric_value: string
  subtext?: string | null
}

export interface CricketMatchStats {
  document_id: string
  match_id: string
  top_scorers: CricketTopPerformer[]
  top_wicket_takers: CricketTopPerformer[]
  highest_strike_rates: CricketTopPerformer[]
  best_economies: CricketTopPerformer[]
  total_match_runs: number
  total_match_wickets: number
  total_boundaries_fours: number
  total_boundaries_sixes: number
}

export interface CricketMatchSummary {
  document_id: string
  match_id: string
  title: string
  summary_text: string
  highlights: string[]
  winner?: string | null
  player_of_match?: string | null
  generated_at: string
}

export interface CricketPlayerStats {
  player_name: string
  matches_count: number
  innings_batted: number
  total_runs: number
  highest_score: number
  batting_average?: number | null
  batting_strike_rate?: number | null
  fifties: number
  hundreds: number
  total_fours: number
  total_sixes: number
  innings_bowled: number
  total_overs: number
  total_wickets: number
  runs_conceded: number
  bowling_average?: number | null
  bowling_economy?: number | null
  best_bowling_figures?: string | null
}

export async function detectCricketScorecard(documentId: string): Promise<CricketDetectionResponse> {
  return fetchApi<CricketDetectionResponse>(`/api/cricket/documents/${documentId}/detect`, {
    method: 'POST',
  })
}

export async function extractCricketScorecard(documentId: string): Promise<CricketMatch> {
  return fetchApi<CricketMatch>(`/api/cricket/documents/${documentId}/extract`, {
    method: 'POST',
  })
}

export async function getCricketScorecard(documentId: string): Promise<CricketMatch> {
  return fetchApi<CricketMatch>(`/api/cricket/documents/${documentId}`, {
    method: 'GET',
  })
}

export async function getCricketMatchStatistics(documentId: string): Promise<CricketMatchStats> {
  return fetchApi<CricketMatchStats>(`/api/cricket/documents/${documentId}/statistics`, {
    method: 'GET',
  })
}

export async function getCricketMatchSummary(documentId: string): Promise<CricketMatchSummary> {
  return fetchApi<CricketMatchSummary>(`/api/cricket/documents/${documentId}/summary`, {
    method: 'GET',
  })
}

export async function getCricketPlayerStatistics(playerName: string): Promise<CricketPlayerStats> {
  return fetchApi<CricketPlayerStats>(`/api/cricket/players/${encodeURIComponent(playerName)}/statistics`, {
    method: 'GET',
  })
}
