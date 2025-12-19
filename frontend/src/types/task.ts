export type TaskStatus = "pending" | "in-progress" | "completed";
export type TaskPriority = "low" | "medium" | "high";

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee: string;
  dueDate: string;
  createdAt: string;
}

export const mockTasks: Task[] = [
  {
    id: "1",
    title: "Design system documentation",
    description: "Create comprehensive documentation for the new design system",
    status: "in-progress",
    priority: "high",
    assignee: "Sarah Chen",
    dueDate: "2024-12-20",
    createdAt: "2024-12-10",
  },
  {
    id: "2",
    title: "API integration review",
    description: "Review and test all API endpoints for the mobile app",
    status: "pending",
    priority: "high",
    assignee: "Marcus Johnson",
    dueDate: "2024-12-18",
    createdAt: "2024-12-08",
  },
  {
    id: "3",
    title: "User feedback analysis",
    description: "Analyze Q4 user feedback and create summary report",
    status: "completed",
    priority: "medium",
    assignee: "Emily Rodriguez",
    dueDate: "2024-12-15",
    createdAt: "2024-12-05",
  },
  {
    id: "4",
    title: "Performance optimization",
    description: "Optimize database queries for faster load times",
    status: "in-progress",
    priority: "medium",
    assignee: "David Kim",
    dueDate: "2024-12-22",
    createdAt: "2024-12-12",
  },
  {
    id: "5",
    title: "Security audit preparation",
    description: "Prepare documentation for annual security audit",
    status: "pending",
    priority: "high",
    assignee: "Sarah Chen",
    dueDate: "2024-12-25",
    createdAt: "2024-12-14",
  },
  {
    id: "6",
    title: "Onboarding flow redesign",
    description: "Redesign the new user onboarding experience",
    status: "pending",
    priority: "low",
    assignee: "Emily Rodriguez",
    dueDate: "2024-12-30",
    createdAt: "2024-12-13",
  },
];
