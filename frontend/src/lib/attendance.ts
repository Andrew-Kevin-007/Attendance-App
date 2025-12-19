import { getToken } from "./api";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";

export interface AttendanceStatus {
  registered: boolean;
  markedToday: boolean;
  checkedIn: boolean;
  checkedOut: boolean;
  checkInTime?: string | null;
  checkOutTime?: string | null;
  elapsedSeconds?: number | null;
  timestamp?: string | null;
}

export interface AttendanceResult {
  message: string;
  employee_id?: number;
  employee_name?: string;
  confidence?: number;
  checkInTime?: string;
  checkOutTime?: string | null;
  elapsedSeconds?: number;
  timestamp?: string;
}

export interface AttendanceSummaryItem {
  id: number;
  name: string;
  email: string;
  role: string;
  registered: boolean;
  markedToday: boolean;
  checkedIn: boolean;
  checkedOut: boolean;
  checkInTime?: string | null;
  checkOutTime?: string | null;
  elapsedSeconds?: number | null;
  timestamp?: string | null;
}

export interface AttendanceSummary {
  date: string;
  totals: { 
    users: number; 
    registered: number; 
    present: number; 
    absent: number;
    checkedOut: number;
  };
  items: AttendanceSummaryItem[];
}

export const attendanceAPI = {
  async statusToday(): Promise<AttendanceStatus> {
    const token = getToken();
    const res = await fetch(`${API_BASE_URL}/attendance/status-today`, {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });
    const json = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(json?.detail || "Failed to fetch status");
    }
    return json;
  },

  async checkIn(imageDataUrl: string): Promise<AttendanceResult> {
    return this.markAttendance(imageDataUrl, "check_in");
  },

  async checkOut(imageDataUrl: string): Promise<AttendanceResult> {
    return this.markAttendance(imageDataUrl, "check_out");
  },

  async markAttendance(imageDataUrl: string, action: "check_in" | "check_out" = "check_in"): Promise<AttendanceResult> {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/attendance/mark`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify({ image: imageDataUrl, action }),
    });

    const json = await response.json().catch(() => ({ error: "Invalid response" }));
    if (!response.ok) {
      throw new Error(json?.detail || json?.error || "Failed to mark attendance");
    }
    return json;
  },

  async registerFace(user_id: number, imageDataUrl: string) {
    const token = getToken();
    const res = await fetch(`${API_BASE_URL}/attendance/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify({ user_id, image: imageDataUrl }),
    });
    const json = await res.json().catch(() => ({ detail: "Invalid response" }));
    if (!res.ok) {
      throw new Error(json?.detail?.message || json?.detail || "Failed to register face");
    }
    return json as { message: string; employee_id: number };
  },

  async todaySummary(): Promise<AttendanceSummary> {
    const token = getToken();
    const res = await fetch(`${API_BASE_URL}/attendance/today-summary`, {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });
    const json = await res.json().catch(() => ({ detail: "Invalid response" }));
    if (!res.ok) {
      throw new Error(json?.detail || "Failed to load attendance summary");
    }
    return json;
  },

  async listUsers(): Promise<Array<{ id: number; name: string; email: string; role: string }>> {
    const token = getToken();
    const res = await fetch(`${API_BASE_URL}/attendance/users`, {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });
    const json = await res.json().catch(() => ({ detail: "Invalid response" }));
    if (!res.ok) {
      throw new Error(json?.detail || "Failed to load users");
    }
    return json;
  },
};

// Helper to format elapsed time
export function formatElapsedTime(seconds: number | null | undefined): string {
  if (seconds == null || seconds < 0) return "--:--:--";
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}
