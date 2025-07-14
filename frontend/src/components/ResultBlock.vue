<template>
  <div style="margin-top: 10px">
    <span class="subtitle">Results</span>
    <div class="function-block d-flex align-center" style="padding: 10px">
      <div style="text-align: start; width: 70%">
        <span class="title">{{ prompt }}</span> is a xxxx term and has the unify color of:
      </div>
      <div v-if="selectedRepresentativeColor" class="color-block" :style="{ backgroundImage: 'url(' + selectedRepresentativeColor + ')' }"></div>
    </div>
    <v-btn flat color="#666" style="width: -webkit-fill-available" @click="storeColor">Store</v-btn>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  computed: {
    ...mapState(['selectedRepresentativeColor', 'prompt']),
  },
  methods: {
    storeColor() {
      console.log("Storing color:", this.selectedRepresentativeColor);
      // 实现保存颜色的逻辑
    }
  }
}
</script>

<style scoped>
.placeholder {
  height: 25vh;
  background-color: #ddd;
  border-radius: 10px;
}
.color-block {
  height: 100px; /* 调整高度 */
  width: 100px;  /* 调整宽度 */
  background-size: cover; /* 确保背景图像覆盖整个块 */
  background-position: center; /* 居中背景图像 */
  border-radius: 10px;
  margin: 5px;
}
</style>
