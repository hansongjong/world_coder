import os
import sys
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

def analyze_project():
    stats = {
        "files": 0,
        "lines": 0,
        "modules": [],
        "commerce_api": 0,
        "core_kernel": 0,
        "docker_files": 0
    }
    
    # 소스 코드 분석
    for root, dirs, files in os.walk(SRC_DIR):
        folder = os.path.basename(root)
        if "__pycache__" in folder: continue
        
        sub_files = [f for f in files if f.endswith('.py')]
        if sub_files:
            stats["modules"].append(folder)
        
        for f in sub_files:
            file_path = Path(root) / f
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                lines = len(file.readlines())
                stats["lines"] += lines
                stats["files"] += 1
                if "commerce" in str(file_path): stats["commerce_api"] += 1
                if "core" in str(file_path): stats["core_kernel"] += 1

    # Docker/배포 관련 파일 확인
    if (BASE_DIR / "Dockerfile").exists(): stats["docker_files"] += 1
    if (BASE_DIR / "docker-compose.yml").exists(): stats["docker_files"] += 1
    if (BASE_DIR / "nginx/nginx.conf").exists(): stats["docker_files"] += 1
    if (BASE_DIR / "start_system.bat").exists(): stats["docker_files"] += 1

    return stats

def get_roadmap_status():
    return [
        {
            "phase": "PHASE 1",
            "title": "Core & Commerce",
            "progress": 100,
            "status": "COMPLETED",
            "items": [
                {"name": "통합 DB (V3 Schema)", "done": True},
                {"name": "인증/보안 (JWT)", "done": True},
                {"name": "상점/상품 API", "done": True},
                {"name": "주문 엔진", "done": True},
                {"name": "POS 앱 (Flutter Code)", "done": True}
            ]
        },
        {
            "phase": "PHASE 2",
            "title": "Expand (Booking/IoT)",
            "progress": 100,
            "status": "COMPLETED",
            "items": [
                {"name": "예약/대기 시스템", "done": True},
                {"name": "IoT 제어 API", "done": True},
                {"name": "O2O 시나리오", "done": True}
            ]
        },
        {
            "phase": "PHASE 3",
            "title": "Enterprise (ERP/Auto)",
            "progress": 80,
            "status": "IN_PROGRESS",
            "items": [
                {"name": "마케팅 봇/스케줄러", "done": True},
                {"name": "매출 통계/리포트", "done": True},
                {"name": "재고/인사 관리", "done": False}
            ]
        },
        {
            "phase": "PHASE 4",
            "title": "Deploy & Ops",
            "progress": 90,
            "status": "IN_PROGRESS",
            "items": [
                {"name": "Docker Container", "done": True},
                {"name": "Nginx Gateway", "done": True},
                {"name": "One-Click Start", "done": True},
                {"name": "CI/CD Pipeline", "done": False}
            ]
        }
    ]

def render_html(stats, roadmap):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    phases_html = ""
    
    for phase in roadmap:
        items_html = ""
        for item in phase['items']:
            icon = "✅" if item['done'] else "⬜"
            cls = "done" if item['done'] else "todo"
            items_html += f'<li class="{cls}"><span class="icon">{icon}</span> {item["name"]}</li>'
            
        color_cls = "green" if phase['status'] == "COMPLETED" else "yellow" if phase['status'] == "IN_PROGRESS" else "gray"
        
        phases_html += f"""
        <div class="card phase-card border-{color_cls}">
            <div class="phase-header">
                <h3>{phase['phase']} <span class="badge {color_cls}">{phase['status']}</span></h3>
                <span class="phase-title">{phase['title']}</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar {color_cls}" style="width: {phase['progress']}%"></div>
            </div>
            <ul class="task-list">
                {items_html}
            </ul>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>TG-SYSTEM Status Dashboard</title>
        <style>
            :root {{ --bg: #0f172a; --card-bg: #1e293b; --text: #e2e8f0; --accent: #38bdf8; --green: #22c55e; --yellow: #eab308; --gray: #64748b; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
            .container {{ max_width: 1400px; margin: 0 auto; }}
            header {{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
            h1 {{ margin: 0; color: var(--accent); }}
            .meta {{ color: var(--gray); font-size: 0.9rem; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }}
            .stat-card {{ background: var(--card-bg); padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .stat-value {{ font-size: 2.5rem; font-weight: bold; color: var(--text); }}
            .stat-label {{ color: var(--gray); text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; }}
            .roadmap-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}
            .phase-card {{ background: var(--card-bg); padding: 25px; border-radius: 10px; border-top: 5px solid; }}
            .border-green {{ border-color: var(--green); }} .border-yellow {{ border-color: var(--yellow); }} .border-gray {{ border-color: var(--gray); }}
            .badge {{ font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; color: #000; }}
            .badge.green {{ background: var(--green); }} .badge.yellow {{ background: var(--yellow); }} .badge.gray {{ background: var(--gray); }}
            .progress-container {{ background: #334155; height: 8px; border-radius: 4px; margin: 15px 0; overflow: hidden; }}
            .progress-bar {{ height: 100%; }}
            .progress-bar.green {{ background: var(--green); }} .progress-bar.yellow {{ background: var(--yellow); }}
            .task-list {{ list-style: none; padding: 0; margin: 0; }}
            .task-list li {{ padding: 8px 0; border-bottom: 1px solid #334155; display: flex; align-items: center; font-size: 0.9rem; }}
            .task-list li.done {{ color: var(--green); }} .task-list li.todo {{ color: var(--gray); }}
            .icon {{ margin-right: 10px; }}
            footer {{ margin-top: 50px; text-align: center; color: var(--gray); font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div>
                    <h1>TG-SYSTEM LIVE DASHBOARD</h1>
                    <div class="meta">Architect: CODER-X | Update: Phase 4 Deployed</div>
                </div>
                <div class="meta">Last Scan: {now}</div>
            </header>
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-value">{stats['files']}</div><div class="stat-label">Python Files</div></div>
                <div class="stat-card"><div class="stat-value">{stats['lines']}</div><div class="stat-label">Total Lines</div></div>
                <div class="stat-card"><div class="stat-value">{stats['commerce_api']}</div><div class="stat-label">Commerce APIs</div></div>
                <div class="stat-card"><div class="stat-value">{stats['docker_files']}</div><div class="stat-label">Docker Configs</div></div>
            </div>
            <h2 style="color: var(--text); border-left: 5px solid var(--accent); padding-left: 15px;">Project Roadmap & Status</h2>
            <div class="roadmap-grid">
                {phases_html}
            </div>
            <footer>TG-SYSTEM Enterprise | Powered by CODER-X Engine</footer>
        </div>
    </body>
    </html>
    """

def main():
    print("[*] Updating Dashboard Status...")
    stats = analyze_project()
    roadmap = get_roadmap_status()
    html_content = render_html(stats, roadmap)
    
    report_file = REPORT_DIR / "TG_Dev_Report.html"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[SUCCESS] Dashboard Updated: {report_file}")

if __name__ == "__main__":
    main()