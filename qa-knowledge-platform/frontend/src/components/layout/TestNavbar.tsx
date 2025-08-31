'use client';

export default function TestNavbar() {
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
        <div style={{ 
          fontSize: '18px', 
          fontWeight: 'bold', 
          color: '#1890ff'
        }}>
          QA知识平台 - 测试导航栏
        </div>
        <div style={{ color: '#666' }}>
          测试用户菜单
        </div>
      </div>
    </div>
  );
}