export type UserRole = 'member' | 'admin' | 'super_admin';

export type ProfessionalRole = 
  | 'test_engineer'
  | 'senior_test_engineer'
  | 'test_lead'
  | 'test_manager'
  | 'qa_engineer'
  | 'automation_engineer'
  | 'performance_engineer'
  | 'security_tester'
  | 'game_tester'
  | 'mobile_tester'
  | 'test_architect'
  | 'qa_director'
  | 'developer'
  | 'product_manager'
  | 'student'
  | 'other';

export type ExperienceLevel = '0-1' | '1-3' | '3-5' | '5-8' | '8+';

export type Specialty = 
  | 'functional'
  | 'automation'
  | 'performance'
  | 'security'
  | 'mobile'
  | 'web'
  | 'api'
  | 'game'
  | 'compatibility'
  | 'usability'
  | 'database'
  | 'devops';

export interface User {
  id: string;
  username: string;
  email: string;
  nickname?: string;
  avatar_url?: string;
  bio?: string;
  role: UserRole;
  professional_role?: ProfessionalRole;
  experience_level?: ExperienceLevel;
  specialties?: Specialty[];
  team_id?: string;
  skills?: Record<string, any>;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
  created_at: string;
  updated_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  nickname?: string;
  bio?: string;
  role?: UserRole;
  professional_role?: ProfessionalRole;
  experience_level?: ExperienceLevel;
  specialties?: Specialty[];
  team_id?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface UserUpdate {
  nickname?: string;
  bio?: string;
  avatar_url?: string;
  professional_role?: ProfessionalRole;
  experience_level?: ExperienceLevel;
  specialties?: Specialty[];
  skills?: Record<string, any>;
}

export interface PasswordReset {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export interface EmailVerification {
  token: string;
}

export interface EmailChangeRequest {
  new_email: string;
  password: string;
}

export interface EmailChangeConfirm {
  token: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
  path: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}