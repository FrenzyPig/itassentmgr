<template>
  <div id="app">
    <div v-if="user" class="app-header">
      <div class="header-left">
        <h3>资产管理系统</h3>
      </div>
      <div class="header-right">
        <span class="user-info">{{ user.username }} ({{ user.is_admin ? '管理员' : '用户' }})</span>
        <el-dropdown @command="handleCommand">
          <el-button type="primary" size="small">
            操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
              <el-dropdown-item v-if="user.is_admin" command="userManagement">用户管理</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    <router-view />
    
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { authApi, type User } from './api/auth'

const router = useRouter()
const route = useRoute()

const user = ref<User | null>(null)
const showPasswordDialog = ref(false)
const passwordLoading = ref(false)
const passwordFormRef = ref()

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 1, message: '新密码不能为空', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const checkUserLogin = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      user.value = JSON.parse(userStr)
    } catch {
      localStorage.removeItem('user')
      user.value = null
      if (route.path !== '/login') {
        router.push('/login')
      }
    }
  } else {
    user.value = null
    if (route.path !== '/login') {
      router.push('/login')
    }
  }
}

onMounted(() => {
  checkUserLogin()
})

watch(() => route.path, () => {
  checkUserLogin()
})

const handleCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await authApi.logout()
      localStorage.removeItem('user')
      user.value = null
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (error) {
      localStorage.removeItem('user')
      router.push('/login')
    }
  } else if (command === 'changePassword') {
    showPasswordDialog.value = true
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } else if (command === 'userManagement') {
    router.push('/users')
  }
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    passwordLoading.value = true
    try {
      const res: any = await authApi.changePassword({
        oldPassword: passwordForm.oldPassword,
        newPassword: passwordForm.newPassword
      })
      
      if (res.success) {
        ElMessage.success('密码修改成功')
        showPasswordDialog.value = false
      } else {
        ElMessage.error(res.message || '修改失败')
      }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '修改失败')
    } finally {
      passwordLoading.value = false
    }
  })
}
</script>

<style>
* {
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
}

#app {
  background-color: #f5f5f5;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

.header-left h3 {
  margin: 0;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  color: #666;
  font-size: 14px;
}

.el-card {
  width: 100%;
  box-sizing: border-box;
}

.el-table {
  width: 100% !important;
}
</style>
