'use client';

import { useState } from 'react';
import { Layout, Button } from 'antd';
import { MenuOutlined } from '@ant-design/icons';
import Link from 'next/link';
import UserActions from './UserActions';

const { Header } = Layout;

interface GlobalHeaderProps {
  className?: string;
}

export default function GlobalHeader({ className = '' }: GlobalHeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <Header className={`bg-white border-b border-gray-200 px-4 lg:px-6 ${className}`}>
      <div className="flex items-center justify-between h-full max-w-7xl mx-auto">
        {/* Logo区域 */}
        <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
          <div className="flex items-center justify-center w-8 h-8 bg-blue-600 rounded-lg">
            <span className="text-white text-lg">📚</span>
          </div>
          <span className="text-lg font-semibold text-gray-800 hidden sm:inline">
            QA知识平台
          </span>
        </Link>

        {/* 桌面端导航菜单 */}
        <div className="hidden md:flex space-x-6">
          <Link href="/knowledge" className="text-gray-600 hover:text-blue-600 transition-colors">
            知识库
          </Link>
          <Link href="/tools" className="text-gray-600 hover:text-blue-600 transition-colors">
            工具库
          </Link>
          <Link href="/news" className="text-gray-600 hover:text-blue-600 transition-colors">
            行业资讯
          </Link>
        </div>

        {/* 用户操作区域 */}
        <div className="flex items-center space-x-4">
          {/* 桌面端用户操作 */}
          <div className="hidden md:block">
            <UserActions />
          </div>

          {/* 移动端菜单按钮 */}
          <Button
            type="text"
            icon={<MenuOutlined />}
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden"
            size="large"
          />
        </div>
      </div>
    </Header>
  );
}
