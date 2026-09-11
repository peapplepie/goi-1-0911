import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ==========================================
# 1. TẠO MOCK DATA THEO ĐÚNG DATA CONTRACT
# ==========================================
@st.cache_data
def load_data():
    """
    Hàm này tạm thời sinh Mock Data. 
    Khi Subteam 2 giao file thật xóa phần sinh dữ liệu giả 
    và thay bằng lệnh: return pd.read_csv("data/processed/oecd_productivity_clean.csv")
    """
    np.random.seed(42)
    years = list(range(2014, 2024))
    countries = [
        {"Country": "Germany", "Country_Code": "DEU"},
        {"Country": "United States", "Country_Code": "USA"},
        {"Country": "South Korea", "Country_Code": "KOR"},
        {"Country": "Japan", "Country_Code": "JPN"}
    ]
    
    data = []
    for c in countries:
        for y in years:
            # Giả lập Năng suất lao động (GDPHOUR)
            if c["Country_Code"] == "DEU":
                prod, hours, rd = np.random.uniform(65, 75), np.random.uniform(1340, 1400), np.random.uniform(3.0, 3.2)
            elif c["Country_Code"] == "USA":
                prod, hours, rd = np.random.uniform(70, 80), np.random.uniform(1700, 1780), np.random.uniform(2.8, 3.5)
            elif c["Country_Code"] == "KOR":
                prod, hours, rd = np.random.uniform(35, 45), np.random.uniform(1900, 2050), np.random.uniform(4.0, 4.8)
            else: # JPN
                prod, hours, rd = np.random.uniform(45, 50), np.random.uniform(1600, 1700), np.random.uniform(3.1, 3.4)
                
            # Thêm dòng GDPHOUR
            data.append([c["Country"], c["Country_Code"], y, "GDPHOUR", prod + (y-2014)*0.5, "USD (Constant PPP)"])
            # Thêm dòng AVGHOURS
            data.append([c["Country"], c["Country_Code"], y, "AVGHOURS", hours - (y-2014)*5, "Hours"])
            # Thêm dòng RD_GDP
            data.append([c["Country"], c["Country_Code"], y, "RD_GDP", rd, "% of GDP"])
            
    df = pd.DataFrame(data, columns=["Country", "Country_Code", "Year", "Indicator_Code", "Value", "Unit"])
    return df

# ==========================================
# 2. XỬ LÝ DỮ LIỆU ĐỂ VẼ BIỂU ĐỒ
# ==========================================
df_raw = load_data()

# Biến đổi bảng (Pivot) để đưa các Indicator thành từng cột riêng biệt dễ vẽ biểu đồ Scatter
df_pivot = df_raw.pivot_table(index=["Country", "Country_Code", "Year"], 
                              columns="Indicator_Code", 
                              values="Value").reset_index()

# ==========================================
# 3. THIẾT KẾ GIAO DIỆN STREAMLIT
# ==========================================
st.set_page_config(page_title="OECD Dashboard - Phân Tích Năng Suất", layout="wide")

st.title("📊 DỰ ÁN OECD: NGHỊCH LÝ NĂNG SUẤT VÀ GIỜ LÀM VIỆC")
st.markdown("**Câu hỏi lớn:** Tại sao một số quốc gia làm việc ít giờ hơn nhưng tạo ra giá trị kinh tế cao hơn?")

# --- THANH BÊN (SIDEBAR) ĐỂ LỌC ---
st.sidebar.header("Bộ lọc Dữ liệu")
selected_year = st.sidebar.slider("Chọn Năm phân tích:", min_value=2014, max_value=2023, value=2023)
selected_countries = st.sidebar.multiselect("Chọn Quốc gia:", 
                                            options=df_pivot["Country"].unique(), 
                                            default=df_pivot["Country"].unique())

# Lọc dữ liệu theo sidebar
df_filtered = df_pivot[(df_pivot["Year"] == selected_year) & (df_pivot["Country"].isin(selected_countries))]
df_trend = df_pivot[df_pivot["Country"].isin(selected_countries)]

# ==========================================
# 4. TRỰC QUAN HÓA BẰNG PLOTLY (4 BIỂU ĐỒ)
# ==========================================

col1, col2 = st.columns(2)

# BIỂU ĐỒ 1: SCATTER PLOT (Thể hiện nghịch lý dữ liệu)
with col1:
    st.subheader(f"1. Tương quan Năng suất & Giờ làm ({selected_year})")
    fig_scatter = px.scatter(df_filtered, 
                             x="AVGHOURS", y="GDPHOUR", 
                             color="Country", size="RD_GDP",
                             hover_name="Country",
                             labels={"AVGHOURS": "Số giờ làm/năm", "GDPHOUR": "Năng suất (USD/giờ)"},
                             title="Góc trên trái: Lý tưởng (Ít giờ - Năng suất cao)")
    st.plotly_chart(fig_scatter, use_container_width=True)

# BIỂU ĐỒ 2: BAR CHART (So sánh trực diện giá trị 1 giờ làm việc)
with col2:
    st.subheader(f"2. Giá trị tạo ra trong 1 giờ làm ({selected_year})")
    fig_bar = px.bar(df_filtered.sort_values("GDPHOUR", ascending=False), 
                     x="Country", y="GDPHOUR", color="Country",
                     labels={"GDPHOUR": "Giá trị 1 giờ (USD PPP)", "Country": ""},
                     title="So sánh hiệu suất lao động đầu ra")
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

col3, col4 = st.columns(2)

# BIỂU ĐỒ 3: LINE CHART KÉP (Xu hướng Năng suất 10 năm)
with col3:
    st.subheader("3. Xu hướng tăng trưởng Năng suất (2014 - 2023)")
    fig_line_prod = px.line(df_trend, x="Year", y="GDPHOUR", color="Country", markers=True,
                            labels={"GDPHOUR": "Năng suất (USD/giờ)", "Year": "Năm"})
    st.plotly_chart(fig_line_prod, use_container_width=True)

# BIỂU ĐỒ 4: LINE CHART KÉP (Xu hướng Giờ làm việc 10 năm)
with col4:
    st.subheader("4. Biến động Số giờ làm việc bình quân (2014 - 2023)")
    fig_line_hours = px.line(df_trend, x="Year", y="AVGHOURS", color="Country", markers=True, line_dash="Country",
                             labels={"AVGHOURS": "Số giờ làm bình quân", "Year": "Năm"})
    st.plotly_chart(fig_line_hours, use_container_width=True)

# ==========================================
# 5. HIỂN THỊ BẢNG DỮ LIỆU ĐỂ KIỂM TRA
# ==========================================
with st.expander("Xem bảng dữ liệu thô (Data Dictionary Preview)"):
    st.dataframe(df_raw[df_raw["Country"].isin(selected_countries)])