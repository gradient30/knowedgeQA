'use client';

import { useState } from 'react';
import { Card, Form, Button, Typography, Select, Checkbox, Alert, Space, Divider, Tag } from 'antd';
import { DownloadOutlined, FileTextOutlined, DatabaseOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/lib/store/auth';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface ExportOption {
  key: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  size?: string;
}

interface ExportFormValues {
  format: 'json' | 'csv';
  include_profile: boolean;
  include_articles: boolean;
  include_comments: boolean;
}

export default function DataExportPage() {
  const { user } = useAuthStore();
  const [form] = Form.useForm();
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState<string | null>(null);

  const exportOptions: ExportOption[] = [
    {
      key: 'include_profile',
      label: '个人资料',
      description: '包含用户名、邮箱、个人简介、技能信息等基本资料',
      icon: <DatabaseOutlined className="text-blue-500" />,
      size: '< 1KB'
    },
    {
      key: 'include_articles',
      label: '我的文章',
      description: '包含您发布的所有文章内容、标题、分类、标签等信息',
      icon: <FileTextOutlined className="text-green-500" />,
      size: '预估大小根据文章数量而定'
    },
    {
      key: 'include_comments',
      label: '我的评论',
      description: '包含您在平台上发表的所有评论内容和时间',
      icon: <FileTextOutlined className="text-orange-500" />,
      size: '预估大小根据评论数量而定'
    }
  ];

  const handleExport = async (values: ExportFormValues) => {
    setIsExporting(true);
    setExportProgress('正在准备导出数据...');

    try {
      const token = localStorage.getItem('access_token');
      
      setExportProgress('正在生成导出文件...');
      
      const response = await fetch('/api/v1/users/profile/export-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        setExportProgress('正在下载文件...');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `user_data_${user?.username}_${new Date().toISOString().split('T')[0]}.${values.format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        setExportProgress('导出完成！');
        
        setTimeout(() => {
          setExportProgress(null);
        }, 2000);
      } else {
        const error = await response.json();
        throw new Error(error.detail || '导出失败');
      }
    } catch (error) {
      console.error('Export error:', error);
      setExportProgress(null);
      // 这里可以显示错误消息
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <Title level={2}>数据导出</Title>
          <Text type="secondary">
            导出您在平台上的个人数据，包括个人资料、文章、评论等信息
          </Text>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 导出表单 */}
          <div className="lg:col-span-2">
            <Card title="选择导出内容" className="shadow-sm">
              <Form
                form={form}
                name="exportData"
                onFinish={handleExport}
                layout="vertical"
                size="large"
                initialValues={{
                  format: 'json',
                  include_profile: true,
                  include_articles: true,
                  include_comments: true,
                }}
              >
                <Form.Item
                  name="format"
                  label="导出格式"
                  rules={[{ required: true, message: '请选择导出格式' }]}
                >
                  <Select placeholder="请选择导出格式">
                    <Option value="json">
                      <Space>
                        <FileTextOutlined />
                        JSON 格式
                        <Text type="secondary" className="text-xs">
                          (结构化数据，适合程序处理)
                        </Text>
                      </Space>
                    </Option>
                    <Option value="csv">
                      <Space>
                        <DatabaseOutlined />
                        CSV 格式
                        <Text type="secondary" className="text-xs">
                          (表格数据，适合Excel打开)
                        </Text>
                      </Space>
                    </Option>
                  </Select>
                </Form.Item>

                <Form.Item label="包含内容">
                  <div className="space-y-4">
                    {exportOptions.map((option) => (
                      <Form.Item
                        key={option.key}
                        name={option.key}
                        valuePropName="checked"
                        noStyle
                      >
                        <div className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                          <Checkbox className="w-full">
                            <div className="flex items-start space-x-3">
                              <div className="flex-shrink-0 mt-1">
                                {option.icon}
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center justify-between">
                                  <Text strong>{option.label}</Text>
                                  {option.size && (
                                    <Tag color="blue" className="text-xs">
                                      {option.size}
                                    </Tag>
                                  )}
                                </div>
                                <Text type="secondary" className="text-sm block mt-1">
                                  {option.description}
                                </Text>
                              </div>
                            </div>
                          </Checkbox>
                        </div>
                      </Form.Item>
                    ))}
                  </div>
                </Form.Item>

                {exportProgress && (
                  <Alert
                    message={exportProgress}
                    type="info"
                    showIcon
                    className="mb-4"
                  />
                )}

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={isExporting}
                    icon={<DownloadOutlined />}
                    size="large"
                    block
                  >
                    {isExporting ? '导出中...' : '开始导出'}
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </div>

          {/* 侧边栏信息 */}
          <div className="space-y-6">
            {/* 用户信息 */}
            <Card title="导出信息" className="shadow-sm">
              <div className="space-y-3">
                <div>
                  <Text type="secondary" className="text-sm">用户名</Text>
                  <Text className="block">{user?.username}</Text>
                </div>
                <div>
                  <Text type="secondary" className="text-sm">邮箱</Text>
                  <Text className="block">{user?.email}</Text>
                </div>
                <div>
                  <Text type="secondary" className="text-sm">注册时间</Text>
                  <Text className="block">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString('zh-CN') : '-'}
                  </Text>
                </div>
              </div>
            </Card>

            {/* 导出说明 */}
            <Card title="导出说明" className="shadow-sm">
              <div className="space-y-4">
                <div>
                  <Text strong className="flex items-center">
                    <InfoCircleOutlined className="mr-2 text-blue-500" />
                    数据格式
                  </Text>
                  <Paragraph className="text-sm text-gray-600 mt-2 mb-0">
                    JSON格式包含完整的结构化数据，CSV格式主要包含文章列表数据。
                  </Paragraph>
                </div>

                <Divider className="my-3" />

                <div>
                  <Text strong className="flex items-center">
                    <InfoCircleOutlined className="mr-2 text-green-500" />
                    数据安全
                  </Text>
                  <Paragraph className="text-sm text-gray-600 mt-2 mb-0">
                    导出的数据仅包含您的个人信息，不包含密码等敏感信息。
                  </Paragraph>
                </div>

                <Divider className="my-3" />

                <div>
                  <Text strong className="flex items-center">
                    <InfoCircleOutlined className="mr-2 text-orange-500" />
                    使用建议
                  </Text>
                  <Paragraph className="text-sm text-gray-600 mt-2 mb-0">
                    建议定期导出数据作为备份，导出的文件请妥善保管。
                  </Paragraph>
                </div>
              </div>
            </Card>

            {/* 最近导出记录 */}
            <Card title="导出历史" className="shadow-sm">
              <Text type="secondary" className="text-sm">
                暂无导出记录
              </Text>
              {/* TODO: 在后续版本中实现导出历史记录 */}
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
