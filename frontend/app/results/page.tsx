"use client";

import { useState, useEffect } from "react";
import { getMatchHistory } from "@/lib/api";
import { toast } from "sonner";
import { Loader2, Filter, Calendar, TrendingUp, Download } from "lucide-react";
import { MatchCard } from "@/components/upload/match-card";
import type { Match } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { CircularProgress } from "@/components/ui/circular-progress";
import { SkillBadge } from "@/components/ui/skill-badge";

export default function ResultsPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [minScore, setMinScore] = useState(0);
  const [sortBy, setSortBy] = useState<"date" | "score">("date");
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const limit = 10;

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
      toast.error(error.response?.data?.detail || "Failed to load match history");
    } finally {
      setLoading(false);
    }
  };

  // Filter and sort matches
  const filteredMatches = matches
    .filter((m) => m.final_score >= minScore)
    .sort((a, b) => {
      if (sortBy === "score") {
        return b.final_score - a.final_score;
      }
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });

  // Count unique CVs processed (not total job matches)
  const uniqueCVs = new Set(filteredMatches.map(m => m.candidate_name || m.cv_filename || 'unknown'));
  const totalCVsProcessed = uniqueCVs.size;
  const avgScore = filteredMatches.reduce((sum, m) => sum + m.final_score, 0) / filteredMatches.length || 0;
  const highMatches = filteredMatches.filter((m) => m.final_score >= 75).length;

  return (
    <div className="max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent mb-2">
          Match Results & History
        </h1>
        <p className="text-gray-400">
          View and analyze your CV matching history with detailed insights
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-white/10 hover:border-purple-500/50 transition-all">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <Calendar className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">CVs Processed (max 5 jobs each)</p>
              <p className="text-3xl font-bold text-white">{totalCVsProcessed}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-white/10 hover:border-green-500/50 transition-all">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-500/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">High Matches (≥75%)</p>
              <p className="text-3xl font-bold text-white">{highMatches}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-white/10 hover:border-purple-500/50 transition-all">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <Filter className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Average Score</p>
              <p className="text-3xl font-bold text-white">{avgScore.toFixed(1)}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-white/10 mb-8">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-purple-400" />
            <span className="text-white font-medium">Filters</span>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-400">Min Score:</label>
            <select
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-white/10 focus:outline-none focus:border-purple-500 transition-all"
              aria-label="Minimum score filter"
            >
              <option value={0}>All (0%+)</option>
              <option value={50}>Medium (50%+)</option>
              <option value={75}>High (75%+)</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-400">Sort by:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as "date" | "score")}
              className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-white/10 focus:outline-none focus:border-purple-500 transition-all"
              aria-label="Sort results by"
            >
              <option value="date">Most Recent</option>
              <option value="score">Highest Score</option>
            </select>
          </div>
          
          <button className="ml-auto px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium transition-all flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Match List */}
      {loading && page === 0 ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
        </div>
      ) : filteredMatches.length === 0 ? (
        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-12 border border-white/10 text-center">
          <p className="text-gray-400 text-lg">No matches found</p>
          <p className="text-gray-500 text-sm mt-2">Try adjusting your filters or upload new CVs</p>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {filteredMatches.map((match) => (
              <div key={match.match_id}>
                <div className="text-xs text-gray-500 mb-2">
                  {formatDate(match.timestamp)}
                </div>
                <MatchCard match={match} />
              </div>
            ))}
          </div>

          {/* Load More */}
          {hasMore && (
            <div className="mt-8 text-center">
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={loading}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-xl font-semibold hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 transition-all inline-flex items-center gap-2 shadow-lg shadow-purple-500/30"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Loading...
                  </>
                ) : (
                  "Load More"
                )}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
