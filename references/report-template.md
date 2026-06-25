# <change-id> Step <NN> 执行报告

## 结论

通过 / 有风险 / 需修改

## 修改文件列表

- [file](file:///absolute/path)

## Diff Summary

```bash
git diff --stat
```

关键变更：
- `<path>:Lx-Ly` — <变更内容与目的>

## 验证命令与结果

```bash
<critical/supporting command>
```

命令级别：critical / supporting

结果：

```
<output summary>
```

## 副作用与边界

- 文件外副作用：无 / 有，说明：<command/network/db/env/cache/service>
- Allow-list 状态：未越界 / 有越界，说明：<details>

## 是否偏离 Brief

无偏离 / 有偏离：<说明偏离原因及影响>

## 剩余风险

- <risk 1>
- <risk 2>
