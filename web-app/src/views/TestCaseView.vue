<template>
    <el-container>
        <el-row style="width: 100%;">
            <el-aside>
                <div class="tree-panel">
                    <div class="tree-header">
                    </div>
                    <div class="tree-container">
                        <el-tree ref="menuTree" style="max-width: 600px" :data="menuData" show-checkbox node-key="id"
                            :check-on-click-node="false" :check-on-click-leaf="false" default-expand-all
                            :expand-on-click-node="false" @node-click="handleNodeClick" @check="handleCheck">
                            <template #default="{ node, data }">
                                <div class="custom-tree-node">
                                    <span class="single-line-overflow">{{ node.label }}</span>
                                    <div>
                                        <el-button type="primary" link @click.stop="viewTree(data.source)">
                                            查看
                                        </el-button>
                                    </div>
                                </div>
                            </template>
                        </el-tree>
                    </div>
                </div>
            </el-aside>


            <el-main>

                <!-- 额外提示词 -->
                <el-card class="query-card">
                    <el-input v-model="hint" placeholder="如果您对于系统生成的测试用力不满意，可以额外补充你的特殊要求" type="textarea" :rows="3"
                        resize="vertical" />
                </el-card>
                <el-card>
                    <template #header>
                        <div class="card-header">
                            <span>当前：{{ curMenuName }}</span>
                            <!-- 操作按钮区域 -->
                            <div class="action-buttons">

                                <el-button type="primary" @click="generateTestCasesByAI">AI测试用例生成</el-button>
                                <el-button type="primary" @click="handleAdd">
                                    <el-icon>
                                        <plus />
                                    </el-icon>
                                    手动新增
                                </el-button>
                                <el-button type="danger" @click="handleBatchDelete">
                                    <el-icon>
                                        <delete />
                                    </el-icon>
                                    批量删除
                                </el-button>
                                <el-button type="warning" @click="handleExport">
                                    <el-icon>
                                        <download />
                                    </el-icon>
                                    导出
                                </el-button>
                            </div>
                        </div>
                    </template>

                    <el-table v-loading="loading" :data="testcaseList" border stripe ref="tableRef">
                        <el-table-column type="selection" width="40" align="center" />
                        <el-table-column label="ID" prop="id" width="60" align="center" />
                        <el-table-column label="用例名称" prop="name" min-width="180">
                            <template #default="{ row }">
                                <el-button link type="primary" @click="handleView(row)">
                                    {{ row.name }}
                                </el-button>
                            </template>
                        </el-table-column>
                        <el-table-column label="优先级" prop="priority" width="80" align="center">
                        </el-table-column>
                        <el-table-column label="操作" width="140" align="center">
                            <template #default="{ row }">
                                <el-button size="small" type="primary" @click="handleEdit(row)">
                                    编辑
                                </el-button>
                                <el-button size="small" type="danger" @click="handleDelete(row)">
                                    删除
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

    <!-- 查看模态框 -->
    <el-dialog v-model="viewModalVisible" :title="viewModalTitle" width="800px" @open="initEditor" append-to-body>
        <div id="editor" class="vditor-container"></div>
    </el-dialog>

    <!-- 添加/编辑测试用例对话框 -->
    <el-dialog v-model="addOrEditModalVisible" :title="addOrEditModalTitle" width="800px">
        <el-form :model="addOrEditForm" label-width="100px" ref="addOrEditFormRef">
            <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="用例名称" prop="name" required>
                        <el-input v-model="addOrEditForm.name" placeholder="请输入用例名称" />
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="优先级" prop="priority" required>
                        <el-select v-model="addOrEditForm.priority" placeholder="请选择优先级">
                            <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label"
                                :value="item.value" />
                        </el-select>
                    </el-form-item>
                </el-col>
            </el-row>
            <el-form-item label="前置条件" prop="precondition">
                <el-input v-model="addOrEditForm.precondition" type="textarea" :rows="2" placeholder="请输入前置条件" />
            </el-form-item>
            <el-form-item label="测试步骤" prop="steps" required>
                <el-input v-model="addOrEditForm.steps" type="textarea" :rows="2" placeholder="请输入测试步骤" />
            </el-form-item>
            <el-form-item label="预期结果" prop="expected" required>
                <el-input v-model="addOrEditForm.expected" type="textarea" :rows="2" placeholder="请输入预期结果" />
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="addOrEditModalVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSave()">确认</el-button>
        </template>
    </el-dialog>

    <!-- 查看测试用例对话框 -->
    <el-dialog v-model="viewDialogVisible" title="用例详情" width="800px">
        <el-descriptions :column="1" label-width="80" border>
            <el-descriptions-item label="用例名称">{{ addOrEditForm.name }}</el-descriptions-item>
            <el-descriptions-item label="优先级">
                <el-tag :type="handlePriorityType(addOrEditForm.priority)">
                    {{ addOrEditForm.priority }}
                </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="前置条件">{{ addOrEditForm.precondition }}</el-descriptions-item>
            <el-descriptions-item label="测试步骤">{{ addOrEditForm.steps }}</el-descriptions-item>
            <el-descriptions-item label="预期结果">{{ addOrEditForm.expected }}</el-descriptions-item>
        </el-descriptions>
    </el-dialog>


    <!-- AI分析对话框 -->
    <el-dialog v-model="aiAnalysisDialogVisible" title="AI生成测试用例" width="80%">
        <el-tabs v-model="activeName">
            <el-tab-pane label="生成结果" name="result">
                <el-scrollbar height="400px">
                    <div v-if="tmp_testcaseList.length > 0" class="test-cases-result">
                        <el-table :data="tmp_testcaseList" style="width: 100%" :row-key="(row) => row.id"
                            @selection-change="handleAISelectionChange">
                            <el-table-column type="selection" width="55" />
                            <el-table-column prop="id" label="编号" width="55" />
                            <el-table-column prop="name" label="测试用例名称" width="250" />
                            <el-table-column prop="precondition" label="前置条件" width="200" />
                            <el-table-column prop="steps" label="测试步骤" />
                            <el-table-column prop="expected" label="预期结果" width="300" />
                            <el-table-column prop="priority" label="优先级" width="80" />
                        </el-table>
                    </div>
                    <div v-else class="empty-result">
                        <el-empty description="暂无测试用例，请点击生成">
                        </el-empty>
                    </div>
                </el-scrollbar>
            </el-tab-pane>
        </el-tabs>

        <template #footer>
            <el-button type="primary" @click="generateTestCasesByAI">重新生成</el-button>
            <el-button type="success" @click="applyTestCases">应用</el-button>
            <el-button @click="aiAnalysisDialogVisible = false">关闭</el-button>
        </template>
    </el-dialog>

    <StreamingDialog v-model="streamDialogVisible" title="AI处理中..." :content="streamContent" :progress="streamProgress">
    </StreamingDialog>
