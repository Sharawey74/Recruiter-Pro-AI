"use client";

interface CircularProgressProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
}

export function CircularProgress({ 
  score, 
  size = 80, 
  strokeWidth = 8,
  showLabel = true 
}: CircularProgressProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;

  // Color based on score
  const getColor = () => {
    if (score >= 75) return { stroke: "#10B981", bg: "#10B98120" }; // Green
    if (score >= 50) return { stroke: "#F59E0B", bg: "#F59E0B20" }; // Yellow
    return { stroke: "#EF4444", bg: "#EF444420" }; // Red
  };

  const colors = getColor();

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={colors.bg}
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={colors.stroke}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500 ease-out"
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xl font-bold" style={{ color: colors.stroke }}>
            {Math.round(score)}%
          </span>
        </div>
      )}
    </div>
  );
}
