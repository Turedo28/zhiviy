'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import Label from '@/components/ui/Label';

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
    { label: 'Спокійний HR', data: restingHR },
    { label: 'SpO2', data: spo2 },
    { label: 'Темп. шкіри', data: skinTemp },
    { label: 'Макс. HR', data: maxHR },
    { label: 'Активні кал', data: activeCal },
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
        <Label>Vita Metrics</Label>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {vitals.map((vital) => (
          <div
            key={vital.label}
            className="glass-card-sm p-4 text-center"
          >
            <p className="text-xs text-textDim mb-2">{vital.label}</p>
            <div className="flex items-baseline justify-center gap-1 mb-2">
              <span className="text-2xl font-bold text-text">{vital.data.value}</span>
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
        ))}
      </div>
    </Card>
  );
}
