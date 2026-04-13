'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import Label from '@/components/ui/Label';
import ProgressBar from '@/components/ui/ProgressBar';

interface SleepDetailData {
  totalHours: number;
  bedTime: string;
  wakeTime: string;
  quality: number;
  consistency: number;
  stages: {
    awake: number;
    light: number;
    deep: number;
    rem: number;
  };
  notes: string;
}

export default function SleepDetail({
  totalHours,
  bedTime,
  wakeTime,
  quality,
  consistency,
  stages,
  notes,
}: SleepDetailData) {
  return (
    <Card>
      <div className="mb-6">
        <Label>Детальна інформація про сон</Label>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="glass-card-sm p-4 text-center">
          <p className="text-xs text-textDim mb-1">Було</p>
          <p className="text-xl font-bold text-accent">{bedTime}</p>
        </div>
        <div className="glass-card-sm p-4 text-center">
          <p className="text-xs text-textDim mb-1">Прокинувся</p>
          <p className="text-xl font-bold text-accent">{wakeTime}</p>
        </div>
        <div className="glass-card-sm p-4 text-center">
          <p className="text-xs text-textDim mb-1">Якість</p>
          <p className="text-xl font-bold text-green">{quality}%</p>
        </div>
        <div className="glass-card-sm p-4 text-center">
          <p className="text-xs text-textDim mb-1">Послідовність</p>
          <p className="text-xl font-bold text-blue">{consistency}%</p>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        <ProgressBar
          current={stages.deep}
          target={totalHours}
          label="Глибокий сон"
          unit="ч"
          showPercentage={false}
        />
        <ProgressBar
          current={stages.rem}
          target={totalHours}
          label="REM сон"
          unit="ч"
          showPercentage={false}
        />
        <ProgressBar
          current={stages.light}
          target={totalHours}
          label="Легкий сон"
          unit="ч"
          showPercentage={false}
        />
        <ProgressBar
          current={stages.awake}
          target={totalHours}
          label="Пробудження"
          unit="ч"
          showPercentage={false}
        />
      </div>

      <div className="pt-6 border-t border-cardBorder">
        <p className="text-sm text-textSec">{notes}</p>
      </div>
    </Card>
  );
}
