import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/assets'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../pages/Login.vue')
    },
    {
      path: '/users',
      name: 'user-management',
      component: () => import('../pages/UserManagement.vue')
    },
    {
      path: '/assets',
      name: 'asset-list',
      component: () => import('../pages/AssetList.vue')
    },
    {
      path: '/assets/:id',
      name: 'asset-detail',
      component: () => import('../pages/AssetDetail.vue')
    },
    {
      path: '/import',
      name: 'asset-import',
      component: () => import('../pages/AssetImport.vue')
    },
    {
      path: '/claim',
      name: 'asset-claim',
      component: () => import('../pages/AssetClaim.vue')
    },
    {
      path: '/change',
      name: 'asset-change',
      component: () => import('../pages/AssetChange.vue')
    },
    {
      path: '/logs',
      name: 'operation-log',
      component: () => import('../pages/OperationLog.vue')
    }
  ]
})

export default router
