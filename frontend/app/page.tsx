'use client';

import React, { useState } from 'react';
import BirthDataForm from '@/components/BirthDataForm';
import ProgressBar from '@/components/ProgressBar';
import ContentDisplay from '@/components/ContentDisplay';
import api from '@/lib/api';
import type { BirthData, SessionResponse, StepContent, SessionInfo } from '@/types';

type AppState = 'input' | 'processing' | 'generating' | 'complete';

export default function Home() {
  const [state, setState] = useState<AppState>('input');
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [currentContent, setCurrentContent] = useState<StepContent | null>(null);
  const [totalCharacters, setTotalCharacters] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Get all steps from sessions
  const allSteps = sessions.flatMap(s => s.steps);

  const handleSubmit = async (birthData: BirthData) => {
    setLoading(true);
    setError(null);
    setState('processing');

    try {
      // Create session
      const sessionResponse = await api.createSession(birthData);
      setSession(sessionResponse);

      // Get session structure
      const structure = await api.getSessionsStructure();
      setSessions(structure);

      // Move to generating state
      setState('generating');
      setLoading(false);

      // Start generating first step automatically
      await generateNextStep(sessionResponse.session_id, structure);
    } catch (err: any) {
      console.error('Session creation failed:', err);
      setError(err.response?.data?.detail || err.message || '処理中にエラーが発生しました');
      setLoading(false);
      setState('input');
    }
  };

  const generateNextStep = async (sessionId: string, structure: SessionInfo[]) => {
    const allSteps = structure.flatMap(s => s.steps);
    
    if (currentStepIndex >= allSteps.length) {
      setState('complete');
      return;
    }

    const step = allSteps[currentStepIndex];
    setLoading(true);
    setError(null);

    try {
      // Generate step content
      const content = await api.generateStep(sessionId, step.step_id);
      setCurrentContent(content);
      setCompletedSteps(prev => [...prev, step.step_id]);
      setTotalCharacters(prev => prev + (content.character_count || 0));
      setLoading(false);

    } catch (err: any) {
      console.error('Step generation failed:', err);
      setError(err.response?.data?.detail || err.message || 'コンテンツ生成中にエラーが発生しました');
      setLoading(false);
    }
  };

  const handleNextStep = () => {
    if (currentStepIndex < allSteps.length - 1) {
      setCurrentStepIndex(prev => prev + 1);
      setCurrentContent(null);
      if (session) {
        generateNextStep(session.session_id, sessions);
      }
    } else {
      setState('complete');
    }
  };

  const handleDownloadPDF = async () => {
    if (!session) return;

    setLoading(true);
    setError(null);

    try {
      const pdfBlob = await api.downloadPDF(session.session_id);
      const url = window.URL.createObjectURL(pdfBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `anti_gravity_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setLoading(false);
    } catch (err: any) {
      console.error('PDF download failed:', err);
      setError(err.response?.data?.detail || err.message || 'PDF生成中にエラーが発生しました');
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12 animate-fade-in">
        <h2 className="text-4xl font-bold text-anti-gravity-dark mb-4">
          人生経営戦略書
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          あなたの出生図を「人生経営の設計図」として読み解き、
          <br />
          約50,000文字の包括的な戦略書を作成します。
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 animate-slide-up">
          <div className="flex items-center">
            <svg
              className="w-5 h-5 text-red-500 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Input State */}
      {state === 'input' && (
        <BirthDataForm onSubmit={handleSubmit} loading={loading} />
      )}

      {/* Processing State */}
      {state === 'processing' && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-lg text-gray-600">ホロスコープを計算中...</p>
        </div>
      )}

      {/* Generating State */}
      {state === 'generating' && (
        <div className="space-y-6">
          <ProgressBar
            current={completedSteps.length}
            total={allSteps.length}
            currentStep={allSteps[currentStepIndex]?.chapter_title}
            totalCharacters={totalCharacters}
          />

          {currentContent && (
            <>
              <ContentDisplay content={currentContent} />

              <div className="flex justify-center space-x-4">
                {currentStepIndex < allSteps.length - 1 ? (
                  <button
                    onClick={handleNextStep}
                    disabled={loading}
                    className="px-8 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all active:scale-95"
                  >
                    {loading ? '生成中...' : '次のステップへ'}
                  </button>
                ) : (
                  <button
                    onClick={() => setState('complete')}
                    className="px-8 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-all active:scale-95"
                  >
                    完了して確認する
                  </button>
                )}
              </div>
            </>
          )}

          {loading && !currentContent && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p className="mt-4 text-lg text-gray-600">コンテンツ生成中...</p>
            </div>
          )}
        </div>
      )}

      {/* Complete State */}
      {state === 'complete' && session && (
        <div className="space-y-6 animate-fade-in">
          <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
            <svg
              className="w-16 h-16 text-green-500 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h3 className="text-2xl font-bold text-green-800 mb-2">
              鑑定書の作成が完了しました！
            </h3>
            <p className="text-green-700">
              総文字数: {totalCharacters.toLocaleString()} 文字
            </p>
          </div>

          <div className="flex justify-center space-x-4">
            <button
              onClick={handleDownloadPDF}
              disabled={loading}
              className="px-8 py-4 bg-primary-600 text-white rounded-lg font-medium text-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all active:scale-95 flex items-center"
            >
              <svg
                className="w-6 h-6 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                />
              </svg>
              {loading ? 'PDF生成中...' : 'PDFをダウンロード'}
            </button>

            <button
              onClick={() => {
                setState('input');
                setSession(null);
                setCurrentStepIndex(0);
                setCompletedSteps([]);
                setCurrentContent(null);
                setTotalCharacters(0);
              }}
              className="px-8 py-4 bg-gray-600 text-white rounded-lg font-medium text-lg hover:bg-gray-700 transition-all active:scale-95"
            >
              新しい鑑定を開始
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
