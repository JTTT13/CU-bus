import sqlite3
import json
import os

# ★★★ 修改這裡：強制使用腳本所在路徑 ★★★
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, 'cuhk_bus.db') 
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'bus_data.json')

def export_to_json():
    # 增加一行 Debug 訊息話你知佢去邊度搵
    print(f"Looking for DB at: {DB_FILE}")

    if not os.path.exists(DB_FILE):
        print(f"Error: Database file not found at that path.")
        # 列出該目錄下有甚麼檔案，幫手除錯
        print(f"Files in directory: {os.listdir(SCRIPT_DIR)}") 
        return

    print(f"Connecting to {DB_FILE}...")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # 讓我們可以用欄位名稱存取
    cursor = conn.cursor()

    try:
        # 1. 獲取所有路線 (Route)
        # 我們需要 id, name, 和 operating_day_type 來做前端過濾
        print("Fetching routes...")
        cursor.execute("""
            SELECT 
                id, 
                name_zh, 
                name_en, 
                operating_day_type, 
                remarks_zh 
            FROM route
        """)
        routes = cursor.fetchall()

        export_data = []

        for route in routes:
            route_id = route['id']
            
            # 2. 獲取該路線的所有發車時間
            # 注意：這裡假設 arrival_time 格式是 "HH:MM" 或類似
            # 我們只取第一個站的發車時間，或者所有站的時間？
            # 根據你的 index.html 邏輯，你似乎只需要一個時間代表該班次。
            # 通常 arrival_schedule 有多個 stop，我們需要過濾出「起始站」或 distinct 的班次時間。
            # 這裡我們先把所有時間拿出來，前端再處理，或者在這裡做 distinct。
            
            cursor.execute("""
                SELECT DISTINCT arrival_time 
                FROM arrival_schedule 
                WHERE route_id = ? 
                ORDER BY arrival_time ASC
            """, (route_id,))
            
            schedules = cursor.fetchall()
            time_list = [row['arrival_time'] for row in schedules]

            # 構建 JSON 物件
            route_obj = {
                "Route": route['name_zh'],  # 對應前端用的 .Route
                "RouteEn": route['name_en'],
                "RouteId": route_id,
                "DayType": route['operating_day_type'], # 關鍵：用來篩選
                "Note": route['remarks_zh'],
                "Times": time_list # 這裡放一個陣列，前端之後要展開
            }
            
            # 只有當有時間表時才加入
            if time_list:
                export_data.append(route_obj)

        # 3. 寫入 JSON
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully exported {len(export_data)} routes to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    export_to_json()