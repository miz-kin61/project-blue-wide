# =====================================================================
# 🕐 HD 24時間分析 - 出生時刻不明者向けダッシュボード
# =====================================================================
 
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import calendar
 
# --- ページ設定 ---
st.set_page_config(page_title="HD 24時間分析", layout="wide", page_icon="🕐")
 
# --- 🔐 パスワード認証 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: 
        return True
    
    st.markdown("<h1 style='text-align: center; color: #00BFFF;'>🕐 HD 24時間分析</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>出生時刻不明者の可能性を24時間で可視化</p>", unsafe_allow_html=True)
    
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
 
# --- 🎨 カラーパレット ---
color_map = {
    "MG": "#E53935", "PG": "#FFB300", "P": "#43A047", 
    "M": "#3949AB", "R": "#9E9E9E", 
    "ワイド": "#00BFFF", "スプリット": "#B0BEC5", "シンプル": "#B0BEC5",
    "シングル": "#CFD8DC", "トリプル": "#90A4AE", "クアドルプル": "#78909C", "定義なし": "#ECEFF1",
    "感情": "#FFCDD2", "仙骨": "#F8BBD0", "脾臓": "#E1BEE7", 
    "エゴ": "#D1C4E9", "G": "#C5CAE9", "環境": "#B3E5FC", 
    "月（の周期）": "#B2DFDB", "権威なし": "#ECEFF1"
}
 
# --- データクリーニング関数 ---
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
    return '不明'
 
# --- データ読み込み ---
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
    
    # カラムの検出
    type_cols = [c for c in df.columns if 'type' in c.lower() or 'タイプ' in c]
    auth_cols = [c for c in df.columns if 'auth' in c.lower() or '権威' in c]
    def_cols = [c for c in df.columns if 'def' in c.lower() or '定義' in c]
    chan_cols = [c for c in df.columns if 'channel' in c.lower() or 'チャネル' in c]
    
    df['Type_Clean'] = df[type_cols[0] if type_cols else df.columns[1]].apply(clean_type)
    df['Auth_Clean'] = df[auth_cols[0] if auth_cols else df.columns[2]].apply(clean_auth)
    df['Def_Clean'] = df[def_cols[0] if def_cols else df.columns[3]].apply(clean_def)
    df['Channels'] = df[chan_cols[0]] if chan_cols else "データなし"
    
    # 日付・時刻情報
    df['Date'] = df['Datetime'].dt.date
    df['Year'] = df['Datetime'].dt.year
    df['Month'] = df['Datetime'].dt.month
    df['Day'] = df['Datetime'].dt.day
    df['Hour'] = df['Datetime'].dt.hour
    df['Minute'] = df['Datetime'].dt.minute
    df['Time'] = df['Datetime'].dt.time
    
    return df
 
df = load_data()
 
# ==========================================
# 🎯 日付選択UI
# ==========================================
st.title("🕐 HD 24時間分析 - 出生時刻不明者向け")
st.markdown("**その日の0:00～23:59の間に、どのようなパターンが何％の確率で現れるかを可視化します**")
 
st.divider()
 
# 利用可能な範囲
min_date = df['Date'].min()
max_date = df['Date'].max()
 
# 年選択
col1, col2, col3 = st.columns(3)
with col1:
    available_years = sorted(df['Year'].unique())
    selected_year = st.selectbox(
        "📅 年", 
        available_years, 
        index=available_years.index(2026) if 2026 in available_years else len(available_years)-1
    )
 
# 月選択（1-12全表示）
with col2:
    selected_month = st.selectbox("📅 月", list(range(1, 13)))
 
# 日選択（月に応じた日数を全表示）
with col3:
    # その年月の最大日数を取得
    max_day = calendar.monthrange(selected_year, selected_month)[1]
    selected_day = st.selectbox("📅 日", list(range(1, max_day + 1)))
 
selected_date = date(selected_year, selected_month, selected_day)
 
st.divider()
 
# ==========================================
# 📊 24時間データ生成
# ==========================================
 
