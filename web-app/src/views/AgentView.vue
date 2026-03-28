<template>
    <div class="ai-employee-center">
        <!-- 页面标题 -->
        <div class="page-header">
            <h1 class="page-title">智能“数字员工”中心，让测试“降本增效”</h1>
            <p class="page-subtitle"></p>
        </div>

        <!-- AI员工卡片网格 -->
        <div class="ai-employee-grid">
            <el-row :gutter="20">
                <el-col v-for="employee in employees" :key="employee.id" :xs="24" :sm="12" :md="8" :lg="8"
                    class="employee-col">
                    <div class="ai-employee-card" @click="enterEmployee(employee.id)">
                        <!-- 卡片顶部装饰元素 -->
                        <div class="card-decoration">
                            <div class="tech-circle"></div>
                            <div class="tech-line"></div>
                        </div>

                        <!-- 员工头像和标题 -->
                        <div class="employee-header">
                            <div class="employee-avatar">
                                <img :src="employee.avatar" :alt="employee.name" />
                            </div>
                            <div class="employee-title">
                                <h3>{{ employee.name }}</h3>
                                <div class="ai-badge">AI</div>
                            </div>
                        </div>

                        <!-- 员工信息 -->
                        <div class="employee-info">
                            <!-- <p class="description">{{ employee.description }}</p> -->
                        </div>

                        <!-- 能力标签 -->
                        <div class="skill-tags">
                            <el-tag v-for="skill in employee.skills.slice(0, 3)" :key="skill"
                                :type="employee.type ? employee.type : 'primary'" effect="dark">
                                {{ skill }}
                            </el-tag>
                        </div>

                        <!-- 交互按钮 -->
                        <div class="action-button">
                            <el-button type="primary" round size="small">
                                立即使用
                                <el-icon class="el-icon--right">
                                    <Right />
                                </el-icon>
                            </el-button>
                        </div>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8" :lg="8" class="employee-col">
                    <div class="ai-employee-card" @click="enterEmployee(employee.id)">
                        <!-- 卡片顶部装饰元素 -->
                        <div class="card-decoration">
                            <div class="tech-circle"></div>
                            <div class="tech-line"></div>
                        </div>

                        <div
                            style="display: flex;align-items: center;flex-direction: column;justify-content: center;width: 100%;height: 100%;">
                            <el-icon :size="96">
                                <Plus />
                            </el-icon>
                            <p class="description">更多智能体数字员工，会不断更新上线</p>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { Right } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

// 获取路由实例
const router = useRouter()

// AI数字员工数据
const employees = ref([
    {
        id: 1,
        // 名称
        name: 'AI需求评审助手',
        // 头像
        avatar: 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png',
        // 描述
        description: '我是你的需求文档小管家，能快速帮你找出文档里没说清楚的地方和可能存在的问题，让需求更清晰～',
        // 技能
        skills: ['需求分析', '图文识别', '文档评审'],
        type: "warning",
        // 每个AI员工的页面对应的地址
        category: 'document',
    },
    {
        id: 2,
        name: 'AI测试用例智能体',
        avatar: 'https://cdn-icons-png.flaticon.com/512/3135/3135755.png',
        description: '我超会的写测试用例，各种测试场景信手拈来，帮你把功能验得明明白白！',
        skills: ['用例生成', '场景分析', '边界测试'],
        type: "success",
        category: 'test_case',
    },
    {
        id: 8,
        name: 'AI界面UI自动化脚本',
        avatar: 'https://cdn-icons-png.flaticon.com/512/3135/3135823.png',
        description: '点点界面这种事就不劳烦大人您了，WEB和APP都交给我，你喝杯咖啡等着出结果就好～',
        skills: ['WEB浏览器', '移动应用端', '一键 AI 测试'],
        type: "danger",
        category: 'test_case_exec',
    },
    {
        id: 3,
        name: 'AI接口文档分析',
        avatar: 'https://cdn-icons-png.flaticon.com/512/3135/3135789.png',
        description: '接口文档太复杂看不懂？我来帮你理得清清楚楚，还能揪出不合规的地方！',
        skills: ['接口解析', '文档分析', '规范检查'],
        type: "warning",
        category: 'api_document',
    },
    {
        id: 4,
        name: 'AI接口用例设计助手',
        avatar: 'https://cdn-icons-png.flaticon.com/512/3135/3135727.png',
        description: '"接口怎么测更全面？我来帮你设计测试思路，各种参数组合都不放过！',
        skills: ['接口用例', '用例设计', '参数组合'],
        type: "success",
        category: 'api_test_case',
    },
    {
        id: 6,
        name: 'AI接口自动化脚本助手',
        avatar: 'https://cdn-icons-png.flaticon.com/512/3135/3135763.png',
        description: '一键生成完成接口测试，自动断言、出报告，省心省力交给我～',
        skills: ['一键 AI 测试', '断言机制', '测试报告'],
        type: "danger",
        category: 'api_test_case_exec',
    },
    {
        id: 7,
        name: 'AI测试数据生成智能体',
        avatar: 'https://cdn-icons-png.flaticon.com/512/3135/3135773.png',
        description: '想要什么样的测试数据？跟我说，合理的数据、刁钻的数据，我都能变出来！',
        skills: ['数据生成', '规则匹配', '边界数据'],
        type: "warning",
        category: 'test_data_template',
    },
    {
        id: 10,
        name: 'AI性能数据分析助手',
        avatar: 'https://cdn-icons-png.flaticon.com/512/3135/3135805.png',
        description: '性能报告太枯燥？我来帮你分析哪里慢、为什么慢，还能给出提速小贴士！',
        skills: ['数据分析', '瓶颈定位', '优化建议'],
        type: "danger",
        category: 'performance',
    }
])

