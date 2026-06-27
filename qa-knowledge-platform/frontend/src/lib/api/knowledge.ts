import { apiRequest } from './client';
import { BusinessDomain, QaArticle, QaCategory, ReviewStatus } from '@/types/platform.types';

export function listArticles(params: {
  business_domain?: BusinessDomain;
  review_status?: ReviewStatus;
}) {
  const query = new URLSearchParams();
  if (params.business_domain) query.set('business_domain', params.business_domain);
  if (params.review_status) query.set('review_status', params.review_status);
  return apiRequest<QaArticle[]>(`/knowledge/articles?${query.toString()}`);
}

export function listKnowledgeCategories(businessDomain?: BusinessDomain) {
  const query = new URLSearchParams();
  if (businessDomain) query.set('business_domain', businessDomain);
  return apiRequest<QaCategory[]>(`/knowledge/categories?${query.toString()}`);
}
