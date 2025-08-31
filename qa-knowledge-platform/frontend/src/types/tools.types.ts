export interface Tool {
  id: string;
  category_id: string;
  name: string;
  url: string;
  description: string;
  icon_url?: string;
  features: string[];
  avg_rating: number;
  rating_count: number;
  usage_count: number;
  is_recommended: boolean;
  created_at: string;
  updated_at: string;
  category?: ToolCategory;
}

export interface ToolCategory {
  id: string;
  name: string;
  description?: string;
  type: '功能测试' | '性能测试' | '自动化测试' | '移动测试' | '游戏测试' | '管理工具';
  sort_order: number;
  created_at: string;
}

export interface ToolRating {
  id: string;
  tool_id: string;
  user_id: string;
  rating: number; // 1-5
  review?: string;
  pros_cons?: {
    pros: string[];
    cons: string[];
  };
  created_at: string;
  updated_at: string;
  user?: {
    id: string;
    username: string;
    nickname?: string;
    avatar_url?: string;
  };
}

export interface CreateToolRequest {
  name: string;
  url: string;
  description: string;
  category_id: string;
  features: string[];
  icon_url?: string;
}

export interface CreateToolRatingRequest {
  rating: number;
  review?: string;
  pros_cons?: {
    pros: string[];
    cons: string[];
  };
}

export interface ToolListParams {
  page?: number;
  size?: number;
  category?: string;
  is_recommended?: boolean;
  search?: string;
}