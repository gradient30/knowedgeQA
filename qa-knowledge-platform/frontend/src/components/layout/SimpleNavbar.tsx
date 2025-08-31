'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import UserActions from './UserActions';

export default function SimpleNavbar() {
  const pathname = usePathname();

  // 首页不显示导航栏（因为首页有自己的导航）
  if (pathname === '/') {
    return null;
  }

  return (
    <div style={{ 
      padding: '12px 24px', 
      borderBottom: '1px solid #f0f0f0', 
      background: '#fff',
      position: 'sticky',
      top: 0,
      zIndex: 1000
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        maxWidth: '1200px', 
        margin: '0 auto' 
      }}>
        {/* Logo区域 */}
        <Link href="/" style={{ textDecoration: 'none' }}>
          <div style={{ 
            fontSize: '18px', 
            fontWeight: 'bold', 
            color: '#1890ff',
            cursor: 'pointer'
          }}>
            QA知识平台
          </div>
        </Link>

        {/* 主导航菜单 */}
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <Link 
            href="/knowledge" 
            style={{ 
              textDecoration: 'none', 
              color: pathname === '/knowledge' ? '#1890ff' : '#666',
              fontWeight: pathname === '/knowledge' ? 'bold' : 'normal'
            }}
          >
            知识库
          </Link>
          <Link 
            href="/tools" 
            style={{ 
              textDecoration: 'none', 
              color: pathname === '/tools' ? '#1890ff' : '#666',
              fontWeight: pathname === '/tools' ? 'bold' : 'normal'
            }}
          >
            工具库
          </Link>
          <Link 
            href="/files" 
            style={{ 
              textDecoration: 'none', 
              color: pathname === '/files' ? '#1890ff' : '#666',
              fontWeight: pathname === '/files' ? 'bold' : 'normal'
            }}
          >
            文件中心
          </Link>
          <Link 
            href="/news" 
            style={{ 
              textDecoration: 'none', 
              color: pathname === '/news' ? '#1890ff' : '#666',
              fontWeight: pathname === '/news' ? 'bold' : 'normal'
            }}
          >
            资讯
          </Link>
        </div>

        {/* 用户操作区域 */}
        <div>
          <UserActions />
        </div>
      </div>
    </div>
  );
}