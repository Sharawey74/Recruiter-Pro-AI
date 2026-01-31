import axios from "axios";
import type {
  Match,
  MatchResponse,
  JobsResponse,
  HistoryResponse,
  HealthResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 150000, // Increased to 150 seconds (2.5 minutes) for 3000 jobs
});

export async function checkHealth(): Promise<HealthResponse> {
  const { data } = await api.get("/health");
  return data;
}

export async function getJobs(
  limit = 100,
  skip = 0,
  search?: string
): Promise<JobsResponse> {
  const { data } = await api.get("/jobs", {
    params: { limit, skip, search },
  });
  return data;
}

export async function matchCV(
  file: File,
  topK = 10,
  useLLM = false,
  useLangChain = false
): Promise<MatchResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await api.post(
    `/match?top_k=${topK}&explain=${useLLM}&use_llm=${useLLM}&use_langchain=${useLangChain}`, 
    formData, 
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return data;
}

export async function matchSingleJob(
  file: File,
  jobId: string
): Promise<Match> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await api.post("/match/single", formData, {
    params: { job_id: jobId },
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}

export async function getMatchHistory(
  limit?: number,
  skip = 0
): Promise<HistoryResponse> {
  const { data } = await api.get("/match/history", {
    params: { limit, skip },
  });
  return data;
}

export async function clearMatchHistory(): Promise<{ 
  success: boolean; 
  deleted_count: number; 
  message: string 
}> {
  const { data } = await api.delete("/match/history");
  return data;
}

export default api;
