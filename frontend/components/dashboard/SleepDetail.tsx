'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import Label from '@/components/ui/Label';
import ProgressBar from '@/components/ui/ProgressBar';

interface SleepDetailData {
  totalHours?: number;
  hours?: number;
  bedTime?: string;
  wakeTime?: string;
  quality?: number;
  score?: number;
  consistency?: number;
  efficiency?: number;
  stages: {
    awake: number;
    light: number;
    deep: number;
    rem: number;
  };
  notes?: string;
}

export default function SleepDetail({
  totalHours,
  hours,
  bedTime,
  wakeTime,
  quality,
  score,
  consistency,
  efficiency,
  stages,
  notes,
}: SleepDetailData) {
  const displayHours = totalHours ?? hours ?? 0;
  const displayQuality = quality ?? score ?? 0;
  const displayConsistency = consistency ?? efficiency ?? 0;
  return (
    <Card>
      <div className="mb-6">
        <Label>Детальна інформація про сон</Label>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="glass-card-sm p-4 text-center">
          <p className="text-xs text-textDim mb-1">Засинання</p>
          <p className="text-xl font-bold text-accent">{bedTime || '—'}</p>
        </div>
        <div className="glass-card-sm p-4 text-center">
          <p className="text-xs text-textDim mb-1">Підйом</p>
          <p className="text-xl font-bold text-accent">{wakeTime || '—'}</p>
        </div>
        <div className="glass-card-sm p-4 text-center">
          <p className="text-xs text-textDim mb-1">Якість</p>
          <p className="text-xl font-bold text-green">{displayQuality ? Math.round(displayQuality) : '—'}%</p>
        </div>
        <div className="glass-card-sm p-4 text-center">
          <p className="text-xs text-textDim mb-1">Ефективність</p>
          <p className="text-xl font-bold text-blue">{displayConsistency ? Math.round(displayConsistency) : '—'}%</p>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        <ProgressBar
          current={stages.deep}
          target={displayHours}
          label="Глибокий сон"
          unit="ч"
          showPercentage={false}
          decimals={1}
        />
        <ProgressBar
          current={stages.rem}
          target={displayHours}
          label="REM сон"
          unit="ч"
          showPercentage={false}
          decimals={1}
        />
        <ProgressBar
          current={stages.light}
          target={displayHours}
          label="Легкий сон"
          unit="ч"
          showPercentage={false}
          decimals={1}
        />
        <ProgressBar
          current={stages.awake}
          target={displayHours}
          label="Пробудження"
          unit="ч"
          showPercentage={false}
          decimals={1}
        />
      </div>

      {notes && (
        <div className="pt-6 border-t border-cardBorder">
          <p className="text-sm text-textSec">{notes}</p>
        </div>
      )}
    </Card>
  );
}
