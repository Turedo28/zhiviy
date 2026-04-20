'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

import DashboardHeader from '@/components/layout/DashboardHeader';
import ScoreStrip from '@/components/dashboard/ScoreStrip';
import NutritionCard from '@/components/dashboard/NutritionCard';
import WaterCard from '@/components/dashboard/WaterCard';
import SleepCard from '@/components/dashboard/SleepCard';
import RecoveryCard from '@/components/dashboard/RecoveryCard';
import TrainingPanel from '@/components/dashboard/TrainingPanel';
import VitalsGrid from '@/components/dashboard/VitalsGrid';
import SleepDetail from '@/components/dashboard/SleepDetail';
import TrendsView from '@/components/dashboard/TrendsView';
import { getAuthToken } from '@/lib/auth';

const TABS = ['Сьогодні', 'Показники', 'Тренди'];

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

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
  bed_time: string | null;
  wake_time: string | null;
}

interface RecoveryData {
  score: number | null;
  hrv: number | null;
  resting_hr: number | null;
  spo2: number | null;
  level: string;
}

interface NutritionRecommendation {
  type: string;
  icon: string;
  text: string;
}

interface NutritionPlanData {
  bmr: number;
  tdee: number;
  target_calories: number;
  protein_target: number;
  carbs_target: number;
  fats_target: number;
  goal: string;
  goal_label: string;
  calories_burned: number;
  day_strain: number | null;
  recommendations: NutritionRecommendation[];
}

interface WaterData {
  consumed_ml: number;
  target_ml: number;
  percentage: number;
}

interface WorkoutData {
  sport_name: string;
  duration_min: number;
  strain: number | null;
  calories: number;
  start_time: string;
}

interface DashboardData {
  date: string;
  user_name: string;
  nutrition: NutritionData;
  sleep: SleepData | null;
  recovery: RecoveryData | null;
  water: WaterData | null;
  workouts: WorkoutData[] | null;
  whoop_connected: boolean;
  strain: number | null;
  nutrition_plan: NutritionPlanData | null;
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background flex items-center justify-center"><div className="animate-pulse text-muted-foreground">Завантаження...</div></div>}>
      <Dashboard />
    </Suspense>
  );
}

