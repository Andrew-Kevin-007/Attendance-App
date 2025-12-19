import { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import { authAPI } from "@/lib/api";
import { Users, Mail, Shield, Loader2, Plus, X } from "lucide-react";

const Employees = () => {
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "employee",
  });
  const [formError, setFormError] = useState("");
  const [formLoading, setFormLoading] = useState(false);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const data = await authAPI.getUsers();
      setEmployees(data);
    } catch (err: any) {
      setError(err.message || "Failed to load employees");
    } finally {
      setLoading(false);
    }
  };

  const handleAddEmployee = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    setFormLoading(true);

    try {
      await authAPI.addEmployee(formData);
      setFormData({ name: "", email: "", password: "", role: "employee" });
      setShowAddForm(false);
      fetchEmployees();
    } catch (err: any) {
      setFormError(err.message || "Failed to add employee");
    } finally {
      setFormLoading(false);
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case "admin":
        return "bg-red-500/10 text-red-600 border-red-500/20";
      case "manager":
        return "bg-blue-500/10 text-blue-600 border-blue-500/20";
      default:
        return "bg-green-500/10 text-green-600 border-green-500/20";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="pt-12">
        {/* Hero */}
        <section className="section-apple border-b border-divider">
          <div className="container-apple">
            <div className="max-w-3xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 mb-4 opacity-0 animate-fade-in">
                <Users className="w-8 h-8" />
              </div>
              <h1 className="headline-large mb-4 opacity-0 animate-fade-in-up">
                Team Members
              </h1>
              <p className="subhead opacity-0 animate-fade-in-up delay-100">
                {employees.length} members in your organization
              </p>
              <button
                onClick={() => setShowAddForm(true)}
                className="btn-apple mt-6 opacity-0 animate-fade-in-up delay-200"
              >
                <Plus className="w-5 h-5" />
                Add Employee
              </button>
            </div>
          </div>
        </section>

        {/* Add Employee Form Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <div className="bg-background rounded-2xl p-6 max-w-md w-full">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold">Add New Employee</h2>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="p-2 hover:bg-accent rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleAddEmployee} className="space-y-4">
                {formError && (
                  <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                    {formError}
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium mb-2">Full Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="input-apple w-full"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="input-apple w-full"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Temporary Password</label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="input-apple w-full"
                    required
                    minLength={6}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Employee should change this on first login
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Role</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="input-apple w-full"
                  >
                    <option value="employee">Employee</option>
                    <option value="manager">Manager</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="flex-1 px-4 py-3 rounded-xl border border-divider hover:bg-accent transition-colors"
                    disabled={formLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-apple flex-1"
                    disabled={formLoading}
                  >
                    {formLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Adding...
                      </>
                    ) : (
                      <>
                        <Plus className="w-5 h-5" />
                        Add Employee
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Employee List */}
        <section className="section-apple">
          <div className="container-apple">
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
              </div>
            ) : error ? (
              <div className="text-center py-20">
                <p className="text-destructive">{error}</p>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {employees.map((employee, index) => (
                  <div
                    key={employee.id}
                    className={`card-apple p-6 opacity-0 animate-fade-in-up`}
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                          <span className="text-lg font-semibold">
                            {employee.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">{employee.name}</h3>
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <Mail className="w-3.5 h-3.5" />
                            {employee.email}
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Shield className="w-4 h-4 text-muted-foreground" />
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium border ${getRoleBadgeColor(employee.role)}`}
                      >
                        {employee.role.charAt(0).toUpperCase() + employee.role.slice(1)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Employees;
