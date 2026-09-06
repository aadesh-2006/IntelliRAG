import React, { useState, useEffect } from 'react'
import {
  Trophy,
  Activity,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Search,
  Sparkles,
  Zap,
  Target,
  Flame,
  ShieldAlert,
  Loader2,
  RefreshCw,
  Award,
  Calendar,
  MapPin,
} from 'lucide-react'
import {
  CricketMatch,
  CricketDetectionResponse,
  CricketMatchStats,
  CricketMatchSummary,
  detectCricketScorecard,
  extractCricketScorecard,
  getCricketScorecard,
  getCricketMatchStatistics,
  getCricketMatchSummary,
} from '../api/cricket'
import { getDocuments, DocumentItem } from '../api/documents'

interface CricketScorecardViewProps {
  refreshTrigger?: number
}

export const CricketScorecardView: React.FC<CricketScorecardViewProps> = ({
  refreshTrigger = 0,
}) => {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [selectedDocId, setSelectedDocId] = useState<string>('')
  const [loadingDocs, setLoadingDocs] = useState(false)

  const [detecting, setDetecting] = useState(false)
  const [extracting, setExtracting] = useState(false)
  const [loadingMatch, setLoadingMatch] = useState(false)

  const [detection, setDetection] = useState<CricketDetectionResponse | null>(null)
  const [match, setMatch] = useState<CricketMatch | null>(null)
  const [stats, setStats] = useState<CricketMatchStats | null>(null)
  const [summary, setSummary] = useState<CricketMatchSummary | null>(null)

  const [activeInningsTab, setActiveInningsTab] = useState<number>(0)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDocuments()
  }, [refreshTrigger])

  useEffect(() => {
    if (selectedDocId) {
      setDetection(null)
      setMatch(null)
      setStats(null)
      setSummary(null)
      setError(null)
      checkExistingScorecard(selectedDocId)
    }
  }, [selectedDocId])

  const loadDocuments = async () => {
    try {
      setLoadingDocs(true)
      const res = await getDocuments()
      const readyDocs = res.items.filter((d) => d.status === 'PROCESSED' || d.status === 'READY')
      setDocuments(readyDocs)
      if (readyDocs.length > 0 && !selectedDocId) {
        setSelectedDocId(readyDocs[0].id)
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load documents')
    } finally {
      setLoadingDocs(false)
    }
  }

  const checkExistingScorecard = async (docId: string) => {
    try {
      setLoadingMatch(true)
      const matchData = await getCricketScorecard(docId)
      setMatch(matchData)
      loadAuxiliaryData(docId)
    } catch {
    } finally {
      setLoadingMatch(false)
    }
  }

  const loadAuxiliaryData = async (docId: string) => {
    try {
      const [statsRes, sumRes] = await Promise.all([
        getCricketMatchStatistics(docId).catch(() => null),
        getCricketMatchSummary(docId).catch(() => null),
      ])
      if (statsRes) setStats(statsRes)
      if (sumRes) setSummary(sumRes)
    } catch {
    }
  }

  const handleDetect = async () => {
    if (!selectedDocId) return
    try {
      setDetecting(true)
      setError(null)
      const res = await detectCricketScorecard(selectedDocId)
      setDetection(res)
    } catch (err: any) {
      setError(err?.message || 'Failed to detect cricket scorecard')
    } finally {
      setDetecting(false)
    }
  }

  const handleExtract = async () => {
    if (!selectedDocId) return
    try {
      setExtracting(true)
      setError(null)
      const matchRes = await extractCricketScorecard(selectedDocId)
      setMatch(matchRes)
      await loadAuxiliaryData(selectedDocId)
    } catch (err: any) {
      setError(err?.message || 'Failed to extract cricket scorecard')
    } finally {
      setExtracting(false)
    }
  }

  const selectedDoc = documents.find((d) => d.id === selectedDocId)
  const currentInnings = match && match.innings.length > activeInningsTab ? match.innings[activeInningsTab] : null

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-amber-500/20">
                <Trophy className="w-5 h-5" />
              </div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Cricket Scorecard AI</h2>
              <span className="px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-full">
                Module 13
              </span>
            </div>
            <p className="text-sm text-slate-400 max-w-2xl">
              Multimodal document intelligence for cricket scorecards. Detects match tables, extracts structured batting/bowling statistics, validates mathematical invariants, and synthesizes match intelligence.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleDetect}
              disabled={!selectedDocId || detecting || extracting}
              className="inline-flex items-center space-x-1.5 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs font-medium rounded-xl border border-slate-700 transition-colors shadow-sm"
            >
              {detecting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                  <span>Detecting...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 text-indigo-400" />
                  <span>Detect Scorecard</span>
                </>
              )}
            </button>
            <button
              onClick={handleExtract}
              disabled={!selectedDocId || extracting || detecting}
              className="inline-flex items-center space-x-1.5 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium rounded-xl shadow-lg shadow-indigo-500/20 transition-colors"
            >
              {extracting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Extracting AI...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  <span>Extract Scorecard</span>
                </>
              )}
            </button>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div className="flex-1 max-w-md">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Select Processed Document
            </label>
            <select
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-500 transition-colors"
            >
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.original_filename} ({doc.file_type})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-3 text-xs text-slate-400">
            {selectedDoc && (
              <span className="flex items-center space-x-1.5 bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                <span>{(selectedDoc.file_size / 1024).toFixed(1)} KB</span>
              </span>
            )}
            <button
              onClick={() => {
                loadDocuments()
                if (selectedDocId) checkExistingScorecard(selectedDocId)
              }}
              title="Refresh workspace"
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingDocs || loadingMatch ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-start space-x-3 text-rose-400 text-xs">
          <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {detection && !match && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div
                className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                  detection.is_scorecard
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                }`}
              >
                {detection.is_scorecard ? <CheckCircle2 className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">
                  {detection.is_scorecard ? 'Cricket Scorecard Detected' : 'Scorecard Confidence Low'}
                </h3>
                <p className="text-xs text-slate-400">{detection.summary}</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xs font-semibold text-slate-400">Detection Confidence</span>
              <p className="text-base font-bold text-indigo-400">{Math.round(detection.confidence * 100)}%</p>
            </div>
          </div>

          <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                detection.is_scorecard ? 'bg-indigo-500' : 'bg-amber-500'
              }`}
              style={{ width: `${Math.round(detection.confidence * 100)}%` }}
            />
          </div>

          <div className="pt-2">
            <h4 className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2">Detected Signals</h4>
            <div className="flex flex-wrap gap-1.5">
              {detection.signals.map((sig, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-300"
                >
                  {sig}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {match && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6 relative overflow-hidden">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b border-slate-800">
              <div>
                <div className="flex items-center space-x-2.5 mb-1.5">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    {match.format || 'Cricket Match'}
                  </span>
                  {match.tournament && (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-slate-800 text-slate-300">
                      {match.tournament}
                    </span>
                  )}
                </div>
                <h3 className="text-2xl font-extrabold text-white tracking-tight">
                  {match.team_1} <span className="text-slate-500 font-normal">vs</span> {match.team_2}
                </h3>
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-2">
                  {match.venue && (
                    <span className="flex items-center space-x-1">
                      <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{match.venue}</span>
                    </span>
                  )}
                  {match.match_date && (
                    <span className="flex items-center space-x-1">
                      <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{match.match_date}</span>
                    </span>
                  )}
                  {match.toss_winner && match.toss_decision && (
                    <span className="text-slate-400">
                      Toss: <strong className="text-slate-300">{match.toss_winner}</strong> elected to {match.toss_decision}
                    </span>
                  )}
                </div>
              </div>

              {match.result_text && (
                <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center space-x-3">
                  <Trophy className="w-6 h-6 text-emerald-400 shrink-0" />
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">Match Outcome</span>
                    <p className="text-sm font-bold text-white">{match.result_text}</p>
                    {match.player_of_match && (
                      <p className="text-xs text-emerald-300 mt-0.5">Player of the Match: {match.player_of_match}</p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {match.innings.length > 1 && (
              <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
                {match.innings.map((inn, idx) => (
                  <button
                    key={inn.id}
                    onClick={() => setActiveInningsTab(idx)}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
                      activeInningsTab === idx
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'bg-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                    }`}
                  >
                    <span>{inn.team}</span>
                    <span className="px-1.5 py-0.5 rounded bg-black/30 text-[10px]">
                      {inn.total_runs}/{inn.wickets} ({inn.overs} ov)
                    </span>
                  </button>
                ))}
              </div>
            )}

            {currentInnings && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Total Score</span>
                    <p className="text-2xl font-black text-white mt-1">
                      {currentInnings.total_runs}
                      <span className="text-sm font-normal text-slate-400">/{currentInnings.wickets}</span>
                    </p>
                  </div>
                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Overs</span>
                    <p className="text-2xl font-black text-white mt-1">{currentInnings.overs}</p>
                  </div>
                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Run Rate</span>
                    <p className="text-2xl font-black text-indigo-400 mt-1">{currentInnings.run_rate || 'N/A'}</p>
                  </div>
                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Extras Total</span>
                    <p className="text-2xl font-black text-amber-400 mt-1">{currentInnings.extras?.total || 0}</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                      <Target className="w-4 h-4 text-indigo-400" />
                      <span>Batting Scorecard — {currentInnings.team}</span>
                    </h4>
                  </div>

                  <div className="overflow-x-auto border border-slate-800 rounded-xl bg-slate-950/60">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-900/80 border-b border-slate-800 text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                        <tr>
                          <th className="py-3 px-4">Batter</th>
                          <th className="py-3 px-4">Dismissal</th>
                          <th className="py-3 px-3 text-right">R</th>
                          <th className="py-3 px-3 text-right">B</th>
                          <th className="py-3 px-3 text-right">4s</th>
                          <th className="py-3 px-3 text-right">6s</th>
                          <th className="py-3 px-4 text-right">SR</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {currentInnings.batting_performances.map((bat) => {
                          const isTop = bat.runs >= 50
                          return (
                            <tr
                              key={bat.id}
                              className={`hover:bg-slate-900/50 transition-colors ${
                                isTop ? 'bg-indigo-950/20' : ''
                              }`}
                            >
                              <td className="py-3 px-4 font-semibold text-white flex items-center space-x-1.5">
                                <span>{bat.player_name}</span>
                                {isTop && <Flame className="w-3.5 h-3.5 text-amber-400 shrink-0" />}
                              </td>
                              <td className="py-3 px-4 text-slate-400">{bat.dismissal || 'not out'}</td>
                              <td className="py-3 px-3 text-right font-bold text-white">{bat.runs}</td>
                              <td className="py-3 px-3 text-right text-slate-400">{bat.balls}</td>
                              <td className="py-3 px-3 text-right text-slate-300">{bat.fours}</td>
                              <td className="py-3 px-3 text-right text-slate-300">{bat.sixes}</td>
                              <td className="py-3 px-4 text-right font-medium text-indigo-400">
                                {bat.strike_rate || '0.00'}
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {currentInnings.bowling_performances.length > 0 && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                        <Activity className="w-4 h-4 text-cyan-400" />
                        <span>Bowling Performance</span>
                      </h4>
                    </div>

                    <div className="overflow-x-auto border border-slate-800 rounded-xl bg-slate-950/60">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-900/80 border-b border-slate-800 text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                          <tr>
                            <th className="py-3 px-4">Bowler</th>
                            <th className="py-3 px-3 text-right">O</th>
                            <th className="py-3 px-3 text-right">M</th>
                            <th className="py-3 px-3 text-right">R</th>
                            <th className="py-3 px-3 text-right">W</th>
                            <th className="py-3 px-4 text-right">Econ</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60">
                          {currentInnings.bowling_performances.map((bowl) => (
                            <tr key={bowl.id} className="hover:bg-slate-900/50 transition-colors">
                              <td className="py-3 px-4 font-semibold text-white">{bowl.player_name}</td>
                              <td className="py-3 px-3 text-right text-slate-300">{bowl.overs}</td>
                              <td className="py-3 px-3 text-right text-slate-400">{bowl.maidens}</td>
                              <td className="py-3 px-3 text-right text-slate-300">{bowl.runs_conceded}</td>
                              <td className="py-3 px-3 text-right font-bold text-cyan-400">{bowl.wickets}</td>
                              <td className="py-3 px-4 text-right font-medium text-slate-300">
                                {bowl.economy || '0.00'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {stats && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-bold text-white">Match Intelligence & Analytics</h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400">Top Scorers</span>
                  {stats.top_scorers.slice(0, 2).map((p, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-white truncate max-w-[130px]">{p.player_name}</span>
                      <span className="font-bold text-indigo-400">{p.metric_value}</span>
                    </div>
                  ))}
                </div>

                <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">Top Wicket Takers</span>
                  {stats.top_wicket_takers.slice(0, 2).map((p, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-white truncate max-w-[130px]">{p.player_name}</span>
                      <span className="font-bold text-cyan-400">{p.metric_value}</span>
                    </div>
                  ))}
                </div>

                <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">Highest Strike Rates</span>
                  {stats.highest_strike_rates.slice(0, 2).map((p, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-white truncate max-w-[130px]">{p.player_name}</span>
                      <span className="font-bold text-emerald-400">{p.metric_value}</span>
                    </div>
                  ))}
                </div>

                <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Best Economies</span>
                  {stats.best_economies.slice(0, 2).map((p, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-white truncate max-w-[130px]">{p.player_name}</span>
                      <span className="font-bold text-indigo-400">{p.metric_value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-slate-950/50 border border-slate-800 rounded-xl flex flex-wrap items-center justify-between gap-4 text-xs">
                <span className="text-slate-400">
                  Total Match Runs: <strong className="text-white">{stats.total_match_runs}</strong>
                </span>
                <span className="text-slate-400">
                  Total Match Wickets: <strong className="text-white">{stats.total_match_wickets}</strong>
                </span>
                <span className="text-slate-400">
                  Total Boundaries: <strong className="text-white">{stats.total_boundaries_fours} (4s)</strong> / <strong className="text-white">{stats.total_boundaries_sixes} (6s)</strong>
                </span>
              </div>
            </div>
          )}

          {summary && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-4">
              <div className="flex items-center space-x-2">
                <Award className="w-5 h-5 text-indigo-400" />
                <h3 className="text-base font-bold text-white">Synthesized Match Summary</h3>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/70 p-4 rounded-xl border border-slate-800">
                {summary.summary_text}
              </p>
            </div>
          )}

          {match.validation && (
            <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="text-slate-300 font-medium">
                  {match.validation.is_valid
                    ? 'Mathematical invariants validated (runs, overs, wickets consistent)'
                    : 'Validation discrepancies detected'}
                </span>
              </div>
              {match.validation.warnings.length > 0 && (
                <span className="text-amber-400 text-[11px]">
                  {match.validation.warnings.length} warning(s)
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
