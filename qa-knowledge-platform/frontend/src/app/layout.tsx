import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AntdRegistry } from '@ant-design/nextjs-registry';
import SimpleNavbar from '@/components/layout/SimpleNavbar';
import AuthInitializer from '@/components/auth/AuthInitializer';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'QA测试知识协作平台',
  description: '专为测试团队打造的知识分享与协作平台',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <AntdRegistry>
          <AuthInitializer>
            <SimpleNavbar />
            {children}
          </AuthInitializer>
        </AntdRegistry>
      </body>
    </html>
  );
}