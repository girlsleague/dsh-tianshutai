window.__ModuleLoader__.load({
  id: "dsh-tianshutai",
  factory: (require) => {
    var module = { exports: {} };
    var exports = module.exports;

    const React = require("react");
    const h = React.createElement;

    const PANEL_ID = "tianshutai";
    const ROUTE_PREFIX = "/dsh-tianshutai";

    // 需要注入的浏览器侧服务
    const inject = ["slots"];

    // 侧边栏图标（罗盘/天枢星）
    function TianshuIcon() {
      return h(
        "svg",
        {
          viewBox: "0 0 16 16",
          width: 16,
          height: 16,
          fill: "none",
          stroke: "currentColor",
          strokeWidth: 1.3,
          strokeLinecap: "round",
          strokeLinejoin: "round",
          "aria-hidden": "true",
        },
        h("circle", { cx: 8, cy: 8, r: 6 }),
        h("path", { d: "M8 2.5v2M8 11.5v2M2.5 8h2M11.5 8h2" }),
        h("path", { d: "M8 5.2l2 2.8-2 2.8-2-2.8z" })
      );
    }

    // 主面板：iframe 承载天枢台完整工作台
    function TianshuPage() {
      return h(
        "div",
        { style: { width: "100%", height: "100%", overflow: "hidden", background: "#0c0d10" } },
        h("iframe", {
          src: ROUTE_PREFIX + "/",
          title: "天枢台 · 命理中心",
          style: { width: "100%", height: "100%", border: "none", display: "block" },
        })
      );
    }

    function apply(ctx) {
      // 1) 侧边栏一级入口
      ctx.effect(() =>
        ctx.slots.inject("sidebar.panellist", () =>
          ctx.slots.register(
            {
              name: "sidebar.panellist",
              id: PANEL_ID,
              order: 5,
              label: "天枢台",
            },
            TianshuIcon
          )
        )
      );

      // 2) 主区域面板
      ctx.effect(() =>
        ctx.slots.inject("main", () =>
          ctx.slots.register({ name: "main", key: PANEL_ID }, TianshuPage)
        )
      );
    }

    exports.name = "dsh-tianshutai";
    exports.inject = inject;
    exports.apply = apply;
    return module.exports;
  },
});
