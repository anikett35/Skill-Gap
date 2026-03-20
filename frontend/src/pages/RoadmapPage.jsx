import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
} from "recharts";
import {
  CheckCircle, Circle, ExternalLink, Download, AlertTriangle,
  Target, Zap, BarChart2, Map, BookOpen,
} from "lucide-react";
import toast from "react-hot-toast";
import { analyzeApi, progressApi, exportApi } from "../services/api";
import {
  Card, CardHeader, CardBody, Badge, Button,
  ProgressBar, Skeleton, EmptyState,
} from "../components/ui";

function ScoreRing({ score }) {
  const radius = 52;
  const circ = 2 * Math.PI * radius;
  const offset = circ - (score / 100) * circ;
  const color = score >= 70 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";
  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="130" height="130">
        <circle cx="65" cy="65" r={radius} fill="none" stroke="#f3f4f6" strokeWidth="10" />
        <circle cx="65" cy="65" r={radius} fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
          transform="rotate(-90 65 65)" style={{ transition: "stroke-dashoffset 1s ease" }} />
      </svg>
      <div className="absolute text-center">
        <p className="text-3xl font-bold" style={{ color }}>{score}</p>
        <p className="text-xs text-gray-400">/ 100</p>
      </div>
    </div>
  );
}

function SkillGapRow({ gap, index }) {
  const variant = gap.gap_score > 70 ? "red" : gap.gap_score > 40 ? "yellow" : "green";
  return (
    <div className="flex items-center gap-4 py-3 border-b border-gray-50 last:border-0">
      <div className="w-6 text-xs text-gray-300 font-mono text-center">{index + 1}</div>
      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-2 mb-1">
          <span className="text-sm font-medium text-gray-900">{gap.skill}</span>
          <Badge variant={variant}>{gap.gap_score.toFixed(0)}%</Badge>
          <Badge variant="default">{gap.category}</Badge>
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span>Required: <strong className="text-gray-600">{gap.required_level}</strong></span>
          <span>Current: <strong className="text-gray-600">{gap.candidate_level || "None"}</strong></span>
          <span>~{gap.estimated_days}d to close</span>
        </div>
        <ProgressBar value={100 - gap.gap_score} className="mt-2 h-1.5" color={variant} />
      </div>
    </div>
  );
}

function RoadmapModule({ module, index, completed, onToggle }) {
  return (
    <div className={`border rounded-xl p-5 transition-colors ${completed ? "border-green-200 bg-green-50" : "border-gray-200 bg-white"}`}>
      <div className="flex items-start gap-4">
        <button onClick={() => onToggle(index)}
          className={`mt-0.5 shrink-0 transition-colors ${completed ? "text-green-500" : "text-gray-300 hover:text-gray-400"}`}>
          {completed ? <CheckCircle size={20} /> : <Circle size={20} />}
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <span className="text-sm font-semibold text-gray-900">{index + 1}. {module.title}</span>
            <Badge variant="blue">{module.category}</Badge>
            <Badge variant="default">{module.duration}</Badge>
            {completed && <Badge variant="green">Done</Badge>}
          </div>
          <p className="text-sm text-gray-600 mb-2">{module.description}</p>
          {module.reason && (
            <div className="flex items-start gap-1.5 text-xs text-blue-600 bg-blue-50 rounded-lg px-3 py-2 mb-3">
              <Zap size={12} className="mt-0.5 shrink-0" /><span>{module.reason}</span>
            </div>
          )}
          <a href={module.resource_url} target="_blank" rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-600 hover:text-blue-700">
            <BookOpen size={12} />
            {module.resource_type === "course" ? "View Course" : "Read More"}
            <ExternalLink size={11} />
          </a>
        </div>
      </div>
    </div>
  );
}

const TABS = [
  { id: "gaps", label: "Skill Gaps", icon: AlertTriangle },
  { id: "roadmap", label: "Roadmap", icon: Map },
  { id: "charts", label: "Charts", icon: BarChart2 },
];

