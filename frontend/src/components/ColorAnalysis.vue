<template>
  <div>
    <span class="subtitle">Color Analysis</span>
    <div class="chart-container">
      <div class="function-block">
        <span class="subsubtitle">Original Distribution in CIELAB</span>
        <img :src="selectedValuesImage" alt="Values Image" />
      </div>
      <div class="function-block">
        <span class="subsubtitle">Clustering Result</span>
        <img :src="selectedValuesImage" alt="Values Image" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";

export default {
  name: "ColorAnalysis",
  computed: {
    ...mapState(["selectedValuesImage"]),
  },
};
</script>

<style>
.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

#vis1,
#vis2 {
  width: 100%;
  height: 200px;
}

.function-block {
  flex: 1;
  padding: 10px;
}

img {
  max-width: 100%; /* 使图片不超过容器宽度 */
  height: auto; /* 保持图片比例 */
}
</style>