// 进入员工详情
const enterEmployee = (id) => {
    console.log(`进入AI数字员工 ${id}`)
    // 获取员工的 category
    const employee = employees.value.find(e => e.id === id)

    // 实际项目中这里应该是路由跳转
    router.push(`/main/${employee.category}`)
}
</script>

<style>
.ai-employee-center {
    max-width: 1400px;
    margin: 0 auto;
}

.page-header {
    text-align: center;
}

.page-title {
    font-size: 28px;
    font-weight: 600;
    background: linear-gradient(90deg, #409EFF, #6a11cb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.page-subtitle {
    font-size: 14px;
    color: #666;
    margin-top: 0;
}

.ai-employee-grid {
    margin-top: 15px;
}

.employee-col {
    padding: 8px !important;
    /* 增加卡片间距 */
}

.ai-employee-card {
    position: relative;
    background: white;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    margin: 8px;
    /* 增加卡片外边距 */
    overflow: hidden;
    border: 1px solid rgba(0, 0, 0, 0.05);
    cursor: pointer;
    height: 13.5vh;
    /* 减去外边距 */
    display: flex;
    flex-direction: column;
}

.ai-employee-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(64, 158, 255, 0.1);
}

.card-decoration {
    position: absolute;
    top: 0;
    right: 0;
    width: 80px;
    height: 80px;
    overflow: hidden;
}

.tech-circle {
    position: absolute;
    top: -25px;
    right: -25px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: rgba(64, 158, 255, 0.1);
}

.tech-line {
    position: absolute;
    top: 15px;
    right: 15px;
    width: 50px;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(64, 158, 255, 0.5));
    transform: rotate(45deg);
}

.employee-header {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
}

.employee-avatar {
    position: relative;
    width: 40px;
    /* 缩小头像尺寸 */
    height: 40px;
    margin-right: 12px;
    /* 增加与标题的间距 */
}

.employee-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
    border: 2px solid white;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.employee-title {
    flex: 1;
    position: relative;
}

.employee-title h3 {
    font-weight: bold;
    margin: 0;
    font-size: 16px;
    color: #df8209;
    line-height: 1.2;
}

.ai-badge {
    position: absolute;
    top: -10px;
    right: 0;
    background: linear-gradient(135deg, #6a11cb, #2575fc);
    color: white;
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 10px;
    font-weight: bold;
}

.employee-info {
    margin-bottom: 12px;
    flex-grow: 1;
}

.description {
    font-size: 14px;
    color: #666;
    line-height: 1.4;
    margin: 8px 0;
    text-align: left;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.skill-tags {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 5px;
    margin-bottom: 12px;
}

.action-button {
    text-align: center;
}

.action-button .el-button {
    width: 100%;
    background: linear-gradient(90deg, #409EFF, #6a11cb);
    border: none;
    color: white;
    font-weight: 500;
    font-size: 14px;
    padding: 8px 15px;
    height: 32px;
}

.action-button .el-button:hover {
    opacity: 0.9;
}

@media (max-width: 768px) {
    .page-title {
        font-size: 24px;
    }

    .ai-employee-card {
        padding: 12px;
    }

    .employee-col {
        padding: 4px !important;
    }
}

.project-card {
    border-radius: 12px;
    border-top: 4px solid var(--el-color-primary);
    height: 22vh;
    display: flex;
    flex-direction: column;
}


.add-card {
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background-color: #f5f7fa;
    border-top: 4px dashed var(--el-color-primary);
}

.add-card-content {
    text-align: center;
    color: var(--el-color-primary);
    padding: 20px;
}

.add-card-content i {
    margin-bottom: 10px;
}
</style>