# =====================================================================
# 🌌 Project Blue Wide - Daily Deep Dive
# 📅 特定日付の詳細分析ダッシュボード
# =====================================================================
 
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
 
# --- ページ設定 ---
st.set_page_config(page_title="HD Daily Analysis", layout="wide", page_icon="📅")
 
# --- 🔐 秘密基地の鍵 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: 
        return True
    
    st.markdown("<h1 style='text-align: center; color: #00BFFF;'>📅 HD Daily Deep Dive</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Access Code", type="password")
        if st.button("System Login"):
            if pwd == "wide":
                st.session_state["password_correct"] = True
                st.rerun()
            else: 
                st.error("Access Denied.")
    return False
 
if not check_password(): 
    st.stop()
 
# --- 🎨 カラーパレット定義 ---
color_map = {
    "MG": "#E53935", "PG": "#FFB300", "P": "#43A047", 
    "M": "#3949AB", "R": "#9E9E9E", 
    "ワイド": "#00BFFF", "スプリット": "#B0BEC5", "シンプル": "#B0BEC5",
    "シングル": "#CFD8DC", "トリプル": "#90A4AE", "クアドルプル": "#78909C", "定義なし": "#ECEFF1",
    "感情": "#FFCDD2", "仙骨": "#F8BBD0", "脾臓": "#E1BEE7", 
    "エゴ": "#D1C4E9", "G": "#C5CAE9", "環境": "#B3E5FC", 
    "月（の周期）": "#B2DFDB", "権威なし": "#ECEFF1"
}
 
type_order = ["MG", "PG", "P", "M", "R"]
 
# --- 🛠️ データクリーニング関数 ---
def clean_type(t):
    t_str = str(t).lower()
    if 'manifesting' in t_str or 'mg' in t_str: return 'MG'
    if 'generator' in t_str or 'pg' in t_str: return 'PG'
    if 'projector' in t_str or 'p' in t_str: return 'P'
    if 'manifestor' in t_str or 'm' in t_str: return 'M'
    if 'reflector' in t_str or 'r' in t_str: return 'R'
    return '不明(タイプ)'
 
def clean_auth(a):
    a_str = str(a).lower()
    if 'solar' in a_str or 'emotional' in a_str or '感情' in a_str: return '感情'
    if 'sacral' in a_str or '仙骨' in a_str: return '仙骨'
    if 'splenic' in a_str or 'spleen' in a_str or '脾臓' in a_str: return '脾臓'
    if 'heart' in a_str or 'ego' in a_str or 'エゴ' in a_str: return 'エゴ'
    if 'g' in a_str or 'self' in a_str: return 'G'
    if 'mental' in a_str or 'environment' in a_str or '環境' in a_str: return '環境'
    if 'none' in a_str or 'lunar' in a_str or '月' in a_str or 'nan' in a_str or 'なし' in a_str or 'outer' in a_str: 
        return '月（の周期）'
    return '権威なし'
 
def clean_def(d):
    d_str = str(d).lower()
    if 'wide' in d_str: return 'ワイド'
    if 'single' in d_str: return 'シングル'
    if 'triple' in d_str: return 'トリプル'
    if 'quad' in d_str: return 'クアドルプル'
    if 'simple' in d_str or 'split' in d_str: return 'スプリット'
    if 'none' in d_str or 'nan' in d_str or 'なし' in d_str: return '定義なし'
    return '不明(定義)'
 
# センター名の対応表
CENTER_NAMES = {
    'Head': '頭脳', 'Ajna': '思考', 'Throat': '表現',
    'G': '自己', 'Heart': '意志', 'Sacral': '生命力',
    'Spleen': '直感', 'SolarPlexus': '感情', 'Root': '活力'
}
 
# センターの定義状態を取得
def get_center_states(row):
    states = {}
    for eng, jpn in CENTER_NAMES.items():
        if eng in row:
            states[jpn] = bool(row[eng] == 1)
        else:
            # 'Centers'カラムから判定
            centers_str = str(row.get('Centers', ''))
            states[jpn] = jpn in centers_str
    return states
 
# ゲート情報を抽出
def extract_gates(row):
    gates = []
    gate_cols = [c for c in row.index if c.startswith('P_') or c.startswith('D_')]
    
    for col in gate_cols:
        if pd.notna(row[col]):
            gate_str = str(row[col])
            if '.' in gate_str:
                gate_num = gate_str.split('.')[0]
                line_num = gate_str.split('.')[1]
                is_design = col.startswith('D_')
                planet = col.split('_')[1] if len(col.split('_')) > 1 else ''
                
                gates.append({
                    'ゲート': gate_num,
                    'ライン': line_num,
                    'タイプ': 'デザイン(赤)' if is_design else 'パーソナリティ(黒)',
                    '天体': planet
                })
    
    return pd.DataFrame(gates) if gates else pd.DataFrame()
 
