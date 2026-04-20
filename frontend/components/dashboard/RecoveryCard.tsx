'use client';

import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import Label from '@/components/ui/Label';
import CircleProgress from '@/components/ui/CircleProgress';

interface RecoveryData {
  score: number;
  recommendation: string;
  level: 'high' | 'medium' | 'low';
}

function Tooltip({ text, children }: { text: string; children: React.ReactNode }) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      {children}
      {show && (
        <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 rounded-lg bg-surface border border-border text-xs text-textSec max-w-[260px] text-center shadow-lg whitespace-normal">
          {text}
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px border-4 border-transparent border-t-border" />
        </div>
      )}
    </div>
  );
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
      <Tooltip text="Відновлення показує, наскільки ваш організм готовий до фізичних навантажень. Шкала від 0 до 100: зелена зона (67–100) — організм готовий, жовта (34–66) — помірна готовність, червона (0–33) — потрібен відпочинок.">
        <div className="mb-6 cursor-help">
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
              <div className="text-xs text-textSec">зі 100</div>
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
      </Tooltip>

      <div className="pt-6 border-t border-cardBorder">
        <p className="text-sm text-textSec leading-relaxed text-center">
          {recommendation}
        </p>
      </div>
    </Card>
  );
}
