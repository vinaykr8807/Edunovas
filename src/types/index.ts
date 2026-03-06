export type Mode = 'ROUTER' | 'INTERVIEWER' | 'QUIZ' | 'ROADMAP' | 'MOTIVATION' | 'SUPPORT' | 'TEACHING' | 'CODING_MENTOR';

export interface User {
  email: string;
  full_name?: string;
  role: 'student' | 'admin';
  token: string;
}

export interface StudentProfile {
  degree: string;
  branch: string;
  year: string;
  domain: string;
  skills: string[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  mode?: Mode;
}

export interface PersonaConfig {
  id: Mode;
  name: string;
  tagline: string;
  icon: string;
  color: string;
  prompt: string;
}
