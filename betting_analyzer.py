import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

class BettingAnalyzer:
    """
    Betting analysis engine for NFL and NBA
    Provides odds, predictions, and value bets
    """
    
    def __init__(self, sport="NFL"):
        self.sport = sport
        
    def calculate_implied_probability(self, american_odds):
        """
        Convert American odds to implied probability
        
        Args:
            american_odds: American odds format (e.g., -110, +150)
        
        Returns:
            Implied probability as percentage
        """
        if american_odds < 0:
            # Favorite
            implied_prob = (-american_odds) / (-american_odds + 100)
        else:
            # Underdog
            implied_prob = 100 / (american_odds + 100)
        
        return implied_prob * 100
    
    def calculate_ev(self, win_probability, american_odds, stake=100):
        """
        Calculate Expected Value of a bet
        
        Args:
            win_probability: Your estimated win probability (0-1)
            american_odds: American odds
            stake: Bet amount
        
        Returns:
            Expected value in dollars
        """
        if american_odds < 0:
            potential_profit = stake * (100 / abs(american_odds))
        else:
            potential_profit = stake * (american_odds / 100)
        
        ev = (win_probability * potential_profit) - ((1 - win_probability) * stake)
        return ev
    
    def find_value_bets(self, predictions_df, odds_df, threshold=5):
        """
        Find bets where your prediction differs significantly from odds
        
        Args:
            predictions_df: DataFrame with your win probabilities
            odds_df: DataFrame with betting odds
            threshold: Minimum edge percentage to consider
        
        Returns:
            DataFrame of value bets
        """
        # Merge predictions with odds
        merged = pd.merge(predictions_df, odds_df, on=['game_id', 'team'])
        
        # Calculate implied probability from odds
        merged['implied_prob'] = merged['odds'].apply(self.calculate_implied_probability)
        
        # Calculate edge
        merged['edge'] = merged['predicted_prob'] - merged['implied_prob']
        
        # Filter for value bets
        value_bets = merged[merged['edge'] >= threshold]
        
        # Calculate EV
        value_bets['ev'] = value_bets.apply(
            lambda row: self.calculate_ev(
                row['predicted_prob'] / 100,
                row['odds']
            ),
            axis=1
        )
        
        return value_bets.sort_values('ev', ascending=False)
    
    def kelly_criterion(self, win_prob, american_odds, bankroll, kelly_fraction=0.25):
        """
        Calculate optimal bet size using Kelly Criterion
        
        Args:
            win_prob: Win probability (0-1)
            american_odds: American odds
            bankroll: Total bankroll
            kelly_fraction: Fraction of Kelly to use (0.25 = quarter Kelly)
        
        Returns:
            Recommended bet size
        """
        if american_odds < 0:
            decimal_odds = 1 + (100 / abs(american_odds))
        else:
            decimal_odds = 1 + (american_odds / 100)
        
        # Kelly formula: (bp - q) / b
        # b = decimal odds - 1, p = win prob, q = 1 - p
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p
        
        kelly_percentage = (b * p - q) / b
        
        # Apply Kelly fraction (conservative approach)
        kelly_percentage = max(0, kelly_percentage * kelly_fraction)
        
        return bankroll * kelly_percentage
    
    def prop_bet_analysis(self, player_stats, prop_line, stat_type='points'):
        """
        Analyze player prop bets
        
        Args:
            player_stats: DataFrame with player's historical stats
            prop_line: The betting line (e.g., 25.5 points)
            stat_type: Stat being bet on
        
        Returns:
            Analysis dict with probabilities and recommendation
        """
        if player_stats.empty:
            return None
        
        # Calculate how often player goes over the line
        over_count = (player_stats[stat_type] > prop_line).sum()
        total_games = len(player_stats)
        over_prob = over_count / total_games if total_games > 0 else 0
        
        # Calculate average and recent form
        avg_stat = player_stats[stat_type].mean()
        recent_avg = player_stats[stat_type].tail(5).mean()
        
        # Calculate variance/consistency
        std_dev = player_stats[stat_type].std()
        consistency_score = 100 - (std_dev / avg_stat * 100) if avg_stat > 0 else 0
        
        return {
            'over_probability': over_prob * 100,
            'under_probability': (1 - over_prob) * 100,
            'season_average': avg_stat,
            'recent_average': recent_avg,
            'consistency_score': consistency_score,
            'games_analyzed': total_games,
            'times_over': over_count,
            'times_under': total_games - over_count,
            'recommendation': 'OVER' if over_prob > 0.55 else 'UNDER' if over_prob < 0.45 else 'PASS'
        }
    
    def matchup_advantage(self, player_stats, opponent_defense_rank, position):
        """
        Calculate betting advantage based on matchup
        
        Args:
            player_stats: Player's recent performance
            opponent_defense_rank: Defense rank vs position (1=worst, 32=best)
            position: Player position
        
        Returns:
            Matchup advantage score
        """
        # Normalize defense rank (1-32 to 0-100 scale)
        # Lower rank (worse defense) = higher advantage
        defense_factor = (32 - opponent_defense_rank) / 32 * 100
        
        # Recent performance trend
        if 'trend' in player_stats:
            trend_factor = player_stats['trend']
        else:
            trend_factor = 50  # Neutral
        
        # Weighted average
        advantage = (defense_factor * 0.6) + (trend_factor * 0.4)
        
        return advantage
    
    def parlay_calculator(self, bets):
        """
        Calculate parlay odds and payout
        
        Args:
            bets: List of dicts with 'odds' key
        
        Returns:
            Combined odds and probability
        """
        combined_decimal_odds = 1.0
        combined_prob = 1.0
        
        for bet in bets:
            odds = bet['odds']
            
            # Convert to decimal
            if odds < 0:
                decimal = 1 + (100 / abs(odds))
            else:
                decimal = 1 + (odds / 100)
            
            combined_decimal_odds *= decimal
            
            # Calculate probability
            prob = self.calculate_implied_probability(odds) / 100
            combined_prob *= prob
        
        # Convert back to American odds
        if combined_decimal_odds >= 2.0:
            american_odds = (combined_decimal_odds - 1) * 100
        else:
            american_odds = -100 / (combined_decimal_odds - 1)
        
        return {
            'combined_odds': american_odds,
            'decimal_odds': combined_decimal_odds,
            'implied_probability': combined_prob * 100,
            'payout_100': (combined_decimal_odds - 1) * 100
        }


