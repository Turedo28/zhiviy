// Mock data matching the Warm Ember design mockup
// Will be replaced with real API calls later

export const mockUserData = {
  id: '1',
  firstName: 'Владислав',
  lastName: '',
  avatar: 'В',
  username: 'vladislav',
};

export const mockTodayMetrics = {
  recovery: 58,
  sleep: 72,
  strain: 12.4,
  hrv: 42,
  steps: 8450,
};

export const mockNutrition = {
  calories: {
    consumed: 1650,
    target: 2100,
  },
  macros: {
    protein: { value: 120, target: 160, unit: 'г' },
    carbs: { value: 145, target: 220, unit: 'г' },
    fat: { value: 52, target: 70, unit: 'г' },
  },
  meals: [
    {
      id: '1',
      name: 'Вівсянка з бананом',
      time: '08:30',
      calories: 380,
      emoji: '🥣',
      protein: 14,
      carbs: 58,
      fat: 8,
    },
    {
      id: '2',
      name: 'Курка гриль + рис',
      time: '13:00',
      calories: 620,
      emoji: '🍗',
      protein: 52,
      carbs: 48,
      fat: 18,
    },
    {
      id: '3',
      name: 'Грецький салат',
      time: '15:30',
      calories: 280,
      emoji: '🥗',
      protein: 12,
      carbs: 16,
      fat: 20,
    },
    {
      id: '4',
      name: 'Протеїновий коктейль',
      time: '18:00',
      calories: 370,
      emoji: '🥤',
      protein: 42,
      carbs: 23,
      fat: 6,
    },
  ],
};

export const mockWater = {
  consumed: 1200,
  target: 2500,
  unit: 'мл',
};

export const mockSleep = {
  hours: 6.2,
  score: 72,
  efficiency: 88,
  bedtime: '00:45',
  wakeup: '07:00',
  stages: {
    deep: 1.1,
    rem: 1.4,
    light: 3.2,
    awake: 0.5,
  },
};

export const mockVitals = {
  hrv: { value: 42, unit: 'мс', trend: 'down' as const },
  restingHR: { value: 62, unit: 'уд/хв', trend: 'stable' as const },
  spo2: { value: 97, unit: '%', trend: 'stable' as const },
  skinTemp: { value: 36.4, unit: '°C', trend: 'stable' as const },
  maxHR: { value: 172, unit: 'уд/хв', trend: 'up' as const },
  activeCal: { value: 420, unit: 'kcal', trend: 'up' as const },
};

export const mockRecovery = {
  score: 58,
  recommendation:
    'Відновлення нижче середнього. HRV впав на 12% порівняно з минулим тижнем. Рекомендуємо полегшене тренування.',
  level: 'medium' as const,
};

export const mockSleepDetail = {
  totalHours: 6.2,
  bedTime: '00:45',
  wakeTime: '07:00',
  quality: 72,
  efficiency: 88,
  stages: {
    deep: 1.1,
    rem: 1.4,
    light: 3.2,
    awake: 0.5,
  },
};

export const mockWeeklyData = {
  calories: [
    { day: 'Пн', value: 1980 },
    { day: 'Вт', value: 2150 },
    { day: 'Ср', value: 1850 },
    { day: 'Чт', value: 2300 },
    { day: 'Пт', value: 1650 },
    { day: 'Сб', value: 0 },
    { day: 'Нд', value: 0 },
  ],
  sleep: [
    { day: 'Пн', value: 7.1 },
    { day: 'Вт', value: 6.5 },
    { day: 'Ср', value: 5.8 },
    { day: 'Чт', value: 6.8 },
    { day: 'Пт', value: 7.2 },
    { day: 'Сб', value: 6.2 },
    { day: 'Нд', value: 0 },
  ],
  recovery: [
    { day: 'Пн', value: 72 },
    { day: 'Вт', value: 65 },
    { day: 'Ср', value: 48 },
    { day: 'Чт', value: 71 },
    { day: 'Пт', value: 68 },
    { day: 'Сб', value: 58 },
    { day: 'Нд', value: 0 },
  ],
  strain: [
    { day: 'Пн', value: 14.2 },
    { day: 'Вт', value: 8.1 },
    { day: 'Ср', value: 16.5 },
    { day: 'Чт', value: 11.3 },
    { day: 'Пт', value: 12.4 },
    { day: 'Сб', value: 0 },
    { day: 'Нд', value: 0 },
  ],
};

export const mockBodyMetrics = {
  weight: { value: 82, unit: 'кг' },
  height: { value: 180, unit: 'см' },
  calorieTarget: { value: 2100, unit: 'kcal/день' },
};

export const mockAverageMacros = {
  protein: { average: 118, target: 160 },
  carbs: { average: 195, target: 220 },
  fat: { average: 62, target: 70 },
};
