# 文件上传系统文档

## 概述

QA测试知识协作平台的文件上传系统提供了完整的文件管理功能，支持图片、文档、压缩包等多种文件类型的上传、存储、处理和下载。

## 功能特性

### 1. 文件类型支持

#### 图片类型
- **支持格式**: JPG, JPEG, PNG, GIF, BMP, WebP, SVG, TIFF
- **自动处理**: 
  - 大尺寸图片自动压缩（最大1920x1080）
  - 自动生成缩略图（300x300）
  - EXIF信息处理和自动旋转
  - 透明背景处理（RGBA转RGB）

#### 文档类型
- **支持格式**: PDF, DOC, DOCX, TXT, RTF, ODT, XLS, XLSX, PPT, PPTX, MD
- **特性**: 保持原始格式，支持预览和下载

#### 压缩文件
- **支持格式**: ZIP, RAR, 7Z, TAR, GZ
- **特性**: 完整性验证，支持批量文件管理

### 2. 安全特性

#### 文件验证
- **大小限制**: 默认10MB，可配置
- **类型检查**: 扩展名和MIME类型双重验证
- **安全扫描**: 防止恶意文件上传
- **权限控制**: 基于用户权限的访问控制

#### 存储安全
- **文件重命名**: 使用UUID避免文件名冲突
- **路径隔离**: 按类型分目录存储
- **访问控制**: 支持私有/团队/公开三级权限

### 3. 性能优化

#### 图片处理
- **智能压缩**: 基于原始尺寸自动调整压缩策略
- **格式转换**: 自动选择最优格式
- **缩略图生成**: 异步生成，提升响应速度
- **渐进式JPEG**: 支持渐进式加载

#### 存储优化
- **分层存储**: 按文件类型分目录存储
- **缓存策略**: 热点文件缓存
- **CDN支持**: 预留云存储和CDN接口

## API接口

### 1. 文件上传

#### 单文件上传
```http
POST /api/v1/files/upload
Content-Type: multipart/form-data

Parameters:
- file: 上传的文件
- is_public: 是否公开（可选，默认false）

Response:
{
  "success": true,
  "message": "文件上传成功",
  "file_info": {
    "id": "uuid",
    "filename": "stored_filename.jpg",
    "original_filename": "original.jpg",
    "file_size": 1024000,
    "file_type": "image/jpeg",
    "file_extension": ".jpg",
    "file_url": "/api/v1/files/download/uuid",
    "thumbnail_url": "/api/v1/files/download/uuid_thumb",
    "upload_time": "2025-08-30T16:00:00Z"
  }
}
```

#### 批量文件上传
```http
POST /api/v1/files/upload-multiple
Content-Type: multipart/form-data

Parameters:
- files: 多个文件
- is_public: 是否公开（可选，默认false）

Response:
[
  {
    "success": true,
    "message": "文件上传成功",
    "file_info": { ... }
  },
  ...
]
```

### 2. 文件下载

```http
GET /api/v1/files/download/{file_id}

Response:
- 文件内容（二进制流）
- 自动设置正确的Content-Type
- 支持缩略图下载（file_id_thumb）
```

### 3. 文件信息

#### 获取文件详情
```http
GET /api/v1/files/info/{file_id}

Response:
{
  "id": "uuid",
  "original_name": "original.jpg",
  "file_name": "stored_filename.jpg",
  "file_size": 1024000,
  "mime_type": "image/jpeg",
  "file_type": "image",
  "status": "ready",
  "download_count": 5,
  "is_public": false,
  "metadata": {
    "original_width": 2000,
    "original_height": 1500,
    "final_width": 1920,
    "final_height": 1440,
    "compressed": true,
    "thumbnail_width": 300,
    "thumbnail_height": 225
  },
  "created_at": "2025-08-30T16:00:00Z",
  "updated_at": "2025-08-30T16:00:00Z",
  "file_url": "/api/v1/files/download/uuid",
  "thumbnail_url": "/api/v1/files/download/uuid_thumb"
}
```

#### 获取用户文件列表
```http
GET /api/v1/files/list?file_type=image&page=1&size=20

Response:
{
  "files": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

### 4. 文件删除

```http
DELETE /api/v1/files/{file_id}

