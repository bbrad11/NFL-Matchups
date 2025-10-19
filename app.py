import streamlit as st
import nflreadpy as nfl
import pandas as pd

# Page config
st.set_page_config(page_title="NFL Matchup Analyzer", page_icon="🏈", layout="wide")

# Title
st.title("🏈 NFL Matchup & Defense Weakness Analyzer")
st.markdown("Track strength-vs-weakness matchups and defensive positional weaknesses")

# Sidebar controls
st.sidebar.header("Settings")
season = st.sidebar.selectbox("Season", [2024, 2023, 2022], index=0)
current_week = st.sidebar.slider("Current Week", 1, 18, 7)

# Cache data loading
@st.cache_data
def load_nfl_data(season):
    player_stats = nfl.load_player_stats([season])
    schedules = nfl.load_schedules([season])
    return player_stats.to_pandas(), schedules.to_pandas()

# Load data
with st.spinner('Loading NFL data...'):
    stats_df, schedule_df = load_nfl_data(season)

st.success(f"✅ Loaded {len(stats_df):,} player-game records")

# Position mapping
positions = {
    'QB': ['QB'],
    'RB': ['RB', 'FB'],
    'WR': ['WR'],
    'TE': ['TE']
}

# Function to analyze defense vs position
def analyze_defense_vs_position(stats_df, position_codes, stat_columns):
    pos_stats = stats_df[stats_df['position'].isin(position_codes)].copy()
    defense_stats = pos_stats.groupby('opponent_team').agg(stat_columns).reset_index()
    defense_stats.columns = ['Defense'] + [col[0] + '_' + col[1] for col in defense_stats.columns[1:]]
    return defense_stats

# ============================================================
# TAB 1: DEFENSE WEAKNESSES
# ============================================================

tab1, tab2, tab3 = st.tabs(["🛡️ Defense Weaknesses", "🔥 Matchup Analysis", "🏆 TD Leaders"])

