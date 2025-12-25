import os
import json
import re
import threading
import subprocess
from datetime import datetime
from pathlib import Path

import customtkinter as ctk
import google.generativeai as genai
from dotenv import load_dotenv

# ==========================================
# 1. 고정 환경 및 지능 로더 (config.env 완벽 연동)
# ==========================================
class CoderConfig:
    def __init__(self):
        load_dotenv("config.env")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")
        self.plan_path = Path(os.getenv("PLANNING_PATH", "TG_MASTER_BLUEPRINT"))
        self.dev_path = Path(os.getenv("DEVELOPMENT_PATH", "TG_DEVELOPMENT_WORKSPACE"))
        
        if not self.api_key:
            raise ValueError("config.env에 API 키가 없습니다.")

        self.persona = self._read_file("persona.txt", "Senior Developer Persona")
        self.instructions = self._read_file("instructions.txt", "Coding Instructions")
        self.tools = self._read_file("tools.txt", "Development Tools")

    def _read_file(self, filename, default):
        p = Path(os.getcwd()) / filename
        if not p.exists():
            p.write_text(default, encoding="utf-8")
        return p.read_text(encoding="utf-8")

    def get_system_instruction(self):
        return (
            f"{self.persona}\n\n"
            f"[CONTEXT PATHS]\n- Planning Data: {self.plan_path}\n- Development Root: {self.dev_path}\n\n"
            f"[INSTRUCTIONS]\n{self.instructions}\n\n"
            f"[TOOLS]\n{self.tools}\n\n"
            "[SYSTEM_ACCESS] 당신은 [CMD_EXEC:명령어]를 통해 실제 터미널을 제어할 권한이 있습니다."
        )

# ==========================================
# 2. 통합 저장소 및 히스토리 관리자 (복원 버그 해결)
# ==========================================
class CoderStorage:
    def __init__(self, config):
        self.config = config
        self.log_path = self.config.dev_path / "00_Dev_Logs"
        self.history_file = self.log_path / "coding_history.json"
        self._ensure_dirs()

    def _ensure_dirs(self):
        self.config.dev_path.mkdir(parents=True, exist_ok=True)
        self.log_path.mkdir(parents=True, exist_ok=True)

    def find_and_read(self, filename):
        """개발 폴더(수정용) 또는 설계 폴더(참조용)에서 파일을 찾아 읽음"""
        search_name = os.path.basename(filename)
        # 1. 개발 워크스페이스 우선 (수정 모드)
        for root, _, files in os.walk(self.config.dev_path):
            if search_name in files:
                return (Path(root) / search_name).read_text(encoding="utf-8"), "DEV_WORKSPACE"
        # 2. 설계 폴더 (참조 모드)
        for root, _, files in os.walk(self.config.plan_path):
            if search_name in files:
                return (Path(root) / search_name).read_text(encoding="utf-8"), "PLAN_DATA"
        return None, None

    def write_code(self, filename, content):
        target_path = (self.config.dev_path / filename).resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"SUCCESS: {filename} written/updated."

    def save_history(self, history):
        """히스토리 저장 시 display_role을 명시하여 로드 시 에러 방지"""
        data = []
        for h in history:
            role = h.role
            d_role = "USER" if role == "user" else "CODER"
            data.append({"role": role, "display_role": d_role, "text": h.parts[0].text})
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return []
        return []

