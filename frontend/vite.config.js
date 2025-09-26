// import { defineConfig } from 'vite'
// import vue from '@vitejs/plugin-vue'

// // https://vite.dev/config/
// export default defineConfig({
//   base: '/',
//   // base: '/portal/',
//   plugins: [vue()],
// })
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  // base: '/portal/',
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173
  }
})
