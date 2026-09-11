"""Tab 3: Additional Knowledge — Thư viện tài liệu."""

import streamlit as st


# Base path trên file server
BASE_PATH = r"\\10.21.229.61"

# Cấu trúc folder Credit
CREDIT_FOLDERS = {
    "A. VĂN BẢN CHẾ ĐỘ": rf"{BASE_PATH}\Credit\A. VĂN BẢN CHẾ ĐỘ",
    "C. KIỂM ĐỊNH MÔ HÌNH": rf"{BASE_PATH}\Credit\C. KIỂM ĐỊNH MÔ HÌNH",
    "G. Tài liệu kiến thức": rf"{BASE_PATH}\Credit\G. KHÁC\Tài liệu kiến thức",
}


def render():
    st.header("📚 Additional Knowledge")
    st.caption("Truy cập nhanh thư viện tài liệu trên file server nội bộ.")

    st.divider()

    # ── Credit ────────────────────────────────────────────────────────────
    st.subheader("📂 Credit")

    for folder_name, folder_path in CREDIT_FOLDERS.items():
        col_icon, col_name, col_btn = st.columns([0.5, 4, 1.5])
        with col_icon:
            st.markdown("📁")
        with col_name:
            st.markdown(f"**{folder_name}**")
            st.caption(folder_path)
        with col_btn:
            # Mở folder trong Windows Explorer
            st.code(folder_path, language=None)

    st.divider()

    st.markdown("""
    **Cách mở folder:**
    1. Copy đường dẫn ở trên
    2. Mở **File Explorer** (Windows + E)
    3. Paste vào thanh địa chỉ → Enter

    Hoặc mở **Run** (Windows + R) → paste đường dẫn → OK
    """)

    st.divider()

    # ── Non-Credit (placeholder) ──────────────────────────────────────────
    st.subheader("📂 Non-Credit")
    st.info("Đang cập nhật cấu trúc folder Non-Credit. Sẽ bổ sung sau.")