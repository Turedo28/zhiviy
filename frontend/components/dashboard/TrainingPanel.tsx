'use client';

import Card from '@/components/ui/Card';
import Label from '@/components/ui/Label';

interface Workout {
  sport_name: string;
  duration_min: number;
  strain: number | null;
  calories: number;
  start_time: string;
}

interface TrainingPanelProps {
  workouts: Workout[];
  dayStrain: number | null;
  caloriesBurned: number;
}

export default function TrainingPanel({ workouts, dayStrain, caloriesBurned }: TrainingPanelProps) {
  const totalDuration = workouts.reduce((sum, w) => sum + w.duration_min, 0);
  const strainLabel = dayStrain != null
    ? dayStrain >= 14 ? 'Висока інтенсивність'
      : dayStrain >= 8 ? 'Помірна інтенсивність'
      : 'Легка інтенсивність'
    : 'Немає даних';

  const strainColor = dayStrain != null
    ? dayStrain >= 14 ? 'text-red-400'
      : dayStrain >= 8 ? 'text-yellow-400'
      : 'text-green-400'
    : 'text-textDim';

  return (
    <Card>
      <div className="mb-6">
        <Label>Тренування</Label>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="glass-card-sm p-3 text-center">
          <div className="text-textDim text-xs mb-1">Навантаження</div>
          <div className={`text-2xl font-bold ${strainColor}`}>
            {dayStrain != null ? dayStrain.toFixed(1) : '—'}
          </div>
          <div className="text-textDim text-xs mt-1">{strainLabel}</div>
        </div>
        <div className="glass-card-sm p-3 text-center">
          <div className="text-textDim text-xs mb-1">Тренувань</div>
          <div className="text-2xl font-bold text-accent">
            {workouts.length}
          </div>
          <div className="text-textDim text-xs mt-1">{totalDuration} хв</div>
        </div>
        <div className="glass-card-sm p-3 text-center">
          <div className="text-textDim text-xs mb-1">Спалено</div>
          <div className="text-2xl font-bold text-green-400">
            {caloriesBurned}
          </div>
          <div className="text-textDim text-xs mt-1">ккал</div>
        </div>
      </div>

      {/* Workout List */}
      {workouts.length > 0 ? (
        <div className="space-y-2">
          {workouts.map((w, i) => (
            <div key={i} className="glass-card-sm p-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-lg">🏋️</span>
                <div>
                  <div className="text-sm font-medium text-textMain">{w.sport_name}</div>
                  <div className="text-xs text-textDim">{w.start_time} · {w.duration_min} хв</div>
                </div>
              </div>
              <div className="text-right">
                {w.strain != null && (
                  <div className="text-sm font-semibold text-accent">{w.strain}</div>
                )}
                <div className="text-xs text-textDim">{w.calories} ккал</div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-4">
          <span className="text-2xl mb-2 block">🏃</span>
          <p className="text-textDim text-sm">Сьогодні тренувань немає</p>
        </div>
      )}
    </Card>
  );
}
