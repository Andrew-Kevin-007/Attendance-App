const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";

// Auth helpers
export const getToken = () => localStorage.getItem("access_token");
export const setToken = (token: string) => localStorage.setItem("access_token", token);
export const removeToken = () => localStorage.removeItem("access_token");
export const getUser = () => {
  const userStr = localStorage.getItem("user");
  return userStr ? JSON.parse(userStr) : null;
};
export const setUser = (user: any) => localStorage.setItem("user", JSON.stringify(user));
export const removeUser = () => localStorage.removeItem("user");

// API client
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  
  const config: RequestInit = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "An error occurred" }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Auth API
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(error.detail || "Invalid credentials");
    }

    return response.json();
  },

  register: async (data: { name: string; email: string; password: string; role: string }) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Registration failed" }));
      throw new Error(error.detail || "Could not create account");
    }

    return response.json();
  },

  getUsers: () => apiRequest<any[]>("/auth/users"),

  getMe: () => apiRequest<any>("/auth/me"),

  addEmployee: (data: { name: string; email: string; password: string; role?: string }) =>
    apiRequest<any>("/auth/add-employee", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// Notifications API
export const notificationsAPI = {
  getAll: () => apiRequest<any[]>("/notifications/"),
  
  getUnreadCount: () => apiRequest<{ count: number }>("/notifications/unread-count"),
  
  markAsRead: (id: number) => apiRequest<any>(`/notifications/${id}/read`, {
    method: "PUT",
  }),
  
  markAllAsRead: () => apiRequest<any>("/notifications/mark-all-read", {
    method: "PUT",
  }),
  
  delete: (id: number) => apiRequest<any>(`/notifications/${id}`, {
    method: "DELETE",
  }),
  
  create: (data: { user_id: number; title: string; message: string; type?: string }) =>
    apiRequest<any>("/notifications/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// Tasks API
export const tasksAPI = {
  getAll: () => apiRequest<any[]>("/tasks"),
  
  getMyTasks: () => apiRequest<any[]>("/tasks/my-tasks"),
  
  getById: (id: number) => apiRequest<any>(`/tasks/${id}`),
  
  getStats: () => apiRequest<{
    total: number;
    completed: number;
    in_progress: number;
    pending: number;
    overdue: number;
    completion_rate: number;
    priority_distribution: { high: number; medium: number; low: number };
    status_distribution: { completed: number; in_progress: number; pending: number };
    team_performance: Array<{
      id: number;
      name: string;
      email: string;
      role: string;
      total_tasks: number;
      completed: number;
      completion_rate: number;
    }>;
    recent_tasks: Array<{
      id: number;
      title: string;
      status: string;
      priority: string;
      deadline: string | null;
      assignee_name: string;
    }>;
  }>("/tasks/stats"),
  
  create: (data: any) => 
    apiRequest<any>("/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  update: (id: number, data: any) =>
    apiRequest<any>(`/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  
  delete: (id: number) =>
    apiRequest<void>(`/tasks/${id}`, {
      method: "DELETE",
    }),
};
