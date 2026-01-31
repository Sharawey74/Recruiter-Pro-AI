"use client";

import { useState, useEffect } from "react";
import { getMatchHistory } from "@/lib/api";
import { toast } from "sonner";
import { Loader2, Eye, X, CheckCircle, AlertCircle, XCircle, Download } from "lucide-react";
import type { Match } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { CircularProgress } from "@/components/ui/circular-progress";
import { SkillBadge } from "@/components/ui/skill-badge";

type StatusFilter = "all" | "accepted" | "review" | "rejected";

export default function ShortlistPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [statusOverrides, setStatusOverrides] = useState<Record<string, string>>({});

  useEffect(() => {
    setMounted(true);
    loadMatches();
    loadStatusOverrides();
  }, []);

  const loadMatches = async () => {
    setLoading(true);
    try {
      const response = await getMatchHistory(500, 0); // Load all recent matches (max 500)
      // Validate that we have an array of matches
      if (response && Array.isArray(response.matches)) {
        setMatches(response.matches);
      } else {
        console.error("Invalid response format:", response);
        toast.error("Invalid data format received");
        setMatches([]);
      }
    } catch (error: any) {
      console.error("Error loading matches:", error);
      toast.error(error.response?.data?.detail || "Failed to load matches");
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const loadStatusOverrides = () => {
    const saved = localStorage.getItem('candidateStatus');
    if (saved) {
      setStatusOverrides(JSON.parse(saved));
    }
  };

  const changeStatus = (matchId: string, newStatus: "accepted" | "review" | "rejected") => {
    const updated = { ...statusOverrides, [matchId]: newStatus };
    setStatusOverrides(updated);
    localStorage.setItem('candidateStatus', JSON.stringify(updated));
    toast.success(`Moved to ${newStatus}`);
  };

  const getEffectiveStatus = (match: Match): "accepted" | "review" | "rejected" => {
    // Check override first, then match.status, then calculate from score
    if (statusOverrides[match.match_id]) {
      return statusOverrides[match.match_id] as "accepted" | "review" | "rejected";
    }
    if (match.status) {
      return match.status;
    }
    // Fallback: calculate from score
    if (match.final_score >= 75) return "accepted";
    if (match.final_score >= 50) return "review";
    return "rejected";
  };

  // Group matches by candidate and take top 5 per candidate
  const groupedByCandidate = matches.reduce((acc, match) => {
    const candidateKey = match.candidate_name || match.cv_filename || 'Unknown';
    if (!acc[candidateKey]) {
      acc[candidateKey] = [];
    }
    acc[candidateKey].push(match);
    return acc;
  }, {} as Record<string, Match[]>);

  // Take only top 5 matches per candidate (sorted by score)
  const top5PerCandidate = Object.values(groupedByCandidate).flatMap(candidateMatches => 
    candidateMatches
      .sort((a, b) => b.final_score - a.final_score)
      .slice(0, 5)
  );

  const filteredMatches = top5PerCandidate.filter((m) => {
    const status = getEffectiveStatus(m);
    return statusFilter === "all" || status === statusFilter;
  });

  // Only calculate counts after component mounts to avoid hydration errors
  // Counts based on top 5 jobs per candidate
  const acceptedCount = mounted ? top5PerCandidate.filter((m) => getEffectiveStatus(m) === "accepted").length : 0;
  const reviewCount = mounted ? top5PerCandidate.filter((m) => getEffectiveStatus(m) === "review").length : 0;
  const rejectedCount = mounted ? top5PerCandidate.filter((m) => getEffectiveStatus(m) === "rejected").length : 0;

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
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent mb-2">
          Candidate Management
        </h1>
        <p className="text-gray-400">
          Review all uploaded resumes and their top 5 job matches. Auto-categorized by score with manual override.
        </p>
      </div>

      {/* Status Filter Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        <button
          onClick={() => setStatusFilter("all")}
          className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
            statusFilter === "all"
              ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg shadow-purple-500/30"
              : "bg-gray-700/50 text-gray-400 hover:bg-gray-700"
          }`}
        >
          All Candidates ({mounted ? top5PerCandidate.length : 0})
        </button>
        <button
          onClick={() => setStatusFilter("accepted")}
          className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
            statusFilter === "accepted"
              ? "bg-green-500 text-white shadow-lg shadow-green-500/30"
              : "bg-gray-700/50 text-gray-400 hover:bg-gray-700"
          }`}
        >
          <CheckCircle className="w-4 h-4" />
          Accepted ({acceptedCount})
        </button>
        <button
          onClick={() => setStatusFilter("review")}
          className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
            statusFilter === "review"
              ? "bg-yellow-500 text-white shadow-lg shadow-yellow-500/30"
              : "bg-gray-700/50 text-gray-400 hover:bg-gray-700"
          }`}
        >
          <AlertCircle className="w-4 h-4" />
          Review ({reviewCount})
        </button>
        <button
          onClick={() => setStatusFilter("rejected")}
          className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
            statusFilter === "rejected"
              ? "bg-red-500 text-white shadow-lg shadow-red-500/30"
              : "bg-gray-700/50 text-gray-400 hover:bg-gray-700"
          }`}
        >
          <XCircle className="w-4 h-4" />
          Rejected ({rejectedCount})
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-white/10 hover:border-green-500/50 transition-all">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-500/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Accepted Jobs (≥75%)</p>
              <p className="text-3xl font-bold text-white">{acceptedCount}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-white/10 hover:border-yellow-500/50 transition-all">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-500/20 rounded-lg">
              <AlertCircle className="w-6 h-6 text-yellow-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Review Jobs (50-74%)</p>
              <p className="text-3xl font-bold text-white">{reviewCount}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border border-white/10 hover:border-red-500/50 transition-all">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-500/20 rounded-lg">
              <XCircle className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Rejected Jobs (&lt;50%)</p>
              <p className="text-3xl font-bold text-white">{rejectedCount}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Candidates Grid */}
      {loading ? (
        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-12 border border-white/10 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-purple-500" />
          <p className="text-gray-400 mt-2">Loading candidates...</p>
        </div>
      ) : filteredMatches.length === 0 ? (
        <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-12 border border-white/10 text-center">
          <AlertCircle className="w-16 h-16 mx-auto text-gray-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-300 mb-2">No Candidates Found</h3>
          <p className="text-gray-400 max-w-md mx-auto">
            {statusFilter === "all" 
              ? "Upload resumes to see candidates here."
              : `No candidates in ${statusFilter} status.`}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredMatches.map((match) => {
            const effectiveStatus = getEffectiveStatus(match);
            return (
              <div
                key={match.match_id}
                className={`bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl p-6 border transition-all hover:shadow-lg ${
                  effectiveStatus === "accepted"
                    ? "border-green-500/50 hover:shadow-green-500/20"
                    : effectiveStatus === "review"
                    ? "border-yellow-500/50 hover:shadow-yellow-500/20"
                    : "border-red-500/50 hover:shadow-red-500/20"
                }`}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {effectiveStatus === "accepted" && (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      )}
                      {effectiveStatus === "review" && (
                        <AlertCircle className="w-5 h-5 text-yellow-400" />
                      )}
                      {effectiveStatus === "rejected" && (
                        <XCircle className="w-5 h-5 text-red-400" />
                      )}
                      <span className={`text-xs font-semibold uppercase ${
                        effectiveStatus === "accepted"
                          ? "text-green-400"
                          : effectiveStatus === "review"
                          ? "text-yellow-400"
                          : "text-red-400"
                      }`}>
                        {effectiveStatus}
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-white mb-1 truncate">
                      {String(match.candidate_name || match.cv_filename || 'Unknown Candidate')}
                    </h3>
                    <p className="text-sm text-gray-400 font-semibold truncate">{String(match.job_title || 'N/A')}</p>
                    <div className="flex items-center gap-2 mt-1 text-xs text-gray-500 truncate">
                      <span>{String(match.company_name || match.company || 'N/A')}</span>
                      <span>•</span>
                      <span>{String(match.location_city || 'Unknown')}, {String(match.location_country || '')}</span>
                      <span>•</span>
                      <span className="capitalize">{String(match.remote_type || match.job_type || 'on-site')}</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{formatDate(match.timestamp)}</p>
                  </div>
                  <div className="flex-shrink-0 ml-2">
                    <CircularProgress score={match.final_score} size={64} strokeWidth={6} />
                  </div>
                </div>

                {/* Scores */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="bg-white/5 rounded-lg p-3">
                    <p className="text-xs text-gray-400 mb-1">Quality</p>
                    <p className="text-lg font-bold text-white">{Math.round(match.parser_score)}%</p>
                  </div>
                  <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                    <p className="text-xs text-blue-400 mb-1 font-semibold">ATS</p>
                    <p className="text-lg font-bold text-blue-400">{Math.round(match.matcher_score)}%</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3">
                    <p className="text-xs text-gray-400 mb-1">Matching</p>
                    <p className="text-lg font-bold text-white">{Math.round(match.scorer_score)}%</p>
                  </div>
                </div>

                {/* Status Change Actions */}
                <div className="flex gap-2">
                  {effectiveStatus !== "accepted" && (
                    <button
                      onClick={() => changeStatus(match.match_id, "accepted")}
                      className="flex-1 px-3 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 border border-green-500/30 rounded-lg text-xs font-medium transition flex items-center justify-center gap-1"
                    >
                      <CheckCircle className="w-3 h-3" />
                      Accept
                    </button>
                  )}
                  {effectiveStatus !== "review" && (
                    <button
                      onClick={() => changeStatus(match.match_id, "review")}
                      className="flex-1 px-3 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 border border-yellow-500/30 rounded-lg text-xs font-medium transition flex items-center justify-center gap-1"
                    >
                      <Eye className="w-3 h-3" />
                      Review
                    </button>
                  )}
                  {effectiveStatus !== "rejected" && (
                    <button
                      onClick={() => changeStatus(match.match_id, "rejected")}
                      className="flex-1 px-3 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-lg text-xs font-medium transition flex items-center justify-center gap-1"
                    >
                      <X className="w-3 h-3" />
                      Reject
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
