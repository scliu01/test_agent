<template>
    <el-container>
        <el-row style="width: 100%;">
            <el-main>

                <!-- 查询区域布局 -->
                <el-card class="query-card">
                    <el-form :inline="true" :model="queryParams">
                        <el-form-item label="用例名称">
                            <el-input v-model="queryParams.name" placeholder="请输入用例名称" clearable
                                @keyup.enter="loadTestCases" />
                        </el-form-item>
                        <el-form-item label="优先级">
                            <el-select v-model="queryParams.priority" placeholder="请选择优先级" style="width: 200px;">
                                <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label"
                                    :value="item.value" />
                            </el-select>


                        </el-form-item>
                        <el-form-item label="指定模块">
                            <el-tree-select v-model="queryParams.module_ids" :data="menuData" multiple collapse-tags
                                :render-after-expand="false" style="width: 240px" node-key="id" />

                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" @click="loadTestCases()">
                                <el-icon>
                                    <search />
                                </el-icon>
                                查询
                            </el-button>
                            <el-button @click="resetQuery">
                                <el-icon>
                                    <refresh />
                                </el-icon>
                                重置
                            </el-button>
                        </el-form-item>
                    </el-form>
                </el-card>
                <el-card>
                    <template #header>
                        <div class="card-header">
                            <!-- 操作按钮区域 -->
                            <!-- 操作按钮区域 居右-->
                            <div class="action-buttons">
                                <el-select v-model="tmp_exec_type" placeholder="选择用例类型">
                                    <el-option label="HTTP 接口" value="http" selected />
                                </el-select>
                                <el-button type="primary" @click="handlePreparedTask"> 创建 AI 测试任务 </el-button>
                                <el-button type="warning" @click="handleExecHistory">
                                    AI 测试执行记录
                                </el-button>
                            </div>
                        </div>
                    </template>

                    <el-scrollbar height="500px">
                        <el-table v-loading="loading" :data="testcaseList" border stripe ref="tableRef"
                            :row-key="getRowKey">
                            <el-table-column type="selection" width="40" align="center" :reserve-selection="true" />
                            <el-table-column label="ID" prop="id" width="60" align="center" />
                            <el-table-column label="优先级" prop="priority" width="80" align="center">
                            </el-table-column>
                            <el-table-column label="用例名称" prop="name" min-width="180">
                                <template #default="{ row }">
                                    <el-button link type="primary" @click="handleView(row)">
                                        {{ row.name }}
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-scrollbar>
                    <!-- 分页 -->
                    <div class="pagination-container">
                        <el-pagination v-model:current-page="queryParams.page" v-model:page-size="queryParams.pageSize"
                            :page-sizes="[10, 20, 30, 50]" layout="total, sizes, prev, pager, next, jumper"
                            :total="total" @size-change="handleSizeChange" @current-change="handleCurrentChange" />
                    </div>
                </el-card>
            </el-main>
        </el-row>
    </el-container>

    <!-- 查看测试用例对话框 -->
    <el-dialog v-model="viewDialogVisible" title="用例详情" width="800px">
        <el-descriptions :column="1" label-width="80" border>
            <el-descriptions-item label="用例名称"><span style="white-space: pre-wrap;">{{ addOrEditForm.name }}</span></el-descriptions-item>
            <el-descriptions-item label="优先级">
                <el-tag :type="handlePriorityType(addOrEditForm.priority)">
                    {{ addOrEditForm.priority }}
                </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="前置条件"><span style="white-space: pre-wrap;">{{ addOrEditForm.precondition }}</span></el-descriptions-item>
        </el-descriptions>
        <el-divider></el-divider>
        <el-descriptions title="接口请求参数" :column="1" label-width="80" border>
            <el-descriptions-item v-if='addOrEditForm.steps["path"]' label="接口路径">{{ addOrEditForm.steps["path"]
            }}</el-descriptions-item>
            <el-descriptions-item v-if='addOrEditForm.steps["method"]' label="请求方式">{{ addOrEditForm.steps["method"]
            }}</el-descriptions-item>
            <el-descriptions-item v-if='addOrEditForm.steps["params"]' label="URL参数">{{ addOrEditForm.steps["params"]
            }}</el-descriptions-item>
            <el-descriptions-item v-if='addOrEditForm.steps["data"]' label="FORM">{{ addOrEditForm.steps['data']
            }}</el-descriptions-item>
            <el-descriptions-item v-if='addOrEditForm.steps["json"]' label="JSON">{{ addOrEditForm.steps["json"]
            }}</el-descriptions-item>
            <el-descriptions-item v-if='addOrEditForm.steps["cookies"]' label="Cookies">{{
                addOrEditForm.steps['cookies']
                }}</el-descriptions-item>
            <el-descriptions-item v-if='addOrEditForm.steps["headers"]' label="Headers">{{
                addOrEditForm.steps["headers"]
                }}</el-descriptions-item>
            <el-descriptions-item label="预期结果">{{ addOrEditForm.expected }}</el-descriptions-item>
        </el-descriptions>

    </el-dialog>


    <!-- 创建 AI 测试任务对话框 -->
    <el-dialog v-model="execInitFormVisible" title="AI 测试任务" width="500">
        <el-form :model="execForm" label-position="left">
            <el-form-item label="名称" :label-width="80" required>
                <el-input v-model="execForm.name" />
            </el-form-item>
            <el-form-item label="类型" :label-width="80">
                <el-select v-model="execForm.exec_type" placeholder="选择用例类型">
                    <el-option label="HTTP 请求" value="http" />
                </el-select>
            </el-form-item>
        </el-form>
        <el-divider content-position="center">用例参数配置</el-divider>
        <el-collapse>
            <el-collapse-item v-for="(item, index) in execForm.exec_param" :title="item.case_id + '.' + item.case_name"
                :key="index">
                <el-form-item v-for="(value, key) in item.case_param" :label="key" :label-width="160">
                    <el-input v-model="item.case_param[key]" placeholder="请输入参数值" :value="value" />
                </el-form-item>
            </el-collapse-item>
        </el-collapse>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="execInitFormVisible = false">取消</el-button>
                <el-button type="primary" @click="handleSave">
                    提交
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>
<script setup>
import { onMounted, reactive, ref } from 'vue';
import api_document_api from '@/api/api_document_api'
import api_test_case_api from '@/api/api_test_case_api'
import api from '@/api/api_test_case_exec_api'
import { flatToTree } from '@/utils/dataUtils'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
const menuTree = ref()
const menuData = ref([])

