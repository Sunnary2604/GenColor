<template>
  <div>
    <span class="title">Semantic Color</span>
    <div>
      <span class="subtitle">Dataset</span>
      <v-select
        label="Data"
        :items="$store.state.prompts"
        @click="fetchFileList('')"
        v-model="$store.state.prompt"
      ></v-select>
    </div>
    <v-divider></v-divider>
    <div>
      <span class="subtitle">Setting</span>
      <div class="d-flex flex-column align-start">
        <!-- <span class="subsubtitle">User Input Prompt</span> -->
        <div class="input-container">
          <!-- <v-text-field
            label="Input a Prompt"
            v-model="prompt"
            @keyup.enter="processImages(prompt)"
          ></v-text-field> -->
          <v-btn @click="processImages(prompt)" class="action-button"
            >Generate Images</v-btn
          >
          <v-btn @click="fetchSegmentImages(prompt)" class="action-button"
            >Segment Images</v-btn
          >
          <v-btn @click="loadImages()" class="action-button">Load Images</v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";

export default {
  data() {
    return {
      prompt: "",
    };
  },
  methods: {
    ...mapActions(["processImages", "fetchSegmentImages", "fetchFileList"]),
    loadImages() {
      this.fetchFileList(this.$store.state.prompt);

      console.log(this.$store.state.images);
    },
  },
};
</script>

<style scoped>
.v-text-field,
.v-btn {
  width: 100%;
  box-sizing: border-box;
}

.input-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.d-flex.flex-column.align-start {
  width: 100%;
}
</style>
