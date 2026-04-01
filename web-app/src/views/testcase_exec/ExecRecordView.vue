<template>
    <el-container>
        <el-row style="width: 100%;">
            <el-main>
                <el-card>
                    <template #header>
                        <div class="card-header">
                            <!-- 操作按钮区域 -->
                            <!-- 操作按钮区域 居右-->
                            <div class="action-buttons">
                                <el-button type="primary" @click="handleBack"> 返回 </el-button>
                                <el-button type="success" @click="loadData">
                                    刷新
                                </el-button>
                                <el-button type="danger" @click="handleBatchDelete">
                                    批量删除
                                </el-button>
                            </div>
                        </div>
                    </template>

                    <el-table v-loading="loading" :data="taskList" border stripe ref="tableRef" :row-key="getRowKeys">
                        <el-table-column type="selection" width="55" align="center" :reserve-selection="true" />
                        <el-table-column label="ID" prop="id" width="60" align="center" />
                        <el-table-column label="创建时间" prop="created_at" width="170" />
                        <el-table-column label="执行状态" prop="exec_status" width="140" align="center">
                        </el-table-column>
                        <el-table-column label="测试计划" prop="name" min-width="180">
                            <template #default="{ row }">
                                <el-button link type="primary" @click="handleView(row)">
                                    {{ row.name }}
                                </el-button>
                            </template>
                        </el-table-column>
                        <el-table-column label="操作" width="160" align="center">
                            <template #default="{ row }">
                                <el-button link type="primary" @click="handleDelete(row)">
                                    删除
                                </el-button>
                                <el-button link type="primary" @click="handlePreparedTask(row)">
                                    复制执行
                                </el-button>
                            </template>
                        </el-table-column>
                    </el-table>
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
            <el-collapse-item v-for="(item, index) in execForm.exec_param" :title="item.case_id + '.' + item.case_name" :key="index">
                <el-form-item v-for="(value, key) in item.case_param" :label="key" :label-width="160">
                    <el-input v-model="item.case_param[key]" placeholder="请输入参数值" :value="value" />
                </el-form-item>
            </el-collapse-item>
        </el-collapse>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="execInitFormVisible = false">取消</el-button>
                <el-button type="primary" @click="handleSave">提交</el-button>
            </div>
        </template>
    </el-dialog>

    <!-- 查看测试用例对话框 -->
    <el-dialog v-model="viewDialogVisible" title="执行结果" width="800px">
        <el-divider content-position="center">{{ viewData.desc }}</el-divider>
        <el-collapse>
            <el-collapse-item v-for="(detail, index) in viewData.details" :key="index">
                <template #title>
                    <div>
                        {{ detail.case_id + '.' + detail.case_name }}
                        <el-tag v-if="detail.result" type="success">测试通过</el-tag>
                        <el-tag v-if="!detail.result" type="danger">测试失败</el-tag>
                    </div>
                </template>
                <el-descriptions :column="1" label-width="100" border>
                    <el-descriptions-item label="测试步骤">{{ detail.steps }}</el-descriptions-item>
                    <el-descriptions-item label="预期结果">{{ detail.expected }}</el-descriptions-item>
                    <el-descriptions-item label="AI执行记录">{{ detail.ai_result }}</el-descriptions-item>
                    <el-descriptions-item label="可视化记录" v-if="detail.attachments && detail.attachments.length > 0">
                        <el-image style="width: 100px; height: 100px" :src="detail.attachments[0]" :zoom-rate="1.2"
                            :max-scale="7" :min-scale="0.2" :preview-src-list="detail.attachments" show-progress
                            :initial-index="4" fit="cover" />

                    </el-descriptions-item>
                </el-descriptions>
            </el-collapse-item>
        </el-collapse>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="viewDialogVisible = false">取消</el-button>
            </div>
        </template>
    </el-dialog>
</template>
<script setup>
import { onMounted, reactive, ref } from 'vue';
import api from '@/api/test_case_exec_api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
const router = useRouter()

function handleBack() {
    router.back()
}
const getRowKeys = (row) => {
    return row.id
}

// 获取当前项目ID
const project_id = sessionStorage.getItem('project_id')

/**
 * 加载数据
 */
async function loadData() {
    if (!project_id) {
        console.error('项目ID不存在')
        return
    }
    loading.value = true
    // 加载测试用例数据
    let res = await api.queryByPage(queryParams)
    console.log('test_cases loadData res', res)
    let resData = res.data
    if (resData.code == 200) {
        taskList.value = resData.data
        loading.value = false
        total.value = resData.total
    }
}

// 查询参数
const queryParams = reactive({
    page: 1,
    pageSize: 10,
    project_id: project_id,
})

// 执行类型
const tmp_exec_type = ref('http')
// 分页总数
const total = ref(0)

// 测试用例表格相关
const loading = ref(false)
// 保存所有的测试用例数据
const taskList = ref([])

// 分页大小改变
const handleSizeChange = (val) => {
    queryParams.pageSize = val
    loadData()
}

