'use client';

import React from 'react';
import Card from '@/components/ui/Card';

export default function Preview() {
  return (
    <div className="py-20">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-text mb-4">Переглянь дашборд</h2>
        <p className="text-textSec">Все основне на одному екрані</p>
      </div>

      <Card accent>
        <div
          className="w-full bg-gradient-to-b from-accentBg to-bg rounded-card overflow-hidden"
          style={{ minHeight: '400px' }}
        >
          <div className="p-6 space-y-6">
            {/* Mock dashboard elements */}
            <div className="grid grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="glass-card-sm p-4 text-center"
                  style={{ minHeight: '120px' }}
                >
                  <div
                    className="w-12 h-12 mx-auto mb-3 rounded-full"
                    style={{ backgroundColor: 'rgba(251,146,60,0.2)' }}
                  />
                  <div className="h-3 bg-textMuted rounded w-3/4 mx-auto" />
                </div>
              ))}
            </div>

            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="glass-card-sm p-3 flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent mt-2" />
                  <div className="flex-1 space-y-2">
                    <div className="h-2 bg-textMuted rounded w-1/3" />
                    <div className="h-2 bg-textMuted rounded w-2/3" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
