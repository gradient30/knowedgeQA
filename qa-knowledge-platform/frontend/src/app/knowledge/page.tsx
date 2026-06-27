'use client';

import { useMemo, useState } from 'react';
import { Button, Card, Col, Row, Select, Space, Table, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { QaArticle, BusinessDomain } from '@/types/platform.types';

const { Title, Text } = Typography;

const articles: QaArticle[] = [
  {
    id: 'saas-incident-001',
    title: 'SaaS灰度发布复盘：权限缓存导致租户数据异常',
    summary: '覆盖灰度批次、SLA影响、回滚动作和测试漏检点。',
    content: 'incident review',
    type: '最佳实践',
    business_domain: 'saas',
    visibility: 'team',
    review_status: 'approved',
    project_key: 'crm-saas',
    tags: ['灰度', 'SLA', '回归'],
  },
  {
    id: 'game-release-120',
    title: '游戏版本质量报告：1.2.0 提审前兼容性结论',
    summary: '覆盖机型矩阵、帧率、弱网和阻塞缺陷。',
    content: 'release report',
    type: 'Bug案例',
    business_domain: 'game',
    visibility: 'team',
    review_status: 'pending',
    project_key: 'moba-1.2.0',
    tags: ['提审', '机型兼容', 'FPS'],
  },
];

const domainLabel: Record<BusinessDomain, string> = {
  saas: 'SaaS',
  game: '游戏',
  common: '通用',
};

export default function KnowledgePage() {
  const [businessDomain, setBusinessDomain] = useState<BusinessDomain | 'all'>('all');

  const data = useMemo(
    () =>
      businessDomain === 'all'
        ? articles
        : articles.filter((item) => item.business_domain === businessDomain),
    [businessDomain]
  );

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
            <Button type="primary">新建知识</Button>
          </Col>
        </Row>

        <Card>
          <Space>
            <Text strong>业务域</Text>
            <Select
              value={businessDomain}
              style={{ width: 180 }}
              onChange={setBusinessDomain}
              options={[
                { value: 'all', label: '全部' },
                { value: 'saas', label: 'SaaS' },
                { value: 'game', label: '游戏' },
              ]}
            />
          </Space>
        </Card>

        <Table rowKey="id" columns={columns} dataSource={data} pagination={false} />
      </Space>
    </main>
  );
}
