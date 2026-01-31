"use client";

import { useState, useEffect } from "react";
import { getMatchHistory, clearMatchHistory } from "@/lib/api";
import { toast } from "sonner";
import { Loader2, Calendar, TrendingUp, FileText, Trash2 } from "lucide-react";
import type { Match } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { CircularProgress } from "@/components/ui/circular-progress";
import { SkillBadge } from "@/components/ui/skill-badge";

export default function HistoryPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const limit = 20;

  useEffect(() => {
    loadMatches();
  }, [page]);

  const loadMatches = async () => {
    setLoading(true);
    try {
      const response = await getMatchHistory(limit, page * limit);
      
      if (response.matches.length < limit) {
        setHasMore(false);
      }

      setMatches((prev) => (page === 0 ? response.matches : [...prev, ...response.matches]));
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  // Count unique resumes uploaded (not total job matches)
  const uniqueResumes = new Set(matches.map(m => m.candidate_name || m.cv_filename || 'unknown'));
  const totalResumes = uniqueResumes.size;
  const avgScore = matches.reduce((sum, m) => sum + m.final_score, 0) / matches.length || 0;

  const getScoreColor = (score: number) => {
    if (score >= 75) return "text-green-500";
    if (score >= 50) return "text-yellow-500";
    return "text-red-500";
  };

  const getScoreBg = (score: number) => {
    if (score >= 75) return "bg-green-500/10 border-green-500/30";
    if (score >= 50) return "bg-yellow-500/10 border-yellow-500/30";
    return "bg-red-500/10 border-red-500/30";
  };

  return (
    <div className="max-w-7xl">
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent mb-2">
            Resume History
          </h1>
          <p className="text-gray-400">
            Complete history of all uploaded resumes and their match results
          </p>
        </div>
        <button
          onClick={async () => {
            if (confirm('Are you sure you want to clear all history? This action cannot be undone.')) {
              try {
                // Clear database
                const result = await clearMatchHistory();
                
                // Clear localStorage
                localStorage.removeItem('matchResults');
                localStorage.removeItem('latestAnalysis');
                localStorage.removeItem('selectedFileName');
                localStorage.removeItem('shortlist');
                localStorage.removeItem('candidateStatus');
                
                // Clear UI state
                setMatches([]);
                
                toast.success(`All history cleared: ${result.deleted_count} records deleted`);
              } catch (error: any) {
                console.error('Failed to clear history:', error);
                toast.error('Failed to clear history: ' + (error.response?.data?.detail || error.message));
              }
            }
          }}
          className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-lg text-sm font-medium transition flex items-center gap-2"
        >
          <Trash2 className="w-4 h-4" />
          Clear All History
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-white/10 hover:border-purple-500/50 transition-all">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <FileText className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Resumes Uploaded</p>
              <p className="text-3xl font-bold text-white">{totalResumes}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-white/10 hover:border-purple-500/50 transition-all">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Average Match Score</p>
              <p className="text-3xl font-bold text-white">{avgScore.toFixed(1)}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl border border-white/10 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Resume / Position
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Scores
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Match Score
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Date
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {loading && matches.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto text-purple-500" />
                    <p className="text-gray-400 mt-2">Loading history...</p>
                  </td>
                </tr>
              ) : matches.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-gray-400">
                    No history available. Upload resumes to see results.
                  </td>
                </tr>
              ) : (
                matches.map((match, idx) => (
                  <tr key={idx} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-white font-medium">{match.candidate_name || match.cv_filename || 'Unknown Candidate'}</p>
                        <p className="text-sm text-gray-400 font-semibold">{match.job_title}</p>
                        <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                          <span>{match.company_name || match.company || 'N/A'}</span>
                          <span>•</span>
                          <span>{match.location_city || 'Unknown'}, {match.location_country || ''}</span>
                          <span>•</span>
                          <span className="capitalize">{match.remote_type || match.job_type || 'on-site'}</span>
                        </div>
                        {match.candidate_name && match.cv_filename && (
                          <p className="text-xs text-gray-500 mt-1">{match.cv_filename}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2">
                        <div className="text-xs">
                          <span className="text-gray-400">Quality: </span>
                          <span className="text-white font-medium">{Math.round(match.parser_score)}%</span>
                        </div>
                        <div className="text-xs">
                          <span className="text-blue-400">ATS: </span>
                          <span className="text-blue-400 font-medium">{Math.round(match.matcher_score)}%</span>
                        </div>
                        <div className="text-xs">
                          <span className="text-gray-400">Match: </span>
                          <span className="text-white font-medium">{Math.round(match.scorer_score)}%</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className={`inline-flex items-center px-3 py-1 rounded-full border ${getScoreBg(match.final_score)}`}>
                        <span className={`text-sm font-bold ${getScoreColor(match.final_score)}`}>
                          {Math.round(match.final_score)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        <Calendar className="w-4 h-4" />
                        {formatDate(match.timestamp)}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Load More */}
        {hasMore && matches.length > 0 && (
          <div className="p-4 border-t border-white/10">
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={loading}
              className="w-full px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:bg-gray-600 rounded-lg text-white font-medium transition-all shadow-lg shadow-purple-500/20"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Loading...
                </span>
              ) : (
                'Load More'
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
