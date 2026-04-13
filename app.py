import streamlit as st
import pandas as pd
import plotly.express as px

# --- ページ設定 ---
st.set_page_config(page_title="Project Blue Wide", layout="wide", page_icon="🌌")

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
            if pwd == "blue-wide-90":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Access Denied.")
    return False

if not check_password(): st.stop()

# --- 🎨 カラーパレット定義 ---
color_map = {
    "MG": "#E53935", "PG": "#FFB300", "P": "#43A047", 
    "M": "#3949AB", "R": "#9E9E9E", "ワイド": "#00BFFF", "スプリット": "#B0BEC5", "シンプル": "#B0BEC5",
    "シングル": "#CFD8DC", "トリプル": "#90A4AE", "クアドルプル": "#78909C",
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
    time_cols = [c for c in df.columns if 'time' in c.lower() or '日時' in c]
    type_cols = [c for c in df.columns if 'type' in c.lower() or 'タイプ' in c]
    auth_cols = [c for c in df.columns if 'auth' in c.lower() or '権威' in c]
    def_cols = [c for c in df.columns if 'def' in c.lower() or '定義' in c]
    cause_cols = [c for c in df.columns if 'cause' in c.lower() or '原因' in c or 'チャネル' in c or 'channel' in c.lower()]
    
    t_col = time_cols[0] if time_cols else df.columns[0]
    ty_col = type_cols[0] if type_cols else df.columns[1]
    a_col = auth_cols[0] if auth_cols else df.columns[2]
    d_col = def_cols[0] if def_cols else df.columns[3]
    
    df['Datetime'] = pd.to_datetime(df[t_col])
    df['Type_Clean'] = df[ty_col].apply(clean_type)
    df['Auth_Clean'] = df[a_col].apply(clean_auth)
    df['Def_Original'] = df[d_col].apply(clean_def)
    df['Cause_Info'] = df[cause_cols[0]] if cause_cols else "データなし"

    df['Def_Category'] = df['Def_Original'].replace({'ワイド': 'スプリット'})
    df['Def_Detail_3rd'] = df['Def_Original'].apply(lambda d: 'シンプル' if d == 'スプリット' else d + " ")
    df['Year'] = df['Datetime'].dt.year
    df['Month'] = df['Datetime'].dt.month
    df['Day'] = df['Datetime'].dt.day
    return df

df = load_data()
years = sorted(df['Year'].unique())
default_year = 2026 if 2026 in years else years[-1]
selected_year = st.selectbox("📅 観測年", years, index=years.index(default_year))
year_df = df[df['Year'] == selected_year]

# --- 📊 1. 上段：2重/3重円グラフ ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("タイプ × 権威")
    sb1 = year_df.groupby(['Type_Clean', 'Auth_Clean']).size().reset_index(name='count')
    fig1 = px.sunburst(sb1, path=['Type_Clean', 'Auth_Clean'], values='count', color='Type_Clean', color_discrete_map=color_map)
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.subheader("タイプ × 定義カテゴリ × 詳細")
    sb2 = year_df.groupby(['Type_Clean', 'Def_Category', 'Def_Detail_3rd'], dropna=False).size().reset_index(name='count')
    fig2 = px.sunburst(sb2, path=['Type_Clean', 'Def_Category', 'Def_Detail_3rd'], values='count', color='Type_Clean', color_discrete_map=color_map)
    st.plotly_chart(fig2, use_container_width=True)

# --- 📊 2. 中段：タイプ別定義型百分率棒グラフ ---
st.divider()
st.subheader(f"📊 {selected_year}年：タイプ別 定義型百分率 (Reflector除く)") # ★年を追加

def plot_type_bar(target_type, container):
    target_df = year_df[year_df['Type_Clean'] == target_type]
    if target_df.empty: return
    counts = target_df['Def_Original'].value_counts(normalize=True).reset_index()
    counts.columns = ['Def', 'Percentage']
    counts['Percentage'] *= 100
    fig = px.bar(counts, y='Def', x='Percentage', orientation='h', title=f"{target_type} の定義型分布",
                 text=counts['Percentage'].apply(lambda x: f'{x:.1f}%'),
                 color='Def', color_discrete_map=color_map)
    fig.update_layout(showlegend=False, height=200, margin=dict(t=30, b=10, l=10, r=10), xaxis_title=None, yaxis_title=None)
    container.plotly_chart(fig, use_container_width=True)

bar_col1, bar_col2 = st.columns(2)
plot_type_bar("MG", bar_col1)
plot_type_bar("PG", bar_col2)
plot_type_bar("P", bar_col1)
plot_type_bar("M", bar_col2)

# --- 📊 3. 中段：ALL全体グラフ ---
st.divider()
st.subheader(f"🌐 {selected_year}年：ALL 全体統計") # ★年を追加
all_col1, all_col2 = st.columns(2)

with all_col1:
    st.write("▼ 全体：定義型（スプリット詳細順）")
    def_order = ["シングル", "スプリット", "ワイド", "トリプル", "クアドルプル"]
    all_def = year_df['Def_Original'].value_counts(normalize=True).reindex(def_order).fillna(0).reset_index()
    all_def.columns = ['Def', 'Percentage']
    all_def['Percentage'] *= 100
    fig_all_def = px.bar(all_def, x='Percentage', y='Def', orientation='h', text=all_def['Percentage'].apply(lambda x: f'{x:.1f}%'),
                         color='Def', color_discrete_map=color_map)
    fig_all_def.update_layout(showlegend=False, height=250, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_all_def, use_container_width=True)

with all_col2:
    st.write("▼ 全体：権威（多い順）")
    all_auth = year_df['Auth_Clean'].value_counts(normalize=True).reset_index()
    all_auth.columns = ['Auth', 'Percentage']
    all_auth['Percentage'] *= 100
    fig_all_auth = px.bar(all_auth, x='Percentage', y='Auth', orientation='h', text=all_auth['Percentage'].apply(lambda x: f'{x:.1f}%'),
                          color='Auth', color_discrete_map=color_map)
    fig_all_auth.update_layout(showlegend=False, height=250, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_all_auth, use_container_width=True)

# --- 📅 4. 下段：特異日カレンダー ---
st.divider()
st.subheader(f"🗓️ {selected_year}年：ワイド発生マトリクス (12x31)")
wide_days = year_df[year_df['Def_Original'] == 'ワイド'].groupby(['Month', 'Day']).size().unstack(fill_value=0)
cal_matrix = wide_days.reindex(index=range(1, 13), columns=range(1, 32)).fillna(0)
fig_cal = px.imshow(cal_matrix, labels=dict(x="日", y="月", color="ワイド"), x=list(range(1, 32)), y=list(range(1, 13)),
                    color_continuous_scale=[[0, '#1E1E1E'], [1, '#00BFFF']], aspect="auto")
fig_cal.update_yaxes(autorange="reversed", dtick=1)
fig_cal.update_xaxes(dtick=1)
st.plotly_chart(fig_cal, use_container_width=True)

# --- 📜 5. 最下段：タイムライン・ログ ---
st.divider()
st.subheader(f"📜 {selected_year}年：タイムライン・ログ")

log_display = pd.DataFrame({
    '日時': year_df['Datetime'].dt.strftime('%m/%d %H:%M'),
    'Type': year_df['Type_Clean'],
    '定義型': year_df['Def_Original'],
    '権威': year_df['Auth_Clean'],
    'トリガー': year_df['Cause_Info']
})

def style_log(row):
    styles = [''] * len(row)
    if row['Type'] in color_map: styles[1] = f'background-color: {color_map[row["Type"]]}; color: white; font-weight: bold;'
    if row['定義型'] == 'ワイド': styles[2] = f'color: {color_map["ワイド"]}; font-weight: bold;'
    return styles

# 表のスタイルを設定（文字の折り返しを追加）
styled_df = log_display.style.apply(style_log, axis=1)
styled_df = styled_df.set_properties(subset=['トリガー'], **{'white-space': 'normal'})

# hide_index=True で左の列番号を消去！ use_container_width=Trueで横幅を広々と使います。
st.dataframe(styled_df, hide_index=True, use_container_width=True, height=500)
