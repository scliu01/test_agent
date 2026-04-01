<template>
    <div class="common-layout">
        <el-container>
            <el-header height="80px">
                <div class="logo-container">
                    <img class="logo" src="/logo.png" alt="华测教育">
                    <span>AI测试平台</span>
                </div>
            </el-header>
            <el-main>
                <div class="main-container">
                    <el-row :gutter="20">
                        <!-- @click：绑定点击事件 -->
                        <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" @click="handleAdd">
                            <el-card class="project-card add-card" shadow="hover">
                                <div class="add-card-content">
                                    <el-icon :size="48">
                                        <Plus />
                                    </el-icon>
                                    <p>添加新项目</p>
                                </div>
                            </el-card>
                        </el-col>

                        <!-- 项目卡片 -->
                        <el-col v-for="item in all_data" :xs="24" :sm="12" :md="8" :lg="6" :xl="6">
                            <el-card class="project-card" shadow="hover">
                                <template #header>
                                    <div class="card-header">
                                        <h3>{{ item.name }}</h3>
                                        <span class="create-time">{{ item.created_at }}</span>
                                    </div>
                                </template>

                                <div class="card-body">
                                    <p class="description">{{ item.description }}</p>
                                </div>

                                <div class="card-footer">
                                    <el-button type="primary" size="small" :icon="House"
                                        @click="handleEnter(item.id, item.password)">
                                        进入项目
                                    </el-button>

                                    <el-button type="info" size="small" :icon="Edit"
                                        @click="handleEdit(item.id, item.password)">
                                        编辑
                                    </el-button>

                                    <el-button type="danger" size="small" :icon="Delete"
                                        @click="handleDelete(item.id, item.password)">
                                        删除
                                    </el-button>
                                </div>
                            </el-card>
                        </el-col>
                    </el-row>
                </div>
            </el-main>
            <!-- 底部 -->
            <el-footer>
                <el-row>
                    <el-col :span="24" justify="center" align="middle">
                        <el-text>
                            © 2026 智能体 - AI测试工具开发
                        </el-text>
                    </el-col>
                </el-row>
                <!-- <el-row>
                    <el-col :span="24" justify="center" align="middle">
                        <el-text>
                            XXXXX
                        </el-text>
                    </el-col>
                </el-row> -->
            </el-footer>
        </el-container>
    </div>
    <el-dialog v-model="addDialogVisible" :title="addBean.id ? '编辑项目' : '添加项目'" width="600">
        <el-form :model="addBean" label-width="auto">
            <el-form-item label="项目名称" prop="name" required>
                <el-input v-model="addBean.name" placeholder="请输入项目名称" />
            </el-form-item>
            <el-form-item label="项目描述" prop="description">
                <el-input v-model="addBean.description" type="textarea" :rows="3" placeholder="请输入项目描述（可选）" />
            </el-form-item>
            <el-form-item label="密码" prop="password" required>
                <el-input v-model="addBean.password" type="password" placeholder="请输入密码" />
            </el-form-item>
            <el-form-item label="大语言模型URL" prop="llm_url" required>
                <el-input v-model="addBean.llm_url" placeholder="请输入大模型API URL" />
            </el-form-item>
            <el-form-item label="语言模型API Key" prop="llm_key" required>
                <el-input v-model="addBean.llm_key" placeholder="请输入大模型API Key" />
            </el-form-item>
            <el-form-item label="语言模型名称" prop="llm_model" required>
                <el-input v-model="addBean.llm_model" placeholder="请输入模型名称" />
            </el-form-item>
            <el-form-item label="视觉语言模型 URL" prop="lvm_url" required>
                <el-input v-model="addBean.lvm_url" placeholder="请输入大模型API URL" />
            </el-form-item>
            <el-form-item label="视觉语言模型API Key" prop="lvm_key" required>
                <el-input v-model="addBean.lvm_key" placeholder="请输入大模型API Key" />
            </el-form-item>
            <el-form-item label="视觉语言模型名称" prop="lvm_model" required>
                <el-input v-model="addBean.lvm_model" placeholder="请输入模型名称" />
            </el-form-item>
        </el-form>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="addDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="handleSave">
                    {{ addBean.id ? '更新' : '创建' }}
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>
<script setup>
import { House, Edit, Delete } from '@element-plus/icons-vue';
import { reactive, ref } from 'vue';
import api from '@/api/projects_api.js';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router'

// axios使用不同方法去做不同请求，不能弄错了
// axios.get('http://localhost:5001/project/queryAll')
//     // .then()就是处理请求成功的函数
//     .then((response) => {
//         console.log(response);
//     })
//     // .catch()就是处理请求失败的函数
//     .catch((error) => {
//         console.log(error);
//     });
// 保存所有项目数据
let all_data = ref([]);
async function loadData() {
    // await 等待异步操作完成，简单点说就是你给我等着
    const response = await api.queryAll();
    console.log(response);
    // 获取响应数据
    const res_data = response.data;
    if (res_data.code == 200) {
        // ref 数据类型，在js中修改值时必须通过ref.value 赋值
        all_data.value = res_data.data;
    } else {
        console.log('请求失败');
    }
}

