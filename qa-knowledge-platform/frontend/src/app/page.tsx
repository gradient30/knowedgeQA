'use client';

import { Button, Typography, Card, Row, Col } from 'antd';
import { BookOutlined, ToolOutlined, GlobalOutlined } from '@ant-design/icons';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';

const { Title, Paragraph } = Typography;

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      // 已登录用户跳转到知识库
      router.push('/knowledge');
    } else {
      // 未登录用户跳转到登录页
      router.push('/login');
    }
  };

  const handleLearnMore = () => {
    alert('了解更多功能：知识库管理、测试工具库、行业资讯');
  };

  return (
    <div>
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <Title level={1}>QA测试知识协作平台</Title>
          <Paragraph className="text-lg max-w-2xl mx-auto">
            专为测试团队打造的知识分享与协作平台，提供测试经验分享、工具管理和行业资讯追踪
          </Paragraph>
          <div className="space-x-4">
            <Button type="primary" size="large" onClick={handleGetStarted}>
              开始使用
            </Button>
            <Button size="large" onClick={handleLearnMore}>
              了解更多
            </Button>
          </div>
        </div>

        <Row gutter={[24, 24]} className="mt-12">
          <Col xs={24} md={8}>
            <Card 
              hoverable
              className="text-center h-full"
              cover={<div className="p-8"><BookOutlined style={{ fontSize: '48px', color: '#1890ff' }} /></div>}
            >
              <Card.Meta
                title="知识库管理"
                description="测试经验分享、最佳实践沉淀、团队知识传承"
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card 
              hoverable
              className="text-center h-full"
              cover={<div className="p-8"><ToolOutlined style={{ fontSize: '48px', color: '#52c41a' }} /></div>}
            >
              <Card.Meta
                title="测试工具库"
                description="工具推荐、使用评价、分类管理、收藏功能"
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card 
              hoverable
              className="text-center h-full"
              cover={<div className="p-8"><GlobalOutlined style={{ fontSize: '48px', color: '#fa8c16' }} /></div>}
            >
              <Card.Meta
                title="行业资讯"
                description="自动抓取行业动态、技术趋势、最新资讯"
              />
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
}