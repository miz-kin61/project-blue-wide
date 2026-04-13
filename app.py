# =====================================================================
# 🌌 Project Blue Wide - Time Machine Dashboard
# 📅 最終更新: 2026年4月14日 03:50
# 💡 バージョン: V16 (グラフ完全復活 & 滞在時間 & 1文字トリガー対応)
# 📝 メモ: 1.93M行のマスターファイル読込に最適化。
# =====================================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# --- ページ設定 ---
st.set_page_config(page_title="Project Blue Wide - Master V16", layout="wide", page_icon="🌌")

# --- 🔐 秘密基地の鍵 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True
    st.markdown("<h1 style='text-align: center; color: #00BFFF;'>🌌 Project Blue Wide</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Access Code", type="password")
        if st.button("System Login"):
            if pwd == "Bwide": # パスワード
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Access Denied.")
    return False

if not check_password(): st.stop()

# --- 🎨 カラーパレット定義 ---
color_map = {
    "MG": "#E53935", "PG": "#FFB300", "P": "#43A047", 
    "M": "#3949AB", "R": "#9E9E9E", "ワイド": "#00BFFF", "スプリット": "#B0BEC5", "シンプル": "#B0BEC5",
    "シングル": "#CFD8DC", "トリプル": "#90A4AE", "クアドルプル": "#78909C", "定義なし": "#ECEFF1",
    "感情": "#FFCDD2", "仙骨": "#F8BBD0", "脾臓": "#E1BEE7", "エゴ": "#D1C4E9", "G": "#C5CAE9", "環境": "#B3E5FC", 
    "月（の周期）": "#B2DFDB", "権威なし": "#ECEFF1"
}
type_order = ["MG", "PG", "P", "M", "R"]
type_order_map = {t: i for i, t in enumerate(type_order)}

# --- 🛠️ 翻訳＆変換関数 ---
def clean_type(t):
    t_str = str(t).lower()
    if 'manifesting' in t_str or 'mg' in t_str: return 'MG'
    if 'generator' in t_str or 'pg' in t_str: return 'PG'
    if 'projector' in t_str or 'p' in t_str: return 'P'
    if 'manifestor' in t_str or 'm' in t_str: return 'M'
    if 'reflector' in t_str or 'r' in t_str: return 'R'
    return '不明'

def clean_auth(a):
    a_str = str(a).lower()
    if 'solar' in a_str or 'emotional' in a_str or '感情' in a_str: return '感情'
    if 'sacral' in a_str or '仙骨' in a_str: return '仙骨'
    if 'splenic' in a_str or 'spleen' in a_str or '脾臓' in a_str: return '脾臓'
    if 'heart' in a_str or 'ego' in a_str or 'エゴ' in a_str: return 'エゴ'
    if 'g' in a_str or 'self' in a_str: return 'G'
    if 'mental' in a_str or 'environment' in a_str or '環境' in a_str: return '環境'
    if 'none' in a_str or 'lunar' in a_str or '月' in a_str: return '月（の周期）'
    return '権威なし'

def clean_def(d):
    d_str = str(d).lower()
    if 'wide' in d_str: return 'ワイド'
    if 'single' in d_str: return 'シングル'
    if 'triple' in d_str: return 'トリプル'
    if 'quad' in d_str: return 'クアドルプル'
    if 'simple' in d_str or 'split' in d_str: return 'スプリット'
    if 'none' in d_str or 'nan' in d_str or 'なし' in d_str or 'reflector' in d_str: return '定義なし'
    return '不明'

def make_center_barcode(row):
    c_map = [
        ('Head', '頭'), ('Ajna', 'Aji'), ('Throat', '喉'), ('G', 'Ｇ'),
        ('Heart', 'エ'), ('Sacral', '仙'), ('Spleen', '脾'),
        ('SolarPlexus', '感'), ('Root', 'ル')
    ]
    barcode = []
    for col, short in c_map:
        is_on = (row.get(col) == 1)
        barcode.append(short if is_on else '・')
    return " ".join(barcode)

