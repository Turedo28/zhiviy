'use client';

import React, { useState, useCallback } from 'react';
import Card from '@/components/ui/Card';
import ProgressBar from '@/components/ui/ProgressBar';
import Label from '@/components/ui/Label';
import { getAuthToken } from '@/lib/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

interface WaterCardProps {
  consumed: number;
  target: number;
  unit: string;
  onUpdate?: (newTotal: number) => void;
}

export default function WaterCard({ consumed, target, unit, onUpdate }: WaterCardProps) {
  const [total, setTotal] = useState(consumed);
  const [isAdding, setIsAdding] = useState(false);

  const handleAddWater = useCallback(async (amount: number) => {
    // Optimistic update
    setTotal(prev => prev + amount);
    setIsAdding(true);

    try {
      const token = getAuthToken();
      if (!token) return;

      const res = await fetch(`${API_URL}/water`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ amount_ml: amount }),
      });

      if (res.ok) {
        const data = await res.json();
        setTotal(data.total_today_ml);
        onUpdate?.(data.total_today_ml);
      } else {
        // Revert on error
        setTotal(prev => prev - amount);
      }
    } catch {
      // Revert on network error
      setTotal(prev => prev - amount);
    } finally {
      setIsAdding(false);
    }
  }, [onUpdate]);

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
            {target > 0 ? Math.round((total / target) * 100) : 0}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <button
          onClick={() => handleAddWater(150)}
          disabled={isAdding}
          className="glass-card-sm py-3 px-2 text-sm font-semibold text-accent border border-accentBorder hover:bg-accentBg transition disabled:opacity-50"
        >
          +150 мл
        </button>
        <button
          onClick={() => handleAddWater(250)}
          disabled={isAdding}
          className="glass-card-sm py-3 px-2 text-sm font-semibold text-accent border border-accentBorder hover:bg-accentBg transition disabled:opacity-50"
        >
          +250 мл
        </button>
        <button
          onClick={() => handleAddWater(500)}
          disabled={isAdding}
          className="glass-card-sm py-3 px-2 text-sm font-semibold text-accent border border-accentBorder hover:bg-accentBg transition disabled:opacity-50"
        >
          +500 мл
        </button>
      </div>
    </Card>
  );
}