// 当前页改变
const handleCurrentChange = (val) => {
    queryParams.page = val
    loadData()
}


/**
 * 删除
 * @param item 
 */
async function handleDelete(item) {
    try {
        // 确认删除弹窗
        await ElMessageBox.confirm('确认删除数据吗？', '删除确认', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        })
        // 取消后面的代码不会执行，直接跳到了catch部分了

        let res = await api.deleteById(item.id)
        console.log('removeTree res', res)
        let resData = res.data
        if (resData.code == 200) {
            loadData()
            ElMessage.success('删除成功')
        }
    } catch (error) {
        console.error('removeTree error', error)
        ElMessage.error('删除失败')
        return
    }
}

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

const handleBatchDelete = async () => {
    let selectedRows = tableRef.value.getSelectionRows()
    console.log('selectedRows', selectedRows)
    if (selectedRows.length == 0) {
        ElMessage.warning('请选择要删除的执行记录')
        return
    }
    // 提取选中行的ID
    let selectedIds = selectedRows.map(row => row.id)
    console.log('selectedIds', selectedIds)
    // 确认删除弹窗
    await ElMessageBox.confirm('确认删除数据吗？', '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    })
    // 调用 API 删除选中的执行记录
    let res = await api.deleteBatch(selectedIds)
    console.log('handleBatchDelete res', res)
    let resData = res.data
    if (resData.code == 200) {
        ElMessage.success('删除执行记录成功')
        // 刷新执行记录列表
        loadData()
    } else {
        ElMessage.error(resData.message)
    }
}


/**
 * 处理创建 AI 测试任务
 */
async function handlePreparedTask(row) {
    // 根据id查询
    let res = await api.queryById(row.id)
    console.log('editItem', res.data)
    let case_ids = ""
    let resData = res.data
    if (resData.code == 200) {
        Object.assign(execForm, resData.data)
        case_ids = resData.data.case_ids
    }
    if (!case_ids) {
        return
    }
    // 调用 API 创建 AI 测试任务
    res = await api.prepared_task({
        case_ids: case_ids
    })
    console.log('handlePreparedTask res', res)
    resData = res.data
    if (resData.code == 200) {
        // 刷新测试用例列表
        // loadTestCases()
        execForm.exec_param = resData.data
        execForm.case_ids = case_ids
        // 显示创建 AI 测试任务对话框
        execInitFormVisible.value = true
    } else {
        ElMessage.error(resData.message)
    }
}

async function handleSave() {
    // 调用 API 创建 AI 测试任务
    let res = await api.insert(execForm)
    console.log('handleSave res', res)
    let resData = res.data
    if (resData.code == 200) {
        ElMessage.success('创建 AI 测试任务成功')
        // 刷新测试用例列表
        loadData()
        execInitFormVisible.value = false
    } else {
        ElMessage.error(resData.message)
    }
}


// 查看测试用例对话框相关
const viewDialogVisible = ref(false)
const viewData = reactive({})
// 服务器地址
const server_url = "http://localhost:5001"

// 查看执行结果
const handleView = async (row) => {
    try {
        // 获取完整的执行记录数据
        const res = await api.queryById(row.id)
        console.log('handleView res', res)
        const resData = res.data
        if (resData.code == 200) {
            Object.assign(viewData, resData.data)
            if (typeof viewData.details === 'string') {
                viewData.details = JSON.parse(viewData.details)
                // 拼接正确的图片附件地址
                viewData.details.forEach(element => {
                    console.log('element.attachments前', element.attachments);
                    element.attachments = element.attachments.map(item => `${server_url + item}`);
                    console.log('element.attachments后', element.attachments);
                });
            }
            viewDialogVisible.value = true
        } else {
            ElMessage.error(resData.message)
        }
    } catch (error) {
        console.error('获取执行记录详情失败:', error)
        ElMessage.error('获取执行记录详情失败，请稍后重试')
    }
}


onMounted(() => {
    loadData()

})
</script>

<style scoped>
.el-aside {
    height: 100%;
}

.tree-panel {
    width: 100%;
    height: 100%;
    background-color: white;
}

.tree-header {
    width: 100%;
    background-color: white;
    display: flex;
    justify-content: center;
    padding-top: 10px;
    padding-bottom: 10px;
    border-bottom: 1px #3b82f680 solid;
}

.custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    padding-right: 8px;
}

/* 单行文本溢出隐藏并显示省略号 */
.single-line-overflow {
    /* 1. 强制文本在一行内显示（不换行），核心属性 */
    white-space: nowrap;
    /* 2. 超出容器部分隐藏（不显示滚动条，不溢出容器） */
    overflow: hidden;
    /* 3. 用省略号...替代超出部分的文本（仅在单行生效） */
    text-overflow: ellipsis;
    /* 4. 设置宽度，超出宽度部分将显示省略号 */
    width: 170px;
}

/* 处理对齐 */
.el-main {
    padding-top: 0;
    flex-basis: none;
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

.pagination-container {
    margin-top: 15px;
    display: flex;
    justify-content: flex-end;
}
</style>