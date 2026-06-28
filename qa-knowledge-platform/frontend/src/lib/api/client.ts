export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') || 'http://localhost:8000';

export function apiUrl(path: string) {
  if (/^https?:\/\//.test(path)) {
    return path;
  }

  if (path.startsWith('/api/')) {
    return `${API_BASE_URL}${path}`;
  }

  return `${API_BASE_URL}/api/v1${path.startsWith('/') ? path : `/${path}`}`;
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(apiUrl(path), {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}
