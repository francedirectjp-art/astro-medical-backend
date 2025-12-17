// Anti-Gravity Frontend Type Definitions

export interface BirthData {
  name: string;
  birth_year: number;
  birth_month: number;
  birth_day: number;
  birth_hour: number;
  birth_minute: number;
  birth_place: string;
  birth_time_unknown?: boolean;
}

export interface SessionResponse {
  session_id: string;
  chart_data: ChartData;
  variables: Record<string, any>;
}

export interface ChartData {
  name: string;
  birth_datetime: string;
  birth_place: string;
  elements: ElementBalance;
  modalities: ModalityBalance;
  planets: Planet[];
  angles: Angles;
  houses: House[];
  aspects: Aspect[];
}

export interface ElementBalance {
  fire: number;
  earth: number;
  air: number;
  water: number;
  dominant: string;
  lacking: string;
}

export interface ModalityBalance {
  cardinal: number;
  fixed: number;
  mutable: number;
  dominant: string;
}

export interface Planet {
  name_jp: string;
  name_en: string;
  longitude: number;
  latitude: number;
  sign: string;
  sign_jp: string;
  sign_en: string;
  degree: number;
  degree_formatted: string;
  sabian_degree: number;
  sabian_symbol?: string;
  retrograde: boolean;
  speed: number;
  house: number;
}

export interface Angles {
  asc: Planet;
  mc: Planet;
  ic: Planet;
  dc: Planet;
}

export interface House {
  number: number;
  cusp_degree: number;
  sign: string;
  sign_jp: string;
}

export interface Aspect {
  planet1: string;
  planet2: string;
  aspect: string;
  aspect_jp: string;
  orb: number;
  applying: boolean;
}

export interface StepContent {
  step_id: string;
  static_content: Record<string, ContentBlock>;
  dynamic_content: Record<string, string>;
  character_count: number;
  status: string;
}

export interface ContentBlock {
  title: string;
  text: string;
}

export interface GenerationStatus {
  session_id: string;
  current_step: string;
  total_steps: number;
  completed_steps: number;
  status: 'pending' | 'generating' | 'completed' | 'error';
  total_characters: number;
}

export interface SessionInfo {
  session_id: string;
  title: string;
  description: string;
  steps: StepInfo[];
}

export interface StepInfo {
  step_id: string;
  chapter_number: string;
  chapter_title: string;
  target_characters: number;
  completed: boolean;
}

export interface PDFPreview {
  session_id: string;
  document_title: string;
  total_characters: number;
  completed_steps: number;
  sections: PDFSection[];
}

export interface PDFSection {
  session_id: number;
  title: string;
  steps: PDFStepInfo[];
}

export interface PDFStepInfo {
  step_id: string;
  chapter_title: string;
  character_count: number;
  has_content: boolean;
}

export interface Prefecture {
  name: string;
  latitude: number;
  longitude: number;
}

export const PREFECTURES: string[] = [
  "東京都", "大阪府", "京都府", "神奈川県", "愛知県", "北海道",
  "福岡県", "兵庫県", "埼玉県", "千葉県", "広島県", "宮城県",
  "茨城県", "静岡県", "新潟県", "長野県", "岐阜県", "群馬県",
  "栃木県", "岡山県", "福島県", "三重県", "熊本県", "鹿児島県",
  "沖縄県", "山口県", "愛媛県", "長崎県", "奈良県", "滋賀県",
  "青森県", "岩手県", "石川県", "山形県", "宮崎県", "富山県",
  "秋田県", "和歌山県", "香川県", "山梨県", "佐賀県", "大分県",
  "福井県", "徳島県", "高知県", "島根県", "鳥取県"
];
