import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Asset, AssetSimple, AssetFilters, Pagination } from '../types'
import { assetApi } from '../api/asset'

export const useAssetStore = defineStore('asset', () => {
  const assets = ref<AssetSimple[]>([])
  const currentAsset = ref<Asset | null>(null)
  const pendingAssets = ref<AssetSimple[]>([])
  const loading = ref(false)

  const pagination = ref<Pagination>({
    page: 1,
    pageSize: 20,
    total: 0
  })

  const filters = ref<AssetFilters>({})

  const hasPendingAssets = computed(() => pendingAssets.value.length > 0)

  async function fetchAssets() {
    loading.value = true
    try {
      const res: any = await assetApi.getList({
        page: pagination.value.page,
        pageSize: pagination.value.pageSize,
        ...filters.value
      })
      if (res.code === 200) {
        assets.value = res.data.items
        pagination.value.total = res.data.total
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchAssetById(id: string) {
    loading.value = true
    try {
      const res: any = await assetApi.getById(id)
      if (res.code === 200) {
        currentAsset.value = res.data
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchPendingAssets() {
    const res: any = await assetApi.getPending()
    if (res.code === 200) {
      pendingAssets.value = res.data
    }
  }

  async function createAsset(data: any) {
    const res: any = await assetApi.create(data)
    if (res.code === 200) {
      await fetchAssets()
      await fetchPendingAssets()
      return res.data
    }
    throw new Error(res.message)
  }

  async function claimAsset(id: string, data: any) {
    const res: any = await assetApi.claim(id, data)
    if (res.code === 200) {
      currentAsset.value = res.data
      await fetchAssets()
      await fetchPendingAssets()
      return res.data
    }
    throw new Error(res.message)
  }

  async function retireAsset(id: string, operator?: string) {
    const res: any = await assetApi.retire(id, operator)
    if (res.code === 200) {
      currentAsset.value = res.data
      await fetchAssets()
      return res.data
    }
    throw new Error(res.message)
  }

  async function returnToStorage(id: string, operator?: string) {
    const res: any = await assetApi.returnToStorage(id, operator)
    if (res.code === 200) {
      currentAsset.value = res.data
      await fetchAssets()
      await fetchPendingAssets()
      return res.data
    }
    throw new Error(res.message)
  }

  async function deleteAsset(id: string, operator?: string) {
    const res: any = await assetApi.delete(id, operator)
    if (res.code === 200) {
      await fetchAssets()
      await fetchPendingAssets()
    }
  }

  function setFilters(newFilters: AssetFilters) {
    filters.value = newFilters
    pagination.value.page = 1
  }

  function setPage(page: number) {
    pagination.value.page = page
  }

  function clearCurrentAsset() {
    currentAsset.value = null
  }

  async function downloadTemplate() {
    const res: any = await assetApi.downloadTemplate()
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '资产导入模板.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  async function importAssets(file: File) {
    const res: any = await assetApi.importAssets(file)
    if (res.code === 200) {
      await fetchAssets()
      await fetchPendingAssets()
      return res.data
    }
    throw new Error(res.message)
  }

  return {
    assets,
    currentAsset,
    pendingAssets,
    loading,
    pagination,
    filters,
    hasPendingAssets,
    fetchAssets,
    fetchAssetById,
    fetchPendingAssets,
    createAsset,
    claimAsset,
    retireAsset,
    returnToStorage,
    deleteAsset,
    setFilters,
    setPage,
    clearCurrentAsset,
    downloadTemplate,
    importAssets
  }
})
