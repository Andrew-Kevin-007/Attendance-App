import { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import StatusBadge from "@/components/StatusBadge";
import {
  ListTodo,
  CheckCircle2,
  Clock,
  TrendingUp,
  Users,
  AlertCircle,
  ChevronRight,
  ArrowRight,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { Link } from "react-router-dom";
import { attendanceAPI } from "@/lib/attendance";
import { getUser, tasksAPI } from "@/lib/api";
import { formatElapsedTime } from "@/lib/attendance";

type TaskStats = Awaited<ReturnType<typeof tasksAPI.getStats>>;

const Dashboard = () => {
  const currentUser = getUser();
  const isAdmin = currentUser?.role === "admin";
  const canViewAttendance = currentUser?.role === "admin" || currentUser?.role === "manager";
  
  // Task stats
  const [stats, setStats] = useState<TaskStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState("");

  // Attendance summary
  const [attnLoading, setAttnLoading] = useState(false);
  const [attnError, setAttnError] = useState<string>("");
  const [attnSummary, setAttnSummary] = useState<null | Awaited<ReturnType<typeof attendanceAPI.todaySummary>>>(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await tasksAPI.getStats();
        setStats(data);
      } catch (e: any) {
        setStatsError(e?.message || "Failed to load stats");
      } finally {
        setStatsLoading(false);
      }
    };
    loadStats();
  }, []);

  useEffect(() => {
    if (!canViewAttendance) return;
    const loadAttendance = async () => {
      setAttnLoading(true);
      try {
        const data = await attendanceAPI.todaySummary();
        setAttnSummary(data);
      } catch (e: any) {
        setAttnError(e?.message || "Failed to load attendance");
      } finally {
        setAttnLoading(false);
      }
    };
    loadAttendance();
  }, [canViewAttendance]);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      <main className="pt-12">
        {/* Hero Header */}
        <section className="py-16 md:py-20 border-b border-divider">
          <div className="container-apple">
            <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
              <div className="opacity-0 animate-fade-in-up">
                <p className="eyebrow mb-3">Dashboard</p>
                <h1 className="headline-large">Overview</h1>
                <p className="subhead mt-2">
                  Your productivity summary at a glance.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Key Metrics */}
        <section className="py-12 bg-surface">
          <div className="container-apple">
            {statsLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
              </div>
            ) : statsError ? (
              <div className="p-4 rounded-xl bg-destructive/10 text-destructive text-sm flex items-center gap-2">
                <AlertCircle className="w-4 h-4" /> {statsError}
              </div>
            ) : (
              <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                <div className="rounded-2xl border border-divider bg-background p-5 opacity-0 animate-fade-in-up delay-100">
                  <div className="flex items-center justify-between mb-3">
                    <ListTodo className="w-5 h-5 text-blue-500" />
                  </div>
                  <p className="text-3xl font-semibold">{stats?.total ?? 0}</p>
                  <p className="text-sm text-muted-foreground mt-1">Total Tasks</p>
                </div>
                
                <div className="rounded-2xl border border-divider bg-background p-5 opacity-0 animate-fade-in-up delay-200">
                  <div className="flex items-center justify-between mb-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                  </div>
                  <p className="text-3xl font-semibold text-emerald-600">{stats?.completed ?? 0}</p>
                  <p className="text-sm text-muted-foreground mt-1">Completed</p>
                </div>
                
                <div className="rounded-2xl border border-divider bg-background p-5 opacity-0 animate-fade-in-up delay-300">
                  <div className="flex items-center justify-between mb-3">
                    <Clock className="w-5 h-5 text-amber-500" />
                  </div>
                  <p className="text-3xl font-semibold text-amber-600">{stats?.in_progress ?? 0}</p>
                  <p className="text-sm text-muted-foreground mt-1">In Progress</p>
                </div>
                
                <div className="rounded-2xl border border-divider bg-background p-5 opacity-0 animate-fade-in-up delay-400">
                  <div className="flex items-center justify-between mb-3">
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                  </div>
                  <p className="text-3xl font-semibold text-red-600">{stats?.overdue ?? 0}</p>
                  <p className="text-sm text-muted-foreground mt-1">Overdue</p>
                </div>
                
                <div className="rounded-2xl border border-divider bg-background p-5 opacity-0 animate-fade-in-up delay-500">
                  <div className="flex items-center justify-between mb-3">
                    <TrendingUp className="w-5 h-5 text-purple-500" />
                  </div>
                  <p className="text-3xl font-semibold text-purple-600">{stats?.completion_rate ?? 0}%</p>
                  <p className="text-sm text-muted-foreground mt-1">Completion Rate</p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Main Content */}
        <section className="py-16">
          <div className="container-apple space-y-8">
            {canViewAttendance && (
              <div className="bg-background rounded-3xl p-6 md:p-8 opacity-0 animate-fade-in-up">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-xl font-semibold text-foreground">Today's Attendance</h2>
                    <p className="text-sm text-muted-foreground mt-1">
                      {attnSummary?.date ? new Date(attnSummary.date).toLocaleDateString() : ""}
                    </p>
                  </div>
                  <Link to="/employees" className="link-apple text-sm flex items-center gap-1">
                    Manage employees
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>

                {attnError && (
                  <div className="p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2 mb-4">
                    <AlertCircle className="w-4 h-4" /> {attnError}
                  </div>
                )}

                <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
                  <div className="rounded-2xl border border-divider p-4">
                    <p className="text-xs text-muted-foreground mb-1">Users</p>
                    <p className="text-2xl font-semibold">{attnSummary?.totals.users ?? (attnLoading ? "—" : 0)}</p>
                  </div>
                  <div className="rounded-2xl border border-divider p-4">
                    <p className="text-xs text-muted-foreground mb-1">Registered</p>
                    <p className="text-2xl font-semibold">{attnSummary?.totals.registered ?? (attnLoading ? "—" : 0)}</p>
                  </div>
                  <div className="rounded-2xl border border-divider p-4">
                    <p className="text-xs text-muted-foreground mb-1">Present</p>
                    <p className="text-2xl font-semibold text-emerald-500">{attnSummary?.totals.present ?? (attnLoading ? "—" : 0)}</p>
                  </div>
                  <div className="rounded-2xl border border-divider p-4">
                    <p className="text-xs text-muted-foreground mb-1">Checked Out</p>
                    <p className="text-2xl font-semibold text-blue-500">{attnSummary?.totals.checkedOut ?? (attnLoading ? "—" : 0)}</p>
                  </div>
                  <div className="rounded-2xl border border-divider p-4">
                    <p className="text-xs text-muted-foreground mb-1">Absent</p>
                    <p className="text-2xl font-semibold text-red-500">{attnSummary?.totals.absent ?? (attnLoading ? "—" : 0)}</p>
                  </div>
                </div>

                <div className="rounded-2xl border border-divider overflow-hidden">
                  <div className="grid grid-cols-12 px-4 py-2 text-xs text-muted-foreground bg-surface/60">
                    <div className="col-span-3">Employee</div>
                    <div className="col-span-2">Email</div>
                    <div className="col-span-1">Registered</div>
                    <div className="col-span-2 text-center">Check In</div>
                    <div className="col-span-2 text-center">Check Out</div>
                    <div className="col-span-2 text-right">Duration</div>
                  </div>
                  <div className="divide-y divide-divider">
                    {(attnSummary?.items || []).slice(0, 8).map((it) => (
                      <div key={it.id} className="grid grid-cols-12 px-4 py-3 text-sm items-center">
                        <div className="col-span-3 truncate font-medium">{it.name}</div>
                        <div className="col-span-2 truncate text-muted-foreground text-xs">{it.email}</div>
                        <div className="col-span-1">
                          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs ${it.registered ? "bg-emerald-500/10 text-emerald-600" : "bg-muted text-muted-foreground"}`}>
                            {it.registered ? "Yes" : "No"}
                          </span>
                        </div>
                        <div className="col-span-2 text-center">
                          {it.checkInTime ? (
                            <span className="inline-flex items-center gap-1 text-emerald-600 text-xs">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                              {new Date(it.checkInTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                            </span>
                          ) : (
                            <span className="text-muted-foreground text-xs">—</span>
                          )}
                        </div>
                        <div className="col-span-2 text-center">
                          {it.checkOutTime ? (
                            <span className="inline-flex items-center gap-1 text-orange-600 text-xs">
                              <span className="w-1.5 h-1.5 rounded-full bg-orange-500"></span>
                              {new Date(it.checkOutTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                            </span>
                          ) : it.checkedIn ? (
                            <span className="text-yellow-600 text-xs">Working...</span>
                          ) : (
                            <span className="text-muted-foreground text-xs">—</span>
                          )}
                        </div>
                        <div className="col-span-2 text-right">
                          {it.elapsedSeconds != null && it.elapsedSeconds > 0 ? (
                            <span className={`font-mono text-xs ${it.checkedOut ? "text-blue-600" : "text-muted-foreground"}`}>
                              {formatElapsedTime(it.elapsedSeconds)}
                            </span>
                          ) : (
                            <span className="text-muted-foreground text-xs">—</span>
                          )}
                        </div>
                      </div>
                    ))}
                    {attnSummary && attnSummary.items.length === 0 && (
                      <div className="px-4 py-6 text-sm text-muted-foreground">No users found.</div>
                    )}
                  </div>
                </div>
              </div>
            )}
            {/* Task Trend Chart */}
            <div className="grid lg:grid-cols-2 gap-8">
              {/* Priority Distribution */}
              <div className="bg-surface rounded-3xl p-6 md:p-8 opacity-0 animate-fade-in-up delay-300">
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Priority Breakdown
                </h2>
                <p className="text-sm text-muted-foreground mb-6">
                  Tasks by priority level
                </p>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-red-500"></div>
                      <span className="text-sm">High Priority</span>
                    </div>
                    <span className="font-semibold">{stats?.priority_distribution?.high ?? 0}</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-red-500 rounded-full transition-all" 
                      style={{ width: `${stats?.total ? (stats.priority_distribution.high / stats.total) * 100 : 0}%` }}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                      <span className="text-sm">Medium Priority</span>
                    </div>
                    <span className="font-semibold">{stats?.priority_distribution?.medium ?? 0}</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-amber-500 rounded-full transition-all" 
                      style={{ width: `${stats?.total ? (stats.priority_distribution.medium / stats.total) * 100 : 0}%` }}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-slate-400"></div>
                      <span className="text-sm">Low Priority</span>
                    </div>
                    <span className="font-semibold">{stats?.priority_distribution?.low ?? 0}</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-slate-400 rounded-full transition-all" 
                      style={{ width: `${stats?.total ? (stats.priority_distribution.low / stats.total) * 100 : 0}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Status Breakdown */}
              <div className="bg-surface rounded-3xl p-6 md:p-8 opacity-0 animate-fade-in-up delay-400">
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Status Breakdown
                </h2>
                <p className="text-sm text-muted-foreground mb-6">
                  Current task distribution by status
                </p>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                      <span className="text-sm">Completed</span>
                    </div>
                    <span className="font-semibold">{stats?.status_distribution?.completed ?? 0}</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-emerald-500 rounded-full transition-all" 
                      style={{ width: `${stats?.total ? (stats.status_distribution.completed / stats.total) * 100 : 0}%` }}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                      <span className="text-sm">In Progress</span>
                    </div>
                    <span className="font-semibold">{stats?.status_distribution?.in_progress ?? 0}</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 rounded-full transition-all" 
                      style={{ width: `${stats?.total ? (stats.status_distribution.in_progress / stats.total) * 100 : 0}%` }}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-gray-400"></div>
                      <span className="text-sm">Pending</span>
                    </div>
                    <span className="font-semibold">{stats?.status_distribution?.pending ?? 0}</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gray-400 rounded-full transition-all" 
                      style={{ width: `${stats?.total ? (stats.status_distribution.pending / stats.total) * 100 : 0}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Team & Recent Activity */}
        <section className="py-16 bg-surface">
          <div className="container-apple">
            <div className="grid lg:grid-cols-2 gap-8">
              {/* Team Performance */}
              <div className="bg-background rounded-3xl p-6 md:p-8 opacity-0 animate-fade-in-up delay-600">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-xl font-semibold text-foreground">
                      Team Performance
                    </h2>
                    <p className="text-sm text-muted-foreground mt-1">
                      Task completion by team member
                    </p>
                  </div>
                  <Users className="w-5 h-5 text-muted-foreground" />
                </div>
                
                {stats?.team_performance && stats.team_performance.length > 0 ? (
                  <div className="space-y-4">
                    {stats.team_performance.map((member) => (
                      <div key={member.id} className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-sm font-semibold text-blue-600 dark:text-blue-400 flex-shrink-0">
                          {member.name.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <p className="font-medium text-sm truncate">{member.name}</p>
                            <span className="text-xs text-muted-foreground">{member.completed}/{member.total_tasks}</span>
                          </div>
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-blue-500 rounded-full transition-all" 
                              style={{ width: `${member.completion_rate}%` }}
                            />
                          </div>
                        </div>
                        <span className="text-sm font-semibold w-12 text-right">{member.completion_rate}%</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground py-8 text-center">No tasks assigned yet</p>
                )}
              </div>

              {/* Recent Tasks */}
              <div className="bg-background rounded-3xl p-6 md:p-8 opacity-0 animate-fade-in-up delay-700">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-xl font-semibold text-foreground">
                      Recent Tasks
                    </h2>
                    <p className="text-sm text-muted-foreground mt-1">
                      Latest task updates
                    </p>
                  </div>
                  <Link to="/tasks" className="link-apple text-sm flex items-center gap-1">
                    View all
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
                
                {stats?.recent_tasks && stats.recent_tasks.length > 0 ? (
                  <div className="space-y-3">
                    {stats.recent_tasks.map((task) => (
                      <div
                        key={task.id}
                        className="flex items-center justify-between py-3 px-4 rounded-xl bg-muted/30 hover:bg-muted/50 transition-colors"
                      >
                        <div className="min-w-0 flex-1">
                          <p className="font-medium text-sm truncate">
                            {task.title}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {task.assignee_name} • {task.deadline ? new Date(task.deadline).toLocaleDateString() : "No deadline"}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            task.priority === "high" ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                            task.priority === "medium" ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" :
                            "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400"
                          }`}>
                            {task.priority}
                          </span>
                          <StatusBadge status={task.status} />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground py-8 text-center">No tasks created yet</p>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Quick Actions CTA */}
        <section className="py-20">
          <div className="container-apple text-center">
            <h2 className="headline-small mb-4 opacity-0 animate-fade-in-up">
              Ready to get more done?
            </h2>
            <p className="text-muted-foreground mb-8 opacity-0 animate-fade-in-up delay-100">
              Create a task and stay on top of your workflow.
            </p>
            <div className="flex items-center justify-center gap-4 opacity-0 animate-fade-in-up delay-200">
              <Link to="/create-task" className="btn-apple-primary">
                Create task
                <ArrowRight className="w-5 h-5 ml-1" />
              </Link>
              <Link to="/my-tasks" className="btn-apple-text">
                View my tasks
                <ChevronRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-8 border-t border-divider">
        <div className="container-apple">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
            <p>© 2024 Tasks. All rights reserved.</p>
            <div className="flex items-center gap-6">
              <button className="hover:text-foreground transition-colors">Privacy Policy</button>
              <button className="hover:text-foreground transition-colors">Terms of Service</button>
              <button className="hover:text-foreground transition-colors">Support</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
