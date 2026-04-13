'use client';

import { useEffect, useState } from 'react';

import DashboardHeader from '@/components/layout/DashboardHeader';
import ScoreStrip from '@/components/dashboard/ScoreStrip';
import NutritionCard from '@/components/dashboard/NutritionCard';
import WaterCard from '@/components/dashboard/WaterCard';
import SleepCard from '@/components/dashboard/SleepCard';
import RecoveryCard from '@/components/dashboard/RecoveryCard';
import VitalsGrid from '@/components/dashboard/VitalsGrid';
import SleepDetail from '@/components/dashboard/SleepDetail';
import TrendsView from '@/components/dashboard/TrendsView';
import { getAuthToken } from '@/lib/auth';
import {
  mockTodayMetrics,
  mockWater,
  mockSleep,
  mockVitals,
  mockRecovery,
  mockSleepDetail,
  mockWeeklyData,
  mockAverageMacros,
} from '@/lib/mockData';

const TABS = ['Сьогодні', 'Показники', 'Тренди'];

// Fallback for demo mode when no JWT token
const DEMO_TELEGRAM_ID = 470208930;
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface MealData {
  id: number;
  name: string;
  description: string | null;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  time: string;
  source: string;
}

interface NutritionData {
  calories_consumed: number;
  calories_target: number;
  protein_g: number;
  protein_target: number;
  carbs_g: number;
  carbs_target: number;
  fats_g: number;
  fats_target: number;
  meals: MealData[];
}

interface SleepData {
  hours: number;
  score: number | null;
  efficiency: number | null;
  deep_hours: number;
  rem_hours: number;
  light_hours: number;
  awake_hours: number;
}

interface RecoveryData {
  score: number | null;
  hrv: number | null;
  resting_hr: number | null;
  spo2: number | null;
  level: string;
}

