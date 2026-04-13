'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const workoutData = [
  { day: 'Mon', strain: 7.2 },
  { day: 'Tue', strain: 5.8 },
  { day: 'Wed', strain: 8.5 },
  { day: 'Thu', strain: 6.5 },
  { day: 'Fri', strain: 7.1 },
  { day: 'Sat', strain: 8.3 },
  { day: 'Sun', strain: 4.5 },
];

export default function TrainingPanel() {
  return (
    <div className="bg-secondary border border-tertiary rounded-lg p-6">
      <h3 className="text-xl font-semibold text-white mb-6">Training</h3>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Today's Strain */}
        <div className="bg-tertiary rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">Today's Strain</div>
          <div className="text-4xl font-bold text-warning mb-1">6.8</div>
          <div className="text-gray-500 text-sm">Moderate intensity</div>
        </div>

        {/* This Week */}
        <div className="bg-tertiary rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">Weekly Average</div>
          <div className="text-4xl font-bold text-accent mb-1">7.1</div>
          <div className="text-gray-500 text-sm">53 min avg duration</div>
        </div>

        {/* Calories Burned */}
        <div className="bg-tertiary rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">Calories Burned</div>
          <div className="text-4xl font-bold text-success mb-1">487</div>
          <div className="text-gray-500 text-sm">kcal today</div>
        </div>
      </div>

      {/* Weekly Chart */}
      <div>
        <h4 className="text-sm font-semibold text-white mb-4">Weekly Strain</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={workoutData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262629" />
            <XAxis dataKey="day" stroke="#999999" />
            <YAxis stroke="#999999" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1d', border: '1px solid #262629' }}
              labelStyle={{ color: '#ffb000' }}
            />
            <Bar dataKey="strain" fill="#ffb000" name="Strain Score" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
