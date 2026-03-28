<template>
  <div class="ai-performance-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">AI性能分析</h1>
      <el-button type="primary" @click="startAnalysis" :loading="isAnalyzing">
        开始分析
      </el-button>
    </div>

    <!-- 配置区域 -->
    <el-card class="config-section" shadow="never">
      <div class="section-header">
        <h3>性能压测-监控数据源 <text style="font-size:smaller; color: blue;">(勾选即启用)</text></h3>
        <div class="action-buttons">
          <el-button type="primary" plain @click="showServerConfigDialog">
            <el-icon>
              <Monitor />
            </el-icon>
            数据源配置
          </el-button>
          <el-button type="primary" plain @click="loadData">
            <el-icon>
              <RefreshRight />
            </el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <!-- 服务器选择 -->
      <div class="server-selection">
        <el-checkbox-group v-model="selectedServers">
          <el-checkbox v-for="server in curConfig.configs" :value="server.id" :label="server.name" border>
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <!-- 时间范围选择 -->
      <div class="time-range-section">
        <h4>性能压测时间范围</h4>
        <div class="time-range-picker">
          <el-date-picker v-model="timeRange" value-format="x" type="datetimerange" range-separator="至"
            start-placeholder="开始时间" end-placeholder="结束时间" format="YYYY-MM-DD HH:mm:ss" />
        </div>
      </div>
    </el-card>

    <!-- 分析结果区域 -->
    <el-card class="result-section" shadow="never">
      <div class="section-header">
        <h3>分析结果</h3>
        <el-button type="info" plain @click="exportResults">
          <el-icon>
            <Download />
          </el-icon>
          导出报告
        </el-button>
      </div>

      <!-- 结果展示 -->
      <div v-if="analysisResults" class="result-content">
        <!-- 问题诊断 -->
        <div class="result-diagnosis">
          <el-collapse v-model="activeDiagnosisItems">
            <el-collapse-item v-for="(issue, index) in analysisResults" :key="index" :title="issue.title" :name="index">
              <div class="diagnosis-item">
                <p>{{ issue.content }}</p>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <!-- 无结果时的提示 -->
      <div v-else class="empty-result">
        <el-empty description="暂无分析结果，请配置数据源并点击开始分析">
          <el-icon :size="60">
            <DataAnalysis />
          </el-icon>
        </el-empty>
      </div>
    </el-card>

    <!-- 改进后的服务器配置对话框 -->
    <el-dialog v-model="serverConfigDialogVisible" title="监控数据源配置" width="800">

      <!-- 服务器配置表单 -->
      <el-form :model="addOrEditForm" :inline="true">
        <el-form-item label="名称" required>
          <el-input v-model="addOrEditForm.name" placeholder="请输入名称" />
        </el-form-item>

        <el-form-item required>
          <el-input v-model="addOrEditForm.source_url" placeholder="监控系统界面URL链接" />
        </el-form-item>

        <el-form-item required>
          <el-button type="success" @click="addNewServerConfig">添加</el-button>
        </el-form-item>
      </el-form>
      <!-- 服务器列表表格 -->
      <el-table :data="curConfig.configs" stripe style="width: 100%; margin-bottom: 20px;">
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="source_url" label="监控数据源地址" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click.stop="handleDelete(row.id)" icon="Delete" circle />
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button type="primary" @click="handleSave">永久保存</el-button>
      </template>
    </el-dialog>

    <StreamingDialog v-model="streamDialogVisible" title="AI处理中..." :content="streamContent" :progress="streamProgress">
    </StreamingDialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  MagicStick,
  Monitor,
  Download,
  DataAnalysis,
} from '@element-plus/icons-vue'
import api from '@/api/performance_api.js'
import StreamingDialog from '@/components/StreamingDialog.vue'

// 获取当前项目ID
const project_id = sessionStorage.getItem('project_id')

// 服务器配置

const curConfig = ref({
  id: '',
  configs: [],
  project_id: project_id
})

// 选择的服务器
const selectedServers = ref([])

// 时间范围
const timeRange = ref([])


// 加载服务器配置
const loadData = async () => {
  // 从后台获取服务器配置
  const res = await api.queryAll(project_id)
  console.log('loadData', res)
  let resData = res.data
  if (resData.code === 200 && resData.data.length > 0) {
    curConfig.value = resData.data[0]
  }
}

const serverConfigDialogVisible = ref(false)
const addOrEditForm = ref({
  id: '',
  name: '',
  source_url: '',
})
// 显示服务器配置对话框
const showServerConfigDialog = async () => {
  serverConfigDialogVisible.value = true
}

// 添加新服务器配置
const addNewServerConfig = () => {
  if (!addOrEditForm.value.name || !addOrEditForm.value.source_url) {
    ElMessage.error('请填写完整的服务器配置')
    return
  }
  // 新增，加一个ID序号
  addOrEditForm.value.id = Date.now()
  if (curConfig.value.configs) {
    curConfig.value.configs.push(addOrEditForm.value)
  }
  // 数据清空
  addOrEditForm.value = {
    id: null,
    name: '',
    source_url: ''
  }
}

