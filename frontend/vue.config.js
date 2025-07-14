// vue.config.js
const { defineConfig } = require("@vue/cli-service");
const path = require("path");
module.exports = defineConfig({
  configureWebpack: {
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src/"), // 确保 '@' 指向 'src' 目录
      },
    },
  },
  transpileDependencies: true,
  publicPath: process.env.NODE_ENV === "production" ? "/color-concept/" : "/",

  pluginOptions: {
    vuetify: {
      // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
    },
  },
});
