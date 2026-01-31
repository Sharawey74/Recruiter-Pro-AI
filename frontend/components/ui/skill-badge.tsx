"use client";

interface SkillBadgeProps {
  skill: string;
  type?: "required" | "preferred" | "matched" | "missing";
}

export function SkillBadge({ skill, type = "matched" }: SkillBadgeProps) {
  const getStyle = () => {
    switch (type) {
      case "required":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      case "preferred":
        return "bg-gray-500/20 text-gray-400 border-gray-500/30";
      case "matched":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case "missing":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      default:
        return "bg-purple-500/20 text-purple-400 border-purple-500/30";
    }
  };

  return (
    <span className={`px-2 py-1 rounded text-xs border font-medium ${getStyle()}`}>
      {skill}
    </span>
  );
}
