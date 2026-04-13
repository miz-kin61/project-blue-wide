import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- ページ設定 ---
st.set_page_config(page_title="Project Blue Wide", layout="wide", page_icon="🌌")

# --- 🔐 秘密基地の鍵（パスワード） ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.markdown("<h1 style='text-align: center; color: #00BFFF;'>🌌 Project Blue Wide</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>- Private Cosmic Archive -</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Access Code", type="password")
        if st.button("System Login"):
            if pwd == "blue-wide-90":  # 🔑 ここを好きなパスワードに変更してください！
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Access Denied.")
    return False

if not check_password():
    st.stop()

# --- 🛠️ 翻訳辞書（データクリーニング用） ---
# タイプの統一
def clean_type(t):
    t_str = str(t).lower()
    if 'manifesting' in t_str or 'mg' in t_str: return 'MG'
    if 'generator' in t_str or 'pg' in t_str: return 'PG'
    if 'projector' in t_str or 'p' in t_str: return 'P'
    if 'manifestor' in t_str or 'm' in t_str: return 'M'
    if 'reflector' in t_str or 'r' in t_str: return 'R'
    return '不明'

# 権威の統一（spleen を追加！）
def clean_auth(a):
    a_str = str(a).lower() # ←★ここで大文字を小文字に変換しています！
    if 'solar' in a_str or 'emotional' in a_str or '感情' in a_str: return '感情'
    if 'sacral' in a_str or '仙骨' in a_str: return '仙骨'
    if 'splenic' in a_str or 'spleen' in a_str or '脾臓' in a_str: return '脾臓' # ←spleen追加
    if 'heart' in a_str or 'ego' in a_str or 'エゴ' in a_str: return 'エゴ'
    if 'g' in a_str or 'self' in a_str: return 'G'
    if 'mental' in a_str or 'environment' in a_str or '環境' in a_str: return '環境'
    if 'none' in a_str or 'lunar' in a_str or '月' in a_str: return '月'
    return '不明'

# 定義型の統一（Wideは青色強調のために独立させます！）
def clean_def(d):
    d_str = str(d).lower()
    if 'wide' in d_str: return 'ワイド' # ★別格として抽出
    if 'single' in d_str: return 'シングル'
    if 'simple' in d_str or 'split' in d_str: return 'スプリット'
    if 'triple' in d_str: return 'トリプル'
    if 'quad' in d_str: return 'クアドルプル'
    return '不明'


# --- データの読み込みと整形 ---
@st.cache_data
def load_and_clean_data():
    try:
        df = pd.read_csv('HD_Special_Dictionary.csv')
        
        # 時間列を見つけてDatetime型にする（JST_Timeか日時の列を自動検索）
        time_col = [c for c in df.columns if 'time' in c.lower() or '日時' in c][0]
        df['Datetime'] = pd.to_datetime(df[time_col])
        
        # 列名が違っても動くように、文字を含んでいる列を探す
        type_col = [c for c in df.columns if 'type' in c.lower() or 'タイプ' in c][0]
        auth_col = [c for c in df.columns if 'auth' in c.lower() or '権威' in c][0]
        def_col = [c for c in df.columns if 'def' in c.lower() or '定義' in c][0]
        
        # 翻訳辞書を適用
        df['Type_Clean'] = df[type_col].apply(clean_type)
        df['Auth_Clean'] = df[auth_col].apply(clean_auth)
        df['Def_Clean'] = df[def_col].apply(clean_def)
        
        # カレンダー用に年月日の列を作成
        df['Year'] = df['Datetime'].dt.year
        df['Month'] = df['Datetime'].dt.month
        df['Day'] = df['Datetime'].dt.day
        
        return df
    except Exception as e:
        st.error(f"データの読み込みに失敗しました。列名を確認してください。\n詳細: {e}")
        return pd.DataFrame()

df = load_and_clean_data()

if not df.empty:
    st.title("🌌 Project Blue Wide - Analysis Cockpit")
    
    # 年選択
    years = sorted(df['Year'].unique())
    selected_year = st.selectbox("📅 観測年 (Year)", years, index=len(years)-1)
    year_df = df[df['Year'] == selected_year]

    # --- 🎨 カラーパレット設定（みずきさん指定の最強配色） ---
    color_map = {
        "MG": "#E53935", # 赤
        "PG": "#FFB300", # 黄色に近いオレンジ
        "P": "#43A047",  # 緑
        "M": "#3949AB",  # 紫に近い青色（ロイヤルブルー）
        "R": "#9E9E9E",  # 灰色
        "ワイド": "#00BFFF", # ★際立つ青（アジュール）
        "スプリット": "#B0BEC5", "シングル": "#CFD8DC", "トリプル": "#90A4AE", "クアドルプル": "#78909C",
        "感情": "#FFCDD2", "仙骨": "#F8BBD0", "脾臓": "#E1BEE7", "エゴ": "#D1C4E9", "G": "#C5CAE9", "環境": "#B3E5FC", "月": "#B2DFDB"
    }
    # タイプの表示順序（時計回り）
    type_order = ["MG", "PG", "P", "M", "R"]

