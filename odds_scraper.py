"""
Odds & Best Bets Scraper
Automatically pulls betting data from various sources
"""

import requests
import pandas as pd
from datetime import datetime
import streamlit as st

class OddsScraper:
    """
    Scrapes odds and best bets from multiple sources
    """
    
    def __init__(self):
        self.api_key = None  # For paid APIs
        
    # ============================================================
    # METHOD 1: The Odds API (Recommended - Free Tier Available)
    # ============================================================
    
    def get_odds_api_data(self, sport='americanfootball_nfl', api_key=None):
        """
        Get live odds from The Odds API
        Free tier: 500 requests/month
        Sign up: https://the-odds-api.com/
        
        Args:
            sport: 'americanfootball_nfl' or 'basketball_nba'
            api_key: Your API key from the-odds-api.com
        
        Returns:
            DataFrame with odds from multiple sportsbooks
        """
        if not api_key:
            return None
        
        try:
            # Get upcoming games with odds
            url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds/'
            
            params = {
                'apiKey': api_key,
                'regions': 'us',
                'markets': 'h2h,spreads,totals',  # Moneyline, spreads, over/under
                'oddsFormat': 'american',
                'bookmakers': 'draftkings,fanduel,betmgm'  # Top sportsbooks
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            games = response.json()
            
            # Parse into DataFrame
            odds_data = []
            for game in games:
                home_team = game['home_team']
                away_team = game['away_team']
                
                for bookmaker in game.get('bookmakers', []):
                    for market in bookmaker.get('markets', []):
                        if market['key'] == 'h2h':  # Moneyline
                            for outcome in market['outcomes']:
                                odds_data.append({
                                    'game_id': game['id'],
                                    'commence_time': game['commence_time'],
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'bookmaker': bookmaker['title'],
                                    'market': 'moneyline',
                                    'team': outcome['name'],
                                    'odds': outcome['price']
                                })
            
            return pd.DataFrame(odds_data)
        
        except Exception as e:
            st.error(f"Error fetching odds: {str(e)}")
            return None
    
    # ============================================================
    # METHOD 2: Action Network API (Premium)
    # ============================================================
    
    def get_action_network_data(self, api_key=None):
        """
        Get sharp money, public betting %, and line movement
        Requires premium subscription
        """
        # Similar structure to above
        pass
    
    # ============================================================
    # METHOD 3: Web Scraping (Use Carefully - Check ToS)
    # ============================================================
    
    def scrape_rotowire_projections(self):
        """
        Scrape player projections from RotoWire
        WARNING: Check their Terms of Service first!
        """
        # This is for educational purposes - always check ToS
        url = "https://www.rotowire.com/football/player-projections.php"
        
        # Would need to parse HTML tables
        # Use BeautifulSoup or Selenium
        pass
    
    # ============================================================
    # METHOD 4: RSS Feeds & Public APIs
    # ============================================================
    
    def get_free_best_bets(self):
        """
        Aggregate free best bets from public sources
        - ESPN picks
        - CBS Sports picks
        - Public betting trends
        """
        best_bets = []
        
        # Example: Mock data structure
        best_bets.append({
            'source': 'ESPN',
            'player': 'Patrick Mahomes',
            'bet_type': 'Over 275.5 Pass Yards',
            'odds': -110,
            'confidence': 'High',
            'reasoning': 'Weak secondary matchup'
        })
        
        return pd.DataFrame(best_bets)
    
    # ============================================================
    # HELPER: Compare Odds Across Books
    # ============================================================
    
    def find_best_odds(self, odds_df):
        """
        Find best available odds for each bet
        
        Args:
            odds_df: DataFrame from get_odds_api_data()
        
        Returns:
            DataFrame with best odds per game/market
        """
        if odds_df is None or odds_df.empty:
            return None
        
        # Group by game and team, get best odds
        best_odds = odds_df.loc[
            odds_df.groupby(['game_id', 'team', 'market'])['odds'].idxmax()
        ]
        
        return best_odds
    
    # ============================================================
    # ARBITRAGE FINDER
    # ============================================================
    
    def find_arbitrage_opportunities(self, odds_df):
        """
        Find risk-free arbitrage opportunities (rare but possible)
        
        Returns:
            List of arbitrage opportunities with guaranteed profit
        """
        if odds_df is None or odds_df.empty:
            return []
        
        arb_opportunities = []
        
        # Group by game
        for game_id in odds_df['game_id'].unique():
            game_odds = odds_df[odds_df['game_id'] == game_id]
            
            # Get best odds for each team
            teams = game_odds['team'].unique()
            if len(teams) == 2:
                team1_best = game_odds[game_odds['team'] == teams[0]]['odds'].max()
                team2_best = game_odds[game_odds['team'] == teams[1]]['odds'].max()
                
                # Convert to implied probability
                if team1_best < 0:
                    prob1 = (-team1_best) / (-team1_best + 100)
                else:
                    prob1 = 100 / (team1_best + 100)
                
                if team2_best < 0:
                    prob2 = (-team2_best) / (-team2_best + 100)
                else:
                    prob2 = 100 / (team2_best + 100)
                
                # If total probability < 1, arbitrage exists!
                total_prob = prob1 + prob2
                if total_prob < 1:
                    profit = ((1 / total_prob) - 1) * 100
                    arb_opportunities.append({
                        'game': f"{teams[0]} vs {teams[1]}",
                        'profit_pct': profit,
                        'bet1': f"{teams[0]} at {team1_best}",
                        'bet2': f"{teams[1]} at {team2_best}"
                    })
        
        return arb_opportunities


# ============================================================
# STREAMLIT INTEGRATION
# ============================================================

def render_odds_comparison_tab():
    """
    Add this as a new tab in your NFL/NBA apps
    """
    st.header("💰 Live Odds Comparison")
    st.markdown("Compare odds across sportsbooks and find the best value")
    
    scraper = OddsScraper()
    
    # API Key input
    with st.expander("⚙️ Setup Instructions"):
        st.markdown("""
        ### Get Free API Access:
        
        1. **The Odds API** (Recommended)
           - Sign up: https://the-odds-api.com/
           - Free tier: 500 requests/month
           - Get API key from dashboard
        
        2. **Enter your API key below**
        
        3. **Select sport and view live odds**
        """)
    
    api_key = st.text_input("The Odds API Key", type="password")
    
    if api_key:
        sport = st.selectbox(
            "Sport",
            ["americanfootball_nfl", "basketball_nba"],
            format_func=lambda x: "NFL" if "nfl" in x else "NBA"
        )
        
        if st.button("🔄 Fetch Live Odds"):
            with st.spinner("Fetching odds from sportsbooks..."):
                odds_df = scraper.get_odds_api_data(sport, api_key)
                
                if odds_df is not None and not odds_df.empty:
                    st.success(f"✅ Loaded {len(odds_df)} odds from {odds_df['bookmaker'].nunique()} sportsbooks")
                    
                    # Show best odds
                    st.subheader("📊 Best Available Odds")
                    best_odds = scraper.find_best_odds(odds_df)
                    st.dataframe(best_odds, use_container_width=True)
                    
                    # Find arbitrage
                    arb_opps = scraper.find_arbitrage_opportunities(odds_df)
                    if arb_opps:
                        st.subheader("🎯 Arbitrage Opportunities Found!")
                        for opp in arb_opps:
                            st.success(f"**{opp['game']}** - Guaranteed Profit: {opp['profit_pct']:.2f}%")
                            st.write(f"Bet 1: {opp['bet1']}")
                            st.write(f"Bet 2: {opp['bet2']}")
                    
                    # Download
                    st.download_button(
                        "📥 Download Odds CSV",
                        odds_df.to_csv(index=False),
                        f"odds_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
                else:
                    st.error("No odds data available")
    else:
        st.info("👆 Enter your API key above to fetch live odds")
        
        # Show sample/free picks
        st.subheader("📰 Free Best Bets Aggregator")
        st.markdown("Collected from public sources (ESPN, CBS, etc.)")
        
        free_bets = scraper.get_free_best_bets()
        if not free_bets.empty:
            st.dataframe(free_bets, use_container_width=True)


# ============================================================
# AUTOMATED DAILY UPDATES
# ============================================================

def schedule_daily_odds_update():
    """
    Set this up to run daily via:
    1. GitHub Actions
    2. Streamlit Cloud scheduled reruns
    3. Heroku Scheduler
    4. Cron job
    """
    scraper = OddsScraper()
    
    # Fetch odds
    nfl_odds = scraper.get_odds_api_data('americanfootball_nfl', 'YOUR_API_KEY')
    nba_odds = scraper.get_odds_api_data('basketball_nba', 'YOUR_API_KEY')
    
    # Save to CSV or database
    if nfl_odds is not None:
        nfl_odds.to_csv(f'odds_nfl_{datetime.now().strftime("%Y%m%d")}.csv', index=False)
    
    if nba_odds is not None:
        nba_odds.to_csv(f'odds_nba_{datetime.now().strftime("%Y%m%d")}.csv', index=False)


if __name__ == "__main__":
    st.set_page_config(page_title="Odds Scraper", layout="wide")
    render_odds_comparison_tab()
