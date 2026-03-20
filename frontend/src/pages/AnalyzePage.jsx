import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  FileText, Briefcase, ChevronDown, Loader2,
  Sparkles, CheckCircle, AlertCircle, ArrowRight
} from "lucide-react";
import { analyzeApi } from "../services/api";
import { Card, CardHeader, CardBody, Button, Textarea, Badge } from "../components/ui";
import { RESUME_PRESETS, JD_PRESETS } from "../data/presets";

const STEPS = [
  "Extracting skills with NER...",
  "Running embedding similarity...",
  "Scoring skill gaps...",
  "Ordering learning path...",
  "Generating roadmap with AI...",
  "Finalizing analysis...",
];

function PresetDropdown({ presets, onSelect, label }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-xs text-blue-600 border border-blue-200 bg-blue-50 hover:bg-blue-100 px-2.5 py-1.5 rounded-lg transition-colors"
      >
        {label} <ChevronDown size={12} />
      </button>
      {open && (
        <div className="absolute right-0 top-8 z-30 w-56 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
          {presets.map((p, i) => (
            <button
              key={i}
              onClick={() => { onSelect(p); setOpen(false); }}
              className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors border-b border-gray-50 last:border-0"
            >
              <p className="font-medium">{p.name}</p>
              <p className="text-xs text-gray-400 truncate">{p.role}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function LoadingOverlay({ step }) {
  return (
    <div className="fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl border border-gray-200 shadow-xl p-10 max-w-sm w-full mx-4 text-center">
        <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-5">
          <Loader2 size={24} className="text-blue-600 animate-spin" />
        </div>
        <h3 className="font-semibold text-gray-900 mb-2">Analyzing your profile</h3>
        <p className="text-sm text-blue-600 font-medium mb-1">{STEPS[Math.min(step, STEPS.length - 1)]}</p>
        <p className="text-xs text-gray-400">This takes 15–30 seconds</p>
        <div className="mt-5 h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 rounded-full transition-all duration-1000"
            style={{ width: `${Math.round(((step + 1) / STEPS.length) * 100)}%` }}
          />
        </div>
        <div className="mt-4 space-y-1.5">
          {STEPS.map((s, i) => (
            <div key={i} className={`flex items-center gap-2 text-xs ${i <= step ? "text-gray-700" : "text-gray-300"}`}>
              {i < step ? (
                <CheckCircle size={13} className="text-green-500 shrink-0" />
              ) : i === step ? (
                <Loader2 size={13} className="text-blue-500 animate-spin shrink-0" />
              ) : (
                <div className="w-3 h-3 rounded-full border border-current shrink-0" />
              )}
              {s}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function AnalyzePage() {
  const navigate = useNavigate();
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState("");
  const [step, setStep] = useState(0);

  const mutation = useMutation({
    mutationFn: analyzeApi.run,
    onMutate: () => {
      let s = 0;
      const interval = setInterval(() => {
        s = Math.min(s + 1, STEPS.length - 2);
        setStep(s);
      }, 2500);
      mutation._interval = interval;
    },
    onSuccess: (data) => {
      clearInterval(mutation._interval);
      setStep(STEPS.length - 1);
      toast.success("Analysis complete!");
      setTimeout(() => navigate(`/roadmap?id=${data.id}`), 300);
    },
    onError: (err) => {
      clearInterval(mutation._interval);
      toast.error(err.response?.data?.detail || "Analysis failed. Check backend.");
    },
  });

  const handleRun = () => {
    if (!resumeText.trim() || !jdText.trim()) {
      toast.error("Please fill in both resume and job description.");
      return;
    }
    setStep(0);
    mutation.mutate({ resume_text: resumeText, jd_text: jdText });
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {mutation.isPending && <LoadingOverlay step={step} />}

      <div>
        <h1 className="text-xl font-bold text-gray-900">Analyze Resume</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Paste your resume and target job description for a full ML-powered skill gap analysis
        </p>
      </div>

      {/* Info banner */}
      <div className="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-xl px-4 py-3">
        <Sparkles size={16} className="text-blue-600 mt-0.5 shrink-0" />
        <p className="text-sm text-blue-700">
          <strong>ML Pipeline:</strong> NER extraction → embedding similarity → feature-based gap scoring → dependency graph ordering → LLM roadmap
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        {/* Resume */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText size={16} className="text-gray-500" />
                <span className="font-semibold text-gray-900 text-sm">Resume</span>
                {resumeText && <Badge variant="green">Filled</Badge>}
              </div>
              <PresetDropdown
                presets={RESUME_PRESETS}
                label="Load preset"
                onSelect={(p) => setResumeText(p.text)}
              />
            </div>
          </CardHeader>
          <CardBody>
            <Textarea
              placeholder="Paste your full resume here...&#10;&#10;Include: work experience, education, skills, projects"
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              className="h-80 font-mono text-xs leading-relaxed"
              hint={resumeText ? `${resumeText.length} chars` : ""}
            />
          </CardBody>
        </Card>

        {/* JD */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Briefcase size={16} className="text-gray-500" />
                <span className="font-semibold text-gray-900 text-sm">Job Description</span>
                {jdText && <Badge variant="green">Filled</Badge>}
              </div>
              <PresetDropdown
                presets={JD_PRESETS}
                label="Load preset"
                onSelect={(p) => setJdText(p.text)}
              />
            </div>
          </CardHeader>
          <CardBody>
            <Textarea
              placeholder="Paste the job description here...&#10;&#10;Include: requirements, responsibilities, must-have skills"
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              className="h-80 font-mono text-xs leading-relaxed"
              hint={jdText ? `${jdText.length} chars` : ""}
            />
          </CardBody>
        </Card>
      </div>

      <div className="flex items-center justify-end gap-3">
        <p className="text-sm text-gray-400">
          {!resumeText && "Add resume · "}
          {!jdText && "Add job description · "}
          {resumeText && jdText && "Ready to analyze"}
        </p>
        <Button
          size="lg"
          onClick={handleRun}
          disabled={mutation.isPending || !resumeText || !jdText}
        >
          {mutation.isPending ? (
            <><Loader2 size={16} className="animate-spin" /> Analyzing...</>
          ) : (
            <>Run Analysis <ArrowRight size={16} /></>
          )}
        </Button>
      </div>
    </div>
  );
}
