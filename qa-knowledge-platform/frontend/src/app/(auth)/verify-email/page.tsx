'use client';

import { Suspense, useCallback, useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card, Button, Typography, Alert, Spin } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import AuthAPI from '@/lib/api/auth';

const { Title, Text } = Typography;

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(true);
  const [isVerified, setIsVerified] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const verifyEmail = useCallback(async (token: string) => {
    try {
      setIsLoading(true);
      const result = await AuthAPI.verifyEmail({ token });
      
      if (result.verified) {
        setIsVerified(true);
      } else {
        setError('邮箱验证失败');
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : '验证失败，请重试';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      setError('验证链接无效');
      setIsLoading(false);
      return;
    }

    verifyEmail(token);
  }, [searchParams, verifyEmail]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <Title level={2} className="text-gray-900">
            邮箱验证
          </Title>
        </div>

        <Card className="shadow-lg">
          {isLoading ? (
            <div className="text-center py-8">
              <Spin size="large" />
              <Text className="block mt-4" type="secondary">
                正在验证您的邮箱...
              </Text>
            </div>
          ) : isVerified ? (
            <div className="text-center py-8">
              <CheckCircleOutlined className="text-6xl text-green-500 mb-4" />
              <Title level={3} className="text-green-600 mb-4">
                邮箱验证成功！
              </Title>
              <Text type="secondary" className="block mb-6">
                您的账户已成功激活，现在可以登录使用平台的所有功能。
              </Text>
              <Button
                type="primary"
                size="large"
                onClick={() => router.push('/login')}
                className="w-full"
              >
                前往登录
              </Button>
            </div>
          ) : (
            <div className="text-center py-8">
              <CloseCircleOutlined className="text-6xl text-red-500 mb-4" />
              <Title level={3} className="text-red-600 mb-4">
                验证失败
              </Title>
              {error && (
                <Alert
                  message={error}
                  type="error"
                  showIcon
                  className="mb-6"
                />
              )}
              <Text type="secondary" className="block mb-6">
                验证链接可能已过期或无效。请重新注册或联系管理员。
              </Text>
              <div className="space-y-3">
                <Button
                  type="primary"
                  size="large"
                  onClick={() => router.push('/register')}
                  className="w-full"
                >
                  重新注册
                </Button>
                <Button
                  type="default"
                  size="large"
                  onClick={() => router.push('/login')}
                  className="w-full"
                >
                  返回登录
                </Button>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={null}>
      <VerifyEmailContent />
    </Suspense>
  );
}
