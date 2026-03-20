import clsx from "clsx";

/* ── Button ─────────────────────────────────────────────────────────────────── */
const btnBase = `
  inline-flex items-center justify-center gap-2 font-medium rounded-lg
  transition-all duration-150 select-none focus-visible:outline-none
  focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
  disabled:opacity-50 disabled:pointer-events-none
`;

const btnVariants = {
  primary: "bg-blue-600 text-white hover:bg-blue-700 shadow-sm active:scale-[0.98]",
  secondary: "bg-white text-gray-700 border border-gray-200 hover:bg-gray-50 shadow-sm active:scale-[0.98]",
  ghost: "text-gray-600 hover:bg-gray-100 hover:text-gray-900",
  danger: "bg-red-50 text-red-600 border border-red-200 hover:bg-red-100",
};

const btnSizes = {
  sm: "h-8 px-3 text-sm",
  md: "h-9 px-4 text-sm",
  lg: "h-11 px-6 text-base",
};

export function Button({ variant = "primary", size = "md", className, children, ...props }) {
  return (
    <button
      className={clsx(btnBase, btnVariants[variant], btnSizes[size], className)}
      {...props}
    >
      {children}
    </button>
  );
}

/* ── Badge ─────────────────────────────────────────────────────────────────── */
const badgeVariants = {
  default: "bg-gray-100 text-gray-700",
  blue: "bg-blue-50 text-blue-700",
  green: "bg-green-50 text-green-700",
  yellow: "bg-yellow-50 text-yellow-700",
  red: "bg-red-50 text-red-700",
  purple: "bg-purple-50 text-purple-700",
};

export function Badge({ variant = "default", className, children }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
        badgeVariants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

/* ── Card ──────────────────────────────────────────────────────────────────── */
export function Card({ className, children, ...props }) {
  return (
    <div
      className={clsx(
        "bg-white rounded-xl border border-gray-200 shadow-sm",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className, children }) {
  return (
    <div className={clsx("px-6 py-4 border-b border-gray-100", className)}>
      {children}
    </div>
  );
}

export function CardBody({ className, children }) {
  return <div className={clsx("px-6 py-5", className)}>{children}</div>;
}

/* ── Skeleton ──────────────────────────────────────────────────────────────── */
export function Skeleton({ className }) {
  return (
    <div
      className={clsx(
        "animate-pulse bg-gray-200 rounded-md",
        className
      )}
    />
  );
}

export function SkeletonCard() {
  return (
    <Card className="p-6 space-y-3">
      <Skeleton className="h-5 w-40" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-10 w-32 mt-4" />
    </Card>
  );
}

/* ── Progress Bar ──────────────────────────────────────────────────────────── */
export function ProgressBar({ value = 0, max = 100, className, color = "blue" }) {
  const pct = Math.round((value / max) * 100);
  const colors = {
    blue: "bg-blue-500",
    green: "bg-green-500",
    yellow: "bg-yellow-500",
    red: "bg-red-500",
  };
  return (
    <div className={clsx("h-2 bg-gray-100 rounded-full overflow-hidden", className)}>
      <div
        className={clsx("h-full rounded-full transition-all duration-500", colors[color])}
        style={{ width: `${Math.min(pct, 100)}%` }}
      />
    </div>
  );
}

/* ── Input ─────────────────────────────────────────────────────────────────── */
export function Input({ className, label, error, ...props }) {
  return (
    <div className="space-y-1.5">
      {label && (
        <label className="block text-sm font-medium text-gray-700">{label}</label>
      )}
      <input
        className={clsx(
          "w-full h-10 px-3 text-sm border rounded-lg outline-none transition-all",
          "border-gray-200 bg-white text-gray-900 placeholder:text-gray-400",
          "focus:border-blue-500 focus:ring-2 focus:ring-blue-100",
          error && "border-red-400 focus:border-red-500 focus:ring-red-100",
          className
        )}
        {...props}
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}

/* ── Textarea ─────────────────────────────────────────────────────────────── */
export function Textarea({ className, label, hint, ...props }) {
  return (
    <div className="space-y-1.5">
      {label && (
        <div className="flex items-center justify-between">
          <label className="block text-sm font-medium text-gray-700">{label}</label>
          {hint && <span className="text-xs text-gray-400">{hint}</span>}
        </div>
      )}
      <textarea
        className={clsx(
          "w-full px-3 py-2.5 text-sm border rounded-lg outline-none transition-all resize-none",
          "border-gray-200 bg-white text-gray-900 placeholder:text-gray-400",
          "focus:border-blue-500 focus:ring-2 focus:ring-blue-100",
          className
        )}
        {...props}
      />
    </div>
  );
}

/* ── Divider ──────────────────────────────────────────────────────────────── */
export function Divider({ className }) {
  return <hr className={clsx("border-gray-100", className)} />;
}

/* ── Empty State ──────────────────────────────────────────────────────────── */
export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      {Icon && (
        <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mb-4">
          <Icon size={22} className="text-gray-400" />
        </div>
      )}
      <p className="font-semibold text-gray-900 mb-1">{title}</p>
      {description && <p className="text-sm text-gray-500 mb-5 max-w-xs">{description}</p>}
      {action}
    </div>
  );
}
