'use client';

import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import ProgressBar from '@/components/ui/ProgressBar';
import Label from '@/components/ui/Label';

interface WaterCardProps {
  consumed: number;
  target: number;
  unit: string;
}

export default function WaterCard({ consumed, target, unit }: WaterCardProps) {
  const [total, setTotal] = useState(consumed);

  const handleAddWater = (amount: number) => {
    setTotal(prev => prev + amount);
  };

  return (
    <Card>
      <div className="mb-6">
        <Label>Вода</Label>
      </div>

      <div className="flex items-center gap-6 mb-6">
        <div className="flex-1">
          <ProgressBar
            current={total}
            target={target}
            label={`${total} / ${target} ${unit}`}
            showPercentage={true}
          />
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-accent">
            {Math.round((total / target) * 100)}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <button
          onClick={() => handleAddWater(150)}
          className="glass-card-sm py-3 px-2 text-sm font-semibold text-accent border border-accentBorder hover:bg-accentBg transition"
        >
          +150 мл
        </button>
        <button
          onClick={() => handleAddWater(250)}
          className="glass-card-sm py-3 px-2 text-sm font-semibold text-accent border border-accentBorder hover:bg-accentBg transition"
        >
          +250 мл
        </button>
        <button
          onClick={() => handleAddWater(500)}
          className="glass-card-sm py-3 px-2 text-sm font-semibold text-accent border border-accentBorder hover:bg-accentBg transition"
        >
          +500 мл
        </button>
      </div>
    </Card>
  );
}
