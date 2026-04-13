'use client';

import React from 'react';
import Card from '@/components/ui/Card';

export default function Features() {
  const features = [
    {
      icon: '🍽️',
      title: 'AI розпізнавання їжі',
      description: 'Фотографуй своє харчування, а ШІ автоматично аналізує калорійність та макроелементи',
    },
    {
      icon: '⌚',
      title: 'WHOOP інтеграція',
      description: 'Синхронізуй дані про сон, відновлення та напругу з твоїм носівним пристроєм',
    },
    {
      icon: '📊',
      title: 'Розумна аналітика',
      description: 'Отримуй персоналізовані інсайти і рекомендації на основі твоїх показників',
    },
    {
      icon: '💬',
      title: 'Telegram бот',
      description: 'Отримуй щоденні звіти та напередодні тренування прямо в Telegram',
    },
  ];

  return (
    <div className="py-20">
      <h2 className="text-4xl font-bold text-center text-text mb-12">
        Можливості платформи
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feature, index) => (
          <Card key={index} accent={index === 0 || index === 3}>
            <div className="text-4xl mb-4">{feature.icon}</div>
            <h3 className="text-xl font-bold text-text mb-2">{feature.title}</h3>
            <p className="text-textSec text-sm leading-relaxed">{feature.description}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
