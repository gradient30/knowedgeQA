'use client';

import { Drawer, Divider } from 'antd';
import NavigationMenu from './NavigationMenu';
import UserActions from './UserActions';
import Logo from './Logo';

interface MobileMenuProps {
  open: boolean;
  onClose: () => void;
}

export default function MobileMenu({ open, onClose }: MobileMenuProps) {
  return (
    <Drawer
      title={<Logo />}
      placement="right"
      onClose={onClose}
      open={open}
      width={280}
      styles={{
        body: { padding: '16px 0' },
      }}
    >
      {/* 导航菜单 */}
      <div className="mb-4">
        <NavigationMenu 
          mode="vertical" 
          onItemClick={onClose}
          className="border-none"
        />
      </div>

      <Divider />

      {/* 用户操作区域 */}
      <div className="px-4">
        <UserActions />
      </div>
    </Drawer>
  );
}