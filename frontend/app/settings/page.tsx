'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getAuthToken, isAuthenticated } from '@/lib/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

interface UserProfile {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  language: string;
  date_of_birth: string | null;
  gender: string | null;
  height_cm: number | null;
  weight_kg: number | null;
  activity_level: string | null;
  goal: string | null;
  water_tracking_enabled: boolean;
  supplements_tracking_enabled: boolean;
  onboarding_completed: boolean;
}

const ACTIVITY_LEVELS = [
  { value: 'sedentary', label: 'Сидячий спосіб життя' },
  { value: 'light', label: 'Легка активність' },
  { value: 'moderate', label: 'Помірна активність' },
  { value: 'active', label: 'Активний' },
  { value: 'very_active', label: 'Дуже активний' },
];

const GOALS = [
  { value: 'lose', label: 'Схуднення' },
  { value: 'maintain', label: 'Підтримка ваги' },
  { value: 'gain', label: 'Набір маси' },
];

const GENDERS = [
  { value: 'male', label: 'Чоловіча' },
  { value: 'female', label: 'Жіноча' },
];

export default function SettingsPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  // Form state
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [gender, setGender] = useState('');
  const [heightCm, setHeightCm] = useState('');
  const [weightKg, setWeightKg] = useState('');
  const [activityLevel, setActivityLevel] = useState('');
  const [goal, setGoal] = useState('');
  const [language, setLanguage] = useState('uk');

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/');
      return;
    }
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = getAuthToken();
      if (!token) return;

      const res = await fetch(`${API_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const data: UserProfile = await res.json();
        setProfile(data);
        setFirstName(data.first_name || '');
        setLastName(data.last_name || '');
        setDateOfBirth(data.date_of_birth || '');
        setGender(data.gender || '');
        setHeightCm(data.height_cm?.toString() || '');
        setWeightKg(data.weight_kg?.toString() || '');
        setActivityLevel(data.activity_level || '');
        setGoal(data.goal || '');
        setLanguage(data.language || 'uk');
      }
    } catch (err) {
      console.error('Failed to fetch profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveStatus(null);

    try {
      const token = getAuthToken();
      if (!token) return;

      const body: Record<string, unknown> = {};
      if (firstName !== (profile?.first_name || '')) body.first_name = firstName;
      if (lastName !== (profile?.last_name || '')) body.last_name = lastName;
      if (dateOfBirth !== (profile?.date_of_birth || '')) body.date_of_birth = dateOfBirth || null;
      if (gender !== (profile?.gender || '')) body.gender = gender || null;
      if (heightCm !== (profile?.height_cm?.toString() || '')) body.height_cm = heightCm ? parseFloat(heightCm) : null;
      if (weightKg !== (profile?.weight_kg?.toString() || '')) body.weight_kg = weightKg ? parseFloat(weightKg) : null;
      if (activityLevel !== (profile?.activity_level || '')) body.activity_level = activityLevel || null;
      if (goal !== (profile?.goal || '')) body.goal = goal || null;
      if (language !== (profile?.language || 'uk')) body.language = language;

      if (Object.keys(body).length === 0) {
        setSaveStatus('Нічого не змінено');
        setIsSaving(false);
        return;
      }

      const res = await fetch(`${API_URL}/users/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      if (res.ok) {
        const data = await res.json();
        setProfile(data);
        setSaveStatus('Збережено!');
        setTimeout(() => setSaveStatus(null), 3000);
      } else {
        setSaveStatus('Помилка збереження');
      }
    } catch (err) {
      setSaveStatus('Помилка мережі');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-bg">
      {/* Header */}
      <div className="border-b border-white/10 bg-card">
        <div className="max-w-3xl mx-auto px-4 py-6 sm:px-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-textMain">Налаштування</h1>
              <p className="text-textDim text-sm mt-1">Керуйте профілем та параметрами</p>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 glass-card-sm text-textSec hover:text-textMain transition text-sm"
            >
              Назад
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-8 sm:px-6 space-y-8">
        {/* Personal Info */}
        <section className="bg-card rounded-2xl border border-white/10 p-6">
          <h2 className="text-lg font-semibold text-textMain mb-4">Особисті дані</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-textDim mb-1">Ім'я</label>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-textMain focus:border-accent focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-textDim mb-1">Прізвище</label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-textMain focus:border-accent focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-textDim mb-1">Дата народження</label>
              <input
                type="date"
                value={dateOfBirth}
                onChange={(e) => setDateOfBirth(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-textMain focus:border-accent focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-textDim mb-1">Стать</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-textMain focus:border-accent focus:outline-none"
              >
                <option value="">Не вказано</option>
                {GENDERS.map(g => (
                  <option key={g.value} value={g.value}>{g.label}</option>
                ))}
              </select>
            </div>
          </div>
        </section>

        {/* Body Metrics */}
        <section className="bg-card rounded-2xl border border-white/10 p-6">
          <h2 className="text-lg font-semibold text-textMain mb-4">Метрики тіла</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-textDim mb-1">Вага (кг)</label>
              <input
                type="number"
                step="0.1"
                value={weightKg}
                onChange={(e) => setWeightKg(e.target.value)}
                placeholder="80"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-textMain focus:border-accent focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-textDim mb-1">Зріст (см)</label>
              <input
                type="number"
                step="0.1"
                value={heightCm}
                onChange={(e) => setHeightCm(e.target.value)}
                placeholder="180"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-textMain focus:border-accent focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-textDim mb-1">Рівень активності</label>
              <select
                value={activityLevel}
                onChange={(e) => setActivityLevel(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-textMain focus:border-accent focus:outline-none"
              >
                <option value="">Не вказано</option>
                {ACTIVITY_LEVELS.map(a => (
                  <option key={a.value} value={a.value}>{a.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-textDim mb-1">Ціль</label>
              <select
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-textMain focus:border-accent focus:outline-none"
              >
                <option value="">Не вказано</option>
                {GOALS.map(g => (
                  <option key={g.value} value={g.value}>{g.label}</option>
                ))}
              </select>
            </div>
          </div>
          <p className="text-xs text-textDim mt-3">
            Ці дані впливають на розрахунок денної норми калорій та макроелементів
          </p>
        </section>

        {/* Integrations info */}
        <section className="bg-card rounded-2xl border border-white/10 p-6">
          <h2 className="text-lg font-semibold text-textMain mb-4">Інтеграції</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between glass-card-sm p-3">
              <div className="flex items-center gap-3">
                <span className="text-xl">⌚</span>
                <div>
                  <div className="text-sm font-medium text-textMain">WHOOP</div>
                  <div className="text-xs text-textDim">Сон, відновлення, тренування</div>
                </div>
              </div>
              <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">
                Підключено
              </span>
            </div>
            <div className="flex items-center justify-between glass-card-sm p-3">
              <div className="flex items-center gap-3">
                <span className="text-xl">🤖</span>
                <div>
                  <div className="text-sm font-medium text-textMain">Telegram Bot</div>
                  <div className="text-xs text-textDim">@zhiviy_bot — трекінг їжі</div>
                </div>
              </div>
              <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">
                Підключено
              </span>
            </div>
          </div>
        </section>

        {/* Save button */}
        <div className="flex items-center gap-4">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-6 py-3 bg-accent text-black rounded-xl font-semibold hover:bg-accent/80 transition disabled:opacity-50"
          >
            {isSaving ? 'Збереження...' : 'Зберегти зміни'}
          </button>
          {saveStatus && (
            <span className={`text-sm ${saveStatus === 'Збережено!' ? 'text-green-400' : 'text-red-400'}`}>
              {saveStatus}
            </span>
          )}
        </div>
      </div>
    </main>
  );
}
