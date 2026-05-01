import axios from 'axios'
import router from '../router'

const api = axios.create({
    baseURL: '/api',
    timeout: 10000,
    withCredentials: true
})

api.interceptors.response.use(
    response => response.data,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('user')
            router.push('/login')
        }
        return Promise.reject(error)
    }
)

export default api