Response:
{
  "message": "文件删除成功"
}
```

## 数据库设计

### uploaded_files 表结构

```sql
CREATE TABLE uploaded_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_type filetype NOT NULL,
    status filestatus NOT NULL DEFAULT 'uploading',
    thumbnail_path TEXT,
    file_metadata JSONB,
    download_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_uploaded_files_user_id ON uploaded_files(user_id);
CREATE INDEX idx_uploaded_files_file_type ON uploaded_files(file_type);
CREATE INDEX idx_uploaded_files_status ON uploaded_files(status);
CREATE INDEX idx_uploaded_files_created_at ON uploaded_files(created_at);
```

### 枚举类型

```sql
-- 文件类型
CREATE TYPE filetype AS ENUM ('image', 'document', 'archive', 'other');

-- 文件状态
CREATE TYPE filestatus AS ENUM ('uploading', 'processing', 'ready', 'error');
```

## 配置说明

### 环境变量配置

```env
# 文件上传配置
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=.jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.zip

# 云存储配置（可选）
USE_CLOUD_STORAGE=false
CLOUD_STORAGE_TYPE=local  # local, aws_s3, aliyun_oss

# AWS S3配置
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket
AWS_S3_REGION=us-east-1

# 阿里云OSS配置
ALIYUN_OSS_ACCESS_KEY_ID=your_access_key
ALIYUN_OSS_ACCESS_KEY_SECRET=your_secret_key
ALIYUN_OSS_BUCKET=your_bucket
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
```

### 目录结构

```
uploads/
├── images/          # 图片文件
├── documents/       # 文档文件
├── archives/        # 压缩文件
├── thumbnails/      # 缩略图
└── temp/           # 临时文件
```

## 使用示例

### 前端上传示例

```javascript
// 单文件上传
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('is_public', 'false');
  
  const response = await fetch('/api/v1/files/upload', {
    method: 'POST',
    body: formData,
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};

// 批量上传
const uploadMultipleFiles = async (files) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });
  
  const response = await fetch('/api/v1/files/upload-multiple', {
    method: 'POST',
    body: formData,
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

### 图片预览组件

```jsx
const ImagePreview = ({ fileId, alt }) => {
  const [imageUrl, setImageUrl] = useState('');
  const [thumbnailUrl, setThumbnailUrl] = useState('');
  
  useEffect(() => {
    setImageUrl(`/api/v1/files/download/${fileId}`);
    setThumbnailUrl(`/api/v1/files/download/${fileId}_thumb`);
  }, [fileId]);
  
  return (
    <div className="image-preview">
      <img 
        src={thumbnailUrl} 
        alt={alt}
        onClick={() => window.open(imageUrl, '_blank')}
        style={{ cursor: 'pointer', maxWidth: '300px' }}
      />
    </div>
  );
};
```

## 错误处理

### 常见错误码

- `400`: 文件验证失败（大小超限、类型不支持等）
- `401`: 未授权访问
- `403`: 权限不足
- `404`: 文件不存在
- `413`: 文件过大
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

## 性能监控

### 关键指标

- **上传成功率**: 成功上传文件数 / 总上传请求数
- **平均上传时间**: 文件上传完成的平均耗时
- **存储使用量**: 总文件大小和数量
- **下载频次**: 文件下载次数统计
- **错误率**: 各类错误的发生频率

### 监控建议

1. **实时监控**: 上传失败率、响应时间
2. **容量监控**: 存储空间使用情况
3. **性能分析**: 大文件上传性能优化
4. **安全审计**: 恶意文件上传尝试

## 扩展计划

### V2.0 功能规划

1. **云存储集成**: AWS S3、阿里云OSS、腾讯云COS
2. **CDN加速**: 文件分发网络支持
3. **图片处理**: 更多格式转换和滤镜效果
4. **视频支持**: 视频文件上传和转码
5. **文件版本**: 文件版本管理和历史记录
6. **批量操作**: 文件批量下载和管理
7. **API限流**: 上传频率限制和配额管理
8. **文件分享**: 临时分享链接和权限控制

### 技术优化

1. **异步处理**: 大文件异步上传和处理
2. **断点续传**: 大文件断点续传支持
3. **压缩优化**: 更智能的压缩算法
4. **缓存策略**: 多级缓存提升性能
5. **负载均衡**: 文件服务负载均衡