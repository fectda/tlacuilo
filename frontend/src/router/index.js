import { createRouter, createWebHistory } from 'vue-router'
import CommandCenter from '../views/CommandCenter.vue'
import ProjectDigital from '../views/ProjectDigital.vue'
import ProjectStudio from '../views/ProjectStudio.vue'

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
        },
        {
            path: '/project/:collection/:slug/studio',
            name: 'ProjectStudio',
            component: ProjectStudio
        }
    ]
})

export default router
