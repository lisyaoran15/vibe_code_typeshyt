"""Tab 1: Dashboard — Thống kê mô hình + Báo cáo tình hình kiểm định."""

import streamlit as st
import pandas as pd
import plotly.express as px
from config import (
    PLOTLY_CONFIG, COLOR_SEQUENCE, FLAG_COLOR_MAP,
    clean_layout, color_flag,
)


def render(models_list, log_details, last_qual, last_quan):
    st.header("Dashboard")
    today = pd.Timestamp.now()

    # Trạng thái mới nhất mỗi model
    latest_log = (
        log_details
        .sort_values("schedule_dt", na_position="first")
        .drop_duplicates(subset="model_id", keep="last")
    )

    # =====================================================================
    # PHẦN 1: THỐNG KÊ MÔ HÌNH
    # =====================================================================
    st.subheader("📊 Thống kê mô hình")

    # Đếm theo model_name (unique)
    model_name_counts = models_list.drop_duplicates(subset="model_name")
    total_model_names = len(model_name_counts)
    status_counts = model_name_counts["status"].value_counts()
    deployed = int(status_counts.get("deploy", 0))
    validating = int(status_counts.get("validating", 0))
    building = int(status_counts.get("development", 0) + status_counts.get("building", 0))
    other_status = total_model_names - deployed - validating - building

    # ── KPI row ───────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Tổng mô hình", total_model_names)
    k2.metric("Đang deploy", deployed)
    k3.metric("Đang validating", validating)
    k4.metric("Đang phát triển", building)
    k5.metric("Khác", other_status)

    # ── Charts: Status / Tier / Type / Department ────────────────────────
    ca, cb, cc, cd = st.columns(4)

    with ca:
        status_df = status_counts.reset_index()
        status_df.columns = ["Trạng thái", "Số lượng"]
        status_cmap = {"deploy": "#00804D", "validating": "#FFC62F", "development": "#33996E",
                       "building": "#33996E", "under review": "#CC3333", "retired": "#999999"}
        fig = px.pie(status_df, names="Trạng thái", values="Số lượng", title="Theo trạng thái",
                     color="Trạng thái", color_discrete_map=status_cmap, hole=0.4)
        fig.update_traces(textinfo="percent+label",
                          hovertemplate="<b>%{label}</b><br>Số lượng: %{value}<br>%{percent}<extra></extra>")
        st.plotly_chart(clean_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

    with cb:
        tier_df = model_name_counts["tier"].value_counts().sort_index().reset_index()
        tier_df.columns = ["Tier", "Số lượng"]
        tier_df["Label"] = tier_df["Tier"].apply(lambda t: f"Tier {int(t)}" if not pd.isna(t) else str(t))
        fig = px.pie(tier_df, names="Label", values="Số lượng", title="Theo Tier",
                     color_discrete_sequence=["#00804D", "#FFC62F", "#33996E", "#66CC99"], hole=0.4)
        fig.update_traces(textinfo="percent+label",
                          hovertemplate="<b>%{label}</b><br>Số lượng: %{value}<br>%{percent}<extra></extra>")
        st.plotly_chart(clean_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

    with cc:
        type_df = model_name_counts["type"].value_counts().reset_index()
        type_df.columns = ["Loại mô hình", "Số lượng"]
        fig = px.bar(type_df, x="Loại mô hình", y="Số lượng", color="Loại mô hình",
                     color_discrete_sequence=COLOR_SEQUENCE, title="Theo loại mô hình", text="Số lượng")
        fig.update_traces(textposition="outside",
                          hovertemplate="<b>%{x}</b><br>Số lượng: %{y}<extra></extra>")
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(clean_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

    with cd:
        if "dev_department" in model_name_counts.columns:
            dept_df = model_name_counts["dev_department"].value_counts().reset_index()
            dept_df.columns = ["Đơn vị", "Số lượng"]
            fig = px.bar(dept_df, y="Đơn vị", x="Số lượng", orientation="h",
                         title="Theo đơn vị xây dựng", color="Số lượng",
                         color_continuous_scale=[[0, "#FFC62F"], [1, "#00804D"]], text="Số lượng")
            fig.update_traces(textposition="outside",
                              hovertemplate="<b>%{y}</b><br>Số lượng: %{x}<extra></extra>")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(clean_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

    st.divider()

    # =====================================================================
    # PHẦN 2: BÁO CÁO TÌNH HÌNH KIỂM ĐỊNH
    # =====================================================================
    st.subheader("📋 Báo cáo tình hình kiểm định")

    # ── Kế hoạch kiểm định trong năm ─────────────────────────────────────
    st.markdown("#### 📅 Kế hoạch kiểm định trong năm")
    current_year = today.year

    # Tính ngày KĐ cuối cùng cho mỗi model_name
    unique_models = model_name_counts[["model_name", "type", "status", "val_frequency"]].copy()
    model_ids_map = models_list.groupby("model_name")["model_id"].apply(list).to_dict()

    def get_last_val_date(name):
        ids = model_ids_map.get(name, [])
        qual_d = last_qual.loc[last_qual["model_name"] == name, "val_date"]
        quan_d = last_quan.loc[last_quan["model_id"].isin(ids), "val_date"]
        all_d = pd.concat([qual_d, quan_d]).dropna()
        return all_d.max() if len(all_d) > 0 else pd.NaT

    unique_models["last_val_date"] = unique_models["model_name"].apply(get_last_val_date)

    # Count vào kế hoạch nếu: KĐ cuối là năm trước HOẶC chưa có dữ liệu KĐ
    planned_mask = (
        unique_models["last_val_date"].isna()
        | (unique_models["last_val_date"].dt.year < current_year)
    )
    planned_models = unique_models[planned_mask].copy()
    planned_count = len(planned_models)

    # Format ngày
    planned_models["KĐ gần nhất"] = planned_models["last_val_date"].apply(
        lambda d: d.strftime("%d/%m/%Y") if pd.notna(d) else "Chưa có"
    )

    st.metric(f"📊 Số mô hình cần kiểm định năm {current_year}", planned_count)

    with st.expander(f"📋 Danh sách {planned_count} mô hình cần kiểm định năm {current_year}", expanded=False):
        if planned_count > 0:
            display_planned = planned_models[["model_name", "type", "status", "val_frequency", "KĐ gần nhất"]].copy()
            display_planned.columns = ["Tên mô hình", "Loại", "Trạng thái", "Tần suất KĐ", "KĐ gần nhất"]
            st.dataframe(display_planned, use_container_width=True, hide_index=True)
        else:
            st.success("Tất cả mô hình đã được kiểm định trong năm nay.")

    st.divider()

    # ── Sắp đến hạn ──────────────────────────────────────────────────────
    st.markdown("#### 🔔 Mô hình sắp đến hạn kiểm định")

    def get_upcoming(days):
        mask = (
            log_details["schedule_dt"].notna()
            & (log_details["schedule_dt"] >= today)
            & (log_details["schedule_dt"] <= today + pd.Timedelta(days=days))
            & (log_details["status"] != "finished")
        )
        if not mask.any():
            return pd.DataFrame()
        df = (
            log_details[mask]
            .merge(models_list[["model_id", "model_name", "type", "tier", "val_frequency"]].drop_duplicates(),
                   on="model_id", how="left")
            .drop_duplicates(subset="model_id", keep="last")
            .sort_values("schedule_dt")
        )
        df["days_left"] = (df["schedule_dt"] - today).dt.days
        # Periodic vs Initial: dựa vào val_frequency — nếu có giá trị → periodic, nếu rỗng/nan → initial
        if "val_frequency" in df.columns:
            df["loại_KĐ"] = df["val_frequency"].apply(
                lambda v: "Initial" if pd.isna(v) or str(v).strip().lower() in ["nan", "", "none"] else "Periodic"
            )
        return df

    tab_7, tab_15, tab_30 = st.tabs(["⚡ 7 ngày tới", "📅 15 ngày tới", "🗓️ 30 ngày tới"])

    def show_upcoming_table(df, label):
        if len(df) == 0:
            st.success(f"Không có mô hình nào đến hạn trong {label}.")
            return
        show_cols = [c for c in ["model_id", "model_name", "type", "tier", "loại_KĐ", "stage", "schedule_date", "days_left"]
                     if c in df.columns]

        def hl_days(val):
            if val <= 7:
                return "background-color: #CC3333; color: white; font-weight: 600"
            elif val <= 15:
                return "background-color: #FFC62F; color: #1a1a1a; font-weight: 600"
            return ""

        st.dataframe(df[show_cols].style.map(hl_days, subset=["days_left"]),
                      use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} mô hình đến hạn trong {label}")

    with tab_7:
        show_upcoming_table(get_upcoming(7), "7 ngày tới")
    with tab_15:
        show_upcoming_table(get_upcoming(15), "15 ngày tới")
    with tab_30:
        show_upcoming_table(get_upcoming(30), "30 ngày tới")

    st.divider()

    # ── Quá hạn ───────────────────────────────────────────────────────────
    overdue_mask = (
        log_details["schedule_dt"].notna()
        & (log_details["schedule_dt"] < today)
        & (log_details["status"] != "finished")
    )
    overdue_count = int(log_details.loc[overdue_mask, "model_id"].nunique()) if overdue_mask.any() else 0

    if overdue_count > 0:
        st.markdown(f"#### ⚠️ Mô hình quá hạn ({overdue_count})")
        overdue_df = (
            log_details[overdue_mask]
            .merge(models_list[["model_id", "model_name", "type", "tier"]].drop_duplicates(), on="model_id", how="left")
            .drop_duplicates(subset="model_id", keep="last")
            .sort_values("schedule_dt")
        )
        overdue_df["days_overdue"] = (today - overdue_df["schedule_dt"]).dt.days
        show_cols = [c for c in ["model_id", "model_name", "type", "tier", "stage", "schedule_date", "days_overdue"]
                     if c in overdue_df.columns]
        st.dataframe(overdue_df[show_cols].style.background_gradient(subset=["days_overdue"], cmap="Reds"),
                      use_container_width=True, hide_index=True)
        st.divider()

    # ── Mô hình cần chú ý (red flags) ────────────────────────────────────
    st.markdown("#### 🔴 Mô hình đã kiểm định cần chú ý")
    st.caption("Mô hình có finding bị flag Red — xếp theo số lượng giảm dần.")

    col_rq, col_rn = st.columns(2)

    with col_rq:
        red_qual = last_qual[last_qual["flag"] == "red"]
        if len(red_qual) > 0:
            st.markdown("**Định tính (Qualitative)**")
            rq_summary = red_qual.groupby("model_name").size().reset_index(name="Red findings")
            rq_summary = rq_summary.sort_values("Red findings", ascending=False)
            st.dataframe(
                rq_summary.style.map(
                    lambda _: "background-color: #CC3333; color: white; font-weight: 600",
                    subset=["Red findings"]),
                use_container_width=True, hide_index=True)
        else:
            st.success("Không có red finding định tính.")

    with col_rn:
        red_quan = last_quan[last_quan["flag"] == "red"]
        if len(red_quan) > 0:
            st.markdown("**Định lượng (Quantitative)**")
            rn_summary = red_quan.groupby("model_id").size().reset_index(name="Red metrics")
            rn_summary = rn_summary.sort_values("Red metrics", ascending=False)
            st.dataframe(
                rn_summary.style.map(
                    lambda _: "background-color: #CC3333; color: white; font-weight: 600",
                    subset=["Red metrics"]),
                use_container_width=True, hide_index=True)
        else:
            st.success("Không có red finding định lượng.")