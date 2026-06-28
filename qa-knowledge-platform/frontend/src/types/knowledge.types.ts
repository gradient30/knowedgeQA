export interface Article {
  id: string;
  user_id: string;
  category_id: string;
  project_id?: string;
  title: string;
  summary?: string;
  content: string;
  cover_image?: string;
  status: 'draft' | 'private' | 'team' | 'public';
  type: '经验分享' | 'Bug案例' | '工具教程' | '最佳实践';
  view_count: number;
  like_count: number;
  comment_count: number;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  published_at?: string;
  author?: {
    id: string;
    username: string;
    nickname?: string;
    avatar_url?: string;
  };
  category?: Category;
  tags?: Tag[];
}

export interface Category {
  id: string;
  name: string;
  description?: string;
  type: '功能测试' | '性能测试' | '自动化测试' | '游戏测试' | '安全测试' | '移动测试';
  parent_id?: string;
  sort_order: number;
  created_at: string;
}

export interface Tag {
  id: string;
  name: string;
  color?: string;
  category: '技术' | '工具' | '平台' | '难度' | '类型';
  usage_count: number;
  created_at: string;
}

export interface CreateArticleRequest {
  title: string;
  content: string;
  category_id: string;
  project_id?: string;
  type: '经验分享' | 'Bug案例' | '工具教程' | '最佳实践';
  tags?: string[];
  status: 'draft' | 'private' | 'team' | 'public';
  metadata?: Record<string, unknown>;
}

export interface ArticleListParams {
  page?: number;
  size?: number;
  category?: string;
  type?: string;
  project_id?: string;
  status?: string;
  search?: string;
}