@st.cache_data
def load_data():
    # ★ 統合完了したマスターファイルを指定 (ファイル名注意)
    try:
        df = pd.read_csv('HD_Master_Archive_1900_2043.csv')
    except:
        # まだ統合が終わっていない場合の予備
        df = pd.read_csv('HD_Special_Dictionary.csv') 

    df['Datetime'] = pd.to_datetime(df['JST_Time'])
    df = df.dropna(subset=['Datetime']).sort_values('Datetime').reset_index(drop=True)

    # ⏳ 滞在時間の計算
    df['Duration_Min'] = df['Datetime'].diff().shift(-1).dt.total_seconds() / 60
    df['Duration_Min'] = df['Duration_Min'].fillna(1).astype(int)

    # データクリーニング
    df['Type_Clean'] = df['Type'].apply(clean_type)
    df['Auth_Clean'] = df['Authority'].apply(clean_auth)
    df['Def_Clean'] = df['Definition'].apply(clean_def)
    
    # グラフ用カテゴリ
    df['Def_Category'] = df['Def_Clean']
    df['Def_Detail_3rd'] = df['Definition'].apply(lambda d: 'ワイド' if 'Wide' in str(d) else ('シンプル' if 'Simple' in str(d) else ' '))

    df['Year'] = df['Datetime'].dt.year
    df['Decade'] = (df['Year'] // 10) * 10 
    df['Center_Barcode'] = df.apply(make_center_barcode, axis=1)

    return df

df = load_data()

# ==========================================
# 📊 グラフ描画職人（完全復活！）
# ==========================================
def draw_sunbursts(target_df):
    col1, col2 = st.columns(2)
    with col1:
        st.write("▼ タイプ × 権威")
        sb1 = target_df.groupby(['Type_Clean', 'Auth_Clean']).size().reset_index(name='count')
        sb1['sort_val'] = sb1['Type_Clean'].map(lambda x: type_order_map.get(x, 99))
        sb1 = sb1.sort_values('sort_val').drop(columns=['sort_val'])
        fig1 = px.sunburst(sb1, path=['Type_Clean', 'Auth_Clean'], values='count', color='Type_Clean', color_discrete_map=color_map)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.write("▼ タイプ × 定義カテゴリ")
        sb2 = target_df.groupby(['Type_Clean', 'Def_Category', 'Def_Detail_3rd']).size().reset_index(name='count')
        sb2['sort_val'] = sb2['Type_Clean'].map(lambda x: type_order_map.get(x, 99))
        sb2 = sb2.sort_values('sort_val').drop(columns=['sort_val'])
        fig2 = px.sunburst(sb2, path=['Type_Clean', 'Def_Category', 'Def_Detail_3rd'], values='count', color='Type_Clean', color_discrete_map=color_map)
        st.plotly_chart(fig2, use_container_width=True)

def draw_type_bars(target_df):
    def plot_type_bar(target_type, container):
        t_df = target_df[target_df['Type_Clean'] == target_type]
        if t_df.empty: return
        counts = t_df['Def_Clean'].value_counts(normalize=True).reset_index()
        counts.columns = ['Def', 'Percentage']
        counts['Percentage'] *= 100
        fig = px.bar(counts, y='Def', x='Percentage', orientation='h', title=f"{target_type} の定義型分布",
                     text=counts['Percentage'].apply(lambda x: f'{x:.1f}%'), color='Def', color_discrete_map=color_map)
        fig.update_layout(showlegend=False, height=200, margin=dict(t=30, b=10, l=10, r=10), xaxis_title=None, yaxis_title=None)
        container.plotly_chart(fig, use_container_width=True)
    c1, c2 = st.columns(2)
    plot_type_bar("MG", c1)
    plot_type_bar("PG", c2)
    plot_type_bar("P", c1)
    plot_type_bar("M", c2)

def draw_all_stats(target_df):
    c1, c2 = st.columns(2)
    with c1:
        st.write("▼ 全体：定義型（詳細順）")
        def_order = ["シングル", "スプリット", "ワイド", "トリプル", "クアドルプル", "定義なし"]
        all_def = target_df['Def_Clean'].value_counts(normalize=True).reindex(def_order).fillna(0).reset_index()
        all_def.columns = ['Def', 'Percentage']
        all_def['Percentage'] *= 100
        fig_def = px.bar(all_def, x='Percentage', y='Def', orientation='h', text=all_def['Percentage'].apply(lambda x: f'{x:.1f}%'),
                         color='Def', color_discrete_map=color_map)
        fig_def.update_layout(showlegend=False, height=250, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_def, use_container_width=True)
    with c2:
        st.write("▼ 全体：権威")
        all_auth = target_df['Auth_Clean'].value_counts(normalize=True).reset_index()
        all_auth.columns = ['Auth', 'Percentage']
        all_auth['Percentage'] *= 100
        fig_auth = px.bar(all_auth, x='Percentage', y='Auth', orientation='h', text=all_auth['Percentage'].apply(lambda x: f'{x:.1f}%'),
                          color='Auth', color_discrete_map=color_map)
        fig_auth.update_layout(showlegend=False, height=250, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_auth, use_container_width=True)

# ==========================================
# 🪐 UI: 年代 / 年 選択
# ==========================================
st.title("🌌 Project Blue Wide - V16")
decades = sorted(df['Decade'].unique())
selected_decade = st.selectbox("🪐 観測年代 (Decade)", decades, index=len(decades)-1)
decade_df = df[df['Decade'] == selected_decade]

years_in_dec = sorted(decade_df['Year'].unique())
selected_year = st.radio("▼ 観測年を選択", years_in_dec, index=len(years_in_dec)-1, horizontal=True)
year_df = df[df['Year'] == selected_year]

# --- 📊 統計表示エリア ---
st.header(f"📊 {selected_year}年：統計サマリー")
draw_sunbursts(year_df)
st.subheader(f"🌐 {selected_year}年：タイプ別分布 ＆ 全体統計")
draw_type_bars(year_df)
draw_all_stats(year_df)

st.divider()

# --- 🗓️ マトリクス ---
st.subheader(f"🗓️ {selected_year}年：ワイド発生マトリクス (12x31)")
wide_days = year_df[year_df['Def_Clean'] == 'ワイド'].groupby([year_df['Datetime'].dt.month, year_df['Datetime'].dt.day]).size().unstack(fill_value=0)
cal_matrix = wide_days.reindex(index=range(1, 13), columns=range(1, 32)).fillna(0)
fig_cal = px.imshow(cal_matrix, labels=dict(x="日", y="月", color="ワイド"), x=list(range(1, 32)), y=list(range(1, 13)),
                    color_continuous_scale=[[0, '#1E1E1E'], [1, '#00BFFF']], aspect="auto")
fig_cal.update_yaxes(autorange="reversed", dtick=1)
fig_cal.update_xaxes(dtick=1)
st.plotly_chart(fig_cal, use_container_width=True)

# --- 📜 タイムラインログ ---
st.subheader(f"📜 {selected_year}年：詳細タイムライン")

log_display = pd.DataFrame({
    '日時': year_df.apply(lambda r: f"{r['Datetime'].strftime('%m/%d %H:%M')} ({r['Duration_Min']}分)", axis=1),
    'Type': year_df['Type_Clean'],
    '定義型': year_df['Def_Clean'],
    '天体トリガー': year_df['Trigger'],
    'チャネル': year_df['Channels'],
    'センター': year_df['Center_Barcode']
})

def style_log(row):
    styles = [''] * len(row)
    if row['Type'] in color_map: styles[1] = f'background-color: {color_map[row["Type"]]}; color: white; font-weight: bold;'
    if row['定義型'] == 'ワイド': styles[2] = f'color: {color_map["ワイド"]}; font-weight: bold;'
    styles[5] = 'font-family: monospace; letter-spacing: 1px;' 
    return styles

st.dataframe(log_display.style.apply(style_log, axis=1), hide_index=True, use_container_width=True, height=600)
