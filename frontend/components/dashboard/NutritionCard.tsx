'use client';

import React from 'react';
import Card from '@/components/ui/Card';
import CircleProgress from '@/components/ui/CircleProgress';
import ProgressBar from '@/components/ui/ProgressBar';
import Label from '@/components/ui/Label';

interface NutritionData {
  calories: { consumed: number; target: number };
  macros: {
    protein: { value: number; target: number; unit: string };
    carbs: { value: number; target: number; unit: string };
    fat: { value: number; target: number; unit: string };
  };
  meals: Array<{ id: string; name: string; time: string; calories: number; items: string[] }>;
}

export default function NutritionCard({ calories, macros, meals }: NutritionData) {
  return (
    <Card>
      <div className="mb-6">
        <Label>Харчування</Label>
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
              <div className="text-xs text-textSec">кал</div>
            </div>
          </div>
          <p className="text-xs text-textDim">z {calories.target} кал</p>
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
        </div>
      </div>

      {/* Meal Timeline */}
      <div className="mt-8 pt-6 border-t border-cardBorder">
        <h4 className="text-sm font-semibold text-textSec mb-4">Прием їжі</h4>
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
                    <p className="text-xs font-semibold text-accent">{meal.calories} кал</p>
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
