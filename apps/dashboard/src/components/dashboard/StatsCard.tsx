"use client";

import { useEffect, useState } from "react";
import { ReactNode } from "react";

interface StatsCardProps {
  title: string;
  value: number;
  icon: ReactNode;
  description?: string;
  duration?: number;
}

export default function StatsCard({ title, value, icon, description, duration = 1500 }: StatsCardProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTime: number | null = null;
    const endValue = value;

    const animateCount = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      
      // easeOutQuart
      const easeProgress = 1 - Math.pow(1 - progress, 4);
      
      setDisplayValue(Math.floor(easeProgress * endValue));

      if (progress < 1) {
        requestAnimationFrame(animateCount);
      } else {
        setDisplayValue(endValue);
      }
    };

    requestAnimationFrame(animateCount);
  }, [value, duration]);

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm p-6 flex flex-col transition-all hover:bg-zinc-800/50">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-zinc-400 font-medium text-sm">{title}</h3>
        <div className="text-zinc-500 bg-zinc-800/50 p-2 rounded-lg">
          {icon}
        </div>
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-3xl font-semibold text-zinc-100">
          {displayValue.toLocaleString()}
        </span>
        {description && (
          <span className="text-xs text-zinc-500">{description}</span>
        )}
      </div>
    </div>
  );
}
