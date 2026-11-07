import { SearchOutlined } from '@ant-design/icons'
import { Button, Card, Checkbox, Form, Input, InputNumber, Space, Tag, Typography } from 'antd'
import { useState } from 'react'
import client from '../api/client'
import type { RetrieveResponse } from '../types'

export default function Retrieval() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<RetrieveResponse | null>(null)

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      const { data } = await client.post<RetrieveResponse>('/rag/retrieve', values)
      setResult(data)
    } catch (e: any) {
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Card title="检索调试" style={{ marginBottom: 16 }}>
        <Form
          form={form}
          layout="inline"
          initialValues={{ top_k: 5, generate: false }}
          onFinish={onFinish}
        >
          <Form.Item name="question" rules={[{ required: true, message: '请输入测试问题' }]}>
            <Input placeholder="输入测试问题" style={{ width: 360 }} />
          </Form.Item>
          <Form.Item name="top_k" label="Top-K">
            <InputNumber min={1} max={50} />
          </Form.Item>
          <Form.Item name="threshold" label="阈值">
            <InputNumber min={0} max={1} step={0.05} placeholder="默认" />
          </Form.Item>
          <Form.Item name="generate" valuePropName="checked">
            <Checkbox>同时生成回答</Checkbox>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" icon={<SearchOutlined />} loading={loading}>
              检索
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {result && (
        <>
          <Card title="Query Embedding" style={{ marginBottom: 16 }}>
            <Typography.Text>
              向量维度：{result.query_embedding_dim}，命中 {result.hits.length} 条
            </Typography.Text>
          </Card>

          <Card title="Top-K 检索结果" style={{ marginBottom: 16 }}>
            {result.hits.length === 0 ? (
              <Typography.Text type="secondary">未检索到相关内容</Typography.Text>
            ) : (
              result.hits.map((h) => (
                <div key={h.index} style={{ padding: 12, borderBottom: '1px solid #f0f0f0' }}>
                  <Space>
                    <Tag color="blue">#{h.index}</Tag>
                    <Tag color="green">相似度 {h.score.toFixed(4)}</Tag>
                    <Tag>{h.filename}</Tag>
                    {h.page_number && <Tag>第 {h.page_number} 页</Tag>}
                  </Space>
                  <div style={{ whiteSpace: 'pre-wrap', marginTop: 8, color: '#555' }}>
                    {h.content}
                  </div>
                </div>
              ))
            )}
          </Card>

          {result.answer && (
            <Card title="最终回答">
              <div style={{ whiteSpace: 'pre-wrap' }}>{result.answer}</div>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
