import { cn } from "@/lib/utils";

interface TeamMember {
  name: string;
  completed: number;
  pending: number;
  efficiency: number;
}

interface TeamPerformanceProps {
  data: TeamMember[];
  className?: string;
}

const TeamPerformance = ({ data, className }: TeamPerformanceProps) => {
  return (
    <div className={cn("space-y-4", className)}>
      {data.map((member, index) => (
        <div
          key={member.name}
          className="flex items-center gap-4 opacity-0 animate-fade-in-up"
          style={{ animationDelay: `${index * 100}ms` }}
        >
          {/* Avatar */}
          <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center shrink-0">
            <span className="text-sm font-medium text-foreground">
              {member.name.split(' ').map(n => n[0]).join('')}
            </span>
          </div>
          
          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <p className="text-sm font-medium text-foreground truncate">
                {member.name}
              </p>
              <span className="text-sm font-medium text-foreground">
                {member.efficiency}%
              </span>
            </div>
            
            {/* Progress bar */}
            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${member.efficiency}%`,
                  backgroundColor: 
                    member.efficiency >= 90 
                      ? 'hsl(152, 69%, 41%)' 
                      : member.efficiency >= 80 
                      ? 'hsl(211, 100%, 50%)' 
                      : 'hsl(35, 100%, 50%)',
                }}
              />
            </div>
            
            {/* Stats */}
            <div className="flex items-center gap-4 mt-1">
              <span className="text-xs text-muted-foreground">
                {member.completed} completed
              </span>
              <span className="text-xs text-muted-foreground">
                {member.pending} pending
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TeamPerformance;
