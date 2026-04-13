'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import { getScoreColor } from '@/lib/utils';

interface ScoreStripProps {
  recovery: number;
  sleep: number;
  strain: number;
}

export default function ScoreStrip({ recovery, sleep, strain }: ScoreStripProps) {
  const recoveryColor = getScoreColor(recovery);
  const sleepColor = getScoreColor(sleep);
  const strainColor = strain > 8 ? '#ef4444' : strain > 6 ? '#FFB020' : '#00D26A';

  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      {/* Recovery */}
      <Card accent>
        <div className="text-center">
          <div className="mb-3 flex justify-center">
            <div
              className="w-20 h-20 rounded-full flex items-center justify-center"
              style={{
                background: `linear-gradient(135deg, ${recoveryColor}20 0%, ${recoveryColor}10 100%)`,
                border: `2px solid ${recoveryColor}`,
              }}
            >
              <span className="text-2xl font-bold" style={{ color: recoveryColor }}>
                {recovery}
              </span>
            </div>
          </div>
          <h4 className="text-textSec text-sm font-semibold">Відновлення</h4>
          <p className="text-xs text-textDim mt-1">Ready to train</p>
        </div>
      </Card>

      {/* Sleep */}
      <Card accent>
        <div className="text-center">
          <div className="mb-3 flex justify-center">
            <div
              className="w-20 h-20 rounded-full flex items-center justify-center"
              style={{
                background: `linear-gradient(135deg, ${sleepColor}20 0%, ${sleepColor}10 100%)`,
                border: `2px solid ${sleepColor}`,
              }}
            >
              <span className="text-2xl font-bold" style={{ color: sleepColor }}>
                {sleep}
              </span>
            </div>
          </div>
          <h4 className="text-textSec text-sm font-semibold">Сон</h4>
          <p className="text-xs text-textDim mt-1">Good quality</p>
        </div>
      </Card>

      {/* Strain */}
      <Card accent>
        <div className="text-center">
          <div className="mb-3 flex justify-center">
            <div
              className="w-20 h-20 rounded-full flex items-center justify-center"
              style={{
                background: `linear-gradient(135deg, ${strainColor}20 0%, ${strainColor}10 100%)`,
                border: `2px solid ${strainColor}`,
              }}
            >
              <span className="text-2xl font-bold" style={{ color: strainColor }}>
                {strain}
              </span>
            </div>
          </div>
          <h4 className="text-textSec text-sm font-semibold">Напруга</h4>
          <p className="text-xs text-textDim mt-1">Moderate</p>
        </div>
      </Card>
    </div>
  );
}
