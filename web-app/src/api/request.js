import axios from 'axios';
// import { ref } from 'vue';
// import { ElLoading, ElMessage, ElNotification } from 'element-plus';
import { ElMessage } from 'element-plus';

// 创建axios实例
const service = axios.create({
	// 设置服务器地址和端口号
	// baseURL: 'http://127.0.0.1:5001',
	// baseURL: 'http://8.162.0.206:5001',
	baseURL: 'http://www.agentscl.cn:5001',
	// 生产环境：同域名部署，使用相对路径，无跨域无OPTIONS预请求
	baseURL: '/api',
});

// 注释后关闭请求拦截和响应拦截
// const nums = ref(0);
// const loading = ref(null);

// function open() {
// 	if (nums.value <= 0) {
// 		loading.value = ElLoading.service({
// 			lock: true,
// 			text: '加载中',
// 			background: 'rgba(0, 0, 0, 0.05)',
// 		});
// 	}
// 	nums.value++; // 记录数值加一
// }

// function close() {
// 	nums.value--; // 记录数值减1
// 	if (nums.value <= 0) {
// 		nums.value = 0;
// 		loading.value.close();
// 	}
// }
// 不需要token校验的接口白名单
const whiteList = [
	'/project/queryAll',
	'/project/openProject',
	'/project/insert',
];

// 添加请求拦截器
service.interceptors.request.use(
	(config) => {
		// open();//开启拦截
		// 不在白名单中的接口，自动添加Authorization token
		if (!whiteList.some(url => config.url.includes(url))) {
			const token = localStorage.getItem('access_token');
			if (token) {
				config.headers.Authorization = `Bearer ${token}`;
			}
		}
		return config;
	},
	(error) => {
		// close();
		ElMessage.error('网络异常，请稍后再试');
		return Promise.reject(error);
	}
);

// 添加响应拦截器
service.interceptors.response.use(
	(response) => {
		// close();//开启拦截
		// 打印请求信息以便调试
		// console.log('请求成功:', response);
		return response;
	},
	(error) => {
		// close();
		// 打印错误信息以便调试
		console.log('请求失败:', {
			url: error.config?.url,
			method: error.config?.method,
			error: error.message,
			response: error.response?.data,
		});
		// ElMessage.error(`网络异常:${error.message || '未知错误'}, 状态码:${error.response?.status || 'undefined'}`);
		return Promise.reject(error);
	}
);

export default service;
