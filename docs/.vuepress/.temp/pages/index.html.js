import comp from "/Users/cody/CodeBuddy/20251209001439/docs/.vuepress/.temp/pages/index.html.vue"
const data = JSON.parse("{\"path\":\"/\",\"title\":\"微信文章集\",\"lang\":\"zh-CN\",\"frontmatter\":{},\"git\":{\"updatedTime\":1765287906000,\"contributors\":[{\"name\":\"codytang\",\"username\":\"codytang\",\"email\":\"codytang@tencent.com\",\"commits\":2,\"url\":\"https://github.com/codytang\"}],\"changelog\":[{\"hash\":\"c607bf47ce8dd3f66534befb4e1456f41f8f35a7\",\"time\":1765287906000,\"email\":\"codytang@tencent.com\",\"author\":\"codytang\",\"message\":\"重构：按公众号组织文章结构并优化导航配置\"},{\"hash\":\"21d6c5f63a6fa3dd1b5e0c53ca2c595b3e96de09\",\"time\":1765237769000,\"email\":\"codytang@tencent.com\",\"author\":\"codytang\",\"message\":\"first commit\"}]},\"filePathRelative\":\"README.md\"}")
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
