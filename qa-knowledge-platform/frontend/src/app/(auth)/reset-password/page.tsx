'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card, Form, Input, Button, Typography, Alert } from 'antd';
import { LockOutlined, CheckCircleOutlined } from '@ant-design/icons';
import AuthAPI from '@/lib/api/auth';

const { Title, Text } = Typography;

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [form] = Form.useForm();
  const [isLoading, setIsLoading] = useState(false);
  const [isReset, setIsReset] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const tokenParam = searchParams.get('token');
    
    if (!tokenParam) {
      setError('重置链接无效');
      return;
    }

    setToken(tokenParam);
  }, [searchParams]);

  const handleResetPassword = async (values: { password: string }) => {
    if (!token) {
      setError('重置令牌无效');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const result = await AuthAPI.resetPassword({
        token,
        new_password: values.password,
      });
      
      if (result.reset) {
        setIsReset(true);
        form.resetFields();
      } else {
        setError('密码重置失败');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || '重置失败，请重试';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const validatePassword = (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('请输入新密码'));
    }
    if (value.length < 8) {
      return Promise.reject(new Error('密码至少需要8个字符'));
    }
    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
      return Promise.reject(new Error('密码需要包含大小写字母和数字'));
    }
    return Promise.resolve();
  };

  const validateConfirmPassword = (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('请确认新密码'));
    }
    if (value !== form.getFieldValue('password')) {
      return Promise.reject(new Error('两次输入的密码不一致'));
    }
    return Promise.resolve();
  };

  if (!token && !error) {
    return null; // 避免闪烁
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <Title level={2} className="text-gray-900">
            重置密码
          </Title>
        </div>

        <Card className="shadow-lg">
          {!token ? (
            <div className="text-center py-8">
              <Alert
                message="重置链接无效"
                description="重置链接可能已过期或无效，请重新申请密码重置。"
                type="error"
                showIcon
                className="mb-6"
              />
              <Button
                type="primary"
                size="large"
                onClick={() => router.push('/login')}
                className="w-full"
              >
                返回登录
              </Button>
            </div>
          ) : isReset ? (
            <div className="text-center py-8">
              <CheckCircleOutlined className="text-6xl text-green-500 mb-4" />
              <Title level={3} className="text-green-600 mb-4">
                密码重置成功！
              </Title>
              <Text type="secondary" className="block mb-6">
                您的密码已成功重置，现在可以使用新密码登录。
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
            <>
              <Title level={3} className="text-center mb-6">
                设置新密码
              </Title>

              <Text type="secondary" className="block text-center mb-6">
                请输入您的新密码
              </Text>

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
                name="reset-password"
                onFinish={handleResetPassword}
                layout="vertical"
                size="large"
              >
                <Form.Item
                  name="password"
                  label="新密码"
                  rules={[{ validator: validatePassword }]}
                  hasFeedback
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="请输入新密码"
                    autoComplete="new-password"
                  />
                </Form.Item>

                <Form.Item
                  name="confirmPassword"
                  label="确认新密码"
                  dependencies={['password']}
                  rules={[{ validator: validateConfirmPassword }]}
                  hasFeedback
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="请再次输入新密码"
                    autoComplete="new-password"
                  />
                </Form.Item>

                <div className="mb-4">
                  <Text type="secondary" className="text-xs">
                    密码要求：至少8个字符，包含大小写字母和数字
                  </Text>
                </div>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={isLoading}
                    className="w-full"
                    size="large"
                  >
                    {isLoading ? '重置中...' : '重置密码'}
                  </Button>
                </Form.Item>
              </Form>

              <div className="text-center mt-4">
                <Button
                  type="link"
                  onClick={() => router.push('/login')}
                  className="p-0"
                >
                  返回登录
                </Button>
              </div>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}