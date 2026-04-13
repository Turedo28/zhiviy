'use client';

import React, { useState } from 'react';
import { logout } from '@/lib/auth';

interface DashboardHeaderProps {
  avatar: string;
  name: string;
  currentDate: string;
  tabs: string[];
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export default function DashboardHeader({
  avatar,
  name,
  currentDate,
  tabs,
  activeTab,
  onTabChange,
}: DashboardHeaderProps) {
  const [showMenu, setShowMenu] = useState(false);

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="sticky top-0 z-50 glass-card border-b border-cardBorder">
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Top row: Logo, date, avatar */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-text">Health</h1>
            <h1 className="text-2xl font-bold text-gradient">Track</h1>
          </div>

          <div className="text-right">
            <p className="text-sm text-textSec">{currentDate}</p>
          </div>

          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="w-12 h-12 rounded-full accent-gradient flex items-center justify-center text-text font-bold text-lg hover:shadow-glow transition"
            >
              {avatar}
            </button>

            {showMenu && (
              <div className="absolute right-0 top-14 glass-card rounded-card p-2 w-48">
                <button
                  className="w-full text-left px-4 py-2 text-sm text-text hover:bg-accentBg rounded-sm transition"
                >
                  Профіль
                </button>
                <button
                  className="w-full text-left px-4 py-2 text-sm text-text hover:bg-accentBg rounded-sm transition"
                >
                  Налаштування
                </button>
                <div className="border-t border-cardBorder my-2" />
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-sm text-red hover:bg-red/10 rounded-sm transition"
                >
                  Вихід
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-6 border-b border-cardBorder pb-4">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => onTabChange(tab)}
              className={`text-sm font-semibold pb-2 transition relative ${
                activeTab === tab
                  ? 'text-accent'
                  : 'text-textSec hover:text-text'
              }`}
            >
              {tab}
              {activeTab === tab && (
                <div
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent"
                  style={{ borderRadius: '2px' }}
                />
              )}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}
