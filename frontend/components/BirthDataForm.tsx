'use client';

import { useState } from 'react';
import type { BirthData } from '@/types';
import { PREFECTURES } from '@/types';
import { validateBirthData } from '@/lib/utils';

interface BirthDataFormProps {
  onSubmit: (data: BirthData) => void;
  loading?: boolean;
}

export default function BirthDataForm({ onSubmit, loading = false }: BirthDataFormProps) {
  const currentYear = new Date().getFullYear();
  
  const [formData, setFormData] = useState<Partial<BirthData>>({
    name: '',
    birth_year: currentYear - 30,
    birth_month: 1,
    birth_day: 1,
    birth_hour: 12,
    birth_minute: 0,
    birth_place: '東京都',
    birth_time_unknown: false,
  });

  const [errors, setErrors] = useState<string[]>([]);

  const handleChange = (field: keyof BirthData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setErrors([]);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const validation = validateBirthData(formData);
    
    if (!validation.valid) {
      setErrors(validation.errors);
      return;
    }

    onSubmit(formData as BirthData);
  };

  const handleTimeUnknownChange = (checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      birth_time_unknown: checked,
      birth_hour: checked ? 12 : prev.birth_hour,
      birth_minute: checked ? 0 : prev.birth_minute,
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name */}
      <div>
        <label htmlFor="name" className="label">
          氏名 <span className="text-red-500">*</span>
        </label>
        <input
          id="name"
          type="text"
          className="input"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          placeholder="山田 太郎"
          disabled={loading}
          required
        />
      </div>

      {/* Birth Date */}
      <div>
        <label className="label">
          出生日 <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <select
              className="select"
              value={formData.birth_year}
              onChange={(e) => handleChange('birth_year', parseInt(e.target.value))}
              disabled={loading}
              required
            >
              {Array.from({ length: 121 }, (_, i) => currentYear - i).map(year => (
                <option key={year} value={year}>{year}年</option>
              ))}
            </select>
          </div>
          <div>
            <select
              className="select"
              value={formData.birth_month}
              onChange={(e) => handleChange('birth_month', parseInt(e.target.value))}
              disabled={loading}
              required
            >
              {Array.from({ length: 12 }, (_, i) => i + 1).map(month => (
                <option key={month} value={month}>{month}月</option>
              ))}
            </select>
          </div>
          <div>
            <select
              className="select"
              value={formData.birth_day}
              onChange={(e) => handleChange('birth_day', parseInt(e.target.value))}
              disabled={loading}
              required
            >
              {Array.from({ length: 31 }, (_, i) => i + 1).map(day => (
                <option key={day} value={day}>{day}日</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Birth Time */}
      <div>
        <label className="label">
          出生時刻 {!formData.birth_time_unknown && <span className="text-red-500">*</span>}
        </label>
        <div className="grid grid-cols-2 gap-3 mb-2">
          <div>
            <select
              className="select"
              value={formData.birth_hour}
              onChange={(e) => handleChange('birth_hour', parseInt(e.target.value))}
              disabled={loading || formData.birth_time_unknown}
              required={!formData.birth_time_unknown}
            >
              {Array.from({ length: 24 }, (_, i) => i).map(hour => (
                <option key={hour} value={hour}>
                  {String(hour).padStart(2, '0')}時
                </option>
              ))}
            </select>
          </div>
          <div>
            <select
              className="select"
              value={formData.birth_minute}
              onChange={(e) => handleChange('birth_minute', parseInt(e.target.value))}
              disabled={loading || formData.birth_time_unknown}
              required={!formData.birth_time_unknown}
            >
              {Array.from({ length: 60 }, (_, i) => i).map(minute => (
                <option key={minute} value={minute}>
                  {String(minute).padStart(2, '0')}分
                </option>
              ))}
            </select>
          </div>
        </div>
        <label className="flex items-center text-sm text-gray-600 cursor-pointer">
          <input
            type="checkbox"
            checked={formData.birth_time_unknown}
            onChange={(e) => handleTimeUnknownChange(e.target.checked)}
            disabled={loading}
            className="mr-2"
          />
          出生時刻が不明（正午として計算します）
        </label>
        {formData.birth_time_unknown && (
          <p className="text-xs text-amber-600 mt-1">
            ⚠️ ハウスとアングルの解釈は参考程度となります
          </p>
        )}
      </div>

      {/* Birth Place */}
      <div>
        <label htmlFor="birth_place" className="label">
          出生地 <span className="text-red-500">*</span>
        </label>
        <select
          id="birth_place"
          className="select"
          value={formData.birth_place}
          onChange={(e) => handleChange('birth_place', e.target.value)}
          disabled={loading}
          required
        >
          {PREFECTURES.map(pref => (
            <option key={pref} value={pref}>{pref}</option>
          ))}
        </select>
        <p className="text-xs text-gray-500 mt-1">
          より正確な計算には都道府県を選択してください
        </p>
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <ul className="text-sm text-red-800 space-y-1">
            {errors.map((error, index) => (
              <li key={index}>• {error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        className="btn btn-primary w-full py-3 text-lg font-bold disabled:opacity-50"
        disabled={loading}
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <span className="spinner mr-2" />
            処理中...
          </span>
        ) : (
          '鑑定書を作成する'
        )}
      </button>

      {/* Info */}
      <p className="text-xs text-center text-gray-500">
        セッション作成後、15ステップの生成プロセスが開始されます
      </p>
    </form>
  );
}
