import customtkinter as ctk
import google.generativeai as genai
import json
import os
import threading

# --- 1. HÀM XỬ LÝ JSON ---
DATA_FILE = "history.json"

def load_history():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history_data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=4)

# --- 2. CẤU HÌNH API ---
API_KEY = "AIzaSyAoJAYM8FY61qv_k1Wad3k-V5UvAuab-c0" 
genai.configure(api_key=API_KEY)

def get_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        return "gemini-pro"
    return "gemini-pro"

model = genai.GenerativeModel(get_available_model())

# --- 3. GIAO DIỆN DESKTOP (CUSTOMTKINTER) ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🤖 Trợ Lý Lập Trình AI")
        self.geometry("950x650")
        
        # Load lịch sử từ file
        self.history = load_history()

        # Chia layout làm 2 cột: Cột 0 (Sidebar) - Cột 1 (Main)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()

    def setup_sidebar(self):
        """Khởi tạo giao diện thanh bên trái (Sidebar)"""
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        # Tiêu đề & Nút xóa
        ctk.CTkLabel(self.sidebar_frame, text="📜 Lịch sử yêu cầu", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkButton(self.sidebar_frame, text="🗑️ Xóa lịch sử", fg_color="#C62828", hover_color="#B71C1C", command=self.clear_history).grid(row=1, column=0, padx=20, pady=10)

        # Khu vực cuộn chứa danh sách lịch sử
        self.history_scroll = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="Các câu hỏi trước")
        self.history_scroll.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        self.load_history_ui()

    def setup_main_area(self):
        """Khởi tạo giao diện chính bên phải"""
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # --- THÊM DÒNG NÀY ĐỂ GIÃN FULL CHIỀU NGANG ---
        self.main_frame.grid_columnconfigure(0, weight=1) 
        
        # Dòng này giúp ô output giãn full chiều dọc
        self.main_frame.grid_rowconfigure(3, weight=1)

        # Tiêu đề
        ctk.CTkLabel(self.main_frame, text="Giao diện Code Assistant", font=("Arial", 24, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Ô nhập liệu
        self.txt_input = ctk.CTkTextbox(self.main_frame, height=80, font=("Consolas", 14))
        self.txt_input.grid(row=1, column=0, sticky="ew", pady=(0, 10)) # sticky="ew" giúp giãn ngang
        self.txt_input.insert("0.0", "Nhập đề bài tập lập trình vào đây...")

        # Nút thực hiện
        self.btn_submit = ctk.CTkButton(self.main_frame, text="🚀 Thực hiện và Lưu", font=("Arial", 14, "bold"), command=self.on_submit_click)
        self.btn_submit.grid(row=2, column=0, sticky="w", pady=(0, 20))

        # Ô hiển thị kết quả (Output)
        self.txt_output = ctk.CTkTextbox(self.main_frame, font=("Consolas", 14))
        self.txt_output.grid(row=3, column=0, sticky="nsew") # sticky="nsew" giúp giãn cả 4 hướng
    def load_history_ui(self):
        """Đổ dữ liệu từ mảng lịch sử ra Sidebar"""
        # Xóa các nút cũ trước khi load lại
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        for i, item in enumerate(self.history):
            req_number = len(self.history) - i
            # Nút thu gọn text hiển thị
            short_text = f"Yêu cầu {req_number}: {item['question'][:15]}..."
            btn = ctk.CTkButton(self.history_scroll, text=short_text, anchor="w", fg_color="transparent", border_width=1,
                                command=lambda q=item['question'], a=item['answer']: self.show_old_item(q, a))
            btn.pack(fill="x", pady=2)

    def show_old_item(self, question, answer):
        """Hiển thị lại câu hỏi cũ khi bấm vào Sidebar"""
        self.txt_input.delete("0.0", "end")
        self.txt_input.insert("0.0", question)
        
        self.txt_output.delete("0.0", "end")
        self.txt_output.insert("0.0", answer)

    def clear_history(self):
        """Xóa toàn bộ lịch sử"""
        self.history = []
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        self.load_history_ui()
        self.txt_output.delete("0.0", "end")
        self.txt_input.delete("0.0", "end")

    def on_submit_click(self):
        """Xử lý khi bấm nút Thực hiện"""
        user_input = self.txt_input.get("0.0", "end").strip()
        if not user_input or user_input == "Nhập đề bài tập lập trình vào đây...":
            return

        # Khóa nút bấm và hiển thị trạng thái chờ
        self.btn_submit.configure(state="disabled", text="⏳ Đang xử lý...")
        self.txt_output.delete("0.0", "end")
        self.txt_output.insert("0.0", "AI đang viết code, vui lòng đợi...\n")

        # Chạy AI ở một luồng (thread) riêng để giao diện không bị đơ (Not Responding)
        threading.Thread(target=self.call_ai, args=(user_input,)).start()

    def call_ai(self, user_input):
        """Hàm gọi API ngầm"""
        try:
            prompt = f"Viết code Python cho: {user_input}. Giải thích ngắn."
            response = model.generate_content(prompt)
            ans_text = response.text

            # Cập nhật UI (Phải dùng .after để cập nhật từ Thread phụ sang Main Thread)
            self.after(0, self.update_ui_after_ai_call, user_input, ans_text)
        except Exception as e:
            self.after(0, self.update_ui_error, str(e))

    def update_ui_after_ai_call(self, user_input, ans_text):
        """Cập nhật giao diện sau khi AI trả kết quả về"""
        self.txt_output.delete("0.0", "end")
        self.txt_output.insert("0.0", ans_text)

        # Lưu lịch sử
        self.history.insert(0, {"question": user_input, "answer": ans_text})
        save_history(self.history)
        self.load_history_ui()

        # Mở khóa nút bấm
        self.btn_submit.configure(state="normal", text="🚀 Thực hiện và Lưu")

    def update_ui_error(self, error_msg):
        """Hiển thị lỗi nếu có"""
        self.txt_output.insert("end", f"\n[LỖI]: {error_msg}")
        self.btn_submit.configure(state="normal", text="🚀 Thực hiện và Lưu")

# --- CHẠY ỨNG DỤNG ---
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark") # Có thể đổi thành "Light" hoặc "System"
    ctk.set_default_color_theme("blue")
    
    app = App()
    app.mainloop()