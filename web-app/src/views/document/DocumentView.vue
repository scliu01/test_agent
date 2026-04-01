<template>
    <el-container>
        <el-row style="width: 100%;">
            <el-aside>
                <div class="tree-panel">
                    <div class="tree-header">
                        <el-button type="primary" @click="addTreeRoot">
                            <i class="fas fa-plus me-1"></i> 添加根目录
                        </el-button>
                        <el-button type="primary" @click="importModalVisible = true">
                            <i class="fas fa-file-import me-1"></i> 导入文档
                        </el-button>
                    </div>
                    <div class="tree-container">
                        <el-tree ref="menuTree" style="max-width: 600px" :data="menuData" show-checkbox node-key="id"
                            :check-on-click-node="false" :check-on-click-leaf="false" default-expand-all
                            :expand-on-click-node="false" @node-click="handleNodeClick" @check="handleCheck">
                            <template #default="{ node, data }">
                                <div class="custom-tree-node">
                                    <span class="single-line-overflow">{{ node.label }}</span>
                                    <div>
                                        <el-button type="primary" link @click.stop="addTree(data.source)">
                                            添加
                                        </el-button>
                                        <el-button type="primary" link @click.stop="editTree(data.source)">
                                            编辑
                                        </el-button>
                                        <el-button style="margin-left: 4px" type="danger" link
                                            @click.stop="removeTree(node, data.source)">
                                            删除
                                        </el-button>
                                    </div>
                                </div>
                            </template>
                        </el-tree>
                    </div>
                </div>
            </el-aside>


            <el-main>
                <el-card>
                    <template #header>
                        <div class="card-header">
                            <span>当前：{{ curMenuName }}</span>
                            <div>
                                <el-button type="success" @click="showAiDialog">
                                    AI需求评审
                                </el-button>
                                <el-button type="primary" @click="saveTree">
                                    保存需求
                                </el-button>
                            </div>
                        </div>
                    </template>

                    <div id="editor" class="h-100"></div>

                </el-card>
            </el-main>
        </el-row>
    </el-container>

    <!-- 添加/编辑模态框 -->
    <el-dialog v-model="addOrEditModalVisible" :title="addOrEditModalTitle" width="500px" :destroy-on-close="true">
        <el-form :model="addOrEditForm" label-width="80px">
            <el-form-item label="名称" prop="name" required>
                <el-input v-model="addOrEditForm.name" placeholder="请输入名称" />
            </el-form-item>
        </el-form>

        <template #footer>
            <el-button @click="addOrEditModalVisible = false">取消</el-button>
            <el-button type="primary" @click="saveTree()">确认</el-button>
        </template>
    </el-dialog>

    <!-- 导入文档模态框 -->
    <el-dialog v-model="importModalVisible" class="aaa" style="width: fit-content;" title="导入需求文档" width="600px"
        :destroy-on-close="true" :modal="false" :close-on-click-modal="false" :modal-penetrable="true"
        :append-to-body="true">
        <el-form label-position="top">
            <el-form-item label="选择文档">
                <el-upload class="upload-demo" drag action="#" :limit="1" :auto-upload="false"
                    :on-change="handleFileChange">
                    <el-icon class="el-icon--upload">
                        <upload-filled />
                    </el-icon>
                    <div class="el-upload__text">
                        拖拽文件到此处或 <em>点击上传</em>
                    </div>
                    <template #tip>
                        <div class="el-upload__tip">
                            支持格式: WORD(.docx)、Markdown(.md)
                        </div>
                    </template>
                </el-upload>
            </el-form-item>

            <el-form-item label="导入选项">
                <el-checkbox v-model="replaceExisting" label="替换现有需求" />
                <div class="el-form-item__tip">如果勾选，将删除当前项目的所有需求并替换为文档内容</div>
            </el-form-item>

            <el-form-item label="需求标题层级">
                <el-select v-model="headingLevels" placeholder="请选择标题层级">
                    <el-option label="一级标题" value="1" />
                    <el-option label="二级标题" value="2" />
                    <el-option label="三级标题" value="3" />
                    <el-option label="四级标题" value="4" />
                    <el-option label="五级标题" value="5" />
                    <el-option label="六级标题" value="6" />
                </el-select>
                <div class="el-form-item__tip">选中的层级将作为需求标题</div>
            </el-form-item>
        </el-form>

        <template #footer>
            <el-button @click="importModalVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmImportDocument">导入</el-button>
        </template>
    </el-dialog>
    <!-- AI.需求评审模态框 -->
    <el-dialog v-model="aiModalVisible" :title="'AI 评审 - ' + addOrEditForm.name" width="800px" draggable :modal="false"
        :modal-penetrable="true" overflow :close-on-click-modal="false" modal-class="ai-review-dialog"
        :append-to-body="true">
        <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleTabClick">
            <el-tab-pane label="需求评审" name="first">

                <el-scrollbar height="400px">
                    <div class="test-cases-container">
                        <template v-if="ai_results.data && Object.keys(ai_results.data).length > 0">
                            <el-collapse>
                                <el-collapse-item v-for="(value, key, i) in ai_results.data" :key="key" :name="key"
                                    class="test-case-category">
                                    <template #title>
                                        <el-checkbox @change="handleAiHistoryChange(key, value, $event)"></el-checkbox>
                                        {{ i + 1 }}. {{ key }}
                                    </template>
                                    <ul class="test-cases-list">
                                        <li class="test-case-item">
                                            {{ value }}
                                        </li>
                                    </ul>
                                </el-collapse-item>
                            </el-collapse>
                        </template>

                        <!-- 无结果时的提示 -->
                        <div v-else class="empty-result">
                            <el-empty description="暂无评审结果，请点击 立即开始">
                            </el-empty>
                        </div>
                    </div>
                </el-scrollbar>
                <el-input v-model="hint" placeholder="如果你对需求评审有特殊要求，请补充。" type="textarea" :rows="3" resize="vertical" />

            </el-tab-pane>
            <el-tab-pane label="采纳记录" name="second">
                <el-scrollbar height="400px">
                    <div class="test-cases-container">
                        <template v-if="ai_suggest && Object.keys(ai_suggest).length > 0">
                            <el-collapse>
                                <el-collapse-item v-for="(value, key, i) in ai_suggest" :key="key" :name="key"
                                    class="test-case-category">
                                    <template #title>
                                        <!--按钮靠右排列，垂直居中，按钮与文字间距10px-->
                                        <div class="record-item">
                                            <span>{{ i + 1 }}. {{ key }}</span>
                                            <el-button type="danger" size="small"
                                                @click="handleAiDelete(key)">删除</el-button>
                                        </div>
                                    </template>
                                    <ul class="test-cases-list">
                                        <li class="test-case-item">
                                            {{ value }}
                                        </li>
                                    </ul>
                                </el-collapse-item>
                            </el-collapse>
                        </template>

                        <!-- 无结果时的提示 -->
                        <div v-else class="empty-result">
                            <el-empty description="暂无评审结果，请点击 立即开始">
                            </el-empty>
                        </div>
                    </div>
                </el-scrollbar>
            </el-tab-pane>
        </el-tabs>

        <template #footer>
            <el-button type="primary" @click="handleAnalysis">立即开始 AI 需求评审</el-button>
            <el-button type="success" @click="applySuggest">采纳</el-button>
            <el-button @click="saveSuggest">保存</el-button>
        </template>
    </el-dialog>

    <StreamingDialog v-model="streamDialogVisible" title="AI处理中..." :content="streamContent" :progress="streamProgress">
    </StreamingDialog>
