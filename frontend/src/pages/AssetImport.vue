<template>
  <div class="asset-import">
    <el-button @click="$router.back()">返回</el-button>

    <el-card style="margin-top: 16px">
      <template #header>
        <span>资产入库</span>
      </template>

      <el-tabs v-model="activeTab" class="import-tabs">
        <el-tab-pane label="单条入库" name="single">
          <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
            <el-form-item label="机器型号" prop="machine_model">
              <el-input v-model="form.machine_model" placeholder="请输入机器型号" />
            </el-form-item>

            <el-form-item label="机器类型" prop="machine_type">
              <el-select v-model="form.machine_type" placeholder="请选择机器类型">
                <el-option label="台式机" value="台式机" />
                <el-option label="笔记本" value="笔记本" />
                <el-option label="打印/扫描" value="打印/扫描" />
                <el-option label="电视机" value="电视机" />
                <el-option label="服务器" value="服务器" />
                <el-option label="其它" value="其它" />
              </el-select>
            </el-form-item>

            <el-form-item label="资产编号" prop="asset_code">
              <el-input v-model="form.asset_code" placeholder="不填则自动生成临时编号" />
            </el-form-item>

            <el-form-item label="MAC地址" required>
              <div v-for="(mac, index) in form.mac_addresses" :key="index" class="mac-item">
                <el-input
                  v-model="mac.mac"
                  placeholder="001A2B3C4D5E"
                  style="width: 180px"
                  @input="mac.mac = mac.mac.toUpperCase().replace(/[^A-F0-9]/g, '')"
                  :maxlength="12"
                />
                <el-select v-model="mac.remark" placeholder="MAC类型" style="width: 140px; margin-left: 8px">
                  <el-option label="有线" value="有线" />
                  <el-option label="无线" value="无线" />
                  <el-option label="USB有线" value="USB有线" />
                  <el-option label="USB无线" value="USB无线" />
                </el-select>
                <el-button type="danger" link @click="removeMac(index)" v-if="form.mac_addresses.length > 1">删除</el-button>
              </div>
              <el-button type="primary" link @click="addMac">+ 添加MAC地址</el-button>
            </el-form-item>

            <el-form-item label="CPU">
              <el-input v-model="form.cpu" placeholder="如: Intel i7-1165G7" />
            </el-form-item>

            <el-form-item label="内存">
              <el-input v-model="form.memory" placeholder="如: 16GB" />
            </el-form-item>

            <el-form-item label="硬盘">
              <el-input v-model="form.disk" placeholder="如: 512GB SSD" />
            </el-form-item>

            <el-form-item label="序列号">
              <el-input v-model="form.serial_number" placeholder="请输入序列号" />
            </el-form-item>

            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleSubmit" :loading="submitting">提交入库</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Excel 导入" name="excel" v-if="isAdmin">
          <div class="excel-import">
            <el-alert
              title="导入说明"
              type="info"
              :closable="false"
              style="margin-bottom: 16px"
            >
              <template #default>
                <div>
                  <p>• 必填：机器型号、机器类型</p>
                  <p>• MAC地址格式：MAC,IP,MAC,IP（交替），IP可不填，如：001A2B3C4D5E,192.168.1.100,001A2B3C4D5F,,</p>
                  <p>• 使用人：填写则资产状态为"使用中"，不填则为"在库"</p>
                  <p>• 是否报废：填写"是"则资产状态为"报废"，不填则为正常</p>
                  <p>• 资产编号为空时会自动生成临时编号</p>
                </div>
              </template>
            </el-alert>

            <el-button type="primary" @click="handleDownloadTemplate" style="margin-bottom: 16px">
              <el-icon><Download /></el-icon>
              下载导入模板
            </el-button>

            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :show-file-list="true"
              :limit="1"
              accept=".xlsx,.xls"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              drag
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  只支持 .xlsx 或 .xls 文件
                </div>
              </template>
            </el-upload>

            <el-button
              type="primary"
              @click="handleImport"
              :loading="importing"
              :disabled="!selectedFile"
              style="margin-top: 16px"
            >
              开始导入
            </el-button>

            <el-card v-if="importResult" style="margin-top: 16px">
              <template #header>
                <span>导入结果</span>
              </template>
              <el-alert
                :title="`成功: ${importResult.success} 条，失败: ${importResult.failed} 条`"
                :type="importResult.failed === 0 ? 'success' : 'warning'"
                :closable="false"
                style="margin-bottom: 12px"
              />
              <el-scrollbar v-if="importResult.errors.length > 0" max-height="300px">
                <ul class="error-list">
                  <li v-for="(error, index) in importResult.errors" :key="index" class="error-item">
                    {{ error }}
                  </li>
                </ul>
              </el-scrollbar>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download, UploadFilled } from '@element-plus/icons-vue'
