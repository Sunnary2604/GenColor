<template>
  <div :id="`photohere_${id}`">
    <div class="color_palette" :id="`cp_${id}`"></div>

    <div class="d-flex" style="justify-content: space-around">
      <div
        style="
          width: fit-content;
          padding: 4px;
          max-width: 150px;
          word-break: break-word;
        "
        class="concept"
      >
        {{ colors.concept.replace(/_/g, " ") }}
      </div>
    </div>
    <div :style="backgroundStyle" class="style">{{ colors.style }}</div>
  </div>
</template>
<script>
import * as d3 from "d3";
import { id } from "vega";
export default {
  data() {
    return {
      padding: 3,
    };
  },
  props: {
    colors: Object,
    id: String,
  },
  computed: {
    backgroundStyle() {
      // clipart: #fac03d
      // photo: # #0076ba
      // design: #888
      return {
        backgroundColor:
          this.colors.style === "clipart" ? "#fac03d" : this.colors.style === "photo" ? "#0076ba" : "#888",
        color: "#fff", // 可选：设置文本颜色为白色，以确保可读性
        padding: "4px", // 可选：增加一些填充
        borderRadius: "5px", // 可选：圆角
        width: "fit-content",
        marginTop: "5px",
        height: "fit-content",
      };
    },
  },
  mounted() {
    this.draw_color_distribution();
  },
  methods: {
    draw_color_distribution() {
      // create svg
      let svg = d3
        .select(`#cp_${this.id}`)
        .append("svg")
        .attr("width", this.colors.radius * 2 + 2 * this.padding)
        .attr("height", this.colors.radius * 1.5 + 2 * this.padding);
      let x_center = this.colors.radius + this.padding;
      let y_center = this.colors.radius * 1.5 + this.padding;
      const g = svg
        .append("g")
        .attr("transform", `translate(${x_center},${y_center})`);

      const arc = d3
        .arc()
        .innerRadius(this.colors.radius * 0.75)
        .outerRadius(this.colors.radius);

      const pie = d3
        .pie()
        .startAngle(-Math.PI / 2)
        .endAngle(Math.PI / 2)
        .value((d) => d.value)
        .sort(null);

      // 外圈
      g.selectAll("path")
        .data(pie(this.colors.outerArcData))
        .enter()
        .append("path")
        .attr("d", arc)
        .attr("fill", (d) => d.data.color);

      // 内圈
      g.append("path")
        .attr(
          "d",
          d3
            .arc()
            .innerRadius(0)
            .outerRadius(this.colors.radius * 0.75 - this.padding)
            .startAngle(-Math.PI / 2)
            .endAngle(Math.PI / 2)
        )
        .attr("fill", this.colors.innerArcColor);
    },
  },
};
</script>
<style>
.concept {
  font-size: 0.84em;
  font-weight: bold;
}
.style {
  font-size: 0.6em;
  font-weight: bold;
}
</style>
