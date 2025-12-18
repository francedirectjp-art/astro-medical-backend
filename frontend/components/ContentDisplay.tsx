'use client';

import React, { useState, useEffect } from 'react';
import { StepContent } from '@/types';

interface ContentDisplayProps {
  content: StepContent | null;
  streaming?: boolean;
  streamContent?: string;
}

export default function ContentDisplay({
  content,
  streaming = false,
  streamContent = '',
}: ContentDisplayProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  // Typewriter effect for streaming content
  useEffect(() => {
    if (streaming && streamContent) {
      if (currentIndex < streamContent.length) {
        const timeout = setTimeout(() => {
          setDisplayedText(streamContent.slice(0, currentIndex + 1));
          setCurrentIndex(currentIndex + 1);
        }, 20); // 20ms per character for smooth typewriter effect

        return () => clearTimeout(timeout);
      }
    }
  }, [streaming, streamContent, currentIndex]);

  // Reset when new streaming starts
  useEffect(() => {
    if (streaming) {
      setCurrentIndex(0);
      setDisplayedText('');
    }
  }, [streaming, streamContent]);

  if (!content && !streaming) {
    return null;
  }

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Static Content */}
      {content && content.static_content && (
        <div className="space-y-4">
          {Object.entries(content.static_content).map(([key, block]) => (
            <div key={key} className="bg-white shadow-md rounded-lg p-6">
              <h3 className="text-lg font-bold text-anti-gravity-primary mb-3">
                {block.title}
              </h3>
              <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                {block.text}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Dynamic Content */}
      {content && content.dynamic_content && (
        <div className="space-y-4">
          {Object.entries(content.dynamic_content).map(([key, text]) => {
            if (!text) return null;

            const titles: Record<string, string> = {
              analysis: '【配置分析】',
              symbol: '【深層読解】',
              scenario: '【シナリオ】',
              action: '【提言とワーク】',
              letter: '【CEOへの手紙】',
            };

            return (
              <div key={key} className="bg-gradient-to-br from-blue-50 to-white shadow-md rounded-lg p-6">
                <h3 className="text-lg font-bold text-primary-700 mb-3">
                  {titles[key] || key}
                </h3>
                <div className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                  {text}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Streaming Content with Typewriter Effect */}
      {streaming && (
        <div className="bg-gradient-to-br from-green-50 to-white shadow-md rounded-lg p-6">
          <div className="flex items-center mb-3">
            <div className="animate-pulse flex space-x-1 mr-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="w-2 h-2 bg-green-500 rounded-full animation-delay-200"></div>
              <div className="w-2 h-2 bg-green-500 rounded-full animation-delay-400"></div>
            </div>
            <h3 className="text-lg font-bold text-green-700">
              生成中...
            </h3>
          </div>
          <div className="text-gray-800 whitespace-pre-wrap leading-relaxed font-mono">
            {displayedText}
            <span className="inline-block w-2 h-5 bg-green-500 ml-1 animate-pulse"></span>
          </div>
        </div>
      )}

      {/* Character Count */}
      {content && content.character_count > 0 && (
        <div className="text-right text-sm text-gray-500">
          このステップ: {content.character_count.toLocaleString()} 文字
        </div>
      )}
    </div>
  );
}
