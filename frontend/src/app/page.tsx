"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, CheckCircle2, ChevronRight, Loader2, Sparkles, FileText, AlertCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";

const PHASES = [
  "Initializing",
  "Data Ingestion",
  "Data Sanitization & PII Stripping",
  "LLM Engine (Pulse Report Generation)",
  "MCP Google Workspace Delivery",
  "Complete"
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [currentPhase, setCurrentPhase] = useState<string>("");
  const [percent, setPercent] = useState<number>(0);
  const [status, setStatus] = useState<"idle" | "processing" | "done" | "failed">("idle");
  const [error, setError] = useState<string>("");
  const [report, setReport] = useState<string>("");

  const startJob = async () => {
    try {
      setStatus("processing");
      setPercent(0);
      setCurrentPhase("Initializing");
      setError("");
      setReport("");
      const res = await fetch(`${API_BASE}/generate`, { method: "POST" });
      const data = await res.json();
      setJobId(data.job_id);
    } catch (err: unknown) {
      setStatus("failed");
      setError(err instanceof Error ? err.message : "Failed to connect to backend");
    }
  };

  useEffect(() => {
    if (!jobId || status === "done" || status === "failed") return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/status/${jobId}`);
        const data = await res.json();
        
        if (data.phase) setCurrentPhase(data.phase);
        if (data.percent) setPercent(data.percent);
        
        if (data.status === "failed") {
          setStatus("failed");
          setError(data.error || "Job failed internally");
        } else if (data.status === "done") {
          setStatus("done");
          const repRes = await fetch(`${API_BASE}/report/${jobId}`);
          const repData = await repRes.json();
          setReport(repData.report);
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId, status]);

  return (
    <main className="min-h-screen p-8 md:p-24 flex flex-col items-center">
      <div className="w-full max-w-4xl">
        <header className="mb-12 text-center">
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center justify-center p-3 mb-6 rounded-2xl bg-white/5 border border-white/10 shadow-xl backdrop-blur-sm"
          >
            <Sparkles className="w-8 h-8 text-blue-400 mr-3" />
            <h1 className="text-3xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
              Groww AI Agent
            </h1>
          </motion.div>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Automated Weekly Pulse Orchestrator. Fetches real-time Android reviews, sanitizes PII, and extracts key themes using a Groq Map-Reduce engine.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          <div className="md:col-span-4">
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-white/5">
                <motion.div 
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-500" 
                  initial={{ width: 0 }}
                  animate={{ width: `${percent}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              
              <div className="mb-8 mt-2">
                <h2 className="text-xl font-semibold mb-2">Control Panel</h2>
                <p className="text-sm text-slate-400">Trigger the 12-minute AI pipeline manually.</p>
              </div>

              <button
                onClick={startJob}
                disabled={status === "processing"}
                className={`w-full py-4 rounded-xl font-medium text-white flex items-center justify-center transition-all ${
                  status === "processing" 
                    ? "bg-white/10 cursor-not-allowed" 
                    : "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 hover:shadow-[0_0_20px_rgba(59,130,246,0.5)] shadow-lg"
                }`}
              >
                {status === "processing" ? (
                  <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Processing ({percent}%)</>
                ) : status === "done" ? (
                  <><Activity className="w-5 h-5 mr-2" /> Run Again</>
                ) : (
                  <><Activity className="w-5 h-5 mr-2" /> Generate Pulse Report</>
                )}
              </button>

              <div className="mt-8 space-y-4">
                {PHASES.map((phase, idx) => {
                  const isActive = currentPhase === phase && status === "processing";
                  const isPast = PHASES.indexOf(currentPhase) > idx || status === "done";
                  return (
                    <div key={phase} className={`flex items-center text-sm ${isActive ? "text-white" : isPast ? "text-slate-400" : "text-slate-600"}`}>
                      <div className="w-6 flex justify-center mr-3">
                        {isPast ? (
                          <CheckCircle2 className="w-4 h-4 text-green-400" />
                        ) : isActive ? (
                          <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                        ) : (
                          <div className="w-1.5 h-1.5 rounded-full bg-slate-700" />
                        )}
                      </div>
                      <span className={isActive ? "font-medium" : ""}>{phase}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="md:col-span-8">
            <AnimatePresence mode="wait">
              {status === "idle" && (
                <motion.div 
                  key="idle"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="bg-white/5 border border-white/10 rounded-3xl p-12 h-full flex flex-col items-center justify-center text-center backdrop-blur-xl"
                >
                  <FileText className="w-16 h-16 text-slate-600 mb-6" />
                  <h3 className="text-2xl font-semibold text-slate-300 mb-2">Ready to Orchestrate</h3>
                  <p className="text-slate-500 max-w-sm">Click the generate button to begin the data ingestion and LLM pipeline.</p>
                </motion.div>
              )}

              {status === "processing" && (
                <motion.div 
                  key="processing"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="bg-white/5 border border-white/10 rounded-3xl p-12 h-full flex flex-col items-center justify-center text-center backdrop-blur-xl"
                >
                  <div className="relative mb-8">
                    <div className="absolute inset-0 bg-blue-500 blur-[40px] opacity-20 rounded-full animate-pulse" />
                    <Loader2 className="w-16 h-16 text-blue-400 animate-spin relative z-10" />
                  </div>
                  <h3 className="text-2xl font-semibold text-slate-200 mb-4">{currentPhase}...</h3>
                  <p className="text-slate-400 max-w-sm text-sm leading-relaxed">
                    {currentPhase === "LLM Engine (Pulse Report Generation)" 
                      ? "The Map-Reduce engine is now active. This phase takes ~12 minutes to comply with Groq API limits. Please leave this page open."
                      : "The AI agent is securely processing the data pipeline."}
                  </p>
                </motion.div>
              )}

              {status === "failed" && (
                <motion.div 
                  key="failed"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="bg-red-950/20 border border-red-500/20 rounded-3xl p-12 h-full flex flex-col items-center justify-center text-center backdrop-blur-xl"
                >
                  <AlertCircle className="w-16 h-16 text-red-400 mb-6" />
                  <h3 className="text-2xl font-semibold text-red-200 mb-2">Pipeline Failed</h3>
                  <p className="text-red-400/80 max-w-sm mb-6">{error}</p>
                </motion.div>
              )}

              {status === "done" && (
                <motion.div 
                  key="done"
                  initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
                  className="bg-white/[0.02] border border-white/10 rounded-3xl overflow-hidden backdrop-blur-xl flex flex-col h-full"
                >
                  <div className="bg-white/5 border-b border-white/10 px-6 py-4 flex items-center justify-between">
                    <h3 className="font-medium flex items-center">
                      <CheckCircle2 className="w-4 h-4 text-green-400 mr-2" />
                      Final Pulse Report
                    </h3>
                    <span className="text-xs text-slate-400 bg-white/5 px-2 py-1 rounded-md">Also delivered to Google Docs & Gmail</span>
                  </div>
                  <div className="p-8 prose prose-invert max-w-none overflow-y-auto max-h-[600px] custom-scrollbar">
                    <ReactMarkdown>{report}</ReactMarkdown>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </main>
  );
}
