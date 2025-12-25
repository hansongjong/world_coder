import os
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

# [설계-구현 추적 매트릭스 정의]
# 명칭, 예상경로, 페이즈
ARTIFACTS_MAP = {
    "1. Database & Core": [
        {"name": "V3 Core Schema", "path": "src/core/database/v3_schema.py", "phase": "P1"},
        {"name": "Commerce Models", "path": "src/commerce/domain/models.py", "phase": "P1"},
        {"name": "Extension Models", "path": "src/commerce/domain/models_gap_v2.py", "phase": "P2.5"},
        {"name": "System Kernel", "path": "src/core/kernel.py", "phase": "P1"},
        {"name": "Security Module", "path": "src/commerce/auth/security.py", "phase": "P1"},
    ],
    "2. Business API (Backend)": [
        {"name": "Product API", "path": "src/commerce/api/products.py", "phase": "P1"},
        {"name": "Order Engine", "path": "src/commerce/api/orders.py", "phase": "P1"},
        {"name": "Booking Engine", "path": "src/commerce/api/booking.py", "phase": "P2"},
        {"name": "IoT Controller", "path": "src/commerce/api/iot.py", "phase": "P2"},
        {"name": "Delivery/P2P", "path": "src/commerce/api/delivery.py", "phase": "P2.5"},
        {"name": "Membership", "path": "src/commerce/api/membership.py", "phase": "P2.5"},
        {"name": "HR System", "path": "src/commerce/api/hr.py", "phase": "P2.5"},
        {"name": "ERP Stats", "path": "src/commerce/api/stats.py", "phase": "P3"},
    ],
    "3. Frontend (POS App)": [
        {"name": "Flutter Config", "path": "tg_pos_app/pubspec.yaml", "phase": "P1"},
        {"name": "App Entry", "path": "tg_pos_app/lib/main.dart", "phase": "P1"},
        {"name": "API Service", "path": "tg_pos_app/lib/services/api_service_v2.dart", "phase": "P2"},
        {"name": "POS Screen", "path": "tg_pos_app/lib/screens/pos_screen_v2.dart", "phase": "P2"},
        {"name": "Booking Screen", "path": "tg_pos_app/lib/screens/reservation_screen.dart", "phase": "P2"},
    ],
    "4. Infrastructure & Ops": [
        {"name": "Main App (Core)", "path": "src/main.py", "phase": "P1"},
        {"name": "Main App (Commerce)", "path": "src/main_commerce.py", "phase": "P2"},
        {"name": "Dockerfile", "path": "Dockerfile", "phase": "P4"},
        {"name": "Docker Compose", "path": "docker-compose.yml", "phase": "P4"},
        {"name": "Nginx Config", "path": "nginx/nginx.conf", "phase": "P4"},
        {"name": "Startup Script", "path": "start_system.bat", "phase": "P4"},
    ]
}

def check_artifacts():
    results = {}
    total_items = 0
    found_items = 0
    
    for category, items in ARTIFACTS_MAP.items():
        results[category] = []
        for item in items:
            full_path = BASE_DIR / item["path"]
            exists = full_path.exists()
            
            last_mod = "-"
            size = "-"
            status = "MISSING"
            
            if exists:
                found_items += 1
                status = "FOUND"
                mtime = datetime.datetime.fromtimestamp(full_path.stat().st_mtime)
                last_mod = mtime.strftime("%Y-%m-%d %H:%M")
                size = f"{full_path.stat().st_size} bytes"
            
            total_items += 1
            results[category].append({
                "name": item["name"],
                "path": item["path"],
                "phase": item["phase"],
                "status": status,
                "last_mod": last_mod,
                "size": size
            })
            
    return results, total_items, found_items

def render_html(results, total, found):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    progress = int((found / total) * 100) if total > 0 else 0
    
    table_rows = ""
    
    for category, items in results.items():
        table_rows += f'<tr class="category-row"><td colspan="5">{category}</td></tr>'
        for item in items:
            status_cls = "status-found" if item["status"] == "FOUND" else "status-missing"
            icon = "✅" if item["status"] == "FOUND" else "❌"
            table_rows += f"""
            <tr>
                <td><span class="phase-badge">{item['phase']}</span> {item['name']}</td>
                <td class="path-cell">{item['path']}</td>
                <td class="{status_cls}">{icon} {item['status']}</td>
                <td>{item['last_mod']}</td>
                <td>{item['size']}</td>
            </tr>
            """

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>TG-SYSTEM Artifact Traceability</title>
        <style>
            :root {{ --bg: #0f172a; --card-bg: #1e293b; --text: #e2e8f0; --accent: #38bdf8; --green: #22c55e; --red: #ef4444; --border: #334155; }}
            body {{ font-family: 'Consolas', 'Monaco', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
            .container {{ max_width: 1400px; margin: 0 auto; }}
            
            header {{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 30px; }}
            h1 {{ margin: 0; color: var(--accent); }}
            .meta {{ color: #94a3b8; font-size: 0.9rem; margin-top: 5px; }}
            
            .summary-card {{ background: var(--card-bg); padding: 20px; border-radius: 8px; margin-bottom: 30px; display: flex; align-items: center; justify-content: space-around; border: 1px solid var(--border); }}
            .score-box {{ text-align: center; }}
            .score-val {{ font-size: 3rem; font-weight: bold; color: var(--green); }}
            .score-label {{ text-transform: uppercase; color: #94a3b8; font-size: 0.8rem; letter-spacing: 1px; }}
            
            table {{ width: 100%; border-collapse: collapse; background: var(--card-bg); font-size: 0.9rem; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid var(--border); }}
            th {{ background: #0f172a; color: var(--accent); text-transform: uppercase; font-size: 0.8rem; }}
            
            .category-row td {{ background: #334155; color: #fff; font-weight: bold; padding: 10px; font-size: 1rem; }}
            .path-cell {{ font-family: 'Courier New', monospace; color: #94a3b8; }}
            .phase-badge {{ background: #475569; color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin-right: 8px; }}
            
            .status-found {{ color: var(--green); font-weight: bold; }}
            .status-missing {{ color: var(--red); font-weight: bold; }}
            
            footer {{ margin-top: 50px; text-align: center; color: #64748b; font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>TG-SYSTEM ARTIFACT TRACKER</h1>
                <div class="meta">Validation based on physical file existence | Generated: {now}</div>
            </header>
            
            <div class="summary-card">
                <div class="score-box">
                    <div class="score-val">{progress}%</div>
                    <div class="score-label">Traceability Score</div>
                </div>
                <div class="score-box">
                    <div class="score-val">{found}/{total}</div>
                    <div class="score-label">Artifacts Verified</div>
                </div>
                <div class="score-box">
                    <div class="score-val">V3.5</div>
                    <div class="score-label">System Version</div>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Deliverable (Module)</th>
                        <th>Physical Path</th>
                        <th>Status</th>
                        <th>Last Modified</th>
                        <th>Size</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            
            <footer>
                TG-SYSTEM Enterprise | Traceability Matrix by CODER-X
            </footer>
        </div>
    </body>
    </html>
    """

def main():
    print("[*] scanning artifacts...")
    results, total, found = check_artifacts()
    html = render_html(results, total, found)
    
    report_file = REPORT_DIR / "TG_Artifact_Report.html"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"[SUCCESS] Traceability Report Generated: {report_file}")
    print(f"    - Score: {int((found/total)*100)}% ({found}/{total} items found)")

if __name__ == "__main__":
    main()