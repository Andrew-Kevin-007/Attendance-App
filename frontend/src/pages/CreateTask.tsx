import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Navigation from "@/components/Navigation";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { CalendarIcon, ChevronLeft, ChevronDown, Loader2, Check } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { tasksAPI, authAPI, getUser } from "@/lib/api";

const CreateTask = () => {
  const navigate = useNavigate();
  const currentUser = getUser();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("");
  const [assignee, setAssignee] = useState("");
  const [dueDate, setDueDate] = useState<Date>();
  const [showPriority, setShowPriority] = useState(false);
  const [showAssignee, setShowAssignee] = useState(false);
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  const priorityRef = useRef<HTMLDivElement>(null);
  const assigneeRef = useRef<HTMLDivElement>(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (priorityRef.current && !priorityRef.current.contains(e.target as Node)) {
        setShowPriority(false);
      }
      if (assigneeRef.current && !assigneeRef.current.contains(e.target as Node)) {
        setShowAssignee(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    // Only admin can create tasks
    if (currentUser?.role !== "admin") {
      toast.error("Only admins can create tasks");
      navigate("/dashboard", { replace: true });
      return;
    }
    fetchEmployees();
  }, [currentUser, navigate]);

  const fetchEmployees = async () => {
    try {
      const data = await authAPI.getUsers();
      setEmployees(data);
    } catch (err) {
      toast.error("Failed to load employees");
    }
  };

  const priorities = [
    { value: "low", label: "Low", color: "bg-slate-100 text-slate-700" },
    { value: "medium", label: "Medium", color: "bg-amber-100 text-amber-700" },
    { value: "high", label: "High", color: "bg-red-100 text-red-700" },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title || !priority || !assignee || !dueDate) {
      toast.error("Please fill in all required fields");
      return;
    }

    setLoading(true);

    try {
      await tasksAPI.create({
        title,
        description,
        priority: priority.toLowerCase(),
        assigned_to: parseInt(assignee),
        deadline: format(dueDate, "yyyy-MM-dd"),
      });
      toast.success("Task created successfully");
      navigate("/tasks");
    } catch (err: any) {
      toast.error(err.message || "Failed to create task");
    } finally {
      setLoading(false);
    }
  };

  const selectedPriority = priorities.find(p => p.value === priority);
  const selectedEmployee = employees.find(e => e.id.toString() === assignee);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="pt-12">
        {/* Hero */}
        <section className="section-apple border-b border-divider">
          <div className="container-apple">
            <button
              onClick={() => navigate(-1)}
              className="btn-apple-text mb-8 opacity-0 animate-fade-in"
            >
              <ChevronLeft className="w-5 h-5" />
              Back
            </button>

            <div className="text-center">
              <h1 className="headline-large mb-4 opacity-0 animate-fade-in-up delay-100">
                New task
              </h1>
              <p className="subhead opacity-0 animate-fade-in-up delay-200">
                Add a new task to your workflow
              </p>
            </div>
          </div>
        </section>

        {/* Form */}
        <section className="py-16">
          <div className="max-w-xl mx-auto px-6">
            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Title */}
              <div className="opacity-0 animate-fade-in-up delay-300">
                <label className="block text-sm font-medium text-foreground mb-3">
                  Title
                </label>
                <input
                  type="text"
                  placeholder="What needs to be done?"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="input-apple w-full"
                />
              </div>

              {/* Description */}
              <div className="opacity-0 animate-fade-in-up delay-400">
                <label className="block text-sm font-medium text-foreground mb-3">
                  Description
                </label>
                <textarea
                  placeholder="Add more details..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="input-apple w-full min-h-[120px] resize-none py-4"
                />
              </div>

              {/* Priority */}
              <div className="opacity-0 animate-fade-in-up delay-500 relative z-40" ref={priorityRef}>
                <label className="block text-sm font-medium text-foreground mb-3">
                  Priority
                </label>
                <div className="relative">
                  <button
                    type="button"
                    onClick={() => {
                      setShowPriority(!showPriority);
                      setShowAssignee(false);
                    }}
                    className="input-apple w-full text-left flex items-center justify-between"
                  >
                    {selectedPriority ? (
                      <span className={cn("px-2.5 py-1 rounded-lg text-sm font-medium", selectedPriority.color)}>
                        {selectedPriority.label}
                      </span>
                    ) : (
                      <span className="text-muted-foreground">Select priority</span>
                    )}
                    <ChevronDown className={cn(
                      "w-5 h-5 text-muted-foreground transition-transform",
                      showPriority && "rotate-180"
                    )} />
                  </button>
                  {showPriority && (
                    <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-zinc-900 rounded-xl border border-gray-200 dark:border-zinc-700 shadow-2xl z-[100] overflow-hidden">
                      {priorities.map((p) => (
                        <button
                          key={p.value}
                          type="button"
                          onClick={() => {
                            setPriority(p.value);
                            setShowPriority(false);
                          }}
                          className="w-full px-4 py-3 text-left bg-white dark:bg-zinc-900 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors flex items-center justify-between border-b border-gray-100 dark:border-zinc-800 last:border-b-0"
                        >
                          <span className={cn("px-2.5 py-1 rounded-lg text-sm font-medium", p.color)}>
                            {p.label}
                          </span>
                          {priority === p.value && <Check className="w-4 h-4 text-blue-500" />}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Assignee */}
              <div className="opacity-0 animate-fade-in-up delay-600 relative z-30" ref={assigneeRef}>
                <label className="block text-sm font-medium text-foreground mb-3">
                  Assignee
                </label>
                <div className="relative">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAssignee(!showAssignee);
                      setShowPriority(false);
                    }}
                    className="input-apple w-full text-left flex items-center justify-between"
                  >
                    {selectedEmployee ? (
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm font-medium">
                          {selectedEmployee.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-medium text-foreground text-sm">{selectedEmployee.name}</div>
                          <div className="text-xs text-muted-foreground">{selectedEmployee.email}</div>
                        </div>
                      </div>
                    ) : (
                      <span className="text-muted-foreground">Select assignee</span>
                    )}
                    <ChevronDown className={cn(
                      "w-5 h-5 text-muted-foreground transition-transform flex-shrink-0",
                      showAssignee && "rotate-180"
                    )} />
                  </button>
                  {showAssignee && (
                    <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-zinc-900 rounded-xl border border-gray-200 dark:border-zinc-700 shadow-2xl z-[100] overflow-hidden max-h-64 overflow-y-auto">
                      {employees.length === 0 ? (
                        <div className="px-4 py-8 text-center text-gray-500 text-sm bg-white dark:bg-zinc-900">
                          No employees found
                        </div>
                      ) : (
                        employees.map((emp) => (
                          <button
                            key={emp.id}
                            type="button"
                            onClick={() => {
                              setAssignee(emp.id.toString());
                              setShowAssignee(false);
                            }}
                            className="w-full px-4 py-3 text-left bg-white dark:bg-zinc-900 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors flex items-center justify-between border-b border-gray-100 dark:border-zinc-800 last:border-b-0"
                          >
                            <div className="flex items-center gap-3">
                              <div className="w-9 h-9 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-sm font-semibold text-blue-600 dark:text-blue-400">
                                {emp.name.charAt(0).toUpperCase()}
                              </div>
                              <div>
                                <div className="font-medium text-gray-900 dark:text-white text-sm">{emp.name}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">{emp.email}</div>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-zinc-800 text-gray-600 dark:text-gray-400 capitalize">
                                {emp.role}
                              </span>
                              {assignee === emp.id.toString() && <Check className="w-4 h-4 text-blue-500" />}
                            </div>
                          </button>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Due Date */}
              <div className="opacity-0 animate-fade-in-up delay-700 relative z-10">
                <label className="block text-sm font-medium text-foreground mb-3">
                  Due date
                </label>
                <Popover>
                  <PopoverTrigger asChild>
                    <button
                      type="button"
                      className={cn(
                        "input-apple w-full text-left flex items-center justify-between",
                        !dueDate && "text-muted-foreground"
                      )}
                    >
                      <span className="flex items-center gap-3">
                        <CalendarIcon className="w-5 h-5" />
                        {dueDate ? format(dueDate, "MMMM d, yyyy") : "Select date"}
                      </span>
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0 rounded-xl border border-divider bg-background" align="start">
                    <Calendar
                      mode="single"
                      selected={dueDate}
                      onSelect={setDueDate}
                      initialFocus
                      className="rounded-xl"
                    />
                  </PopoverContent>
                </Popover>
              </div>

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-4 pt-8 opacity-0 animate-fade-in-up delay-800">
                <button
                  type="button"
                  onClick={() => navigate(-1)}
                  className="btn-apple-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-apple-primary flex-1"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create task"
                  )}
                </button>
              </div>
            </form>
          </div>
        </section>
      </main>
    </div>
  );
};

export default CreateTask;
