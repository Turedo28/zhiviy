'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const sleepData = [
  { day: 'Mon', hours: 7.2 },
  { day: 'Tue', hours: 6.8 },
  { day: 'Wed', hours: 7.5 },
  { day: 'Thu', hours: 6.5 },
  { day: 'Fri', hours: 8.1 },
  { day: 'Sat', hours: 8.3 },
  { day: 'Sun', hours: 7.9 },
];

export default function SleepPanel() {
  return (
    <div className="bg-secondary border border-tertiary rounded-lg p-6">
      <h3 className="text-xl font-semibold text-white mb-4">Sleep</h3>

      <div className="space-y-4">
        {/* Last Night */}
        <div className="bg-tertiary rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-1">Last Night</div>
          <div className="flex items-baseline space-x-2">
            <div className="text-3xl font-bold text-accent">7h 54m</div>
            <div className="text-gray-500 text-sm">REM: 1h 45m</div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Deep: 2h 30m | Light: 3h 39m
          </div>
        </div>

        {/* Chart */}
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={sleepData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262629" />
            <XAxis dataKey="day" stroke="#999999" />
            <YAxis stroke="#999999" domain={[0, 10]} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1d', border: '1px solid #262629' }}
              labelStyle={{ color: '#00d9ff' }}
            />
            <Line
              type="monotone"
              dataKey="hours"
              stroke="#00d9ff"
              dot={{ fill: '#00d9ff', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>

        {/* Status */}
        <div className="bg-tertiary rounded-lg p-3 text-sm">
          <div className="text-gray-400">Sleep Quality Score</div>
          <div className="text-2xl font-bold text-success mt-1">8.5/10</div>
        </div>
      </div>
    </div>
  );
}
