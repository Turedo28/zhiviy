'use client';

import React, { useEffect, useState } from 'react';
import Card from '@/components/ui/Card';
import Label from '@/components/ui/Label';
import WeeklyChart from '@/components/ui/WeeklyChart';
import { getAuthToken } from '@/lib/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';
const DEMO_TELEGRAM_ID = 470208930;

interface DataPoint {
  day: string;
  value: number;
}

interface TrendsData {
  calories: DataPoint[];
  sleep: DataPoint[];
  recovery: DataPoint[];
  strain: DataPoint[];
  water?: DataPoint[];
}

interface AverageMacros {
  protein: number;
  carbs: number;
  fat: number;
}

export default function TrendsView() {
  const [data, setData] = useState<TrendsData | null>(null);
  const [averageMacros, setAverageMacros] = useState<AverageMacros>({ protein: 0, carbs: 0, fat: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [days, setDays] = useState(7);

  useEffect(() => {
    fetchTrends();
  }, [days]);

  const fetchTrends = async () => {
    setIsLoading(true);
    try {
      const token = getAuthToken();
      let res;

      if (token) {
        res = await fetch(`${API_URL}/stats/weekly?days=${days}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }

      if (!res || !res.ok) {
        res = await fetch(`${API_URL}/stats/weekly/demo?telegram_id=${DEMO_TELEGRAM_ID}&days=${days}`);
      }

      if (res.ok) {
        const json = await res.json();
        if (!json.error) {
          setData({
            calories: json.calories,
            sleep: json.sleep,
            recovery: json.recovery,
            strain: json.strain,
            water: json.water,
          });
          setAverageMacros(json.avg_macros);
        }
      }
    } catch (err) {
      console.log('Failed to fetch trends data');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card>
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
            <span className="ml-3 text-textDim">Завантаження трендів...</span>
          </div>
        </Card>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6">
        <Card>
          <div className="text-center py-12">
            <span className="text-3xl mb-3 block">📊</span>
            <p className="text-textSec">Недостатньо даних для відображення трендів</p>
            <p className="text-textDim text-sm mt-1">Додавайте їжу та тренуйтесь — дані з'являться тут</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Period toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => setDays(7)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            days === 7 ? 'bg-accent text-black' : 'glass-card-sm text-textSec hover:text-textMain'
          }`}
        >
          7 днів
        </button>
        <button
          onClick={() => setDays(14)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            days === 14 ? 'bg-accent text-black' : 'glass-card-sm text-textSec hover:text-textMain'
          }`}
        >
          14 днів
        </button>
        <button
          onClick={() => setDays(30)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            days === 30 ? 'bg-accent text-black' : 'glass-card-sm text-textSec hover:text-textMain'
          }`}
        >
          30 днів
        </button>
      </div>

      {/* Calories */}
      <Card>
        <Label>Калорії</Label>
        <WeeklyChart data={data.calories} color="#fb923c" showValues={true} />
      </Card>

      {/* Sleep */}
      <Card>
        <Label>Сон</Label>
        <WeeklyChart data={data.sleep} color="#a78bfa" showValues={true} maxValue={10} />
      </Card>

      {/* Recovery */}
      <Card>
        <Label>Відновлення</Label>
        <WeeklyChart data={data.recovery} color="#00D26A" showValues={true} maxValue={100} />
      </Card>

      {/* Strain */}
      <Card>
        <Label>Навантаження</Label>
        <WeeklyChart data={data.strain} color="#ef4444" showValues={true} maxValue={21} />
      </Card>

      {/* Average Macros */}
      <Card>
        <Label>Середні макроелементи за період</Label>
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
