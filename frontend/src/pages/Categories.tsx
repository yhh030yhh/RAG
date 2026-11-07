import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button, Form, Input, Modal, Popconfirm, Space, Table, message } from 'antd'
import { useState } from 'react'
import client from '../api/client'
import type { Category } from '../types'

export default function Categories() {
  const qc = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Category | null>(null)
  const [form] = Form.useForm()

  const { data, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => (await client.get<Category[]>('/categories')).data,
  })

  const saveMutation = useMutation({
    mutationFn: async (values: { name: string; description?: string }) => {
      if (editing) return (await client.put(`/categories/${editing.id}`, values)).data
      return (await client.post('/categories', values)).data
    },
    onSuccess: () => {
      message.success('保存成功')
      setOpen(false)
      form.resetFields()
      qc.invalidateQueries({ queryKey: ['categories'] })
    },
    onError: (e: any) => message.error(e.response?.data?.detail || '保存失败'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => client.delete(`/categories/${id}`),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['categories'] })
    },
  })

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setOpen(true)
  }
  const openEdit = (c: Category) => {
    setEditing(c)
    form.setFieldsValue(c)
    setOpen(true)
  }

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description' },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, r: Category) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)}>
            编辑
          </Button>
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
      <Button type="primary" icon={<PlusOutlined />} onClick={openCreate} style={{ marginBottom: 16 }}>
        新增分类
      </Button>
      <Table rowKey="id" loading={isLoading} dataSource={data} columns={columns} />
      <Modal
        title={editing ? '编辑分类' : '新增分类'}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={(v) => saveMutation.mutate(v)}>
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
