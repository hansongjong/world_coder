import os
import json
import re
import threading
from datetime import datetime
from pathlib import Path

import customtkinter as ctk
import google.generativeai as genai
from dotenv import load_dotenv

# ==========================================
# 1. 고정 환경 설정 로더
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
            f"[TOOLS]\n{self.tools}"
        )

# ==========================================
# 2. 개발 워크스페이스 및 기억 저장소
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

    def read_plan_file(self, filename):
        """설계 폴더에서 파일을 찾아 내용을 읽음"""
        search_name = os.path.basename(filename)
        for root, _, files in os.walk(self.config.plan_path):
            if search_name in files:
                return (Path(root) / search_name).read_text(encoding="utf-8")
        return None

    def write_code(self, filename, content):
        """개발 폴더 내에 소스 코드 작성"""
        target_path = (self.config.dev_path / filename).resolve()
        # 보안: 개발 폴더 외부로 나가는 것 방지
        if not str(target_path).startswith(str(self.config.dev_path.resolve())):
            return f"ERROR: Security Breach - Path traversal blocked."
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"SUCCESS: {filename} has been developed."

    def save_history(self, history):
        data = [{"role": h.role, "text": h.parts[0].text} for h in history]
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_history(self):
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

# ==========================================
# 3. 개발 엔진 (Coder Engine)
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
        past_history = [{"role": h["role"], "parts": [h["text"]]} for h in history_raw]
        self.session = self.model.start_chat(history=past_history)

    def develop(self, cmd):
        # 1. 명령에 포함된 설계 파일 언급 탐색 (예: "tg_system_contract.json 참고해서")
        match = re.search(r'([a-zA-Z0-9_\-\./\\]+\.(?:md|txt|json|html))', cmd)
        plan_content = ""
        if match:
            plan_content = self.storage.read_plan_file(match.group(1))
        
        prompt = (
            f"[PLANNING CONTEXT LOADED]\n{plan_content[:3000] if plan_content else 'No specific plan file linked.'}\n\n"
            f"[USER COMMAND]: {cmd}\n"
            f"지시: 설계 내용을 바탕으로 고품질 코드를 작성하고 [CODE_WRITE:파일명]...[/CODE_WRITE]를 사용하십시오."
        )

        try:
            response = self.session.send_message(prompt)
            # [CODE_WRITE] 태그 파싱 및 파일 저장
            matches = re.findall(r"\[CODE_WRITE:(.*?)\](.*?)\[/CODE_WRITE\]", response.text, re.DOTALL)
            results = [self.storage.write_code(f.strip(), c.strip()) for f, c in matches]
            
            self.storage.save_history(self.session.history)
            return response.text + ("\n\n[DEVELOPMENT LOGS]\n" + "\n".join(results) if results else "")
        except Exception as e:
            return f"DEVELOPMENT_FAILURE: {str(e)}"

# ==========================================
# 4. 사용자 인터페이스 (Coder Dashboard)
# ==========================================
class CoderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = CoderConfig()
        self.engine = CoderEngine(self.config)

        self.title(f"CODER-X SUPREME | {self.config.model_name}")
        self.geometry("1200x950")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, height=50, fg_color="#1A1A1A")
        self.header.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        status_txt = f"● CODER ONLINE | SRC: {self.config.plan_path.name} | DEST: {self.config.dev_path.name}"
        self.lbl_status = ctk.CTkLabel(self.header, text=status_txt, text_color="#00FFCC", font=("Consolas", 14, "bold"))
        self.lbl_status.pack(side="left", padx=20)

        # Chat Window
        self.console = ctk.CTkTextbox(self, font=("Consolas", 14), spacing2=8, border_width=2, border_color="#222")
        self.console.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.console.configure(state="disabled")

        # Input Area
        self.input_area = ctk.CTkFrame(self, fg_color="transparent")
        self.input_area.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.entry = ctk.CTkEntry(self.input_area, placeholder_text="개발 명령 입력 (예: 'tg_system_contract.json 기반으로 백엔드 API 구현해줘')", height=65, font=("Consolas", 16))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.run_dev())

        self.btn = ctk.CTkButton(self.input_area, text="CODE EXECUTE", width=160, height=65, command=self.run_dev, font=("Impact", 16), fg_color="#C0392B")
        self.btn.pack(side="right")

        self.restore_history()
        self.add_log("SYSTEM", f"CODER-X 수석 개발자 엔진 가동. '{self.config.plan_path}'의 설계도를 바탕으로 개발을 수행할 준비가 되었습니다.")

    def restore_history(self):
        history = self.engine.storage.load_history()
        if history:
            self.console.configure(state="normal")
            for h in history:
                sender = "USER" if h["role"] == "user" else "CODER"
                self.add_log(sender, h["text"], is_past=True)
            self.console.configure(state="disabled")
            self.console.see("end")

    def add_log(self, sender, msg, is_past=False):
        self.console.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        color = "#3498db" if sender == "USER" else "#e74c3c" if sender == "CODER" else "#2ecc71"
        header = f"[{sender} | {ts if not is_past else 'PAST'}]\n"
        self.console.insert("end", f"{header}{msg}\n\n" + "="*80 + "\n\n")
        
        tag_id = f"tag_{datetime.now().timestamp()}"
        self.console.tag_add(tag_id, "end -3lines", "end -2lines")
        self.console.tag_config(tag_id, foreground=color)
        
        self.console.configure(state="disabled")
        self.console.see("end")

    def run_dev(self):
        cmd = self.entry.get()
        if not cmd: return
        self.add_log("USER", cmd)
        self.entry.delete(0, "end")
        self.lbl_status.configure(text="● CODER-X IS CODING...", text_color="#F1C40F")
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