export default function RoadmapPage() {
  const [params] = useSearchParams();
  const analysisId = params.get("id");
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("gaps");

  const { data: result, isLoading } = useQuery({
    queryKey: ["analysis", analysisId],
    queryFn: () => analyzeApi.get(analysisId),
    enabled: !!analysisId,
  });

  const { data: progress } = useQuery({
    queryKey: ["progress", analysisId],
    queryFn: () => progressApi.get(analysisId),
    enabled: !!analysisId,
  });

  const progressMutation = useMutation({
    mutationFn: progressApi.update,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["progress", analysisId] }),
  });

  if (!analysisId) {
    return (
      <EmptyState icon={Target} title="No analysis selected"
        description="Run an analysis first, then come back here"
        action={<Button onClick={() => navigate("/analyze")}>Go to Analyze</Button>} />
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto space-y-4">
        {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-32 w-full" />)}
      </div>
    );
  }

  if (!result) return null;

  const completedSet = new Set(progress?.completed_modules || []);
  const progressPct = (result.learning_roadmap?.length || 0) > 0
    ? Math.round((completedSet.size / result.learning_roadmap.length) * 100) : 0;

  const handleToggle = (idx) => {
    progressMutation.mutate({ analysis_id: analysisId, module_index: idx, completed: !completedSet.has(idx) });
  };

  const handleExportPdf = async () => {
    try {
      const blob = await exportApi.roadmapPdf(analysisId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `roadmap-${analysisId.slice(0, 8)}.pdf`; a.click();
      URL.revokeObjectURL(url);
    } catch { toast.error("PDF export failed"); }
  };

  const radarData = (result.skill_gaps || []).slice(0, 7).map((g) => ({
    subject: g.skill.length > 10 ? g.skill.slice(0, 10) + "…" : g.skill,
    gap: g.gap_score, match: 100 - g.gap_score,
  }));

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{result.candidate_name} → {result.job_title}</h1>
          <p className="text-sm text-gray-500 mt-0.5">{result.ai_summary}</p>
        </div>
        <Button variant="secondary" size="sm" onClick={handleExportPdf}>
          <Download size={14} /> Export PDF
        </Button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="col-span-2 lg:col-span-1 flex flex-col items-center justify-center p-6">
          <p className="text-xs font-medium text-gray-500 mb-3">Resume Score</p>
          <ScoreRing score={result.resume_score?.score || 0} />
          <p className="text-xs text-gray-400 mt-2">{result.learner_level} level</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs text-gray-500 mb-1">Skill Gaps</p>
          <p className="text-2xl font-bold text-red-600">{result.skill_gaps?.length || 0}</p>
          <p className="text-xs text-gray-400">areas to improve</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs text-gray-500 mb-1">Time to Close</p>
          <p className="text-2xl font-bold text-yellow-600">{result.time_estimate?.total_weeks}w</p>
          <p className="text-xs text-gray-400">at 2h/day</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs text-gray-500 mb-1">Progress</p>
          <p className="text-2xl font-bold text-blue-600">{progressPct}%</p>
          <p className="text-xs text-gray-400">{completedSet.size}/{result.learning_roadmap?.length || 0} done</p>
          <ProgressBar value={progressPct} className="mt-2" />
        </Card>
      </div>

      {result.resume_score?.breakdown && (
        <Card>
          <CardHeader><h2 className="font-semibold text-gray-900 text-sm">Score Breakdown</h2></CardHeader>
          <CardBody>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(result.resume_score.breakdown).map(([k, v]) => (
                <div key={k}>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="text-gray-500 capitalize">{k.replace(/_/g, " ")}</span>
                    <span className="font-medium text-gray-700">{v}/40</span>
                  </div>
                  <ProgressBar value={v} max={40} />
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      <div className="border-b border-gray-200 flex gap-1">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === id ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}>
            <Icon size={14} />{label}
          </button>
        ))}
      </div>

      {activeTab === "gaps" && (
        <Card>
          <CardHeader><h2 className="font-semibold text-gray-900 text-sm">{result.skill_gaps?.length} Skill Gaps — ordered by priority</h2></CardHeader>
          <CardBody className="py-0">
            {(result.skill_gaps || []).map((gap, i) => <SkillGapRow key={i} gap={gap} index={i} />)}
          </CardBody>
        </Card>
      )}

      {activeTab === "roadmap" && (
        <div className="space-y-3">
          {(result.learning_roadmap || []).map((module, i) => (
            <RoadmapModule key={i} module={module} index={i} completed={completedSet.has(i)} onToggle={handleToggle} />
          ))}
        </div>
      )}

      {activeTab === "charts" && (
        <div className="grid lg:grid-cols-2 gap-5">
          <Card>
            <CardHeader><h3 className="text-sm font-semibold">Gap Radar</h3></CardHeader>
            <CardBody>
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#f3f4f6" />
                  <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: "#6b7280" }} />
                  <Radar name="Gap" dataKey="gap" stroke="#ef4444" fill="#ef4444" fillOpacity={0.15} strokeWidth={2} />
                  <Radar name="Match" dataKey="match" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.1} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>
          <Card>
            <CardHeader><h3 className="text-sm font-semibold">Gap Scores by Skill</h3></CardHeader>
            <CardBody>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={(result.skill_gaps || []).slice(0, 8)} layout="vertical" margin={{ left: 0 }}>
                  <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="skill" width={90} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v) => [`${v.toFixed(1)}%`, "Gap"]}
                    contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e5e7eb" }} />
                  <Bar dataKey="gap_score" radius={[0, 4, 4, 0]}>
                    {(result.skill_gaps || []).slice(0, 8).map((g, i) => (
                      <Cell key={i} fill={g.gap_score > 70 ? "#ef4444" : g.gap_score > 40 ? "#f59e0b" : "#22c55e"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>
        </div>
      )}
    </div>
  );
}
