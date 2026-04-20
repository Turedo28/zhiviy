'use client';

import React from 'react';
import { getCalColor } from '@/lib/utils';

interface ProgressBarProps {
  current: number;
  target: number;
  label?: string;
  unit?: string;
  showPercentage?: boolean;
  decimals?: number;
}

export default function ProgressBar({
  current,
  target,
  label,
  unit = '',
  showPercentage = true,
  decimals,
}: ProgressBarProps) {
  const percentage = Math.min((current / target) * 100, 100);
  const color = getCalColor(current, target);
  const fmt = (v: number) => decimals != null ? v.toFixed(decimals) : String(Math.round(v));

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-textSec">{label}</span>
          <span className="text-sm font-semibold text-text">
            {fmt(current)} / {fmt(target)} {unit}
          </span>
        </div>
      )}
      <div
        className="w-full h-2 bg-textMuted rounded-full overflow-hidden"
        style={{ backgroundColor: 'rgba(255,255,255,0.1)' }}
      >
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{
            width: `${percentage}%`,
            backgroundColor: color,
          }}
        />
      </div>
      {showPercentage && (
        <div className="text-xs text-textSec mt-1">{Math.round(percentage)}%</div>
      )}
    </div>
  );
}