# --- 📊 1. 上段：2重円グラフ（サンバースト） ---
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("タイプ × 権威")
        sb_auth = year_df.groupby(['Type_Clean', 'Auth_Clean']).size().reset_index(name='Count')
        
        # ★エラー回避：オプションを使わず、データ自体をMG→PG→Pの順に並び替える作戦
        sb_auth['Type_Clean'] = pd.Categorical(sb_auth['Type_Clean'], categories=type_order, ordered=True)
        sb_auth = sb_auth.sort_values('Type_Clean')
        
        try:
            # category_orders を削除しました！
            fig_auth = px.sunburst(sb_auth, path=['Type_Clean', 'Auth_Clean'], values='Count', color='Type_Clean',
                                   color_discrete_map=color_map)
            fig_auth.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_auth, use_container_width=True)
        except Exception as e:
            st.error(f"エラーの正体（グラフ1）: {e}") # もしまたエラーが出ても、画面に直接表示させます！

    with col2:
        st.subheader("タイプ × 定義型")
        sb_def = year_df.groupby(['Type_Clean', 'Def_Clean']).size().reset_index(name='Count')
        
        # ★こちらも同様にデータを並び替え
        sb_def['Type_Clean'] = pd.Categorical(sb_def['Type_Clean'], categories=type_order, ordered=True)
        sb_def = sb_def.sort_values('Type_Clean')
        
        try:
            # category_orders を削除しました！
            fig_def = px.sunburst(sb_def, path=['Type_Clean', 'Def_Clean'], values='Count', color='Def_Clean',
                                  color_discrete_map=color_map)
            fig_def.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_def, use_container_width=True)
        except Exception as e:
            st.error(f"エラーの正体（グラフ2）: {e}")

    # --- 📅 2. 中段：特異日カレンダー（基礎枠組み） ---
    st.divider()
    st.subheader(f"🗓️ {selected_year}年 特異日マトリクス (Wide Heatmap)")
    st.markdown("※ カレンダーの完全連動と天体トリガー表記はフェーズ2で実装します。まずはワイドの発生日を青く点灯させます。")
    
    # その日に「ワイド」が発生した回数をカウントするピボットテーブル
    wide_df = year_df[year_df['Def_Clean'] == 'ワイド']
    calendar_data = wide_df.groupby(['Month', 'Day']).size().unstack(fill_value=0)
    
    # 12ヶ月×31日の空枠を作ってマージする（2月30日などはNaNになる）
    full_months = pd.Index(range(1, 13), name="Month")
    full_days = pd.Index(range(1, 32), name="Day")
    calendar_matrix = calendar_data.reindex(index=full_months, columns=full_days).fillna(0)
    
    # Plotlyでヒートマップを描画（青色系グラデーション）
    fig_cal = px.imshow(calendar_matrix, 
                        labels=dict(x="日 (Day)", y="月 (Month)", color="Wide回数"),
                        x=full_days, y=full_months,
                        color_continuous_scale=[[0, '#1E1E1E'], [1, '#00BFFF']], # 黒から際立つ青へ
                        aspect="auto")
    fig_cal.update_yaxes(autorange="reversed", dtick=1) # 1月を上に
    fig_cal.update_xaxes(dtick=1)
    st.plotly_chart(fig_cal, use_container_width=True)

    # --- 📝 3. 下段：整形されたタイムラインログ ---
    st.divider()
    st.subheader("📜 タイムライン・ログ")
    
    # 表示用の綺麗なデータフレームを作成
    log_df = pd.DataFrame()
    log_df['日時'] = year_df['Datetime'].dt.strftime('%m/%d %H:%M')
    log_df['Type'] = year_df['Type_Clean']
    log_df['定義型'] = year_df['Def_Clean']
    log_df['権威'] = year_df['Auth_Clean']
    
    # Cause（原因）列があれば追加
    cause_col = [c for c in df.columns if 'cause' in c.lower() or '原因' in c]
    if cause_col:
        log_df['トリガー'] = year_df[cause_col[0]]
    else:
        log_df['トリガー'] = "算出準備中"

    # Streamlitの機能で、エクセルのように綺麗な表を表示（縦線ピシッと揃います）
    st.dataframe(log_df, use_container_width=True, height=400)
