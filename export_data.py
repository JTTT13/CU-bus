import sqlite3
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, 'cuhk_bus.db')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'bus_data.json')

def export_data():
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. 抓取所有車站
    cursor.execute("SELECT id, name_zh, name_en FROM stop ORDER BY sorting_order")
    stops = [dict(row) for row in cursor.fetchall()]

    # 2. 抓取所有到站時間，並關聯路線資訊
    # 這裡我們 join route 表來取得 day_type 和路線名稱
    query = """
        SELECT 
            s.stop_id,
            s.arrival_time,
            r.name_zh as route_name,
            r.operating_day_type as day_type,
            r.remarks_zh as note
        FROM arrival_schedule s
        JOIN route r ON s.route_id = r.id
        ORDER BY s.arrival_time ASC
    """
    cursor.execute(query)
    arrivals = [dict(row) for row in cursor.fetchall()]

    final_data = {
        "stops": stops,
        "arrivals": arrivals
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"Done! Exported {len(stops)} stops and {len(arrivals)} arrival records.")
    conn.close()

if __name__ == "__main__":
    export_data()