import { DeleteOutlined, PlusOutlined, SendOutlined } from '@ant-design/icons'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button, Card, Empty, Input, List, Popconfirm, Space, Tag, Typography } from 'antd'
import { useEffect, useRef, useState } from 'react'
import client from '../api/client'
import type { ChatMessage, ChatSession, Source } from '../types'

export default function Chat() {
  const qc = useQueryClient()
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const { data: sessions } = useQuery({
    queryKey: ['chat-sessions'],
    queryFn: async () => (await client.get<ChatSession[]>('/chat/sessions')).data,
  })

  const loadMessages = async (id: string) => {
    const { data } = await client.get<ChatMessage[]>(`/chat/sessions/${id}/messages`)
    setMessages(data)
  }

  useEffect(() => {
    if (sessionId) loadMessages(sessionId)
  }, [sessionId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const createSession = useMutation({
    mutationFn: () => client.post<ChatSession>('/chat/sessions', {}),
    onSuccess: ({ data }) => {
      qc.invalidateQueries({ queryKey: ['chat-sessions'] })
      setSessionId(data.id)
      setMessages([])
    },
  })

  const deleteSession = useMutation({
    mutationFn: (id: string) => client.delete(`/chat/sessions/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['chat-sessions'] })
      if (sessionId === null) setMessages([])
    },
  })

  const send = async () => {
    const content = input.trim()
    if (!content || !sessionId || streaming) return
    setInput('')
    const token = localStorage.getItem('token')
    setMessages((prev) => [
      ...prev,
      { id: `tmp-${Date.now()}`, session_id: sessionId, role: 'user', content, sources: null, created_at: new Date().toISOString() },
    ])
    setStreaming(true)
    let full = ''
    let sources: Source[] = []
    setMessages((prev) => [
      ...prev,
      { id: 'streaming', session_id: sessionId, role: 'assistant', content: '', sources: null, created_at: new Date().toISOString() },
    ])
    try {
      const resp = await fetch(`/api/v1/chat/sessions/${sessionId}/messages?stream=true`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ content }),
      })
      const reader = resp.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (!line.startsWith('data:')) continue
          const payload = line.slice(5).trim()
          if (payload === '[DONE]') continue
          try {
            const parsed = JSON.parse(payload)
            if (Array.isArray(parsed)) {
              sources = parsed
              setMessages((prev) => prev.map((m) => (m.id === 'streaming' ? { ...m, sources } : m)))
            } else if (typeof parsed === 'string') {
              full += parsed
              setMessages((prev) =>
                prev.map((m) => (m.id === 'streaming' ? { ...m, content: full, sources } : m)),
              )
            }
          } catch {
            /* ignore partial */
          }
        }
      }
    } catch {
      /* handle error */
    } finally {
      setStreaming(false)
      await loadMessages(sessionId)
      qc.invalidateQueries({ queryKey: ['chat-sessions'] })
    }
  }

  return (
    <div style={{ display: 'flex', gap: 16, height: 'calc(100vh - 140px)' }}>
      <Card
        title="会话"
        extra={
          <Button size="small" icon={<PlusOutlined />} onClick={() => createSession.mutate()}>
            新建
          </Button>
        }
        style={{ width: 260 }}
        styles={{ body: { padding: 8, overflowY: 'auto' } }}
      >
        <List
          dataSource={sessions}
          renderItem={(s) => (
            <List.Item
              onClick={() => setSessionId(s.id)}
              style={{
                cursor: 'pointer',
                padding: '8px 12px',
                borderRadius: 6,
                background: s.id === sessionId ? '#e6f4ff' : 'transparent',
              }}
              actions={[
                <Popconfirm
                  key="del"
                  title="删除会话？"
                  onConfirm={(e) => {
                    e?.stopPropagation()
                    deleteSession.mutate(s.id)
                  }}
                >
                  <DeleteOutlined onClick={(e) => e.stopPropagation()} />
                </Popconfirm>,
              ]}
            >
              <Typography.Text ellipsis>{s.title}</Typography.Text>
            </List.Item>
          )}
          locale={{ emptyText: '暂无会话' }}
        />
      </Card>

      <Card style={{ flex: 1, display: 'flex', flexDirection: 'column' }} styles={{ body: { flex: 1, display: 'flex', flexDirection: 'column' } }}>
        <div style={{ flex: 1, overflowY: 'auto', paddingBottom: 8 }}>
          {messages.length === 0 ? (
            <Empty description={sessionId ? '开始提问吧' : '请先创建或选择一个会话'} />
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                style={{
                  display: 'flex',
                  justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
                  marginBottom: 12,
                }}
              >
                <div style={{ maxWidth: '75%' }}>
                  <div
                    style={{
                      padding: '8px 12px',
                      borderRadius: 8,
                      background: m.role === 'user' ? '#1677ff' : '#f0f0f0',
                      color: m.role === 'user' ? '#fff' : '#000',
                      whiteSpace: 'pre-wrap',
                    }}
                  >
                    {m.content || (streaming && m.id === 'streaming' ? '思考中…' : '')}
                  </div>
                  {m.sources && m.sources.length > 0 && (
                    <div style={{ marginTop: 6 }}>
                      {m.sources.map((s) => (
                        <Card
                          key={s.index}
                          size="small"
                          style={{ marginBottom: 4 }}
                          title={
                            <Space>
                              <Tag color="blue">[{s.index}]</Tag>
                              <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                                {s.filename}
                                {s.page_number ? ` · P${s.page_number}` : ''} · 相似度 {s.score.toFixed(3)}
                              </Typography.Text>
                            </Space>
                          }
                        >
                          <Typography.Text style={{ fontSize: 12 }}>{s.content}</Typography.Text>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={bottomRef} />
        </div>
        <Space.Compact style={{ width: '100%', marginTop: 8 }}>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={send}
            placeholder="输入问题，回车发送"
            disabled={!sessionId}
          />
          <Button type="primary" icon={<SendOutlined />} onClick={send} loading={streaming} disabled={!sessionId}>
            发送
          </Button>
        </Space.Compact>
      </Card>
    </div>
  )
}