def render_betting_tab(sport="NFL", stats_df=None, schedule_df=None):
    """
    Streamlit component for betting analysis
    Can be added as a tab in your NFL/NBA apps
    """
    st.header("💰 Betting Analysis")
    st.markdown("Find value bets and analyze odds using your data")
    
    analyzer = BettingAnalyzer(sport=sport)
    
    # Sub-tabs for different betting types
    betting_tab1, betting_tab2, betting_tab3, betting_tab4 = st.tabs([
        "🎯 Game Lines",
        "👤 Player Props",
        "📊 Parlays",
        "📚 Betting Guide"
    ])
    
    # TAB 1: Game Lines
    with betting_tab1:
        st.subheader("Game Line Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Enter Game Odds")
            favorite_odds = st.number_input("Favorite Odds (e.g., -150)", value=-150, step=10)
            underdog_odds = st.number_input("Underdog Odds (e.g., +130)", value=130, step=10)
            
            your_win_prob = st.slider("Your Win Probability (%)", 0, 100, 50)
        
        with col2:
            st.markdown("### Analysis")
            
            # Calculate implied probabilities
            fav_implied = analyzer.calculate_implied_probability(favorite_odds)
            dog_implied = analyzer.calculate_implied_probability(underdog_odds)
            
            st.metric("Favorite Implied Probability", f"{fav_implied:.1f}%")
            st.metric("Underdog Implied Probability", f"{dog_implied:.1f}%")
            
            # Calculate EV
            ev = analyzer.calculate_ev(your_win_prob / 100, favorite_odds)
            
            if ev > 0:
                st.success(f"✅ Positive EV: ${ev:.2f} per $100 bet")
                st.markdown("**Recommendation: VALUE BET**")
            else:
                st.error(f"❌ Negative EV: ${ev:.2f} per $100 bet")
                st.markdown("**Recommendation: PASS**")
            
            # Kelly Criterion
            bankroll = st.number_input("Your Bankroll ($)", value=1000, step=100)
            kelly_bet = analyzer.kelly_criterion(your_win_prob / 100, favorite_odds, bankroll)
            
            st.metric("Kelly Criterion Bet Size", f"${kelly_bet:.2f}")
            st.caption("Using 25% Kelly (conservative)")
    
    # TAB 2: Player Props
    with betting_tab2:
        st.subheader("Player Prop Analysis")
        
        if stats_df is None or stats_df.empty:
            st.info("Load player data to analyze props")
        else:
            # Player selection
            if 'player_display_name' in stats_df.columns:
                players = sorted(stats_df['player_display_name'].unique())
                selected_player = st.selectbox("Select Player", players)
                
                player_data = stats_df[stats_df['player_display_name'] == selected_player]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Prop Line")
                    
                    stat_type = st.selectbox(
                        "Stat Type",
                        ["passing_yards", "rushing_yards", "receiving_yards", "passing_tds", "receptions"] 
                        if sport == "NFL" else ["PTS", "REB", "AST", "FG3M"]
                    )
                    
                    prop_line = st.number_input("Line", value=25.5, step=0.5)
                    over_odds = st.number_input("Over Odds", value=-110, step=10)
                    under_odds = st.number_input("Under Odds", value=-110, step=10)
                
                with col2:
                    st.markdown("### Analysis")
                    
                    if stat_type in player_data.columns:
                        analysis = analyzer.prop_bet_analysis(
                            player_data,
                            prop_line,
                            stat_type
                        )
                        
                        if analysis:
                            st.metric("Season Average", f"{analysis['season_average']:.1f}")
                            st.metric("Recent Average (L5)", f"{analysis['recent_average']:.1f}")
                            st.metric("Hit Rate (Over)", f"{analysis['over_probability']:.1f}%")
                            
                            st.markdown("---")
                            
                            if analysis['recommendation'] == 'OVER':
                                st.success("✅ **LEAN: OVER**")
                            elif analysis['recommendation'] == 'UNDER':
                                st.warning("⚠️ **LEAN: UNDER**")
                            else:
                                st.info("🤷 **LEAN: PASS**")
                            
                            st.caption(f"Hit over {analysis['times_over']}/{analysis['games_analyzed']} times")
                    else:
                        st.warning("Stat type not available for this player")
    
    # TAB 3: Parlays
    with betting_tab3:
        st.subheader("Parlay Calculator")
        
        st.markdown("Add multiple bets to calculate parlay odds and payout")
        
        num_legs = st.number_input("Number of Legs", min_value=2, max_value=10, value=3)
        
        bets = []
        for i in range(num_legs):
            col1, col2 = st.columns(2)
            with col1:
                bet_name = st.text_input(f"Bet {i+1} Name", value=f"Bet {i+1}", key=f"name_{i}")
            with col2:
                odds = st.number_input(f"Odds", value=-110, step=10, key=f"odds_{i}")
            
            bets.append({'name': bet_name, 'odds': odds})
        
        if st.button("Calculate Parlay"):
            result = analyzer.parlay_calculator(bets)
            
            st.markdown("---")
            st.markdown("### Parlay Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Combined Odds", f"{result['combined_odds']:+.0f}")
            with col2:
                st.metric("Win Probability", f"{result['implied_probability']:.1f}%")
            with col3:
                st.metric("$100 Payout", f"${result['payout_100']:.2f}")
            
            st.caption(f"Decimal Odds: {result['decimal_odds']:.2f}")
    
    # TAB 4: Betting Guide
    with betting_tab4:
        st.subheader("📚 Betting Strategy Guide")
        
        st.markdown("""
        ### Understanding the Tools
        
        **Expected Value (EV)**
        - Positive EV = Good bet long-term
        - Negative EV = Avoid
        - Formula: (Win Prob × Profit) - (Loss Prob × Stake)
        
        **Kelly Criterion**
        - Optimal bet sizing strategy
        - We use 25% Kelly (conservative)
        - Never bet more than Kelly suggests
        
        **Implied Probability**
        - What the odds say the win % is
        - Compare to your own predictions
        - Find edges where you disagree
        
        ### Bankroll Management
        
        1. **Never bet more than 1-5% per game**
        2. **Track all bets in a spreadsheet**
        3. **Don't chase losses**
        4. **Set daily/weekly limits**
        
        ### Finding Value
        
        ✅ **Good Bets:**
        - Your model predicts 60% win, odds imply 50%
        - Positive EV of $5+ per $100
        - Matchup advantages from your analysis
        
        ❌ **Avoid:**
        - Negative EV bets
        - Parlays (high variance)
        - Emotional/homer bets
        
        ### Using Your Analysis Tools
        
        1. **Check defense rankings** → Find weak matchups
        2. **Review consistency ratings** → Bet reliable players
        3. **Analyze trends** → Recent form matters
        4. **Compare to odds** → Find value
        """)
        
        st.warning("⚠️ **Disclaimer:** Gambling involves risk. Only bet what you can afford to lose. This tool is for entertainment and educational purposes only.")

if __name__ == "__main__":
    st.set_page_config(page_title="Betting Analyzer", page_icon="💰", layout="wide")
    render_betting_tab()
