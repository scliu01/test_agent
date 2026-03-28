<template>
    <!-- 已移除的组件 -->
    <div class="data-generator-container">
        <!-- 页面标题 -->
        <div class="page-header">
            <h1 class="page-title">AI测试数据生成系统</h1>
            <div class="header-actions">
                <el-button type="primary" @click="runGeneration" :icon="VideoPlay" :loading="isRunning">
                    运行生成
                </el-button>
                <el-button type="success" @click="saveAsTemplate" :icon="FolderAdd">
                    保存为模板
                </el-button>
                <el-button type="info" @click="showTemplateDialog" :icon="FolderOpened">
                    加载模板
                </el-button>
            </div>
        </div>
        <!-- 主配置区域 -->
        <div class="main-config-area">
            <!-- 基础配置 -->
            <div class="config-section base-config">
                <el-row :gutter="20">
                    <el-col :span="4">
                        <h3 class="section-title">
                            <el-icon>
                                <Setting />
                            </el-icon>
                            <span>基础配置</span>
                        </h3>
                    </el-col>
                    <el-col :span="4">
                        <el-form-item label="数据量">
                            <el-input-number v-model="config.data_count" :min="1" :max="100000"
                                controls-position="right" />
                        </el-form-item>
                    </el-col>
                    <el-col :span="4">
                        <el-form-item label="数据格式">
                            <el-select v-model="config.format" placeholder="选择格式" @change="handleFormatChange">
                                <el-option v-for="format in formatOptions" :key="format.value" :label="format.label"
                                    :value="format.value" />
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="4">
                        <el-form-item label="语言">
                            <el-select v-model="config.language" placeholder="选择语言">
                                <el-option v-for="lang in languageOptions" :key="lang.value" :label="lang.label"
                                    :value="lang.value" />
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>
            </div>

            <!-- 结果示例参考 -->
            <div class="config-section example-config">
                <h3 class="section-title">
                    <el-icon>
                        <DataLine />
                    </el-icon>
                    <span>结果示例参考</span>
                </h3>
                <el-input v-model="exampleResult" type="textarea" :rows="4" placeholder="输入你期望的结果示例(hint字段)" />
            </div>

            <!-- 字段配置 -->
            <div class="config-section fields-config">
                <div class="section-header">
                    <h3 class="section-title">
                        <el-icon>
                            <List />
                        </el-icon>
                        <span>字段配置</span>
                    </h3>
                    <el-button type="primary" plain @click="addField" :icon="Plus">
                        添加字段
                    </el-button>
                </div>

                <div class="fields-list">
                    <div v-for="(field, index) in config.fields" :key="index" class="field-item">
                        <div class="field-content">
                            <div class="field-name">
                                <el-input v-model="field.name" placeholder="字段名" size="default" style="width: 180px" />
                            </div>
                            <div class="field-type">
                                <el-select v-model="field.type" placeholder="选择类型" size="default" style="width: 150px"
                                    filterable>
                                    <el-option v-for="type in fieldTypeOptions" :key="type.value" :label="type.label"
                                        :value="type.value" />
                                </el-select>
                            </div>
                            <div class="field-desc">
                                <el-input v-model="field.description"
                                    :placeholder="getDescriptionPlaceholder(field.type)" size="default" />
                            </div>
                            <div class="field-actions">
                                <el-button type="danger" :icon="Delete" circle plain @click="removeField(index)" />
                            </div>
                        </div>

                        <div v-if="field.type === 'custom'" class="custom-prompt">
                            <el-input v-model="field.customRule" type="textarea" :rows="2" size="default"
                                placeholder="详细描述你希望生成的数据规则" />
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 结果展示区域 -->
        <div class="result-section">
            <div class="result-header">
                <h3 class="section-title">
                    <el-icon>
                        <DataLine />
                    </el-icon>
                    <span>生成结果</span>
                </h3>
                <div class="result-actions">
                    <el-button @click="copyResult" :icon="DocumentCopy">
                        复制{{ config.format === 'json' ? 'JSON' : 'SQL' }}
                    </el-button>
                    <el-button @click="downloadResult" :icon="Download">
                        下载文件
                    </el-button>
                </div>
            </div>

            <div class="result-content">
                <el-alert :title="'生成成功，耗时' + generationTime + '秒'" type="success" :closable="false"
                    class="result-alert">
                </el-alert>

                <div class="result-preview">
                    <div class="preview-container">
                        <div class="preview-header">
                            <span class="preview-title">{{ config.format.toUpperCase() }} 预览</span>
                        </div>
                        <pre class="preview-content">{{ formattedResult }}</pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- 模板选择对话框 -->
    <el-dialog v-model="templateDialogVisible" title="选择模板" width="800px">
        <el-table :data="templates" style="width: 100%">
            <el-table-column prop="name" label="模板名称" width="200" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="操作" width="200">
                <template #default="{ row }">
                    <el-button type="danger" size="small" @click="handleDeleteTemplate(row.id)">删除</el-button>
                    <el-button type="primary" size="small" @click="selectTemplate(row)">应用</el-button>
                </template>
            </el-table-column>
        </el-table>
    </el-dialog>
    <!-- 保存模板对话框 -->
    <el-dialog v-model="saveTemplateDialogVisible" title="保存为模板" width="500px">
        <el-form :model="templateForm" label-width="100px">
            <el-form-item label="模板名称" required>
                <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
            </el-form-item>
            <el-form-item label="模板描述">
                <el-input v-model="templateForm.description" type="textarea" :rows="3" placeholder="请输入模板描述（可选）" />
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="saveTemplateDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmSaveTemplate">保存</el-button>
        </template>
    </el-dialog>
    <StreamingDialog v-model="streamDialogVisible" title="AI处理中..." :content="streamContent" :progress="streamProgress">
    </StreamingDialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
