"use client";

export function Header({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-8">
      {subtitle && <p className="text-gray-400 text-sm mb-2">{subtitle}</p>}
      <h1 className="text-3xl font-bold text-white">{title}</h1>
    </div>
  );
}
