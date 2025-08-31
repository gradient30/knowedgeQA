# 后端开发问题

## SQLAlchemy metadata属性冲突 {#sqlalchemy-metadata-issue}

**问题描述**: FastAPI启动时报错，提示SQLAlchemy中`metadata`属性名冲突

**错误信息**:
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

**解决方案**:
将模型中的`metadata`字段重命名为其他名称：

```python
# 修改前
class Article(Base):
    metadata = Column(JSON)

# 修改后  
class Article(Base):
    extra_data = Column(JSON)  # 重命名避免与SQLAlchemy metadata冲突
```

**根本原因**: SQLAlchemy的DeclarativeBase类保留了`metadata`属性名，用于存储表元数据信息

**预防措施**: 
- 避免使用SQLAlchemy保留的属性名
- 参考SQLAlchemy文档了解保留字段
- 使用更具描述性的字段名

**相关链接**: [SQLAlchemy文档 - 保留属性](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html)

---

## 数据库连接失败 - 主机名解析错误

**问题描述**: 后端服务无法连接到PostgreSQL数据库

**错误信息**:
```
socket.gaierror: [Errno -5] No address associated with hostname
```

**解决方案**:
1. 确保数据库服务已启动
2. 检查Docker网络配置
3. 验证环境变量中的数据库连接字符串

**根本原因**: Docker容器间网络通信配置问题或服务启动顺序问题

**预防措施**: 
- 使用Docker Compose的depends_on确保启动顺序
- 添加健康检查确保服务就绪
- 使用服务名而不是localhost进行容器间通信