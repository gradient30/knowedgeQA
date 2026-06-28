'use client';

import React, { useCallback, useState, useEffect } from 'react';
import { Card, Tabs, Table, Button, Space, Tag, message, Modal, Image } from 'antd';
import { DownloadOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import FileUpload from '@/components/common/FileUpload/FileUpload';

interface FileInfo {
  id: string;
  original_name: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  file_type: string;
  status: string;
  download_count: number;
  is_public: boolean;
  created_at: string;
  file_url: string;
  thumbnail_url?: string;
}

const authHeaders = (): HeadersInit => {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const FilesPage: React.FC = () => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewFile, setPreviewFile] = useState<FileInfo | null>(null);
  const [previewImageUrl, setPreviewImageUrl] = useState<string | null>(null);

  const fetchFiles = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/files/list', {
        headers: authHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      } else {
        message.error('获取文件列表失败');
      }
    } catch (error) {
      message.error('获取文件列表失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]);

  const handleDownload = async (file: FileInfo) => {
    try {
      const response = await fetch(file.file_url, {
        headers: authHeaders(),
      });

      if (!response.ok) {
        message.error('下载文件失败');
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.original_name;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      message.error('下载文件失败');
    }
  };

  const handlePreview = async (file: FileInfo) => {
    if (previewImageUrl) {
      URL.revokeObjectURL(previewImageUrl);
      setPreviewImageUrl(null);
    }

    setPreviewFile(file);
    setPreviewVisible(true);

    if (!isImageFile(file.mime_type)) {
      return;
    }

    try {
      const response = await fetch(file.thumbnail_url || file.file_url, {
        headers: authHeaders(),
      });

      if (!response.ok) {
        message.error('获取预览失败');
        return;
      }

      const blob = await response.blob();
      setPreviewImageUrl(URL.createObjectURL(blob));
    } catch (error) {
      message.error('获取预览失败');
    }
  };

  const closePreview = () => {
    if (previewImageUrl) {
      URL.revokeObjectURL(previewImageUrl);
      setPreviewImageUrl(null);
    }
    setPreviewVisible(false);
  };

  const handleDelete = async (fileId: string) => {
    try {
      const response = await fetch(`/api/v1/files/${fileId}`, {
        method: 'DELETE',
        headers: authHeaders(),
      });

      if (response.ok) {
        message.success('文件删除成功');
        fetchFiles(); // 重新获取文件列表
      } else {
        message.error('删除文件失败');
      }
    } catch (error) {
      message.error('删除文件失败');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileTypeColor = (fileType: string) => {
    const colors: { [key: string]: string } = {
      'image': 'green',
      'document': 'blue',
      'archive': 'orange',
      'other': 'default'
    };
    return colors[fileType] || 'default';
  };

  const isImageFile = (mimeType: string) => {
    return mimeType.startsWith('image/');
  };

  const columns = [
    {
      title: '文件名',
      dataIndex: 'original_name',
      key: 'original_name',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
      render: (fileType: string) => (
        <Tag color={getFileTypeColor(fileType)}>{fileType}</Tag>
      ),
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => formatFileSize(size),
    },
    {
      title: '状态',
      dataIndex: 'is_public',
      key: 'is_public',
      render: (isPublic: boolean) => (
        <Tag color={isPublic ? 'green' : 'orange'}>
          {isPublic ? '公开' : '私有'}
        </Tag>
      ),
    },
    {
      title: '下载次数',
      dataIndex: 'download_count',
      key: 'download_count',
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: unknown, file: FileInfo) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handlePreview(file)}
          />
          <Button
            type="text"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(file)}
          />
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(file.id)}
          />
        </Space>
      ),
    },
  ];

  const tabItems = [
    {
      key: 'upload',
      label: '上传文件',
      children: (
        <FileUpload
          maxCount={10}
          maxSize={50}
          onUploadSuccess={() => {
            message.success('文件上传成功');
            fetchFiles(); // 重新获取文件列表
          }}
          onUploadError={(error) => {
            message.error(`上传失败: ${error}`);
          }}
        />
      ),
    },
    {
      key: 'manage',
      label: '文件管理',
      children: (
        <Table
          columns={columns}
          dataSource={files}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个文件`,
          }}
        />
      ),
    },
  ];

  return (
    <div className="p-6">
      <Card title="文件中心" className="w-full">
        <Tabs items={tabItems} />
      </Card>

      {/* 文件预览模态框 */}
      <Modal
        title={previewFile?.original_name}
        open={previewVisible}
        onCancel={closePreview}
        footer={[
          <Button key="download" onClick={() => previewFile && handleDownload(previewFile)}>
            下载文件
          </Button>,
          <Button key="close" onClick={closePreview}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {previewFile && (
          <div className="text-center">
            {isImageFile(previewFile.mime_type) && previewImageUrl ? (
              <Image
                src={previewImageUrl}
                alt={previewFile.original_name}
                style={{ maxWidth: '100%', maxHeight: '500px' }}
              />
            ) : (
              <div className="p-8">
                <p className="text-gray-500 mb-4">无法预览此文件类型</p>
                <p><strong>文件名:</strong> {previewFile.original_name}</p>
                <p><strong>文件大小:</strong> {formatFileSize(previewFile.file_size)}</p>
                <p><strong>文件类型:</strong> {previewFile.mime_type}</p>
                <p><strong>上传时间:</strong> {new Date(previewFile.created_at).toLocaleString('zh-CN')}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default FilesPage;
