import { Link, useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { removeToken, removeUser, getUser } from "@/lib/api";
import { LogOut } from "lucide-react";

const Navigation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const user = getUser();
  const isAdmin = user?.role === "admin";
  const isManager = user?.role === "manager";
  const canRegisterFaces = isAdmin || isManager;

  const navItems = isAdmin ? [
    { path: "/dashboard", label: "Overview" },
    { path: "/tasks", label: "All Tasks" },
    { path: "/employees", label: "Employees" },
    { path: "/create-task", label: "New Task" },
    { path: "/attendance/register", label: "Register Face" },
  ] : isManager ? [
    { path: "/dashboard", label: "Overview" },
    { path: "/tasks", label: "All Tasks" },
    { path: "/my-tasks", label: "My Tasks" },
    { path: "/attendance/register", label: "Register Face" },
  ] : [
    { path: "/dashboard", label: "Overview" },
    { path: "/my-tasks", label: "My Tasks" },
    { path: "/inbox", label: "Inbox" },
  ];

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    removeToken();
    removeUser();
    navigate("/", { replace: true });
  };

  return (
    <nav className="nav-apple">
      <div className="h-full max-w-5xl mx-auto px-6 flex items-center justify-between">
        {/* Logo */}
        <Link to="/dashboard" className="flex items-center">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18.71 19.5C17.88 20.74 17 21.95 15.66 21.97C14.32 22 13.89 21.18 12.37 21.18C10.84 21.18 10.37 21.95 9.1 22C7.79 22.05 6.8 20.68 5.96 19.47C4.25 17 2.94 12.45 4.7 9.39C5.57 7.87 7.13 6.91 8.82 6.88C10.1 6.86 11.32 7.75 12.11 7.75C12.89 7.75 14.37 6.68 15.92 6.84C16.57 6.87 18.39 7.1 19.56 8.82C19.47 8.88 17.39 10.1 17.41 12.63C17.44 15.65 20.06 16.66 20.09 16.67C20.06 16.74 19.67 18.11 18.71 19.5ZM13 3.5C13.73 2.67 14.94 2.04 15.94 2C16.07 3.17 15.6 4.35 14.9 5.19C14.21 6.04 13.07 6.7 11.95 6.61C11.8 5.46 12.36 4.26 13 3.5Z"/>
          </svg>
        </Link>

        {/* Center Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "text-xs font-normal transition-opacity duration-200",
                isActive(item.path)
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {item.label}
            </Link>
          ))}
        </div>

        {/* Sign Out */}
        <button
          onClick={handleLogout}
          className="text-xs text-muted-foreground hover:text-foreground transition-opacity duration-200"
        >
          Sign out
        </button>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden border-t border-divider bg-background/95 backdrop-blur-xl">
        <div className="flex items-center justify-around py-3">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "text-xs font-normal transition-opacity duration-200",
                isActive(item.path)
                  ? "text-foreground"
                  : "text-muted-foreground"
              )}
            >
              {item.label}
            </Link>
          ))}
          <button
            onClick={handleLogout}
            className="text-xs font-normal text-muted-foreground hover:text-foreground transition-opacity duration-200 flex items-center gap-1"
            title="Logout"
          >
            <LogOut className="w-3.5 h-3.5" />
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
