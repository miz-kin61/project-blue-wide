import streamlit as st
import pandas as pd
import plotly.express as px

# --- ページ設定 ---
st.set_page_config(page_title="Cosmic Timeline", layout="wide", page_icon="🌌")
st.title("🌌 宇宙の設計予定表 (Cosmic Timeline)")
st.markdown("90年間のエネルギー変化と「Wide」の軌跡を読み解く私専用辞書")

# --- データの読み込み ---
@st.cache_data
def load_data():
    try:
        # みずきさんが作成したスペシャル辞書を読み込む
        df = pd.read_csv('HD_Special_Dictionary.csv')
        df['JST_Time'] = pd.to_datetime(df['JST_Time'])
        df['Year'] = df['JST_Time'].dt.year
        df['Month'] = df['JST_Time'].dt.month
        return df
    except FileNotFoundError:
        st.error("⚠️ `HD_Special_Dictionary.csv` が見つかりません。統合コードを実行してファイルを作成してください。")
        return pd.DataFrame() # 空のデータフレームを返す

df = load_data()

if not df.empty:
    # --- 1. 年選択 ---
    years = sorted(df['Year'].unique())
    selected_year = st.selectbox("📅 年を選択してください", years, index=len(years)-1)
    
    # 選択された年のデータを抽出
    year_df = df[df['Year'] == selected_year]
    total_count = len(year_df)

    # --- カラーパレットの定義（みずきさん指定！） ---
    color_type = {
        "Generator": "#FFB74D",             # 黄色に近いオレンジ
        "Manifesting Generator": "#E57373", # 目にやさしい赤
        "Manifestor": "#7986CB",            # 目に優しい紺色
        "Projector": "#81C784",             # 目に優しい深めの緑色
        "Reflector": "#BA68C8"              # 紫
    }

    color_auth = {
        "SolarPlexus": "#BCAAA4",  # 少し明るめ茶色
        "Sacral": "#E57373",       # MGと同じ赤
        "Splenic": "#C0CA33",      # 黄色め茶色（オリーブ系）
        "Heart": "#E53935",        # 赤（エゴ）独立
        "G": "#FFF176",            # やさしい黄色 独立
        "None": "#BDBDBD"          # メンタル・リフレクター（灰色）
    }

    # --- 2. 統計ダッシュボード ---
    st.header(f"📊 {selected_year}年のエネルギー統計 (総変化数: {total_count}回)")
    col1, col2, col3 = st.columns(3)

    # ❶ タイプ発生率 (円グラフ)
    with col1:
        st.subheader("タイプ分布")
        type_counts = year_df['Type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']
        fig_type = px.pie(type_counts, values='Count', names='Type', hole=0.4, 
                          color='Type', color_discrete_map=color_type)
        fig_type.update_layout(margin=dict(t=20, b=20, l=0, r=0), showlegend=True)
        st.plotly_chart(fig_type, use_container_width=True)

    # ❷ 定義型分布 (スタック棒グラフ ＋ Wide単体表示)
    with col2:
        st.subheader("定義型分布")
        
        # グラフ用にデータを整形（SimpleとWideを「Split」という親カテゴリにまとめる）
        def map_base_def(d):
            if d in ['Simple', 'Wide']: return 'Split'
            return d
        
        def map_sub_def(d):
            if d == 'Wide': return 'Wide'
            return 'Normal' # それ以外（Single, Simple, Triple, Quad）はNormal扱い

        year_df['Base_Def'] = year_df['Definition'].apply(map_base_def)
        year_df['Sub_Def'] = year_df['Definition'].apply(map_sub_def)
        
        def_counts = year_df.groupby(['Base_Def', 'Sub_Def']).size().reset_index(name='Count')
        
        # 色設定（通常は薄い灰色、Wideは青！）
        color_def = {"Normal": "#E0E0E0", "Wide": "#42A5F5"}
        
        fig_def = px.bar(def_counts, x='Base_Def', y='Count', color='Sub_Def',
                         color_discrete_map=color_def,
                         category_orders={"Base_Def": ["Single", "Split", "Triple", "Quad"]})
        fig_def.update_layout(showlegend=False, margin=dict(t=20, b=20, l=0, r=0), xaxis_title="")
        st.plotly_chart(fig_def, use_container_width=True)

        # ★ エモいポイント：Wide単体の発生率を下に表示 ★
        wide_count = len(year_df[year_df['Definition'] == 'Wide'])
        wide_percent = (wide_count / total_count) * 100 if total_count > 0 else 0
        st.markdown(f"<div style='text-align: center; font-size: 1.2em; font-weight: bold; color: #42A5F5;'>"
                    f"🔷 ワイドスプリット単体：{wide_percent:.1f}％ ({wide_count}回)</div>", unsafe_allow_html=True)

    # ❸ 権威分布 (棒グラフ)
    with col3:
        st.subheader("権威分布")
        auth_counts = year_df['Authority'].value_counts().reset_index()
        auth_counts.columns = ['Authority', 'Count']
        fig_auth = px.bar(auth_counts, x='Authority', y='Count', color='Authority',
                          color_discrete_map=color_auth)
        fig_auth.update_layout(showlegend=False, margin=dict(t=20, b=20, l=0, r=0), xaxis_title="")
        st.plotly_chart(fig_auth, use_container_width=True)

    # --- 3. メインコンテンツ：時の流れ羅列 (ログ) ---
    st.divider()
    st.header(f"📜 {selected_year}年 タイムラインログ")

    # 月別ジャンプボタン
    month_cols = st.columns(12)
    selected_month = st.session_state.get('selected_month', 1)

    for i, col in enumerate(month_cols):
        with col:
            if st.button(f"{i+1}月", key=f"btn_{i+1}"):
                selected_month = i + 1
                st.session_state['selected_month'] = selected_month

    st.subheader(f"🔽 {selected_month}月の変化履歴")
    month_data = year_df[year_df['Month'] == selected_month]

    # 漆黒のログ表示エリアを構築
    timeline_html = "<div style='line-height:1.8; font-family:monospace; background-color:#121212; color:#E0E0E0; padding:20px; border-radius:10px; height: 500px; overflow-y: scroll;'>"
    
    for index, row in month_data.iterrows():
        time_str = row['JST_Time'].strftime("%m-%d %H:%M")
        
        # タイプの短縮表示と色付け
        type_str = row['Type']
        type_color = color_type.get(type_str, "#FFFFFF")
        if type_str == "Manifesting Generator": short_type = "MG "
        elif type_str == "Generator": short_type = "GEN"
        elif type_str == "Projector": short_type = "PRO"
        elif type_str == "Manifestor": short_type = "MAN"
        else: short_type = "REF"
        
        # 定義型（Wideの太字・青文字化）
        def_str = row['Definition']
        if def_str == 'Wide':
            def_html = f"<strong style='color:#42A5F5;'>Wide  </strong>"
        else:
            # 桁を揃えるためにスペースでパディング
            def_html = f"{def_str:<6}"
            
        auth_str = row['Authority']
        auth_color = color_auth.get(auth_str, "#FFFFFF")
        
        # 原因（Cause）がある場合は表示
        cause_str = row.get('Cause', '')
        
        # 1行のHTMLフォーマット
        line = (f"<span style='color:gray;'>{time_str}</span> | "
                f"<strong style='color:{type_color};'>{short_type}</strong> | "
                f"{def_html} | "
                f"<span style='color:{auth_color};'>{auth_str:<11}</span> | "
                f"<span style='color:#888888; font-size:0.9em;'>{cause_str}</span><br>")
        timeline_html += line

    timeline_html += "</div>"
    st.markdown(timeline_html, unsafe_allow_html=True)