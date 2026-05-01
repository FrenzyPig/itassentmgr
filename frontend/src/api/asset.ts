import api from './request'
import type { ApiResponse, Asset, AssetSimple, AssetListResponse, OperationLog, MacAddress } from '../types'

export const assetApi = {
  getList: (params: {
    page?: number
    pageSize?: number
    assetCode?: string
    machineModel?: string
    machineType?: string
    status?: string
    userName?: string
    deviceId?: string
    mac?: string
    ip?: string
  }) => {
    return api.get<ApiResponse<AssetListResponse>>('/assets', { params })
  },

  getById: (id: string) => {
    return api.get<ApiResponse<Asset>>(`/assets/${id}`)
  },

  create: (data: {
    machine_model: string
    machine_type: string
    asset_code?: string
    mac_addresses?: Array<{ mac: string; remark?: string }>
    cpu?: string
    memory?: string
    disk?: string
    serial_number?: string
    remark?: string
    operator?: string
  }) => {
    return api.post<ApiResponse<Asset>>('/assets', data)
  },

  update: (id: string, data: Partial<Asset> & { operator?: string }) => {
    return api.put<ApiResponse<Asset>>(`/assets/${id}`, data)
  },

  delete: (id: string, operator?: string) => {
    return api.delete(`/assets/${id}`, { params: { operator } })
  },

  claim: (id: string, data: {
    user_name: string
    ip_addresses: Array<{ mac_id: string; ip: string }>
    operator?: string
  }) => {
    return api.post<ApiResponse<Asset>>(`/assets/${id}/claim`, data)
  },

  retire: (id: string, operator?: string) => {
    return api.post<ApiResponse<Asset>>(`/assets/${id}/retire`, { operator })
  },

  changeUser: (id: string, data: {
    user_name: string
    operator?: string
    ip_addresses?: Array<{ mac_id: string; ip: string }>
  }) => {
    return api.post<ApiResponse<Asset>>(`/assets/${id}/change-user`, data)
  },

  returnToStorage: (id: string, operator?: string) => {
    return api.post<ApiResponse<Asset>>(`/assets/${id}/return`, { operator })
  },

  getPending: () => {
    return api.get<ApiResponse<AssetSimple[]>>('/assets/pending')
  },

  addMac: (assetId: string, data: { mac: string; ip?: string; remark?: string; operator?: string }) => {
    return api.post<ApiResponse<MacAddress>>(`/assets/${assetId}/mac`, data)
  },

  deleteMac: (macId: string, operator?: string) => {
    return api.delete(`/mac/${macId}`, { params: { operator } })
  },

  updateMac: (macId: string, data: { mac?: string; ip?: string; remark?: string; operator?: string }) => {
    return api.put<ApiResponse<MacAddress>>(`/mac/${macId}`, data)
  },

  downloadTemplate: () => {
    return api.get('/assets/import/template', { responseType: 'blob' })
  },

  importAssets: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<ApiResponse<{ success: number; failed: number; errors: string[] }>>('/assets/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export const logApi = {
  getList: (params: {
    page?: number
    pageSize?: number
    startDate?: string
    endDate?: string
    operator?: string
    assetCode?: string
  }) => {
    return api.get<ApiResponse<{ items: OperationLog[]; page: number; pageSize: number; total: number }>>('/logs', { params })
  },

  getByAssetId: (assetId: string) => {
    return api.get<ApiResponse<OperationLog[]>>(`/logs/${assetId}`)
  }
}

export default api
