from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    MEMBER = "member"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class ProfessionalRole(str, enum.Enum):
    TEST_ENGINEER = "test_engineer"
    SENIOR_TEST_ENGINEER = "senior_test_engineer"
    TEST_LEAD = "test_lead"
    TEST_MANAGER = "test_manager"
    QA_ENGINEER = "qa_engineer"
    AUTOMATION_ENGINEER = "automation_engineer"
    PERFORMANCE_ENGINEER = "performance_engineer"
    SECURITY_TESTER = "security_tester"
    GAME_TESTER = "game_tester"
    MOBILE_TESTER = "mobile_tester"
    TEST_ARCHITECT = "test_architect"
    QA_DIRECTOR = "qa_director"
    DEVELOPER = "developer"
    PRODUCT_MANAGER = "product_manager"
    STUDENT = "student"
    OTHER = "other"


class ExperienceLevel(str, enum.Enum):
    BEGINNER = "0-1"  # 0-1年（新手）
    JUNIOR = "1-3"  # 1-3年（初级）
    INTERMEDIATE = "3-5"  # 3-5年（中级）
    SENIOR = "5-8"  # 5-8年（高级）
    EXPERT = "8+"  # 8年以上（专家）


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100))
    avatar_url = Column(Text)
    bio = Column(Text)
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    professional_role = Column(
        Enum(ProfessionalRole), default=ProfessionalRole.TEST_ENGINEER
    )
    experience_level = Column(Enum(ExperienceLevel), default=ExperienceLevel.JUNIOR)
    specialties = Column(JSON)  # 存储专业领域数组
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    skills = Column(JSON)  # 保留原有技能字段
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    team = relationship("Team", foreign_keys=[team_id], back_populates="members")
    # Article关系 - 使用字符串引用避免循环导入
    articles = relationship("Article", back_populates="author")


class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(128), unique=True, nullable=False, index=True)
    token_type = Column(String(50), nullable=False, index=True)
    extra_data = Column(JSON)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    leader_id = Column(UUID(as_uuid=True), ForeignKey("users.id", use_alter=True))
    settings = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    members = relationship("User", foreign_keys="User.team_id", back_populates="team")
    leader = relationship("User", foreign_keys=[leader_id])
