<template>
  <div
    class="d-flex flex-row align-center justify-center box"
    style="background-color: #eee"
  >
    <div class="app-container">
      <div class="side">
        <span class="title">GenColor</span>
        <div class="d-flex flex-column align-center justify-space-between">
          <span class="subtitle">Background Mode</span>
          <v-switch
            v-model="$store.state.viewmode"
            :label="`${$store.state.viewmode ? 'Dark' : 'Light'}`"
            hide-details
          ></v-switch>
        </div>
        <span class="subtitle">Query by Concept</span>
        <v-combobox
          label="Input concept"
          :items="all_concepts"
          v-model="selected_concept"
          variant="outlined"
          class="concept-input"
          autofocus
          @keyup.enter="filter_colors"
          @update:modelValue="filter_colors"
        ></v-combobox>

        <span class="subtitle">Query by Color</span>
        <v-color-picker
          elevation="0"
          v-model="targetColor"
          mode="hex"
          class="color-picker"
          hide-details
        ></v-color-picker>
        <v-btn
          flat
          class="btn"
          @click="calculateDistances"
          variant="outlined"
          style="width: 100%; margin-top: 10px"
          >get</v-btn
        >
        <v-divider></v-divider>
        <span class="subtitle">Color Detail Info</span>
        <span
          class="concept-text"
          :style="`color:${$store.state.selected_colors.innerArcColor};`"
          >{{
            this.$store.state.selected_colors.concept?.replace("_", " ")
          }}</span
        >
        <div
          class="d-flex justify-space-between colorblock"
          style="width: 100%"
        >
          <div
            v-for="color in this.$store.state.selected_colors.outerArcData"
            :key="color"
            :style="`${color.value > 50 ? 'width: 18%' : 'display:none'}`"
          >
            <div
              v-if="color.value > 50"
              @click="copy_color(color.color)"
              :style="`background-color:${color.color};height:40px;width:100%;border-radius:4px;cursor:pointer;margin:1px;text-align:center;line-height:40px;text-stroke: #fff;stroke-width: 0.5px;`"
            >
              {{ computeColorText(color.color) }}
            </div>
          </div>
        </div>
        <div
          :style="`background-color:${$store.state.selected_colors.innerArcColor};height:40px;width:100%;border-radius:4px;cursor:pointer;margin-top:10px;text-align:center;line-height:40px;font-weight:600;text-stroke: #fff;stroke-width: 0.5px;`"
          @click="copy_color($store.state.selected_colors.innerArcColor)"
        >
          {{ computeColorText($store.state.selected_colors.innerArcColor) }}
        </div>
      </div>

      <!-- <v-btn @click="saveAllDomElementsAsPng">save</v-btn> -->
      <div class="grid-container">
        <ColorPalette
          class="color-palette-item"
          v-for="(color, id) in colors"
          :colors="color"
          :key="color"
          :id="id + ''"
          @click="selectColor(color)"
        ></ColorPalette>
      </div>
    </div>
  </div>
