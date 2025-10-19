import nflreadpy as nfl

# Load Next Gen Stats for the current season, with passing metrics
ngs_passing = nfl.load_nextgen_stats(seasons=[2025], stat_type="passing")
# For rushing or receiving you can use stat_type="rushing" or "receiving"
ngs_receiving = nfl.load_nextgen_stats(seasons=[2025], stat_type="receiving")
ngs_rushing = nfl.load_nextgen_stats(seasons=[2025], stat_type="rushing")

# If you want all years since 2016:
ngs_all = nfl.load_nextgen_stats(seasons=True, stat_type="passing")

# The data is a Polars DataFrame; convert to pandas for use with your app:
ngs_passing_pd = ngs_passing.to_pandas()
