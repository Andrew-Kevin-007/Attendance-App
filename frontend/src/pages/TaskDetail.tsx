import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navigation from "@/components/Navigation";
import StatusBadge, { TaskStatus } from "@/components/StatusBadge";
import { tasksAPI, getUser } from "@/lib/api";
import {
  ArrowLeft,
  Clock,
  User,
  Calendar,
  Flag,
  Loader2,
  CheckCircle2,
  Play,
  Save,
  AlertCircle,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

// Normalize status for comparison
const normalizeStatus = (status: string): string => {
  return status.toLowerCase().replace(/\s+/g, "_").replace(/-/g, "_");
};

interface TaskData {
  id: number;
  title: string;
  description: string;
  priority: string;
  status: string;
  deadline: string;
  notes: string | null;
  updated_at: string | null;
  assigned_to: number;
  assignee_name: string;
}

const TaskDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const user = getUser();
  const [task, setTask] = useState<TaskData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  useEffect(() => {
    if (id) {
      fetchTask();
    }
  }, [id]);

  const fetchTask = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await tasksAPI.getById(Number(id));
      setTask(data);
      setNotes(data.notes || "");
    } catch (err: any) {
      setError(err.message || "Failed to load task");
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (newStatus: TaskStatus) => {
    if (!task) return;
    setUpdatingStatus(true);
    try {
      const res = await tasksAPI.update(task.id, { status: newStatus });
      setTask(res.task);
      toast.success(`Task marked as ${newStatus.replace("_", " ")}`);
    } catch (err: any) {
      toast.error(err.message || "Failed to update status");
    } finally {
      setUpdatingStatus(false);
    }
  };

  const saveNotes = async () => {
    if (!task) return;
    setSaving(true);
    try {
      const res = await tasksAPI.update(task.id, { notes });
      setTask(res.task);
      toast.success("Notes saved successfully");
    } catch (err: any) {
      toast.error(err.message || "Failed to save notes");
    } finally {
      setSaving(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case "high":
        return "text-red-600 bg-red-50 border-red-200";
      case "medium":
        return "text-amber-600 bg-amber-50 border-amber-200";
      default:
        return "text-emerald-600 bg-emerald-50 border-emerald-200";
    }
  };

  const isOverdue = task && new Date(task.deadline) < new Date() && normalizeStatus(task.status) !== "completed";
  const currentStatus = task ? normalizeStatus(task.status) : "pending";

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Loading task...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] p-6">
          <div className="max-w-md text-center">
            <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
            <h1 className="text-2xl font-semibold mb-2">Task Not Found</h1>
            <p className="text-muted-foreground mb-6">{error || "The task you're looking for doesn't exist or you don't have permission to view it."}</p>
            <button
              onClick={() => navigate("/my-tasks")}
              className="btn-apple-primary"
            >
              <ArrowLeft className="w-5 h-5 mr-1" />
              Back to My Tasks
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      <main className="pt-12">
        {/* Header */}
        <section className="py-8 border-b border-divider">
          <div className="container-apple">
            <button
              onClick={() => navigate(-1)}
              className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </button>

            <div className="flex flex-wrap items-start gap-4 mb-4">
              <StatusBadge status={task.status as TaskStatus} />
              <span className={cn(
                "text-xs font-medium px-3 py-1 rounded-full border capitalize",
                getPriorityColor(task.priority)
              )}>
                <Flag className="w-3 h-3 inline mr-1" />
                {task.priority} Priority
              </span>
              {isOverdue && (
                <span className="text-xs font-medium px-3 py-1 rounded-full bg-red-500 text-white">
                  Overdue
                </span>
              )}
            </div>

            <h1 className="text-3xl md:text-4xl font-semibold tracking-tight mb-2">
              {task.title}
            </h1>

            <div className="flex flex-wrap items-center gap-6 text-sm text-muted-foreground mt-4">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Due {new Date(task.deadline).toLocaleDateString("en-US", {
                  weekday: "short",
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                })}
              </div>
              <div className="flex items-center gap-2">
                <User className="h-4 w-4" />
                Assigned to {task.assignee_name}
              </div>
              {task.updated_at && (
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Updated {new Date(task.updated_at).toLocaleDateString()}
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Content */}
        <section className="py-12">
          <div className="container-apple">
            <div className="grid lg:grid-cols-3 gap-8">
              {/* Main Content */}
              <div className="lg:col-span-2 space-y-8">
                {/* Description */}
                <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl p-6">
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <FileText className="h-5 w-5 text-primary" />
                    Description
                  </h2>
                  <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                    {task.description || "No description provided."}
                  </p>
                </div>

                {/* Notes / Results */}
                <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl p-6">
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-500" />
                    Notes & Results
                  </h2>
                  <p className="text-sm text-muted-foreground mb-4">
                    Add your progress updates, notes, or final results here. This will be visible to your manager.
                  </p>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Enter your notes, progress updates, or final results..."
                    className="w-full min-h-[200px] rounded-xl border border-border bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"
                  />
                  <div className="flex justify-end mt-4">
                    <button
                      onClick={saveNotes}
                      disabled={saving}
                      className="inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-6 py-2.5 text-sm font-medium shadow hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-60 transition-all"
                    >
                      {saving ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="h-4 w-4" />
                          Save Notes
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Status Actions */}
                <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl p-6">
                  <h3 className="font-semibold mb-4">Update Status</h3>
                  
                  <div className="space-y-3">
                    {currentStatus === "pending" && (
                      <button
                        onClick={() => updateStatus("in_progress")}
                        disabled={updatingStatus}
                        className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 text-white px-4 py-3 text-sm font-medium shadow hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/30 disabled:opacity-60 transition-all"
                      >
                        {updatingStatus ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Play className="h-4 w-4" />
                        )}
                        Start Working
                      </button>
                    )}

                    {currentStatus === "in_progress" && (
                      <button
                        onClick={() => updateStatus("completed")}
                        disabled={updatingStatus}
                        className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 text-white px-4 py-3 text-sm font-medium shadow hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/30 disabled:opacity-60 transition-all"
                      >
                        {updatingStatus ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <CheckCircle2 className="h-4 w-4" />
                        )}
                        Mark Complete
                      </button>
                    )}

                    {currentStatus === "completed" && (
                      <div className="flex items-center justify-center gap-2 py-4 text-emerald-600">
                        <CheckCircle2 className="h-5 w-5" />
                        <span className="font-medium">Task Completed</span>
                      </div>
                    )}

                    {/* Revert options */}
                    {currentStatus === "in_progress" && (
                      <button
                        onClick={() => updateStatus("pending")}
                        disabled={updatingStatus}
                        className="w-full text-sm text-muted-foreground hover:text-foreground transition-colors py-2"
                      >
                        Move back to Pending
                      </button>
                    )}

                    {currentStatus === "completed" && (
                      <button
                        onClick={() => updateStatus("in_progress")}
                        disabled={updatingStatus}
                        className="w-full text-sm text-muted-foreground hover:text-foreground transition-colors py-2"
                      >
                        Reopen Task
                      </button>
                    )}
                  </div>
                </div>

                {/* Task Info */}
                <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl p-6">
                  <h3 className="font-semibold mb-4">Task Details</h3>
                  
                  <div className="space-y-4 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Task ID</span>
                      <span className="font-mono text-xs bg-muted px-2 py-1 rounded">#{task.id}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Priority</span>
                      <span className={cn(
                        "text-xs font-medium px-2 py-0.5 rounded capitalize",
                        task.priority === "high" ? "bg-red-100 text-red-700" :
                        task.priority === "medium" ? "bg-amber-100 text-amber-700" :
                        "bg-emerald-100 text-emerald-700"
                      )}>
                        {task.priority}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Deadline</span>
                      <span className={isOverdue ? "text-red-600 font-medium" : ""}>
                        {new Date(task.deadline).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Tips */}
                <div className="rounded-2xl border border-border/60 bg-blue-500/5 p-6">
                  <h3 className="font-semibold mb-3 text-blue-600">Tips</h3>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li>• Update your notes regularly with progress</li>
                    <li>• Mark task as "In Progress" when you start</li>
                    <li>• Add final results before marking complete</li>
                    <li>• Your manager can view all updates</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default TaskDetail;
