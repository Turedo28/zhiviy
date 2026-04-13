'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface TagProps {
  children: React.ReactNode;
  variant?: 'accent' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md';
  className?: string;
}

const variantStyles: Record<string, string> = {
  accent:
    'bg-accentBg text-accent border border-accentBorder',
  success:
    'bg-green/10 text-green border border-green/20',
  warning:
    'bg-yellow/10 text-yellow border border-yellow/20',
  danger:
    'bg-red/10 text-red border border-red/20',
  info: 'bg-blue/10 text-blue border border-blue/20',
};

const sizeStyles: Record<string, string> = {
  sm: 'px-2 py-1 text-xs',
  md: 'px-3 py-1.5 text-sm',
};

export default function Tag({
  children,
  variant = 'accent',
  size = 'md',
  className,
}: TagProps) {
  return (
    <span
      className={cn(
        'inline-block font-semibold rounded-sm',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {children}
    </span>
  );
}
