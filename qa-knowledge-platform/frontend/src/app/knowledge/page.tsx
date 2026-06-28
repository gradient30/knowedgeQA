'use client';

import { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Form, Input, Modal, Row, Segmented, Select, Space, Table, Tag, Typography, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { QaArticle, BusinessDomain, QaCategory } from '@/types/platform.types';
import { createArticle, listArticles, listKnowledgeCategories } from '@/lib/api/knowledge';

const { Title, Text } = Typography;
const { TextArea } = Input;
const ACCEPTANCE_USER_ID = '00000000-0000-0000-0000-000000000001';

interface KnowledgeFormValues {
  title: string;
  summary?: string;
  content: string;
  business_domain: BusinessDomain;
  project_key?: string;
  tags?: string;
  attachment_file_ids?: string;
}

const domainLabel: Record<BusinessDomain, string> = {
  saas: 'SaaS',
  game: '游戏',
  common: '通用',
};

export default function KnowledgePage() {
  const [form] = Form.useForm<KnowledgeFormValues>();
  const [businessDomain, setBusinessDomain] = useState<BusinessDomain | 'all'>('all');
  const [data, setData] = useState<QaArticle[]>([]);
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

    listArticles({
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
    listKnowledgeCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  async function handleCreate(values: KnowledgeFormValues) {
    const category = categories.find(
      (item) => item.business_domain === values.business_domain
    );
    if (!category) {
      message.error('当前业务域缺少知识分类');
      return;
    }

    setSubmitting(true);
    try {
      await createArticle({
        category_id: category.id,
        user_id: ACCEPTANCE_USER_ID,
        title: values.title,
        summary: values.summary,
        content: values.content,
        type: '最佳实践',
        business_domain: values.business_domain,
        visibility: 'team',
        project_key: values.project_key,
        tags: values.tags ? values.tags.split(',').map((tag) => tag.trim()).filter(Boolean) : [],
        attachment_file_ids: values.attachment_file_ids
          ? values.attachment_file_ids.split(',').map((fileId) => fileId.trim()).filter(Boolean)
          : [],
      });
      const items = await listArticles({
        business_domain: businessDomain === 'all' ? undefined : businessDomain,
      });
      setData(items);
      setModalOpen(false);
      form.resetFields();
      message.success('知识已创建，等待审核');
    } catch (requestError) {
      message.error(requestError instanceof Error ? requestError.message : '创建失败');
    } finally {
      setSubmitting(false);
    }
  }

  const columns: ColumnsType<QaArticle> = [
    {
      title: '标题',
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
      render: (value: BusinessDomain) => <Tag color={value === 'game' ? 'purple' : 'blue'}>{domainLabel[value]}</Tag>,
    },
    { title: '项目', dataIndex: 'project_key', width: 130 },
    { title: '类型', dataIndex: 'type', width: 110 },
    {
      title: '状态',
      dataIndex: 'review_status',
      width: 110,
      render: (value) => <Tag color={value === 'approved' ? 'green' : 'gold'}>{value}</Tag>,
    },
    {
      title: '标签',
      dataIndex: 'tags',
      render: (tags: string[]) => tags.map((tag) => <Tag key={tag}>{tag}</Tag>),
    },
    {
      title: '附件',
      dataIndex: 'attachment_file_ids',
      width: 90,
      render: (fileIds: string[]) => <Tag color={fileIds.length > 0 ? 'green' : 'default'}>{fileIds.length}</Tag>,
    },
  ];

  return (
    <main className="p-6">
      <Space direction="vertical" size="large" className="w-full">
        <Row align="middle" justify="space-between" gutter={[16, 16]}>
          <Col>
            <Title level={2}>QA知识库</Title>
            <Text type="secondary">沉淀 SaaS 与游戏测试经验、事故复盘和版本质量报告。</Text>
          </Col>
          <Col>
            <Button type="primary" onClick={() => setModalOpen(true)}>
              新建知识
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

        {error ? <Alert type="error" message="知识库数据加载失败" description={error} showIcon /> : null}

        <Table rowKey="id" columns={columns} dataSource={data} loading={loading} pagination={false} />
      </Space>

      <Modal
        title="新建知识"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        okText="提交审核"
        cancelText="取消"
        destroyOnHidden
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ business_domain: 'saas', content: '验收背景：\n测试结论：\n风险与后续：' }}
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
          <Form.Item name="title" label="标题" rules={[{ required: true }]}>
            <Input placeholder="例如：SaaS API 兼容性验收复盘" />
          </Form.Item>
          <Form.Item name="summary" label="摘要">
            <Input />
          </Form.Item>
          <Form.Item name="project_key" label="项目">
            <Input placeholder="例如：crm-saas / game-1.2.0" />
          </Form.Item>
          <Form.Item name="tags" label="标签">
            <Input placeholder="用英文逗号分隔，例如：回归,SLA,弱网" />
          </Form.Item>
          <Form.Item name="attachment_file_ids" label="附件文件 ID">
            <Input placeholder="上传证据文件后填入 ID，多个用英文逗号分隔" />
          </Form.Item>
          <Form.Item name="content" label="内容" rules={[{ required: true }]}>
            <TextArea rows={6} />
          </Form.Item>
        </Form>
      </Modal>
    </main>
  );
}
