import base64
import csv
from datetime import datetime
from email.message import EmailMessage
import os
from pathlib import Path
import smtplib

import streamlit as st


def _find_logo_file() -> Path | None:
    """Tìm file logo trong thư mục dự án.

    Ưu tiên:
    - ./logo.png
    - ./assets/logo.png
    """
    base_dir = Path(__file__).parent
    candidates = [base_dir / "logo.png", base_dir / "assets" / "logo.png"]
    for path in candidates:
        if path.exists():
            return path
    return None


def init_page_config() -> None:
    logo_file = _find_logo_file()
    page_icon = str(logo_file) if logo_file is not None else "📮"

    st.set_page_config(
        page_title="Hòm thư góp ý Trung đoàn CSCĐ Đông Bắc",
        page_icon=page_icon,
        layout="centered",
        initial_sidebar_state="collapsed",
    )


def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* Toàn bộ nền trang */
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #4f46e5, #06b6d4);
        }

        /* Vùng nội dung chính của Streamlit */
        .stApp {
            background: linear-gradient(135deg, #4f46e5, #06b6d4);
        }

        /* Đưa nội dung chính sát thanh công cụ/địa chỉ trình duyệt - triệt toàn bộ khoảng trống trên */
        .stApp [data-testid="stAppViewContainer"] {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        .stApp [data-testid="stAppViewContainer"] > section {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        .main .block-container {
            padding-top: 0 !important;
            padding-bottom: 2rem;
            max-width: 100%;
        }
        section.main {
            padding-top: 0 !important;
        }
        section.main > div {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        /* Bỏ khoảng trống do header ẩn của Streamlit để lại */
        header[data-testid="stHeader"] {
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Ẩn menu mặc định của Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Khối tiêu đề trên cùng */
        .feedback-header {
            background: linear-gradient(to right, #e57373, #c62828);
            padding: 22px 32px;
            border-radius: 18px 18px 0 0;
            color: #ffeb3b;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.25);
            text-align: left;
        }

        .feedback-header-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 26px;
            font-weight: 700;
        }

        .feedback-header-title-text {
            display: flex;
            flex-direction: column;
            line-height: 1.3;
        }

        .feedback-header-title-text .line1 {
            font-size: 32px;
        }

        .feedback-header-title-text .line2 {
            font-size: 22px;
            opacity: 0.95;
        }

        .feedback-header-subtitle {
            margin-top: 8px;
            font-size: 14px;
            opacity: 0.95;
            color: #ffffff;
        }

        .feedback-icon {
            font-size: 30px;
        }

        .feedback-logo {
            height: 60px;
            width: auto;
        }

        /* Thẻ trắng chứa form */
        .feedback-card {
            background: #ffffff;
            padding: 12px 32px 12px 32px;
            border-radius: 0 0 18px 18px;
            box-shadow: 0 22px 40px rgba(15, 23, 42, 0.3);
            margin-bottom: 22px;
        }

        /* Hộp thông tin quan trọng */
        .info-box {
            background: #f5f7ff;
            border-radius: 14px;
            padding: 16px 18px 18px 18px;
            border-left: 4px solid #4f46e5;
            margin-bottom: 22px;
        }

        .info-title {
            font-weight: 700;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
            color: #1f2937;
        }

        .info-list {
            margin: 0;
            padding-left: 20px;
            font-size: 14px;
            color: #374151;
        }

        .info-list li {
            margin-bottom: 2px;
        }

        /* Nhãn trường form */
        label, .stTextInput > label, .stTextArea > label, .stSelectbox > label {
            font-weight: 600 !important;
            font-size: 14px !important;
        }

        .required-star {
            color: #ef4444;
        }

        /* Nút bấm */
        .stButton button {
            border-radius: 999px;
            font-weight: 600;
            padding: 10px 28px;
            border: none;
            font-size: 14px;
        }

        .primary-btn button {
            background: linear-gradient(135deg, #2563eb, #22d3ee);
            color: white;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.45);
        }

        .primary-btn button:hover {
            filter: brightness(1.05);
        }

        .secondary-btn button {
            background: #e5e7eb;
            color: #111827;
        }

        .secondary-btn button:hover {
            background: #d1d5db;
        }

        .stTextInput > div > div > input,
        .stTextArea > div > textarea,
        .stSelectbox > div > div {
            border-radius: 10px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_logo_base64() -> str:
    """Đọc file logo và trả về chuỗi base64 để nhúng vào HTML."""
    logo_path = _find_logo_file()
    if logo_path is None:
        return ""
    try:
        with logo_path.open("rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return ""


def save_uploaded_images(uploaded_files) -> str:
    """Lưu các file ảnh tải lên vào data/uploads, trả về chuỗi tên file cách nhau bởi dấu phẩy."""
    if not uploaded_files:
        return ""
    upload_dir = Path("data") / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    for i, uf in enumerate(uploaded_files):
        ext = Path(uf.name).suffix or ".jpg"
        name = f"{ts}_{i}{ext}"
        path = upload_dir / name
        path.write_bytes(uf.getvalue())
        saved.append(name)
    return ",".join(saved)


def save_feedback(row: dict) -> None:
    """Lưu phản hồi vào file CSV."""
    data_path = Path("data")
    data_path.mkdir(exist_ok=True)
    file_path = data_path / "feedback.csv"
    file_exists = file_path.exists()
    fieldnames = ["timestamp", "name", "category", "priority", "title", "images", "detail"]
    with file_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def send_email(row: dict) -> None:
    """Gửi email phản hồi đến admin@gmail.com."""
    to_email = "admin@gmail.com"
    host = os.getenv("FEEDBACK_SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("FEEDBACK_SMTP_PORT", "587"))
    username = os.getenv("FEEDBACK_SMTP_USER", "")
    password = os.getenv("FEEDBACK_SMTP_PASS", "")
    if not username or not password:
        return
    subject = f"[Hòm thư CSCĐ Đông Bắc] {row['priority']} - {row['title']}"
    body_lines = [
        "Bạn có một phản hồi mới từ Hòm thư góp ý Trung đoàn CSCĐ Đông Bắc:\n",
        f"Thời gian: {row['timestamp']}",
        f"Họ và tên: {row['name'] or '(không cung cấp)'}",
        f"Danh mục: {row['category']}",
        f"Mức độ ưu tiên: {row['priority']}",
        f"Tiêu đề: {row['title']}",
        f"Hình ảnh phản ánh: {row.get('images') or '(không có)'}",
        "",
        "Nội dung chi tiết:",
        row["detail"],
    ]
    body = "\n".join(body_lines)
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = username
    msg["To"] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
    except Exception as exc:
        st.warning(f"Không gửi được email thông báo: {exc}")


def main() -> None:
    init_page_config()
    inject_css()

    if "form_seed" not in st.session_state:
        st.session_state["form_seed"] = 0
    seed = st.session_state["form_seed"]

    logo_b64 = get_logo_base64()
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="feedback-logo" />'
    else:
        logo_html = '<span class="feedback-icon">📮</span>'

    with st.container():
        st.markdown(
            f"""
            <div class="feedback-header">
                <div class="feedback-header-title">
                    {logo_html}
                    <div class="feedback-header-title-text">
                        <span class="line1">Trung đoàn CSCĐ Đông Bắc</span>
                        <span class="line2">Hòm thư góp ý</span>
                    </div>
                </div>
                <div class="feedback-header-subtitle">
                    Ý kiến của đồng chí sẽ được gửi ẩn danh đến Chỉ huy Trung đoàn
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="feedback-card">', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="info-box">
                <div class="info-title">
                    <span>📞 Đường dây nóng:</span>
                </div>
                <ul class="info-list">
                    <li>Đại tá Phan Công Côn - Trung đoàn trưởng: 0912345678</li>
                    <li>Thượng tá Mai Đình Dũng - Phó trung đoàn trưởng: 0912345678</li>
                    <li>Thượng tá Mai Đình Dũng - Phó trung đoàn trưởng: 0912345678</li>
                    <li>Trung tá Đinh Sơn TrườngTrường - Phó trung đoàn trưởng: 0912345678</li>
                    <li>Trực ban Trung đoàn: 0912345678</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("feedback_form"):
            name = st.text_input(
                "Họ và tên (tùy chọn):",
                placeholder="Nhập họ tên của bạn...",
                key=f"name_{seed}",
            )
            category = st.selectbox(
                "Danh mục phản hồi: *",
                [
                    "-- Chọn danh mục --",
                    "Công tác tổ chức, cán bộ",
                    "Chế độ, chính sách",
                    "Huấn luyện, sẵn sàng chiến đấu",
                    "Cơ sở vật chất, trang bị",
                    "Quan hệ nội bộ, kỷ luật",
                    "Khác",
                ],
                key=f"category_{seed}",
            )
            priority = st.selectbox(
                "Mức độ ưu tiên: *",
                [
                    "-- Chọn mức độ --",
                    "Bình thường",
                    "Quan trọng",
                    "Khẩn cấp",
                ],
                key=f"priority_{seed}",
            )
            title = st.text_input(
                "Tiêu đề: *",
                placeholder="Nhập tiêu đề ngắn gọn...",
                key=f"title_{seed}",
            )
            image_files = st.file_uploader(
                "Hình ảnh phản ánh (tùy chọn):",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                accept_multiple_files=True,
                key=f"images_{seed}",
            )
            detail = st.text_area(
                "Nội dung chi tiết: *",
                height=180,
                placeholder="Mô tả chi tiết vấn đề, góp ý hoặc đề xuất của bạn...",
                key=f"detail_{seed}",
            )
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Gửi Phản hồi", use_container_width=True)
            with col2:
                reset = st.form_submit_button("Làm mới", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    if reset:
        st.session_state["form_seed"] += 1
        st.rerun()

    if submit:
        errors = []
        if category == "-- Chọn danh mục --":
            errors.append("Vui lòng chọn **Danh mục phản hồi**.")
        if priority == "-- Chọn mức độ --":
            errors.append("Vui lòng chọn **Mức độ ưu tiên**.")
        if not title.strip():
            errors.append("Vui lòng nhập **Tiêu đề**.")
        if not detail.strip():
            errors.append("Vui lòng nhập **Nội dung chi tiết**.")
        if errors:
            for err in errors:
                st.error(err)
        else:
            images_str = save_uploaded_images(image_files)
            row = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "name": name.strip(),
                "category": category,
                "priority": priority,
                "title": title.strip(),
                "images": images_str,
                "detail": detail.strip(),
            }
            save_feedback(row)
            send_email(row)
            st.success("Cảm ơn bạn! Phản hồi đã được gửi thành công.")


if __name__ == "__main__":
    main()
