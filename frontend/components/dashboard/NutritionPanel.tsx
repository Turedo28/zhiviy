'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const macroData = [
  { name: 'Protein', value: 85, goal: 150 },
  { name: 'Carbs', value: 220, goal: 250 },
  { name: 'Fats', value: 60, goal: 70 },
];

const caloriesData = [
  { name: 'Breakfast', calories: 450 },
  { name: 'Lunch', calories: 720 },
  { name: 'Snack', calories: 200 },
  { name: 'Dinner', calories: 580 },
];

const pieData = [
  { name: 'Protein', value: 20 },
  { name: 'Carbs', value: 55 },
  { name: 'Fats', value: 25 },
];

const COLORS = ['#00ff41', '#00d9ff', '#ffb000'];

export default function NutritionPanel() {
  return (
    <div className="bg-secondary border border-tertiary rounded-lg p-6">
      <h3 className="text-xl font-semibold text-white mb-6">Nutrition</h3>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calorie Summary */}
        <div className="bg-tertiary rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">Total Calories</div>
          <div className="text-4xl font-bold text-accent mb-1">1,850</div>
          <div className="text-gray-500 text-sm">of 2,200 kcal (84%)</div>
          <div className="mt-3 w-full bg-tertiary rounded-full h-2">
            <div className="bg-accent h-2 rounded-full" style={{ width: '84%' }}></div>
          </div>
        </div>

        {/* Macros Summary */}
        <div className="bg-tertiary rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">Protein</div>
          <div className="flex items-baseline space-x-2">
            <div className="text-3xl font-bold text-success">85g</div>
            <div className="text-gray-500">/150g</div>
          </div>
          <div className="mt-3 w-full bg-tertiary rounded-full h-2">
            <div className="bg-success h-2 rounded-full" style={{ width: '57%' }}></div>
          </div>
        </div>

        {/* Pie Chart */}
        <div className="bg-tertiary rounded-lg p-4 flex justify-center">
          <ResponsiveContainer width="100%" height={150}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={60}
                paddingAngle={2}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Macro Breakdown */}
      <div className="mt-6">
        <h4 className="text-sm font-semibold text-white mb-4">Macro Breakdown</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={macroData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262629" />
            <XAxis dataKey="name" stroke="#999999" />
            <YAxis stroke="#999999" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1d', border: '1px solid #262629' }}
              labelStyle={{ color: '#00d9ff' }}
            />
            <Legend />
            <Bar dataKey="value" fill="#00d9ff" name="Current" />
            <Bar dataKey="goal" fill="#262629" name="Goal" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Meals */}
      <div className="mt-6">
        <h4 className="text-sm font-semibold text-white mb-4">Recent Meals</h4>
        <div className="space-y-3">
          {caloriesData.map((meal, idx) => (
            <div key={idx} className="flex justify-between items-center bg-tertiary p-3 rounded">
              <span className="text-gray-400">{meal.name}</span>
              <span className="text-accent font-semibold">{meal.calories} kcal</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