interface DashboardData {
  date: string;
  user_name: string;
  nutrition: NutritionData;
  sleep: SleepData | null;
  recovery: RecoveryData | null;
  whoop_connected: boolean;
}

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(TABS[0]);
  const [currentDate, setCurrentDate] = useState('');
  const [dashData, setDashData] = useState<DashboardData | null>(null);
  const [userName, setUserName] = useState('Владислав');

  useEffect(() => {
    // Set current date
    const today = new Date();
    const formatter = new Intl.DateTimeFormat('uk-UA', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    setCurrentDate(formatter.format(today));

    // Fetch real data from backend
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = getAuthToken();
      let res;

      if (token) {
        // Authenticated — use real JWT endpoint
        res = await fetch(`${API_URL}/dashboard/today`, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }

      // Fallback to demo endpoint
      if (!res || !res.ok) {
        res = await fetch(`${API_URL}/dashboard/today/demo?telegram_id=${DEMO_TELEGRAM_ID}`);
      }

      if (res.ok) {
        const data = await res.json();
        if (!data.error) {
          setDashData(data);
          setUserName(data.user_name || 'Владислав');
        }
      }
    } catch (err) {
      console.log('Using mock data (backend unavailable)');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
          <p className="mt-4 text-textSec">Завантаження...</p>
        </div>
      </div>
    );
  }

  // Build nutrition data from real API or mock
  const nutritionData = dashData
    ? {
        calories: {
          consumed: dashData.nutrition.calories_consumed,
          target: dashData.nutrition.calories_target,
        },
        macros: {
          protein: { value: dashData.nutrition.protein_g, target: dashData.nutrition.protein_target, unit: 'г' },
          carbs: { value: dashData.nutrition.carbs_g, target: dashData.nutrition.carbs_target, unit: 'г' },
          fat: { value: dashData.nutrition.fats_g, target: dashData.nutrition.fats_target, unit: 'г' },
        },
        meals: dashData.nutrition.meals.map((m) => ({
          id: String(m.id),
          name: m.name,
          time: m.time,
          calories: m.calories,
          emoji: m.source === 'telegram' ? '📸' : '🍽',
          protein: m.protein_g,
          carbs: m.carbs_g,
          fat: m.fats_g,
        })),
      }
    : {
        calories: { consumed: 0, target: 2100 },
        macros: {
          protein: { value: 0, target: 160, unit: 'г' },
          carbs: { value: 0, target: 220, unit: 'г' },
          fat: { value: 0, target: 70, unit: 'г' },
        },
        meals: [],
      };

  const renderContent = () => {
    switch (activeTab) {
      case 'Сьогодні':
        const sleepScore = dashData?.sleep?.score ?? mockTodayMetrics.sleep;
        const recoveryScore = dashData?.recovery?.score ?? mockTodayMetrics.recovery;
        const strainValue = mockTodayMetrics.strain; // strain comes from cycles, keep mock for now

        const sleepHours = dashData?.sleep?.hours ?? mockSleep.hours;
        const sleepStages = dashData?.sleep
          ? {
              deep: dashData.sleep.deep_hours,
              rem: dashData.sleep.rem_hours,
              light: dashData.sleep.light_hours,
              awake: dashData.sleep.awake_hours,
            }
          : mockSleep.stages;

        const recoveryLevel = dashData?.recovery?.level ?? mockRecovery.level;
        const recoveryScoreVal = dashData?.recovery?.score ?? mockRecovery.score;
        const recoveryRec = recoveryLevel === 'green'
          ? 'Відмінне відновлення. Готові до навантажень!'
          : recoveryLevel === 'yellow'
          ? 'Помірне відновлення. Тренуйтесь з обережністю.'
          : 'Низьке відновлення. Рекомендований відпочинок.';

        return (
          <div className="space-y-6">
            {/* Score Strip */}
            <ScoreStrip
              recovery={recoveryScore ?? 0}
              sleep={sleepScore ?? 0}
              strain={strainValue}
            />

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Nutrition - spans 2 columns */}
              <div className="lg:col-span-2">
                <NutritionCard
                  calories={nutritionData.calories}
                  macros={nutritionData.macros}
                  meals={nutritionData.meals}
                />
              </div>

              {/* Sleep Mini */}
              <SleepCard hours={sleepHours} stages={sleepStages} />
            </div>

            {/* Bottom Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Water - spans 2 columns */}
              <div className="lg:col-span-2">
                <WaterCard
                  consumed={mockWater.consumed}
                  target={mockWater.target}
                  unit={mockWater.unit}
                />
              </div>

              {/* Recovery Card */}
              <RecoveryCard
                score={recoveryScoreVal}
                recommendation={recoveryRec}
                level={recoveryLevel}
              />
            </div>

            {/* No meals hint */}
            {nutritionData.meals.length === 0 && (
              <div className="text-center py-8 bg-white/5 rounded-2xl border border-white/10">
                <p className="text-textSec text-lg">📷 Надішліть фото їжі боту <b>@zhiviy_bot</b> в Telegram</p>
                <p className="text-textDim text-sm mt-2">Дані з'являться тут автоматично</p>
              </div>
            )}
          </div>
        );

      case 'Показники':
        const vitalsData = dashData?.recovery
          ? {
              hrv: dashData.recovery.hrv ?? mockVitals.hrv,
              restingHr: dashData.recovery.resting_hr ?? mockVitals.restingHr,
              spo2: dashData.recovery.spo2 ?? mockVitals.spo2,
              skinTemp: mockVitals.skinTemp,
            }
          : mockVitals;

        const sleepDetailData = dashData?.sleep
          ? {
              hours: dashData.sleep.hours,
              score: dashData.sleep.score ?? 0,
              efficiency: dashData.sleep.efficiency ?? 0,
              stages: {
                deep: dashData.sleep.deep_hours,
                rem: dashData.sleep.rem_hours,
                light: dashData.sleep.light_hours,
                awake: dashData.sleep.awake_hours,
              },
            }
          : mockSleepDetail;

        const recLevel2 = dashData?.recovery?.level ?? mockRecovery.level;
        const recScore2 = dashData?.recovery?.score ?? mockRecovery.score;
        const recRec2 = recLevel2 === 'green'
          ? 'Відмінне відновлення. Готові до навантажень!'
          : recLevel2 === 'yellow'
          ? 'Помірне відновлення. Тренуйтесь з обережністю.'
          : 'Низьке відновлення. Рекомендований відпочинок.';

        return (
          <div className="space-y-6">
            <RecoveryCard
              score={recScore2}
              recommendation={recRec2}
              level={recLevel2}
            />
            <VitalsGrid {...vitalsData} />
            <SleepDetail {...sleepDetailData} />
          </div>
        );

      case 'Тренди':
        return (
          <TrendsView data={mockWeeklyData} averageMacros={mockAverageMacros} />
        );

      default:
        return null;
    }
  };

  return (
    <main className="min-h-screen bg-bg">
      {/* Header */}
      <DashboardHeader
        avatar={userName.charAt(0).toUpperCase()}
        name={userName}
        currentDate={currentDate}
        tabs={TABS}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {renderContent()}
      </div>
    </main>
  );
}
