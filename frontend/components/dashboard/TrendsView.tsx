'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import Label from '@/components/ui/Label';
import WeeklyChart from '@/components/ui/WeeklyChart';

interface DataPoint {
  day: string;
  value: number;
}

interface TrendsData {
  calories: DataPoint[];
  sleep: DataPoint[];
  recovery: DataPoint[];
  strain: DataPoint[];
}

interface AverageMacros {
  protein: number;
  carbs: number;
  fat: number;
}

interface TrendsViewProps {
  data: TrendsData;
  averageMacros: AverageMacros;
}

export default function TrendsView({ data, averageMacros }: TrendsViewProps) {
  return (
    <div className="space-y-6">
      {/* Calories */}
      <Card>
        <Label>Тижневі калорії</Label>
        <WeeklyChart data={data.calories} color="#fb923c" showValues={true} />
      </Card>

      {/* Sleep */}
      <Card>
        <Label>Тижневий сон</Label>
        <WeeklyChart data={data.sleep} color="#a78bfa" showValues={true} maxValue={10} />
      </Card>

      {/* Recovery */}
      <Card>
        <Label>Тижневе відновлення</Label>
        <WeeklyChart data={data.recovery} color="#00D26A" showValues={true} maxValue={100} />
      </Card>

      {/* Strain */}
      <Card>
        <Label>Тижнева напруга</Label>
        <WeeklyChart data={data.strain} color="#ef4444" showValues={true} maxValue={12} />
      </Card>

      {/* Average Macros */}
      <Card>
        <Label>Середні макроелементи на тиждень</Label>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center glass-card-sm p-4">
            <div className="w-16 h-16 mx-auto mb-3 rounded-full flex items-center justify-center" style={{ backgroundColor: 'rgba(251,146,60,0.1)', border: '2px solid #fb923c' }}>
              <span className="text-xl font-bold text-accent">{averageMacros.protein}</span>
            </div>
            <p className="text-xs text-textDim">Білки (г)</p>
          </div>
          <div className="text-center glass-card-sm p-4">
            <div className="w-16 h-16 mx-auto mb-3 rounded-full flex items-center justify-center" style={{ backgroundColor: 'rgba(168,139,250,0.1)', border: '2px solid #a78bfa' }}>
              <span className="text-xl font-bold text-purple">{averageMacros.carbs}</span>
            </div>
            <p className="text-xs text-textDim">Вуглеводи (г)</p>
          </div>
          <div className="text-center glass-card-sm p-4">
            <div className="w-16 h-16 mx-auto mb-3 rounded-full flex items-center justify-center" style={{ backgroundColor: 'rgba(56,189,248,0.1)', border: '2px solid #38bdf8' }}>
              <span className="text-xl font-bold text-blue">{averageMacros.fat}</span>
            </div>
            <p className="text-xs text-textDim">Жири (г)</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
