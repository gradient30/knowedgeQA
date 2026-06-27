import { apiRequest } from './client';
import { BusinessDomain, QaTool } from '@/types/platform.types';

export function listTools(params: {
  business_domain?: BusinessDomain;
  is_recommended?: boolean;
}) {
  const query = new URLSearchParams();
  if (params.business_domain) query.set('business_domain', params.business_domain);
  if (params.is_recommended !== undefined) {
    query.set('is_recommended', String(params.is_recommended));
  }
  return apiRequest<QaTool[]>(`/tools/?${query.toString()}`);
}