loadData()

let addDialogVisible = ref(false);


// 表单数据
const addBean = ref({
    name: '',
    description: '',
    password: '',
    llm_url: '',
    llm_key: '',
    llm_model: '',
    lvm_url: '',
    lvm_key: '',
    lvm_model: ''
})

/**
 * 添加项目
 */
const handleSave = async () => {
    if (!addBean.value.name) {
        ElMessage.error('请输入项目名称');
        return;
    }
    // if (!addBean.value.password) {
    //     ElMessage.error('请输入密码');
    //     return;
    // }
    // 隐藏弹窗
    addDialogVisible.value = false;
    let res = undefined
    // 提交表单数据到服务器
    if (addBean.value.id) {
        // 编辑
        res = await api.update(addBean.value)
    } else {
        // 添加
        res = await api.insert(addBean.value)
    }
    const res_data = res.data;
    if (res_data.code == 200) {
        ElMessage.success(addBean.value.id ? '更新成功' : '添加成功');
        // 自动刷新数据
        loadData();
    } else {
        ElMessage.success(addBean.value.id ? '更新失败' : '添加失败');
    }
}
/**
 * 编辑项目
 */
async function handleEdit(id, password) {
    if (!await checkPass(password)) {
        ElMessage.error('密码错误');
        return;
    }
    // 调用查询接口，获取最新的项目数据信息
    const res = await api.queryById(id)
    // 获取响应数据
    const res_data = res.data
    // 取出res_data的code和data属性
    const { code, data } = res_data
    // code为200表示成功，这个是由开发人员设计的
    if (code == 200) {
        addDialogVisible.value = true
        addBean.value = data
    }
}

function handleAdd() {
    addDialogVisible.value = true
    addBean.value = {
        name: '',
        description: '',
        password: '',
        llm_url: '',
        llm_key: '',
        llm_model: '',
        lvm_url: '',
        lvm_key: '',
        lvm_model: ''
    }
}

/**
 * 删除项目
 */
async function handleDelete(id, password) {
    if (!await checkPass(password)) {
        ElMessage.error('密码错误');
        return;
    }
    // 删除项目
    const res = await api.deleteById(id)
    // 获取响应数据
    const res_data = res.data
    // 获取响应数据
    const { code, data } = res_data
    // code为200表示成功，这个是由开发人员设计的
    if (code == 200) {
        ElMessage.success('删除成功');
        // 自动刷新数据
        loadData();
    } else {
        ElMessage.success('删除失败');
    }
}

const router = useRouter()
/**
 * 进入项目
 */
async function handleEnter(id, password) {
    if (!await checkPass(password)) {
        ElMessage.error('密码错误');
        return;
    }
    sessionStorage.setItem('project_id', id)
    // 使用router进行路由跳转
    router.push('/main')
}

/**
 * 检查密码
 * @param password 项目的密码
 */
async function checkPass(password) {
    try {
        // 输入密码的提示框
        const { value } = await ElMessageBox.prompt('请输入项目密码', '验证', {
            inputType: 'password',
            confirmButtonText: '确认',
            cancelButtonText: '取消',
            inputPlaceholder: '请输入密码'
        })

        return password === value
    } catch (error) {
        return false
    }
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
    flex-basis: 0 !important;
    padding: 10px;
}


.main-container>.el-row {
    width: 100%;
    padding-left: 60px;
    padding-right: 60px;
}

.main-container>.el-row>.el-col {
    padding-bottom: 20px;
}

.project-card {
    border-radius: 12px;
    transition: all 0.3s ease;
    transform: translateY(20px);
    animation: cardAppear 0.4s ease forwards;
    animation-delay: calc(var(--animation-order) * 0.1s);
    border-top: 4px solid var(--el-color-primary);
    height: 100%;
    display: flex;
    flex-direction: column;
}

.project-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.add-card {
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background-color: #f5f7fa;
    border-top: 4px dashed var(--el-color-primary);
    min-height: 200px;
}

.add-card-content {
    text-align: center;
    color: var(--el-color-primary);
    padding: 20px;
}

.add-card-content i {
    margin-bottom: 10px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header h3 {
    margin: 0;
    font-size: 18px;
    color: var(--el-text-color-primary);
}

.create-time {
    font-size: 12px;
    color: var(--el-text-color-secondary);
}

.description {
    margin: 0;
    color: var(--el-text-color-regular);
    min-height: 60px;
    flex-grow: 1;
    text-align: left;
    /* 明确设置为左对齐 */
    display: block;
    /* 确保是块级元素，默认就是从左上开始排列 */
}

.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 15px;
    border-top: 1px solid var(--el-border-color-light);
}

@keyframes cardAppear {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>