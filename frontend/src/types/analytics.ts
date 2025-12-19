import { Task, TaskStatus, TaskPriority } from "./task";

export interface ChartDataPoint {
  name: string;
  completed: number;
  created: number;
  pending?: number;
  inProgress?: number;
}

export interface PieDataPoint {
  name: string;
  value: number;
  fill: string;
}

// Generate weekly data (last 7 days)
export const generateWeeklyData = (): ChartDataPoint[] => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  return days.map((day, index) => ({
    name: day,
    completed: Math.floor(Math.random() * 8) + 2,
    created: Math.floor(Math.random() * 10) + 3,
    pending: Math.floor(Math.random() * 5) + 1,
    inProgress: Math.floor(Math.random() * 4) + 1,
  }));
};

// Generate monthly data (last 4 weeks)
export const generateMonthlyData = (): ChartDataPoint[] => {
  return [
    { name: 'Week 1', completed: 24, created: 32, pending: 8, inProgress: 6 },
    { name: 'Week 2', completed: 31, created: 28, pending: 5, inProgress: 8 },
    { name: 'Week 3', completed: 28, created: 35, pending: 12, inProgress: 7 },
    { name: 'Week 4', completed: 35, created: 30, pending: 7, inProgress: 5 },
  ];
};

// Generate annual data (last 12 months)
export const generateAnnualData = (): ChartDataPoint[] => {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return months.map((month) => ({
    name: month,
    completed: Math.floor(Math.random() * 80) + 40,
    created: Math.floor(Math.random() * 100) + 50,
    pending: Math.floor(Math.random() * 30) + 10,
    inProgress: Math.floor(Math.random() * 25) + 8,
  }));
};

// Status distribution for pie chart
export const getStatusDistribution = (): PieDataPoint[] => [
  { name: 'Completed', value: 42, fill: 'hsl(152, 69%, 41%)' },
  { name: 'In Progress', value: 28, fill: 'hsl(211, 100%, 50%)' },
  { name: 'Pending', value: 30, fill: 'hsl(35, 100%, 50%)' },
];

// Priority distribution
export const getPriorityDistribution = (): PieDataPoint[] => [
  { name: 'High', value: 25, fill: 'hsl(0, 84%, 60%)' },
  { name: 'Medium', value: 45, fill: 'hsl(35, 100%, 50%)' },
  { name: 'Low', value: 30, fill: 'hsl(152, 69%, 41%)' },
];

// Team performance data
export const getTeamPerformance = () => [
  { name: 'Sarah Chen', completed: 18, pending: 3, efficiency: 94 },
  { name: 'Marcus Johnson', completed: 15, pending: 5, efficiency: 88 },
  { name: 'Emily Rodriguez', completed: 22, pending: 2, efficiency: 96 },
  { name: 'David Kim', completed: 12, pending: 4, efficiency: 85 },
];

// Summary stats
export const getSummaryStats = (period: 'week' | 'month' | 'year') => {
  const multiplier = period === 'week' ? 1 : period === 'month' ? 4 : 52;
  return {
    totalTasks: Math.floor(35 * multiplier),
    completedTasks: Math.floor(24 * multiplier),
    completionRate: 86,
    avgCompletionTime: '2.4 days',
    tasksCreated: Math.floor(32 * multiplier),
    overdueTasks: Math.floor(3 * multiplier * 0.5),
  };
};
