from etls.nba_etl import extract_players_total_stats, load_to_csv

def nba_totals_pipeline(season, season_type, file_path, date_to=None):
    df = extract_players_total_stats(season=season, season_type=season_type, date_to=date_to)
    load_to_csv(df, file_path)