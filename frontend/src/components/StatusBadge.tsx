import { cn } from "@/lib/utils";

type TaskStatus = "pending" | "in_progress" | "completed" | "Pending" | "In Progress" | "Completed";

interface StatusBadgeProps {
  status: TaskStatus;
  className?: string;
}

// Normalize status to lowercase with underscores
const normalizeStatus = (status: string): "pending" | "in_progress" | "completed" => {
  const lower = status.toLowerCase().replace(/\s+/g, "_").replace(/-/g, "_");
  if (lower === "in_progress" || lower === "inprogress") return "in_progress";
  if (lower === "completed") return "completed";
  return "pending";
};

const statusConfig: Record<"pending" | "in_progress" | "completed", { label: string; className: string }> = {
  pending: {
    label: "Pending",
    className: "badge-pending",
  },
  in_progress: {
    label: "In Progress",
    className: "badge-progress",
  },
  completed: {
    label: "Completed",
    className: "badge-completed",
  },
};

const StatusBadge = ({ status, className }: StatusBadgeProps) => {
  const normalized = normalizeStatus(status);
  const config = statusConfig[normalized];

  return (
    <span className={cn("badge-status", config?.className, className)}>
      {config?.label || status}
    </span>
  );
};

export default StatusBadge;
export type { TaskStatus };
