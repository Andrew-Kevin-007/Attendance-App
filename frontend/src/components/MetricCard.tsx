import { cn } from "@/lib/utils";
import { LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: number;
    direction: "up" | "down" | "neutral";
  };
  icon?: LucideIcon;
  className?: string;
  delay?: number;
}

const MetricCard = ({
  title,
  value,
  subtitle,
  trend,
  icon: Icon,
  className,
  delay = 0,
}: MetricCardProps) => {
  const TrendIcon = trend?.direction === "up" 
    ? TrendingUp 
    : trend?.direction === "down" 
    ? TrendingDown 
    : Minus;

  return (
    <div
      className={cn(
        "bg-surface rounded-2xl p-6 opacity-0 animate-fade-in-up",
        className
      )}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="text-3xl font-semibold text-foreground tracking-tight">
            {value}
          </p>
          {subtitle && (
            <p className="text-xs text-muted-foreground">{subtitle}</p>
          )}
        </div>
        {Icon && (
          <div className="p-2 bg-muted rounded-xl">
            <Icon className="w-5 h-5 text-muted-foreground" />
          </div>
        )}
      </div>
      
      {trend && (
        <div className="flex items-center gap-1 mt-3">
          <TrendIcon
            className={cn(
              "w-4 h-4",
              trend.direction === "up" && "text-emerald-500",
              trend.direction === "down" && "text-red-500",
              trend.direction === "neutral" && "text-muted-foreground"
            )}
          />
          <span
            className={cn(
              "text-sm font-medium",
              trend.direction === "up" && "text-emerald-500",
              trend.direction === "down" && "text-red-500",
              trend.direction === "neutral" && "text-muted-foreground"
            )}
          >
            {trend.value}%
          </span>
          <span className="text-xs text-muted-foreground">vs last period</span>
        </div>
      )}
    </div>
  );
};

export default MetricCard;
