import comp from "/Users/cody/CodeBuddy/20251209001439/docs/.vuepress/.temp/pages/index.html.vue"
const data = JSON.parse("{\"path\":\"/\",\"title\":\"微信文章集\",\"lang\":\"zh-CN\",\"frontmatter\":{},\"git\":{\"updatedTime\":1765237769000,\"contributors\":[{\"name\":\"codytang\",\"username\":\"codytang\",\"email\":\"codytang@tencent.com\",\"commits\":1,\"url\":\"https://github.com/codytang\"}],\"changelog\":[{\"hash\":\"21d6c5f63a6fa3dd1b5e0c53ca2c595b3e96de09\",\"time\":1765237769000,\"email\":\"codytang@tencent.com\",\"author\":\"codytang\",\"message\":\"first commit\"}]},\"filePathRelative\":\"README.md\"}")
export { comp, data }

if (import.meta.webpackHot) {
  import.meta.webpackHot.accept()
  if (__VUE_HMR_RUNTIME__.updatePageData) {
    __VUE_HMR_RUNTIME__.updatePageData(data)
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(({ data }) => {
    __VUE_HMR_RUNTIME__.updatePageData(data)
  })
}