</template>
<script setup>
import { onMounted, ref } from 'vue';
import Vditor from 'vditor'
import 'vditor/dist/index.css' // 引入 Vditor 的样式文件
import document_api from '@/api/document_api'
import api from '@/api/test_case_api'
import { flatToTree } from '@/utils/dataUtils'
import { ElMessage, ElMessageBox } from 'element-plus'
import StreamingDialog from '@/components/StreamingDialog.vue'
const menuTree = ref()
const menuData = ref([])

// 获取当前项目ID
const project_id = sessionStorage.getItem('project_id')
// 用户输入的提示词
const hint = ref('')
// 当前选中的菜单名称
const curMenuName = ref('')
// 当前选中的模块ID
const curModuleId = ref('')

/**
 * 加载数据
 */
async function loadData() {
    if (!project_id) {
        console.error('项目ID不存在')
        return
    }
    let res = await document_api.queryAll(project_id)
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
    let res = await api.queryByPage(queryParams.value)
    console.log('test_cases loadData res', res)
    let resData = res.data
    if (resData.code == 200) {
        testcaseList.value = resData.data
        loading.value = false
        total.value = resData.total
    }
}

// 查询参数
const queryParams = ref({
    page: 1,
    pageSize: 10,
    project_id: project_id,
    module_id: curModuleId.value,
})
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

