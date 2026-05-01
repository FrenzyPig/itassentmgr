<template>
  <div class="asset-change">
    <el-button @click="$router.back()">返回</el-button>

    <el-card style="margin-top: 16px">
      <template #header>
        <span>更换使用人</span>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="选择资产" prop="asset_id">
          <el-select
            v-model="form.asset_id"
            placeholder="请选择要更换的资产"
            filterable
            @change="handleAssetChange"
          >
            <el-option
              v-for="asset in availableAssets"
              :key="asset.id"
              :label="`${asset.asset_code} - ${asset.machine_model}`"
              :value="asset.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item v-if="currentMacs.length > 0" label="MAC地址">
          <div style="display: flex; flex-direction: column;">
            <div v-for="mac in currentMacs" :key="mac.id" class="mac-row">
              <el-input :model-value="mac.mac" disabled placeholder="MAC地址" style="width: 160px; margin-right: 8px" />
              <el-input :model-value="mac.remark || '有线'" disabled placeholder="MAC类型" style="width: 100px; margin-right: 8px" />
              <el-input v-model="mac.ip" placeholder="IP地址" style="width: 220px" />
            </div>
          </div>
        </el-form-item>

        <el-form-item label="新使用人" prop="user_name">
          <el-input v-model="form.user_name" placeholder="请输入新使用人姓名" />
        </el-form-item>

        <el-form-item label="操作人">
          <span>{{ currentUser }}</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确认更换</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAssetStore } from '../stores/asset'
import { assetApi } from '../api/asset'
import type { AssetSimple, MacAddress } from '../types'

interface MacWithIp extends MacAddress {
  ip: string
}

const router = useRouter()
const route = useRoute()
const store = useAssetStore()

const formRef = ref()
const submitting = ref(false)
const availableAssets = ref<AssetSimple[]>([])
const currentMacs = ref<MacWithIp[]>([])

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

const form = reactive({
  asset_id: '',
  user_name: ''
})

const rules = {
  asset_id: [{ required: true, message: '请选择资产', trigger: 'change' }],
  user_name: [{ required: true, message: '请输入新使用人', trigger: 'blur' }]
}

onMounted(async () => {
  const id = route.query.id as string
  if (id) {
    form.asset_id = id
    await handleAssetChange()
  }
  await fetchAvailableAssets()
})

async function fetchAvailableAssets() {
  try {
    const res: any = await assetApi.getList({ status: '使用中', pageSize: 100 })
    if (res.code === 200) {
      availableAssets.value = res.data.items
    }
  } catch (error) {
    console.error('Failed to fetch assets:', error)
  }
}

async function handleAssetChange() {
  if (form.asset_id) {
    await store.fetchAssetById(form.asset_id)
    if (store.currentAsset) {
      const macs = store.currentAsset.mac_addresses || []

      currentMacs.value = macs.map((m) => ({
        ...m,
        ip: m.ip || ''
      }))
    }
  }
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  const ipAddresses = currentMacs.value
    .filter(m => m.ip && m.ip !== '0.0.0.0')
    .map(m => ({
      mac_id: m.id,
      ip: m.ip
    }))

  submitting.value = true
  try {
    const res: any = await assetApi.changeUser(form.asset_id, {
      user_name: form.user_name,
      ip_addresses: ipAddresses,
      operator: currentUser.value
    })
    if (res.code === 200) {
      ElMessage.success('更换成功')
      router.push('/assets')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '更换失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.mac-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
</style>
