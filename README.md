## Hòm thư góp ý CNT 2025-2026

Ứng dụng web được xây dựng bằng **Python + Streamlit** mô phỏng giao diện hòm thư góp ý như trong hình mẫu.

### 1. Cài đặt môi trường

```bash
cd d:\LearnAI\Homthugopy
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

```bash
streamlit run app.py
```

Sau khi chạy lệnh trên, trình duyệt sẽ tự mở trang web form góp ý.

### 3. Lưu phản hồi

- Mỗi phản hồi hợp lệ sẽ được lưu vào file CSV:
  - `data/feedback.csv`
- File này có thể mở bằng Excel hoặc bất kỳ công cụ xử lý bảng tính nào.

