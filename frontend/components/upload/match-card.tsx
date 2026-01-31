"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Building2, MapPin, Briefcase, ArrowRight } from "lucide-react";
import type { Match } from "@/lib/types";
import { formatScore } from "@/lib/utils";
import { CircularProgress } from "@/components/ui/circular-progress";
import { SkillBadge } from "@/components/ui/skill-badge";

interface MatchCardProps {
  match: Match;
}

export function MatchCard({ match }: MatchCardProps) {
  const [expanded, setExpanded] = useState(false);

  // Color coding based on score
  const getScoreColor = (score: number) => {
    if (score >= 75) return "border-green-500 bg-green-500/5";
    if (score >= 50) return "border-yellow-500 bg-yellow-500/5";
    return "border-orange-500 bg-orange-500/5";
  };

  const getScoreBadgeColor = (score: number) => {
    if (score >= 75) return "bg-green-500/20 text-green-400 border-green-500/50";
    if (score >= 50) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/50";
    return "bg-orange-500/20 text-orange-400 border-orange-500/50";
  };

  return (
    <div className={`rounded-xl border-2 p-6 transition-all ${getScoreColor(match.final_score)}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-4 flex-1">
          {/* Avatar/Icon */}
          <div className="w-12 h-12 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-bold text-white mb-1 truncate">{match.job_title}</h3>
            <p className="text-sm text-gray-400">{match.company_name || match.company}</p>
          </div>
        </div>

        {/* Circular Score Badge */}
        <div className="flex-shrink-0">
          <CircularProgress score={match.final_score} size={64} strokeWidth={6} />
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-400 mb-4 line-clamp-2">
        {match.explanation || match.description || 'Exceptional portfolio demonstrating user-centric design principles and proficiency in Figma and prototyping.'}
      </p>

      {/* Location & Type Info */}
      <div className="flex items-center gap-3 text-gray-400 text-xs mb-4 flex-wrap">
        <div className="flex items-center gap-1">
          <MapPin className="w-3 h-3" />
          <span>{match.location_city || match.location}, {match.location_country || 'India'}</span>
        </div>
        <div className="flex items-center gap-1">
          <Briefcase className="w-3 h-3" />
          <span className="capitalize">{match.remote_type || match.job_type || 'on-site'}</span>
        </div>
        {match.seniority_level && (
          <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded capitalize">
            {match.seniority_level}
          </span>
        )}
      </div>

      {/* Skills Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {match.matched_skills && match.matched_skills.length > 0 ? (
          match.matched_skills.slice(0, 4).map((skill, idx) => (
            <SkillBadge key={idx} skill={skill} type="matched" />
          ))
        ) : (
          match.required_skills && match.required_skills.slice(0, 4).map((skill, idx) => (
            <SkillBadge key={idx} skill={skill} type="required" />
          ))
        )}
      </div>

      {/* View Details Button */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 group"
      >
        {expanded ? 'Hide Details' : 'View Details'}
        {expanded ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
        )}
      </button>

      {/* Expanded Content */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-white/10 space-y-4">
          {/* Agent Scores */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-gray-400 mb-1">Quality</p>
              <p className="text-lg font-bold text-white">{formatScore(match.parser_score)}</p>
            </div>
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 relative">
              <div className="absolute top-2 right-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              </div>
              <p className="text-xs text-blue-400 mb-1 font-semibold">ATS</p>
              <p className="text-lg font-bold text-blue-400">{formatScore(match.matcher_score)}</p>
            </div>
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-gray-400 mb-1">Matching</p>
              <p className="text-lg font-bold text-white">{formatScore(match.scorer_score)}</p>
            </div>
          </div>

          {/* Explanation */}
          {match.explanation && (
            <div>
              <h4 className="text-sm font-semibold text-white mb-2">🤖 AI Explanation</h4>
              <p className="text-gray-300 text-sm leading-relaxed">{match.explanation}</p>
            </div>
          )}

          {/* Job Description */}
          {match.description && (
            <div>
              <h4 className="text-sm font-semibold text-white mb-2">📋 Job Description</h4>
              <p className="text-gray-400 text-sm leading-relaxed">{match.description}</p>
            </div>
          )}

          {/* Required Skills */}
          {match.required_skills && match.required_skills.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-white mb-2">🎯 Required Skills</h4>
              <div className="flex flex-wrap gap-2">
                {match.required_skills.slice(0, 10).map((skill, idx) => (
                  <SkillBadge key={idx} skill={skill} type="required" />
                ))}
              </div>
            </div>
          )}

          {/* Preferred Skills */}
          {match.preferred_skills && match.preferred_skills.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-white mb-2">✨ Preferred Skills</h4>
              <div className="flex flex-wrap gap-2">
                {match.preferred_skills.slice(0, 5).map((skill, idx) => (
                  <SkillBadge key={idx} skill={skill} type="preferred" />
                ))}
              </div>
            </div>
          )}

          {/* Experience & Additional Info */}
          <div className="grid grid-cols-2 gap-3">
            {match.min_experience_years !== undefined && (
              <div className="bg-white/5 rounded-lg p-3">
                <p className="text-xs text-gray-400 mb-1">Experience Required</p>
                <p className="text-sm font-semibold text-white">
                  {match.min_experience_years}-{match.max_experience_years || match.min_experience_years + 3} years
                </p>
              </div>
            )}
            {match.posted_date && (
              <div className="bg-white/5 rounded-lg p-3">
                <p className="text-xs text-gray-400 mb-1">Posted Date</p>
                <p className="text-sm font-semibold text-white">{match.posted_date}</p>
              </div>
            )}
          </div>

          {/* Missing Skills Warning */}
          {match.missing_skills && match.missing_skills.length > 0 && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-yellow-400 mb-2">⚠️ Missing Skills</h4>
              <div className="flex flex-wrap gap-2">
                {match.missing_skills.slice(0, 5).map((skill, idx) => (
                  <SkillBadge key={idx} skill={skill} type="missing" />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