# --- 📊 データ読み込み ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('HD_Master_Archive_1900_2043.zip')
    except:
        try:
            df = pd.read_csv('HD_Special_Dictionary.csv')
        except:
            st.error("⚠️ データファイルが見つかりません。")
            st.stop()
    
    # 日時カラムの検出
    jst_cols = [c for c in df.columns if 'jst' in c.lower() or '日本時間' in c]
    time_cols = [c for c in df.columns if 'time' in c.lower() or '日時' in c]
    t_col = jst_cols[0] if jst_cols else (time_cols[0] if time_cols else df.columns[0])
    
    df['Datetime'] = pd.to_datetime(df[t_col])
    df = df.dropna(subset=['Datetime']).sort_values('Datetime').reset_index(drop=True)
    
    # 滞在時間の計算
    df['Duration_Min'] = df['Datetime'].diff().shift(-1).dt.total_seconds() / 60
    df['Duration_Min'] = df['Duration_Min'].fillna(1).astype(int)
    
    # カラムの検出とクリーニング
    type_cols = [c for c in df.columns if 'type' in c.lower() or 'タイプ' in c]
    auth_cols = [c for c in df.columns if 'auth' in c.lower() or '権威' in c]
    def_cols = [c for c in df.columns if 'def' in c.lower() or '定義' in c]
    chan_cols = [c for c in df.columns if 'channel' in c.lower() or 'チャネル' in c]
    
    df['Type_Clean'] = df[type_cols[0] if type_cols else df.columns[1]].apply(clean_type)
    df['Auth_Clean'] = df[auth_cols[0] if auth_cols else df.columns[2]].apply(clean_auth)
    df['Def_Clean'] = df[def_cols[0] if def_cols else df.columns[3]].apply(clean_def)
    df['Channels'] = df[chan_cols[0]] if chan_cols else "データなし"
    
    # 日付情報
    df['Date'] = df['Datetime'].dt.date
    df['Year'] = df['Datetime'].dt.year
    df['Month'] = df['Datetime'].dt.month
    df['Day'] = df['Datetime'].dt.day
    df['Hour'] = df['Datetime'].dt.hour
    df['Minute'] = df['Datetime'].dt.minute
    
    return df
 
df = load_data()
 
# ==========================================
# 🎯 UI: 日付選択
# ==========================================
st.title("📅 HD Daily Deep Dive - 特定日の詳細分析")
 
# 利用可能な日付範囲を取得
min_date = df['Date'].min()
max_date = df['Date'].max()
 
col1, col2, col3 = st.columns(3)
with col1:
    available_years = sorted(df['Year'].unique())
    selected_year = st.selectbox("📆 年", available_years, 
                                 index=available_years.index(2026) if 2026 in available_years else len(available_years)-1)
 
# 選択された年で利用可能な月を取得
year_df = df[df['Year'] == selected_year]
available_months = sorted(year_df['Month'].unique())
 
with col2:
    selected_month = st.selectbox("📆 月", available_months,
                                  index=0 if available_months else 0)
 
# 選択された年月で利用可能な日を取得
month_df = year_df[year_df['Month'] == selected_month]
available_days = sorted(month_df['Day'].unique())
 
with col3:
    selected_day = st.selectbox("📆 日", available_days,
                                index=0 if available_days else 0)
 
# 選択された日付のデータを抽出
selected_date = date(selected_year, selected_month, selected_day)
day_df = df[df['Date'] == selected_date].copy()
 
if day_df.empty:
    st.warning(f"⚠️ {selected_date} のデータがありません。")
    st.stop()
 
st.divider()
 
# ==========================================
# 📊 サマリー統計
# ==========================================
st.header(f"📊 {selected_date.strftime('%Y年%m月%d日')} のサマリー")
 
col1, col2, col3, col4 = st.columns(4)
 
with col1:
    st.metric("データ数", f"{len(day_df)} 件")
    
with col2:
    total_duration = day_df['Duration_Min'].sum()
    st.metric("合計時間", f"{total_duration} 分")
    
with col3:
    most_common_type = day_df['Type_Clean'].mode()[0] if not day_df.empty else "N/A"
    type_pct = (day_df['Type_Clean'] == most_common_type).sum() / len(day_df) * 100
    st.metric("最多タイプ", f"{most_common_type} ({type_pct:.1f}%)")
    
with col4:
    wide_count = (day_df['Def_Clean'] == 'ワイド').sum()
    wide_pct = wide_count / len(day_df) * 100 if len(day_df) > 0 else 0
    st.metric("ワイド発生", f"{wide_count} 件 ({wide_pct:.1f}%)")
 
st.divider()
 
# ==========================================
# 📈 分布グラフ
# ==========================================
st.header(f"📈 {selected_date.strftime('%Y年%m月%d日')} の分布分析")
 
