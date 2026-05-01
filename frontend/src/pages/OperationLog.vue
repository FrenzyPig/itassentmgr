<template>
  <div class="operation-log">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
          <el-button @click="$router.push('/assets')">返回资产列表</el-button>
        </div>
      </template>

      <div class="filters">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="资产编号">
            <el-input v-model="filterForm.assetCode" placeholder="资产编号" clearable />
          </el-form-item>
          <el-form-item label="操作人">
            <el-input v-model="filterForm.operator" placeholder="操作人" clearable />
          </el-form-item>
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column prop="device_id" label="设备ID" min-width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewAsset(row.asset_id)">
              {{ row.device_id }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="asset_code" label="资产编码" min-width="140" />
        <el-table-column prop="action" label="操作" min-width="100" />
        <el-table-column prop="operator" label="操作人" min-width="100" />
        <el-table-column prop="created_at" label="时间" min-width="160" />
        <el-table-column label="变更详情" min-width="180">
          <template #default="{ row }">
            <span v-if="row.action === '领用资产' || row.action === '退回入库' || row.action === '更换使用人'">
              <span v-if="row.before_state?.user || row.after_state?.user">
                {{ row.before_state?.user || '在库' }} -> {{ row.after_state?.user || '在库' }}
              </span>
              <span v-else>
                在库 -> {{ row.after_state?.user || row.after_state?.status }}
              </span>
            </span>
            <span v-else-if="row.action === '报废资产'">
              {{ row.before_state?.user || '在库' }} -> 报废
            </span>
            <span v-else-if="row.action === '修改网络信息'">
              修改网络配置
            </span>
            <span v-else>
              {{ row.action }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next"
          @current-change="fetchLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { logApi } from '../api/asset'
import type { OperationLog } from '../types'

const router = useRouter()

const logs = ref<OperationLog[]>([])
const loading = ref(false)
const dateRange = ref<[string, string] | null>(null)

const filterForm = reactive({
  assetCode: '',
  operator: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

function viewAsset(assetId: string) {
  router.push(`/assets/${assetId}`)
}

onMounted(() => {
  fetchLogs()
})

async function fetchLogs() {
  loading.value = true
  try {
    const res: any = await logApi.getList({
      page: pagination.page,
      pageSize: pagination.pageSize,
      assetCode: filterForm.assetCode || undefined,
      operator: filterForm.operator || undefined,
      startDate: dateRange.value?.[0] || undefined,
      endDate: dateRange.value?.[1] || undefined
    })
    if (res.code === 200) {
      logs.value = res.data.items
      pagination.total = res.data.total
    }
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchLogs()
}

function handleReset() {
  filterForm.assetCode = ''
  filterForm.operator = ''
  dateRange.value = null
  pagination.page = 1
  fetchLogs()
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
