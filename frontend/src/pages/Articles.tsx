import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Button,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  message,
} from 'antd'
import { useState } from 'react'
import client from '../api/client'
import type { Article, Category, Page, Tag as TagT } from '../types'

const { TextArea } = Input

export default function Articles() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string | undefined>()
  const [editing, setEditing] = useState<Article | null>(null)
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => (await client.get<Category[]>('/categories')).data,
  })
  const { data: tags } = useQuery({
    queryKey: ['tags'],
    queryFn: async () => (await client.get<TagT[]>('/tags')).data,
  })
  const { data, isLoading } = useQuery({
    queryKey: ['articles', page, pageSize, search, status],
    queryFn: async () =>
      (
        await client.get<Page<Article>>('/articles', {
          params: { page, page_size: pageSize, search, status },
        })
      ).data,
  })

  const saveMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editing) return (await client.put(`/articles/${editing.id}`, values)).data
      return (await client.post('/articles', values)).data
    },
    onSuccess: () => {
      message.success('保存成功')
      setOpen(false)
      form.resetFields()
      qc.invalidateQueries({ queryKey: ['articles'] })
    },
    onError: (e: any) => message.error(e.response?.data?.detail || '保存失败'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => client.delete(`/articles/${id}`),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['articles'] })
    },
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: 'publish' | 'archive' }) =>
      client.post(`/articles/${id}/${action}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['articles'] }),
  })

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setOpen(true)
  }
  const openEdit = (a: Article) => {
    setEditing(a)
    form.setFieldsValue({
      title: a.title,
      summary: a.summary,
      content: a.content,
      category_id: a.category_id,
      tag_ids: a.tags.map((t) => t.id),
    })
    setOpen(true)
  }

  const columns = [
    { title: '标题', dataIndex: 'title', key: 'title' },
    {
      title: '分类',
      key: 'category',
      render: (_: any, r: Article) => r.category?.name || '-',
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      render: (ts: TagT[]) => ts.map((t) => <Tag key={t.id}>{t.name}</Tag>),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (s: string) => {
        const color = s === 'PUBLISHED' ? 'green' : s === 'ARCHIVED' ? 'default' : 'orange'
        return <Tag color={color}>{s}</Tag>
      },
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (v: string) => new Date(v).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, r: Article) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)}>
            编辑
          </Button>
          {r.status === 'DRAFT' && (
            <Button size="small" onClick={() => statusMutation.mutate({ id: r.id, action: 'publish' })}>
              发布
            </Button>
          )}
          {r.status === 'PUBLISHED' && (
            <Button size="small" onClick={() => statusMutation.mutate({ id: r.id, action: 'archive' })}>
              归档
            </Button>
          )}
          <Popconfirm title="确认删除？" onConfirm={() => deleteMutation.mutate(r.id)}>
            <Button size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          新建文章
        </Button>
        <Input.Search
          placeholder="搜索标题/正文"
          allowClear
          onSearch={(v) => {
            setSearch(v)
            setPage(1)
          }}
          style={{ width: 240 }}
        />
        <Select
          placeholder="状态筛选"
          allowClear
          value={status}
          onChange={(v) => {
            setStatus(v)
            setPage(1)
          }}
          style={{ width: 160 }}
          options={[
            { value: 'DRAFT', label: '草稿' },
            { value: 'PUBLISHED', label: '已发布' },
            { value: 'ARCHIVED', label: '已归档' },
          ]}
        />
      </Space>
      <Table
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items}
        columns={columns}
        pagination={{
          current: page,
          pageSize,
          total: data?.total,
          onChange: (p, ps) => {
            setPage(p)
            setPageSize(ps)
          },
        }}
      />
      <Modal
        title={editing ? '编辑文章' : '新建文章'}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
        width={760}
      >
        <Form form={form} layout="vertical" onFinish={(v) => saveMutation.mutate(v)}>
          <Form.Item name="title" label="标题" rules={[{ required: true, message: '请输入标题' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="summary" label="摘要">
            <Input />
          </Form.Item>
          <Space size="large" style={{ display: 'flex' }}>
            <Form.Item name="category_id" label="分类" style={{ minWidth: 240 }}>
              <Select
                allowClear
                placeholder="选择分类"
                options={categories?.map((c) => ({ value: c.id, label: c.name }))}
              />
            </Form.Item>
            <Form.Item name="tag_ids" label="标签" style={{ minWidth: 240 }}>
              <Select
                mode="multiple"
                allowClear
                placeholder="选择标签"
                options={tags?.map((t) => ({ value: t.id, label: t.name }))}
              />
            </Form.Item>
          </Space>
          <Form.Item name="content" label="正文（Markdown）" rules={[{ required: true, message: '请输入正文' }]}>
            <TextArea rows={12} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
