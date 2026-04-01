import { fileURLToPath, URL } from 'node:url';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';
import WindiCSS from 'vite-plugin-windicss';

// https://vite.dev/config/
export default defineConfig({
	define: {
		__VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
	},
	// plugins: [vue(), vueDevTools(), WindiCSS()],
	plugins: [vue(), WindiCSS()],
	resolve: {
		alias: {
			'@': fileURLToPath(new URL('./src', import.meta.url)),
		},
	},

	// // 生产环境关键配置
    // define: {
    //   __VUE_PROD_DEVTOOLS__: false, // 彻底禁用 devtools
    //   __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
    // },
	build: {
		outDir: 'dist', // 打包输出目录
		assetsDir: 'static', // 静态资源目录
		sourcemap: false, // 关闭 sourcemap（安全！）
		minify: 'terser', // 代码压缩
		terserOptions: {
			compress: {
			drop_console: true, // 生产删除 console.log
			drop_debugger: true // 删除 debugger
			}
		},
		chunkSizeWarningLimit: 1500, // 取消打包体积警告
	},

	server: {
		allowedHosts: ['www.agentscl.cn'],
		host: '0.0.0.0',
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:5001',
				// target: 'http://8.162.0.206:5001',
				// target: 'http://www.agentscl.cn:5001',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api/, ''),
			},
		},
	},
});