// 移除已删除的组件导入
import { ElMessage, ElNotification } from 'element-plus'
import {
    VideoPlay,
    FolderAdd,
    FolderOpened,
    DocumentCopy,
    Download,
    Setting,
    List,
    Plus,
    Delete,
    DataLine
} from '@element-plus/icons-vue';

import api from '@/api/test_data_template_api.js'
import StreamingDialog from '@/components/StreamingDialog.vue'


// 配置选项
const formatOptions = [
    { value: 'json', label: 'JSON' },
    { value: 'sql', label: 'SQL' }
]

const languageOptions = [
    { value: 'zh', label: '中文' },
    { value: 'en', label: '英文' },
    { value: 'ja', label: '日文' },
    { value: 'multi', label: '多语言' }
]

const fieldTypeOptions = [
    { value: 'string', label: '字符串' },
    { value: 'number', label: '数字' },
    { value: 'boolean', label: '布尔值' },
    { value: 'date', label: '日期' },
    { value: 'datetime', label: '日期时间' },
    { value: 'name', label: '姓名' },
    { value: 'email', label: '邮箱' },
    { value: 'phone', label: '电话' },
    { value: 'address', label: '地址' },
    { value: 'text', label: '文本' },
    { value: 'id', label: 'ID' },
    { value: 'url', label: 'URL' },
    { value: 'image', label: '图片URL' },
    { value: 'custom', label: '自定义' }
]

// 主配置数据
const config = reactive({
    data_count: 100,
    format: 'json',
    language: 'zh',
    fields: [
        {
            name: '',
            type: '',
            description: ''
        }
    ]
})
// 处理格式变化的方法
const handleFormatChange = (value) => {
    // 清空当前生成结果
    // generationResult.value = null
    // 可以在这里添加其他格式切换逻辑
    ElMessage.info(`已切换数据格式为: ${value}`)
}


// UI状态
const isRunning = ref(false)
const exampleResult = ref('')

