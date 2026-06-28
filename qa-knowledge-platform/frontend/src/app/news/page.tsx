'use client';

import { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Form, Input, InputNumber, Modal, Row, Segmented, Select, Space, Table, Tag, Typography, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { BusinessDomain, QaNewsItem } from '@/types/platform.types';
import { createNewsSource, listNewsItems } from '@/lib/api/news';

const { Title, Text } = Typography;

interface NewsSourceFormValues {
  name: string;
  url: string;
  category: string;
  business_domain: BusinessDomain;
  keywords?: string;
  frequency_hours: number;
}

export default function NewsPage() {
  const [form] = Form.useForm<NewsSourceFormValues>();
  const [businessDomain, setBusinessDomain] = useState<BusinessDomain | 'all'>('all');
  const [data, setData] = useState<QaNewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    setData([]);

    listNewsItems({
      business_domain: businessDomain === 'all' ? undefined : businessDomain,
    })
      .then((items) => {
        if (active) {
          setData(items);
        }
      })
      .catch((requestError: Error) => {
        if (active) {
          setData([]);
          setError(requestError.message);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [businessDomain]);

  async function handleCreateSource(values: NewsSourceFormValues) {
    setSubmitting(true);
    try {
      await createNewsSource({
        name: values.name,
        url: values.url,
        category: values.category,
        business_domain: values.business_domain,
        keywords: values.keywords
          ? values.keywords.split(',').map((keyword) => keyword.trim()).filter(Boolean)
          : [],
        frequency_hours: values.frequency_hours,
        is_active: true,
      });
      setModalOpen(false);
      form.resetFields();
      message.success('资讯源已创建');
    } catch (requestError) {
      message.error(requestError instanceof Error ? requestError.message : '创建失败');
    } finally {
      setSubmitting(false);
    }
  }

  const columns: ColumnsType<QaNewsItem> = [
    {
      title: '资讯',
      dataIndex: 'title',
      render: (_, record) => (
        <Space direction="vertical" size={2}>
          <Text strong>{record.title}</Text>
          <Text type="secondary">{record.summary}</Text>
        </Space>
      ),
    },
    {
      title: '业务域',
      dataIndex: 'business_domain',
      width: 100,
      render: (value: BusinessDomain) => <Tag color={value === 'game' ? 'purple' : 'blue'}>{value === 'game' ? '游戏' : 'SaaS'}</Tag>,
    },
    { title: '相关性', dataIndex: 'relevance_score', width: 100 },
    {
      title: '审核',
      dataIndex: 'review_status',
      width: 110,
      render: (value) => <Tag color={value === 'approved' ? 'green' : 'gold'}>{value}</Tag>,
    },
    {
      title: '标签',
      dataIndex: 'tags',
      render: (tags: string[]) => tags.map((tag) => <Tag key={tag}>{tag}</Tag>),
    },
  ];

  return (
    <main className="p-6">
      <Space direction="vertical" size="large" className="w-full">
        <Row align="middle" justify="space-between" gutter={[16, 16]}>
          <Col>
            <Title level={2}>质量情报中心</Title>
            <Text type="secondary">筛选 SaaS 与游戏 QA 趋势、资讯源和待审核内容。</Text>
          </Col>
          <Col>
            <Button type="primary" onClick={() => setModalOpen(true)}>
              配置资讯源
            </Button>
          </Col>
        </Row>

        <Card>
          <Space>
            <Text strong>业务域</Text>
            <Segmented
              value={businessDomain}
              onChange={(value) => setBusinessDomain(value as BusinessDomain | 'all')}
              options={[
                { value: 'all', label: '全部' },
                { value: 'saas', label: 'SaaS' },
                { value: 'game', label: '游戏' },
              ]}
            />
          </Space>
        </Card>

        {error ? <Alert type="error" message="资讯数据加载失败" description={error} showIcon /> : null}

        <Table rowKey="id" columns={columns} dataSource={data} loading={loading} pagination={false} />
      </Space>

      <Modal
        title="配置资讯源"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        okText="保存"
        cancelText="取消"
        destroyOnHidden
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            business_domain: 'saas',
            category: 'SaaS质量',
            frequency_hours: 24,
          }}
          onFinish={handleCreateSource}
        >
          <Form.Item name="business_domain" label="业务域" rules={[{ required: true }]}>
            <Select
              options={[
                { value: 'saas', label: 'SaaS' },
                { value: 'game', label: '游戏' },
              ]}
            />
          </Form.Item>
          <Form.Item name="category" label="分类" rules={[{ required: true }]}>
            <Select
              options={[
                { value: 'SaaS质量', label: 'SaaS质量' },
                { value: '游戏测试', label: '游戏测试' },
                { value: 'AI测试', label: 'AI测试' },
                { value: '行业动态', label: '行业动态' },
              ]}
            />
          </Form.Item>
          <Form.Item name="name" label="资讯源名称" rules={[{ required: true }]}>
            <Input placeholder="例如：SaaS 质量工程周报" />
          </Form.Item>
          <Form.Item name="url" label="源地址" rules={[{ required: true }]}>
            <Input placeholder="https://example.com/qa-news" />
          </Form.Item>
          <Form.Item name="keywords" label="关键词">
            <Input placeholder="用英文逗号分隔，例如：SLA,灰度,弱网" />
          </Form.Item>
          <Form.Item name="frequency_hours" label="抓取频率（小时）" rules={[{ required: true }]}>
            <InputNumber min={1} className="w-full" />
          </Form.Item>
        </Form>
      </Modal>
    </main>
  );
}
