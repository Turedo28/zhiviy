export function getCalColor(current: number, target: number): string {
  const percentage = (current / target) * 100;

  if (percentage < 50) return '#38bdf8'; // blue
  if (percentage < 80) return '#a78bfa'; // purple
  if (percentage < 100) return '#fb923c'; // orange
  if (percentage < 120) return '#00D26A'; // green
  return '#ef4444'; // red (over target)
}

export function getScoreColor(score: number): string {
  if (score < 30) return '#ef4444'; // red
  if (score < 50) return '#FFB020'; // yellow
  if (score < 70) return '#fb923c'; // orange
  return '#00D26A'; // green
}

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function formatTime(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours === 0) return `${mins}м`;
  return `${hours}ч ${mins}м`;
}

export function formatCalories(cal: number): string {
  return `${Math.round(cal)}`;
}
