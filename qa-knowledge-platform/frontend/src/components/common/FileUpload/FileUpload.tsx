'use client';

import React, { useState } from 'react';
import { Upload, Button, message, Progress, Card, List, Typography } from 'antd';
import { UploadOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { apiUrl } from '@/lib/api/client';

const { Text } = Typography;

interface FileUploadProps {
  maxCount?: number;
  accept?: string;
  maxSize?: number; // MB
  onUploadSuccess?: (files: UploadedFile[]) => void;
  onUploadError?: (error: string) => void;
  showPreview?: boolean;
  isPublic?: boolean;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  thumbnailUrl?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  maxCount = 5,
  accept = '*',
  maxSize = 10,
  onUploadSuccess,
  onUploadError,
  showPreview = true,
  isPublic = false
}) => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});

  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('is_public', isPublic.toString());

    try {
      setUploading(true);
      setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));

      const response = await fetch(apiUrl('/files/upload'), {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('上传失败');
      }

      const result = await response.json();
      
      if (result.success && result.file_info) {
        const originalName =
          result.file_info.original_name ||
          result.file_info.original_filename ||
          result.file_info.filename;
        const mimeType = result.file_info.mime_type || result.file_info.file_type;
        const newFile: UploadedFile = {
          id: result.file_info.id,
          name: originalName,
          size: result.file_info.file_size,
          type: mimeType,
          url: result.file_info.file_url,
          thumbnailUrl: result.file_info.thumbnail_url
        };
        
        setUploadedFiles(prev => [...prev, newFile]);
        message.success(`${file.name} 上传成功`);
        
        if (onUploadSuccess) {
          onUploadSuccess([...uploadedFiles, newFile]);
        }
      } else {
        throw new Error(result.message || '上传失败');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '上传失败';
      message.error(`${file.name} ${errorMsg}`);
      
      if (onUploadError) {
        onUploadError(errorMsg);
      }
    } finally {
      setUploading(false);
      setUploadProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[file.name];
        return newProgress;
      });
    }
  };

  const handleRemove = async (fileId: string) => {
    try {
      const response = await fetch(apiUrl(`/files/${fileId}`), {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
        message.success('文件删除成功');
      } else {
        throw new Error('删除失败');
      }
    } catch (error) {
      message.error('删除文件失败');
    }
  };

  const handlePreview = (file: UploadedFile) => {
    // 在新窗口打开文件
    window.open(apiUrl(file.url), '_blank');
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: maxCount > 1,
    fileList,
    accept,
    beforeUpload: (file) => {
      // 检查文件大小
      const isLtMaxSize = file.size / 1024 / 1024 < maxSize;
      if (!isLtMaxSize) {
        message.error(`文件大小不能超过 ${maxSize}MB`);
        return false;
      }

      // 检查文件数量
      if (fileList.length >= maxCount) {
        message.error(`最多只能上传 ${maxCount} 个文件`);
        return false;
      }

      // 立即上传
      handleUpload(file);
      return false; // 阻止默认上传行为
    },
    onChange: (info) => {
      setFileList(info.fileList);
    },
    onRemove: (file) => {
      setFileList(prev => prev.filter(f => f.uid !== file.uid));
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="file-upload-container">
      <Card title="文件上传" size="small">
        <Upload.Dragger {...uploadProps} disabled={uploading}>
          <p className="ant-upload-drag-icon">
            <UploadOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单个或批量上传，最大 {maxSize}MB，最多 {maxCount} 个文件
          </p>
        </Upload.Dragger>

        {/* 上传进度 */}
        {Object.keys(uploadProgress).length > 0 && (
          <div className="mt-4">
            {Object.entries(uploadProgress).map(([fileName, progress]) => (
              <div key={fileName} className="mb-2">
                <Text className="text-sm">{fileName}</Text>
                <Progress percent={progress} size="small" />
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* 已上传文件列表 */}
      {showPreview && uploadedFiles.length > 0 && (
        <Card title="已上传文件" size="small" className="mt-4">
          <List
            dataSource={uploadedFiles}
            renderItem={(file) => (
              <List.Item
                actions={[
                  <Button
                    key="preview"
                    type="text"
                    icon={<EyeOutlined />}
                    onClick={() => handlePreview(file)}
                  />,
                  <Button
                    key="delete"
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleRemove(file.id)}
                  />
                ]}
              >
                <List.Item.Meta
                  title={file.name}
                  description={`${formatFileSize(file.size)} • ${file.type}`}
                />
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  );
};

export default FileUpload;