with tab1:
    st.header("Defensive Positional Weaknesses")
    
    position_select = st.selectbox("Select Position", ["QB", "RB", "WR", "TE"])
    
    if position_select == "QB":
        qb_defense = analyze_defense_vs_position(
            stats_df, 
            positions['QB'],
            {
                'passing_yards': ['sum', 'mean'],
                'passing_tds': ['sum', 'mean'],
                'interceptions': ['sum'],
                'fantasy_points_ppr': ['sum', 'mean']
            }
        )
        qb_defense = qb_defense.sort_values('passing_tds_sum', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Worst Defenses vs QB (by TDs)")
            st.dataframe(qb_defense.head(10), use_container_width=True)
        with col2:
            st.subheader("Best Defenses vs QB (by TDs)")
            st.dataframe(qb_defense.tail(10).iloc[::-1], use_container_width=True)
        
        # Chart
        st.bar_chart(qb_defense.head(15).set_index('Defense')['passing_tds_sum'])
    
    elif position_select == "RB":
        rb_defense = analyze_defense_vs_position(
            stats_df,
            positions['RB'],
            {
                'rushing_yards': ['sum', 'mean'],
                'rushing_tds': ['sum', 'mean'],
                'receiving_tds': ['sum'],
                'fantasy_points_ppr': ['sum', 'mean']
            }
        )
        rb_defense['total_tds'] = rb_defense['rushing_tds_sum'] + rb_defense['receiving_tds_sum']
        rb_defense = rb_defense.sort_values('total_tds', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Worst Defenses vs RB")
            st.dataframe(rb_defense.head(10), use_container_width=True)
        with col2:
            st.subheader("Best Defenses vs RB")
            st.dataframe(rb_defense.tail(10).iloc[::-1], use_container_width=True)
        
        st.bar_chart(rb_defense.head(15).set_index('Defense')['total_tds'])
    
    elif position_select == "WR":
        wr_defense = analyze_defense_vs_position(
            stats_df,
            positions['WR'],
            {
                'receptions': ['sum', 'mean'],
                'receiving_yards': ['sum', 'mean'],
                'receiving_tds': ['sum', 'mean'],
                'fantasy_points_ppr': ['sum', 'mean']
            }
        )
        wr_defense = wr_defense.sort_values('receiving_tds_sum', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Worst Defenses vs WR")
            st.dataframe(wr_defense.head(10), use_container_width=True)
        with col2:
            st.subheader("Best Defenses vs WR")
            st.dataframe(wr_defense.tail(10).iloc[::-1], use_container_width=True)
        
        st.bar_chart(wr_defense.head(15).set_index('Defense')['receiving_tds_sum'])
    
    else:  # TE
        te_defense = analyze_defense_vs_position(
            stats_df,
            positions['TE'],
            {
                'receptions': ['sum', 'mean'],
                'receiving_yards': ['sum', 'mean'],
                'receiving_tds': ['sum', 'mean'],
                'fantasy_points_ppr': ['sum', 'mean']
            }
        )
        te_defense = te_defense.sort_values('receiving_tds_sum', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Worst Defenses vs TE")
            st.dataframe(te_defense.head(10), use_container_width=True)
        with col2:
            st.subheader("Best Defenses vs TE")
            st.dataframe(te_defense.tail(10).iloc[::-1], use_container_width=True)
        
        st.bar_chart(te_defense.head(15).set_index('Defense')['receiving_tds_sum'])

# ============================================================
# TAB 2: MATCHUP ANALYSIS
# ============================================================

with tab2:
    st.header(f"Week {current_week} Matchup Analysis")
    
    upcoming_games = schedule_df[
        (schedule_df['week'] == current_week) & 
        (schedule_df['game_type'] == 'REG')
    ].copy()
    
    st.subheader(f"📅 {len(upcoming_games)} Games This Week")
    
    # Recent form (last 3 weeks)
    recent_stats = stats_df[stats_df['week'] >= current_week - 3].copy()
    
    # Calculate defense rankings
    qb_defense = analyze_defense_vs_position(stats_df, positions['QB'], {'passing_tds': ['sum']})
    rb_defense = analyze_defense_vs_position(stats_df, positions['RB'], {'rushing_tds': ['sum'], 'receiving_tds': ['sum']})
    wr_defense = analyze_defense_vs_position(stats_df, positions['WR'], {'receiving_tds': ['sum']})
    te_defense = analyze_defense_vs_position(stats_df, positions['TE'], {'receiving_tds': ['sum']})
    
    qb_weak = qb_defense.sort_values('passing_tds_sum', ascending=False).head(10)['Defense'].tolist()
    rb_defense['total_tds'] = rb_defense['rushing_tds_sum'] + rb_defense['receiving_tds_sum']
    rb_weak = rb_defense.sort_values('total_tds', ascending=False).head(10)['Defense'].tolist()
    wr_weak = wr_defense.sort_values('receiving_tds_sum', ascending=False).head(10)['Defense'].tolist()
    te_weak = te_defense.sort_values('receiving_tds_sum', ascending=False).head(10)['Defense'].tolist()
    
    # Show matchups
    for _, game in upcoming_games.iterrows():
        with st.expander(f"{game['away_team']} @ {game['home_team']} - {game['gameday']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**{game['away_team']} Offense**")
                if game['home_team'] in qb_weak:
                    st.success(f"✅ QB favorable matchup (vs weak pass D)")
                if game['home_team'] in rb_weak:
                    st.success(f"✅ RB favorable matchup (vs weak run D)")
                if game['home_team'] in wr_weak:
                    st.success(f"✅ WR favorable matchup (vs weak pass D)")
                if game['home_team'] in te_weak:
                    st.success(f"✅ TE favorable matchup (vs weak TE D)")
            
            with col2:
                st.markdown(f"**{game['home_team']} Offense**")
                if game['away_team'] in qb_weak:
                    st.success(f"✅ QB favorable matchup (vs weak pass D)")
                if game['away_team'] in rb_weak:
                    st.success(f"✅ RB favorable matchup (vs weak run D)")
                if game['away_team'] in wr_weak:
                    st.success(f"✅ WR favorable matchup (vs weak pass D)")
                if game['away_team'] in te_weak:
                    st.success(f"✅ TE favorable matchup (vs weak TE D)")

# ============================================================
# TAB 3: TD LEADERS
# ============================================================

with tab3:
    st.header("🏆 Touchdown Leaders")
    
    def get_td_leaders(df, position_list, position_name):
        pos_df = df[df['position'].isin(position_list)].copy()
        
        if position_name == "QB":
            pos_df['total_tds'] = pos_df['passing_tds'].fillna(0) + pos_df['rushing_tds'].fillna(0)
        else:
            pos_df['total_tds'] = pos_df['rushing_tds'].fillna(0) + pos_df['receiving_tds'].fillna(0)
        
        leaders = pos_df.groupby('player_display_name').agg({
            'rushing_tds': 'sum',
            'receiving_tds': 'sum',
            'passing_tds': 'sum',
            'total_tds': 'sum',
            'recent_team': 'last',
        }).reset_index()
        
        if position_name == "QB":
            leaders = leaders.sort_values('passing_tds', ascending=False).head(15)
        else:
            leaders = leaders.sort_values('total_tds', ascending=False).head(15)
        
        return leaders
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 QB Leaders")
        qb_tds = get_td_leaders(stats_df, positions['QB'], "QB")
        st.dataframe(qb_tds[['player_display_name', 'recent_team', 'passing_tds', 'rushing_tds']], use_container_width=True)
        
        st.subheader("🏃 RB Leaders")
        rb_tds = get_td_leaders(stats_df, positions['RB'], "RB")
        st.dataframe(rb_tds[['player_display_name', 'recent_team', 'rushing_tds', 'receiving_tds', 'total_tds']], use_container_width=True)
    
    with col2:
        st.subheader("📡 WR Leaders")
        wr_tds = get_td_leaders(stats_df, positions['WR'], "WR")
        st.dataframe(wr_tds[['player_display_name', 'recent_team', 'receiving_tds', 'total_tds']], use_container_width=True)
        
        st.subheader("🎣 TE Leaders")
        te_tds = get_td_leaders(stats_df, positions['TE'], "TE")
        st.dataframe(te_tds[['player_display_name', 'recent_team', 'receiving_tds', 'total_tds']], use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Data source: nflverse via nflreadpy | Updated weekly during NFL season")