def generate_24h_data(target_date, df):
    """指定された日付の0:00～23:59までのデータを生成（補完含む）"""
    
    # 対象日のデータを抽出
    day_data = df[df['Date'] == target_date].copy()
    
    if day_data.empty:
        st.warning(f"⚠️ {target_date} のデータが見つかりません。")
        return pd.DataFrame()
    
    # 24時間分のタイムスロットを作成（1分刻み）
    start_dt = datetime.combine(target_date, datetime.min.time())
    time_slots = []
    
    for minute in range(24 * 60):  # 1440分
        current_time = start_dt + timedelta(minutes=minute)
        
        # その時刻に最も近いデータを探す
        day_data['time_diff'] = abs((day_data['Datetime'] - current_time).dt.total_seconds())
        closest = day_data.loc[day_data['time_diff'].idxmin()]
        
        time_slots.append({
            'Datetime': current_time,
            'Hour': current_time.hour,
            'Minute': current_time.minute,
            'Type': closest['Type_Clean'],
            'Auth': closest['Auth_Clean'],
            'Def': closest['Def_Clean'],
            'Channels': closest['Channels']
        })
    
    return pd.DataFrame(time_slots)
 
# 24時間データ生成
with st.spinner("24時間データを生成中..."):
    full_24h_data = generate_24h_data(selected_date, df)
 
if full_24h_data.empty:
    st.stop()
 
# ==========================================
# 📈 パターン集計
# ==========================================
 
def calculate_pattern_stats(data):
    """パターンごとの統計を計算"""
    total_minutes = len(data)
    
    # タイプ別
    type_stats = data['Type'].value_counts().to_dict()
    type_pct = {k: (v/total_minutes)*100 for k, v in type_stats.items()}
    
    # 権威別
    auth_stats = data['Auth'].value_counts().to_dict()
    auth_pct = {k: (v/total_minutes)*100 for k, v in auth_stats.items()}
    
    # 定義型別
    def_stats = data['Def'].value_counts().to_dict()
    def_pct = {k: (v/total_minutes)*100 for k, v in def_stats.items()}
    
    # 組み合わせパターン
    data['Pattern'] = data['Type'] + ' + ' + data['Auth'] + ' + ' + data['Def']
    pattern_stats = data['Pattern'].value_counts().to_dict()
    pattern_pct = {k: (v/total_minutes)*100 for k, v in pattern_stats.items()}
    
    return {
        'type': {'count': type_stats, 'pct': type_pct},
        'auth': {'count': auth_stats, 'pct': auth_pct},
        'def': {'count': def_stats, 'pct': def_pct},
        'pattern': {'count': pattern_stats, 'pct': pattern_pct}
    }
 
stats = calculate_pattern_stats(full_24h_data)
 
# ==========================================
# 🎯 サマリー表示
# ==========================================
st.header(f"📊 {selected_date.strftime('%Y年%m月%d日')} の可能性サマリー")
 
# トップ3パターンを表示
top_patterns = sorted(stats['pattern']['pct'].items(), key=lambda x: x[1], reverse=True)[:3]
 
cols = st.columns(3)
for i, (pattern, pct) in enumerate(top_patterns):
    with cols[i]:
        st.metric(
            label=f"第{i+1}位の可能性",
            value=f"{pct:.1f}%",
            delta=pattern
        )
 
st.divider()
 
# ==========================================
# 📊 詳細統計
# ==========================================
st.subheader("📈 要素別の出現割合")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    st.write("**🎯 タイプ別**")
    for t, pct in sorted(stats['type']['pct'].items(), key=lambda x: x[1], reverse=True):
        minutes = stats['type']['count'][t]
        st.write(f"**{t}**: {pct:.1f}% ({minutes}分)")
 
with col2:
    st.write("**⚖️ 権威別**")
    for a, pct in sorted(stats['auth']['pct'].items(), key=lambda x: x[1], reverse=True):
        minutes = stats['auth']['count'][a]
        st.write(f"**{a}**: {pct:.1f}% ({minutes}分)")
 
with col3:
    st.write("**🔷 定義型別**")
    for d, pct in sorted(stats['def']['pct'].items(), key=lambda x: x[1], reverse=True):
        minutes = stats['def']['count'][d]
        st.write(f"**{d}**: {pct:.1f}% ({minutes}分)")
 
st.divider()
 
# ==========================================
# 🕐 24時間タイムライン可視化
# ==========================================
st.header(f"🕐 24時間タイムライン")
 
# タイプ変化の時系列グラフ
def create_timeline_blocks(data, category):
    """カテゴリごとの時間帯ブロックを作成"""
    blocks = []
    current_value = None
    start_time = None
    
    for idx, row in data.iterrows():
        value = row[category]
        time = row['Datetime']
        
        if current_value != value:
            # 前のブロックを保存
            if current_value is not None:
                blocks.append({
                    'Value': current_value,
                    'Start': start_time,
                    'End': time,
                    'Duration': (time - start_time).total_seconds() / 60
                })
            
            # 新しいブロック開始
            current_value = value
            start_time = time
    
    # 最後のブロック
    if current_value is not None:
        end_time = datetime.combine(selected_date, datetime.max.time().replace(microsecond=0))
        blocks.append({
            'Value': current_value,
            'Start': start_time,
            'End': end_time,
            'Duration': (end_time - start_time).total_seconds() / 60
        })
    
    return pd.DataFrame(blocks)
 