// 方法
const getDescriptionPlaceholder = (type) => {
    const placeholders = {
        string: '例如：4-16位字母数字组合的用户名',
        number: '例如：范围在18-99之间的整数',
        boolean: '例如：表示用户是否激活的状态',
        date: '例如：用户的出生日期，格式YYYY-MM-DD',
        datetime: '例如：用户注册时间，格式YYYY-MM-DD HH:mm:ss',
        name: '例如：中文或英文姓名',
        email: '例如：有效的电子邮箱地址',
        phone: '例如：11位手机号码，以1开头',
        address: '例如：完整的邮寄地址，包含省市区',
        text: '例如：商品详细描述，50-500字',
        id: '例如：唯一标识符，UUID格式',
        url: '例如：完整的网址，包含http://或https://',
        image: '例如：图片URL，尺寸800x600',
        custom: '详细描述你希望生成的数据规则'
    }
    return placeholders[type] || '描述该字段的生成规则'
}

const addField = () => {
    // 使用新数组方式确保响应式更新
    config.fields = [...config.fields, {
        name: '',
        type: 'string',
        description: ''
    }]
}

const removeField = (index) => {
    if (config.fields.length > 1) {
        config.fields.splice(index, 1)
    } else {
        ElMessage.warning('至少需要保留一个字段')
    }
}

// 从sessionStorage中获取项目ID
const project_id = sessionStorage.getItem('project_id')
const saveTemplateDialogVisible = ref(false)
// 表单数据
const templateForm = reactive({
    name: '',
    description: ''
})

const saveAsTemplate = () => {
    // 验证字段配置
    for (const field of config.fields) {
        if (!field.name.trim()) {
            ElMessage.error(`字段 ${config.fields.indexOf(field) + 1} 的名称不能为空`)
            return
        }
    }

    templateForm.name = ''
    templateForm.description = ''
    saveTemplateDialogVisible.value = true
}

const confirmSaveTemplate = async () => {
    if (!templateForm.name.trim()) {
        ElMessage.error('模板名称不能为空')
        return
    }
    if (!project_id) {
        ElMessage.error('请先选择项目')
        return
    }

    // 创建新模板
    const newTemplate = {
        name: templateForm.name,
        project_id: project_id,
        description: templateForm.description,
        fields: JSON.parse(JSON.stringify(config.fields)),
        hint: exampleResult.value,
        // 保存完整配置到模板
        count: config.data_count,
        format: config.format,
        lang: config.language
    }

    try {
        const res = await api.insert(newTemplate)
        const resData = res.data
        if (resData.code === 200) {
            ElMessage.success('模板保存成功')
            saveTemplateDialogVisible.value = false
            loadTemplates() // 保存成功后重新加载模板列表
        } else {
            ElMessage.error('模板保存失败: ' + res.msg)
        }
    } catch (error) {
        ElMessage.error('模板保存失败: ' + error.message)
    }
}

// 模板数据
const templates = ref([])
const templateDialogVisible = ref(false)

// 加载模板数据
const loadTemplates = async () => {
    try {
        console.log('project_id:', project_id)
        const response = await api.queryAll(project_id);
        const resData = response.data;
        console.log('加载模板数据:', response)
        // 直接使用响应数据作为模板数组（假设API返回直接是数组）
        if (resData.code === 200) {
            templates.value = resData.data
        }
        if (templates.value.length === 0) {
            ElMessage.info('未找到模板数据，请先创建模板')
        }
    } catch (error) {
        ElMessage.error('加载模板失败: ' + error.message)
    }
}

// 页面加载时自动加载模板
// loadTemplates()

/**
 * 显示所有模板对话框
 */
const showTemplateDialog = () => {
    templateDialogVisible.value = true
    loadTemplates()
}


/**
 * 选择模板
 * @param template 
 */
const selectTemplate = (template) => {
    console.log("选择模板:", template);

    // 加载完整配置到统一的config对象
    config.data_count = template.count || 100
    config.format = template.format || 'json'
    config.language = template.language || 'zh'
    config.fields = JSON.parse(JSON.stringify(template.fields || []))
    exampleResult.value = template.hint || ''
    templateDialogVisible.value = false
    ElMessage.success(`已加载模板 "${template.name}"`)
}

