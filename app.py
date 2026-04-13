import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 🔐 パスワード保護（セキュリティ）
# ==========================================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.title("🔐 Project Blue Wide - Private Access")
    pwd = st.text_input("合言葉を入力してください", type="password")
    if st.button("ログイン"):
        if pwd == "wide": 
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("合言葉が違います。")
    return False

if not check_password():
    st.stop()

# ==========================================
# 2. 📊 データ読み込み（時間のズレを完全解消）
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('HD_Special_Dictionary.csv')
        
        # もし JST_Time があるならそれを使い、なければ UTC_Time に9時間足す
        if 'JST_Time' in df.columns:
            df['Final_Time'] = pd.to_datetime(df['JST_Time'])
        elif 'UTC_Time' in df.columns:
            df['Final_Time'] = pd.to_datetime(df['UTC_Time']) + pd.Timedelta(hours=9)
        else:
            # どちらもない場合は、最初の列を時間として読み込む試行
            df['Final_Time'] = pd.to_datetime(df.iloc[:, 0])
        
        # 年・月を抽出（グラフのフィルター用）
        df['Year'] = df['Final_Time'].dt.year
        df['Month'] = df['Final_Time'].dt.month
        
        # 変化点のみを抽出（ログ用）
        change_mask = (
            (df['Type'] != df['Type'].shift()) | 
            (df['Definition'] != df['Definition'].shift()) | 
            (df['Authority'] != df['Authority'].shift())
        )
        df_logs = df[change_mask].copy()
        
        return df, df_logs
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_full, df_logs = load_data()

# ==========================================
# 3. 🎨 アプリ本体（グラフとログ）
# ==========================================
if not df_full.empty:
    st.title("🌌 宇宙の設計予定表 (Cosmic Timeline)")
    
    # 年選択
    years = sorted(df_full['Year'].unique())
    selected_year = st.selectbox("📅 年を選択してください", years, index=len(years)-1)
    
    # 選択された年のデータを抽出
    year_df_full = df_full[df_full['Year'] == selected_year]
    year_df_logs = df_logs[df_logs['Year'] == selected_year]

    # --- 統計エリア ---
    st.header(f"📊 {selected_year}年のエネルギー統計")
    col1, col2 = st.columns(2)
    
    color_type = {
        "Generator": "#FFB74D", "Manifesting Generator": "#E57373",
        "Manifestor": "#7986CB", "Projector": "#81C784", "Reflector": "#BA68C8"
    }

    with col1:
        st.subheader("タイプ分布")
        # 列名が count または Count に対応できるよう reset_index() の引数を調整
        type_counts = year_df_logs['Type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'count']
        fig_type = px.pie(type_counts, values='count', names='Type', hole=0.4, 
                          color='Type', color_discrete_map=color_type)
        st.plotly_chart(fig_type, use_container_width=True)

    with col2:
        st.subheader("定義型（Wide注目）")
        def_counts = year_df_logs['Definition'].value_counts().reset_index()
        def_counts.columns = ['Definition', 'count']
        def_colors = {d: "#42A5F5" if d == "Wide" else "#E0E0E0" for d in def_counts['Definition']}
        fig_def = px.bar(def_counts, x='Definition', y='count', color='Definition', color_discrete_map=def_colors)
        st.plotly_chart(fig_def, use_container_width=True)

    # --- ログエリア ---
    st.divider()
    st.header("📜 タイムラインログ (日本時間)")
    
    timeline_html = "<div style='line-height:1.6; background-color:#121212; color:#E0E0E0; padding:15px; border-radius:10px; height: 400px; overflow-y: scroll; font-family: monospace;'>"
    for _, row in year_df_logs.iterrows():
        time_str = row['Final_Time'].strftime("%m-%d %H:%M")
        t_color = color_type.get(row['Type'], "#FFF")
        d_style = "color:#42A5F5; font-weight:bold;" if row['Definition'] == 'Wide' else "color:#888;"
        
        line = f"<span style='color:gray;'>{time_str}</span> | <b style='color:{t_color};'>{str(row['Type'])[:3]}</b> | <span style='{d_style}'>{row['Definition']}</span> | {row['Authority']}<br>"
        timeline_html += line
    timeline_html += "</div>"
    st.markdown(timeline_html, unsafe_allow_html=True)
