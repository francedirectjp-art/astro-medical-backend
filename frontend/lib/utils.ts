// Utility Functions

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}年${month}月${day}日`;
}

export function formatTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const hour = String(d.getHours()).padStart(2, '0');
  const minute = String(d.getMinutes()).padStart(2, '0');
  return `${hour}:${minute}`;
}

export function formatDateTime(date: Date | string): string {
  return `${formatDate(date)} ${formatTime(date)}`;
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export function formatCharacterCount(count: number): string {
  return count.toLocaleString('ja-JP') + '文字';
}

export function calculateProgress(completed: number, total: number): number {
  return Math.round((completed / total) * 100);
}

export function getStepLabel(stepId: string): string {
  return stepId;
}

export function validateBirthData(data: Partial<{
  name: string;
  birth_year: number;
  birth_month: number;
  birth_day: number;
  birth_hour: number;
  birth_minute: number;
  birth_place: string;
}>): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!data.name || data.name.trim().length === 0) {
    errors.push('氏名を入力してください');
  }

  if (!data.birth_year || data.birth_year < 1900 || data.birth_year > 2100) {
    errors.push('正しい出生年を入力してください（1900-2100）');
  }

  if (!data.birth_month || data.birth_month < 1 || data.birth_month > 12) {
    errors.push('正しい出生月を入力してください（1-12）');
  }

  if (!data.birth_day || data.birth_day < 1 || data.birth_day > 31) {
    errors.push('正しい出生日を入力してください（1-31）');
  }

  if (data.birth_hour !== undefined && (data.birth_hour < 0 || data.birth_hour > 23)) {
    errors.push('正しい出生時を入力してください（0-23）');
  }

  if (data.birth_minute !== undefined && (data.birth_minute < 0 || data.birth_minute > 59)) {
    errors.push('正しい出生分を入力してください（0-59）');
  }

  if (!data.birth_place || data.birth_place.trim().length === 0) {
    errors.push('出生地を選択してください');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

export function getElementLabel(element: string): string {
  const labels: Record<string, string> = {
    fire: '火',
    earth: '地',
    air: '風',
    water: '水',
  };
  return labels[element] || element;
}

export function getModalityLabel(modality: string): string {
  const labels: Record<string, string> = {
    cardinal: '活動宮',
    fixed: '固定宮',
    mutable: '柔軟宮',
  };
  return labels[modality] || modality;
}

export function getSessionTitle(sessionId: number): string {
  const titles: Record<number, string> = {
    1: '基盤スペック',
    2: '内なる経営チーム',
    3: '社会との関わり',
    4: '独自の物語',
    5: 'ビジネスモデル',
    6: '未来予測',
  };
  return titles[sessionId] || `Session ${sessionId}`;
}

// Local Storage helpers
export const storage = {
  get: <T>(key: string, defaultValue?: T): T | null => {
    if (typeof window === 'undefined') return defaultValue || null;
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue || null;
    } catch {
      return defaultValue || null;
    }
  },
  
  set: <T>(key: string, value: T): void => {
    if (typeof window === 'undefined') return;
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  },
  
  remove: (key: string): void => {
    if (typeof window === 'undefined') return;
    try {
      window.localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
    }
  },
};
