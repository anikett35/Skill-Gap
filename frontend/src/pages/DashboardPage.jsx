import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { FileSearch, TrendingUp, Target, Clock, ChevronRight, Plus } from "lucide-react";
import { analyzeApi } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { Card, CardHeader, CardBody, Badge, Skeleton, Button } from "../components/ui";
import { formatDistanceToNow } from "date-fns";

function StatCard({ icon: Icon, label, value, sub, color = "blue" }) {
  const colors = {
    blue: { bg: "bg-blue-50", icon: "text-blue-600", val: "text-blue-700" },
    green: { bg: "bg-green-50", icon: "text-green-600", val: "text-green-700" },
    yellow: { bg: "bg-yellow-50", icon: "text-yellow-600", val: "text-yellow-700" },
    purple: { bg: "bg-purple-50", icon: "text-purple-600", val: "text-purple-700" },
  }[color];

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{label}</p>
          <p className={`text-2xl font-bold ${colors.val}`}>{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
        </div>
        <div className={`${colors.bg} w-10 h-10 rounded-xl flex items-center justify-center`}>
          <Icon size={18} className={colors.icon} />
        </div>
      </div>
    </Card>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const { data: history, isLoading } = useQuery({
    queryKey: ["history"],
    queryFn: analyzeApi.history,
  });

  const analyses = history || [];
  const latestScore = analyses[0]?.result?.resume_score?.score;
  const avgScore = analyses.length
    ? Math.round(analyses.reduce((a, b) => a + (b.result?.resume_score?.score || 0), 0) / analyses.length)
    : 0;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            Good morning, {user?.name?.split(" ")[0]} 👋
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Here's your career progress at a glance
          </p>
        </div>
        <Button onClick={() => navigate("/analyze")}>
          <Plus size={16} />
          New Analysis
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={FileSearch}
          label="Total Analyses"
          value={analyses.length}
          sub="Career snapshots"
          color="blue"
        />
        <StatCard
          icon={TrendingUp}
          label="Latest Score"
          value={latestScore ? `${latestScore}/100` : "—"}
          sub="Resume match"
          color="green"
        />
        <StatCard
          icon={Target}
          label="Avg Score"
          value={avgScore ? `${avgScore}/100` : "—"}
          sub="Across all roles"
          color="yellow"
        />
        <StatCard
          icon={Clock}
          label="Learning Hours"
          value="0"
          sub="Track via roadmap"
          color="purple"
        />
      </div>

      {/* Recent analyses */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Recent Analyses</h2>
            <Button variant="ghost" size="sm" onClick={() => navigate("/history")}>
              View all <ChevronRight size={14} />
            </Button>
          </div>
        </CardHeader>
        <CardBody className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-4">
              {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-14 w-full" />)}
            </div>
          ) : analyses.length === 0 ? (
            <div className="flex flex-col items-center py-16 text-center">
              <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mb-3">
                <FileSearch size={20} className="text-gray-400" />
              </div>
              <p className="font-medium text-gray-700">No analyses yet</p>
              <p className="text-sm text-gray-400 mb-5">Upload your resume to get started</p>
              <Button size="sm" onClick={() => navigate("/analyze")}>
                <Plus size={14} /> Run first analysis
              </Button>
            </div>
          ) : (
            <div className="divide-y divide-gray-50">
              {analyses.slice(0, 6).map((a) => {
                const score = a.result?.resume_score?.score || 0;
                const scoreColor = score >= 70 ? "green" : score >= 50 ? "yellow" : "red";
                return (
                  <div
                    key={a.id}
                    onClick={() => navigate(`/roadmap?id=${a.id}`)}
                    className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 bg-blue-50 rounded-lg flex items-center justify-center">
                        <FileSearch size={16} className="text-blue-500" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {a.result?.candidate_name || "Candidate"} → {a.result?.job_title || "Role"}
                        </p>
                        <p className="text-xs text-gray-400">
                          {a.created_at ? formatDistanceToNow(new Date(a.created_at), { addSuffix: true }) : ""}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={scoreColor}>{score}/100</Badge>
                      <ChevronRight size={15} className="text-gray-300" />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
