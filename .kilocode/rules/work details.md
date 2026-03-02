# 🛠️ Vibe Coding 施工藍圖

> **摘要**: 將 `getArrivals()` 中秒數轉分鐘的計算由 `Math.ceil`（向上取整）改為 `Math.round`（四捨五入），統一舍入行為。

***

## 步驟 1: 修改 `ScheduleEngine.getArrivals()`
**📍 定位**: JS 內 `routeSegments.forEach(seg => ...)` 區塊
**🔧 動作**: 替換

> **尋找 (Search For):**
```javascript
                // Calculate arrival at this specific stop
                const arrivalMins = tripStartMins + Math.ceil(seg.expecteddurationsec / 60);
```

> **改為 (Change To):**
```javascript
                // Calculate arrival at this specific stop
                const arrivalMins = tripStartMins + Math.round(seg.expecteddurationsec / 60);
```

***

**就改這一行。** Timeline 本身用毫秒級 `Date` 計算，不走分鐘轉換，無需觸碰。

### 行為對比

| `expecteddurationsec` | `Math.ceil` (舊) | `Math.round` (新) |
|---|---|---|
| 30s | +1 分鐘 | +1 分鐘 (0.5 → round up) |
| 29s | +1 分鐘 | **+0 分鐘** |
| 90s | +2 分鐘 | +2 分鐘 (1.5 → round up) |
| 89s | +2 分鐘 | **+1 分鐘** |

> ⚠️ **注意副作用**：`Math.round` 對於 `< 30s` 的 segment 會捨去變成 `+0 分鐘`，如有非常短的行程（例如相鄰站 `expecteddurationsec < 30`），到達時間會與出發時間相同。建議確認 `route_segment.json` 中最短的 segment 是否 `>= 30s`。