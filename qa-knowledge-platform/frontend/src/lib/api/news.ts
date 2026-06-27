import { apiRequest } from './client';
import { BusinessDomain, QaNewsItem, QaNewsSource, ReviewStatus } from '@/types/platform.types';

export function listNewsItems(params: {
  business_domain?: BusinessDomain;
  review_status?: ReviewStatus;
}) {
  const query = new URLSearchParams();
  if (params.business_domain) query.set('business_domain', params.business_domain);
  if (params.review_status) query.set('review_status', params.review_status);
  return apiRequest<QaNewsItem[]>(`/news/items?${query.toString()}`);
}

export function listNewsSources(businessDomain?: BusinessDomain) {
  const query = new URLSearchParams();
  if (businessDomain) query.set('business_domain', businessDomain);
  return apiRequest<QaNewsSource[]>(`/news/sources?${query.toString()}`);
}