# タイプ分布
col1, col2 = st.columns(2)
 
with col1:
    st.subheader("🎯 タイプ分布")
    type_counts = day_df['Type_Clean'].value_counts().reset_index()
    type_counts.columns = ['Type', 'Count']
    type_counts['Percentage'] = (type_counts['Count'] / len(day_df) * 100).round(1)
    
    fig_type = px.pie(type_counts, values='Count', names='Type', 
                      color='Type', color_discrete_map=color_map,
                      hover_data=['Percentage'])
    fig_type.update_traces(textposition='inside', textinfo='label+percent')
    fig_type.update_layout(showlegend=True, height=350)
    st.plotly_chart(fig_type, use_container_width=True)
 
with col2:
    st.subheader("🔷 定義型分布")
    def_counts = day_df['Def_Clean'].value_counts().reset_index()
    def_counts.columns = ['Def', 'Count']
    def_counts['Percentage'] = (def_counts['Count'] / len(day_df) * 100).round(1)
    
    fig_def = px.pie(def_counts, values='Count', names='Def',
                     color='Def', color_discrete_map=color_map,
                     hover_data=['Percentage'])
    fig_def.update_traces(textposition='inside', textinfo='label+percent')
    fig_def.update_layout(showlegend=True, height=350)
    st.plotly_chart(fig_def, use_container_width=True)
 
# 権威分布
col3, col4 = st.columns(2)
 
with col3:
    st.subheader("⚖️ 権威分布")
    auth_counts = day_df['Auth_Clean'].value_counts().reset_index()
    auth_counts.columns = ['Auth', 'Count']
    auth_counts['Percentage'] = (auth_counts['Count'] / len(day_df) * 100).round(1)
    
    fig_auth = px.bar(auth_counts, x='Count', y='Auth', orientation='h',
                      color='Auth', color_discrete_map=color_map,
                      text='Percentage')
    fig_auth.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_auth.update_layout(showlegend=False, height=350, xaxis_title="件数", yaxis_title="")
    st.plotly_chart(fig_auth, use_container_width=True)
 
with col4:
    st.subheader("⏰ 時間別分布")
    hour_counts = day_df.groupby('Hour').size().reset_index(name='Count')
    
    fig_hour = px.bar(hour_counts, x='Hour', y='Count',
                      labels={'Hour': '時', 'Count': '件数'})
    fig_hour.update_layout(showlegend=False, height=350, xaxis_title="時刻", yaxis_title="件数")
    fig_hour.update_xaxes(dtick=1)
    st.plotly_chart(fig_hour, use_container_width=True)
 
st.divider()
 
# ==========================================
# 🎨 センター定義状態の可視化
# ==========================================
st.header(f"🎨 センター定義状態の分析")
 
# 各センターの定義率を計算
center_stats = []
for eng, jpn in CENTER_NAMES.items():
    if eng in day_df.columns:
        defined_count = (day_df[eng] == 1).sum()
    else:
        defined_count = day_df.apply(lambda row: jpn in str(row.get('Centers', '')), axis=1).sum()
    
    defined_pct = (defined_count / len(day_df) * 100) if len(day_df) > 0 else 0
    center_stats.append({
        'センター': jpn,
        '定義率': defined_pct,
        '定義数': defined_count,
        '未定義数': len(day_df) - defined_count
    })
 
center_df = pd.DataFrame(center_stats)
 
# センター定義率のグラフ
fig_centers = px.bar(center_df, x='センター', y='定義率',
                     text='定義率',
                     color='定義率',
                     color_continuous_scale=['#ECEFF1', '#00BFFF'])
fig_centers.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig_centers.update_layout(showlegend=False, height=400, yaxis_title="定義率 (%)")
st.plotly_chart(fig_centers, use_container_width=True)
 
# センター詳細テーブル
st.subheader("📋 センター詳細")
display_center_df = center_df[['センター', '定義率', '定義数', '未定義数']].copy()
display_center_df['定義率'] = display_center_df['定義率'].apply(lambda x: f"{x:.1f}%")
st.dataframe(display_center_df, hide_index=True, use_container_width=True)
 
st.divider()
 
# ==========================================
# 🕐 時系列タイムテーブル
# ==========================================
st.header(f"🕐 {selected_date.strftime('%Y年%m月%d日')} のタイムテーブル")
 
# 時刻でソート
day_df_sorted = day_df.sort_values('Datetime').reset_index(drop=True)
 
# 表示用データフレーム作成
timeline_df = pd.DataFrame({
    '時刻': day_df_sorted['Datetime'].dt.strftime('%H:%M'),
    '滞在': day_df_sorted['Duration_Min'].apply(lambda x: f"{x}分"),
    'タイプ': day_df_sorted['Type_Clean'],
    '定義型': day_df_sorted['Def_Clean'],
    '権威': day_df_sorted['Auth_Clean']
})
 
