import { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import StatusBadge from "@/components/StatusBadge";
import { tasksAPI } from "@/lib/api";
import { Plus, ChevronRight, Search, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

// Normalize status for comparison
const normalizeStatus = (status: string): string => {
  return status.toLowerCase().replace(/\s+/g, "_").replace(/-/g, "_");
};

const Tasks = () => {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | "all">("all");

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const data = await tasksAPI.getAll();
      setTasks(data);
    } catch (err) {
      // Error handled by UI state
    } finally {
      setLoading(false);
    }
  };

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.assignee_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || normalizeStatus(task.status) === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const statusFilters: { value: string | "all"; label: string }[] = [
    { value: "all", label: "All" },
    { value: "pending", label: "Pending" },
    { value: "in_progress", label: "In Progress" },
    { value: "completed", label: "Completed" },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="pt-12">
        {/* Hero */}
        <section className="section-apple border-b border-divider">
          <div className="container-apple text-center">
            <h1 className="headline-large mb-4 opacity-0 animate-fade-in-up">
              Tasks
            </h1>
            <p className="subhead opacity-0 animate-fade-in-up delay-100">
              {tasks.length} tasks in your workflow
            </p>
          </div>
        </section>

        {/* Filters */}
        <section className="py-8 border-b border-divider sticky top-12 bg-background/95 backdrop-blur-xl z-40">
          <div className="container-apple">
            {loading ? (
              <div className="flex justify-center">
                <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
                {/* Search */}
                <div className="relative w-full sm:w-80">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search tasks"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input-apple w-full pl-11 h-12"
                  />
                </div>

                {/* Status Filter Pills */}
                <div className="flex items-center gap-2">
                  {statusFilters.map((filter) => (
                    <button
                      key={filter.value}
                      onClick={() => setStatusFilter(filter.value)}
                      className={cn(
                        "px-4 py-2 rounded-full text-sm font-medium transition-all duration-300",
                        statusFilter === filter.value
                          ? "bg-foreground text-background"
                          : "text-muted-foreground hover:text-foreground"
                      )}
                    >
                      {filter.label}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Task List */}
        <section className="section-apple">
          <div className="container-apple">
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
              </div>
            ) : filteredTasks.length === 0 ? (
              <div className="text-center py-20">
                <p className="text-muted-foreground">
                  {tasks.length === 0 ? "No tasks yet" : "No tasks match your filters"}
                </p>
              </div>
            ) : (
              <div className="grid gap-4">
                {filteredTasks.map((task, index) => (
                  <Link
                    key={task.id}
                    to={`/tasks/${task.id}`}
                    className="tile-apple flex items-center justify-between opacity-0 animate-fade-in-up hover:shadow-lg transition-shadow"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <StatusBadge status={task.status} />
                      <div className="flex flex-1 items-center gap-4">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg mb-1">{task.title}</h3>
                          <p className="text-sm text-muted-foreground">
                            Assigned to {task.assignee_name}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground">Due date</p>
                          <p className="font-medium">
                            {new Date(task.deadline).toLocaleDateString("en-US", {
                              month: "short",
                              day: "numeric",
                            })}
                          </p>
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-muted-foreground" />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Tasks;
