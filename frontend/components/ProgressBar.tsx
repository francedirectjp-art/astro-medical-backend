'use client';

import React from 'react';

interface ProgressBarProps {
  current: number;
  total: number;
  currentStep?: string;
  totalCharacters?: number;
}

export default function ProgressBar({
  current,
  total,
  currentStep,
  totalCharacters = 0,
}: ProgressBarProps) {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div className="w-full bg-white shadow-lg rounded-lg p-6 animate-fade-in">
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            生成進捗
          </span>
          <span className="text-sm font-bold text-primary-600">
            {percentage}% 完了
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${percentage}%` }}
          >
            <div className="h-full w-full bg-white opacity-20 animate-pulse"></div>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center text-sm">
        <div className="text-gray-600">
          <span className="font-medium">{current}</span> / {total} ステップ
        </div>
        {totalCharacters > 0 && (
          <div className="text-gray-600">
            累計 <span className="font-medium">{totalCharacters.toLocaleString()}</span> 文字
          </div>
        )}
      </div>

      {currentStep && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            現在の処理: <span className="font-medium text-gray-900">{currentStep}</span>
          </p>
        </div>
      )}
    </div>
  );
}
