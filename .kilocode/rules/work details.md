好，我已完整讀完代碼。以下是一次過全部修改的施工藍圖。

***

# 🛠️ Vibe Coding 施工藍圖

> **摘要**: 修正 4 個 Critical Bug + 3 個 Performance 優化 + 2 個 Code Quality 改善，共 10 個步驟

***

## 步驟 1: `paste.txt` — CSS 重複 `@keyframes timeline-pulse`
**📍 定位**: `<style>` 內，`animate-apple-spin` 定義之後
**🔧 動作**: 刪除第一組（被後者覆蓋的死碼）

> **尋找 (Search For):**
```css
        /* Apple-style Timeline Pulse Animation */
        @keyframes timeline-pulse {
          0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(0, 122, 255, 0.7);
          }
          50% {
            transform: scale(1.05);
            box-shadow: 0 0 0 4px rgba(0, 122, 255, 0);
          }
          100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(0, 122, 255, 0);
          }
        }
        
        .timeline-pulse {
          animation: timeline-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
  
        /* Smooth Scroll Behavior for Timeline */
```

> **改為 (Change To):**
```css
        /* Smooth Scroll Behavior for Timeline */
```

***

## 步驟 2: `paste.txt` — CSS 移除常駐 `will-change`
**📍 定位**: `#route-modal-card` CSS 規則
**🔧 動作**: 移除靜態 `will-change`，避免持續佔用 GPU 記憶體

> **尋找 (Search For):**
```css
        /* [Drawer Styles] Enhanced spring animation */
        #route-modal-card {
            transition: transform 0.45s cubic-bezier(0.28, 0.84, 0.42, 1),
                        opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            will-change: transform, opacity;
        }
```

> **改為 (Change To):**
```css
        /* [Drawer Styles] Enhanced spring animation */
        #route-modal-card {
            transition: transform 0.45s cubic-bezier(0.28, 0.84, 0.42, 1),
                        opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        }
```

***

## 步驟 3: `paste.txt` — HTML 修正無效 Tailwind class `z-110`
**📍 定位**: `#settings-modal` 的 `div` 元素
**🔧 動作**: 改為合法的 arbitrary value `z-[110]`

> **尋找 (Search For):**
```html
    <div id="settings-modal" class="fixed inset-0 z-110 hidden items-center justify-center">
```

> **改為 (Change To):**
```html
    <div id="settings-modal" class="fixed inset-0 z-[110] hidden items-center justify-center">
```

***

## 步驟 4: `paste.txt` — JS 新增全域變數與擴充 `db`
**📍 定位**: `let db = ...` 和 `let isStopListOpen ...` 兩行
**🔧 動作**: 加入 `segmentsByRoute` 快取欄位及 `lastUserPos` 快取變數

> **尋找 (Search For):**
```javascript
        let db = { stops: [], arrivals: [], route_times: [], routes: [], segments: [] };
```

> **改為 (Change To):**
```javascript
        let db = { stops: [], arrivals: [], route_times: [], routes: [], segments: [], segmentsByRoute: {} };
```

***

> **尋找 (Search For):**
```javascript
        let isStopListOpen = false, expandedTripId = null;
        let isFirstLoad = true;
        let fetchController = null;
        let lastCheckedDay = new Date().getDay(); // [Fix] Midnight auto-refresh
        let userPos = null; // [Stage 2] Store GPS
```

> **改為 (Change To):**
```javascript
        let isStopListOpen = false, expandedTripId = null;
        let isFirstLoad = true;
        let fetchController = null;
        let lastCheckedDay = new Date().getDay(); // [Fix] Midnight auto-refresh
        let userPos = null; // [Stage 2] Store GPS
        let lastUserPos = null; // [Perf] Distance cache invalidation sentinel
```

***

## 步驟 5: `paste.txt` — `ScheduleEngine.getArrivals` 移除重複建 Map + 修正多算一圈
**📍 定位**: `ScheduleEngine.getArrivals` 函數內
**🔧 動作**: 使用 `db.segmentsByRoute`（由 `loadData` 預建），同時修正 `endHour + 1` 多算一小時

