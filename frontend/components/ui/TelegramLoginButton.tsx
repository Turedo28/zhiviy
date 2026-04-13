'use client';

import { useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { setAuthToken } from '@/lib/auth';
import apiClient from '@/lib/api';

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

declare global {
  interface Window {
    onTelegramAuth?: (user: TelegramUser) => void;
  }
}

export default function TelegramLoginButton() {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);

  const handleTelegramLogin = useCallback(async (user: TelegramUser) => {
    try {
      const response = await apiClient.post('/auth/telegram', {
        id: user.id,
        first_name: user.first_name,
        last_name: user.last_name,
        username: user.username,
        photo_url: user.photo_url,
        auth_date: user.auth_date,
        hash: user.hash,
      });

      setAuthToken(response.data.access_token);
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      alert('Помилка входу. Спробуйте ще раз.');
    }
  }, [router]);

  useEffect(() => {
    // Set global callback for Telegram widget
    window.onTelegramAuth = handleTelegramLogin;

    const botId = process.env.NEXT_PUBLIC_TELEGRAM_BOT_ID || '';

    if (containerRef.current && botId) {
      // Create Telegram Login Widget script with data attributes
      const script = document.createElement('script');
      script.src = 'https://telegram.org/js/telegram-widget.js?22';
      script.async = true;
      script.setAttribute('data-telegram-login', botId);
      script.setAttribute('data-size', 'large');
      script.setAttribute('data-onauth', 'onTelegramAuth(user)');
      script.setAttribute('data-request-access', 'write');
      script.setAttribute('data-lang', 'uk');
      script.setAttribute('data-radius', '12');
      containerRef.current.appendChild(script);
    }

    return () => {
      delete window.onTelegramAuth;
    };
  }, [handleTelegramLogin]);

  return (
    <div ref={containerRef} className="flex justify-center">
      {/* Telegram Login Widget renders here */}
    </div>
  );
}
