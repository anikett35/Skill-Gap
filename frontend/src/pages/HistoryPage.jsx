import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { FileSearch, ChevronRight, Calendar } from "lucide-react";
import { analyzeApi } from "../services/api";
import { Card, Badge, Skeleton, Button, EmptyState } from "../components/ui";
import { formatDistanceToNow, format } from "date-fns";

export default function HistoryPage() {
  const navigate = useNavigate();
  const { data: history, isLoading } = useQuery({
    queryKey: ["history"],
    queryFn: analyzeApi.history,
  });

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto space-y-3">
        {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-20 w-full" />)}
      </div>
    );
  }

  const analyses = history || [];

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Analysis History</h1>
          <p className="text-sm text-gray-500">{analyses.length} total analyses</p>
        </div>
        <Button onClick={() => navigate("/analyze")}>New Analysis</Button>
      </div>

      {analyses.length === 0 ? (
        <Card>
          <EmptyState
            icon={FileSearch}
            title="No analyses yet"
            description="Run your first analysis to see results here"
            action={<Button onClick={() => navigate("/analyze")}>Start analyzing</Button>}
          />
        </Card>
      ) : (
        <Card>
          <div className="divide-y divide-gray-50">
            {analyses.map((a) => {
              const score = a.result?.resume_score?.score || 0;
              const scoreColor = score >= 70 ? "green" : score >= 50 ? "yellow" : "red";
              const gaps = a.result?.skill_gaps?.length || 0;

              return (
                <div
                  key={a.id}
                  onClick={() => navigate(`/roadmap?id=${a.id}`)}
                  className="flex items-center gap-4 px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center shrink-0">
                    <FileSearch size={18} className="text-blue-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {a.result?.candidate_name || "Candidate"} → {a.result?.job_title || "Role"}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <Calendar size={11} className="text-gray-400" />
                      <span className="text-xs text-gray-400">
                        {a.created_at ? format(new Date(a.created_at), "MMM d, yyyy") : "—"}
                      </span>
                      <span className="text-gray-300">·</span>
                      <span className="text-xs text-gray-400">{gaps} skill gaps</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <Badge variant={scoreColor}>{score}/100</Badge>
                    <ChevronRight size={15} className="text-gray-300" />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      )}
    </div>
  );
}
