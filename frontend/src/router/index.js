/*
 * @Author: Sunnary2604 50614684+Sunnary2604@users.noreply.github.com
 * @Date: 2023-07-06 03:09:19
 * @LastEditors: Sunnary2604 50614684+Sunnary2604@users.noreply.github.com
 * @LastEditTime: 2023-09-06 14:52:56
 * @FilePath: \LLM4Design\frontend\llm4design\src\router\index.js
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
/* eslint-disable */
import { createRouter, createWebHashHistory } from "vue-router";
// import HomeView from "../views/HomeView.vue";
// import TestView from "../views/TestView.vue";
// import MainView from "../views/MainView.vue";
const routes = [
  {
    path: "/",
    name: "main",
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/GalleryView.vue"),
  },
];

const router = createRouter({
  history: createWebHashHistory(process.env.BASE_URL),
  routes,
});

export default router;