// 删除服务器配置
const handleDelete = async (id) => {
  try {
    // 确认删除
    await ElMessageBox.confirm('确认删除该服务器配置吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 从配置列表中删除
    curConfig.value.configs = curConfig.value.configs.filter(server => server.id !== id)
    // 从已选列表中删除
    selectedServers.value = selectedServers.value.filter(serverId => serverId !== id)
  } catch (error) {
    // 用户取消删除
    ElMessage.info('删除操作已取消')
  }
}

// 保存服务器配置
const handleSave = async () => {
  console.log('handleSave', curConfig.value)
  if (!project_id) {
    ElMessage.error('请先选择项目')
    return
  }
  try {
    let res;
    if (curConfig.value.id) {
      // 更新
      res = await api.update(curConfig.value)
    } else {
      // 新增
      res = await api.insert(curConfig.value)
    }
    let resData = res.data
    if (resData.code === 200) {
      ElMessage.success('更新成功')
      // 关闭对话框
      serverConfigDialogVisible.value = false
      // 刷新数据
      loadData()
    }

  } catch (error) {
    ElMessage.error('保存服务器配置失败: ' + error.message)
  }
}


// 分析结果
const analysisResults = ref([])
const isAnalyzing = ref(false)
const activeDiagnosisItems = ref([])
// 流式输出对话框状态
const streamDialogVisible = ref(false);
// 流式输出内容
const streamContent = ref("");
// 流式输出进度
const streamProgress = ref(0);

/**
 * 运行AI数据生成
 */
const startAnalysis = () => {
  if (selectedServers.value.length === 0) {
    ElMessage.error('请至少选择一个监控服务器')
    return
  }
  // 显示流式输出对话框
  streamDialogVisible.value = true
  // 重置流式输出内容和进度
  streamContent.value = ""
  streamProgress.value = 0

  isAnalyzing.value = true
  // AbortController 用于取消请求
  const controller = new AbortController()
  const signal = controller.signal
  // 构建请求数据
  // 获取选中的服务器配置 - 根据selectedServers中的ID查找对应配置
  const selectedConfigs = curConfig.value.configs.filter(server =>
    selectedServers.value.includes(server.id)
  )
  // 准备API调用参数
  const data = {
    project_id: project_id,
    start_time: timeRange.value[0],
    end_time: timeRange.value[1],
    configs: JSON.stringify(selectedConfigs)
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
      // console.log('AI处理 streaming:', data)
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
      // 关闭流式输出弹窗
      streamDialogVisible.value = false
      analysisResults.value = data.data
      // 重置运行状态
      isAnalyzing.value = false
      break;
    case "error":
      ElMessage.error(data.message || "AI处理失败");
      break;
  }
}

// 导出结果
const exportResults = () => {
  if (!analysisResults.value || analysisResults.value.length === 0) {
    console.warn('没有可导出的分析结果');
    return;
  }

  // 将分析结果转换为TXT格式的字符串
  let txtContent = '性能压测分析报告\n\n';
  txtContent += `生成时间: ${new Date().toLocaleString()}\n\n`;
  txtContent += '----------------------------------------\n\n';

  analysisResults.value.forEach((item, index) => {
    txtContent += `${index + 1}. ${item.title}\n`;
    txtContent += `${item.content}\n\n`;
    txtContent += '----------------------------------------\n\n';
  });

  // 创建文件名
  const fileName = `server_analysis_${new Date().toISOString().slice(0, 10)}.txt`;

  // 创建Blob对象
  const blob = new Blob([txtContent], { type: 'text/plain' });

  // 创建下载链接
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;

  // 触发下载
  document.body.appendChild(a);
  a.click();

  // 清理
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  console.log('导出报告成功');
}

// 组件挂载时加载配置
onMounted(() => {
  loadData()
})
</script>
<style scoped>
.ai-performance-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  background: linear-gradient(135deg, #409EFF, #2c3e50);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
}

.config-section,
.result-section {
  margin-bottom: 24px;
  border-radius: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--el-text-color-primary);
}

.server-selection {
  margin: 20px 0;
}

.server-selection h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: var(--el-text-color-regular);
}

.el-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.el-checkbox {
  margin-right: 0;
}

.time-range-section {
  margin-top: 20px;
}

.time-range-section h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: var(--el-text-color-regular);
}

.time-range-picker {
  display: flex;
  align-items: center;
}

.result-content {
  margin-top: 20px;
}

.result-overview {
  margin-bottom: 30px;
}

.result-charts {
  margin-bottom: 30px;
}

.result-diagnosis {
  margin-top: 30px;
}

.diagnosis-item {
  padding: 10px;
}

.diagnosis-item p {
  margin: 0 0 10px 0;
}

.recommendations {
  margin-top: 15px;
}

.recommendations h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
}

.recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.recommendations li {
  margin-bottom: 5px;
}

.empty-result {
  padding: 40px 0;
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.el-statistic {
  text-align: center;
  padding: 15px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.el-statistic :deep(.el-statistic__content) {
  font-size: 24px;
  font-weight: bold;
}

.el-table {
  cursor: pointer;
}

.el-table :deep(.el-table__row) {
  transition: background-color 0.3s;
}

.el-table :deep(.el-table__row:hover) {
  background-color: var(--el-fill-color-light);
}
</style>