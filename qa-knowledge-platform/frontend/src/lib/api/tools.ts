import { apiRequest } from './client';
import { BusinessDomain, QaCategory, QaTool } from '@/types/platform.types';

export interface ToolCreatePayload {
  category_id: string;
  name: string;
  url: string;
  description: string;
  business_domain: BusinessDomain;
  project_key?: string;
  features: string[];
}

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

export function listToolCategories(businessDomain?: BusinessDomain) {
  const query = new URLSearchParams();
  if (businessDomain) query.set('business_domain', businessDomain);
  return apiRequest<QaCategory[]>(`/tools/categories?${query.toString()}`);
}

export function createTool(payload: ToolCreatePayload) {
  return apiRequest<QaTool>('/tools/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