// 添加/编辑测试用例对话框相关
const addOrEditModalVisible = ref(false)
const addOrEditModalTitle = ref('添加目录')
const addOrEditForm = ref({
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

// 添加测试用例
const handleAdd = () => {
    if (!curModuleId.value) {
        ElMessage.error('请选择模块')
        return
    }
    // 设置标题
    addOrEditModalTitle.value = '添加测试用例'
    // 清空表单数据
    addOrEditForm.value.id = null
    addOrEditForm.value.name = ''
    addOrEditForm.value.module_id = curModuleId.value
    addOrEditForm.value.priority = '0'
    addOrEditForm.value.precondition = ''
    addOrEditForm.value.steps = ''
    addOrEditForm.value.expected = ''
    // 显示模态框
    addOrEditModalVisible.value = true
}

// 编辑测试用例
async function handleEdit(item) {
    console.log('handleEdit item', item)
    addOrEditModalTitle.value = '编辑测试用例'
    addOrEditModalVisible.value = true
    const res = await api.queryById(item.id)
    const resData = res.data
    if (resData.code == 200) {
        addOrEditForm.value = resData.data
    } else {
        ElMessage.error(resData.message)
    }
}

// 
async function handleSave() {
    if (!addOrEditForm.value.name) {
        ElMessage.error('请输入用例名称')
        return
    }
    if (!addOrEditForm.value.priority) {
        ElMessage.error('请选择优先级')
        return
    }
    if (!addOrEditForm.value.steps) {
        ElMessage.error('请输入测试步骤')
        return
    }
    if (!addOrEditForm.value.expected) {
        ElMessage.error('请输入预期结果')
        return
    }
    try {
        let params = {
            project_id: project_id,
            name: addOrEditForm.value.name,
            module_id: addOrEditForm.value.module_id,
            priority: addOrEditForm.value.priority,
            precondition: addOrEditForm.value.precondition,
            steps: addOrEditForm.value.steps,
            expected: addOrEditForm.value.expected,
        }
        let res
        if (addOrEditForm.value.id) {
            // 编辑保存
            params.id = addOrEditForm.value.id
            res = await api.update(params)
        } else {
            // 添加保存
            res = await api.insert(params)
        }

        console.log('saveTree res', res)
        let resData = res.data
        if (resData.code == 200) {
            // 刷新目录树
            loadData()
            ElMessage.success('保存成功')
            addOrEditModalVisible.value = false
        }
    } catch (error) {
        console.error('saveTree error', error)
        ElMessage.error('保存目录失败')
        return
    }
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
async function handleBatchDelete() {
    console.log('handleBatchDelete')
    let rows = tableRef.value.getSelectionRows()
    console.log("rows", rows);
    if (rows.length == 0) {
        ElMessage.error('请选择要删除的数据')
        return
    }
    // 获取选中的数据的id
    let ids = rows.map(item => item.id)
    // 确认删除弹窗
    await ElMessageBox.confirm('确认删除选中的数据吗吗？', '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    })
    let res = await api.deleteBatch(ids)
    console.log('handleBatchDelete res', res)
    let resData = res.data
    if (resData.code == 200) {
        loadData()
        ElMessage.success('删除成功')
    } else {
        ElMessage.error('删除失败')
    }
}


// 查看测试用例对话框相关
const viewDialogVisible = ref(false)

// 查看测试用例
const handleView = async (row) => {
    try {
        // 获取完整的测试用例数据
        const res = await api.queryById(row.id)
        console.log('handleView res', res)
        const resData = res.data
        if (resData.code == 200) {
            addOrEditForm.value = resData.data
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

// 添加流式处理相关状态
const streamDialogVisible = ref(false)
const streamContent = ref('')
const streamProgress = ref(0)

// 保存选中的节点
const selectedNodes = ref([])
/**
 * 处理树节点选中状态改变
 * @param {Object} data - 节点数据
 * @param {Array} checkedNodes - 选中的节点数组
 */
const handleCheck = (
    data,
    checkedNodes
) => {
    console.log(data, checkedNodes, checkedNodes.checkedKeys)
    selectedNodes.value = checkedNodes.checkedKeys
}

const abortController = ref(null)
// 保存ai生成的测试用例
const tmp_testcaseList = ref([])
// ai生成测试用例结果的对话框
const aiAnalysisDialogVisible = ref(false)
const activeName = ref('result')

// 修改测试用例分析函数
const generateTestCasesByAI = async () => {
    if (!curModuleId.value) {
        ElMessage.error('请选择模块')
        return
    }
    // 重置状态
    streamDialogVisible.value = true
    streamContent.value = ''
    streamProgress.value = 0

    const prompt_value = {
        primary_content: curModuleId.value,
        second_content: selectedNodes.value.map((item) => `${item}`).join(","),
        hint: hint.value,
        project_id: project_id
    }

    try {
        // 创建AbortController用于取消请求
        abortController.value = new AbortController()

        // 调用流式API
        const response = await api.processWithAIStream(prompt_value, {
            signal: abortController.value.signal,
            onMessage: (data) => {
                switch (data.status) {
                    case 'start':
                        streamContent.value = '开始生成内容...\n'
                        break
                    case 'streaming':
                        streamContent.value += data.content
                        // 根据内容长度估算进度
                        if (data.full_content.length > 100) {
                            streamProgress.value = Math.min(95, Math.floor((data.full_content.length / 2000) * 100))
                        }
                        break
                    case 'completed':
                        console.log('AI处理成功：', data.data)
                        // 处理返回的测试用例数据
                        if (data.data) {
                            // 清空现有测试用例
                            tmp_testcaseList.value = [];

                            // 添加新生成的测试用例
                            data.data.forEach(testcase => {
                                tmp_testcaseList.value.push(testcase);
                            });
                            console.log('tmp_testcaseList.value', tmp_testcaseList.value)

                            aiAnalysisDialogVisible.value = true;
                        }
                        streamProgress.value = 100
                        // 延迟关闭流式显示
                        setTimeout(() => {
                            streamDialogVisible.value = false
                        }, 1000)
                        break
                    case 'error':
                        ElMessage.error(data.message || 'AI处理失败')
                        streamDialogVisible.value = false
                        break
                }
            },
            onError: (error) => {
                console.error('流式请求错误:', error)
                ElMessage.error('请求失败: ' + (error.message || '网络错误'))
                streamDialogVisible.value = false
            },
            onComplete: () => {
                // 请求完成，但不是处理完成
                console.log('流式请求完成')
            }
        })

    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('请求已被取消')
        } else {
            console.error('AI处理错误:', error)
            ElMessage.error('AI处理失败: ' + (error.message || '未知错误'))
        }
        streamDialogVisible.value = false
    }
}

// 选中的测试用例
const selectedTestcases = ref([]);

// 处理测试用例选择事件
const handleAISelectionChange = (selection) => {
    console.log('handleAISelectionChange selection', selection)
    selectedTestcases.value = selection;
}

// 应用选中的测试用例
const applyTestCases = async () => {
    if (selectedTestcases.value.length === 0) {
        ElMessage.warning('请先选择要应用的测试用例');
        return;
    }

    // 批量添加选中的测试用例
    const data = selectedTestcases.value.map(testcase => {
        const testcaseData = {
            name: testcase.name,
            module_id: curModuleId.value,
            project_id: project_id,
            priority: testcase.priority || '0',
            precondition: testcase.precondition || '',
            steps: testcase.steps || '',
            expected: testcase.expected || ''
        };
        return testcaseData;
    });
    const form = {
        data_list: data,
    }

    const res = await api.insertBatch(form)
    console.log('res', res)
    const resData = res.data
    if (resData.code == 200) {
        ElMessage.success('添加成功')
        aiAnalysisDialogVisible.value = false
        loadData()
    } else {
        ElMessage.error('添加失败')
    }
}

const viewModalVisible = ref(false)
const viewModalTitle = ref('')
/**
 * 显示添加目录模态框
 * @param item
 */
function viewTree(item) {
    console.log('viewTree item', item)
    viewModalVisible.value = true
    viewModalTitle.value = item.name
    // 预防编辑为null时，后面的代码报错
    if (vditorEditor.value) {
        // 修改编辑器内容
        vditorEditor.value.setValue(item.content)
    }
}

/**
 * 处理节点点击事件
 * @param node 点击的节点
 * @param data 节点数据
 */
function handleNodeClick(node, data) {
    console.log('handleNodeClick node', node)
    console.log('handleNodeClick data', data)
    // 点击节点后，将节点的content赋值到编辑器中
    if (vditorEditor.value) {
        vditorEditor.value.setValue(node.source.content)
    }
    // 点击节点后，将节点的name赋值到curMenuName.value中
    curMenuName.value = node.source.name
    // 保存当前节点的ID
    curModuleId.value = node.source.id
    queryParams.value.module_id = node.source.id
    // 添加用例需要指定模块ID
    addOrEditForm.value.module_id = node.source.id

    // 点击节点后，调用分页查询接口
    loadTestCases()
}


// 导出
const handleExport = async () => {
    if (!project_id) {
        ElMessage.warning('项目未选择');
        return;
    }

    try {

        // 发送导出请求
        const response = await api.exportExcel({
            module_id: curModuleId.value,
            project_id: project_id
        });

        // 处理响应
        if (response.status === 200) {
            const blob = response.data;

            // 从响应头中提取文件名
            let filename = '测试用例导出.xlsx';

            // 创建下载链接
            const url = window.URL.createObjectURL(new Blob([blob], {
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }));

            // 创建a标签并触发下载
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);

            document.body.appendChild(link);
            // 点击下载链接
            link.click();

            // 清理资源
            setTimeout(() => {
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            }, 100);

            ElMessage.success('Excel文件导出成功');
        } else {
            throw new Error(`导出失败，状态码：${response.status}`);
        }
    } catch (error) {
        console.error('导出Excel失败:', error);

        // 处理不同类型的错误
        if (error.response) {
            // 服务器返回错误响应
            if (error.response.status === 400) {
                ElMessage.error('导出参数错误');
            } else if (error.response.status === 500) {
                ElMessage.error('服务器内部错误，导出失败');
            } else {
                ElMessage.error(`导出失败：${error.response.data?.message || '未知错误'}`);
            }
        } else if (error.request) {
            // 请求已发送但没有收到响应
            ElMessage.error('网络异常，导出失败，请检查网络连接');
        } else {
            // 请求配置错误
            ElMessage.error(`导出失败：${error.message}`);
        }
    }
}

// 绑定编辑器
const vditorEditor = ref(null)
// 初始化编辑器
const initEditor = () => {
    // 保存只有一个编辑器对象，避免重复创建，不然的话肯定会影响性能
    if (vditorEditor.value) {
        return
    }
    // 初始化编辑器
    vditorEditor.value = new Vditor('editor', {
        height: 400,
        width: '100%',
        mode: 'ir', // 显示源代码模式
        toolbarConfig: {
            hide: true,
        },
        after() {
            console.log('Vditor after')
        }
    });
}


onMounted(() => {
    loadData()

})
</script>

<style scoped>
.el-aside {
    height: 100%;
    padding: 10px;
    border-radius: 35px
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
    flex-basis: 0 !important;
    padding: 10px;
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
}

.pagination-container {
    margin-top: 15px;
    display: flex;
    justify-content: flex-end;
}
</style>