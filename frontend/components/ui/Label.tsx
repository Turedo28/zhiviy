'use client';

import React from 'react';

interface LabelProps {
  children: React.ReactNode;
  className?: string;
}

export default function Label({ children, className }: LabelProps) {
  return (
    <h3 className={`text-lg font-semibold text-text mb-4 ${className || ''}`}>
      {children}
    </h3>
  );
}
