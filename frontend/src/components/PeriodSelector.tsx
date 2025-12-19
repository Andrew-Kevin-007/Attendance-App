import { cn } from "@/lib/utils";

type Period = "week" | "month" | "year";

interface PeriodSelectorProps {
  value: Period;
  onChange: (period: Period) => void;
  className?: string;
}

const PeriodSelector = ({ value, onChange, className }: PeriodSelectorProps) => {
  const periods: { value: Period; label: string }[] = [
    { value: "week", label: "7D" },
    { value: "month", label: "1M" },
    { value: "year", label: "1Y" },
  ];

  return (
    <div className={cn("inline-flex bg-muted rounded-full p-1", className)}>
      {periods.map((period) => (
        <button
          key={period.value}
          onClick={() => onChange(period.value)}
          className={cn(
            "px-4 py-1.5 text-sm font-medium rounded-full transition-all duration-300",
            value === period.value
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          {period.label}
        </button>
      ))}
    </div>
  );
};

export default PeriodSelector;
export type { Period };
