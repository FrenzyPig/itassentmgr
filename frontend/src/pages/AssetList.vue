<template>
  <div class="asset-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资产列表</span>
          <div>
            <el-button type="primary" @click="$router.push('/import')">入库</el-button>
            <el-button @click="$router.push('/logs')">操作日志</el-button>
          </div>
        </div>
      </template>

      <div class="filters">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="资产编号">
            <el-input v-model="filterForm.assetCode" placeholder="资产编号" clearable />
          </el-form-item>
          <el-form-item label="使用人">
            <el-input v-model="filterForm.userName" placeholder="使用人" clearable />
          </el-form-item>
          <el-form-item label="MAC地址">
            <el-input v-model="filterForm.mac" placeholder="MAC地址" clearable />
          </el-form-item>
          <el-form-item label="IP地址">
            <el-input v-model="filterForm.ip" placeholder="IP地址" clearable />
          </el-form-item>
          <el-form-item label="机器型号">
            <el-input v-model="filterForm.machineModel" placeholder="机器型号" clearable />
          </el-form-item>
          <el-form-item label="机器类型">
            <el-select v-model="filterForm.machineType" placeholder="全部" clearable>
              <el-option label="台式机" value="台式机" />
              <el-option label="笔记本" value="笔记本" />
              <el-option label="打印/扫描" value="打印/扫描" />
              <el-option label="电视机" value="电视机" />
              <el-option label="服务器" value="服务器" />
              <el-option label="其它" value="其它" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="全部" clearable>
              <el-option label="在库" value="在库" />
              <el-option label="使用中" value="使用中" />
              <el-option label="报废" value="报废" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-alert
        v-if="store.hasPendingAssets"
        type="warning"
        :closable="false"
        style="margin-bottom: 16px; display: flex; justify-content: center; align-items: center;"
      >
        <span>有 {{ store.pendingAssets.length }} 个待分配正式编号的资产</span>
        <el-button size="small" type="warning" @click="showPendingDialog = true" style="margin-left: 16px;">查看</el-button>
      </el-alert>

      <el-table :data="store.assets" v-loading="store.loading" stripe>
        <el-table-column prop="asset_code" label="资产编号" min-width="200" />
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="机器信息" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            [{{ row.machine_type }}] {{ row.machine_model }}
          </template>
        </el-table-column>
        <el-table-column label="配置" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.cpu }}|{{ row.memory }}|{{ row.disk }}
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ (row.remark || '').slice(0, 10) }}{{ (row.remark && row.remark.length > 10) ? '...' : '' }}
          </template>
        </el-table-column>
        <el-table-column label="使用人" min-width="120">
          <template #default="{ row }">
            {{ row.current_user || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row.id)">详情</el-button>
            <el-button link type="success" v-if="row.status === '在库'" @click="handleClaim(row)">领用</el-button>
            <el-button link type="warning" v-if="row.status === '使用中'" @click="handleReturn(row)">入库</el-button>
            <el-button link type="info" v-if="row.status === '使用中'" @click="handleChange(row)">更换</el-button>
            <el-button link type="danger" v-if="row.status !== '报废'" @click="handleRetire(row)">报废</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="store.pagination.page"
          :page-size="store.pagination.pageSize"
          :total="store.pagination.total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="showPendingDialog" title="待处理资产" width="700px" align-center>
      <el-table :data="store.pendingAssets">
        <el-table-column prop="asset_code" label="临时编号" min-width="150" />
        <el-table-column label="机器信息" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            [{{ row.machine_type }}] {{ row.machine_model }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row.id)">详情</el-button>
            <el-button link type="warning" @click="editAsset(row.id, true)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAssetStore } from '../stores/asset'

const router = useRouter()
const store = useAssetStore()

const filterForm = reactive({
  deviceId: '',
  assetCode: '',
  mac: '',
  ip: '',
  machineModel: '',
  machineType: '',
  status: '',
  userName: ''
})

const showPendingDialog = ref(false)

const currentUser = computed(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      return user.username
    } catch {
      return 'admin'
    }
  }
  return 'admin'
})

onMounted(() => {
  store.fetchAssets()
  store.fetchPendingAssets()
})

function getStatusType(status: string) {
  switch (status) {
    case '在库': return 'info'
    case '使用中': return 'success'
    case '报废': return 'danger'
    default: return ''
  }
}

function handleSearch() {
  store.setFilters({
    deviceId: filterForm.deviceId || undefined,
    assetCode: filterForm.assetCode || undefined,
    mac: filterForm.mac || undefined,
    ip: filterForm.ip || undefined,
    machineModel: filterForm.machineModel || undefined,
    machineType: filterForm.machineType || undefined,
    status: filterForm.status || undefined,
    userName: filterForm.userName || undefined
  })
  store.fetchAssets()
}

function handleReset() {
  filterForm.deviceId = ''
  filterForm.assetCode = ''
  filterForm.mac = ''
  filterForm.ip = ''
  filterForm.machineModel = ''
  filterForm.machineType = ''
  filterForm.status = ''
  filterForm.userName = ''
  store.setFilters({})
  store.fetchAssets()
}

function handlePageChange(page: number) {
  store.setPage(page)
  store.fetchAssets()
}

function viewDetail(id: string) {
  router.push(`/assets/${id}`)
}

function editAsset(id: string, openEdit: boolean = false) {
  if (openEdit) {
    router.push({ path: `/assets/${id}`, query: { edit: 'true' } })
  } else {
    router.push(`/assets/${id}`)
  }
}

async function handleClaim(row: any) {
  router.push({ name: 'asset-claim', query: { id: row.id } })
}

async function handleChange(row: any) {
  router.push({ name: 'asset-change', query: { id: row.id } })
}

async function handleReturn(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定要将资产 ${row.asset_code} 退回到库吗？`,
      '入库确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await store.returnToStorage(row.id, currentUser.value)
    ElMessage.success('入库成功')
    store.fetchAssets()
    store.fetchPendingAssets()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '入库失败')
    }
  }
}

async function handleRetire(row: any) {
  try {
    const { value } = await ElMessageBox.prompt(
      `请输入资产编码 "${row.asset_code}" 确认报废：`,
      '报废确认',
      {
        confirmButtonText: '确认报废',
        cancelButtonText: '取消',
        type: 'warning',
        inputPattern: new RegExp(`^${row.asset_code}$`),
        inputErrorMessage: '资产编码不匹配'
      }
    )
    if (value === row.asset_code) {
      await store.retireAsset(row.id)
      ElMessage.success('报废成功')
      store.fetchAssets()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '报废失败')
    }
  }
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

.filters :deep(.el-form-item) {
  margin-right: 12px;
  margin-bottom: 12px;
}

.filters :deep(.el-select) {
  width: 150px;
}

.filters :deep(.el-select .el-input__wrapper) {
  width: 100%;
}

.filters :deep(.el-option) {
  min-width: 120px;
}

.filters :deep(.el-input) {
  width: 150px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
