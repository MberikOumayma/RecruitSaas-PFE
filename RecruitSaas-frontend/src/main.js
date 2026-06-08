import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import './style.css'
import { createPinia } from 'pinia' // 1. Import Pinia

const app = createApp(App)
const pinia = createPinia() // 2. Create the instance

app.use(pinia)
app.use(router)
app.mount('#app')
