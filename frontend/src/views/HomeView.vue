<template>
  <div class="grid-container">
    <div style="grid-column: 1 / 3; width: calc(3 / 12 * 100vw - 40px)">
      <SettingPannel class="main-block"></SettingPannel>
    </div>
    <div
      class="main-block"
      style="grid-column: 3 / 8; width: calc(5 / 12 * 100vw)"
    >
      <ImageGenerate></ImageGenerate>
    </div>

    <div style="grid-column: 8 / 12; width: calc(4 / 12 * 100vw)">
      <ColorAnalysis class="main-block"></ColorAnalysis>
      <ResultBlock class="main-block"></ResultBlock>
    </div>
  </div>
</template>

<script>
// @ is an alias to /src
import SettingPannel from "@/components/SettingPannel.vue";
import ImageGenerate from "@/components/ImageGenerate.vue";
import ColorAnalysis from "@/components/ColorAnalysis.vue";
import ResultBlock from "@/components/ResultBlock.vue";
//import SidebarDesign from "@/components/SidebarDesign.vue";
export default {
  name: "HomeView",
  components: {
    SettingPannel,
    ImageGenerate,
    ColorAnalysis,
    ResultBlock,
    //SidebarDesign,
  },
};
</script>
<style>
.grid-container {
  display: grid;
  column-gap: 10px;
  height: 100vh;
  background-color: #eee;
  padding: 10px;
}
.main-block {
  background-color: #fff;
  border-radius: 10px;
  height: -webkit-fill-available;

  padding: 10px;
  /* grid-area: auto; */
}
</style>
