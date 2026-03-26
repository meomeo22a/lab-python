import streamlit as st
import google.generativeai as genai
import json
import os

# hàm xử lý dữ liệu json
DATA_FILE = "history.json"

def load_history():
    """Đọc dữ liệu từ file JSON nếu có"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history_data):
    """Ghi đè danh sách lịch sử hiện tại vào file JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=4)


# 1. API Key và cấu hình
API_KEY = "AIzaSyAoJAYM8FY61qv_k1Wad3k-V5UvAuab-c0" 
genai.configure(api_key=API_KEY)

# 1.1. Khởi tạo mô hình và Lịch sử (Lấy từ file JSON lên)
if "history" not in st.session_state:
    st.session_state.history = load_history()

# 2. Tự động tìm model khả dụng
@st.cache_resource
def get_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        return "gemini-pro" #mặc định
    return "gemini-pro"

available_model_name = get_available_model()
model = genai.GenerativeModel(available_model_name)

# 3. Giao diện Sidebar 
with st.sidebar:
    st.title("📜 Lịch sử yêu cầu")
    
    # Nút xóa lịch sử giờ sẽ xóa cả file JSON
    if st.button("🗑️ Xóa lịch sử"):
        st.session_state.history = []
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()
    
    st.divider()
    
    # Đã bỏ reversed() vì hàm insert(0) bên dưới đã đưa bài mới lên đầu
    for i, item in enumerate(st.session_state.history):
        # Đánh số thứ tự lùi (VD: 5, 4, 3, 2, 1)
        req_number = len(st.session_state.history) - i
        with st.expander(f"Yêu cầu {req_number}: {item['question'][:20]}..."):
            st.write(item['answer'])

# --- GIAO DIỆN CHÍNH ---
st.title("🤖 Trợ Lý Lập Trình AI")

user_input = st.text_area("Nhập đề bài tập lập trình:", placeholder="Ví dụ: Tính giai thừa của n bằng đệ quy...")

if st.button("🚀 Thực hiện và Lưu"):
    if user_input:
        with st.spinner('AI đang viết code...'):
            try:
                prompt = f"Viết code Python cho: {user_input}. Giải thích ngắn."
                response = model.generate_content(prompt)
                ans_text = response.text
                
                # 1. Hiển thị kết quả ngay lập tức (Trước khi rerun)
                st.success("Đã tạo xong!")
                st.markdown("### 💻 Kết quả trả về:")
                st.markdown(ans_text)
                
                # 2. Cập nhật vào lịch sử trong session_state
                # Dùng insert(0,...) để câu hỏi mới nhất lên đầu danh sách
                st.session_state.history.insert(0, {
                    "question": user_input, 
                    "answer": ans_text
                })
                
                # 3. LƯU VÀO FILE JSON
                save_history(st.session_state.history)
                
                # Lưu ý: Không dùng st.rerun() ở đây vì nó sẽ xóa mất 
                # phần st.markdown(ans_text) vừa hiển thị.
                # Sidebar sẽ tự cập nhật ở lần bấm nút hoặc tương tác tiếp theo.
                
            except Exception as e:
                st.error(f"Lỗi: {e}")
    else:
        st.warning("Bạn chưa nhập đề bài!")