'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Menu } from 'antd';
import { BookOutlined, ToolOutlined, GlobalOutlined } from '@ant-design/icons';

interface NavigationMenuProps {
  mode?: 'horizontal' | 'vertical';
  className?: string;
  onItemClick?: () => void;
}

export default function NavigationMenu({ 
  mode = 'horizontal', 
  className = '',
  onItemClick 
}: NavigationMenuProps) {
  const pathname = usePathname();

  const menuItems = [
    {
      key: '/knowledge',
      icon: <BookOutlined />,
      label: <Link href="/knowledge">知识库</Link>,
    },
    {
      key: '/tools',
      icon: <ToolOutlined />,
      label: <Link href="/tools">工具库</Link>,
    },
    {
      key: '/news',
      icon: <GlobalOutlined />,
      label: <Link href="/news">行业资讯</Link>,
    },
  ];

  // 确定当前选中的菜单项
  const selectedKeys = menuItems
    .filter(item => pathname.startsWith(item.key))
    .map(item => item.key);

  return (
    <Menu
      mode={mode}
      selectedKeys={selectedKeys}
      items={menuItems}
      className={`border-none ${className}`}
      onClick={onItemClick}
      style={{ 
        backgroundColor: 'transparent',
        lineHeight: mode === 'horizontal' ? '64px' : 'normal'
      }}
    />
  );
}