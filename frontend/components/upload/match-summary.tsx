"use client";

import type { Match } from "@/lib/types";
import { formatScore } from "@/lib/utils";
import { TrendingUp, Award, Target } from "lucide-react";

interface MatchSummaryProps {
  matches: Match[];
}

export function MatchSummary({ matches }: MatchSummaryProps) {
  const total = matches.length;
  const highMatches = matches.filter((m) => m.final_score >= 75).length;
  const mediumMatches = matches.filter((m) => m.final_score >= 50 && m.final_score < 75).length;
  const avgScore = matches.reduce((sum, m) => sum + m.final_score, 0) / total;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="bg-navy-800 rounded-xl p-6 border border-green-500/30">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-green-500/20 rounded-lg">
            <Award className="w-6 h-6 text-green-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">High Matches (≥75%)</p>
            <p className="text-3xl font-bold text-white">{highMatches}</p>
          </div>
        </div>
      </div>

      <div className="bg-navy-800 rounded-xl p-6 border border-yellow-500/30">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-yellow-500/20 rounded-lg">
            <Target className="w-6 h-6 text-yellow-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Medium Matches (50-75%)</p>
            <p className="text-3xl font-bold text-white">{mediumMatches}</p>
          </div>
        </div>
      </div>

      <div className="bg-navy-800 rounded-xl p-6 border border-blue-500/30">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-500/20 rounded-lg">
            <TrendingUp className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Average Score</p>
            <p className="text-3xl font-bold text-white">{formatScore(avgScore)}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