function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(TABS[0]);
  const [currentDate, setCurrentDate] = useState('');
  const [dashData, setDashData] = useState<DashboardData | null>(null);
  const [userName, setUserName] = useState('Владислав');
  const [whoopConnecting, setWhoopConnecting] = useState(false);
  const [syncStatus, setSyncStatus] = useState<string | null>(null);
  const searchParams = useSearchParams();

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

    // Check if just connected WHOOP
    if (searchParams.get('whoop') === 'connected') {
      setSyncStatus('WHOOP підключено! Дані синхронізуються...');
      // Clean URL
      window.history.replaceState({}, '', '/dashboard');
    }

    // Fetch real data from backend
    fetchDashboardData();
  }, [searchParams]);

  const fetchDashboardData = async () => {
    try {
      const token = getAuthToken();
      let res;

      if (!token) {
        setIsLoading(false);
        return;
      }

      res = await fetch(`${API_URL}/dashboard/today`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const data = await res.json();
        if (!data.error) {
          setDashData(data);
          setUserName(data.user_name || 'Владислав');

          // Auto-sync if WHOOP is connected but no sleep/recovery data
          if (data.whoop_connected && !data.sleep && !data.recovery) {
            triggerSync();
          }
        }
      }
    } catch (err) {
      console.log('Using mock data (backend unavailable)');
    } finally {
      setIsLoading(false);
      // Clear sync status after data loads
      setTimeout(() => setSyncStatus(null), 3000);
    }
  };

  const connectWhoop = async () => {
    setWhoopConnecting(true);
    try {
      const token = getAuthToken();
      if (!token) {
        alert('Спочатку авторизуйтесь через Telegram');
        return;
      }
      const res = await fetch(`${API_URL}/integrations/whoop/auth-url`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        window.location.href = data.auth_url;
      } else {
        alert('Помилка отримання URL авторизації WHOOP');
      }
    } catch (err) {
      alert('Помилка підключення до WHOOP');
    } finally {
      setWhoopConnecting(false);
    }
  };

  const triggerSync = async () => {
    try {
      const token = getAuthToken();
      if (!token) return;
      setSyncStatus('Синхронізація WHOOP...');
      const res = await fetch(`${API_URL}/integrations/whoop/sync`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setSyncStatus('Дані синхронізовано!');
        // Refetch dashboard data
        setTimeout(() => fetchDashboardData(), 500);
      }
    } catch (err) {
      setSyncStatus(null);
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
        const hasSleep = dashData?.sleep != null;
        const hasRecovery = dashData?.recovery != null;
        const hasWhoop = dashData?.whoop_connected ?? false;

        const sleepScore = hasSleep ? dashData.sleep!.score : null;
        const recoveryScore = hasRecovery ? dashData.recovery!.score : null;

        const sleepHours = hasSleep ? dashData.sleep!.hours : 0;
        const sleepStages = hasSleep
          ? {
              deep: dashData.sleep!.deep_hours,
              rem: dashData.sleep!.rem_hours,
              light: dashData.sleep!.light_hours,
              awake: dashData.sleep!.awake_hours,
            }
          : { deep: 0, rem: 0, light: 0, awake: 0 };

        const rawLevel = dashData?.recovery?.level;
        const recoveryLevel: 'high' | 'medium' | 'low' = rawLevel === 'green' ? 'high' : rawLevel === 'yellow' ? 'medium' : rawLevel === 'red' ? 'low' : 'medium';
        const recoveryScoreVal = hasRecovery ? dashData.recovery!.score : null;
        const recoveryRec = !hasRecovery
          ? 'Дані відновлення відсутні'
          : recoveryLevel === 'high'
          ? 'Відмінне відновлення. Готові до навантажень!'
          : recoveryLevel === 'medium'
          ? 'Помірне відновлення. Тренуйтесь з обережністю.'
          : 'Низьке відновлення. Рекомендований відпочинок.';

        return (
          <div className="space-y-6">
            {/* Score Strip — only show real scores */}
            <ScoreStrip
              recovery={recoveryScore ?? 0}
              sleep={sleepScore ?? 0}
              strain={dashData?.strain ?? 0}
            />

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Nutrition - spans 2 columns */}
              <div className="lg:col-span-2">
                <NutritionCard
                  calories={nutritionData.calories}
                  macros={nutritionData.macros}
                  meals={nutritionData.meals}
                  caloriesBurned={dashData?.nutrition_plan?.calories_burned ?? 0}
                  goalLabel={dashData?.nutrition_plan?.goal_label ?? null}
                  tdee={dashData?.nutrition_plan?.tdee ?? null}
                  dayStrain={dashData?.nutrition_plan?.day_strain ?? null}
                  recommendations={dashData?.nutrition_plan?.recommendations ?? []}
                />
              </div>

              {/* Sleep Mini or empty state */}
              {hasSleep ? (
                <SleepCard hours={sleepHours} stages={sleepStages} />
              ) : (
                <div className="bg-card rounded-2xl border border-white/10 p-6 flex flex-col items-center justify-center text-center">
                  <span className="text-3xl mb-3">😴</span>
                  <p className="text-textSec font-medium">Немає даних сну</p>
                  <p className="text-textDim text-sm mt-1">
                    {hasWhoop ? 'Дані WHOOP за сьогодні ще не синхронізовані' : 'Підключіть WHOOP для відстеження сну'}
                  </p>
                  {!hasWhoop && (
                    <button
                      onClick={connectWhoop}
                      disabled={whoopConnecting}
                      className="mt-3 px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium hover:bg-accent/80 transition-colors disabled:opacity-50"
                    >
                      {whoopConnecting ? 'Підключення...' : 'Підключити WHOOP'}
                    </button>
                  )}
                  {hasWhoop && !hasSleep && (
                    <button
                      onClick={triggerSync}
                      className="mt-3 px-4 py-2 bg-white/10 text-textSec rounded-lg text-sm font-medium hover:bg-white/20 transition-colors"
                    >
                      Синхронізувати
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Training Panel — only show if WHOOP connected */}
            {hasWhoop && (
              <TrainingPanel
                workouts={Array.isArray(dashData?.workouts) ? dashData.workouts : (dashData?.workouts?.workouts ?? [])}
                dayStrain={dashData?.strain ?? null}
                caloriesBurned={dashData?.nutrition_plan?.calories_burned ?? 0}
              />
            )}

            {/* Bottom Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Water - spans 2 columns */}
              <div className="lg:col-span-2">
                <WaterCard
                  consumed={dashData?.water?.consumed_ml ?? 0}
                  target={dashData?.water?.target_ml ?? 2500}
                  unit="мл"
                />
              </div>

              {/* Recovery Card or empty state */}
              {hasRecovery ? (
                <RecoveryCard
                  score={recoveryScoreVal ?? 0}
                  recommendation={recoveryRec}
                  level={recoveryLevel}
                />
              ) : (
                <div className="bg-card rounded-2xl border border-white/10 p-6 flex flex-col items-center justify-center text-center">
                  <span className="text-3xl mb-3">💚</span>
                  <p className="text-textSec font-medium">Немає даних відновлення</p>
                  <p className="text-textDim text-sm mt-1">
                    {hasWhoop ? 'Дані WHOOP за сьогодні ще не синхронізовані' : 'Підключіть WHOOP для аналізу відновлення'}
                  </p>
                  {!hasWhoop && (
                    <button
                      onClick={connectWhoop}
                      disabled={whoopConnecting}
                      className="mt-3 px-4 py-2 bg-accent text-black rounded-lg text-sm font-medium hover:bg-accent/80 transition-colors disabled:opacity-50"
                    >
                      {whoopConnecting ? 'Підключення...' : 'Підключити WHOOP'}
                    </button>
                  )}
                </div>
              )}
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
        const hasRecovery2 = dashData?.recovery != null;
        const hasSleep2 = dashData?.sleep != null;
        const hasWhoop2 = dashData?.whoop_connected ?? false;

        const vitalsData = hasRecovery2
          ? {
              hrv: { value: dashData.recovery!.hrv ?? 0, unit: 'мс', trend: 'stable' as const },
              restingHR: { value: dashData.recovery!.resting_hr ?? 0, unit: 'уд/хв', trend: 'stable' as const },
              spo2: { value: dashData.recovery!.spo2 ?? 0, unit: '%', trend: 'stable' as const },
              skinTemp: { value: 0, unit: '°C', trend: 'stable' as const },
              maxHR: { value: 0, unit: 'уд/хв', trend: 'stable' as const },
              activeCal: { value: 0, unit: 'kcal', trend: 'stable' as const },
            }
          : null;

        const sleepDetailData = hasSleep2
          ? {
              hours: dashData.sleep!.hours,
              score: dashData.sleep!.score ?? 0,
              efficiency: dashData.sleep!.efficiency ?? 0,
              bedTime: dashData.sleep!.bed_time ?? undefined,
              wakeTime: dashData.sleep!.wake_time ?? undefined,
              stages: {
                deep: dashData.sleep!.deep_hours,
                rem: dashData.sleep!.rem_hours,
                light: dashData.sleep!.light_hours,
                awake: dashData.sleep!.awake_hours,
              },
            }
          : null;

        const rawLevel2 = dashData?.recovery?.level;
        const recLevel2: 'high' | 'medium' | 'low' = rawLevel2 === 'green' ? 'high' : rawLevel2 === 'yellow' ? 'medium' : rawLevel2 === 'red' ? 'low' : 'medium';
        const recScore2 = hasRecovery2 ? dashData.recovery!.score : null;
        const recRec2 = !hasRecovery2
          ? 'Дані відновлення відсутні'
          : recLevel2 === 'high'
          ? 'Відмінне відновлення. Готові до навантажень!'
          : recLevel2 === 'medium'
          ? 'Помірне відновлення. Тренуйтесь з обережністю.'
          : 'Низьке відновлення. Рекомендований відпочинок.';

        const emptyHint = hasWhoop2
          ? 'Дані WHOOP за сьогодні ще не синхронізовані'
          : 'Підключіть WHOOP для відстеження показників';

        return (
          <div className="space-y-6">
            {!hasWhoop2 && (
              <div className="bg-accent/10 border border-accent/30 rounded-xl p-4 flex items-center justify-between">
                <div>
                  <p className="text-accent font-medium">Підключіть WHOOP для повної аналітики</p>
                  <p className="text-textDim text-sm mt-1">Сон, відновлення, HRV, пульс та інші показники</p>
                </div>
                <button
                  onClick={connectWhoop}
                  disabled={whoopConnecting}
                  className="px-5 py-2 bg-accent text-black rounded-lg text-sm font-medium hover:bg-accent/80 transition-colors disabled:opacity-50 whitespace-nowrap"
                >
                  {whoopConnecting ? 'Підключення...' : 'Підключити WHOOP'}
                </button>
              </div>
            )}
            {hasRecovery2 ? (
              <RecoveryCard
                score={recScore2 ?? 0}
                recommendation={recRec2}
                level={recLevel2}
              />
            ) : (
              <div className="bg-card rounded-2xl border border-white/10 p-6 text-center">
                <span className="text-3xl">💚</span>
                <p className="text-textSec font-medium mt-2">Немає даних відновлення</p>
                <p className="text-textDim text-sm mt-1">{emptyHint}</p>
              </div>
            )}
            {vitalsData ? (
              <VitalsGrid {...vitalsData} />
            ) : (
              <div className="bg-card rounded-2xl border border-white/10 p-6 text-center">
                <span className="text-3xl">📊</span>
                <p className="text-textSec font-medium mt-2">Немає даних показників</p>
                <p className="text-textDim text-sm mt-1">{emptyHint}</p>
              </div>
            )}
            {sleepDetailData ? (
              <SleepDetail {...sleepDetailData} />
            ) : (
              <div className="bg-card rounded-2xl border border-white/10 p-6 text-center">
                <span className="text-3xl">😴</span>
                <p className="text-textSec font-medium mt-2">Немає деталей сну</p>
                <p className="text-textDim text-sm mt-1">{emptyHint}</p>
              </div>
            )}
          </div>
        );

      case 'Тренди':
        return (
          <TrendsView />
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

      {/* Sync Status Banner */}
      {syncStatus && (
        <div className="max-w-7xl mx-auto px-4 pt-4 sm:px-6 lg:px-8">
          <div className="bg-accent/10 border border-accent/30 rounded-xl p-3 text-center text-accent text-sm font-medium">
            {syncStatus}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {renderContent()}
      </div>
    </main>
  );
}
