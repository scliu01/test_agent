import { createRouter, createWebHistory } from 'vue-router';
import ProjectView from '../views/ProjectView.vue';
import AgentView from '../views/AgentView.vue';

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/', // 默认路由地址
			// 重定向到项目页面
			redirect: '/project',
		},
		{
			path: '/project', // 路由地址
			name: 'project', // 路由名称
			// 直接加载，在项目启动时就会加载，首页上使用的内容就应该直接加载，可以提升响应时间
			component: ProjectView,
		},
		{
			path: '/main', // 路由地址
			name: 'main', // 路由名称
			// 直接加载，在项目启动时就会加载，首页上使用的内容就应该直接加载，可以提升响应时间
			component: () => import('../views/MainView.vue'),
			children: [
				{
					path: '', // 嵌套路由默认地址
					name: 'agent',
					component: AgentView,
				},
				{
					path: 'test_data_template', // 嵌套路由默认地址
					name: 'test_data_template',
					component: () => import('../views/TestDataTemplateView.vue'),
				},
				{
					path: 'document', // 嵌套路由默认地址
					name: 'document',
					component: () => import('../views/document/DocumentView.vue'),
				},
				{
					path: 'api_document', // 嵌套路由默认地址
					name: 'api_document',
					component: () => import('../views/api_document/ApiDocumentView.vue'),
				},
				{
					path: 'test_case', // 嵌套路由默认地址
					name: 'test_case',
					component: () => import('../views/TestCaseView.vue'),
				},
				{
					path: 'api_test_case', // 嵌套路由默认地址
					name: 'api_test_case',
					component: () => import('../views/ApiTestCaseView.vue'),
				},
				{
					path: 'api_test_case_exec', // 嵌套路由默认地址
					name: 'api_test_case_exec',
					component: () => import('../views/api_testcase_exec/ApiTestCaseExecView.vue'),
				},
				{
					path: 'api_exec_record', // 嵌套路由默认地址
					name: 'api_exec_record',
					component: () => import('../views/api_testcase_exec/ApiExecRecordView.vue'),
				},
				{
					path: 'test_case_exec', // 嵌套路由默认地址
					name: 'test_case_exec',
					component: () => import('../views/testcase_exec/TestCaseExecView.vue'),
				},
				{
					path: 'exec_record', // 嵌套路由默认地址
					name: 'exec_record',
					component: () => import('../views/testcase_exec/ExecRecordView.vue'),
				},
				{
					path: 'performance', // 嵌套路由默认地址
					name: 'performance',
					component: () => import('../views/PerformanceView.vue'),
				},
			],
		},
		{
			path: '/about',
			name: 'about',
			// route level code-splitting
			// this generates a separate chunk (About.[hash].js) for this route
			// which is lazy-loaded when the route is visited.
			// 懒加载，只有当页面的时候才会加载，当页面不在首页显示时候，就使用懒，可以减轻服务器压力
			component: () => import('../views/AboutView.vue'),
		},
	],
});

export default router;
