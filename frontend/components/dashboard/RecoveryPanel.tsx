'use client';

export default function RecoveryPanel() {
  return (
    <div className="bg-secondary border border-tertiary rounded-lg p-6">
      <h3 className="text-xl font-semibold text-white mb-4">Відновлення</h3>

      <div className="space-y-4">
        {/* Recovery Score */}
        <div className="bg-tertiary rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">Оцінка сьогодні</div>
          <div className="flex items-center justify-between">
            <div className="text-4xl font-bold text-accent">72</div>
            <div className="text-right">
              <div className="text-xs text-gray-500">ВІДМІННО</div>
            </div>
          </div>
          <div className="mt-3 w-full bg-tertiary rounded-full h-3">
            <div className="bg-accent h-3 rounded-full" style={{ width: '72%' }}></div>
          </div>
        </div>

        {/* Metrics */}
        <div className="space-y-3">
          <div className="flex justify-between items-center bg-tertiary p-3 rounded">
            <span className="text-gray-400">Варіабельність пульсу (HRV)</span>
            <span className="text-accent font-semibold">45 мс</span>
          </div>
          <div className="flex justify-between items-center bg-tertiary p-3 rounded">
            <span className="text-gray-400">Пульс у спокої</span>
            <span className="text-accent font-semibold">52 уд/хв</span>
          </div>
          <div className="flex justify-between items-center bg-tertiary p-3 rounded">
            <span className="text-gray-400">Температура тіла</span>
            <span className="text-accent font-semibold">36.8°C</span>
          </div>
          <div className="flex justify-between items-center bg-tertiary p-3 rounded">
            <span className="text-gray-400">SpO2</span>
            <span className="text-success font-semibold">97%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
