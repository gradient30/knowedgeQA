export type BusinessDomain = 'saas' | 'game' | 'common';
export type ReviewStatus = 'pending' | 'approved' | 'rejected' | 'archived';
export type Visibility = 'private' | 'team' | 'public';

export interface QaArticle {
  id: string;
  title: string;
  summary?: string;
  content: string;
  type: '经验分享' | 'Bug案例' | '工具教程' | '最佳实践';
  business_domain: BusinessDomain;
  visibility: Visibility;
  review_status: ReviewStatus;
  project_key?: string;
  tags: string[];
  attachment_file_ids: string[];
}

export interface QaCategory {
  id: string;
  name: string;
  description?: string;
  type: string;
  business_domain: BusinessDomain;
  sort_order: number;
}

export interface QaTool {
  id: string;
  category_id: string;
  name: string;
  url: string;
  description: string;
  business_domain: BusinessDomain;
  project_key?: string;
  features: string[];
  avg_rating: number;
  rating_count: number;
  usage_count: number;
  is_recommended: boolean;
}

export interface QaNewsItem {
  id: string;
  source_id: string;
  title: string;
  url: string;
  summary?: string;
  business_domain: BusinessDomain;
  tags: string[];
  relevance_score: number;
  review_status: ReviewStatus;
}

export interface QaNewsSource {
  id: string;
  name: string;
  url: string;
  category: string;
  business_domain: BusinessDomain;
  keywords: string[];
  frequency_hours: number;
  is_active: boolean;
}