/**
 * 删除模板
 * @param id 
 */
const handleDeleteTemplate = async (id) => {
    try {
        const deleteRes = await api.deleteById(id);
        const resData = deleteRes.data;
        if (resData.code === 200) {
            ElMessage.success('模板删除成功');
            loadTemplates()
        } else {
            ElMessage.error(`删除失败: ${resData.message}`);
        }
        // templates.value = templates.value.filter(template => template.id !== id);
    } catch (error) {
        ElMessage.error(`删除失败: ${error.message}`);
    }
};

// 流式输出对话框状态
const streamDialogVisible = ref(false);
// 流式输出内容
const streamContent = ref("");
// 流式输出进度
const streamProgress = ref(0);

// 最终ai生成结果
const generationResult = ref(null)
// 生成所耗时间（秒）
const generationTime = ref(0)
let startTime = 0 // 记录开始时间
const formattedResult = computed(() => {
    if (!generationResult.value) return ''

    if (config.format === 'json') {
        return JSON.stringify(generationResult.value, null, 2)
    } else if (config.format === 'sql') {
        return generationResult.value
    }
    return ''
})

/**
 * 运行AI数据生成
 */
const runGeneration = () => {
    // 验证基础配置和字段配置
    if (exampleResult.value && exampleResult.value.length > 500) {
        ElMessage.warning('结果示例参考内容过长，建议控制在500字符以内')
    }

    // 验证字段配置
    for (const field of config.fields) {
        if (!field.name.trim()) {
            ElMessage.error(`字段 ${config.fields.indexOf(field) + 1} 的名称不能为空`)
            return
        }
        if (!field.description.trim()) {
            ElMessage.error(`字段 ${field.name} 的描述不能为空`)
            return
        }
        if (field.type === 'custom' && !field.customRule?.trim()) {
            ElMessage.error(`自定义字段 ${field.name} 的规则不能为空`)
            return
        }
    }
    // 显示流式输出对话框
    streamDialogVisible.value = true
    // 重置流式输出内容和进度
    streamContent.value = ""
    streamProgress.value = 0
    startTime = Date.now() // 记录开始时间

    isRunning.value = true
    // AbortController 用于取消请求
    const controller = new AbortController()
    const signal = controller.signal
    // 构建请求数据
    const data = {
        data_count: config.data_count,
        format: config.format,
        language: config.language,
        example_result: exampleResult.value,
        fields: config.fields,
        project_id: project_id
    }

    // 调用API处理流式数据
    api.processWithAIStream(data, {
        onMessage,
        onError: (error) => {
            ElMessage.error(error.message || "AI处理失败");
        },
        onComplete: () => {
            // 处理完成后的操作，例如关闭弹窗
            streamDialogVisible.value = false
        },
        signal
    })
}

/**
 * 处理AI流数据
 * @param {Object} data - 从AI流返回的数据
 */
const onMessage = (data) => {
    switch (data.status) {
        case "start":
            console.log('AI处理 start:', data)
            streamContent.value += data.content
            break;
        case "streaming":
            console.log('AI处理 streaming:', data)
            // 更新流式输出内容和进度
            streamContent.value += data.content
            // 根据内容长度估算进度
            if (data.full_content.length > 100) {
                streamProgress.value = Math.min(
                    95,
                    Math.floor((data.full_content.length / 2000) * 100)
                );
            }
            break;
        case "completed":
            console.log("AI处理成功：", data.data);
            streamProgress.value = 100
            // 记录结束时间
            const endTime = Date.now()
            // 计算生成时间（秒）
            generationTime.value = (endTime - startTime) / 1000
            // 保存生成结果
            generationResult.value = data.data
            // 关闭流式输出弹窗
            streamDialogVisible.value = false
            // 重置运行状态
            isRunning.value = false
            break;
        case "error":
            ElMessage.error(data.message || "AI处理失败");
            break;
    }
}


