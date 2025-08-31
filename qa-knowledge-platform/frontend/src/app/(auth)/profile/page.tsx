'use client';

import { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Typography, Alert, Avatar, Upload, Divider, Space, Tag, Modal, message, Select } from 'antd';
import { UserOutlined, EditOutlined, CameraOutlined, SaveOutlined, LockOutlined, DownloadOutlined, UploadOutlined, MailOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/lib/store/auth';
import { UserUpdate } from '@/types/auth.types';
import type { UploadProps } from 'antd';

const { Title, Text } = Typography;
const { TextArea, Password } = Input;
const { Option } = Select;

export default function ProfilePage() {
  const { user, updateProfile, isLoading, error, setError } = useAuthStore();
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [emailChangeForm] = Form.useForm();
  const [isEditing, setIsEditing] = useState(false);
  const [isPasswordModalVisible, setIsPasswordModalVisible] = useState(false);
  const [isExportModalVisible, setIsExportModalVisible] = useState(false);
  const [isEmailChangeModalVisible, setIsEmailChangeModalVisible] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isChangingEmail, setIsChangingEmail] = useState(false);

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        nickname: user.nickname || '',
        bio: user.bio || '',
      });
    }
  }, [user, form]);

  // 清除错误信息
  useEffect(() => {
    return () => {
      setError(null);
    };
  }, [setError]);

  const handleUpdateProfile = async (values: UserUpdate) => {
    const success = await updateProfile(values);
    if (success) {
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    if (user) {
      form.setFieldsValue({
        nickname: user.nickname || '',
        bio: user.bio || '',
      });
    }
    setIsEditing(false);
    setError(null);
  };

  const getRoleText = (role: string) => {
    const roleMap = {
      member: '测试工程师',
      admin: '测试经理',
      super_admin: '超级管理员',
    };
    return roleMap[role as keyof typeof roleMap] || role;
  };

  const getRoleColor = (role: string) => {
    const colorMap = {
      member: 'blue',
      admin: 'orange',
      super_admin: 'red',
    };
    return colorMap[role as keyof typeof colorMap] || 'default';
  };

  // 头像上传处理
  const handleAvatarUpload: UploadProps['customRequest'] = async (options) => {
    const { file, onSuccess, onError } = options;
    
    try {
      const formData = new FormData();
      formData.append('file', file as File);
      
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/users/profile/upload-avatar', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        message.success('头像上传成功');
        // 更新用户信息中的头像URL
        if (user) {
          await updateProfile({ avatar_url: result.avatar_url });
        }
        onSuccess?.(result);
      } else {
        const error = await response.json();
        message.error(error.detail || '头像上传失败');
        onError?.(new Error(error.detail));
      }
    } catch (error) {
      message.error('头像上传失败');
      onError?.(error as Error);
    }
  };

  // 密码修改处理
  const handlePasswordChange = async (values: { current_password: string; new_password: string; confirm_password: string }) => {
    if (values.new_password !== values.confirm_password) {
      message.error('两次输入的密码不一致');
      return;
    }

    setIsChangingPassword(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/users/profile/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: values.current_password,
          new_password: values.new_password,
        }),
      });

      if (response.ok) {
        message.success('密码修改成功');
        setIsPasswordModalVisible(false);
        passwordForm.resetFields();
      } else {
        const error = await response.json();
        message.error(error.detail || '密码修改失败');
      }
    } catch (error) {
      message.error('密码修改失败');
    } finally {
      setIsChangingPassword(false);
    }
  };

  // 邮箱修改处理
  const handleEmailChange = async (values: { new_email: string; password: string }) => {
    setIsChangingEmail(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/users/profile/request-email-change', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        message.success('邮箱修改验证邮件已发送到新邮箱，请查收并点击验证链接');
        setIsEmailChangeModalVisible(false);
        emailChangeForm.resetFields();
      } else {
        const error = await response.json();
        message.error(error.detail || '邮箱修改请求失败');
      }
    } catch (error) {
      message.error('邮箱修改请求失败');
    } finally {
      setIsChangingEmail(false);
    }
  };

  // 数据导出处理
  const handleDataExport = async (values: { format: string; include_articles: boolean; include_comments: boolean; include_profile: boolean }) => {
    setIsExporting(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/users/profile/export-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `user_data_${user?.username}.${values.format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        message.success('数据导出成功');
        setIsExportModalVisible(false);
      } else {
        const error = await response.json();
        message.error(error.detail || '数据导出失败');
      }
    } catch (error) {
      message.error('数据导出失败');
    } finally {
      setIsExporting(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Text>请先登录</Text>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <Title level={2}>个人资料</Title>
          <Text type="secondary">管理您的个人信息和账户设置</Text>
        </div>

        <div className="space-y-6">
          {/* 基本信息卡片 */}
          <Card className="shadow-sm">
            <div className="flex items-center space-x-4 mb-6">
              <div className="relative">
                <Avatar
                  size={80}
                  src={user.avatar_url}
                  icon={<UserOutlined />}
                  className="flex-shrink-0"
                />
                <Upload
                  name="avatar"
                  showUploadList={false}
                  accept="image/*"
                  customRequest={handleAvatarUpload}
                  beforeUpload={(file) => {
                    const isImage = file.type.startsWith('image/');
                    if (!isImage) {
                      message.error('只能上传图片文件');
                      return false;
                    }
                    const isLt2M = file.size / 1024 / 1024 < 2;
                    if (!isLt2M) {
                      message.error('图片大小不能超过 2MB');
                      return false;
                    }
                    return true;
                  }}
                >
                  <Button
                    type="text"
                    icon={<CameraOutlined />}
                    className="absolute bottom-0 right-0 rounded-full bg-white shadow-md"
                    size="small"
                  />
                </Upload>
              </div>
              <div className="flex-1">
                <Title level={3} className="mb-1">
                  {user.nickname || user.username}
                </Title>
                <Text type="secondary" className="block mb-2">
                  {user.email}
                </Text>
                <Space>
                  <Tag color={getRoleColor(user.role)}>
                    {getRoleText(user.role)}
                  </Tag>
                  {user.is_verified ? (
                    <Tag color="green">已验证</Tag>
                  ) : (
                    <Tag color="orange">未验证</Tag>
                  )}
                  {user.is_active ? (
                    <Tag color="green">活跃</Tag>
                  ) : (
                    <Tag color="red">已禁用</Tag>
                  )}
                </Space>
              </div>
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => setIsEditing(true)}
                disabled={isEditing}
              >
                编辑资料
              </Button>
            </div>

            {user.bio && (
              <>
                <Divider />
                <div>
                  <Text strong>个人简介</Text>
                  <Text className="block mt-2" type="secondary">
                    {user.bio}
                  </Text>
                </div>
              </>
            )}
          </Card>

          {/* 编辑表单 */}
          {isEditing && (
            <Card title="编辑个人资料" className="shadow-sm">
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
                name="profile"
                onFinish={handleUpdateProfile}
                layout="vertical"
                size="large"
              >
                <Form.Item label="用户名">
                  <Input
                    value={user.username}
                    disabled
                    prefix={<UserOutlined />}
                  />
                  <Text type="secondary" className="text-xs">
                    用户名不可修改
                  </Text>
                </Form.Item>

                <Form.Item label="邮箱地址">
                  <Input
                    value={user.email}
                    disabled
                    prefix={<UserOutlined />}
                  />
                  <Text type="secondary" className="text-xs">
                    邮箱地址不可修改
                  </Text>
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
                    placeholder="请输入昵称"
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
                    placeholder="简单介绍一下自己"
                    rows={4}
                    showCount
                    maxLength={500}
                  />
                </Form.Item>

                <Form.Item>
                  <Space>
                    <Button
                      type="primary"
                      htmlType="submit"
                      loading={isLoading}
                      icon={<SaveOutlined />}
                    >
                      {isLoading ? '保存中...' : '保存更改'}
                    </Button>
                    <Button onClick={handleCancel}>
                      取消
                    </Button>
                  </Space>
                </Form.Item>
              </Form>
            </Card>
          )}

          {/* 账户信息 */}
          <Card title="账户信息" className="shadow-sm">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <Text strong>注册时间</Text>
                  <Text className="block" type="secondary">
                    {new Date(user.created_at).toLocaleString('zh-CN')}
                  </Text>
                </div>
              </div>

              {user.last_login && (
                <div className="flex justify-between items-center">
                  <div>
                    <Text strong>最后登录</Text>
                    <Text className="block" type="secondary">
                      {new Date(user.last_login).toLocaleString('zh-CN')}
                    </Text>
                  </div>
                </div>
              )}

              <Divider />

              <div className="space-y-2">
                <Button 
                  type="default" 
                  block 
                  icon={<MailOutlined />}
                  onClick={() => setIsEmailChangeModalVisible(true)}
                >
                  修改邮箱
                </Button>
                <Button 
                  type="default" 
                  block 
                  icon={<LockOutlined />}
                  onClick={() => setIsPasswordModalVisible(true)}
                >
                  修改密码
                </Button>
                <Button 
                  type="default" 
                  block 
                  icon={<DownloadOutlined />}
                  onClick={() => setIsExportModalVisible(true)}
                >
                  导出个人数据
                </Button>
                <Button type="default" danger block>
                  注销账户
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* 修改密码模态框 */}
        <Modal
          title="修改密码"
          open={isPasswordModalVisible}
          onCancel={() => {
            setIsPasswordModalVisible(false);
            passwordForm.resetFields();
          }}
          footer={null}
          destroyOnClose
        >
          <Form
            form={passwordForm}
            name="changePassword"
            onFinish={handlePasswordChange}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="current_password"
              label="当前密码"
              rules={[
                { required: true, message: '请输入当前密码' },
              ]}
            >
              <Password
                prefix={<LockOutlined />}
                placeholder="请输入当前密码"
              />
            </Form.Item>

            <Form.Item
              name="new_password"
              label="新密码"
              rules={[
                { required: true, message: '请输入新密码' },
                { min: 8, message: '密码至少8个字符' },
              ]}
            >
              <Password
                prefix={<LockOutlined />}
                placeholder="请输入新密码"
              />
            </Form.Item>

            <Form.Item
              name="confirm_password"
              label="确认新密码"
              rules={[
                { required: true, message: '请确认新密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('new_password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'));
                  },
                }),
              ]}
            >
              <Password
                prefix={<LockOutlined />}
                placeholder="请再次输入新密码"
              />
            </Form.Item>

            <Form.Item>
              <Space className="w-full justify-end">
                <Button onClick={() => {
                  setIsPasswordModalVisible(false);
                  passwordForm.resetFields();
                }}>
                  取消
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isChangingPassword}
                >
                  {isChangingPassword ? '修改中...' : '确认修改'}
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>

        {/* 修改邮箱模态框 */}
        <Modal
          title="修改邮箱"
          open={isEmailChangeModalVisible}
          onCancel={() => {
            setIsEmailChangeModalVisible(false);
            emailChangeForm.resetFields();
          }}
          footer={null}
          destroyOnClose
        >
          <div className="mb-4">
            <Alert
              message="安全提醒"
              description="修改邮箱后，您需要使用新邮箱地址登录。验证邮件将发送到新邮箱，请确保新邮箱地址正确且可以正常接收邮件。"
              type="warning"
              showIcon
            />
          </div>
          
          <Form
            form={emailChangeForm}
            name="changeEmail"
            onFinish={handleEmailChange}
            layout="vertical"
            size="large"
          >
            <Form.Item label="当前邮箱">
              <Input
                value={user?.email}
                disabled
                prefix={<MailOutlined />}
              />
            </Form.Item>

            <Form.Item
              name="new_email"
              label="新邮箱地址"
              rules={[
                { required: true, message: '请输入新邮箱地址' },
                { type: 'email', message: '请输入有效的邮箱地址' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || value !== user?.email) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('新邮箱不能与当前邮箱相同'));
                  },
                }),
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="请输入新邮箱地址"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="当前密码"
              rules={[
                { required: true, message: '请输入当前密码以确认身份' },
              ]}
            >
              <Password
                prefix={<LockOutlined />}
                placeholder="请输入当前密码"
              />
            </Form.Item>

            <Form.Item>
              <Space className="w-full justify-end">
                <Button onClick={() => {
                  setIsEmailChangeModalVisible(false);
                  emailChangeForm.resetFields();
                }}>
                  取消
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isChangingEmail}
                >
                  {isChangingEmail ? '发送中...' : '发送验证邮件'}
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>

        {/* 数据导出模态框 */}
        <Modal
          title="导出个人数据"
          open={isExportModalVisible}
          onCancel={() => setIsExportModalVisible(false)}
          footer={null}
          destroyOnClose
        >
          <Form
            name="exportData"
            onFinish={handleDataExport}
            layout="vertical"
            size="large"
            initialValues={{
              format: 'json',
              include_articles: true,
              include_comments: true,
              include_profile: true,
            }}
          >
            <Form.Item
              name="format"
              label="导出格式"
              rules={[{ required: true, message: '请选择导出格式' }]}
            >
              <Select placeholder="请选择导出格式">
                <Option value="json">JSON 格式</Option>
                <Option value="csv">CSV 格式</Option>
              </Select>
            </Form.Item>

            <Form.Item label="包含内容">
              <Form.Item name="include_profile" valuePropName="checked" noStyle>
                <input type="checkbox" id="include_profile" className="mr-2" />
                <label htmlFor="include_profile">个人资料</label>
              </Form.Item>
              <br />
              <Form.Item name="include_articles" valuePropName="checked" noStyle>
                <input type="checkbox" id="include_articles" className="mr-2" />
                <label htmlFor="include_articles">我的文章</label>
              </Form.Item>
              <br />
              <Form.Item name="include_comments" valuePropName="checked" noStyle>
                <input type="checkbox" id="include_comments" className="mr-2" />
                <label htmlFor="include_comments">我的评论</label>
              </Form.Item>
            </Form.Item>

            <Form.Item>
              <Space className="w-full justify-end">
                <Button onClick={() => setIsExportModalVisible(false)}>
                  取消
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isExporting}
                  icon={<DownloadOutlined />}
                >
                  {isExporting ? '导出中...' : '开始导出'}
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </div>
  );
}