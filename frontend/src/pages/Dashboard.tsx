import { useQuery } from '@tanstack/react-query'
import { Alert, Card, Col, Descriptions, Row, Statistic, Tag } from 'antd'
import client from '../api/client'
import type { Article, Category, Doc, Page, RagHealth, Tag as TagT } from '../types'

export default function Dashboard() {
  const { data: articles } = useQuery({
    queryKey: ['articles', 'count'],
    queryFn: async () =>
      (await client.get<Page<Article>>('/articles', { params: { page: 1, page_size: 1 } })).data,
  })
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => (await client.get<Category[]>('/categories')).data,
  })
  const { data: tags } = useQuery({
    queryKey: ['tags'],
    queryFn: async () => (await client.get<TagT[]>('/tags')).data,
  })
  const { data: docs } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => (await client.get<Doc[]>('/documents')).data,
  })
  const { data: health } = useQuery({
    queryKey: ['rag-health'],
    queryFn: async () => (await client.get<RagHealth>('/rag/health')).data,
  })

  return (
    <div>
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic title="文章" value={articles?.total ?? 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="分类" value={categories?.length ?? 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="标签" value={tags?.length ?? 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="知识库文档" value={docs?.length ?? 0} />
          </Card>
        </Col>
      </Row>

      <Card title="RAG 服务状态" style={{ marginTop: 16 }}>
        {health ? (
          <Descriptions column={3}>
            <Descriptions.Item label="Embedding 提供者">
              <Tag color={health.embedding_configured ? 'green' : 'red'}>
                {health.embedding_provider}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="LLM 提供者">
              <Tag color={health.llm_configured ? 'green' : 'red'}>{health.llm_provider}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="向量分块数">{health.chunk_count}</Descriptions.Item>
          </Descriptions>
        ) : (
          <Alert type="info" message="加载中…" />
        )}
      </Card>
    </div>
  )
}
