<template>
    <!-- 独立的流式输出对话框 -->
    <el-dialog :model-value="modelValue" @update:modelValue="$emit('update:modelValue', $event)" :title="title"
        width="800px" :close-on-click-modal="false" :show-close="false" :close-on-press-escape="false"
        class="streaming-dialog">
        <div class="streaming-content">
            <div class="streaming-header">
                <el-icon class="loading-icon">
                    <Loading />
                </el-icon>
                <span>{{ headerText }}</span>
            </div>

            <div ref="streamOutputRef" class="streaming-output">
                <div class="streaming-text" v-html="formattedContent"></div>
            </div>

            <div class="streaming-progress">
                <el-progress :percentage="progress" :stroke-width="2" :show-text="false" />
            </div>
        </div>
    </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Loading } from '@element-plus/icons-vue'

// 定义组件属性, 用于接收父组件传递的数据
const props = defineProps({
    modelValue: Boolean,  // 使用 modelValue 替代 visible
    title: {
        type: String,
        default: 'AI处理中...'
    },
    headerText: {
        type: String,
        default: 'AI正在处理中...'
    },
    content: String,
    progress: Number
})

// 定义事件，通过 $emit 触发，可以让子组件向父组件发送数据
const emit = defineEmits(['update:modelValue', 'cancel'])

const streamOutputRef = ref(null)

// 格式化内容（支持Markdown简单格式）
const formattedContent = computed(() => {
    return props.content
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
})

// 自动滚动到底部，监听 content 变化
watch(() => props.content, async () => {
    await nextTick()
    scrollToBottom()
})

// 滚动到底部函数
const scrollToBottom = () => {
    if (streamOutputRef.value) {
        streamOutputRef.value.scrollTo({
            top: streamOutputRef.value.scrollHeight,
            behavior: 'smooth'
        })
    }
}

// 取消按钮点击事件
const cancel = () => {
    emit('cancel')
    emit('update:visible', false)
}
</script>

<style scoped>
.streaming-dialog {
    /* 自定义对话框样式 */
}

.streaming-content {
    display: flex;
    flex-direction: column;
    height: 500px;
}

.streaming-header {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    color: #409EFF;
    font-weight: 500;
}

.loading-icon {
    margin-right: 8px;
    animation: spin 1s linear infinite;
}

.cancel-btn {
    margin-left: auto;
}

.streaming-output {
    flex: 1;
    overflow-y: auto;
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 14px;
    line-height: 1.5;
}

.streaming-progress {
    margin-top: 8px;
}

/* 自定义滚动条 */
.streaming-output::-webkit-scrollbar {
    width: 6px;
}

.streaming-output::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}

.streaming-output::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}
</style>