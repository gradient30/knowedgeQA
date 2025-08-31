'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button, Dropdown, Avatar, Space, Typography } from 'antd';
import { UserOutlined, LogoutOutlined, ExportOutlined, TeamOutlined, SettingOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/lib/store/auth';

const { Text } = Typography;

interface UserActionsProps {
  className?: string;
}

export default function UserActions({ className = '' }: UserActionsProps) {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  // 未登录状态
  if (!isAuthenticated) {
    return (
      <Space className={className}>
        <Link href="/login">
          <Button type="default" size="middle">
            登录
          </Button>
        </Link>
        <Link href="/register">
          <Button type="primary" size="middle">
            注册
          </Button>
        </Link>
      </Space>
    );
  }

  // 处理菜单点击
  const handleMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'profile':
        router.push('/profile');
        break;
      case 'teams':
        router.push('/teams');
        break;
      case 'export':
        router.push('/export');
        break;
      case 'admin':
        router.push('/admin/notifications');
        break;
      case 'logout':
        handleLogout();
        break;
    }
  };

  // 已登录状态 - 用户下拉菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'teams',
      icon: <TeamOutlined />,
      label: '团队管理',
    },
    {
      key: 'export',
      icon: <ExportOutlined />,
      label: '数据导出',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'admin',
      icon: <SettingOutlined />,
      label: '系统管理',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
    },
  ];

  return (
    <div className={className}>
      <Dropdown
        menu={{ 
          items: userMenuItems,
          onClick: handleMenuClick
        }}
        placement="bottomRight"
        trigger={['click']}
      >
        <Button type="text" style={{ display: 'flex', alignItems: 'center', gap: '8px', height: 'auto', padding: '8px' }}>
          <Avatar 
            size="small" 
            icon={<UserOutlined />}
            src={user?.avatar_url}
          />
          <Text style={{ maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {user?.nickname || user?.username || '用户'}
          </Text>
        </Button>
      </Dropdown>
    </div>
  );
}