</template>
<script>
import ColorPalette from "@/components/ColorPalette.vue";
import axios from "axios";
import * as d3 from "d3";
import html2canvas from "html2canvas";
import DeltaE from "delta-e";
import * as chromatism from "chromatism";
export default {
  name: "GalleryView",
  components: {
    ColorPalette,
  },
  mounted() {
    this.loadCSV();
    /* eslint-disable */
    // 添加这段代码：设置 viewport 以强制桌面视图
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
      viewport.setAttribute("content", "width=1200, user-scalable=yes");
    } else {
      const meta = document.createElement("meta");
      meta.name = "viewport";
      meta.content = "width=1200, user-scalable=yes";
      document.head.appendChild(meta);
    }
  },
  watch: {
    "$store.state.viewmode": function (newVal) {
      // Dynamically change the background color based on viewmode
      const appContainer = document.querySelector(".app-container");
      const side = document.querySelector(".side");
      const box = document.querySelector(".box");
      const btn = document.querySelector(".btn");

      if (newVal === true) {
        appContainer.style.backgroundColor = "#000";
        box.style.backgroundColor = "#1e1e1e";
        btn.style.backgroundColor = "#000";
        side.style.backgroundColor = "#000";
        side.style.boxShadow = "0 0 4px 0 rgba(255, 255, 255, 0.3)";
        side.style.color = "#fff";
        btn.style.color = "#fff";

        appContainer.style.color = "#fff";
      } else if (newVal === false) {
        appContainer.style.backgroundColor = "#fff";
        side.style.backgroundColor = "#fff";
        side.style.color = "#000";
        box.style.backgroundColor = "#eee";
        side.style.boxShadow = "0 0 4px 0 rgba(0, 0, 0, 0.3)";
        appContainer.style.color = "#000";
        btn.style.color = "#000";
        btn.style.backgroundColor = "#fff";
      }
      console.log(newVal);
    },
  },
  data() {
    return {
      all_colors: [],
      all_concepts: [],
      selected_concept: "",
      input: "",
      input_color: "#1976D2",
      threthold: 10,
      colors: [],
      targetColor: "rgb(112, 208, 48)",
    };
  },
  methods: {
    computeColorText(color) {
      if (color === undefined) {
        return "";
      }
      return chromatism.convert(color).hex;
    },
    selectColor(color) {
      console.log(color);
      this.$store.state.selected_colors = color;
    },
    getDeltaE(color1, color2) {
      let c1 = chromatism.convert(color1).cielab;
      let c2 = chromatism.convert(color2).cielab;
      c1.A = c1.a;
      c1.B = c1.b;
      c2.A = c2.a;
      c2.B = c2.b;
      return DeltaE.getDeltaE00(c1, c2);
    },
    copy_color(color) {
      // 嫦娥to hex
      color = chromatism.convert(color).hex;
      navigator.clipboard.writeText(color);
    },
    calculateDistances() {
      const targetHue = chromatism.convert(this.targetColor).hsv.h;

      this.colors.forEach((color) => {
        const colorHue = chromatism.convert(color.innerArcColor).hsv.h;
        const hueDifference = Math.abs(colorHue - targetHue);

        if (hueDifference <= 40) {
          const distance = this.getDeltaE(
            color.innerArcColor,
            this.targetColor
          );
          color.distance = distance;
        } else {
          color.distance = Infinity; // 设置一个很大的值，确保颜色不符合条件时排在后面
        }
      });

      this.colors.sort((a, b) => a.distance - b.distance);
      console.log(this.colors);
    },
    saveDomElementAsPng(id, e) {
      const element = document.getElementById(`photohere_${id}`);
      if (element) {
        html2canvas(element)
          .then((canvas) => {
            console.log(e);
            const link = document.createElement("a");
            link.href = canvas.toDataURL("image/png");
            link.download = `photohere_${e.concept}_${e.style}.png`;
            link.click();
          })
          .catch((error) => {
            console.error("Error capturing the element:", error);
          });
      } else {
        console.error(`Element with id photohere_${id} not found`);
      }
    },
    saveAllDomElementsAsPng() {
      this.colors.forEach((e, id) => {
        this.saveDomElementAsPng(id, e);
      });
    },
    query_concept() {
      axios
        .post("http://127.0.0.1:5000/getConcepts", {
          color: this.input_color,
          threthold: this.threthold,
        })
        .then((response) => {
          this.colors = response.data;
        });
    },

    filter_colors() {
      console.log(this.selected_concept);
      if (this.selected_concept === "" || this.selected_concept === null) {
        this.colors = this.all_colors;
      } else {
        this.colors = this.all_colors.filter((color) =>
          color.concept.includes(this.selected_concept)
        );
      }
      console.log(this.colors);
    },
    async loadCSV() {
      const csvFilePath = "all.csv"; // 根据实际文件路径修改

      try {
        // 使用d3读取CSV文件
        const data = await d3.csv(csvFilePath);
        // 将CSV数据转换为目标结构
        const result = data.map((row) => {
          // 提取颜色和数值信息
          const outerArcData = [];
          let len = 5;
          for (let i = 0; i < len; i++) {
            if (row[`color_${i}`] && row[`count_${i}`]) {
              outerArcData.push({
                color: `rgb(${row[`color_${i}`].replace(/[\[\]]/g, "")})`,
                value: parseFloat(row[`count_${i}`]),
              });
            }
          }
          this.all_concepts.push(row.concept.replace("_", " "));

          // 创建最终的对象结构
          return {
            radius: 80, // 固定半径，后期可以根据需求修改
            outerArcData: outerArcData,
            innerArcColor: `rgb(${row.color_dominant.replace(/[\[\]]/g, "")})`,
            concept: row.concept.replace("_", " "),
            style: row.style,
          };
        });

        this.all_colors = result;
        // remove repeat concepts
        this.all_concepts = Array.from(new Set(this.all_concepts));
        this.filter_colors();
        return result;
      } catch (error) {
        console.error("Error loading CSV:", error);
      }
    },
  },
};
</script>
<style>
.grid-container {
  display: flex !important;
  flex-wrap: wrap;
  overflow-y: auto;
  height: 100vh;
  margin-left: 10px;
  align-content: flex-start;
  min-width: 0;
  flex: 1;
}

.side {
  position: relative;
  top: 10px;
  left: 10px;
  width: auto;
  flex-shrink: 0;
  background-color: #fff;
  box-shadow: 0 0 4px 0 rgba(0, 0, 0, 0.3);
  padding: 20px;
  border-radius: 17px;
  margin: 20px 10px;
  display: flex;
  justify-content: start;
  height: 90vh;
  flex-direction: column;
  overflow-y: auto;
  min-width: 280px;
  max-width: 400px;
}

.app-container {
  max-width: 1600px;
  min-width: auto;
  display: flex;
  width: 100%;
  background-color: #fff;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.box {
  width: 100%;
  overflow-x: auto;
  min-height: 100vh;
}

.concept-text {
  font-size: 1.3em;
  font-weight: bold;
  margin: 10px;
  /* font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS", sans-serif; */
}
.colorblock {
  font-size: 0.7em;
  font-weight: 600;
  /* -webkit-text-stroke-width: 0.3px;
  -webkit-text-stroke-color: #fff */
}

.color-palette-item {
  margin: 8px;
  width: 180px; /* 默认中等尺寸 */
  height: 180px;
  padding: 8px;
}

.colorblock > div {
  transition: width 0.3s ease; /* 添加过渡效果 */
}

.grid-container,
.side {
  -webkit-overflow-scrolling: touch;
}

.concept-input {
  max-width: 300px;
  height: 50px;
  max-height: 50px;
}

.color-picker {
  max-width: 300px;
  width: 100%;
}
</style>
