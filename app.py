import streamlit as st
import pandas as pd
import plotly.express as px

# --- ページ設定 ---
st.set_page_config(page_title="Project Blue Wide", layout="wide", page_icon="🌌")

# --- 🔐 秘密基地の鍵（パスワード） ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True
    st.markdown("<h1 style='text-align: center; color: #00BFFF;'>🌌 Project Blue Wide</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Access Code", type="password")
        if st.button("System Login"):
            if pwd == "blue-wide-90":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Access Denied.")
    return False

if not check_password(): st.stop()

# --- 🎨 カラーパレット定義 ---
color_map = {
    "MG": "#E53935", "PG": "#FFB300", "P": "#43A047", 
    "M": "#3949AB", "R": "#9E9E9E", "ワイド": "#00BFFF", "シンプル": "#B0BEC5",
    "感情": "#FFCDD2", "仙骨": "#F8BBD0", "脾臓": "#E1BEE7", "エゴ": "#D1C4E9", "G": "#C5CAE9", "環境": "#B3E5FC", "月": "#B2DFDB"
}
type_order = ["MG", "PG", "P", "M", "R"]

# --- 🛠️ データ変換関数 ---
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
    if 'none' in a_str or 'lunar' in a_str or '月' in a_str: return '月'
    return '不明(権威)'

def clean_def(d):
    d_str = str(d).lower()
    if 'wide' in d_str: return 'ワイド'
    if 'single' in d_str: return 'シングル'
    if 'simple' in d_str or 'split' in d_str: return 'スプリット'
    if 'triple' in d_str: return 'トリプル'
    if 'quad' in d_str: return 'クアドルプル'
    return '不明(定義)'

@st.cache_data
def load_data():
    df = pd.read_csv('HD_Special_Dictionary.csv')
    
    # 🔍 V1の賢い「列名自動検索システム」を超強化（絶対エラー出さないマン）
    time_cols = [c for c in df.columns if 'time' in c.lower() or '日時' in c]
    type_cols = [c for c in df.columns if 'type' in c.lower() or 'タイプ' in c]
    auth_cols = [c for c in df.columns if 'auth' in c.lower() or '権威' in c]
    def_cols = [c for c in df.columns if 'def' in c.lower() or '定義' in c]
    
    # 見つからなかった場合は左から順に強制割り当てする安全装置
    t_col = time_cols[0] if time_cols else df.columns[0]
    ty_col = type_cols[0] if type_cols else df.columns[1]
    a_col = auth_cols[0] if auth_cols else df.columns[2]
    d_col = def_cols[0] if def_cols else df.columns[3]
    
    df['Datetime'] = pd.to_datetime(df[t_col])
    
    df['Type_Clean'] = df[ty_col].apply(clean_type)
    df['Auth_Clean'] = df[a_col].apply(clean_auth)
    df['Def_Original'] = df[d_col].apply(clean_def)

    # 3重円用の階層データ作成
    def map_category(d):
        if d in ['ワイド', 'スプリット']: return 'スプリット'
        return d

    def map_detail(d):
        if d == 'ワイド': return 'ワイド'
        if d == 'スプリット': return 'シンプル'
        return None

    df['Def_Category'] = df['Def_Original'].apply(map_category)
    df['Def_Detail_3rd'] = df['Def_Original'].apply(map_detail)
    df['Year'] = df['Datetime'].dt.year
    return df

# ★これ！この1行が消えていたのが原因でした！！
df = load_data()

# 🎯 デフォルト年を2026年に設定
years = sorted(df['Year'].unique())
default_year = 2026 if 2026 in years else years[-1]
default_index = years.index(default_year)
selected_year = st.selectbox("📅 観測年", years, index=default_index)

year_df = df[df['Year'] == selected_year]

# 並び替え用
type_order_map = {t: i for i, t in enumerate(type_order)}

# --- 📊 1. 上段：2重/3重円グラフ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("タイプ × 権威")
    sb1 = year_df.groupby(['Type_Clean', 'Auth_Clean']).size().reset_index(name='count')
    sb1 = sb1[sb1['count'] > 0]
    sb1['sort_val'] = sb1['Type_Clean'].map(lambda x: type_order_map.get(x, 99))
    sb1 = sb1.sort_values('sort_val').drop(columns=['sort_val'])
    
    fig1 = px.sunburst(sb1, path=['Type_Clean', 'Auth_Clean'], values='count',
                       color='Type_Clean', color_discrete_map=color_map)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("タイプ × 定義カテゴリ × 詳細")
    sb2 = year_df.groupby(['Type_Clean', 'Def_Category', 'Def_Detail_3rd'], dropna=False).size().reset_index(name='count')
    sb2 = sb2[sb2['count'] > 0]
    sb2['sort_val'] = sb2['Type_Clean'].map(lambda x: type_order_map.get(x, 99))
    sb2 = sb2.sort_values('sort_val').drop(columns=['sort_val'])
    
    fig2 = px.sunburst(sb2, path=['Type_Clean', 'Def_Category', 'Def_Detail_3rd'], values='count',
                       color='Type_Clean', color_discrete_map=color_map)
    st.plotly_chart(fig2, use_container_width=True)

# --- 📝 2. 下段：着色されたタイムライン・ログ ---
st.divider()
st.subheader("📜 タイムライン・ログ")

log_display = pd.DataFrame({
    '日時': year_df['Datetime'].dt.strftime('%m/%d %H:%M'),
    'Type': year_df['Type_Clean'],
    '定義型': year_df['Def_Original'],
    '権威': year_df['Auth_Clean']
})

def style_log(row):
    styles = [''] * len(row)
    t = row['Type']
    if t in color_map:
        styles[1] = f'background-color: {color_map[t]}; color: white; font-weight: bold;'
    if row['定義型'] == 'ワイド':
        styles[2] = f'color: {color_map["ワイド"]}; font-weight: bold; font-size: 1.1em;'
    return styles

st.dataframe(log_display.style.apply(style_log, axis=1), use_container_width=True, height=500)
