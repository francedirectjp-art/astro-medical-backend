// Anti-Gravity API Client

import axios, { AxiosInstance } from 'axios';
import type {
  BirthData,
  SessionResponse,
  StepContent,
  GenerationStatus,
  SessionInfo,
  PDFPreview,
  Prefecture,
  ChartData
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class AntiGravityAPI {
  private client: AxiosInstance;

  constructor(baseURL: string = API_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 300000, // 5 minutes for long operations
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Session Management
  async createSession(birthData: BirthData): Promise<SessionResponse> {
    const response = await this.client.post<SessionResponse>(
      '/api/session/create',
      birthData
    );
    return response.data;
  }

  async getSession(sessionId: string) {
    const response = await this.client.get(`/api/session/${sessionId}`);
    return response.data;
  }

  async getChart(sessionId: string): Promise<ChartData> {
    const response = await this.client.get<ChartData>(
      `/api/session/${sessionId}/chart`
    );
    return response.data;
  }

  async getStepVariables(sessionId: string, stepId: string) {
    const response = await this.client.get(
      `/api/session/${sessionId}/variables/${stepId}`
    );
    return response.data;
  }

  // Content Generation
  async generateStep(
    sessionId: string,
    stepId: string,
    provider: 'openai' | 'gemini' = 'openai'
  ): Promise<StepContent> {
    const response = await this.client.post<StepContent>(
      '/api/generate/step',
      {
        session_id: sessionId,
        step_id: stepId,
        provider,
        stream: false,
      }
    );
    return response.data;
  }

  async *generateStepStream(
    sessionId: string,
    stepId: string,
    provider: 'openai' | 'gemini' = 'openai'
  ): AsyncGenerator<any> {
    const response = await fetch(`${API_URL}/api/generate/step/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        step_id: stepId,
        provider,
        stream: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`Stream failed: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Stream reader not available');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data.trim()) {
              try {
                const parsed = JSON.parse(data);
                yield parsed;
              } catch (e) {
                console.error('Failed to parse SSE data:', data);
              }
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async getGenerationStatus(sessionId: string): Promise<GenerationStatus> {
    const response = await this.client.get<GenerationStatus>(
      `/api/generate/status/${sessionId}`
    );
    return response.data;
  }

  async getSessionContent(sessionId: string) {
    const response = await this.client.get(
      `/api/session/${sessionId}/content`
    );
    return response.data;
  }

  async getFullText(sessionId: string) {
    const response = await this.client.get(
      `/api/session/${sessionId}/full-text`
    );
    return response.data;
  }

  // PDF Generation
  async downloadPDF(sessionId: string): Promise<Blob> {
    const response = await this.client.get(
      `/api/session/${sessionId}/pdf`,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  }

  async savePDF(sessionId: string, outputDir?: string) {
    const response = await this.client.post(
      `/api/session/${sessionId}/pdf/save`,
      { output_dir: outputDir }
    );
    return response.data;
  }

  async getPDFPreview(sessionId: string): Promise<PDFPreview> {
    const response = await this.client.get<PDFPreview>(
      `/api/session/${sessionId}/pdf/preview`
    );
    return response.data;
  }

  // Forecast
  async getProgressed(sessionId: string, targetDate?: string) {
    const params = targetDate ? { target_date: targetDate } : {};
    const response = await this.client.get(
      `/api/session/${sessionId}/progressed`,
      { params }
    );
    return response.data;
  }

  async getTransit(sessionId: string, targetDate?: string) {
    const params = targetDate ? { target_date: targetDate } : {};
    const response = await this.client.get(
      `/api/session/${sessionId}/transit`,
      { params }
    );
    return response.data;
  }

  async getForecast(sessionId: string, years: number = 3) {
    const response = await this.client.get(
      `/api/session/${sessionId}/forecast`,
      { params: { years } }
    );
    return response.data;
  }

  // Content Structure
  async getSessionsStructure(): Promise<SessionInfo[]> {
    const response = await this.client.get<SessionInfo[]>(
      '/api/content/sessions'
    );
    return response.data;
  }

  async getStepContent(stepId: string) {
    const response = await this.client.get(`/api/content/step/${stepId}`);
    return response.data;
  }

  // Utilities
  async getPrefectures(): Promise<Prefecture[]> {
    const response = await this.client.get<Prefecture[]>('/api/prefectures');
    return response.data;
  }

  async getAIStatus() {
    const response = await this.client.get('/api/ai/status');
    return response.data;
  }

  async testAI(provider: 'openai' | 'gemini' = 'openai', prompt?: string) {
    const response = await this.client.post('/api/ai/test', null, {
      params: { provider, prompt },
    });
    return response.data;
  }

  // Health Check
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Singleton instance
const api = new AntiGravityAPI();

export default api;
export { AntiGravityAPI };
