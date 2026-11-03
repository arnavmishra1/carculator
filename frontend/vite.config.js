import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  // Relative asset paths, so the build works from any folder, such as
  // https://<user>.github.io/carculator/ on GitHub Pages.
  base: './',
})
