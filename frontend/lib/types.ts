export interface Match {
  match_id: string;
  job_id: string;
  job_title: string;
  // New structure fields
  company_name: string;
  location_city: string;
  location_country: string;
  remote_type: "on-site" | "hybrid" | "remote";
  employment_type: "full-time" | "part-time" | "contract" | "internship";
  seniority_level: "entry" | "mid" | "senior" | "lead" | "manager" | "executive";
  min_experience_years: number;
  max_experience_years: number;
  description?: string;
  required_skills?: string[];
  preferred_skills?: string[];
  posted_date?: string;
  // Legacy fields for backward compatibility
  company?: string;
  location?: string;
  job_type?: string;
  salary_range?: string;
  experience_level?: string;
  // Candidate fields
  candidate_name?: string;
  cv_filename?: string;
  // Scores and status
  final_score: number;
  parser_score: number;
  matcher_score: number;
  scorer_score: number;
  status: "accepted" | "review" | "rejected";
  explanation?: string;
  timestamp: string;
}

export interface MatchResponse {
  matches: Match[];
  cv_text?: string;
  processing_time?: number;
}

export interface Job {
  job_id: string;
  title: string;
  job_title?: string; // Legacy
  // New structure fields
  company_name: string;
  location_city: string;
  location_country: string;
  remote_type: "on-site" | "hybrid" | "remote";
  employment_type: "full-time" | "part-time" | "contract" | "internship";
  seniority_level: "entry" | "mid" | "senior" | "lead" | "manager" | "executive";
  min_experience_years: number;
  max_experience_years: number;
  description?: string;
  required_skills?: string[];
  preferred_skills?: string[];
  posted_date?: string;
  // Legacy fields for backward compatibility
  company?: string;
  location?: string;
  job_type?: string;
  salary_range?: string;
  experience_level?: string;
}

export interface JobsResponse {
  jobs: Job[];
  total: number;
}

export interface HistoryResponse {
  matches: Match[];
  total: number;
}

export interface HealthResponse {
  status: "healthy" | "unhealthy";
  version?: string;
}
