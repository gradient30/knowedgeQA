'use client';

import { useMemo, useState } from 'react';
import { Button, Card, Col, Row, Select, Space, Table, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { BusinessDomain, QaNewsItem } from '@/types/platform.types';

const { Title, Text } = Typography;

const newsItems: QaNewsItem[] = [
  {
    id: 'news-dora-ai',
    source_id: 'source-dora',
    title: 'DORA 研究：AI 放大工程体系能力',
    url: 'https://dora.dev/research/',
    summary: '适合 SaaS 团队用于交付效能和质量治理复盘。',
    business_domain: 'saas',
    tags: ['DevOps', '质量工程'],
    relevance_score: 91,
    review_status: 'approved',
  },
  {
    id: 'news-game-agent',
    source_id: 'source-game-ai',
    title: 'LLM Agent 在 MMORPG 自动化测试中的应用',
    url: 'https://arxiv.org/abs/2509.22170',
    summary: '适合游戏 QA 团队评估自动化探索和测试资产归档。',
    business_domain: 'game',
    tags: ['AI测试', '游戏自动化'],
    relevance_score: 94,
    review_status: 'pending',
  },
];

export default function NewsPage() {
  const [businessDomain, setBusinessDomain] = useState<BusinessDomain | 'all'>('all');
  const data = useMemo(
    () =>
      businessDomain === 'all'
        ? newsItems
        : newsItems.filter((item) => item.business_domain === businessDomain),
    [businessDomain]
  );

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
            <Button type="primary">配置资讯源</Button>
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
