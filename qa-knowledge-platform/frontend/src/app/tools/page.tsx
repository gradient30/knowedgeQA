'use client';

import { useMemo, useState } from 'react';
import { Button, Card, Col, Rate, Row, Select, Space, Table, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { BusinessDomain, QaTool } from '@/types/platform.types';

const { Title, Text } = Typography;

const tools: QaTool[] = [
  {
    id: 'tool-api-contract',
    category_id: 'cat-saas-api',
    name: 'SaaS接口契约测试工具',
    url: 'https://example.com/api-contract',
    description: '用于接口兼容性、调用方影响和灰度前回归验证。',
    business_domain: 'saas',
    project_key: 'crm-saas',
    features: ['契约测试', 'API回归', '破坏性变更'],
    avg_rating: 4.4,
    rating_count: 12,
    usage_count: 46,
    is_recommended: true,
  },
  {
    id: 'tool-game-fps',
    category_id: 'cat-game-perf',
    name: '游戏帧率巡检工具',
    url: 'https://example.com/game-fps',
    description: '用于团战、弱网和长时间挂机场景的 FPS 与内存巡检。',
    business_domain: 'game',
    project_key: 'moba',
    features: ['FPS', '内存', '弱网'],
    avg_rating: 4.7,
    rating_count: 18,
    usage_count: 88,
    is_recommended: true,
  },
];

export default function ToolsPage() {
  const [businessDomain, setBusinessDomain] = useState<BusinessDomain | 'all'>('all');
  const data = useMemo(
    () =>
      businessDomain === 'all'
        ? tools
        : tools.filter((item) => item.business_domain === businessDomain),
    [businessDomain]
  );

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
            <Button type="primary">添加工具</Button>
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
