'use client';

import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import { getScoreColor } from '@/lib/utils';

interface ScoreStripProps {
  recovery: number;
  sleep: number;
  strain: number;
}

function getRecoveryLabel(score: number): string {
  if (score >= 67) return 'Висока готовність';
  if (score >= 34) return 'Середня готовність';
  return 'Низька готовність';
}

function getSleepLabel(score: number): string {
  if (score >= 85) return 'Відмінна якість';
  if (score >= 70) return 'Хороша якість';
  if (score >= 50) return 'Задовільна якість';
  return 'Погана якість';
}

function getStrainLabel(strain: number): string {
  if (strain >= 18) return 'Максимальне';
  if (strain >= 14) return 'Високе';
  if (strain >= 8) return 'Помірне';
  return 'Легке';
}

interface TooltipProps {
  text: string;
  children: React.ReactNode;
}

function Tooltip({ text, children }: TooltipProps) {
  const [show, setShow] = useState(false);
  return (
    <div
      className="relative"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      {children}
      {show && (
        <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 rounded-lg bg-surface border border-border text-xs text-textSec max-w-[220px] text-center shadow-lg whitespace-normal">
          {text}
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px border-4 border-transparent border-t-border" />
        </div>
      )}
    </div>
  );
}

export default function ScoreStrip({ recovery, sleep, strain }: ScoreStripProps) {
  const recoveryColor = getScoreColor(recovery);
  const sleepColor = getScoreColor(sleep);
  const strainColor = strain > 8 ? '#ef4444' : strain > 6 ? '#FFB020' : '#00D26A';

  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      {/* Recovery */}
      <Tooltip text="Відновлення показує, наскільки ваш організм готовий до навантажень. Від 0 до 100 — чим вище, тим краще відновлення.">
        <Card accent>
          <div className="text-center cursor-help">
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
            <p className="text-xs text-textDim mt-1">{getRecoveryLabel(recovery)}</p>
          </div>
        </Card>
      </Tooltip>

      {/* Sleep */}
      <Tooltip text="Оцінка сну враховує тривалість, глибину та якість вашого нічного відпочинку. Від 0 до 100 — чим вище, тим кращий сон.">
        <Card accent>
          <div className="text-center cursor-help">
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
            <p className="text-xs text-textDim mt-1">{getSleepLabel(sleep)}</p>
          </div>
        </Card>
      </Tooltip>

      {/* Strain */}
      <Tooltip text="Навантаження — це міра фізичної активності за день на основі пульсу. Від 0 до 21 — чим вище, тим інтенсивніший був день.">
        <Card accent>
          <div className="text-center cursor-help">
            <div className="mb-3 flex justify-center">
              <div
                className="w-20 h-20 rounded-full flex items-center justify-center"
                style={{
                  background: `linear-gradient(135deg, ${strainColor}20 0%, ${strainColor}10 100%)`,
                  border: `2px solid ${strainColor}`,
                }}
              >
                <span className="text-2xl font-bold" style={{ color: strainColor }}>
                  {typeof strain === 'number' ? strain.toFixed(1) : strain}
                </span>
              </div>
            </div>
            <h4 className="text-textSec text-sm font-semibold">Навантаження</h4>
            <p className="text-xs text-textDim mt-1">{getStrainLabel(strain)}</p>
          </div>
        </Card>
      </Tooltip>
    </div>
  );
}
