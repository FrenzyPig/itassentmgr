<template>
  <div class="user-management">
    <el-button @click="$router.back()">返回</el-button>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showAddDialog = true">
            添加用户
          </el-button>
        </div>
      </template>
      
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="is_admin" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'danger' : 'success'" size="small">
              {{ row.is_admin ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_banned" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_banned ? 'danger' : 'success'" size="small">
              {{ row.is_banned ? '已禁用' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="!row.is_admin" 
              type="warning" 
              size="small" 
              @click="toggleBan(row)"
            >
              {{ row.is_banned ? '启用' : '禁用' }}
            </el-button>
            <el-button 
              v-if="!row.is_admin" 
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchUsers"
          @size-change="fetchUsers"
        />
      </div>
    </el-card>
    
    <el-dialog v-model="showAddDialog" title="添加用户" width="400px">
      <el-form :model="addForm" :rules="addRules" ref="addFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="addForm.username" 
            placeholder="请输入用户名（仅英文）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" :loading="addLoading" @click="handleAdd">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi, type User } from '../api/auth'

const users = ref<User[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const showAddDialog = ref(false)
const addLoading = ref(false)
const addFormRef = ref()

const addForm = reactive({
  username: ''
})

const addRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { pattern: /^[a-zA-Z]+$/, message: '用户名只能包含英文字母', trigger: 'blur' }
  ]
}

onMounted(() => {
  fetchUsers()
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const res: any = await userApi.getList({
      page: page.value,
      pageSize: pageSize.value
    })
    
    if (res.success) {
      users.value = res.data.items
      total.value = res.data.total
    }
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = async () => {
  if (!addFormRef.value) return
  
  await addFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    addLoading.value = true
    try {
      const res: any = await userApi.create({
        username: addForm.username
      })
      
      if (res.success) {
        ElMessage.success(res.message || '用户创建成功')
        showAddDialog.value = false
        addForm.username = ''
        fetchUsers()
      } else {
        ElMessage.error(res.message || '创建失败')
      }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '创建失败')
    } finally {
      addLoading.value = false
    }
  })
}

const toggleBan = async (user: User) => {
  const action = user.is_banned ? '启用' : '禁用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${user.username}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res: any = user.is_banned 
      ? await userApi.unban(user.id)
      : await userApi.ban(user.id)
    
    if (res.success) {
      ElMessage.success(res.message || `${action}成功`)
      fetchUsers()
    } else {
      ElMessage.error(res.message || `${action}失败`)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || `${action}失败`)
    }
  }
}

const handleDelete = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res: any = await userApi.delete(user.id)
    
    if (res.success) {
      ElMessage.success('删除成功')
      fetchUsers()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.user-management {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
