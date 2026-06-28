'use client';

import { useCallback, useState, useEffect } from 'react';
import { Card, Button, Typography, Space, Avatar, Tag, List, Modal, Form, Input, Select, message } from 'antd';
import { TeamOutlined, UserAddOutlined, UserOutlined, CrownOutlined, EditOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/lib/store/auth';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface TeamMember {
  id: string;
  username: string;
  nickname?: string;
  email: string;
  role: 'member' | 'admin' | 'super_admin';
  avatar_url?: string;
  joined_at: string;
  is_leader: boolean;
}

interface Team {
  id: string;
  name: string;
  description?: string;
  leader_id?: string;
  member_count: number;
  leader?: TeamMember;
  members: TeamMember[];
  created_at: string;
}

export default function TeamsPage() {
  const { user } = useAuthStore();
  const [team, setTeam] = useState<Team | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalVisible, setIsCreateModalVisible] = useState(false);
  const [isInviteModalVisible, setIsInviteModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [createForm] = Form.useForm();
  const [inviteForm] = Form.useForm();
  const [editForm] = Form.useForm();

  const loadTeamInfo = useCallback(async () => {
    if (!user?.team_id) {
      setIsLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/users/profile/team', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const teamData = await response.json();
        setTeam(teamData);
      } else {
        console.error('Failed to load team info');
      }
    } catch (error) {
      console.error('Error loading team info:', error);
    } finally {
      setIsLoading(false);
    }
  }, [user?.team_id]);

  useEffect(() => {
    loadTeamInfo();
  }, [loadTeamInfo]);

  const handleCreateTeam = async (values: { name: string; description?: string }) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/users/teams', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        const newTeam = await response.json();
        setTeam(newTeam);
        setIsCreateModalVisible(false);
        createForm.resetFields();
        message.success('团队创建成功');
        // 刷新用户信息以更新team_id
        window.location.reload();
      } else {
        const error = await response.json();
        message.error(error.detail || '团队创建失败');
      }
    } catch (error) {
      message.error('团队创建失败');
    }
  };

  const handleInviteMember = async (values: { email: string; role: string; message?: string }) => {
    if (!team) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/users/teams/${team.id}/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        setIsInviteModalVisible(false);
        inviteForm.resetFields();
        message.success('邀请发送成功');
        loadTeamInfo(); // 重新加载团队信息
      } else {
        const error = await response.json();
        message.error(error.detail || '邀请发送失败');
      }
    } catch (error) {
      message.error('邀请发送失败');
    }
  };

  const handleUpdateTeam = async (values: { name: string; description?: string }) => {
    if (!team) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/users/teams/${team.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        const updatedTeam = await response.json();
        setTeam(updatedTeam);
        setIsEditModalVisible(false);
        editForm.resetFields();
        message.success('团队信息更新成功');
      } else {
        const error = await response.json();
        message.error(error.detail || '更新失败');
      }
    } catch (error) {
      message.error('更新失败');
    }
  };

  const handleLeaveTeam = async () => {
    Modal.confirm({
      title: '确认离开团队',
      content: '您确定要离开当前团队吗？此操作不可撤销。',
      okText: '确认离开',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          const token = localStorage.getItem('access_token');
          const response = await fetch('/api/v1/users/teams/leave', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (response.ok) {
            setTeam(null);
            message.success('已成功离开团队');
            // 刷新用户信息
            window.location.reload();
          } else {
            const error = await response.json();
            message.error(error.detail || '离开团队失败');
          }
        } catch (error) {
          message.error('离开团队失败');
        }
      },
    });
  };

  const getRoleText = (role: string) => {
    const roleMap = {
      member: '成员',
      admin: '管理员',
      super_admin: '超级管理员',
    };
    return roleMap[role as keyof typeof roleMap] || role;
  };

  const getRoleColor = (role: string) => {
    const colorMap = {
      member: 'blue',
      admin: 'orange',
      super_admin: 'red',
    };
    return colorMap[role as keyof typeof colorMap] || 'default';
  };

  const isTeamLeader = team && user && team.leader_id === user.id;
  const canManageTeam = isTeamLeader || (user && ['admin', 'super_admin'].includes(user.role));

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Text>加载中...</Text>
      </div>
    );
  }

  if (!team) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <TeamOutlined className="text-6xl text-gray-400 mb-4" />
            <Title level={2}>您还没有加入任何团队</Title>
            <Text type="secondary" className="block mb-8">
              创建一个新团队或等待其他人邀请您加入团队
            </Text>
            <Button
              type="primary"
              size="large"
              icon={<TeamOutlined />}
              onClick={() => setIsCreateModalVisible(true)}
            >
              创建团队
            </Button>
          </div>
        </div>

        {/* 创建团队模态框 */}
        <Modal
          title="创建团队"
          open={isCreateModalVisible}
          onCancel={() => {
            setIsCreateModalVisible(false);
            createForm.resetFields();
          }}
          footer={null}
          destroyOnClose
        >
          <Form
            form={createForm}
            name="createTeam"
            onFinish={handleCreateTeam}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="name"
              label="团队名称"
              rules={[
                { required: true, message: '请输入团队名称' },
                { max: 100, message: '团队名称不能超过100个字符' },
              ]}
            >
              <Input placeholder="请输入团队名称" />
            </Form.Item>

            <Form.Item
              name="description"
              label="团队描述"
              rules={[
                { max: 500, message: '团队描述不能超过500个字符' },
              ]}
            >
              <TextArea
                placeholder="简单描述一下团队"
                rows={3}
                showCount
                maxLength={500}
              />
            </Form.Item>

            <Form.Item>
              <Space className="w-full justify-end">
                <Button onClick={() => {
                  setIsCreateModalVisible(false);
                  createForm.resetFields();
                }}>
                  取消
                </Button>
                <Button type="primary" htmlType="submit">
                  创建团队
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <Title level={2}>团队管理</Title>
          <Text type="secondary">管理您的团队信息和成员</Text>
        </div>

        <div className="space-y-6">
          {/* 团队信息卡片 */}
          <Card className="shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-4">
                <Avatar size={64} icon={<TeamOutlined />} className="bg-blue-500" />
                <div>
                  <Title level={3} className="mb-1">
                    {team.name}
                  </Title>
                  <Text type="secondary" className="block mb-2">
                    {team.description || '暂无团队描述'}
                  </Text>
                  <Space>
                    <Tag color="blue">{team.member_count} 名成员</Tag>
                    <Tag color="green">
                      创建于 {new Date(team.created_at).toLocaleDateString('zh-CN')}
                    </Tag>
                  </Space>
                </div>
              </div>
              {canManageTeam && (
                <Space>
                  <Button
                    icon={<EditOutlined />}
                    onClick={() => {
                      editForm.setFieldsValue({
                        name: team.name,
                        description: team.description,
                      });
                      setIsEditModalVisible(true);
                    }}
                  >
                    编辑
                  </Button>
                  <Button
                    type="primary"
                    icon={<UserAddOutlined />}
                    onClick={() => setIsInviteModalVisible(true)}
                  >
                    邀请成员
                  </Button>
                </Space>
              )}
            </div>
          </Card>

          {/* 团队成员列表 */}
          <Card title="团队成员" className="shadow-sm">
            <List
              dataSource={team.members}
              renderItem={(member) => (
                <List.Item
                  actions={[
                    <Tag key="role" color={getRoleColor(member.role)}>
                      {getRoleText(member.role)}
                    </Tag>,
                    member.is_leader && (
                      <Tag key="leader" color="gold" icon={<CrownOutlined />}>
                        负责人
                      </Tag>
                    ),
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar
                        src={member.avatar_url}
                        icon={<UserOutlined />}
                      />
                    }
                    title={
                      <Space>
                        <span>{member.nickname || member.username}</span>
                        {member.is_leader && <CrownOutlined className="text-yellow-500" />}
                      </Space>
                    }
                    description={
                      <div>
                        <Text type="secondary">{member.email}</Text>
                        <br />
                        <Text type="secondary" className="text-xs">
                          加入时间: {new Date(member.joined_at).toLocaleDateString('zh-CN')}
                        </Text>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>

          {/* 操作按钮 */}
          <Card className="shadow-sm">
            <div className="space-y-4">
              <Title level={4}>团队操作</Title>
              <div className="space-y-2">
                {!isTeamLeader && (
                  <Button
                    danger
                    block
                    onClick={handleLeaveTeam}
                  >
                    离开团队
                  </Button>
                )}
              </div>
            </div>
          </Card>
        </div>

        {/* 邀请成员模态框 */}
        <Modal
          title="邀请团队成员"
          open={isInviteModalVisible}
          onCancel={() => {
            setIsInviteModalVisible(false);
            inviteForm.resetFields();
          }}
          footer={null}
          destroyOnClose
        >
          <Form
            form={inviteForm}
            name="inviteMember"
            onFinish={handleInviteMember}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="email"
              label="邮箱地址"
              rules={[
                { required: true, message: '请输入邮箱地址' },
                { type: 'email', message: '请输入有效的邮箱地址' },
              ]}
            >
              <Input placeholder="请输入要邀请的用户邮箱" />
            </Form.Item>

            <Form.Item
              name="role"
              label="角色"
              rules={[{ required: true, message: '请选择角色' }]}
              initialValue="member"
            >
              <Select placeholder="请选择角色">
                <Option value="member">成员</Option>
                <Option value="admin">管理员</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="message"
              label="邀请消息"
            >
              <TextArea
                placeholder="可以添加一些邀请消息（可选）"
                rows={3}
                maxLength={200}
                showCount
              />
            </Form.Item>

            <Form.Item>
              <Space className="w-full justify-end">
                <Button onClick={() => {
                  setIsInviteModalVisible(false);
                  inviteForm.resetFields();
                }}>
                  取消
                </Button>
                <Button type="primary" htmlType="submit">
                  发送邀请
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>

        {/* 编辑团队模态框 */}
        <Modal
          title="编辑团队信息"
          open={isEditModalVisible}
          onCancel={() => {
            setIsEditModalVisible(false);
            editForm.resetFields();
          }}
          footer={null}
          destroyOnClose
        >
          <Form
            form={editForm}
            name="editTeam"
            onFinish={handleUpdateTeam}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="name"
              label="团队名称"
              rules={[
                { required: true, message: '请输入团队名称' },
                { max: 100, message: '团队名称不能超过100个字符' },
              ]}
            >
              <Input placeholder="请输入团队名称" />
            </Form.Item>

            <Form.Item
              name="description"
              label="团队描述"
              rules={[
                { max: 500, message: '团队描述不能超过500个字符' },
              ]}
            >
              <TextArea
                placeholder="简单描述一下团队"
                rows={3}
                showCount
                maxLength={500}
              />
            </Form.Item>

            <Form.Item>
              <Space className="w-full justify-end">
                <Button onClick={() => {
                  setIsEditModalVisible(false);
                  editForm.resetFields();
                }}>
                  取消
                </Button>
                <Button type="primary" htmlType="submit">
                  保存更改
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </div>
  );
}
