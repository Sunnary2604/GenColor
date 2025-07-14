<template>
  <div>
    <div class="function-block">
      <span class="subtitle">Image Generation</span>
      <v-btn-toggle
        v-model="text"
        color="deep-purple-accent-3"
        rounded="0"
        group
      >
        <v-btn value="origin" @click="imgMode = 'origin'"> origin </v-btn>

        <v-btn value="segment" @click="imgMode = 'segment'"> segment </v-btn>
      </v-btn-toggle>
      <div
        style="
          display: flex;
          flex-wrap: wrap;
          width: 100%;
          align-content: space-around;
          justify-content: space-around;
          max-height: 37vh;
          overflow-y: scroll;
        "
      >
        <div v-for="(image, index) in images" :key="index">
          <v-card flat class="image-block">
            <v-card-text>
              <v-img
                v-if="imgMode == 'origin'"
                cover
                aspect-ratio="1"
                :src="image.origin"
              ></v-img>
              <v-img
                v-if="imgMode == 'segment'"
                cover
                aspect-ratio="1"
                :src="image.segment"
              ></v-img>
            </v-card-text>
            <v-card-actions>
              <v-btn
                @click.stop="removeImage(index)"
                density="compact"
                icon="mdi-delete"
              ></v-btn>
            </v-card-actions>
          </v-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from "vuex";

export default {
  computed: {
    ...mapState([
      "images",
      "segmentImages",
      "selectedSegmentImage",
      "selectedRepresentativeImage",
      "selectedValuesImage",
    ]),
  },
  data() {
    return {
      imgMode: "segment",
    };
  },
  methods: {
    ...mapActions([
      "fetchOriginalImages",
      "fetchSegmentImages",
      "fetchRepresentativeImages",
      "fetchValuesImages",
    ]),
    removeImage(index) {
      this.$store.commit("removeImage", index);
    },
    // selectImage(index) {
    //   this.$store.dispatch("selectImage", index);
    // },
  },
  created() {
    // set image
    // this.getFileList();
  },
};
</script>

<style scoped>
.image-grid {
  display: flex;
  flex-wrap: wrap;
  width: 100%;
  align-content: space-around;
  justify-content: space-around;
}

.image-hover:hover {
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.8); /* 显示白色阴影以高亮 */
}

.segment-display {
  display: flex;
  flex-direction: column;
  align-items: center; /* 垂直居中 */
  justify-content: center; /* 水平居中 */
  margin-top: 20px;
  width: 100%; /* 确保容器宽度是100% */
}

.segment-image {
  max-width: 400px;
  max-height: 400px;
  margin: auto; /* 添加 margin auto 来居中图像 */
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5); /* 给分割图像添加阴影 */
}

.image-block {
  border-radius: 5px;
  height: calc(7.5vw + 30px);
  width: 7.5vw;
  margin: 2px;
  border: 1px solid #ccc;
  transition: transform 0.2s ease-in-out, opacity 0.2s ease-in-out; /* 增加动画时间使变换更流畅 */
  opacity: 1; /* 默认完全不透明 */
}

.v-card-text {
  padding: 0;
}

.v-card-actions {
  min-height: 0;
  padding: 2px;
  justify-content: flex-end;
}
</style>
