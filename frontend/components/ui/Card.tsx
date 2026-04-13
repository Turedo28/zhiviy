'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  accent?: boolean;
  className?: string;
}

export default function Card({ children, accent = false, className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'glass-card p-6',
        accent && 'border-t-2 border-t-accent',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