// 获取当前项目ID
const project_id = sessionStorage.getItem('project_id')

function getRowKey(row) {
    return row.id
}

/**
 * 加载数据
 */
async function loadData() {
    if (!project_id) {
        console.error('项目ID不存在')
        return
    }
    let res = await api_document_api.queryAll(project_id)
    console.log('documents loadData res', res)
    let resData = res.data
    if (resData.code == 200) {
        menuData.value = flatToTree(resData.data)
    }
    loadTestCases()
}

// 加载测试用例数据
async function loadTestCases() {
    loading.value = true
    // 加载测试用例数据
    let res = await api_test_case_api.queryByPage(queryParams)
    console.log('test_cases loadData res', res)
    let resData = res.data
    if (resData.code == 200) {
        testcaseList.value = resData.data
        loading.value = false
        total.value = resData.total
    }
}

// 查询参数
const queryParams = reactive({
    page: 1,
    pageSize: 20,
    project_id: project_id,
    name: '',
    priority: null,
    // 关联的文档ID列表
    module_ids: [],
})

// 重置查询
const resetQuery = () => {
    queryParams.page = 1
    queryParams.name = ''
    queryParams.priority = null
    queryParams.module_ids = []
    loadTestCases()
}
// 执行类型
const tmp_exec_type = ref('http')
// 分页总数
const total = ref(0)

// 测试用例表格相关
const loading = ref(false)
// 保存所有的测试用例数据
const testcaseList = ref([])

// 分页大小改变
const handleSizeChange = (val) => {
    queryParams.pageSize = val
    loadTestCases()
}

// 当前页改变
const handleCurrentChange = (val) => {
    queryParams.page = val
    loadTestCases()
}

const addOrEditForm = reactive({
    id: null,
    name: '',
    priority: '0',
    precondition: '',
    steps: '',
    expected: '',
})

// 优先级选项
const priorityOptions = [
    { value: '1', label: '1', type: 'primary' },
    { value: '2', label: '2', type: 'success' },
    { value: '3', label: '3', type: 'info' },
    { value: '4', label: '4', type: 'warning' },
    { value: '5', label: '5', type: 'danger' }
]

// 绑定了table的ref，代表table组件的引用
const tableRef = ref()
const execInitFormVisible = ref(false)
// 执行表单数据
const execForm = reactive({
    name: '',
    exec_type: tmp_exec_type.value,
    project_id: project_id,
    exec_param: []
})



