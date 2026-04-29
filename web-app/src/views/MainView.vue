<template>
    <div class="common-layout">
        <el-container>
            <el-header height="80px">
                <div class="logo-container">
                    <img class="logo" src="/logo.png" alt="AI测试工具">
                    <span>AI测试工具+{{ agentName }}</span>
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
                            © 2026 智能体 - 软件测试工具开发
                        </el-text>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="24" justify="center" align="middle">
                        <el-text>
                            湘ICP备2026010903号
                        </el-text>
                    </el-col>
                </el-row>
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
/* 最外层容器固定高度，干掉全局滚动条 */
.el-container {
    height: 100vh !important;
    overflow: hidden !important;
    display: flex;
    flex-direction: column;
}

/* Header固定80px，永不压缩 */
.el-header {
    background-color: #222529;
    height: 80px !important;
    flex-shrink: 0;
    display: flex;
    align-items: center;
}

/* ✨ Main：填充剩下所有高度，不多不少！ */
.el-main {
    flex: 1 !important;
    height: calc(100vh - 80px - 80px) !important;
    overflow: hidden !important;
    padding: 0 !important;
}

.main-container {
    width: 100%;
    height: 100%;
    overflow: hidden;
}

/* Footer固定80px，永不压缩 */
.el-footer {
    flex-shrink: 0;
    height: 50px !important;
    background-color: #f5f7fa;
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
    flex-basis: 0 !important;
    padding: 10px;
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