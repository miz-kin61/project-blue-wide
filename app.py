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
    "M": "#3949AB", "R": "#9E9E9E", "ワイド": "#00BFFF",
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
    return '不明'

def clean_auth(a):
    a_str = str(a).lower()
    if 'solar' in a_str or 'emotional' in a_str or '感情' in a_str: return '感情'
    if 'sacral' in a_str or '仙骨' in a_str: return '仙骨'
    if 'splenic' in a_str or 'spleen' in a_str or '脾臓' in a_str: return '脾臓'
    if 'heart' in a_str or 'ego' in a_str or 'エゴ' in a_str: return 'エゴ'
    if 'g' in a_str or 'self' in a_str: return 'G'
    if 'mental' in a_str or 'environment' in a_str or '環境' in a_str: return '環境'
    if 'none' in a_str or 'lunar' in a_str or '月' in a_str: return '月'
    return '不明'

def clean_def(d):
    d_str = str(d).lower()
    if 'wide' in d_str: return 'ワイド'
    if 'single' in d_str: return 'シングル'
    if 'simple' in d_str or 'split' in d_str: return 'スプリット' # シンプルスプリット等
    if 'triple' in d_str: return 'トリプル'
    if 'quad' in d_str: return 'クアドルプル'
    return '不明'

@st.cache_data
def load_data():
    df = pd.read_csv('HD_Special_Dictionary.csv')
    time_col = [c for c in df.columns if 'time' in c.lower() or '日時' in c][0]
    df['Datetime'] = pd.to_datetime(df[time_col])
    
    # 基本の変換
    df['Type_Clean'] = df.iloc[:, 1].apply(clean_type) # 2列目がタイプと想定
    df['Auth_Clean'] = df.iloc[:, 2].apply(clean_auth) # 3列目が権威と想定
    df['Def_Detail'] = df.iloc[:, 3].apply(clean_def) # 4列目が定義型と想定

    # ❶-(2) 3重円用の階層データ作成
    # 第2層：カテゴリ（ワイドもスプリットに含める）
    df['Def_Category'] = df['Def_Detail'].replace({'ワイド': 'スプリット'})
    # 第3層：詳細はそのまま Def_Detail を使う
    
    df['Year'] = df['Datetime'].dt.year
    return df

df = load_data()
years = sorted(df['Year'].unique())
selected_year = st.selectbox("📅 観測年", years, index=len(years)-1)
year_df = df[df['Year'] == selected_year]

# --- 📊 1. 上段：2重/3重円グラフ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("タイプ × 権威")
    sb1 = year_df.groupby(['Type_Clean', 'Auth_Clean']).size().reset_index(name='count')
    sb1['Type_Clean'] = pd.Categorical(sb1['Type_Clean'], categories=type_order, ordered=True)
    sb1 = sb1.sort_values('Type_Clean')
    fig1 = px.sunburst(sb1, path=['Type_Clean', 'Auth_Clean'], values='count',
                       color='Type_Clean', color_discrete_map=color_map)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("タイプ × 定義カテゴリ × 詳細（3重円）")
    # ❶-(2) 3層のパスを指定
    sb2 = year_df.groupby(['Type_Clean', 'Def_Category', 'Def_Detail']).size().reset_index(name='count')
    sb2['Type_Clean'] = pd.Categorical(sb2['Type_Clean'], categories=type_order, ordered=True)
    sb2 = sb2.sort_values('Type_Clean')
    # color='Type_Clean' にすることで、中心から外側までタイプの色が引き継がれます
    fig2 = px.sunburst(sb2, path=['Type_Clean', 'Def_Category', 'Def_Detail'], values='count',
                       color='Type_Clean', color_discrete_map=color_map)
    st.plotly_chart(fig2, use_container_width=True)

# --- 📝 2. 下段：着色されたタイムライン・ログ ---
st.divider()
st.subheader("📜 タイムライン・ログ")

# 表示用データの作成
log_display = pd.DataFrame({
    '日時': year_df['Datetime'].dt.strftime('%m/%d %H:%M'),
    'Type': year_df['Type_Clean'],
    '定義型': year_df['Def_Detail'],
    '権威': year_df['Auth_Clean']
})

# ❷ ログの着色ロジック
def style_log(row):
    styles = [''] * len(row)
    # ⑴ タイプ別着色
    t = row['Type']
    if t in color_map:
        styles[1] = f'background-color: {color_map[t]}; color: white; font-weight: bold;'
    # ⑵ ワイドの太字青文字
    if row['定義型'] == 'ワイド':
        styles[2] = f'color: {color_map["ワイド"]}; font-weight: bold; font-size: 1.1em;'
    return styles

# スタイルを適用して表示
st.dataframe(log_display.style.apply(style_log, axis=1), use_container_width=True, height=500)
