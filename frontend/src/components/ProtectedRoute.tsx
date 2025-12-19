import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getToken } from "@/lib/api";
import { attendanceAPI } from "@/lib/attendance";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      navigate("/", { replace: true });
      return;
    }

    const check = async () => {
      try {
        const isAttendancePage = location.pathname === "/attendance";
        const isRegisterPage = location.pathname === "/attendance/register";
        const res = await attendanceAPI.statusToday();
        
        // Only redirect to attendance if:
        // 1. User is registered (can mark attendance)
        // 2. Hasn't marked today
        // 3. Not already on attendance or register page
        if (res.registered && !res.markedToday && !isAttendancePage && !isRegisterPage) {
          navigate("/attendance", { replace: true });
          return;
        }
      } catch (_) {
        // If status check fails, fall back to allowing navigation to avoid hard lock
      } finally {
        setChecked(true);
      }
    };
    check();
  }, [navigate, location.pathname]);

  const token = getToken();
  if (!token || !checked) {
    return null;
  }

  return <>{children}</>;
};
