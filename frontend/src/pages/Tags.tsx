import { DeleteOutlined, PlusOutlined } from '@ant-design/icons'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button, Form, Input, Modal, Popconfirm, Space, Table, Tag, message } from 'antd'
import { useState } from 'react'
import client from '../api/client'
import type { Tag as TagT } from '../types'

export default function Tags() {
  const qc = useQueryClient()
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()

  const { data, isLoading } = useQuery({
    queryKey: ['tags'],
    queryFn: async () => (await client.get<TagT[]>('/tags')).data,
  })

  const createMutation = useMutation({
    mutationFn: (values: { name: string }) => client.post('/tags', values),
    onSuccess: () => {
      message.success('已创建')
      setOpen(false)
      form.resetFields()
      qc.invalidateQueries({ queryKey: ['tags'] })
    },
    onError: (e: any) => message.error(e.response?.data?.detail || '创建失败'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => client.delete(`/tags/${id}`),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['tags'] })
    },
  })

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name', render: (v: string) => <Tag>{v}</Tag> },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, r: TagT) => (
        <Popconfirm title="确认删除？" onConfirm={() => deleteMutation.mutate(r.id)}>
          <Button size="small" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ]

  return (
    <div>
      <Button
        type="primary"
        icon={<PlusOutlined />}
        onClick={() => {
          form.resetFields()
          setOpen(true)
        }}
        style={{ marginBottom: 16 }}
      >
        新增标签
      </Button>
      <Table rowKey="id" loading={isLoading} dataSource={data} columns={columns} />
      <Modal
        title="新增标签"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={(v) => createMutation.mutate(v)}>
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
