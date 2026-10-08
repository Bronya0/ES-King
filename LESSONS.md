# Project Lessons

2026-10-02 高危 i18n 文案含裸花括号：dev 只告警、生产构建 t() 抛错，整块 DOM 消失或初始化被中断。@app/frontend/src/locales
2026-10-08 中危 Vue 组件不认识的 prop 会被静默忽略（NMenu 无 itemHeight），改动不生效、排查被误导，改用 themeOverrides。@app/frontend/src/components
2026-10-08 中危 拼 ES 路径的用户可控段未转义：# 令 query 被当 URL 片段丢弃，200+text/plain 时 resty 不反序列化，界面空表无报错。@app/backend/service
