'use client';

import { Suspense, useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Card, Form, Input, Button, Typography, Alert, Divider, Space } from 'antd';
import { LockOutlined, MailOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/lib/store/auth';
import { LoginRequest } from '@/types/auth.types';

const { Title, Text } = Typography;

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isLoading, error, isAuthenticated, setError } = useAuthStore();
  const [form] = Form.useForm();
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showEmailChangeSuccess, setShowEmailChangeSuccess] = useState(false);

  // 如果已经登录，重定向到首页
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  // 检查是否是邮箱修改后的重定向
  useEffect(() => {
    const message = searchParams.get('message');
    if (message === 'email_changed') {
      setShowEmailChangeSuccess(true);
    }
  }, [searchParams]);

  // 清除错误信息
  useEffect(() => {
    return () => {
      setError(null);
    };
  }, [setError]);

  const handleLogin = async (values: LoginRequest) => {
    const success = await login(values);
    if (success) {
      router.push('/');
    }
  };

  const handleForgotPassword = async (values: { email: string }) => {
    // TODO: 实现忘记密码功能
    console.log('Forgot password for:', values.email);
  };

  if (isAuthenticated) {
    return null; // 避免闪烁
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Title level={2} className="text-gray-900">
            QA测试知识协作平台
          </Title>
          <Text type="secondary" className="mt-2 text-sm">
            专为测试团队打造的知识分享与协作平台
          </Text>
        </div>

        <Card className="shadow-lg">
          {!showForgotPassword ? (
            <>
              <Title level={3} className="text-center mb-6">
                登录账户
              </Title>

              {showEmailChangeSuccess && (
                <Alert
                  message="邮箱修改成功"
                  description="您的邮箱地址已成功更新，请使用新邮箱地址登录。"
                  type="success"
                  showIcon
                  className="mb-4"
                  closable
                  onClose={() => setShowEmailChangeSuccess(false)}
                />
              )}

              {error && (
                <Alert
                  message={error}
                  type="error"
                  showIcon
                  className="mb-4"
                  closable
                  onClose={() => setError(null)}
                />
              )}

              <Form
                form={form}
                name="login"
                onFinish={handleLogin}
                layout="vertical"
                size="large"
              >
                <Form.Item
                  name="email"
                  label="邮箱地址"
                  rules={[
                    { required: true, message: '请输入邮箱地址' },
                    { type: 'email', message: '请输入有效的邮箱地址' },
                  ]}
                >
                  <Input
                    prefix={<MailOutlined />}
                    placeholder="请输入邮箱地址"
                    autoComplete="email"
                  />
                </Form.Item>

                <Form.Item
                  name="password"
                  label="密码"
                  rules={[{ required: true, message: '请输入密码' }]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="请输入密码"
                    autoComplete="current-password"
                  />
                </Form.Item>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={isLoading}
                    className="w-full"
                    size="large"
                  >
                    {isLoading ? '登录中...' : '登录'}
                  </Button>
                </Form.Item>
              </Form>

              <Divider />

              <div className="text-center space-y-2">
                <div>
                  <Button
                    type="link"
                    onClick={() => setShowForgotPassword(true)}
                    className="p-0"
                  >
                    忘记密码？
                  </Button>
                </div>
                <div>
                  <Text type="secondary">还没有账户？</Text>{' '}
                  <Link href="/register">
                    <Button type="link" className="p-0">
                      立即注册
                    </Button>
                  </Link>
                </div>
              </div>
            </>
          ) : (
            <>
              <Title level={3} className="text-center mb-6">
                重置密码
              </Title>

              <Text type="secondary" className="block text-center mb-4">
                输入您的邮箱地址，我们将发送重置链接给您
              </Text>

              <Form
                name="forgot-password"
                onFinish={handleForgotPassword}
                layout="vertical"
                size="large"
              >
                <Form.Item
                  name="email"
                  label="邮箱地址"
                  rules={[
                    { required: true, message: '请输入邮箱地址' },
                    { type: 'email', message: '请输入有效的邮箱地址' },
                  ]}
                >
                  <Input
                    prefix={<MailOutlined />}
                    placeholder="请输入邮箱地址"
                  />
                </Form.Item>

                <Form.Item>
                  <Space className="w-full" direction="vertical" size="middle">
                    <Button
                      type="primary"
                      htmlType="submit"
                      loading={isLoading}
                      className="w-full"
                      size="large"
                    >
                      发送重置链接
                    </Button>
                    <Button
                      type="default"
                      onClick={() => setShowForgotPassword(false)}
                      className="w-full"
                      size="large"
                    >
                      返回登录
                    </Button>
                  </Space>
                </Form.Item>
              </Form>
            </>
          )}
        </Card>

        <div className="text-center">
          <Text type="secondary" className="text-xs">
            登录即表示您同意我们的服务条款和隐私政策
          </Text>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginContent />
    </Suspense>
  );
}