</template>
<script setup>
import { onMounted, ref } from 'vue';
import Vditor from 'vditor'
import 'vditor/dist/index.css' // 引入 Vditor 的样式文件
import api from '@/api/document_api'
import { flatToTree } from '@/utils/dataUtils'
import { ElMessage, ElMessageBox } from 'element-plus'
import StreamingDialog from '@/components/StreamingDialog.vue'
const menuTree = ref()
const menuData = ref([])

// 获取当前项目ID
const project_id = sessionStorage.getItem('project_id')
async function loadData() {
    if (!project_id) {
        console.error('项目ID不存在')
        return
    }
    let res = await api.queryAll(project_id)
    console.log('documents loadData res', res)
    let resData = res.data
    if (resData.code == 200) {
        menuData.value = flatToTree(resData.data)
    }
}


// 添加/编辑目录
const addOrEditModalVisible = ref(false)
const addOrEditModalTitle = ref('添加目录')
const addOrEditForm = ref({
    name: '',
})

/**
 * 显示添加目录模态框
 * @param item
 */
function addTree(item) {
    console.log('addTree item', item)
    addOrEditForm.value.name = ''
    addOrEditForm.value.parent_id = item.id
    addOrEditModalVisible.value = true
    addOrEditModalTitle.value = '添加目录'
}
/**
 * 添加根目录
 */
