import { createStore } from "vuex";
import axios from "axios";

export default createStore({
  state: {
    images: [],
    remoteImages: [],
    segmentImages: [],
    representativeImages: [],
    valuesImages: [],
    processingComplete: true,
    selectedSegmentImage: null,
    selectedRepresentativeImage: null,
    selectedValuesImage: null,
    selectedRepresentativeColor: null,
    prompt: "", // 添加 prompt 字段
    prompts: [], // 添加 prompts 字段
    // host: "http://10.120.18.240:31305/",
    host: "http://127.0.0.1:9999",
    relativedir: "origin/",
    // imghost: "https://semantic-color-1304458321.cos.accelerate.myqcloud.com/",
    imghost: "Case1/",
    selected_colors: [],
    viewmode: false,
  },
  mutations: {
    setImages(state, images) {
      state.images = images;
    },
    setSegmentImages(state, segmentImages) {
      state.segmentImages = segmentImages.map((url) => ({ url }));
    },
    setRepresentativeImages(state, representativeImages) {
      state.representativeImages = representativeImages.map((url) => ({ url }));
    },
    setValuesImages(state, valuesImages) {
      state.valuesImages = valuesImages.map((url) => ({ url }));
    },
    setProcessingComplete(state, status) {
      state.processingComplete = status;
    },
    removeImage(state, index) {
      state.images.splice(index, 1);
    },
    setSelectedSegmentImage(state, url) {
      state.selectedSegmentImage = url;
    },
    setSelectedRepresentativeImage(state, url) {
      state.selectedRepresentativeImage = url;
    },
    setSelectedValuesImage(state, url) {
      state.selectedValuesImage = url;
    },
    setSelectedRepresentativeColor(state, url) {
      state.selectedRepresentativeColor = url;
    },
    setPrompt(state, prompt) {
      // 添加 setPrompt mutation
      state.prompt = prompt;
    },
  },
  actions: {
    processImages({ commit, dispatch }, prompt) {
      if (prompt) {
        commit("setPrompt", prompt); // 设置 prompt
        let that = this;
        axios
          .post(this.state.host + "generate", {
            prompts: prompt,
          })
          .then((response) => {
            if (response.status === 200) {
              this.state.remoteImages = response.data;
              commit("setProcessingComplete", true); // 标记处理完成
              console.log("Images have been successfully processed!");
              dispatch("fetchOriginalImages", that.remoteImages); // 处理后立即获取原始图像
              dispatch("fetchSegmentImages"); // 同时获取分割图像
              // dispatch("fetchRepresentativeImages");
              // dispatch("fetchValuesImages");
            } else {
              console.error("Error during image processing:", response.data);
            }
          })
          .catch((error) => {
            console.error("Error during image processing:", error);
          });
      } else {
        console.log("Please enter a prompt before fetching images.");
      }
    },

    fetchOriginalImages({ commit, state }, imageNameList) {
      if (state.processingComplete) {
        commit("setImages", []);
        for (let imagepath of imageNameList) {
          axios
            .post(
              this.state.host + "/images",
              { filename: imagepath },
              { responseType: "blob" }
            )
            .then((response) => {
              if (response.data) {
                let url = URL.createObjectURL(response.data);

                let newImg = { filename: imagepath, originurl: url };
                commit("setImages", [...this.state.images, newImg]);
                console.log(this.state.images);

                console.log("Original images fetched successfully.");
              } else {
                console.error(
                  "Invalid response from fetch-images-original",
                  response.data
                );
              }
            })
            .catch((error) => {
              console.error(
                "Error fetching images from fetch-images-original",
                error
              );
            });
        }
      } else {
        console.log(
          "Waiting for image processing to complete before fetching."
        );
      }
    },

    fetchSegmentImages({ commit, state }, prompt) {
      if (state.processingComplete) {
        axios
          .post(this.state.host + "segment", { prompts: [prompt] })
          .then((response) => {
            if (response.data) {
              let url = URL.createObjectURL(response.data);
              console.log(url);
              commit("setSegmentImages", [...this.state.segmentImages, url]);
              console.log("Segment images fetched successfully.");
            } else {
              console.error("Error fetching segment images:", response.data);
            }
          })
          .catch((error) => {
            console.error("Error fetching segment images:", error);
          });
      } else {
        console.log(
          "Waiting for image processing to complete before fetching segment images."
        );
      }
    },

    fetchRepresentativeImages({ commit, state }) {
      if (state.processingComplete) {
        axios
          .get("http://127.0.0.1:5000/fetch-images-representative")
          .then((response) => {
            if (response.data && response.data.representative) {
              const fullUrls = response.data.representative.map(
                (url) => `http://127.0.0.1:5000${url}`
              );
              commit("setRepresentativeImages", fullUrls);
              console.log("Representative images fetched successfully.");
            } else {
              console.error(
                "Error fetching representative images:",
                response.data
              );
            }
          })
          .catch((error) => {
            console.error("Error fetching representative images:", error);
          });
      } else {
        console.log(
          "Waiting for image processing to complete before fetching representative images."
        );
      }
    },

    fetchValuesImages({ commit, state }) {
      if (state.processingComplete) {
        axios
          .get("http://127.0.0.1:5000/fetch-images-values")
          .then((response) => {
            if (response.data && response.data.values) {
              const fullUrls = response.data.values.map(
                (url) => `http://127.0.0.1:5000${url}`
              );
              commit("setValuesImages", fullUrls);
              console.log("Values images fetched successfully.");
            } else {
              console.error("Error fetching values images:", response.data);
            }
          })
          .catch((error) => {
            console.error("Error fetching values images:", error);
          });
      } else {
        console.log(
          "Waiting for image processing to complete before fetching values images."
        );
      }
    },
    fetchFileList({ state }, sub_dir) {
      axios
        .post(state.host + "/getFileNames", {
          base_dir: "output/Case1/" + sub_dir,
          file_type: "png",
        })
        .then((response) => {
          console.log("getFileList", response.data);
          // if end with png, then add to images
          if (response.data[0].endsWith(".png")) {
            // fetchOriginalImages
            let images = response.data.map((image) => {
              console.log("origin", sub_dir, image);
              let img = {
                origin:
                  state.imghost + state.relativedir + sub_dir + "/" + image,
                segment: state.imghost + "segment/" + sub_dir + "/" + image,
              };
              return img;
            });
            console.log("images", images);
            this.commit("setImages", images); // 更新 images
          } else {
            state.prompts = response.data;
          }
        })
        .catch((error) => {
          console.log(error);
        });
    },

    // selectImage({ commit, state }, index) {
    //   const originalImageUrl = state.images[index].url;
    //   console.log("Selected original image URL:", originalImageUrl);
    //   const imageIdMatch = originalImageUrl.match(/(\d+_\d+_\d+)\.png$/);
    //   if (imageIdMatch) {
    //     const imageId = imageIdMatch[1]; // 获取匹配的ID部分，例如 5_43_0
    //     const selectedSegmentImageUrl = state.segmentImages.find((image) =>
    //       image.url.includes(imageId)
    //     )?.url;
    //     const selectedRepresentativeImageUrl = state.representativeImages.find(
    //       (image) => image.url.includes(imageId)
    //     )?.url;
    //     const selectedValuesImageUrl = state.valuesImages.find((image) =>
    //       image.url.includes(imageId)
    //     )?.url;

    //     console.log("Matched Segment Image URL:", selectedSegmentImageUrl);
    //     console.log(
    //       "Matched Representative Image URL:",
    //       selectedRepresentativeImageUrl
    //     );
    //     console.log("Matched Values Image URL:", selectedValuesImageUrl);

    //     commit("setSelectedSegmentImage", selectedSegmentImageUrl);
    //     commit(
    //       "setSelectedRepresentativeImage",
    //       selectedRepresentativeImageUrl
    //     );
    //     commit("setSelectedValuesImage", selectedValuesImageUrl);
    //     commit(
    //       "setSelectedRepresentativeColor",
    //       selectedRepresentativeImageUrl
    //     ); // 更新代表颜色
    //   } else {
    //     console.error("Could not extract image ID from URL:", originalImageUrl);
    //   }
    // },
  },
});
