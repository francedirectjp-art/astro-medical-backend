'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import BirthDataForm from '@/components/BirthDataForm';
import type { BirthData } from '@/types';
import api from '@/lib/api';
import { storage } from '@/lib/utils';

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (birthData: BirthData) => {
    setLoading(true);
    setError(null);

    try {
      // Create session with birth data
      const response = await api.createSession(birthData);
      
      // Save session ID to local storage
      storage.set('current_session_id', response.session_id);
      storage.set(`session_${response.session_id}`, {
        birthData,
        chartData: response.chart_data,
        createdAt: new Date().toISOString(),
      });

      // Navigate to generation page
      router.push(`/generate/${response.session_id}`);
    } catch (err: any) {
      console.error('Session creation failed:', err);
      setError(
        err.response?.data?.detail || 
        'セッションの作成に失敗しました。もう一度お試しください。'
      );
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container-custom py-6">
          <h1 className="text-3xl font-bold text-anti-gravity-dark">
            Anti-Gravity
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Strategic Life Navigation System
          </p>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container-custom py-12">
        <div className="max-w-3xl mx-auto text-center mb-12">
          <h2 className="text-4xl font-bold text-anti-gravity-dark mb-4">
            占星術人生経営戦略書
          </h2>
          <p className="text-lg text-gray-600 leading-relaxed">
            あなたの出生データから、MBAホルダーの人生経営戦略コンサルタントが<br />
            約50,000文字の超長編鑑定書を作成します
          </p>
        </div>

        {/* Main Form Card */}
        <div className="max-w-2xl mx-auto">
          <div className="card">
            <div className="mb-6">
              <h3 className="text-2xl font-bold text-anti-gravity-primary mb-2">
                出生データ入力
              </h3>
              <p className="text-sm text-gray-600">
                正確な鑑定のため、できる限り正確な情報をご入力ください
              </p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <BirthDataForm 
              onSubmit={handleSubmit} 
              loading={loading}
            />
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="card text-center">
              <div className="text-3xl mb-2">📊</div>
              <h4 className="font-bold text-anti-gravity-primary mb-1">
                15ステップ
              </h4>
              <p className="text-xs text-gray-600">
                詳細な分析
              </p>
            </div>
            <div className="card text-center">
              <div className="text-3xl mb-2">📝</div>
              <h4 className="font-bold text-anti-gravity-primary mb-1">
                50,000文字
              </h4>
              <p className="text-xs text-gray-600">
                超長編レポート
              </p>
            </div>
            <div className="card text-center">
              <div className="text-3xl mb-2">📄</div>
              <h4 className="font-bold text-anti-gravity-primary mb-1">
                PDFダウンロード
              </h4>
              <p className="text-xs text-gray-600">
                電子書籍品質
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white py-16 mt-12">
        <div className="container-custom">
          <h3 className="text-2xl font-bold text-center text-anti-gravity-dark mb-12">
            システムの特徴
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl mb-4">🎯</div>
              <h4 className="font-bold text-anti-gravity-primary mb-2">
                正確な天体計算
              </h4>
              <p className="text-sm text-gray-600">
                Swiss Ephemerisによる精密な計算
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">🤖</div>
              <h4 className="font-bold text-anti-gravity-primary mb-2">
                AI分析
              </h4>
              <p className="text-sm text-gray-600">
                GPT-4o/Geminiによる高度な解釈
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">💼</div>
              <h4 className="font-bold text-anti-gravity-primary mb-2">
                経営的視点
              </h4>
              <p className="text-sm text-gray-600">
                MBAホルダーの戦略的アドバイス
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">📖</div>
              <h4 className="font-bold text-anti-gravity-primary mb-2">
                6ブロック執筆
              </h4>
              <p className="text-sm text-gray-600">
                理論・分析・シナリオ・提言
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-anti-gravity-dark text-white py-8 mt-16">
        <div className="container-custom text-center">
          <p className="text-sm text-gray-400">
            © 2024 Anti-Gravity | Strategic Life Navigation System
          </p>
        </div>
      </footer>
    </main>
  );
}
