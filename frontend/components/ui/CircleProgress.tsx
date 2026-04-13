'use client';

import React from 'react';
import { getCalColor, getScoreColor } from '@/lib/utils';

interface CircleProgressProps {
  current: number;
  target: number;
  type?: 'calorie' | 'score';
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
}

export default function CircleProgress({
  current,
  target,
  type = 'calorie',
  size = 120,
  strokeWidth = 8,
  showLabel = true,
}: CircleProgressProps) {
  const percentage = Math.min((current / target) * 100, 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  const color = type === 'score' ? getScoreColor(current) : getCalColor(current, target);

  return (
    <div className="flex flex-col items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.3s ease' }}
        />
      </svg>
      {showLabel && (
        <div className="absolute text-center">
          <div className="text-lg font-bold text-text">{Math.round(percentage)}%</div>
          <div className="text-xs text-textSec">{Math.round(current / target * 100)}%</div>
        </div>
      )}
    </div>
  );
}
