"""Tab 2: Chi tiết từng mô hình — selector bên phải, nội dung bên trái."""

import streamlit as st
import pandas as pd
from config import color_flag, color_fix


def render(models_list, last_qual, last_quan):
    # ── Layout: nội dung trái (rộng) | selector phải (hẹp) ───────────────
    col_main, col_select = st.columns([3, 1])

    with col_select:
        st.markdown("#### 🔎 Chọn mô hình")
        search_text = st.text_input("Tìm kiếm", "", key="model_search",
                                     placeholder="Gõ tên mô hình...", label_visibility="collapsed")

        filtered = models_list.copy()
        if search_text.strip():
            filtered = filtered[
                filtered["model_name"].str.contains(search_text.strip(), case=False, na=False)
            ]

        if len(filtered) == 0:
            st.warning("Không tìm thấy.")
            return

        model_names = sorted(filtered["model_name"].dropna().unique())
        selected_name = st.selectbox("Mô hình", model_names, key="select_model_name", label_visibility="collapsed")

    # ── Chuẩn bị data ────────────────────────────────────────────────────
    sub_models = models_list[models_list["model_name"] == selected_name]
    model_ids = sorted(sub_models["model_id"].dropna().unique())
    n_ids = len(model_ids)
    first = sub_models.iloc[0]

    dev_dept = first.get("dev_department", "N/A")
    model_type = first.get("type", "N/A")
    tier = first.get("tier", "N/A")
    flag_owner = first.get("flag_owner", "N/A")
    status = first.get("status", "N/A")

    qual_dates = last_qual.loc[last_qual["model_name"] == selected_name, "val_date"]
    quan_dates = last_quan.loc[last_quan["model_id"].isin(model_ids), "val_date"]
    all_dates = pd.concat([qual_dates, quan_dates]).dropna()
    last_val_date = all_dates.max() if len(all_dates) > 0 else None
    last_val_str = last_val_date.strftime("%d/%m/%Y") if pd.notna(last_val_date) else "Chưa có"

    red_qual = int((last_qual[last_qual["model_name"] == selected_name]["flag"] == "red").sum())
    red_quan = int((last_quan[last_quan["model_id"].isin(model_ids)]["flag"] == "red").sum())
    total_red = red_qual + red_quan

    with col_main:
        # ── Khung thông tin ───────────────────────────────────────────────
        st.markdown(f"""
        <div style="
            background: #ebe5d9;
            border-left: 5px solid #00804D;
            border-radius: 8px;
            padding: 25px 35px;
            margin: 0 0 20px 0;
        ">
            <h3 style="margin-top:0;">{selected_name}</h3>
            <table style="width:100%; border-collapse:collapse; font-size:0.95rem; margin-top:10px;">
                <tr>
                    <td style="padding:8px 15px 8px 0; opacity:0.7; width:200px;">📌 Đơn vị phát triển</td>
                    <td style="padding:8px 15px; font-weight:600;">{dev_dept}</td>
                    <td style="padding:8px 15px; opacity:0.7; width:200px;">📂 Loại mô hình</td>
                    <td style="padding:8px 15px; font-weight:600;">{model_type}</td>
                </tr>
                <tr>
                    <td style="padding:8px 15px 8px 0; opacity:0.7;">⭐ Tier</td>
                    <td style="padding:8px 15px; font-weight:600;">{tier}</td>
                    <td style="padding:8px 15px; opacity:0.7;">🏷️ Flag owner</td>
                    <td style="padding:8px 15px; font-weight:600;">{flag_owner}</td>
                </tr>
                <tr>
                    <td style="padding:8px 15px 8px 0; opacity:0.7;">🔢 Số phân khúc</td>
                    <td style="padding:8px 15px; font-weight:600;">{n_ids}</td>
                    <td style="padding:8px 15px; opacity:0.7;">📊 Trạng thái</td>
                    <td style="padding:8px 15px; font-weight:600;">{status}</td>
                </tr>
                <tr>
                    <td style="padding:8px 15px 8px 0; opacity:0.7;">📅 Kiểm định gần nhất</td>
                    <td style="padding:8px 15px; font-weight:600;">{last_val_str}</td>
                    <td style="padding:8px 15px; opacity:0.7;">🔴 Tổng Red flag</td>
                    <td style="padding:8px 15px; font-weight:600; color:{'#CC3333' if total_red > 0 else '#00804D'};">
                        {total_red} ({red_qual} định tính, {red_quan} định lượng)
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # Bảng phân khúc
        st.markdown("**🗂️ Các phân khúc**")
        segment_cols = [c for c in ["model_id", "model_details", "status"] if c in sub_models.columns]
        st.dataframe(sub_models[segment_cols], use_container_width=True, hide_index=True,
                      height=min(35 * n_ids + 38, 200))

    st.divider()

    # =====================================================================
    # TABS: Định tính / Định lượng
    # =====================================================================
    detail_tab1, detail_tab2 = st.tabs(["🔍 Kết quả định tính", "📐 Kết quả định lượng"])

    # ── Định tính ─────────────────────────────────────────────────────────
    with detail_tab1:
        model_qual = last_qual[last_qual["model_name"] == selected_name].copy()

        if len(model_qual) == 0:
            st.info("Chưa có dữ liệu kiểm định định tính.")
        else:
            summary_cols = [c for c in ["categories", "flag", "importance", "val_date", "fix_status"]
                            if c in model_qual.columns]
            styled_qual = model_qual[summary_cols].style
            if "flag" in summary_cols:
                styled_qual = styled_qual.map(color_flag, subset=["flag"])
            if "fix_status" in summary_cols:
                styled_qual = styled_qual.map(color_fix, subset=["fix_status"])
            st.dataframe(styled_qual, use_container_width=True, hide_index=True)

            for _, row in model_qual.iterrows():
                label = f"📄 {row.get('categories', 'N/A')} — Flag: {row.get('flag', 'N/A')}"
                with st.expander(label, expanded=False):
                    if pd.notna(row.get("modelling_report")) and str(row["modelling_report"]).strip():
                        st.markdown("**Modelling Report:**")
                        st.markdown(str(row["modelling_report"]))
                    if pd.notna(row.get("validation_result")) and str(row["validation_result"]).strip():
                        st.markdown("**Validation Result:**")
                        st.markdown(str(row["validation_result"]))
                    if pd.notna(row.get("sources")) and str(row["sources"]).strip():
                        st.markdown("**Sources:**")
                        st.markdown(str(row["sources"]))
                    notes = row.get("notes", "")
                    if pd.notna(notes) and str(notes).strip() and str(notes).strip().lower() not in ["none", "nan"]:
                        st.markdown(f"*📝 {str(notes)}*")

    # ── Định lượng ────────────────────────────────────────────────────────
    with detail_tab2:
        all_quan = last_quan[last_quan["model_id"].isin(model_ids)].copy()
        show_segment_col = n_ids > 1

        if len(all_quan) == 0:
            st.info("Chưa có dữ liệu kiểm định định lượng.")
        else:
            if "val_date" in all_quan.columns and all_quan["val_date"].notna().any():
                latest_date = all_quan["val_date"].max()
                all_quan = all_quan[all_quan["val_date"] == latest_date]
                st.caption(f"Ngày kiểm định: **{latest_date.strftime('%d/%m/%Y') if pd.notna(latest_date) else 'N/A'}**")

            def classify_sample(t):
                t_str = str(t).strip().lower()
                if t_str.endswith("_train"):
                    return "Train"
                elif t_str.endswith("_valid") or t_str.endswith("_test"):
                    return "Valid"
                return "Other"

            if "type" in all_quan.columns:
                all_quan["sample"] = all_quan["type"].apply(classify_sample)

            metric_types = sorted(all_quan["metric_type"].dropna().unique()) if "metric_type" in all_quan.columns else ["all"]

            for mt in metric_types:
                mt_data = all_quan if mt == "all" else all_quan[all_quan["metric_type"] == mt]
                if len(mt_data) == 0:
                    continue

                st.markdown(f"**{mt.upper() if mt != 'all' else 'Tất cả metric'}**")

                if "sample" in mt_data.columns and mt_data["sample"].nunique() > 1:
                    idx_cols = ["model_id", "metric_name"] if show_segment_col else ["metric_name"]
                    pivot = mt_data.pivot_table(index=idx_cols, columns="sample", values="value", aggfunc="first")
                    flag_order = {"red": 3, "yellow": 2, "green": 1}
                    flag_agg = mt_data.groupby(idx_cols)["flag"].apply(
                        lambda f: max(f, key=lambda x: flag_order.get(x, 0))
                    ).reset_index()
                    flag_agg.columns = idx_cols + ["flag"]
                    display = pivot.reset_index().merge(flag_agg, on=idx_cols, how="left")
                    for nc in [c for c in display.columns if c not in idx_cols + ["flag"]]:
                        display[nc] = display[nc].apply(lambda v: f"{v:.4f}" if pd.notna(v) else "—")
                else:
                    base_cols = (["model_id"] if show_segment_col else []) + ["metric_name", "value", "type", "flag"]
                    show_cols = [c for c in base_cols if c in mt_data.columns]
                    display = mt_data[show_cols].copy()
                    if "value" in display.columns:
                        display["value"] = display["value"].apply(lambda v: f"{v:.4f}" if pd.notna(v) else "—")

                styled = display.style
                if "flag" in display.columns:
                    styled = styled.map(color_flag, subset=["flag"])
                st.dataframe(styled, use_container_width=True, hide_index=True)

                notes_data = mt_data[
                    mt_data["notes"].notna()
                    & (~mt_data["notes"].astype(str).str.strip().str.lower().isin(["", "nan", "none"]))
                ]
                for _, row in notes_data.iterrows():
                    prefix = f"{row.get('model_id', '')} — " if show_segment_col else ""
                    st.markdown(f"*📝 {prefix}{row.get('metric_name', '')}: {str(row['notes']).strip()}*")

                st.markdown("---")