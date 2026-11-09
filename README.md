# 格点 · 字节 LBS 高级研发面试

面向字节跳动 LBS 方向高级研发（大约 2-1）的面试手账。打开 `public/index.html` 即可使用，不需要构建。

本地预览：

```bash
python3 -m http.server -d public 8765
```

然后访问 `http://127.0.0.1:8765`。

发布到 GitHub Pages 前，在仓库 Settings → Pages 里把 Source 选成 GitHub Actions。站点地址是 `https://wangziji.github.io/interview-bytedance/`。页面文件在 `public/`，不要选分支根目录发布。

## 里面有什么

- LBS：坐标系、距离、空间索引、Geohash / S2 / H3、POI、轨迹、地图匹配、围栏、ETA、实时位置、隐私。领域专题按执行顺序拆开代码讲解
- 算法：63 道手写题，按公开的字节高频题型整理，Java / Go / Python 同一组断言
- 语言：Java、Go、Python、Android 定位
- 后台、本地生活推荐、Agent 工具约束
- 简历追问：按本人项目准备的追问链。另有系统设计口述和自测
- 实验室：Geohash、附近点、射线法、距离衰减

掌握进度记在浏览器本地。

## 改内容之后

题解源码在 `code/`，讲解在 `site_src/`。改完运行：

```bash
python3 code/python/solutions.py
javac -d /tmp/algo-java code/java/AlgoLab.java && java -cp /tmp/algo-java AlgoLab
cd code/go && go test ./...
python3 tools/build_site.py
```

`public/js/data.js` 是生成结果，需要一起提交。
