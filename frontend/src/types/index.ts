export interface MacAddress {
  id: string
  asset_id: string
  mac: string
  ip?: string
  remark?: string
  created_at: string
}

export interface UsageRecord {
  id: string
  asset_id: string
  user_name: string
  start_time: string
  end_time?: string
  operation_type: '入库' | '领用' | '归还' | '报废'
  operator: string
  ip_addresses?: string
  created_at: string
}

export interface OperationLog {
  id: string
  asset_id?: string
  device_id?: string
  asset_code?: string
  operator: string
  action: string
  before_state?: Record<string, any>
  after_state?: Record<string, any>
  created_at: string
}

export interface Asset {
    id: string
    device_id: string
    asset_code: string
    temp_code?: string
    machine_model: string
    machine_type: '台式机' | '笔记本' | '打印/扫描' | '电视机' | '服务器' | '其它'
    status: '在库' | '使用中' | '报废'
    cpu?: string
    memory?: string
    disk?: string
    serial_number?: string
    remark?: string
    created_at: string
    updated_at: string
    mac_addresses: MacAddress[]
    usage_records: UsageRecord[]
}

export interface AssetSimple {
    id: string
    device_id: string
    asset_code: string
    temp_code?: string
    machine_model: string
    machine_type: '台式机' | '笔记本' | '打印/扫描' | '电视机' | '服务器' | '其它'
    status: '在库' | '使用中' | '报废'
    cpu?: string
    memory?: string
    disk?: string
    serial_number?: string
    remark?: string
    created_at: string
    updated_at: string
}

export interface Pagination {
  page: number
  pageSize: number
  total: number
}

export interface ApiResponse<T> {
  code: number
  data: T
  message?: string
}

export interface AssetListResponse {
  items: AssetSimple[]
  page: number
  pageSize: number
  total: number
}

export interface AssetFilters {
  assetCode?: string
  machineModel?: string
  machineType?: string
  status?: string
  userName?: string
  deviceId?: string
  mac?: string
  ip?: string
}
