'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, Form, Input, Button, Typography, Alert, Divider, Select, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, EditOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/lib/store/auth';
import { RegisterRequest, UserRole, ProfessionalRole, ExperienceLevel, Specialty } from '@/types/auth.types';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error, isAuthenticated, setError } = useAuthStore();
  const [form] = Form.useForm();
  const [registrationSuccess, setRegistrationSuccess] = useState(false);

  // 如果已经登录，重定向到首页
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  // 清除错误信息
  useEffect(() => {
    return () => {
      setError(null);
    };
  }, [setError]);

  const handleRegister = async (values: RegisterRequest) => {
    const success = await register(values);
    if (success) {
      setRegistrationSuccess(true);
      message.success('注册成功！请查看邮箱验证邮件。');
      form.resetFields();
    }
  };

  const validatePassword = (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('请输入密码'));
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
      return Promise.reject(new Error('请确认密码'));
    }
    if (value !== form.getFieldValue('password')) {
      return Promise.reject(new Error('两次输入的密码不一致'));
    }
    return Promise.resolve();
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
            加入我们，开始您的测试知识分享之旅
          </Text>
        </div>

        <Card className="shadow-lg">
          {!registrationSuccess ? (
            <>
              <Title level={3} className="text-center mb-6">
                创建账户
              </Title>

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
                name="register"
                onFinish={handleRegister}
                layout="vertical"
                size="large"
                scrollToFirstError
              >
                <Form.Item
                  name="username"
                  label="用户名"
                  rules={[
                    { required: true, message: '请输入用户名' },
                    { min: 3, message: '用户名至少需要3个字符' },
                    { max: 50, message: '用户名不能超过50个字符' },
                    { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/, message: '用户名只能包含字母、数字、下划线和中文' },
                  ]}
                >
                  <Input
                    prefix={<UserOutlined />}
                    placeholder="请输入用户名"
                    autoComplete="username"
                  />
                </Form.Item>

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
                  rules={[{ validator: validatePassword }]}
                  hasFeedback
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="请输入密码"
                    autoComplete="new-password"
                  />
                </Form.Item>

                <Form.Item
                  name="confirmPassword"
                  label="确认密码"
                  dependencies={['password']}
                  rules={[{ validator: validateConfirmPassword }]}
                  hasFeedback
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="请再次输入密码"
                    autoComplete="new-password"
                  />
                </Form.Item>

                <Form.Item
                  name="nickname"
                  label="昵称"
                  rules={[
                    { max: 100, message: '昵称不能超过100个字符' },
                  ]}
                >
                  <Input
                    prefix={<EditOutlined />}
                    placeholder="请输入昵称（可选）"
                  />
                </Form.Item>

                <Form.Item
                  name="bio"
                  label="个人简介"
                  rules={[
                    { max: 500, message: '个人简介不能超过500个字符' },
                  ]}
                >
                  <TextArea
                    placeholder="简单介绍一下自己（可选）"
                    rows={3}
                    showCount
                    maxLength={500}
                  />
                </Form.Item>

                <Form.Item
                  name="role"
                  label="职业角色"
                  initialValue="test_engineer"
                  rules={[
                    { required: true, message: '请选择您的职业角色' },
                  ]}
                >
                  <Select placeholder="请选择您的职业角色" showSearch>
                    <Option value="test_engineer">测试工程师</Option>
                    <Option value="senior_test_engineer">高级测试工程师</Option>
                    <Option value="test_lead">测试组长</Option>
                    <Option value="test_manager">测试经理</Option>
                    <Option value="qa_engineer">QA工程师</Option>
                    <Option value="automation_engineer">自动化测试工程师</Option>
                    <Option value="performance_engineer">性能测试工程师</Option>
                    <Option value="security_tester">安全测试工程师</Option>
                    <Option value="game_tester">游戏测试工程师</Option>
                    <Option value="mobile_tester">移动端测试工程师</Option>
                    <Option value="test_architect">测试架构师</Option>
                    <Option value="qa_director">QA总监</Option>
                    <Option value="developer">开发工程师</Option>
                    <Option value="product_manager">产品经理</Option>
                    <Option value="student">学生</Option>
                    <Option value="other">其他</Option>
                  </Select>
                </Form.Item>

                <Form.Item
                  name="experience_level"
                  label="工作经验"
                  initialValue="1-3"
                  rules={[
                    { required: true, message: '请选择您的工作经验' },
                  ]}
                >
                  <Select placeholder="请选择您的工作经验">
                    <Option value="0-1">0-1年（新手）</Option>
                    <Option value="1-3">1-3年（初级）</Option>
                    <Option value="3-5">3-5年（中级）</Option>
                    <Option value="5-8">5-8年（高级）</Option>
                    <Option value="8+">8年以上（专家）</Option>
                  </Select>
                </Form.Item>

                <Form.Item
                  name="specialties"
                  label="专业领域"
                  rules={[
                    { required: true, message: '请选择至少一个专业领域' },
                  ]}
                >
                  <Select 
                    mode="multiple" 
                    placeholder="请选择您的专业领域（可多选）"
                    maxTagCount={3}
                    maxTagTextLength={10}
                  >
                    <Option value="functional">功能测试</Option>
                    <Option value="automation">自动化测试</Option>
                    <Option value="performance">性能测试</Option>
                    <Option value="security">安全测试</Option>
                    <Option value="mobile">移动端测试</Option>
                    <Option value="web">Web测试</Option>
                    <Option value="api">接口测试</Option>
                    <Option value="game">游戏测试</Option>
                    <Option value="compatibility">兼容性测试</Option>
                    <Option value="usability">可用性测试</Option>
                    <Option value="database">数据库测试</Option>
                    <Option value="devops">DevOps/CI/CD</Option>
                  </Select>
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
                    {isLoading ? '注册中...' : '注册账户'}
                  </Button>
                </Form.Item>
              </Form>

              <Divider />

              <div className="text-center">
                <Text type="secondary">已有账户？</Text>{' '}
                <Link href="/login">
                  <Button type="link" className="p-0">
                    立即登录
                  </Button>
                </Link>
              </div>
            </>
          ) : (
            <div className="text-center py-8">
              <div className="mb-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              
              <Title level={3} className="text-green-600 mb-4">
                注册成功！
              </Title>
              
              <Text type="secondary" className="block mb-6">
                我们已向您的邮箱发送了验证邮件，请点击邮件中的链接完成账户激活。
              </Text>
              
              <div className="space-y-3">
                <Button
                  type="primary"
                  onClick={() => router.push('/login')}
                  className="w-full"
                  size="large"
                >
                  前往登录
                </Button>
                
                <Button
                  type="default"
                  onClick={() => setRegistrationSuccess(false)}
                  className="w-full"
                  size="large"
                >
                  重新注册
                </Button>
              </div>
            </div>
          )}
        </Card>

        <div className="text-center">
          <Text type="secondary" className="text-xs">
            注册即表示您同意我们的服务条款和隐私政策
          </Text>
        </div>
      </div>
    </div>
  );
}