# スタイル適用
def style_timeline(row):
    styles = [''] * len(row)
    
    # タイプに色付け
    if row['タイプ'] in color_map:
        styles[2] = f'background-color: {color_map[row["タイプ"]]}; color: white; font-weight: bold;'
    
    # ワイドを強調
    if row['定義型'] == 'ワイド':
        styles[3] = f'color: {color_map["ワイド"]}; font-weight: bold;'
    
    # 権威に色付け
    if row['権威'] in color_map:
        styles[4] = f'background-color: {color_map[row["権威"]]}; color: #333;'
    
    return styles
 
styled_timeline = timeline_df.style.apply(style_timeline, axis=1)
st.dataframe(styled_timeline, hide_index=True, use_container_width=True, height=400)
 
st.divider()
 
# ==========================================
# 🔍 チャネル・ゲート詳細情報
# ==========================================
st.header(f"🔍 チャネル・ゲート詳細情報")
 
# 時刻選択
selected_time_idx = st.selectbox(
    "詳細を見たい時刻を選択",
    range(len(day_df_sorted)),
    format_func=lambda x: f"{day_df_sorted.iloc[x]['Datetime'].strftime('%H:%M')} - {day_df_sorted.iloc[x]['Type_Clean']} / {day_df_sorted.iloc[x]['Def_Clean']}"
)
 
selected_row = day_df_sorted.iloc[selected_time_idx]
 
# 基本情報
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("タイプ", selected_row['Type_Clean'])
with col2:
    st.metric("定義型", selected_row['Def_Clean'])
with col3:
    st.metric("権威", selected_row['Auth_Clean'])
with col4:
    duration = selected_row['Duration_Min']
    st.metric("滞在時間", f"{duration} 分")
 
st.subheader("🔗 チャネル情報")
channels_info = str(selected_row['Channels'])
if channels_info and channels_info != "データなし" and channels_info != 'nan':
    # チャネル情報を整形して表示
    channels_list = channels_info.split(',') if ',' in channels_info else [channels_info]
    
    channel_data = []
    for ch in channels_list:
        ch = ch.strip()
        if ch:
            channel_data.append({'チャネル': ch})
    
    if channel_data:
        channel_df = pd.DataFrame(channel_data)
        st.dataframe(channel_df, hide_index=True, use_container_width=True)
    else:
        st.info("チャネル情報が見つかりませんでした。")
else:
    st.info("チャネル情報が見つかりませんでした。")
 
st.subheader("🎯 ゲート情報")
 
# センター定義状態
st.write("**📍 定義されたセンター**")
center_states = get_center_states(selected_row)
defined_centers = [name for name, is_defined in center_states.items() if is_defined]
undefined_centers = [name for name, is_defined in center_states.items() if not is_defined]
 
col1, col2 = st.columns(2)
with col1:
    if defined_centers:
        st.success(f"✅ 定義: {', '.join(defined_centers)}")
    else:
        st.info("定義されたセンターなし")
        
with col2:
    if undefined_centers:
        st.warning(f"⚪ 未定義: {', '.join(undefined_centers)}")
 
# ゲート詳細
st.write("**🚪 アクティベートされたゲート**")
gates_df = extract_gates(selected_row)
 
if not gates_df.empty:
    # デザイン（赤）とパーソナリティ（黒）で分けて表示
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🔴 デザイン（赤）**")
        design_gates = gates_df[gates_df['タイプ'] == 'デザイン(赤)']
        if not design_gates.empty:
            st.dataframe(design_gates[['天体', 'ゲート', 'ライン']], hide_index=True, use_container_width=True)
        else:
            st.info("デザインゲートなし")
    
    with col2:
        st.write("**⚫ パーソナリティ（黒）**")
        personality_gates = gates_df[gates_df['タイプ'] == 'パーソナリティ(黒)']
        if not personality_gates.empty:
            st.dataframe(personality_gates[['天体', 'ゲート', 'ライン']], hide_index=True, use_container_width=True)
        else:
            st.info("パーソナリティゲートなし")
    
    # 全ゲート一覧
    with st.expander("📋 全ゲート一覧を表示"):
        st.dataframe(gates_df, hide_index=True, use_container_width=True)
else:
    st.info("ゲート情報が見つかりませんでした。")
 
# ==========================================
# 📥 データダウンロード
# ==========================================
st.divider()
st.subheader("📥 データダウンロード")
 
# CSVダウンロード
csv = day_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label=f"📅 {selected_date.strftime('%Y%m%d')} のデータをダウンロード (CSV)",
    data=csv,
    file_name=f"HD_Daily_{selected_date.strftime('%Y%m%d')}.csv",
    mime='text/csv'
)
 