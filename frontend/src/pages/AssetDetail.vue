<template>
  <div class="asset-detail">
    <el-button @click="$router.back()">返回</el-button>
    <el-button type="primary" @click="openEditDialog">编辑</el-button>
    <el-button v-if="isAdmin" type="danger" @click="openDeleteAssetDialog">删除</el-button>

    <el-card v-loading="store.loading" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>资产详情 - {{ asset?.asset_code }}</span>
          <el-tag :type="getStatusType(asset?.status || '')">{{ asset?.status }}</el-tag>
        </div>
      </template>

      <div v-if="asset">
          <el-descriptions :column="2" border>
          <el-descriptions-item label="设备ID">{{ asset.device_id }}</el-descriptions-item>
          <el-descriptions-item label="资产编号">{{ asset.asset_code }}</el-descriptions-item>
          <el-descriptions-item label="机器型号">{{ asset.machine_model }}</el-descriptions-item>
          <el-descriptions-item label="机器类型">{{ asset.machine_type }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ asset.status }}</el-descriptions-item>
          <el-descriptions-item label="CPU">{{ asset.cpu || '-' }}</el-descriptions-item>
          <el-descriptions-item label="内存">{{ asset.memory || '-' }}</el-descriptions-item>
          <el-descriptions-item label="硬盘">{{ asset.disk || '-' }}</el-descriptions-item>
          <el-descriptions-item label="序列号">{{ asset.serial_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ asset.remark || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ asset.created_at }}</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="section">
          <div class="section-header">
            <h4>网络详情</h4>
            <el-button size="small" type="primary" @click="openAddNetworkDialog">添加</el-button>
          </div>
          <el-table :data="networkDetails" v-loading="loading">
            <el-table-column prop="mac" label="MAC地址" min-width="150" />
            <el-table-column prop="macType" label="MAC类型" min-width="100">
              <template #default="{ row }">
                <el-tag v-if="row.macType" :type="row.macType === '有线' ? 'success' : 'warning'" size="small">
                  {{ row.macType }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="ip" label="IP地址" min-width="140">
              <template #default="{ row }">
                {{ row.ip || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="120" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="editNetwork(row)">编辑</el-button>
                <el-button link type="danger" @click="deleteNetwork(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="section">
          <h4>使用历史</h4>
          <el-table :data="reversedUsageRecords">
            <el-table-column prop="user_name" label="使用人" min-width="100" />
            <el-table-column prop="operation_type" label="操作类型" min-width="100" />
            <el-table-column label="网络信息" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.ip_addresses || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="开始时间" min-width="160" />
            <el-table-column prop="end_time" label="结束时间" min-width="160">
              <template #default="{ row }">
                {{ row.end_time || '当前' }}
              </template>
            </el-table-column>
            <el-table-column prop="operator" label="操作人" min-width="100" />
          </el-table>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="showEditDialog" title="编辑资产" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="资产编号">
          <el-input v-model="editForm.asset_code" placeholder="请输入新的资产编号" />
        </el-form-item>
        <el-form-item label="机器型号">
          <el-input v-model="editForm.machine_model" />
        </el-form-item>
        <el-form-item label="CPU">
          <el-input v-model="editForm.cpu" />
        </el-form-item>
        <el-form-item label="内存">
          <el-input v-model="editForm.memory" />
        </el-form-item>
        <el-form-item label="硬盘">
          <el-input v-model="editForm.disk" />
        </el-form-item>
        <el-form-item label="序列号">
          <el-input v-model="editForm.serial_number" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleEdit" :loading="editLoading">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showNetworkDialog" :title="editingMacId ? '编辑网络详情' : '添加网络详情'" width="500px">
      <el-form :model="networkForm" label-width="100px">
        <el-form-item label="MAC地址" required>
          <el-input
            v-model="networkForm.mac"
            placeholder="001A2B3C4D5E"
            @input="networkForm.mac = networkForm.mac.toUpperCase().replace(/[^A-F0-9]/g, '')"
            :maxlength="12"
          />
        </el-form-item>
        <el-form-item label="MAC类型">
          <el-select v-model="networkForm.macType" placeholder="请选择" style="width: 100%">
            <el-option label="有线" value="有线" />
            <el-option label="无线" value="无线" />
            <el-option label="USB有线" value="USB有线" />
            <el-option label="USB无线" value="USB无线" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP地址">
          <el-input v-model="networkForm.ip" placeholder="0.0.0.0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showNetworkDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveNetwork" :loading="networkLoading">
          {{ editingMacId ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDeleteConfirm" title="删除确认" width="400px">
      <p>确定要删除这条网络记录吗？</p>
      <template #footer>
        <el-button @click="showDeleteConfirm = false">取消</el-button>
        <el-button type="danger" @click="confirmDeleteNetwork" :loading="networkLoading">删除</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDeleteAssetConfirm" title="删除资产确认" width="400px">
      <p>确定要删除该资产吗？此操作不可恢复！</p>
      <template #footer>
        <el-button @click="showDeleteAssetConfirm = false">取消</el-button>
        <el-button type="danger" @click="confirmDeleteAsset" :loading="deleteAssetLoading">删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAssetStore } from '../stores/asset'
import { assetApi } from '../api/asset'

const route = useRoute()
const router = useRouter()
const store = useAssetStore()

const showEditDialog = ref(false)
const editLoading = ref(false)
const showNetworkDialog = ref(false)
const showDeleteConfirm = ref(false)
const showDeleteAssetConfirm = ref(false)
const networkLoading = ref(false)
const deleteAssetLoading = ref(false)
const editingMacId = ref('')

const loading = ref(false)

interface NetworkDetail {
  id?: string
  macId: string
  mac: string
  macType: string
  ip: string
  remark: string
}

const editForm = reactive({
  asset_code: '',
  machine_model: '',
  cpu: '',
  memory: '',
  disk: '',
  serial_number: '',
  remark: ''
})

const networkForm = reactive({
  mac: '',
  macType: '',
  ip: '',
  remark: ''
})

let deletingNetwork: NetworkDetail | null = null

const asset = computed(() => store.currentAsset)

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

const isAdmin = computed(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      return user.is_admin
    } catch {
      return false
    }
  }
  return false
})

const networkDetails = computed<NetworkDetail[]>(() => {
  if (!asset.value) return []

  const macs = asset.value.mac_addresses || []

  return macs.map(mac => ({
    id: mac.id,
    macId: mac.id,
    mac: mac.mac,
    macType: mac.remark || '',
    ip: mac.ip || '',
    remark: ''
  }))
})

const reversedUsageRecords = computed(() => {
  if (!asset.value?.usage_records) return []
  return [...asset.value.usage_records].reverse()
})

onMounted(async () => {
  const id = route.params.id as string
  await store.fetchAssetById(id)
  initEditForm()

  if (route.query.edit === 'true') {
    showEditDialog.value = true
  }
})

function initEditForm() {
  if (asset.value) {
    editForm.asset_code = asset.value.asset_code
    editForm.machine_model = asset.value.machine_model
    editForm.cpu = asset.value.cpu || ''
    editForm.memory = asset.value.memory || ''
    editForm.disk = asset.value.disk || ''
    editForm.serial_number = asset.value.serial_number || ''
    editForm.remark = asset.value.remark || ''
  }
}

function openEditDialog() {
  initEditForm()
  showEditDialog.value = true
}

async function handleEdit() {
  if (!asset.value) return

  editLoading.value = true
  try {
    const res: any = await assetApi.update(asset.value.id, {
      asset_code: editForm.asset_code,
      machine_model: editForm.machine_model,
      cpu: editForm.cpu || undefined,
      memory: editForm.memory || undefined,
      disk: editForm.disk || undefined,
      serial_number: editForm.serial_number || undefined,
      remark: editForm.remark || undefined,
      operator: currentUser.value
    })
    if (res.code === 200) {
      ElMessage.success('修改成功')
      showEditDialog.value = false
      await store.fetchAssetById(asset.value.id)
    }
  } catch (error: any) {
    ElMessage.error(error.message || '修改失败')
  } finally {
    editLoading.value = false
  }
}

function openAddNetworkDialog() {
  editingMacId.value = ''
  networkForm.mac = ''
  networkForm.macType = '有线'
  networkForm.ip = '0.0.0.0'
  networkForm.remark = ''
  showNetworkDialog.value = true
}

function editNetwork(row: NetworkDetail) {
  editingMacId.value = row.macId
  networkForm.mac = row.mac
  networkForm.macType = row.macType || '有线'
  networkForm.ip = row.ip
  networkForm.remark = ''
  showNetworkDialog.value = true
}

async function handleSaveNetwork() {
  if (!asset.value) return

  if (!networkForm.mac) {
    ElMessage.warning('请输入MAC地址')
    return
  }

  networkLoading.value = true
  try {
    if (editingMacId.value) {
      await assetApi.updateMac(editingMacId.value, {
        mac: networkForm.mac,
        ip: networkForm.ip || undefined,
        remark: networkForm.macType || undefined,
        operator: currentUser.value
      })
      ElMessage.success('更新成功')
    } else {
      await assetApi.addMac(asset.value.id, {
        mac: networkForm.mac,
        ip: networkForm.ip || undefined,
        remark: networkForm.macType || undefined,
        operator: currentUser.value
      })
      ElMessage.success('添加成功')
    }

    showNetworkDialog.value = false
    await store.fetchAssetById(asset.value.id)
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    networkLoading.value = false
  }
}

function deleteNetwork(row: NetworkDetail) {
  deletingNetwork = row
  showDeleteConfirm.value = true
}

async function confirmDeleteNetwork() {
  if (!asset.value || !deletingNetwork) return

  networkLoading.value = true
  try {
    if (deletingNetwork.macId) {
      await assetApi.deleteMac(deletingNetwork.macId, currentUser.value)
    }

    ElMessage.success('删除成功')
    showDeleteConfirm.value = false
    deletingNetwork = null
    await store.fetchAssetById(asset.value.id)
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  } finally {
    networkLoading.value = false
  }
}

function openDeleteAssetDialog() {
  showDeleteAssetConfirm.value = true
}

async function confirmDeleteAsset() {
  if (!asset.value) return

  deleteAssetLoading.value = true
  try {
    await store.deleteAsset(asset.value.id, currentUser.value)
    ElMessage.success('删除成功')
    showDeleteAssetConfirm.value = false
    router.push('/assets')
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  } finally {
    deleteAssetLoading.value = false
  }
}

function getStatusType(status: string) {
  switch (status) {
    case '在库': return 'info'
    case '使用中': return 'success'
    case '报废': return 'danger'
    default: return ''
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section {
  margin-top: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section h4 {
  margin: 0;
  color: #303133;
}
</style>