import { useAssetStore } from '../stores/asset'

const router = useRouter()
const store = useAssetStore()

const formRef = ref()
const uploadRef = ref()
const submitting = ref(false)
const importing = ref(false)
const activeTab = ref('single')
const selectedFile = ref<File | null>(null)
const importResult = ref<{ success: number; failed: number; errors: string[] } | null>(null)

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

const form = reactive({
  machine_model: '',
  machine_type: '台式机',
  asset_code: '',
  mac_addresses: [
    { mac: '', remark: '有线' }
  ],
  cpu: '',
  memory: '',
  disk: '',
  serial_number: '',
  remark: ''
})

const validateMac = (_rule: any, _value: any, callback: any) => {
  const macRegex = /^[A-F0-9]{12}$/
  for (const mac of form.mac_addresses) {
    if (mac.mac && !macRegex.test(mac.mac)) {
      callback(new Error('MAC地址必须为12位大写字母或数字'))
      return
    }
  }
  callback()
}

const rules = {
  machine_model: [{ required: true, message: '请输入机器型号', trigger: 'blur' }],
  machine_type: [{ required: true, message: '请选择机器类型', trigger: 'change' }],
  mac_addresses: [{ validator: validateMac, trigger: 'blur' }]
}

function addMac() {
  form.mac_addresses.push({ mac: '', remark: '有线' })
}

function removeMac(index: number) {
  form.mac_addresses.splice(index, 1)
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  for (const mac of form.mac_addresses) {
    if (mac.mac && mac.mac.length !== 12) {
      ElMessage.error('MAC地址必须为12位字符')
      return
    }
  }

  submitting.value = true
  try {
    const validMacs = form.mac_addresses.filter(m => m.mac.trim())
    await store.createAsset({
      machine_model: form.machine_model,
      machine_type: form.machine_type,
      asset_code: form.asset_code || undefined,
      mac_addresses: validMacs,
      cpu: form.cpu || undefined,
      memory: form.memory || undefined,
      disk: form.disk || undefined,
      serial_number: form.serial_number || undefined,
      remark: form.remark || undefined,
      operator: currentUser.value
    })
    ElMessage.success('入库成功')
    router.push('/assets')
  } catch (error: any) {
    ElMessage.error(error.message || '入库失败')
  } finally {
    submitting.value = false
  }
}

async function handleDownloadTemplate() {
  try {
    await store.downloadTemplate()
    ElMessage.success('模板下载成功')
  } catch (error: any) {
    ElMessage.error(error.message || '模板下载失败')
  }
}

function handleFileChange(file: any) {
  selectedFile.value = file.raw
  importResult.value = null
}

function handleFileRemove() {
  selectedFile.value = null
  importResult.value = null
}

async function handleImport() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  importing.value = true
  try {
    const result = await store.importAssets(selectedFile.value)
    importResult.value = result
    if (result.failed === 0) {
      ElMessage.success(`成功导入 ${result.success} 条资产`)
    } else {
      ElMessage.warning(`导入完成，成功 ${result.success} 条，失败 ${result.failed} 条`)
    }
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.mac-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.import-tabs {
  margin-top: 8px;
}

.excel-import {
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.excel-import :deep(.el-alert) {
  width: 100%;
  max-width: 800px;
}

.excel-import :deep(.el-alert__description) {
  text-align: center;
}

.error-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.error-item {
  padding: 8px 12px;
  margin-bottom: 4px;
  background-color: #fef0f0;
  border-radius: 4px;
  color: #f56c6c;
}
</style>
