'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import Label from '@/components/ui/Label';
import CircleProgress from '@/components/ui/CircleProgress';

interface RecoveryData {
  score: number;
  recommendation: string;
  level: 'high' | 'medium' | 'low';
}

export default function RecoveryCard({ score, recommendation, level }: RecoveryData) {
  const colors = {
    high: '#00D26A',
    medium: '#FFB020',
    low: '#ef4444',
  };

  const levelLabels = {
    high: 'Висока готовність',
    medium: 'Середня готовність',
    low: 'Низька готовність',
  };

  return (
    <Card accent>
      <div className="mb-6">
        <Label>Відновлення</Label>
      </div>

      <div className="flex flex-col items-center mb-6">
        <div className="relative w-40 h-40 flex items-center justify-center mb-4">
          <CircleProgress
            current={score}
            target={100}
            type="score"
            size={160}
            strokeWidth={8}
            showLabel={false}
          />
          <div className="absolute text-center">
            <div className="text-3xl font-bold text-text">{score}</div>
            <div className="text-xs text-textSec">Балів</div>
          </div>
        </div>
        <div
          className="px-4 py-1 rounded-sm text-sm font-semibold"
          style={{
            backgroundColor: `${colors[level]}20`,
            color: colors[level],
            border: `1px solid ${colors[level]}40`,
          }}
        >
          {levelLabels[level]}
        </div>
      </div>

      <div className="pt-6 border-t border-cardBorder">
        <p className="text-sm text-textSec leading-relaxed text-center">
          {recommendation}
        </p>
      </div>
    </Card>
  );
}
