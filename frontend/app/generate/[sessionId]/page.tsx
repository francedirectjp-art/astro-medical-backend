'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import api from '@/lib/api';
import type { GenerationStatus, StepContent } from '@/types';
import { formatCharacterCount, downloadBlob } from '@/lib/utils';

const TOTAL_STEPS = 15;
const STEP_IDS = [
  '1-A', '1-B', '2-A', '2-B', '3-A', '3-B',
  '4-A', '4-B', '4-C', '5-A', '5-B', '5-C',
  '6-A', '6-B', '6-C'
];

export default function GeneratePage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [status, setStatus] = useState<GenerationStatus | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoMode, setAutoMode] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<Record<string, StepContent>>({});

  useEffect(() => {
    loadStatus();
  }, [sessionId]);

  const loadStatus = async () => {
    try {
      const statusData = await api.getGenerationStatus(sessionId);
      setStatus(statusData);
      setCurrentStepIndex(statusData.completed_steps);
    } catch (err: any) {
      console.error('Failed to load status:', err);
      setError('セッション情報の読み込みに失敗しました');
    }
  };

  const generateStep = async (stepId: string) => {
    setGenerating(true);
    setError(null);

    try {
      const content = await api.generateStep(sessionId, stepId);
      setGeneratedContent(prev => ({ ...prev, [stepId]: content }));
      
      await loadStatus();
      setCurrentStepIndex(prev => prev + 1);
      
      return true;
    } catch (err: any) {
      console.error('Step generation failed:', err);
      setError(err.response?.data?.detail || 'コンテンツ生成に失敗しました');
      return false;
    } finally {
      setGenerating(false);
    }
  };

  const handleNextStep = async () => {
    if (currentStepIndex >= TOTAL_STEPS) return;
    
    const stepId = STEP_IDS[currentStepIndex];
    const success = await generateStep(stepId);
    
    if (success && autoMode && currentStepIndex < TOTAL_STEPS - 1) {
      // Continue automatically
      setTimeout(() => handleNextStep(), 1000);
    }
  };

  const handleAutoGenerate = async () => {
    setAutoMode(true);
    handleNextStep();
  };

  const handleDownloadPDF = async () => {
    try {
      setError(null);
      const blob = await api.downloadPDF(sessionId);
      const timestamp = new Date().toISOString().split('T')[0];
      downloadBlob(blob, `anti_gravity_${timestamp}.pdf`);
    } catch (err: any) {
      console.error('PDF download failed:', err);
      setError('PDFダウンロードに失敗しました');
    }
  };

  const progress = status ? (status.completed_steps / TOTAL_STEPS) * 100 : 0;
  const isComplete = currentStepIndex >= TOTAL_STEPS;

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="container-custom py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-anti-gravity-dark">
                Anti-Gravity
              </h1>
              <p className="text-sm text-gray-600">
                セッション: {sessionId.slice(0, 8)}...
              </p>
            </div>
            <button
              onClick={() => router.push('/')}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              ← 戻る
            </button>
          </div>
        </div>
      </header>

      <div className="container-custom py-8">
        {/* Progress Section */}
        <div className="card mb-8">
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-xl font-bold text-anti-gravity-primary">
                生成進捗
              </h2>
              <span className="text-2xl font-bold text-primary-600">
                {Math.round(progress)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className="progress-bar bg-primary-600 h-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex justify-between text-sm text-gray-600 mt-2">
              <span>
                ステップ {currentStepIndex} / {TOTAL_STEPS}
              </span>
              <span>
                {status && formatCharacterCount(status.total_characters)}
              </span>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            {!isComplete ? (
              <>
                <button
                  onClick={handleNextStep}
                  disabled={generating || autoMode}
                  className="btn btn-primary flex-1 py-3"
                >
                  {generating ? (
                    <span className="flex items-center justify-center">
                      <span className="spinner mr-2" />
                      生成中...
                    </span>
                  ) : (
                    <>次のステップを生成</>
                  )}
                </button>
                {!autoMode && currentStepIndex < TOTAL_STEPS && (
                  <button
                    onClick={handleAutoGenerate}
                    disabled={generating}
                    className="btn btn-secondary px-6"
                  >
                    自動生成
                  </button>
                )}
              </>
            ) : (
              <button
                onClick={handleDownloadPDF}
                className="btn btn-primary flex-1 py-3 text-lg font-bold"
              >
                📄 PDFダウンロード
              </button>
            )}
          </div>

          {isComplete && (
            <p className="text-center text-sm text-green-600 mt-4">
              ✅ すべてのステップが完了しました！
            </p>
          )}
        </div>

        {/* Generated Content Display */}
        {Object.keys(generatedContent).length > 0 && (
          <div className="space-y-6">
            <h3 className="text-xl font-bold text-anti-gravity-primary">
              生成されたコンテンツ
            </h3>
            {Object.entries(generatedContent).map(([stepId, content]) => (
              <div key={stepId} className="card">
                <div className="flex justify-between items-start mb-4">
                  <h4 className="text-lg font-bold text-anti-gravity-secondary">
                    Step {stepId}
                  </h4>
                  <span className="text-sm text-gray-500">
                    {formatCharacterCount(content.character_count)}
                  </span>
                </div>
                
                {/* Static Content */}
                {Object.entries(content.static_content || {}).map(([key, block]) => (
                  <div key={key} className="mb-4">
                    {typeof block === 'object' && block.title && (
                      <>
                        <h5 className="font-bold text-anti-gravity-secondary mb-2">
                          {block.title}
                        </h5>
                        <p className="text-gray-700 whitespace-pre-wrap">
                          {block.text}
                        </p>
                      </>
                    )}
                  </div>
                ))}

                {/* Dynamic Content */}
                {Object.entries(content.dynamic_content || {}).map(([key, text]) => (
                  text && (
                    <div key={key} className="mb-4 pl-4 border-l-4 border-primary-200">
                      <p className="text-gray-700 whitespace-pre-wrap">
                        {text}
                      </p>
                    </div>
                  )
                ))}
              </div>
            ))}
          </div>
        )}

        {/* Initial State */}
        {Object.keys(generatedContent).length === 0 && !generating && (
          <div className="card text-center py-12">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-bold text-anti-gravity-primary mb-2">
              準備完了
            </h3>
            <p className="text-gray-600">
              「次のステップを生成」ボタンをクリックして開始してください
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
