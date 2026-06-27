'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Card, Result, Button, Spin, Alert } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, MailOutlined } from '@ant-design/icons';

function ConfirmEmailChangeContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const token = searchParams.get('token');

  useEffect(() => {
    const confirmEmailChange = async () => {
      if (!token) {
        setStatus('error');
        setMessage('验证链接无效，缺少验证令牌');
        return;
      }

      try {
        const response = await fetch('/api/v1/users/profile/confirm-email-change', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        });

        if (response.ok) {
          const result = await response.json();
          setStatus('success');
          setMessage(result.message || '邮箱修改成功');
          
          // 清除本地存储的token，强制用户重新登录
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          
          // 3秒后跳转到登录页
          setTimeout(() => {
            router.push('/login?message=email_changed');
          }, 3000);
        } else {
          const error = await response.json();
          setStatus('error');
          setMessage(error.detail || '邮箱修改失败');
        }
      } catch (error) {
        setStatus('error');
        setMessage('网络错误，请稍后重试');
      }
    };

    confirmEmailChange();
  }, [token, router]);

  const handleReturnToLogin = () => {
    router.push('/login');
  };

  const handleReturnToProfile = () => {
    router.push('/profile');
  };

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md text-center">
          <Spin size="large" />
          <div className="mt-4">
            <h3 className="text-lg font-medium text-gray-900">正在验证邮箱修改</h3>
            <p className="text-gray-500 mt-2">请稍候，我们正在处理您的请求...</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        {status === 'success' ? (
          <Result
            icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            title="邮箱修改成功"
            subTitle={
              <div className="space-y-2">
                <p>{message}</p>
                <Alert
                  message="重要提醒"
                  description="您的邮箱地址已成功更新。为了安全起见，请使用新邮箱地址重新登录。"
                  type="info"
                  showIcon
                  className="text-left"
                />
                <p className="text-sm text-gray-500">
                  页面将在3秒后自动跳转到登录页面...
                </p>
              </div>
            }
            extra={[
              <Button 
                type="primary" 
                key="login" 
                icon={<MailOutlined />}
                onClick={handleReturnToLogin}
              >
                立即登录
              </Button>
            ]}
          />
        ) : (
          <Result
            icon={<CloseCircleOutlined style={{ color: '#ff4d4f' }} />}
            title="邮箱修改失败"
            subTitle={
              <div className="space-y-2">
                <p>{message}</p>
                <Alert
                  message="可能的原因"
                  description={
                    <ul className="text-left list-disc list-inside space-y-1">
                      <li>验证链接已过期（有效期1小时）</li>
                      <li>验证链接已被使用</li>
                      <li>新邮箱地址已被其他用户使用</li>
                      <li>网络连接问题</li>
                    </ul>
                  }
                  type="warning"
                  showIcon
                />
              </div>
            }
            extra={[
              <Button key="profile" onClick={handleReturnToProfile}>
                返回个人设置
              </Button>,
              <Button 
                type="primary" 
                key="login" 
                onClick={handleReturnToLogin}
              >
                返回登录
              </Button>
            ]}
          />
        )}
      </Card>
    </div>
  );
}

export default function ConfirmEmailChangePage() {
  return (
    <Suspense fallback={null}>
      <ConfirmEmailChangeContent />
    </Suspense>
  );
}