# タイプのタイムライン
st.subheader("🎯 タイプの時系列変化")
type_blocks = create_timeline_blocks(full_24h_data, 'Type')
 
fig_type = go.Figure()
for idx, block in type_blocks.iterrows():
    fig_type.add_trace(go.Bar(
        name=block['Value'],
        x=[block['Duration']],
        y=['タイプ'],
        orientation='h',
        marker=dict(color=color_map.get(block['Value'], '#CCCCCC')),
        text=f"{block['Value']}<br>{block['Start'].strftime('%H:%M')}～{block['End'].strftime('%H:%M')}<br>{block['Duration']:.0f}分 ({block['Duration']/1440*100:.1f}%)",
        textposition='inside',
        hovertemplate=f"{block['Value']}<br>{block['Start'].strftime('%H:%M')}～{block['End'].strftime('%H:%M')}<br>{block['Duration']:.0f}分 ({block['Duration']/1440*100:.1f}%)<extra></extra>",
        showlegend=False,
        base=sum(type_blocks.loc[:idx-1, 'Duration']) if idx > 0 else 0
    ))
 
fig_type.update_layout(
    barmode='stack',
    height=150,
    xaxis=dict(title='時間（分）', range=[0, 1440]),
    yaxis=dict(title=''),
    margin=dict(l=10, r=10, t=10, b=10)
)
st.plotly_chart(fig_type, use_container_width=True)
 
# 権威のタイムライン
st.subheader("⚖️ 権威の時系列変化")
auth_blocks = create_timeline_blocks(full_24h_data, 'Auth')
 
fig_auth = go.Figure()
for idx, block in auth_blocks.iterrows():
    fig_auth.add_trace(go.Bar(
        name=block['Value'],
        x=[block['Duration']],
        y=['権威'],
        orientation='h',
        marker=dict(color=color_map.get(block['Value'], '#CCCCCC')),
        text=f"{block['Value']}<br>{block['Start'].strftime('%H:%M')}～{block['End'].strftime('%H:%M')}<br>{block['Duration']:.0f}分 ({block['Duration']/1440*100:.1f}%)",
        textposition='inside',
        hovertemplate=f"{block['Value']}<br>{block['Start'].strftime('%H:%M')}～{block['End'].strftime('%H:%M')}<br>{block['Duration']:.0f}分 ({block['Duration']/1440*100:.1f}%)<extra></extra>",
        showlegend=False,
        base=sum(auth_blocks.loc[:idx-1, 'Duration']) if idx > 0 else 0
    ))
 
fig_auth.update_layout(
    barmode='stack',
    height=150,
    xaxis=dict(title='時間（分）', range=[0, 1440]),
    yaxis=dict(title=''),
    margin=dict(l=10, r=10, t=10, b=10)
)
st.plotly_chart(fig_auth, use_container_width=True)
 
# 定義型のタイムライン
st.subheader("🔷 定義型の時系列変化")
def_blocks = create_timeline_blocks(full_24h_data, 'Def')
 
fig_def = go.Figure()
for idx, block in def_blocks.iterrows():
    fig_def.add_trace(go.Bar(
        name=block['Value'],
        x=[block['Duration']],
        y=['定義型'],
        orientation='h',
        marker=dict(color=color_map.get(block['Value'], '#CCCCCC')),
        text=f"{block['Value']}<br>{block['Start'].strftime('%H:%M')}～{block['End'].strftime('%H:%M')}<br>{block['Duration']:.0f}分 ({block['Duration']/1440*100:.1f}%)",
        textposition='inside',
        hovertemplate=f"{block['Value']}<br>{block['Start'].strftime('%H:%M')}～{block['End'].strftime('%H:%M')}<br>{block['Duration']:.0f}分 ({block['Duration']/1440*100:.1f}%)<extra></extra>",
        showlegend=False,
        base=sum(def_blocks.loc[:idx-1, 'Duration']) if idx > 0 else 0
    ))
 
fig_def.update_layout(
    barmode='stack',
    height=150,
    xaxis=dict(title='時間（分）', range=[0, 1440]),
    yaxis=dict(title=''),
    margin=dict(l=10, r=10, t=10, b=10)
)
st.plotly_chart(fig_def, use_container_width=True)
 