// 复制结果到剪贴板
const copyResult = () => {
    if (!generationResult.value) {
        ElMessage.warning('没有可复制的数据')
        return
    }
    // 复制格式化后的结果到剪贴板
    navigator.clipboard.writeText(formattedResult.value).then(() => {
        ElMessage.success(`已复制${config.format === 'json' ? 'JSON' : 'SQL'}数据到剪贴板`)
    })
}

// 下载结果文件
const downloadResult = () => {
    if (!generationResult.value) {
        ElMessage.warning('没有可下载的数据')
        return
    }

    let content = formattedResult.value
    let fileName = `test_data_${new Date().toISOString().slice(0, 10)}.${config.format}`
    let mimeType = config.format === 'json' ? 'application/json' : 'text/sql'

    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fileName
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    ElMessage.success(`已下载文件: ${fileName}`)
}
</script>

<style scoped>
.data-generator-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    background-color: var(--el-bg-color-page);
    border-radius: 12px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0px !important;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--el-border-color-light);
}

.page-title {
    font-size: 28px;
    font-weight: 600;
    background: linear-gradient(135deg, #409EFF, #2c3e50);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}

.header-actions {
    display: flex;
    gap: 10px;
}

.main-config-area {
    background-color: var(--el-bg-color);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.section-title {
    display: flex;
    align-items: center;
    font-size: 18px;
    color: var(--el-text-color-primary);
    margin: 10px;
}

.section-title .el-icon {
    margin-right: 8px;
    color: var(--el-color-primary);
}

.fields-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.field-item {
    background-color: var(--el-bg-color-page);
    border-radius: 6px;
    padding: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.field-content {
    display: flex;
    align-items: center;
    gap: 10px;
}

.field-name,
.field-type,
.field-desc {
    flex: 1;
    min-width: 0;
}

.field-desc {
    flex: 3;
}

.field-actions {
    flex-shrink: 0;
}

.custom-prompt {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed var(--el-border-color-light);
}

.result-section {
    background-color: var(--el-bg-color);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.result-actions {
    display: flex;
    gap: 10px;
}

.result-content {
    margin-top: 15px;
}

.result-alert {
    margin-bottom: 20px;
}

.result-preview {
    max-height: 500px;
    overflow-y: auto;
}

.preview-container {
    border: 1px solid var(--el-border-color-light);
    border-radius: 4px;
    background-color: var(--el-bg-color-page);
}

.preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    border-bottom: 1px solid var(--el-border-color-light);
    background-color: var(--el-fill-color-light);
}

.preview-title {
    font-weight: bold;
    color: var(--el-text-color-primary);
}

.preview-content {
    padding: 15px;
    margin: 0;
    white-space: pre-wrap;
    font-family: 'Courier New', Courier, monospace;
    line-height: 1.5;
    color: var(--el-text-color-primary);
    background-color: transparent;
    overflow-x: auto;
}

/* SQL语法高亮 */
.preview-content {
    color: #333;
}

.preview-content .keyword {
    color: #0077aa;
    font-weight: bold;
}

.preview-content .string {
    color: #669900;
}

.preview-content .comment {
    color: #999988;
    font-style: italic;
}

.preview-content .number {
    color: #990055;
}

/* 响应式调整 */
@media (max-width: 992px) {
    .field-content {
        flex-wrap: wrap;
        row-gap: 8px;
    }

    .field-name,
    .field-type {
        flex: 0 0 calc(50% - 5px);
    }

    .field-desc {
        flex: 0 0 100%;
    }
}

@media (max-width: 768px) {
    .page-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .header-actions {
        width: 100%;
        justify-content: flex-end;
    }

    .field-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }

    .field-name,
    .field-type,
    .field-desc {
        width: 100%;
    }

    .field-actions {
        align-self: flex-end;
    }

    .result-actions {
        flex-direction: column;
        align-items: flex-end;
        gap: 8px;
    }
}
</style>