'use client';

import { useState } from 'react';

export default function WaterPanel() {
  const [waterIntake, setWaterIntake] = useState(1850); // ml
  const dailyGoal = 2000; // ml
  const percentage = (waterIntake / dailyGoal) * 100;

  const addWater = (amount: number) => {
    setWaterIntake(prev => prev + amount);
  };

  return (
    <div className="bg-secondary border border-tertiary rounded-lg p-6">
      <h3 className="text-xl font-semibold text-white mb-4">Hydration</h3>

      <div className="space-y-4">
        {/* Water Intake */}
        <div className="bg-tertiary rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-400 text-sm">Daily Intake</span>
            <span className="text-accent font-semibold">{waterIntake}ml</span>
          </div>
          <div className="flex justify-between items-center text-xs text-gray-500 mb-3">
            <span>Goal: {dailyGoal}ml</span>
            <span>{Math.round(percentage)}%</span>
          </div>
          <div className="w-full bg-tertiary rounded-full h-3">
            <div
              className="bg-accent h-3 rounded-full transition-all"
              style={{ width: `${Math.min(percentage, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Quick Add Buttons */}
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => addWater(250)}
            className="bg-tertiary hover:bg-secondary border border-tertiary hover:border-accent rounded-lg p-3 transition text-center"
          >
            <div className="text-sm font-semibold text-white">250ml</div>
            <div className="text-xs text-gray-500">Glass</div>
          </button>
          <button
            onClick={() => addWater(500)}
            className="bg-tertiary hover:bg-secondary border border-tertiary hover:border-accent rounded-lg p-3 transition text-center"
          >
            <div className="text-sm font-semibold text-white">500ml</div>
            <div className="text-xs text-gray-500">Bottle</div>
          </button>
          <button
            onClick={() => addWater(750)}
            className="bg-tertiary hover:bg-secondary border border-tertiary hover:border-accent rounded-lg p-3 transition text-center"
          >
            <div className="text-sm font-semibold text-white">750ml</div>
            <div className="text-xs text-gray-500">Large</div>
          </button>
        </div>

        {/* Reminder */}
        <div className="bg-tertiary rounded-lg p-3 text-sm text-gray-400">
          💧 Great hydration! Keep it up!
        </div>
      </div>
    </div>
  );
}
