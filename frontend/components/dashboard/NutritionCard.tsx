'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import CircleProgress from '@/components/ui/CircleProgress';
import ProgressBar from '@/components/ui/ProgressBar';
import Label from '@/components/ui/Label';

interface Recommendation {
  type: string;
  icon: string;
  text: string;
}

interface NutritionData {
  calories: { consumed: number; target: number };
  macros: {
    protein: { value: number; target: number; unit: string };
    carbs: { value: number; target: number; unit: string };
    fat: { value: number; target: number; unit: string };
  };
  meals: Array<{ id: string; name: string; time: string; calories: number; items?: string[]; emoji?: string; protein?: number; carbs?: number; fat?: number }>;
  caloriesBurned?: number;
  goalLabel?: string | null;
  tdee?: number | null;
  dayStrain?: number | null;
  recommendations?: Recommendation[];
}

export default function NutritionCard({ calories, macros, meals, caloriesBurned, goalLabel, tdee, dayStrain, recommendations }: NutritionData) {
  const remaining = Math.max(0, calories.target - calories.consumed);

  return (
    <Card>
      {/* Header with goal label */}
      <div className="mb-6 flex items-center justify-between">
        <Label>Харчування</Label>
        {goalLabel && (
          <span className="text-xs font-medium px-3 py-1 rounded-full bg-accent/15 text-accent">
            {goalLabel}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calories Circle */}
        <div className="flex flex-col items-center">
          <div className="relative w-32 h-32 flex items-center justify-center mb-4">
            <CircleProgress
              current={calories.consumed}
              target={calories.target}
              type="calorie"
              size={130}
              strokeWidth={6}
              showLabel={false}
            />
            <div className="absolute text-center">
              <div className="text-2xl font-bold text-text">{Math.round(calories.consumed)}</div>
              <div className="text-xs text-textSec">ккал</div>
            </div>
          </div>
          <p className="text-xs text-textDim">з {calories.target} ккал</p>

          {/* Burned calories & remaining */}
          <div className="mt-3 flex flex-col items-center gap-1">
            {(caloriesBurned ?? 0) > 0 && (
              <div className="flex items-center gap-1.5 text-xs">
                <span className="text-orange-400">🔥</span>
                <span className="text-textSec">Спалено: <span className="font-semibold text-orange-400">{caloriesBurned}</span> ккал</span>
              </div>
            )}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-green-400">🎯</span>
              <span className="text-textSec">Залишилось: <span className="font-semibold text-green-400">{Math.round(remaining)}</span> ккал</span>
            </div>
          </div>
        </div>

        {/* Macros */}
        <div className="lg:col-span-2 space-y-4">
          <ProgressBar
            current={macros.protein.value}
            target={macros.protein.target}
            label="Білки"
            unit={macros.protein.unit}
            showPercentage={false}
          />
          <ProgressBar
            current={macros.carbs.value}
            target={macros.carbs.target}
            label="Вуглеводи"
            unit={macros.carbs.unit}
            showPercentage={false}
          />
          <ProgressBar
            current={macros.fat.value}
            target={macros.fat.target}
            label="Жири"
            unit={macros.fat.unit}
            showPercentage={false}
          />

          {/* TDEE & Strain info */}
          {(tdee || dayStrain !== null) && (
            <div className="flex items-center gap-4 mt-2 pt-3 border-t border-cardBorder">
              {tdee && (
                <div className="text-xs text-textDim">
                  TDEE: <span className="font-semibold text-textSec">{tdee}</span> ккал
                </div>
              )}
              {dayStrain !== null && dayStrain !== undefined && (
                <div className="text-xs text-textDim">
                  Навантаження: <span className="font-semibold text-textSec">{typeof dayStrain === 'number' ? dayStrain.toFixed(1) : dayStrain}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Smart Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="mt-6 pt-4 border-t border-cardBorder">
          <div className="space-y-2">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2.5 px-3 py-2.5 rounded-xl bg-white/5"
              >
                <span className="text-base flex-shrink-0 mt-0.5">{rec.icon}</span>
                <span className="text-sm text-textSec">{rec.text}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Meal Timeline */}
      <div className="mt-8 pt-6 border-t border-cardBorder">
        <h4 className="text-sm font-semibold text-textSec mb-4">Прийом їжі</h4>
        <div className="space-y-3">
          {meals.map((meal, index) => (
            <div key={meal.id} className="flex items-start gap-3">
              <div className="flex flex-col items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full mt-1.5"
                  style={{ backgroundColor: '#fb923c' }}
                />
                {index < meals.length - 1 && (
                  <div
                    className="w-0.5 h-8"
                    style={{ backgroundColor: 'rgba(251,146,60,0.2)' }}
                  />
                )}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm font-semibold text-text">{meal.name}</p>
                    <p className="text-xs text-textDim">{meal.items ? meal.items.join(', ') : `Б:${meal.protein}г В:${meal.carbs}г Ж:${meal.fat}г`}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs font-semibold text-accent">{Math.round(meal.calories)} ккал</p>
                    <p className="text-xs text-textDim">{meal.time}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