> **尋找 (Search For):**
```javascript
                // Pre-group segments by route to avoid repetitive filtering in loops
                const segmentsByRoute = {};
                db.segments.forEach(s => {
                    if (!segmentsByRoute[s.route_id]) segmentsByRoute[s.route_id] = [];
                    segmentsByRoute[s.route_id].push(s);
                });
```

> **改為 (Change To):**
```javascript
                // [Perf] Reuse pre-built map from loadData; fallback to inline build on first call
                const segmentsByRoute = Object.keys(db.segmentsByRoute).length > 0
                    ? db.segmentsByRoute
                    : db.segments.reduce((map, s) => {
                        if (!map[s.route_id]) map[s.route_id] = [];
                        map[s.route_id].push(s);
                        return map;
                    }, {});
```

***

> **尋找 (Search For):**
```javascript
                    // Loop through each operating hour
                    for (let h = startHour; h <= endHour + 1; h++) {
```

> **改為 (Change To):**
```javascript
                    // Loop through each operating hour
                    for (let h = startHour; h <= endHour; h++) {
```

***

## 步驟 6: `paste.txt` — `loadData` 預建 `db.segmentsByRoute`
**📍 定位**: `loadData` 函數內，`if (segRes) db.segments = segRes;` 所在行
**🔧 動作**: 在 segments 載入後立即建立排序好的 route→segments Map，供後續所有函數共用

> **尋找 (Search For):**
```javascript
                if (stopRes) db.stops = stopRes;
                if (routeRes) db.routes = routeRes;
                if (segRes) db.segments = segRes;
```

> **改為 (Change To):**
```javascript
                if (stopRes) db.stops = stopRes;
                if (routeRes) db.routes = routeRes;
                if (segRes) {
                    db.segments = segRes;
                    // [Perf] Pre-build sorted lookup: { routeId: Segment[] }
                    db.segmentsByRoute = segRes.reduce((map, s) => {
                        if (!map[s.route_id]) map[s.route_id] = [];
                        map[s.route_id].push(s);
                        return map;
                    }, {});
                    Object.values(db.segmentsByRoute).forEach(segs =>
                        segs.sort((a, b) => a.expected_duration_sec - b.expected_duration_sec)
                    );
                }
```

***

## 步驟 7: `paste.txt` — `updateSettingsUI` 消除重複 i18n 迴圈
**📍 定位**: `updateSettingsUI` 函數開頭
**🔧 動作**: 移除重複的 `querySelectorAll('[data-i18n]')` 迴圈，改為呼叫現有的 `updateI18n()`

> **尋找 (Search For):**
```javascript
        window.updateSettingsUI = () => {
            // 1. Update Texts for Current Language
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (i18n[lang][key]) el.textContent = i18n[lang][key];
            });

            // 2. Theme Toggle
```

> **改為 (Change To):**
```javascript
        window.updateSettingsUI = () => {
            // 1. Update Texts for Current Language (delegates to updateI18n to avoid duplication)
            updateI18n();

            // 2. Theme Toggle
```

***

## 步驟 8: `paste.txt` — `renderStopGrid` 快取 GPS 距離計算
**📍 定位**: `renderStopGrid` 函數內，`// Stage 2: Distance Calculation` 區塊
**🔧 動作**: 只在 `userPos` 變化時重算距離並寫入 `s._cachedDist`，其餘情況直接讀取快取

> **尋找 (Search For):**
```javascript
            // Stage 2: Distance Calculation & Sorting
            filteredStops = filteredStops.map(s => {
                let dist = null;
                // 修正：確保 lat/lng 欄位匹配 (JSON uses 'lng')
                const sLong = (s.lng !== undefined) ? s.lng : s.long;
                if (userPos && s.lat && sLong) {
                    dist = getDistanceFromLatLonInKm(userPos.lat, userPos.lng, s.lat, sLong);
                }
                return { ...s, distance: dist };
            });
```

