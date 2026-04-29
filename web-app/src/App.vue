<template>
  <router-view></router-view>
</template>

<style>
/* 去除默认样式的内外边距 */
* {
  padding: 0;
  margin: 0;
}

/* 移除全局滚动条，固定页面高度 */
html,
body,
#app {
  background-color: #f4f4f4;
  height: 100vh;
  width: 100vw;
  overflow: hidden !important;
}

/* 全局美化滚动条 - 只在分区滚动时出现 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f3f4;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c6cd;
  border-radius: 3px;
  transition: all 0.2s;
}

::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>
