'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import TelegramLoginButton from '@/components/ui/TelegramLoginButton';
import Hero from '@/components/landing/Hero';
import Features from '@/components/landing/Features';
import Preview from '@/components/landing/Preview';

export default function Home() {
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

  const handleCtaClick = () => {
    const telegramSection = document.getElementById('telegram-login');
    telegramSection?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <main className="min-h-screen bg-bg">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <Hero onCtaClick={handleCtaClick} />

        {/* Features */}
        <Features />

        {/* Preview */}
        <Preview />

        {/* Telegram Login Section */}
        <div id="telegram-login" className="py-20 text-center">
          <h2 className="text-4xl font-bold text-text mb-4">Розпочни зараз</h2>
          <p className="text-textSec text-lg mb-12">
            Увійди через Telegram безпечно та швидко
          </p>

          {isLoaded && <TelegramLoginButton />}

          <p className="text-xs text-textDim mt-8">
            © 2024 HealthTrack. Всі права захищені.
          </p>
        </div>
      </div>
    </main>
  );
}