> **改為 (Change To):**
```javascript
            // Stage 2: Distance Calculation & Sorting
            // [Perf] Only recompute when GPS position actually changes
            const posChanged = userPos && (
                !lastUserPos ||
                lastUserPos.lat !== userPos.lat ||
                lastUserPos.lng !== userPos.lng
            );
            if (posChanged) {
                lastUserPos = { lat: userPos.lat, lng: userPos.lng };
                db.stops.forEach(s => {
                    const sLong = (s.lng !== undefined) ? s.lng : s.long;
                    s._cachedDist = (s.lat && sLong)
                        ? getDistanceFromLatLonInKm(userPos.lat, userPos.lng, s.lat, sLong)
                        : null;
                });
            }
            filteredStops = filteredStops.map(s => ({ ...s, distance: userPos ? (s._cachedDist ?? null) : null }));
```

***

## 步驟 9: `paste.txt` — `processAndRender` 修正污染 `db.arrivals` 原始物件
**📍 定位**: `processAndRender` 函數內的 `filtered` 建立邏輯
**🔧 動作**: 改用 `reduce` + spread，確保 `diff` 只存在於副本中，不污染 `db.arrivals`

> **尋找 (Search For):**
```javascript
            const filtered = db.arrivals.filter(arr => {
                if (arr.stop_id !== currentStopId) return false;
                const dt = arr.day_type || "";
                let isMatch = false;
                if (currentMode === 'weekday') {
                    isMatch = dt.includes('MON') || dt === 'N' || dt === '';
                } else if (currentMode === 'nonteaching') {
                    isMatch = dt.includes('MON') && !dt.includes('TEACHING');
                } else if (currentMode === 'sunday') {
                    isMatch = dt.includes('SUN') || dt.includes('HOLIDAY') || dt === 'N';
                }
                if (!isMatch) return false;
                // [Fix A] Use helper
                arr.diff = calcDiffMinutes(arr.arrival_time, currentMinutes);
                return arr.diff >= -1 && arr.diff <= 60;
            }).sort((a, b) => a.diff - b.diff);
```

> **改為 (Change To):**
```javascript
            // [Fix] Use reduce+spread to avoid mutating db.arrivals objects
            const filtered = db.arrivals.reduce((acc, arr) => {
                if (arr.stop_id !== currentStopId) return acc;
                const dt = arr.day_type || "";
                let isMatch = false;
                if (currentMode === 'weekday') {
                    isMatch = dt.includes('MON') || dt === 'N' || dt === '';
                } else if (currentMode === 'nonteaching') {
                    isMatch = dt.includes('MON') && !dt.includes('TEACHING');
                } else if (currentMode === 'sunday') {
                    isMatch = dt.includes('SUN') || dt.includes('HOLIDAY') || dt === 'N';
                }
                if (!isMatch) return acc;
                const diff = calcDiffMinutes(arr.arrival_time, currentMinutes);
                if (diff >= -1 && diff <= 60) acc.push({ ...arr, diff });
                return acc;
            }, []).sort((a, b) => a.diff - b.diff);
```

***

## 步驟 10: `paste.txt` — 移除殭屍函數 `applyTestTime()`
**📍 定位**: `window.applyTestTime` 整個函數定義
**🔧 動作**: 完整刪除，DOM 中不存在 `test-time-input` / `test-day-input`，此函數永遠無法正常執行

> **尋找 (Search For):**
```javascript
        window.applyTestTime = () => {
            const timeInput = document.getElementById('test-time-input');
            const dayInput = document.getElementById('test-day-input');
            
            if (!timeInput.value) {
                alert('請選擇測試時間');
                return;
            }
            
            testTime = timeInput.value;
            testDay = parseInt(dayInput.value);
            
            // Update URL param for backward compatibility
            const url = new URL(window.location);
            url.searchParams.set('time', testTime);
            window.history.replaceState({}, '', url);
            
            saveSettings();
            updateSettingsUI();
            loadData(); // Refresh with new test time
            
            if (navigator.vibrate) navigator.vibrate(50);
        };
```

> **改為 (Change To):**
```javascript
        // applyTestTime() removed — superseded by handleTimeChange() + setTestDay()
```