async function addTreeRoot() {
    console.log('addTreeRoot')
    addOrEditForm.value.name = ''
    addOrEditForm.value.parent_id = null
    addOrEditModalVisible.value = true
    addOrEditModalTitle.value = '添加根目录'
}


/**
 * 显示编辑目录模态框
 * @param item
 */
function editTree(item) {
    console.log('editTree item', item)
    // 将item中的数据复制到addOrEditForm.value中，同名替换
    Object.assign(addOrEditForm.value, item)
    addOrEditModalVisible.value = true
    addOrEditModalTitle.value = '编辑目录'
    console.log('editTree addOrEditForm', addOrEditForm.value)
}


/**
 * 保存目录
 */
async function saveTree() {
    if (!addOrEditForm.value.name) {
        ElMessage.error('请输入目录名称')
        return
    }
    try {
        let params = {
            project_id: project_id,
            parent_id: addOrEditForm.value.parent_id,
            name: addOrEditForm.value.name,
        }
        let res
        if (addOrEditForm.value.id) {
            // 编辑保存
            params.id = addOrEditForm.value.id
            // 编辑保存时，需要将编辑器中的内容赋值到params中
            params.content = vditorEditor.value.getValue()
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
            addOrEditForm.value = {
                name: '',
            }
        }
    } catch (error) {
        console.error('saveTree error', error)
        ElMessage.error('保存目录失败')
        return
    }
}


/**
 * 删除目录
 * @param item 要删除的目录项
 */
async function removeTree(node, item) {
    console.log('removeTree item', item)
    try {
        // 确认删除弹窗
        await ElMessageBox.confirm('确认删除目录吗？', '删除确认', {
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
            ElMessage.success('删除目录成功')
        }
    } catch (error) {
        console.error('removeTree error', error)
        ElMessage.error('删除目录失败')
        return
    }
}

const curMenuName = ref('')

/**
 * 处理节点点击事件
 * @param node 点击的节点
 * @param data 节点数据
 */
function handleNodeClick(node, data) {
    console.log('handleNodeClick node', node)
    console.log('handleNodeClick data', data)
    // 点击节点后，将节点数据复制到addOrEditForm.value中，同名替换
    Object.assign(addOrEditForm.value, node.source)
    console.log('handleNodeClick addOrEditForm', addOrEditForm.value)
    // 点击节点后，将节点的content赋值到编辑器中
    if (vditorEditor.value) {
        vditorEditor.value.setValue(node.source.content)
    }
    // 点击节点后，将节点的name赋值到curMenuName.value中
    curMenuName.value = node.source.name

    // 给ai_suggest赋值
    if (node.source.ai_suggest && node.source.ai_suggest != 'null') {
        // 给ai_suggest赋值
        ai_suggest.value = JSON.parse(node.source.ai_suggest || '{}')
    } else {
        ai_suggest.value = {}
    }
}

// 模态框状态
const importModalVisible = ref(false)
const replaceExisting = ref(false)
const headingLevels = ref("1")
const selectedFile = ref(null)

const handleFileChange = (file) => {
    selectedFile.value = file.raw
}


const confirmImportDocument = async () => {
    if (!selectedFile.value) {
        ElMessage.error('请选择要导入的文档')
        return
    }

    try {
        ElMessage.info('开始导入文档...')

        const formData = new FormData()
        formData.append('file', selectedFile.value)
        formData.append('project_id', project_id)
        formData.append('replace_existing', replaceExisting.value ? 'true' : 'false')
        formData.append('max_level', headingLevels.value)

        const res = await api.importDocument(formData)
        console.log('导入文档响应:', res)
        const resData = res.data

        if (resData.code === 200) {
            ElMessage.success(`成功导入`)
            loadData()
            // 重置表单状态
            selectedFile.value = null
            importModalVisible.value = false
        } else {
            ElMessage.error(resData.message || '导入失败')
        }
    } catch (error) {
        console.error('导入文档出错:', error)
        ElMessage.error('导入失败: ' + (error.message || '服务器错误'))
    }
}

// AI需求评审分析结果
const ai_results = ref({ data: {}, message: '' })
// AI评审输入的内容
const hint = ref('')
// AI需求评审模态框状态
const aiModalVisible = ref(false)
// 需求评审标签页
const activeName = ref('first')
const handleTabClick = (tab, event) => {
    // console.log(tab, event)
    activeName.value = tab.name
}

const handleAiDelete = (key) => {
    ElMessageBox.confirm('确定删除吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        delete ai_suggest.value[key]
    })
}

