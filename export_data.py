import sqlite3
import json
import os

# 配置路徑
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, 'cuhk_bus.db')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def export_table(query, output_name, json_fields=None):
    """通用匯出函數"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]
        
        # 處理 JSON 字串欄位，將其轉換回 Python List/Dict
        if json_fields:
            for row in rows:
                for field in json_fields:
                    if field in row and isinstance(row[field], str):
                        try:
                            row[field] = json.loads(row[field])
                        except json.JSONDecodeError:
                            pass

        output_path = os.path.join(SCRIPT_DIR, f"{output_name}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=4)
        print(f"✅ 已匯出 {output_name}.json (共 {len(rows)} 筆資料)")
    except sqlite3.OperationalError as e:
        print(f"❌ 匯出 {output_name} 時出錯: {e}")
    finally:
        conn.close()

def run_export():
    if not os.path.exists(DB_FILE):
        print(f"錯誤: 找不到資料庫檔案 {DB_FILE}")
        return

    # 1. 匯出 stop.json (保持原樣)
    stop_query = """
        SELECT id, name_zh, name_en, lat, long as lng
        FROM stop 
    """
    export_table(stop_query, "stop")

    # 2. 匯出 route.json (根據你的新結構修改)
    # 只保留你提供的範例中有的欄位
    route_query = """
        SELECT 
            category_en, category_zh, close_time, departure_mins_json,
            has_not_standing_bus, has_standing_bus, id,
            name_en, name_zh, open_time, operating_day_type,
            remarks_en, remarks_zh
        FROM route
    """
    export_table(route_query, "route", json_fields=['departure_mins_json'])

    # 3. 匯出 route_segment.json (保持原樣)
    segment_query = """
        SELECT id, route_id, from_stop_id, to_stop_id, expected_duration_sec 
        FROM route_segment
    """
    export_table(segment_query, "route_segment")

if __name__ == "__main__":
    run_export()