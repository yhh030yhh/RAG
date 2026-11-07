import {
  BookOutlined,
  CommentOutlined,
  DashboardOutlined,
  ExperimentOutlined,
  FileTextOutlined,
  LogoutOutlined,
  TagsOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons'
import { Layout, Menu, Space, Typography } from 'antd'
import { useMemo } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../stores/auth'

const { Header, Sider, Content } = Layout

export default function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { username, logout } = useAuth()

  const selectedKey = useMemo(() => {
    const seg = location.pathname.split('/')[2] || 'dashboard'
    return seg
  }, [location.pathname])

  const menuItems = [
    { key: 'dashboard', icon: <DashboardOutlined />, label: '首页' },
    { key: 'articles', icon: <FileTextOutlined />, label: '文章管理' },
    { key: 'categories', icon: <UnorderedListOutlined />, label: '分类管理' },
    { key: 'tags', icon: <TagsOutlined />, label: '标签管理' },
    { key: 'knowledge', icon: <BookOutlined />, label: '知识库管理' },
    { key: 'retrieval', icon: <ExperimentOutlined />, label: 'RAG 调试' },
    { key: 'chat', icon: <CommentOutlined />, label: 'AI 问答' },
  ]

  const onLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={220}>
        <div
          style={{
            height: 56,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontWeight: 600,
            fontSize: 18,
          }}
        >
          SmartCMS
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(`/admin/${key}`)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Typography.Text strong style={{ fontSize: 16 }}>
            智能内容管理系统
          </Typography.Text>
          <Space>
            <Typography.Text>{username || 'admin'}</Typography.Text>
            <a onClick={onLogout}>
              <LogoutOutlined /> 退出
            </a>
          </Space>
        </Header>
        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
