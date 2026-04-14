'use client';

import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import Label from '@/components/ui/Label';

function Tooltip({ text, children }: { text: string; children: React.ReactNode }) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      {children}
      {show && (
        <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 rounded-lg bg-surface border border-border text-xs text-textSec max-w-[240px] text-center shadow-lg whitespace-normal">
          {text}
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px border-4 border-transparent border-t-border" />
        </div>
      )}
    </div>
  );
}

interface VitalMetric {
  value: number;
  unit: string;
  trend?: 'up' | 'down' | 'stable';
}

interface VitalsData {
  hrv: VitalMetric;
  restingHR: VitalMetric;
  spo2: VitalMetric;
  skinTemp: VitalMetric;
  maxHR: VitalMetric;
  activeCal: VitalMetric;
}

const vitalTooltips: Record<string, string> = {
  'HRV': 'Варіабельність серцевого ритму — показник адаптивності організму. Чим вище, тим краще відновлення.',
  'Пульс у спокої': 'Частота серцевих скорочень у стані спокою. Нижчий пульс зазвичай означає кращу фізичну форму.',
  'SpO2': 'Рівень насичення крові киснем. Норма — 95–100%.',
  'Темп. шкіри': 'Температура поверхні шкіри. Підвищення може вказувати на хворобу або перетренованість.',
  'Макс. пульс': 'Максимальна частота серцевих скорочень за день під час навантажень.',
  'Активні ккал': 'Кількість калорій, спалених під час фізичної активності (без базового метаболізму).',
};

export default function VitalsGrid({
  hrv,
  restingHR,
  spo2,
  skinTemp,
  maxHR,
  activeCal,
}: VitalsData) {
  const vitals = [
    { label: 'HRV', data: hrv },
    { label: 'Пульс у спокої', data: restingHR },
    { label: 'SpO2', data: spo2 },
    { label: 'Темп. шкіри', data: skinTemp },
    { label: 'Макс. пульс', data: maxHR },
    { label: 'Активні ккал', data: activeCal },
  ];

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      default:
        return '→';
    }
  };

  const getTrendColor = (trend?: string) => {
    switch (trend) {
      case 'up':
        return '#00D26A';
      case 'down':
        return '#ef4444';
      default:
        return '#999999';
    }
  };

  return (
    <Card>
      <div className="mb-6">
        <Label>Показники здоров&#39;я</Label>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {vitals.map((vital) => (
          <Tooltip key={vital.label} text={vitalTooltips[vital.label] || ''}>
            <div className="glass-card-sm p-4 text-center cursor-help">
              <p className="text-xs text-textDim mb-2">{vital.label}</p>
              <div className="flex items-baseline justify-center gap-1 mb-2">
                <span className="text-2xl font-bold text-text">
                  {typeof vital.data.value === 'number' ? Number(vital.data.value.toFixed(1)) : vital.data.value}
                </span>
                <span className="text-xs text-textSec">{vital.data.unit}</span>
              </div>
              {vital.data.trend && (
                <span
                  style={{ color: getTrendColor(vital.data.trend) }}
                  className="text-sm font-semibold"
                >
                  {getTrendIcon(vital.data.trend)}
                </span>
              )}
            </div>
          </Tooltip>
        ))}
      </div>
    </Card>
  );
}
