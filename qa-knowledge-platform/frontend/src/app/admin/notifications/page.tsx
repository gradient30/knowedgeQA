'use client';

import React, { useCallback, useState, useEffect } from 'react';
import {
  Card,
  Tabs,
  Form,
  Switch,
  Button,
  Input,
  Table,
  Tag,
  Space,
  Modal,
  message,
  Alert,
  Descriptions,
  Select
} from 'antd';
import {
  MailOutlined,
  SettingOutlined,
  SendOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { apiUrl } from '@/lib/api/client';

const { Option } = Select;

interface EmailLog {
  id: string;
  to_email: string;
  subject: string;
  template_name: string;
  status: 'success' | 'failed' | 'pending';
  sent_at: string;
  error_message?: string;
}

interface EmailTemplate {
  id: string;
  name: string;
  description: string;
  variables: string[];
}

interface EmailSettings {
  email_verification: boolean;
  password_reset: boolean;
  welcome_email: boolean;
  article_comments: boolean;
  team_invitations: boolean;
  system_updates: boolean;
}

interface EmailSettingsResponse {
  notifications: EmailSettings;
}

interface SmtpStatus {
  status: 'healthy' | 'not_configured' | 'error';
  message: string;
  details: {
    smtp_host?: string;
    smtp_port?: number | string;
    smtp_user?: string;
    smtp_tls?: boolean;
    last_check?: string;
  };
}

interface TestEmailValues {
  to_email: string;
}

interface PreviewTemplateValues {
  template_name: string;
}

interface PreviewTemplateResponse {
  html_content: string;
}

const NotificationsPage: React.FC = () => {
  const [emailLogs, setEmailLogs] = useState<EmailLog[]>([]);
  const [emailTemplates, setEmailTemplates] = useState<EmailTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [testEmailVisible, setTestEmailVisible] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewContent, setPreviewContent] = useState('');
  const [smtpStatus, setSmtpStatus] = useState<SmtpStatus | null>(null);
  
  const [testEmailForm] = Form.useForm();
  const [settingsForm] = Form.useForm();
  const [previewForm] = Form.useForm();

  // 获取邮件设置
  const fetchEmailSettings = useCallback(async () => {
    try {
      const response = await fetch(apiUrl('/notifications/email-settings'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = (await response.json()) as EmailSettingsResponse;
        settingsForm.setFieldsValue(data.notifications);
      }
    } catch (error) {
      message.error('获取邮件设置失败');
    }
  }, [settingsForm]);

  // 获取邮件日志
  const fetchEmailLogs = useCallback(async () => {
    try {
      const response = await fetch(apiUrl('/notifications/email-logs'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = (await response.json()) as { logs: EmailLog[] };
        setEmailLogs(data.logs);
      }
    } catch (error) {
      message.error('获取邮件日志失败');
    }
  }, []);

  // 获取邮件模板
  const fetchEmailTemplates = useCallback(async () => {
    try {
      const response = await fetch(apiUrl('/notifications/email-templates'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = (await response.json()) as { templates: EmailTemplate[] };
        setEmailTemplates(data.templates);
      }
    } catch (error) {
      message.error('获取邮件模板失败');
    }
  }, []);

  // 获取SMTP状态
  const fetchSmtpStatus = useCallback(async () => {
    try {
      const response = await fetch(apiUrl('/notifications/smtp-status'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = (await response.json()) as SmtpStatus;
        setSmtpStatus(data);
      }
    } catch (error) {
      message.error('获取SMTP状态失败');
    }
  }, []);

  useEffect(() => {
    fetchEmailSettings();
    fetchEmailLogs();
    fetchEmailTemplates();
    fetchSmtpStatus();
  }, [fetchEmailLogs, fetchEmailSettings, fetchEmailTemplates, fetchSmtpStatus]);

  // 更新邮件设置
  const handleUpdateSettings = async (values: EmailSettings) => {
    try {
      setLoading(true);
      const response = await fetch(apiUrl('/notifications/email-settings'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ notifications: values })
      });
      
      if (response.ok) {
        message.success('邮件设置已更新');
        fetchEmailSettings();
      } else {
        message.error('更新邮件设置失败');
      }
    } catch (error) {
      message.error('更新邮件设置失败');
    } finally {
      setLoading(false);
    }
  };

  // 发送测试邮件
  const handleSendTestEmail = async (values: TestEmailValues) => {
    try {
      setLoading(true);
      const response = await fetch(apiUrl('/notifications/test-email'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(values)
      });
      
      if (response.ok) {
        message.success('测试邮件发送成功');
        setTestEmailVisible(false);
        testEmailForm.resetFields();
        fetchEmailLogs();
      } else {
        const error = await response.json();
        message.error(error.detail || '测试邮件发送失败');
      }
    } catch (error) {
      message.error('测试邮件发送失败');
    } finally {
      setLoading(false);
    }
  };

  // 预览邮件模板
  const handlePreviewTemplate = async (values: PreviewTemplateValues) => {
    try {
      setLoading(true);
      const response = await fetch(apiUrl('/notifications/preview-template'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(values)
      });
      
      if (response.ok) {
        const data = (await response.json()) as PreviewTemplateResponse;
        setPreviewContent(data.html_content);
        setPreviewVisible(true);
      } else {
        message.error('生成模板预览失败');
      }
    } catch (error) {
      message.error('生成模板预览失败');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'pending':
        return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const emailLogColumns = [
    {
      title: '收件人',
      dataIndex: 'to_email',
      key: 'to_email',
    },
    {
      title: '主题',
      dataIndex: 'subject',
      key: 'subject',
      ellipsis: true,
    },
    {
      title: '模板',
      dataIndex: 'template_name',
      key: 'template_name',
      render: (template: string) => {
        const templateInfo = emailTemplates.find(t => t.id === template);
        return templateInfo ? templateInfo.name : template;
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
          {status === 'success' ? '成功' : status === 'failed' ? '失败' : '发送中'}
        </Tag>
      ),
    },
    {
      title: '发送时间',
      dataIndex: 'sent_at',
      key: 'sent_at',
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '错误信息',
      dataIndex: 'error_message',
      key: 'error_message',
      render: (error: string) => error || '-',
    },
  ];

  const tabItems = [
    {
      key: 'settings',
      label: (
        <span>
          <SettingOutlined />
          邮件设置
        </span>
      ),
      children: (
        <div>
          {/* SMTP状态 */}
          {smtpStatus && (
            <Alert
              message="SMTP服务状态"
              description={
                <Descriptions size="small" column={2}>
                  <Descriptions.Item label="状态">
                    <Tag color={smtpStatus.status === 'healthy' ? 'success' : 'error'}>
                      {smtpStatus.message}
                    </Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="SMTP主机">
                    {smtpStatus.details.smtp_host || '未设置'}
                  </Descriptions.Item>
                  <Descriptions.Item label="端口">
                    {smtpStatus.details.smtp_port || '未设置'}
                  </Descriptions.Item>
                  <Descriptions.Item label="用户名">
                    {smtpStatus.details.smtp_user || '未设置'}
                  </Descriptions.Item>
                </Descriptions>
              }
              type={smtpStatus.status === 'healthy' ? 'success' : 'warning'}
              showIcon
              className="mb-4"
            />
          )}

          {/* 通知设置 */}
          <Card title="通知设置" size="small">
            <Form
              form={settingsForm}
              layout="vertical"
              onFinish={handleUpdateSettings}
            >
              <Form.Item
                name="email_verification"
                label="邮箱验证通知"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
              
              <Form.Item
                name="password_reset"
                label="密码重置通知"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
              
              <Form.Item
                name="welcome_email"
                label="欢迎邮件"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
              
              <Form.Item
                name="article_comments"
                label="文章评论通知"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
              
              <Form.Item
                name="team_invitations"
                label="团队邀请通知"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
              
              <Form.Item
                name="system_updates"
                label="系统更新通知"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
              
              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit" loading={loading}>
                    保存设置
                  </Button>
                  <Button onClick={() => setTestEmailVisible(true)}>
                    发送测试邮件
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </div>
      ),
    },
    {
      key: 'templates',
      label: (
        <span>
          <MailOutlined />
          邮件模板
        </span>
      ),
      children: (
        <div>
          <Card title="模板预览" size="small" className="mb-4">
            <Form
              form={previewForm}
              layout="inline"
              onFinish={handlePreviewTemplate}
            >
              <Form.Item name="template_name" label="选择模板" rules={[{ required: true }]}>
                <Select placeholder="选择邮件模板" style={{ width: 200 }}>
                  {emailTemplates.map(template => (
                    <Option key={template.id} value={template.id}>
                      {template.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
              
              <Form.Item>
                <Button type="primary" htmlType="submit" icon={<EyeOutlined />} loading={loading}>
                  预览模板
                </Button>
              </Form.Item>
            </Form>
          </Card>

          <Card title="可用模板" size="small">
            <div className="space-y-4">
              {emailTemplates.map(template => (
                <div key={template.id} className="border rounded p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-medium">{template.name}</h4>
                      <p className="text-gray-600 text-sm">{template.description}</p>
                      <div className="mt-2">
                        <span className="text-xs text-gray-500">可用变量: </span>
                        {template.variables.map(variable => (
                          <Tag key={variable}>{variable}</Tag>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      ),
    },
    {
      key: 'logs',
      label: (
        <span>
          <SendOutlined />
          发送日志
        </span>
      ),
      children: (
        <Card title="邮件发送日志" size="small">
          <Table
            columns={emailLogColumns}
            dataSource={emailLogs}
            rowKey="id"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
          />
        </Card>
      ),
    },
  ];

  return (
    <div className="p-6">
      <Card title="邮件通知管理" className="w-full">
        <Tabs items={tabItems} />
      </Card>

      {/* 测试邮件模态框 */}
      <Modal
        title="发送测试邮件"
        open={testEmailVisible}
        onCancel={() => setTestEmailVisible(false)}
        footer={null}
      >
        <Form
          form={testEmailForm}
          layout="vertical"
          onFinish={handleSendTestEmail}
        >
          <Form.Item
            name="to_email"
            label="收件人邮箱"
            rules={[
              { required: true, message: '请输入收件人邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="请输入收件人邮箱" />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                发送测试邮件
              </Button>
              <Button onClick={() => setTestEmailVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 模板预览模态框 */}
      <Modal
        title="邮件模板预览"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        <div 
          dangerouslySetInnerHTML={{ __html: previewContent }}
          style={{ maxHeight: '500px', overflow: 'auto' }}
        />
      </Modal>
    </div>
  );
};

export default NotificationsPage;