/**
 * 处理创建 AI 测试任务
 */
async function handlePreparedTask() {
    let selectedRows = tableRef.value.getSelectionRows()
    console.log('selectedRows', selectedRows)
    if (selectedRows.length == 0) {
        ElMessage.warning('请选择要创建 AI 测试任务的测试用例')
        return
    }
    // 提取选中行的ID
    let selectedIds = selectedRows.map(row => row.id)
    console.log('selectedIds', selectedIds)
    let case_ids = selectedIds.join(',')
    // 调用 API 创建 AI 测试任务
    let res = await api.prepared_task({
        case_ids: case_ids
    })
    console.log('handlePreparedTask res', res)
    let resData = res.data
    if (resData.code == 200) {
        // 刷新测试用例列表
        // loadTestCases()
        execForm.exec_param = resData.data
        execForm.exec_type = tmp_exec_type.value
        execForm.case_ids = case_ids
        // 显示创建 AI 测试任务对话框
        execInitFormVisible.value = true
    } else {
        ElMessage.error(resData.message)
    }

}
const router = useRouter()
function handleExecHistory() {
    // 跳转路由到执行记录页面
    router.push({ name: 'api_exec_record' })
}

async function handleSave() {
    
    // 调用 API 创建 AI 测试任务
    let res = await api.insert(execForm)
    console.log('handleSave res', res)
    let resData = res.data
    if (resData.code == 200) {
        ElMessage.success('创建 AI 测试任务成功')
        execInitFormVisible.value = false
    } else {
        ElMessage.error(resData.message)
    }
}

// 查看测试用例对话框相关
const viewDialogVisible = ref(false)

// 查看测试用例
const handleView = async (row) => {
    try {
        // 获取完整的测试用例数据
        const res = await api_test_case_api.queryById(row.id)
        console.log('handleView res', res)
        const resData = res.data
        if (resData.code == 200) {
            // addOrEditForm = resData.data
            Object.assign(addOrEditForm, resData.data)
            addOrEditForm.steps = JSON.parse(addOrEditForm.steps)
            console.log("addOrEditForm.steps", addOrEditForm.steps)
            viewDialogVisible.value = true
        } else {
            ElMessage.error(resData.message)
        }
    } catch (error) {
        console.error('获取测试用例详情失败:', error)
        ElMessage.error('获取测试用例详情失败')
    }
}
function handlePriorityType(priority) {
    console.log('handlePriorityType priority', priority)
    let type = priorityOptions.filter(item => priority == item.value)[0]?.type
    console.log('handlePriorityType type', type)
    return type
}


onMounted(() => {
    loadData()

})
</script>

<style scoped>
/* 容器高度锁定在main内，不溢出 */
.el-container {
    height: 100%;
    overflow: hidden;
}

.el-row {
    height: 100%;
    overflow: hidden;
}

/* el-main自然填充父容器，不出滚动条 */
.el-main {
    --el-main-padding: 10px;
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.record-item {
    display: flex;
    align-items: center;
    font-size: 14px;
    justify-content: space-between;
    margin-right: 10px;
}

.query-card {
    margin-bottom: 10px;
}

.action-buttons {
    margin-bottom: 10px;
    width: 100%;
    display: flex;
    gap: 10px;
}

/* 主表格卡片弹性撑满（排除query-card） */
.el-card:not(.query-card) {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
}

/* el-card__body改为flex列布局，整体不出滚动条 */
.el-card:not(.query-card) :deep(.el-card__body) {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* el-table弹性占满 */
.el-card:not(.query-card) :deep(.el-table) {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

/* el-table__body-wrapper单独出滚动条（只滚动表格行，表头不动） */
.el-card:not(.query-card) :deep(.el-table__body-wrapper) {
    overflow-y: auto !important;
    flex: 1;
}

/* 🎨 美化滚动条 —— el-table__body-wrapper */
.el-card:not(.query-card) :deep(.el-table__body-wrapper)::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

.el-card:not(.query-card) :deep(.el-table__body-wrapper)::-webkit-scrollbar-track {
    background: #f1f3f4;
    border-radius: 3px;
}

.el-card:not(.query-card) :deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb {
    background: #c1c6cd;
    border-radius: 3px;
    transition: all 0.2s;
}

.el-card:not(.query-card) :deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb:hover {
    background: #909399;
}

/* 分页器固定在卡片底部 */
.pagination-container {
    margin-top: auto;
    padding-top: 15px;
    display: flex;
    justify-content: flex-end;
    flex-shrink: 0;
}
</style>