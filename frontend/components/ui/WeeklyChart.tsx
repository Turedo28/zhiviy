'use client';

import React from 'react';

interface DataPoint {
  day: string;
  value: number;
}

interface WeeklyChartProps {
  data: DataPoint[];
  color?: string;
  maxValue?: number;
  height?: number;
  showValues?: boolean;
}

export default function WeeklyChart({
  data,
  color = '#fb923c',
  maxValue,
  height = 200,
  showValues = true,
}: WeeklyChartProps) {
  const max = maxValue || Math.max(...data.map(d => d.value));
  const barWidth = 100 / data.length / 1.2;
  const barGap = (100 / data.length) * 0.2;

  return (
    <div className="w-full">
      <div
        className="flex items-flex-end justify-around gap-2"
        style={{ height: `${height}px` }}
      >
        {data.map((point, index) => {
          const barHeight = (point.value / max) * 100;
          return (
            <div
              key={index}
              className="flex flex-col items-center justify-end flex-1 gap-2"
            >
              <div
                className="w-full rounded-t-sm transition-all duration-300 hover:opacity-80"
                style={{
                  height: `${barHeight}%`,
                  backgroundColor: color,
                  minHeight: '4px',
                }}
              />
              {showValues && (
                <span className="text-xs font-semibold text-textSec">
                  {point.value.toFixed(point.value % 1 !== 0 ? 1 : 0)}
                </span>
              )}
              <span className="text-xs text-textDim">{point.day}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