// 添加流式处理相关状态
const streamDialogVisible = ref(false)
const streamContent = ref('')
const streamProgress = ref(0)
const abortController = ref(null)

// 修改测试用例分析函数
const handleAnalysis = async () => {

    // 重置状态
    streamDialogVisible.value = true
    streamContent.value = ''
    streamProgress.value = 0
    ai_results.value = { data: {}, message: '' }

    const prompt_value = {
        primary_content: addOrEditForm.value.id,
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
                        ai_results.value = {
                            data: data.data,
                            message: 'AI处理成功',
                            raw_content: data.raw_content
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


// ai需求评审历史记录
const ai_suggest = ref({})
const checked_ai_suggest = ref({})
const handleAiHistoryChange = (key, value, checked) => {
    console.log("handleAiHistoryChange", key, value, checked)
    if (checked) {
        checked_ai_suggest.value[key] = value
    } else {
        delete checked_ai_suggest.value[key]
    }
}

const applySuggest = () => {
    console.log("applySuggest checked_ai_suggest.value", checked_ai_suggest.value)
    ai_suggest.value = Object.assign(ai_suggest.value, checked_ai_suggest.value)
    checked_ai_suggest.value = {}
    console.log("applySuggest ai_suggest.value", ai_suggest.value)
}

const saveSuggest = () => {
    console.log("saveSuggest ai_suggest ", ai_suggest.value)
    api.update(
        {
            id: addOrEditForm.value.id,
            ai_suggest: JSON.stringify(ai_suggest.value)
        }
    ).then(res => {
        // 获取响应数据
        const res_data = res.data
        // 取出res_data上的code和data属性
        const { code, msg } = res_data
        // code为200表示成功，这个是由开发人员设计的
        if (code == 200) {
            // 创建成功后，重新拉取项目列表
            loadData()
        }
        // 弹窗信息提示
        ElMessage.success(msg)
    })
}

/**
 * 显示AI需求评审模态框
 */
function showAiDialog() {
    if (!curMenuName.value) {
        ElMessage.warning('请选择一个需求')
        return
    }
    aiModalVisible.value = true
}

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


// 编辑器实例
const vditorEditor = ref(null)
const initEditor = () => {
    // 确保编辑器容器存在
    if (!document.getElementById('editor')) {
        console.error('Editor container not found')
        return
    }

    try {
        // height需要根据分辨率来调整，计算公式，分辨率高度-header和footer的高度-100px
        const height = window.innerHeight - 110

        // 创建Vditor实例
        vditorEditor.value = new Vditor('editor', {
            height: height,
            mode: 'wysiwyg',
            after() {
                adjustEditorSize()
                console.log('Vditor after')
            },
        })
    } catch (error) {
        console.error('Failed to initialize Vditor:', error)
    }
}


const adjustEditorSize = () => {
    if (!vditorEditor.value) return

    // 获取 el-container 和 tree-panel 元素
    const elContainer = document.querySelectorAll('.el-container')[1] // 修正选择器，避免取到多个容器
    const treePanel = document.querySelector('.tree-panel')
    if (!elContainer || !treePanel) return

    // 计算编辑器的固定宽度
    const elContainerWidth = elContainer.offsetWidth
    const treePanelWidth = treePanel.offsetWidth
    const fixedWidth = elContainerWidth - treePanelWidth - 100 // 应用100px边距
    console.log('计算后固定宽度:', fixedWidth)

    const editorElement = document.getElementById('editor')
    if (!editorElement) return

    // 设置编辑器容器固定宽度
    editorElement.style.width = `${fixedWidth}px`
    editorElement.style.maxWidth = `${fixedWidth}px` // 限制最大宽度
    editorElement.style.minWidth = `${fixedWidth}px` // 限制最小宽度
    editorElement.style.overflowX = 'hidden' // 禁止水平滚动
    editorElement.style.overflowY = 'auto'
    editorElement.style.position = 'relative'
}

// 监听窗口resize事件
window.addEventListener('resize', adjustEditorSize)

onMounted(() => {
    initEditor()
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
    width: 100px;
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
</style>