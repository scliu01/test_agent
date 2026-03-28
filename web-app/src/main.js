import { createApp } from 'vue';
// 导入ElementPlus
import ElementPlus from 'element-plus';
// 导入ElementPlus的中文配置，其它的语言也可以有对应的导入
import zhCn from 'element-plus/dist/locale/zh-cn.mjs';
// 导入了ElementPlus的样式
import 'element-plus/dist/index.css';
// 导入了ElementPlus的icon图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue';
// 导入App，也就是页面的入口
import App from './App.vue';
// 导入路由文件
import router from './router';
// echarts是数据图形，比如饼图、柱状图等
import * as echarts from 'echarts';
// 创建vue对象
const app = createApp(App);
// 加载路由配置
app.use(router);
// 加载ElementPlus
app.use(ElementPlus, {
	locale: zhCn,
});
// 加载ElementPlus的Icon，固定写法
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
	app.component(key, component);
}

app.config.globalProperties.$echarts = echarts; // 挂载到全局
// 将app对象与index.html的id=app元素挂载
app.mount('#app');
