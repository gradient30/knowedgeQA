import { Typography } from 'antd';
const { Title } = Typography;

export default function KnowledgePage() {
  return (
    <div className="qa-container py-8">
      <Title level={1}>知识库</Title>
      <p className="text-gray-600">知识库功能开发中...</p>
    </div>
  );
}