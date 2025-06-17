from etls.nba_etl import extract_players_metadata, load_to_csv

def nba_metadata_pipeline(season, season_type, file_path, date_to=None):
    df = extract_players_metadata(season=season, season_type=season_type, date_to=date_to)
    load_to_csv(df, file_path)