st.divider()
 
# ==========================================
# 📋 時間帯別詳細テーブル
# ==========================================
st.header("📋 時間帯別詳細情報")
 
# タブで切り替え
tab1, tab2, tab3 = st.tabs(["🎯 タイプ別", "⚖️ 権威別", "🔷 定義型別"])
 
with tab1:
    type_blocks['開始時刻'] = type_blocks['Start'].dt.strftime('%H:%M')
    type_blocks['終了時刻'] = type_blocks['End'].dt.strftime('%H:%M')
    type_blocks['継続時間（分）'] = type_blocks['Duration'].astype(int)
    type_blocks['割合（%）'] = (type_blocks['Duration'] / 1440 * 100).round(1)
    
    display_type = type_blocks[['Value', '開始時刻', '終了時刻', '継続時間（分）', '割合（%）']].copy()
    display_type.columns = ['タイプ', '開始時刻', '終了時刻', '継続時間（分）', '割合（%）']
    st.dataframe(display_type, hide_index=True, use_container_width=True)
 
with tab2:
    auth_blocks['開始時刻'] = auth_blocks['Start'].dt.strftime('%H:%M')
    auth_blocks['終了時刻'] = auth_blocks['End'].dt.strftime('%H:%M')
    auth_blocks['継続時間（分）'] = auth_blocks['Duration'].astype(int)
    auth_blocks['割合（%）'] = (auth_blocks['Duration'] / 1440 * 100).round(1)
    
    display_auth = auth_blocks[['Value', '開始時刻', '終了時刻', '継続時間（分）', '割合（%）']].copy()
    display_auth.columns = ['権威', '開始時刻', '終了時刻', '継続時間（分）', '割合（%）']
    st.dataframe(display_auth, hide_index=True, use_container_width=True)
 
with tab3:
    def_blocks['開始時刻'] = def_blocks['Start'].dt.strftime('%H:%M')
    def_blocks['終了時刻'] = def_blocks['End'].dt.strftime('%H:%M')
    def_blocks['継続時間（分）'] = def_blocks['Duration'].astype(int)
    def_blocks['割合（%）'] = (def_blocks['Duration'] / 1440 * 100).round(1)
    
    display_def = def_blocks[['Value', '開始時刻', '終了時刻', '継続時間（分）', '割合（%）']].copy()
    display_def.columns = ['定義型', '開始時刻', '終了時刻', '継続時間（分）', '割合（%）']
    st.dataframe(display_def, hide_index=True, use_container_width=True)
 
st.divider()
 
# ==========================================
# 📥 詳細データダウンロード
# ==========================================
st.subheader("📥 詳細データダウンロード")
 
# 1分単位の全データ
csv_full = full_24h_data.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label=f"📅 {selected_date.strftime('%Y%m%d')} の1分単位データ (CSV)",
    data=csv_full,
    file_name=f"HD_24H_{selected_date.strftime('%Y%m%d')}_full.csv",
    mime='text/csv'
)
 
# サマリーレポート
summary_text = f"""
# {selected_date.strftime('%Y年%m月%d日')} HD 24時間分析レポート
 
## トップ3パターン
"""
 
for i, (pattern, pct) in enumerate(top_patterns, 1):
    summary_text += f"{i}. {pattern}: {pct:.1f}%\n"
 
summary_text += "\n## タイプ別統計\n"
for t, pct in sorted(stats['type']['pct'].items(), key=lambda x: x[1], reverse=True):
    minutes = stats['type']['count'][t]
    summary_text += f"- {t}: {pct:.1f}% ({minutes}分)\n"
 
summary_text += "\n## 権威別統計\n"
for a, pct in sorted(stats['auth']['pct'].items(), key=lambda x: x[1], reverse=True):
    minutes = stats['auth']['count'][a]
    summary_text += f"- {a}: {pct:.1f}% ({minutes}分)\n"
 
summary_text += "\n## 定義型別統計\n"
for d, pct in sorted(stats['def']['pct'].items(), key=lambda x: x[1], reverse=True):
    minutes = stats['def']['count'][d]
    summary_text += f"- {d}: {pct:.1f}% ({minutes}分)\n"
 
st.download_button(
    label=f"📄 {selected_date.strftime('%Y%m%d')} のサマリーレポート (TXT)",
    data=summary_text.encode('utf-8'),
    file_name=f"HD_24H_{selected_date.strftime('%Y%m%d')}_summary.txt",
    mime='text/plain'
