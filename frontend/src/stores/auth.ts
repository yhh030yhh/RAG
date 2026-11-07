import { create } from 'zustand'

interface AuthState {
  token: string | null
  username: string | null
  setToken: (token: string) => void
  setUser: (username: string) => void
  logout: () => void
}

export const useAuth = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  username: localStorage.getItem('username'),
  setToken: (token) => {
    localStorage.setItem('token', token)
    set({ token })
  },
  setUser: (username) => {
    localStorage.setItem('username', username)
    set({ username })
  },
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    set({ token: null, username: null })
  },
}))
