<template>
  <v-app id="app”">
    <router-view />
  </v-app>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
}
.title {
  font-size: 2em;
  font-weight: bold;
}
.subtitle {
  font-size: 1.2em;
  font-weight: bold;
  margin: 10px;
}
.subsubtitle {
  font-size: 0.9em;
  font-weight: bold;
}
/* 定义滚动条的宽度 */
*::-webkit-scrollbar {
  width: 3px !important;
  min-width: 3px !important;
}

/* 滚动条轨道 */
*::-webkit-scrollbar-track {
  background: transparent;
}

/* 滚动条滑块 */
*::-webkit-scrollbar-thumb {
  background-color: #c5c5c5; /* 滑块颜色 */
  border-radius: 3px;
}

/* 为 Firefox 定义滚动条样式 */
* {
  scrollbar-width: thin; /* 滚动条宽度 */
  scrollbar-color: #c5c5c5 transparent; /* 滑块颜色和轨道背景色 */
  margin: 0;
  padding: 0;
}
</style>
