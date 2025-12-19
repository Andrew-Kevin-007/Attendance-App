import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Navigation from "@/components/Navigation";
import StatusBadge, { TaskStatus } from "@/components/StatusBadge";
import { tasksAPI, getUser } from "@/lib/api";
import { CheckCircle2, ArrowRight, Clock, Loader2, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

// Normalize status for comparison (handles both old "In Progress" and new "in_progress" formats)
const normalizeStatus = (status: string): string => {
  return status.toLowerCase().replace(/\s+/g, "_").replace(/-/g, "_");
};

const MyTasks = () => {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const user = getUser();

  useEffect(() => {
    fetchMyTasks();
  }, []);

  const fetchMyTasks = async () => {
    try {
      const data = await tasksAPI.getMyTasks();
      setTasks(data);
    } catch (err: any) {
      toast.error(err.message || "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  };

  const updateTaskStatus = async (taskId: number, newStatus: TaskStatus) => {
    try {
      await tasksAPI.update(taskId, { status: newStatus });
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
      );
      toast.success("Task updated");
    } catch (err: any) {
      toast.error(err.message || "Failed to update task");
    }
  };

  const pendingTasks = tasks.filter((t) => normalizeStatus(t.status) === "pending");
  const inProgressTasks = tasks.filter((t) => normalizeStatus(t.status) === "in_progress");
  const completedTasks = tasks.filter((t) => normalizeStatus(t.status) === "completed");

  const TaskCard = ({ task, index }: { task: typeof tasks[0]; index: number }) => (
    <div
      className="bg-surface rounded-3xl p-8 opacity-0 animate-fade-in-up"
      style={{ animationDelay: `${200 + index * 100}ms` }}
    >
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <StatusBadge status={task.status} />
        <span className={cn(
          "text-xs font-medium px-2 py-0.5 rounded-full",
          task.priority === "high" ? "bg-red-50 text-red-600" :
          task.priority === "medium" ? "bg-amber-50 text-amber-600" : 
          "bg-emerald-50 text-emerald-600"
        )}>
          {task.priority}
        </span>
      </div>

      <h3 className="text-xl font-semibold text-foreground mb-2">
        {task.title}
      </h3>
      <p className="text-muted-foreground text-sm mb-4 line-clamp-2">
        {task.description}
      </p>

      <div className="flex items-center gap-2 text-muted-foreground text-sm mb-6">
        <Clock className="w-4 h-4" />
        Due {new Date(task.deadline).toLocaleDateString("en-US", {
          month: "long",
          day: "numeric",
        })}
      </div>

      {/* View Details Link */}
      <Link
        to={`/tasks/${task.id}`}
        className="inline-flex items-center gap-1 text-sm text-primary hover:underline mb-4"
      >
        View Details & Update
        <ExternalLink className="w-3.5 h-3.5" />
      </Link>

      {/* Quick Actions */}
      {normalizeStatus(task.status) === "pending" && (
        <button
          onClick={() => updateTaskStatus(task.id, "in_progress")}
          className="btn-apple-primary w-full"
        >
          Start task
          <ArrowRight className="w-5 h-5 ml-1" />
        </button>
      )}
      {normalizeStatus(task.status) === "in_progress" && (
        <button
          onClick={() => updateTaskStatus(task.id, "completed")}
          className="btn-apple-primary w-full"
        >
          <CheckCircle2 className="w-5 h-5 mr-1" />
          Mark complete
        </button>
      )}
      {normalizeStatus(task.status) === "completed" && (
        <div className="flex items-center justify-center gap-2 text-emerald-600 font-medium py-3">
          <CheckCircle2 className="w-5 h-5" />
          Completed
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      <main className="pt-12">
        {/* Hero */}
        <section className="section-apple border-b border-divider">
          <div className="container-apple text-center">
            <p className="eyebrow mb-4 opacity-0 animate-fade-in">Assigned to you</p>
            <h1 className="headline-large mb-4 opacity-0 animate-fade-in-up delay-100">
              My Tasks
            </h1>
            <p className="subhead opacity-0 animate-fade-in-up delay-200">
              {tasks.length} tasks assigned to {user?.name || "you"}
            </p>
          </div>
        </section>

        {/* Stats */}
        <section className="py-16 bg-surface">
          <div className="container-apple">
            <div className="grid grid-cols-3 gap-8 text-center">
              {[
                { label: "Pending", value: pendingTasks.length },
                { label: "In Progress", value: inProgressTasks.length },
                { label: "Completed", value: completedTasks.length },
              ].map((stat, i) => (
                <div 
                  key={stat.label}
                  className="opacity-0 animate-fade-in-up"
                  style={{ animationDelay: `${100 + i * 100}ms` }}
                >
                  <p className="headline-medium text-foreground">{stat.value}</p>
                  <p className="caption mt-1">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Task Sections */}
        <section className="section-apple">
          <div className="container-apple">
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
              </div>
            ) : tasks.length === 0 ? (
              <div className="text-center py-20">
                <p className="text-muted-foreground">No tasks assigned yet</p>
              </div>
            ) : (
              <div className="space-y-16">
                {/* In Progress */}
                {inProgressTasks.length > 0 && (
                  <div>
                    <div className="text-center mb-12 opacity-0 animate-fade-in-up">
                      <p className="eyebrow mb-2 text-blue-600">Currently working on</p>
                      <h2 className="headline-small">In Progress</h2>
                    </div>
                    <div className="grid md:grid-cols-2 gap-6">
                      {inProgressTasks.map((task, i) => (
                        <TaskCard key={task.id} task={task} index={i} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Pending */}
                {pendingTasks.length > 0 && (
                  <div>
                    <div className="text-center mb-12 opacity-0 animate-fade-in-up">
                      <p className="eyebrow mb-2">Up next</p>
                      <h2 className="headline-small">Pending</h2>
                    </div>
                    <div className="grid md:grid-cols-2 gap-6">
                      {pendingTasks.map((task, i) => (
                        <TaskCard key={task.id} task={task} index={i + inProgressTasks.length} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Completed */}
                {completedTasks.length > 0 && (
                  <div>
                    <div className="text-center mb-12 opacity-0 animate-fade-in-up">
                      <p className="eyebrow mb-2 text-emerald-600">Done</p>
                      <h2 className="headline-small">Completed</h2>
                    </div>
                    <div className="grid md:grid-cols-2 gap-6">
                      {completedTasks.map((task, i) => (
                        <TaskCard key={task.id} task={task} index={i + inProgressTasks.length + pendingTasks.length} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default MyTasks;
