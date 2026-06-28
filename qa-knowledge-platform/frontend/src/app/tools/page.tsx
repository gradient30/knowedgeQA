'use client';

import { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Form, Input, Modal, Rate, Row, Segmented, Select, Space, Table, Tag, Typography, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { BusinessDomain, QaCategory, QaTool } from '@/types/platform.types';
import { createTool, listToolCategories, listTools } from '@/lib/api/tools';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface ToolFormValues {
  name: string;
  url: string;
  description: string;
  business_domain: BusinessDomain;
  project_key?: string;
  features?: string;
}

export default function ToolsPage() {
  const [form] = Form.useForm<ToolFormValues>();
  const [businessDomain, setBusinessDomain] = useState<BusinessDomain | 'all'>('all');
  const [data, setData] = useState<QaTool[]>([]);
  const [categories, setCategories] = useState<QaCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    setData([]);

    listTools({
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

  useEffect(() => {
    listToolCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  async function handleCreate(values: ToolFormValues) {
    const category = categories.find(
      (item) => item.business_domain === values.business_domain
    );
    if (!category) {
      message.error('当前业务域缺少工具分类');
      return;
    }

    setSubmitting(true);
    try {
      await createTool({
        category_id: category.id,
        name: values.name,
        url: values.url,
        description: values.description,
        business_domain: values.business_domain,
        project_key: values.project_key,
        features: values.features
          ? values.features.split(',').map((feature) => feature.trim()).filter(Boolean)
          : [],
      });
      const items = await listTools({
        business_domain: businessDomain === 'all' ? undefined : businessDomain,
      });
      setData(items);
      setModalOpen(false);
      form.resetFields();
      message.success('工具已添加');
    } catch (requestError) {
      message.error(requestError instanceof Error ? requestError.message : '添加失败');
    } finally {
      setSubmitting(false);
    }
  }

  const columns: ColumnsType<QaTool> = [
    {
      title: '工具',
      dataIndex: 'name',
      render: (_, record) => (
        <Space direction="vertical" size={2}>
          <Text strong>{record.name}</Text>
          <Text type="secondary">{record.description}</Text>
        </Space>
      ),
    },
    {
      title: '业务域',
      dataIndex: 'business_domain',
      width: 100,
      render: (value: BusinessDomain) => <Tag color={value === 'game' ? 'purple' : 'blue'}>{value === 'game' ? '游戏' : 'SaaS'}</Tag>,
    },
    { title: '项目', dataIndex: 'project_key', width: 120 },
    {
      title: '评分',
      dataIndex: 'avg_rating',
      width: 150,
      render: (value: number) => <Rate disabled allowHalf value={value} />,
    },
    { title: '使用次数', dataIndex: 'usage_count', width: 100 },
    {
      title: '特性',
      dataIndex: 'features',
      render: (features: string[]) => features.map((feature) => <Tag key={feature}>{feature}</Tag>),
    },
  ];

  return (
    <main className="p-6">
      <Space direction="vertical" size="large" className="w-full">
        <Row align="middle" justify="space-between" gutter={[16, 16]}>
          <Col>
            <Title level={2}>测试工具库</Title>
            <Text type="secondary">运营 SaaS 与游戏 QA 团队推荐工具、评分和使用经验。</Text>
          </Col>
          <Col>
            <Button type="primary" onClick={() => setModalOpen(true)}>
              添加工具
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

        {error ? <Alert type="error" message="工具库数据加载失败" description={error} showIcon /> : null}

        <Table rowKey="id" columns={columns} dataSource={data} loading={loading} pagination={false} />
      </Space>

      <Modal
        title="添加工具"
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
          initialValues={{ business_domain: 'saas', url: 'https://example.com/qa-tool' }}
          onFinish={handleCreate}
        >
          <Form.Item name="business_domain" label="业务域" rules={[{ required: true }]}>
            <Select
              options={[
                { value: 'saas', label: 'SaaS' },
                { value: 'game', label: '游戏' },
              ]}
            />
          </Form.Item>
          <Form.Item name="name" label="工具名称" rules={[{ required: true }]}>
            <Input placeholder="例如：弱网回归巡检工具" />
          </Form.Item>
          <Form.Item name="url" label="工具链接" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="project_key" label="项目">
            <Input placeholder="例如：crm-saas / moba" />
          </Form.Item>
          <Form.Item name="features" label="特性">
            <Input placeholder="用英文逗号分隔，例如：API回归,性能,FPS" />
          </Form.Item>
          <Form.Item name="description" label="说明" rules={[{ required: true }]}>
            <TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </main>
  );
}
