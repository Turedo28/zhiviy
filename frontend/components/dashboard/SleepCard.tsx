'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import Label from '@/components/ui/Label';

interface SleepData {
  hours: number;
  stages: {
    awake: number;
    light: number;
    deep: number;
    rem: number;
  };
}

export default function SleepCard({ hours, stages }: SleepData) {
  const total = Object.values(stages).reduce((a, b) => a + b, 0);
  const stageKeys = ['deep', 'rem', 'light', 'awake'] as const;

  const stageColors = {
    deep: '#a78bfa',
    rem: '#9333ea',
    light: '#60a5fa',
    awake: '#555555',
  };

  const stageLabels = {
    deep: 'Глибокий',
    rem: 'REM',
    light: 'Легкий',
    awake: 'Пробудження',
  };

  return (
    <Card>
      <div className="mb-4">
        <Label>Сон</Label>
      </div>

      <div className="text-center mb-6">
        <div className="text-4xl font-bold text-text">{hours.toFixed(1)}</div>
        <p className="text-sm text-textSec">годин сну</p>
      </div>

      {/* Sleep stages bar */}
      <div className="flex gap-1 mb-4 h-6 bg-textMuted rounded-sm overflow-hidden bg-opacity-20">
        {stageKeys.map(stage => {
          const duration = stages[stage];
          const percentage = (duration / total) * 100;
          return (
            <div
              key={stage}
              style={{
                width: `${percentage}%`,
                backgroundColor: stageColors[stage],
                transition: 'width 0.3s ease',
              }}
              title={`${stageLabels[stage]}: ${duration.toFixed(1)}ч`}
            />
          );
        })}
      </div>

      {/* Stage legend */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        {stageKeys.map(stage => (
          <div key={stage} className="flex items-center gap-2">
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: stageColors[stage] }}
            />
            <span className="text-textDim">{stageLabels[stage]}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
