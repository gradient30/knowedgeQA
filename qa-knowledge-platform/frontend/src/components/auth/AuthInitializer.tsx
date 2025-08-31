'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/lib/store/auth';

export default function AuthInitializer({ children }: { children: React.ReactNode }) {
  const { initialize, isLoading } = useAuthStore();

  useEffect(() => {
    // 页面加载时初始化认证状态
    initialize();
  }, [initialize]);

  // 可以在这里添加加载状态显示
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}