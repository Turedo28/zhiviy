'use client';

import React from 'react';

interface HeroProps {
  onCtaClick: () => void;
}

export default function Hero({ onCtaClick }: HeroProps) {
  return (
    <div className="text-center space-y-8 py-20">
      {/* Badge */}
      <div className="inline-block">
        <span
          className="px-4 py-2 rounded-sm text-sm font-semibold"
          style={{
            backgroundColor: 'rgba(251,146,60,0.1)',
            color: '#fb923c',
            border: '1px solid rgba(251,146,60,0.2)',
          }}
        >
          ✨ HEALTHTRACK
        </span>
      </div>

      {/* Title */}
      <div className="space-y-4">
        <h1 className="text-5xl md:text-7xl font-bold text-text">
          Твоє здоров'я.<br />
          <span className="text-gradient">Одна платформа.</span>
        </h1>
      </div>

      {/* Subtitle */}
      <p className="text-lg md:text-xl text-textSec max-w-2xl mx-auto leading-relaxed">
        Відстежуй харчування, сон, відновлення та фізичні показники в одному місці.
        Отримуй персоналізовані рекомендації на основі AI-аналізу.
      </p>

      {/* CTA Button */}
      <button
        onClick={onCtaClick}
        className="inline-block mt-8 accent-gradient text-white font-bold py-4 px-8 rounded-card text-lg hover:shadow-glow transition transform hover:scale-105"
      >
        Почати безкоштовно
      </button>
    </div>
  );
}
