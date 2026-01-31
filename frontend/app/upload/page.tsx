"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X, FileText, Loader2 } from "lucide-react";
import { matchCV } from "@/lib/api";
import { toast } from "sonner";
import type { Match } from "@/lib/types";
import { MatchCard } from "@/components/upload/match-card";
import { MatchSummary } from "@/components/upload/match-summary";

export default function UploadPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [useLLM, setUseLLM] = useState(false); // Default: rule-based (no Ollama)
  const [results, setResults] = useState<{ filename: string; matches: Match[] }[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
    },
    multiple: true,
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleMatch = async () => {
    if (files.length === 0) {
      toast.error("Please upload at least one CV");
      return;
    }

    setLoading(true);
    const newResults: { filename: string; matches: Match[] }[] = [];

    try {
      for (const file of files) {
        toast.info(`Processing ${file.name}...`);
        const response = await matchCV(file, 10, useLLM);
        
        newResults.push({
          filename: file.name,
          matches: response.matches,
        });

        toast.success(`Completed ${file.name}`);
      }

      setResults(newResults);
      setFiles([]);
      toast.success(`Processed ${files.length} CV(s) successfully!`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to process CVs");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Upload & Match CVs</h1>
        <p className="text-gray-400">
          Upload CVs and match against job descriptions using our 4-agent AI pipeline
        </p>
      </div>

      {/* LLM Toggle */}
      <div className="bg-navy-800/50 rounded-xl p-5 border border-navy-700 mb-6">
        <label className="flex items-start gap-4 cursor-pointer">
          <input
            type="checkbox"
            checked={useLLM}
            onChange={(e) => setUseLLM(e.target.checked)}
            className="mt-1 w-5 h-5 rounded border-navy-600 bg-navy-700 text-blue-500 focus:ring-2 focus:ring-blue-500 cursor-pointer"
          />
          <div className="flex-1">
            <div className="text-base font-semibold text-white mb-1">
              Enable AI Explanations (Ollama LLM)
            </div>
            {useLLM ? (
              <div className="text-sm text-yellow-400">
                ⚡ <strong>Requires Ollama running</strong> on port 11500. Generates detailed explanations but slower (~30-60s per CV).
              </div>
            ) : (
              <div className="text-sm text-green-400">
                ✓ <strong>Fast mode enabled</strong> - Rule-based matching only. No Ollama required (~5-10s per CV).
              </div>
            )}
          </div>
        </label>
      </div>

      {/* File Uploader */}
      <div className="bg-navy-800 rounded-2xl p-8 border border-white/10 mb-8">
        <h2 className="text-xl font-bold text-white mb-6">Batch CV Matching</h2>
        <p className="text-gray-400 mb-6">
          Upload one or more CVs to match against all jobs in the database
        </p>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
            isDragActive
              ? "border-blue-500 bg-blue-500/10"
              : "border-white/20 hover:border-white/40 hover:bg-white/5"
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-white font-medium mb-2">
            {isDragActive ? "Drop files here..." : "Drag and drop files here"}
          </p>
          <p className="text-sm text-gray-400">
            Limit 200MB per file • PDF, DOCX, TXT
          </p>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="mt-6">
            <p className="text-sm text-gray-400 mb-4">
              ✓ {files.length} file(s) uploaded
            </p>
            <div className="space-y-2">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between bg-white/5 rounded-lg p-4"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-blue-400" />
                    <div>
                      <p className="text-white font-medium">{file.name}</p>
                      <p className="text-xs text-gray-400">
                        {(file.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-red-400 transition-colors"
                    aria-label={`Remove ${file.name}`}
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Match Button */}
        <button
          onClick={handleMatch}
          disabled={loading || files.length === 0}
          className="w-full mt-6 bg-blue-500 text-white py-4 rounded-xl font-semibold hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing CVs...
            </>
          ) : (
            <>🔍 Match CVs</>
          )}
        </button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">Match Results</h2>
          {results.map((result, idx) => (
            <div key={idx} className="mb-12">
              <h3 className="text-xl font-semibold text-white mb-4">
                📄 {result.filename}
              </h3>
              
              <MatchSummary matches={result.matches} />

              <div className="mt-6">
                <h4 className="text-lg font-semibold text-white mb-4">Top Matches</h4>
                <div className="space-y-4">
                  {result.matches.slice(0, 5).map((match) => (
                    <MatchCard key={match.match_id} match={match} />
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
