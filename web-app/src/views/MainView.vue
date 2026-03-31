<template>
    <div class="common-layout">
        <el-container>
            <el-header height="80px">
                <div class="logo-container">
                    <img class="logo" src="/logo.png" alt="AI测试平台">
                    <span>AI测试平台+{{ agentName }}</span>
                </div>
                <div>
                    <el-text class="project-name">
                        {{ projectName }}
                    </el-text>
                    <el-text class="project-name" @click="goBack()">
                        退出项目
                    </el-text>
                </div>
            </el-header>
            <el-main>
                <div class="main-container">
                    <router-view></router-view>
                </div>
            </el-main>
            <!-- 底部 -->
            <el-footer>
                <el-row>
                    <el-col :span="24" justify="center" align="middle">
                        <el-text>
                            © 2025 智能体 - 智能体工具开发
                        </el-text>
                    </el-col>
                </el-row>
                <!-- <el-row>
                    <el-col :span="24" justify="center" align="middle">
                        <el-text>
                            
                        </el-text>
                    </el-col>
                </el-row> -->
            </el-footer>
        </el-container>
    </div>
</template>
<script setup>
import { House, Edit, Delete } from '@element-plus/icons-vue';
import { onBeforeMount, onMounted, ref } from 'vue';
import api from '../api/projects_api.js'
import router from '@/router';

let projectName = ref('项目1');
let agentName = ref('智能体');
// onMounted(() => {
//     console.log('项目加载完成');
// });
// onBeforeMount(() => {
//     console.log('项目加载开始');
// });
// onMounted页面加载完成Vue会自动调用的函数
onMounted(async () => {
    // 当页面加载成功后，取出前面保存的project_id
    let project_id = sessionStorage.getItem("project_id")
    // 判断是否成功取到project_id
    if (project_id) {
        // 成功取到后，进行接口访问
        let res = await api.queryById(project_id)
        console.log("onMounted res", res)
        const res_data = res.data
        const { code, data } = res_data
        if (code == 200) {
            projectName.value = data.name
        }
    }
    // 通过id去后台请求项目信息
    // 将需要的信息显示在页面上
})
function goBack() {
    // 删除sessionStorage中的project_id
    sessionStorage.removeItem("project_id")
    // 跳转到项目列表页面
    router.replace('/project')
}
</script>
<style scoped>
.el-container {
    /* vh 100% 浏览器可见区域高度 */
    height: 100vh;
}

/* 样式重写 */
.el-header {
    background-color: #222529;
    /* height: 80px; */
    /* 设置弹性盒子 */
    display: flex;
    /* 设置元素垂直居中 */
    align-items: center;
}

.logo-container {
    width: 100%;
    display: flex;
    align-items: center;
    /* 字体颜色 */
    color: white;
    /* 字段大小 */
    font-size: 26px;
    /* 字体加粗 */
    font-weight: bold;
    /* 离左边间隔100px */
    margin-left: 100px;
}

.logo-container>.logo {
    margin-right: 10px;
    width: 40px;
    height: 40px;
}

.el-main {
    flex: 1;
}


.main-container>.el-row {
    width: 100%;
    height: 100%;
    padding-left: 60px;
    padding-right: 60px;
}

.main-container>.el-row>.el-col {
    padding-bottom: 20px;
}

.el-header div {
    /* 最小宽度500px */
    min-width: 500px;
}

.project-name {
    color: white;
    font-size: 16px;
    cursor: pointer;
    padding-left: 20px;
    padding-right: 20px;
}

.project-name:hover {
    color: #409eff;
}
</style>