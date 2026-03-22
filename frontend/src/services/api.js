import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 120000, // 2 minutes for long-running analysis
});

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle 401 globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (data) => api.post("/auth/login", data).then((r) => r.data),
  register: (data) => api.post("/auth/register", data).then((r) => r.data),
};

// ── Analysis ──────────────────────────────────────────────────────────────────
export const analyzeApi = {
  run: (data) => api.post("/analyze", data).then((r) => r.data),
  history: () => api.get("/analyze/history").then((r) => r.data),
  get: (id) => api.get(`/analyze/${id}`).then((r) => r.data),
};

// ── Chat ─────────────────────────────────────────────────────────────────────
export const chatApi = {
  send: (data) => api.post("/chat", data).then((r) => r.data),
  history: (analysisId) =>
    api.get("/chat/history", { params: { analysis_id: analysisId } }).then((r) => r.data),
};

// ── Progress ─────────────────────────────────────────────────────────────────
export const progressApi = {
  get: (analysisId) => api.get(`/progress/${analysisId}`).then((r) => r.data),
  update: (data) => api.post("/progress/update", data).then((r) => r.data),
};

// ── Export ───────────────────────────────────────────────────────────────────
export const exportApi = {
  roadmapPdf: (analysisId) =>
    api
      .get(`/export/roadmap/${analysisId}/pdf`, { responseType: "blob" })
      .then((r) => r.data),
};
