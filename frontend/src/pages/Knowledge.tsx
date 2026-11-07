import { DeleteOutlined, ReloadOutlined, UploadOutlined } from '@ant-design/icons'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button, Modal, Popconfirm, Space, Table, Tag, message } from 'antd'
import { useRef, useState } from 'react'
import client from '../api/client'
import type { Doc, DocChunk } from '../types'

const STATUS_COLOR: Record<string, string> = {
  PENDING: 'orange',
  PROCESSING: 'blue',
  COMPLETED: 'green',
  FAILED: 'red',
}

export default function Knowledge() {
  const qc = useQueryClient()
  const fileRef = useRef<HTMLInputElement>(null)
  const [chunks, setChunks] = useState<DocChunk[]>([])
  const [chunkOpen, setChunkOpen] = useState(false)
  const [uploading, setUploading] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => (await client.get<Doc[]>('/documents')).data,
    refetchInterval: 3000,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => client.delete(`/documents/${id}`),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  const reindexMutation = useMutation({
    mutationFn: (id: string) => client.post(`/documents/${id}/reindex`),
    onSuccess: () => {
      message.success('已提交重新索引')
      qc.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  const onUpload = async (file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    setUploading(true)
    try {
      await client.post('/documents/upload', fd)
      message.success('上传成功，正在处理…')
      qc.invalidateQueries({ queryKey: ['documents'] })
    } catch (e: any) {
      message.error(e.response?.data?.detail || '上传失败')
    } finally {
      setUploading(false)
    }
  }

  const viewChunks = async (id: string) => {
    const { data } = await client.get<DocChunk[]>(`/documents/${id}/chunks`)
    setChunks(data)
    setChunkOpen(true)
  }

  const columns = [
    { title: '文件名', dataIndex: 'filename', key: 'filename' },
    { title: '类型', dataIndex: 'file_type', key: 'file_type', render: (v: string) => <Tag>{v}</Tag> },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (v: string, r: Doc) => (
        <Tag color={STATUS_COLOR[v]}>
          {v}
          {v === 'FAILED' && r.error_message ? `: ${r.error_message}` : ''}
        </Tag>
      ),
    },
    { title: '分块数', dataIndex: 'chunk_count', key: 'chunk_count' },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, r: Doc) => (
        <Space>
          <Button size="small" onClick={() => viewChunks(r.id)} disabled={r.chunk_count === 0}>
            查看分块
          </Button>
          <Button size="small" icon={<ReloadOutlined />} onClick={() => reindexMutation.mutate(r.id)}>
            重新索引
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
      <Button
        type="primary"
        icon={<UploadOutlined />}
        loading={uploading}
        onClick={() => fileRef.current?.click()}
        style={{ marginBottom: 16 }}
      >
        上传文档（PDF / TXT / MD）
      </Button>
      <input
        ref={fileRef}
        type="file"
        accept=".pdf,.txt,.md,.markdown"
        style={{ display: 'none' }}
        onChange={(e) => {
          const f = e.target.files?.[0]
          if (f) onUpload(f)
          e.target.value = ''
        }}
      />
      <Table rowKey="id" loading={isLoading} dataSource={data} columns={columns} />
      <Modal
        title={`分块内容（共 ${chunks.length} 块）`}
        open={chunkOpen}
        onCancel={() => setChunkOpen(false)}
        footer={null}
        width={800}
      >
        {chunks.map((c) => (
          <div key={c.id} style={{ marginBottom: 12, padding: 8, background: '#fafafa', borderRadius: 6 }}>
            <div style={{ color: '#888', fontSize: 12 }}>
              分块 #{c.chunk_index}
              {c.page_number ? ` · 第 ${c.page_number} 页` : ''}
            </div>
            <div style={{ whiteSpace: 'pre-wrap', marginTop: 4 }}>{c.content}</div>
          </div>
        ))}
      </Modal>
    </div>
  )
}
