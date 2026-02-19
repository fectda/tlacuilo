import { createRouter, createWebHistory } from 'vue-router'
import CommandCenter from '../views/CommandCenter.vue'
import ProjectDigital from '../views/ProjectDigital.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'Home',
            component: CommandCenter
        },
        {
            path: '/project/:collection/:slug',
            name: 'ProjectDigital',
            component: ProjectDigital
        }
    ]
})

export default router
