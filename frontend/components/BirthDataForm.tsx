'use client';

import React, { useState } from 'react';
import { BirthData, PREFECTURES } from '@/types';

interface BirthDataFormProps {
  onSubmit: (data: BirthData) => void;
  loading?: boolean;
}

export default function BirthDataForm({ onSubmit, loading = false }: BirthDataFormProps) {
  const [formData, setFormData] = useState<BirthData>({
    name: '',
    birth_year: new Date().getFullYear() - 30,
    birth_month: 1,
    birth_day: 1,
    birth_hour: 12,
    birth_minute: 0,
    birth_place: '東京都',
    birth_time_unknown: false,
  });

  const [errors, setErrors] = useState<Partial<Record<keyof BirthData, string>>>({});

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof BirthData, string>> = {};

    if (!formData.name.trim()) {
      newErrors.name = '氏名を入力してください';
    }

    if (formData.birth_year < 1900 || formData.birth_year > new Date().getFullYear()) {
      newErrors.birth_year = '有効な年を入力してください（1900年〜現在）';
    }

    if (formData.birth_month < 1 || formData.birth_month > 12) {
      newErrors.birth_month = '月は1〜12の範囲で入力してください';
    }

    if (formData.birth_day < 1 || formData.birth_day > 31) {
      newErrors.birth_day = '日は1〜31の範囲で入力してください';
    }

    if (!formData.birth_time_unknown) {
      if (formData.birth_hour < 0 || formData.birth_hour > 23) {
        newErrors.birth_hour = '時は0〜23の範囲で入力してください';
      }
      if (formData.birth_minute < 0 || formData.birth_minute > 59) {
        newErrors.birth_minute = '分は0〜59の範囲で入力してください';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      // If time unknown, set to noon
      const submitData = formData.birth_time_unknown
        ? { ...formData, birth_hour: 12, birth_minute: 0 }
        : formData;
      onSubmit(submitData);
    }
  };

  const handleChange = (field: keyof BirthData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl mx-auto">
      <div className="bg-white shadow-lg rounded-lg p-8 animate-fade-in">
        <h2 className="text-2xl font-bold text-anti-gravity-dark mb-6">
          出生データ入力
        </h2>

        {/* 氏名 */}
        <div className="mb-6">
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            氏名 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="name"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
              errors.name ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="山田太郎"
            disabled={loading}
          />
          {errors.name && <p className="mt-1 text-sm text-red-500">{errors.name}</p>}
        </div>

        {/* 出生日 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            出生日 <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <input
                type="number"
                value={formData.birth_year}
                onChange={(e) => handleChange('birth_year', parseInt(e.target.value))}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 ${
                  errors.birth_year ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="年"
                min="1900"
                max={new Date().getFullYear()}
                disabled={loading}
              />
              <label className="block text-xs text-gray-500 mt-1">年</label>
            </div>
            <div>
              <input
                type="number"
                value={formData.birth_month}
                onChange={(e) => handleChange('birth_month', parseInt(e.target.value))}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 ${
                  errors.birth_month ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="月"
                min="1"
                max="12"
                disabled={loading}
              />
              <label className="block text-xs text-gray-500 mt-1">月</label>
            </div>
            <div>
              <input
                type="number"
                value={formData.birth_day}
                onChange={(e) => handleChange('birth_day', parseInt(e.target.value))}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 ${
                  errors.birth_day ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="日"
                min="1"
                max="31"
                disabled={loading}
              />
              <label className="block text-xs text-gray-500 mt-1">日</label>
            </div>
          </div>
          {(errors.birth_year || errors.birth_month || errors.birth_day) && (
            <p className="mt-1 text-sm text-red-500">
              {errors.birth_year || errors.birth_month || errors.birth_day}
            </p>
          )}
        </div>

        {/* 出生時間 */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              出生時間 {!formData.birth_time_unknown && <span className="text-red-500">*</span>}
            </label>
            <label className="flex items-center text-sm text-gray-600">
              <input
                type="checkbox"
                checked={formData.birth_time_unknown}
                onChange={(e) => handleChange('birth_time_unknown', e.target.checked)}
                className="mr-2 rounded"
                disabled={loading}
              />
              時間不明
            </label>
          </div>
          {!formData.birth_time_unknown && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <input
                  type="number"
                  value={formData.birth_hour}
                  onChange={(e) => handleChange('birth_hour', parseInt(e.target.value))}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 ${
                    errors.birth_hour ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="時"
                  min="0"
                  max="23"
                  disabled={loading}
                />
                <label className="block text-xs text-gray-500 mt-1">時（0-23）</label>
              </div>
              <div>
                <input
                  type="number"
                  value={formData.birth_minute}
                  onChange={(e) => handleChange('birth_minute', parseInt(e.target.value))}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 ${
                    errors.birth_minute ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="分"
                  min="0"
                  max="59"
                  disabled={loading}
                />
                <label className="block text-xs text-gray-500 mt-1">分（0-59）</label>
              </div>
            </div>
          )}
          {formData.birth_time_unknown && (
            <p className="text-sm text-gray-500 mt-2">
              ※ 出生時間が不明な場合、正午（12:00）として計算されます。
              ハウスとアングルの解釈は参考程度とお考えください。
            </p>
          )}
          {(errors.birth_hour || errors.birth_minute) && (
            <p className="mt-1 text-sm text-red-500">
              {errors.birth_hour || errors.birth_minute}
            </p>
          )}
        </div>

        {/* 出生地 */}
        <div className="mb-6">
          <label htmlFor="birth_place" className="block text-sm font-medium text-gray-700 mb-2">
            出生地 <span className="text-red-500">*</span>
          </label>
          <select
            id="birth_place"
            value={formData.birth_place}
            onChange={(e) => handleChange('birth_place', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={loading}
          >
            {PREFECTURES.map((pref) => (
              <option key={pref} value={pref}>
                {pref}
              </option>
            ))}
          </select>
        </div>

        {/* Submit Button */}
        <div className="mt-8">
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 px-6 rounded-lg font-medium text-white transition-all ${
              loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-primary-600 hover:bg-primary-700 active:scale-95'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                処理中...
              </span>
            ) : (
              '鑑定を開始する'
            )}
          </button>
        </div>

        <p className="mt-4 text-xs text-gray-500 text-center">
          入力された個人情報は鑑定書作成のみに使用され、適切に管理されます。
        </p>
      </div>
    </form>
  );
}
