export interface User {
  id: string
  username: string
  email: string | null
  role: string
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface Category {
  id: string
  name: string
  description: string | null
  created_at: string
}

export interface Tag {
  id: string
  name: string
  created_at: string
}

export interface Article {
  id: string
  title: string
  slug: string
  summary: string | null
  content: string
  category_id: string | null
  author_id: string | null
  status: string
  published_at: string | null
  created_at: string
  updated_at: string
  category: Category | null
  tags: Tag[]
}

export interface Page<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface Doc {
  id: string
  filename: string
  file_type: string
  file_size: number
  status: string
  chunk_count: number
  error_message: string | null
  created_at: string
  indexed_at: string | null
}

export interface DocChunk {
  id: string
  document_id: string
  chunk_index: number
  content: string
  page_number: number | null
  meta: Record<string, unknown> | null
  created_at: string
}

export interface Source {
  index: number
  document_id: string
  filename: string
  chunk_index: number
  page_number: number | null
  score: number
  content: string
}

export interface ChatSession {
  id: string
  user_id: string | null
  title: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  sources: Source[] | null
  created_at: string
}

export interface RetrieveHit {
  index: number
  score: number
  chunk_index: number
  page_number: number | null
  content: string
  filename: string
}

export interface RetrieveResponse {
  question: string
  query_embedding_dim: number
  hits: RetrieveHit[]
  answer: string | null
}

export interface RagHealth {
  embedding_provider: string
  embedding_configured: boolean
  llm_provider: string
  llm_configured: boolean
  document_count: number
  chunk_count: number
}
