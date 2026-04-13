'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import TelegramLoginButton from '@/components/ui/TelegramLoginButton';
import Card from '@/components/ui/Card';

export default function AuthPage() {
  const router = useRouter();
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);

    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <main className="min-h-screen bg-bg flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo Circle */}
        <div className="flex justify-center mb-8">
          <div
            className="w-20 h-20 rounded-full accent-gradient flex items-center justify-center text-3xl font-bold text-text shadow-glow"
          >
            H
          </div>
        </div>

        {/* Card */}
        <Card className="text-center">
          <h1 className="text-3xl font-bold text-text mb-2">HealthTrack</h1>
          <p className="text-textSec text-sm mb-8">
            Твоя персональна платформа здоров'я
          </p>

          {/* Telegram Login */}
          {isLoaded && (
            <div className="mb-6">
              <TelegramLoginButton />
            </div>
          )}

          {/* Divider */}
          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-cardBorder" />
            <span className="text-textDim text-sm">або</span>
            <div className="flex-1 h-px bg-cardBorder" />
          </div>

          {/* QR Code Placeholder */}
          <div className="bg-cardBorder rounded-card p-6 mb-6 flex flex-col items-center justify-center" style={{ minHeight: '200px' }}>
            <div className="text-4xl mb-2">📱</div>
            <p className="text-sm text-textSec">Сканюй QR код</p>
            <p className="text-xs text-textDim mt-2">Або введи код:  HD-2024</p>
          </div>

          {/* Terms Links */}
          <div className="pt-6 border-t border-cardBorder space-y-2">
            <p className="text-xs text-textDim">
              Входячи, ти приймаєш{' '}
              <a href="#" className="text-accent hover:text-accentDim">
                Умови використання
              </a>
              {' '}і{' '}
              <a href="#" className="text-accent hover:text-accentDim">
                Політику приватності
              </a>
            </p>
          </div>
        </Card>
      </div>
    </main>
  );
}