# ==========================================
# 3. 개발/실행 통합 엔진
# ==========================================
class CoderEngine:
    def __init__(self, config):
        self.config = config
        self.storage = CoderStorage(config)
        genai.configure(api_key=self.config.api_key)
        
        self.model = genai.GenerativeModel(
            model_name=self.config.model_name,
            system_instruction=self.config.get_system_instruction()
        )
        
        history_raw = self.storage.load_history()
        # AI 모델용 포맷으로 변환
        past_history = [{"role": h.get("role", "user"), "parts": [h.get("text", "")]} for h in history_raw]
        self.session = self.model.start_chat(history=past_history)

    def execute_terminal(self, command):
        """실제 터미널 명령 수행"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                cwd=self.config.dev_path,
                capture_output=True, text=True, timeout=120, encoding='utf-8'
            )
            return f"\n[STDOUT]\n{result.stdout}\n[STDERR]\n{result.stderr}"
        except Exception as e:
            return f"\n[EXECUTION_ERROR] {str(e)}"

    def develop(self, cmd):
        # 파일 자동 탐색 및 컨텍스트 주입
        match = re.search(r'([a-zA-Z0-9_\-\./\\]+\.(?:md|txt|json|html|py|js|java|cpp|cs|go))', cmd)
        related_content = ""
        if match:
            content, source = self.storage.find_and_read(match.group(1))
            if content:
                related_content = f"\n[CONTEXT LOADED ({source})]\n{content[:4000]}"

        prompt = f"{related_content}\n\n[USER COMMAND]: {cmd}\n지시: 설계를 따르고 기존 코드를 보완한 뒤 실행 테스트를 수행하십시오."

        try:
            response = self.session.send_message(prompt)
            full_text = response.text
            
            # 1. 코드 작성 처리
            matches = re.findall(r"\[CODE_WRITE:(.*?)\](.*?)\[/CODE_WRITE\]", full_text, re.DOTALL)
            results = [self.storage.write_code(f.strip(), c.strip()) for f, c in matches]
            
            # 2. 터미널 명령 처리
            cmd_matches = re.findall(r"\[CMD_EXEC:(.*?)\]", full_text)
            for t_cmd in cmd_matches:
                t_res = self.execute_terminal(t_cmd.strip())
                full_text += f"\n\n[TERMINAL OUTPUT: {t_cmd}]{t_res}"
            
            self.storage.save_history(self.session.history)
            return full_text + ("\n\n[DEV LOGS]\n" + "\n".join(results) if results else "")
        except Exception as e:
            return f"DEVELOPMENT_FAILURE: {str(e)}"

# ==========================================
# 4. 고정 인터페이스 GUI (히스토리 복원 수정)
# ==========================================
class CoderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = CoderConfig()
        self.engine = CoderEngine(self.config)

        self.title(f"CODER-X SUPREME v5.0 | {self.config.model_name}")
        self.geometry("1200x950")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, height=50, fg_color="#1A1A1A")
        self.header.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        status_txt = f"● CODER ACTIVE | WS: {self.config.dev_path.name} | EXEC: ENABLED"
        self.lbl_status = ctk.CTkLabel(self.header, text=status_txt, text_color="#00FFCC", font=("Consolas", 14, "bold"))
        self.lbl_status.pack(side="left", padx=20)

        # Chat
        self.console = ctk.CTkTextbox(self, font=("Consolas", 14), spacing2=8, border_width=2, border_color="#222")
        self.console.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.console.configure(state="disabled")

        # Input
        self.input_area = ctk.CTkFrame(self, fg_color="transparent")
        self.input_area.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.entry = ctk.CTkEntry(self.input_area, placeholder_text="개발/수정/테스트 명령 입력...", height=65, font=("Consolas", 16))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.run_dev())

        self.btn = ctk.CTkButton(self.input_area, text="CODE EXECUTE", width=160, height=65, command=self.run_dev, font=("Impact", 16), fg_color="#C0392B")
        self.btn.pack(side="right")

        self.restore_history()
        self.add_log("SYSTEM", "수석 개발자 엔진 가동. 이전 대화 기록이 성공적으로 복구되었습니다.")

    def restore_history(self):
        """히스토리 로드 시 display_role이 없어도 안전하게 로드하도록 수정"""
        history = self.engine.storage.load_history()
        if history:
            self.console.configure(state="normal")
            for h in history:
                # 데이터 호환성 보장 로직
                sender = h.get("display_role")
                if not sender:
                    sender = "USER" if h.get("role") == "user" else "CODER"
                
                msg = h.get("text", "")
                self.add_log(sender, msg, is_past=True)
            self.console.configure(state="disabled")
            self.console.see("end")

    def add_log(self, sender, msg, is_past=False):
        self.console.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        tag_ts = ts if not is_past else "PAST"
        
        # 색상 고정
        color = "#3498db" if sender == "USER" else "#e74c3c" if sender == "CODER" else "#2ecc71"
        header = f"[{sender} | {tag_ts}]\n"
        self.console.insert("end", f"{header}{msg}\n\n" + "="*80 + "\n\n")
        
        tag_id = f"tag_{datetime.now().timestamp()}_{sender}"
        self.console.tag_add(tag_id, "end -3lines", "end -2lines")
        self.console.tag_config(tag_id, foreground=color)
        
        self.console.configure(state="disabled")
        self.console.see("end")

    def run_dev(self):
        cmd = self.entry.get()
        if not cmd: return
        self.add_log("USER", cmd)
        self.entry.delete(0, "end")
        self.lbl_status.configure(text="● CODER-X ANALYZING & TESTING...", text_color="#F1C40F")
        threading.Thread(target=self._exec, args=(cmd,), daemon=True).start()

    def _exec(self, cmd):
        res = self.engine.develop(cmd)
        self.after(0, lambda: self._finalize(res))

    def _finalize(self, res):
        self.add_log("CODER", res)
        self.lbl_status.configure(text="● CODER ONLINE", text_color="#00FFCC")

if __name__ == "__main__":
    app = CoderApp()
    app.mainloop()