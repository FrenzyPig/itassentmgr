import api from './request'
import type { ApiResponse } from '../types'

export interface User {
  id: number
  username: string
  is_admin: boolean
  is_banned: boolean
  created_at: string
}

export interface LoginData {
  username: string
  password: string
}

export interface ChangePasswordData {
  oldPassword: string
  newPassword: string
}

export interface CreateUserData {
  username: string
}

export const authApi = {
  login: (data: LoginData) => {
    return api.post<ApiResponse<{ user: User }>>('/login', data)
  },

  logout: () => {
    return api.post<ApiResponse<null>>('/logout')
  },

  getCurrentUser: () => {
    return api.get<ApiResponse<{ user: User }>>('/current-user')
  },

  changePassword: (data: ChangePasswordData) => {
    return api.post<ApiResponse<null>>('/change-password', data)
  }
}

export const userApi = {
  getList: (params?: { page?: number; pageSize?: number }) => {
    return api.get<ApiResponse<{ items: User[]; page: number; pageSize: number; total: number }>>('/users', { params })
  },

  create: (data: CreateUserData) => {
    return api.post<ApiResponse<{ user: User }>>('/users', data)
  },

  ban: (userId: number) => {
    return api.post<ApiResponse<null>>(`/users/${userId}/ban`)
  },

  unban: (userId: number) => {
    return api.post<ApiResponse<null>>(`/users/${userId}/unban`)
  },

  delete: (userId: number) => {
    return api.delete(`/users/${userId}`)
  }
}

export default api
