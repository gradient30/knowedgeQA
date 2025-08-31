'use client';

import Link from 'next/link';
import { Typography } from 'antd';
import { BookOutlined } from '@ant-design/icons';

const { Title } = Typography;

interface LogoProps {
  className?: string;
  collapsed?: boolean;
}

export default function Logo({ className = '', collapsed = false }: LogoProps) {
  return (
    <Link href="/" className={`flex items-center space-x-2 hover:opacity-80 transition-opacity ${className}`}>
      <div className="flex items-center justify-center w-8 h-8 bg-blue-600 rounded-lg">
        <BookOutlined className="text-white text-lg" />
      </div>
      {!collapsed && (
        <Title level={4} className="!mb-0 !text-gray-800 whitespace-nowrap">
          QA知识平台
        </Title>
      )}
    </Link>
  );
}