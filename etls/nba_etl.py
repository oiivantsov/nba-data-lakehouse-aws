import time
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats, commonplayerinfo


def extract_players_total_stats(season: str = None, date_to: str = None, season_type: str = None) -> pd.DataFrame:
    """
    Extracts NBA player total stats using optional parameters.

    :param season: e.g., '2024-25'
    :param date_to: e.g., '03-01-2025'
    :param season_type: e.g., 'Regular Season'
    :return: DataFrame of player stats
    """
    params = {}
    if season is not None:
        params['season'] = season
    if season_type is not None:
        params['season_type_all_star'] = season_type
    if date_to is not None:
        params['date_to_nullable'] = date_to

    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(**params)
    player_stats_df = player_stats.get_data_frames()[0]
    return player_stats_df


def extract_players_metadata(season: str = None, date_to: str = None, season_type: str = None) -> pd.DataFrame:
    """
    Extracts player metadata for a given NBA season (optional parameters).

    :param season: e.g., '2024-25'
    :param date_to: e.g., '03-01-2025'
    :param season_type: e.g., 'Regular Season'
    :return: DataFrame of player metadata
    """
    # Step 1: Prepare parameters
    params = {}
    if season is not None:
        params['season'] = season
    if season_type is not None:
        params['season_type_all_star'] = season_type
    if date_to is not None:
        params['date_to_nullable'] = date_to

    # Step 2: Load player stats
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(**params)
    player_stats_df = player_stats.get_data_frames()[0]

    # Step 3: Extract metadata for each player
    player_ids = player_stats_df['PLAYER_ID'].unique()
    player_metadata = []

    for i, player_id in enumerate(player_ids, 1):
        try:
            info = commonplayerinfo.CommonPlayerInfo(player_id=int(player_id)).get_normalized_dict()
            data = info['CommonPlayerInfo'][0]
            player_metadata.append({
                'PLAYER_ID': data.get('PERSON_ID'),
                'PLAYER_NAME': data.get('DISPLAY_FIRST_LAST'),
                'TEAM_NAME': data.get('TEAM_NAME'),
                'POSITION': data.get('POSITION'),
                'HEIGHT': data.get('HEIGHT'),
                'WEIGHT': data.get('WEIGHT'),
                'COUNTRY': data.get('COUNTRY'),
                'BIRTHDATE': data.get('BIRTHDATE'),
                'DRAFT_YEAR': data.get('DRAFT_YEAR'),
                'DRAFT_NUMBER': data.get('DRAFT_NUMBER'),
                'FROM_YEAR': data.get('FROM_YEAR'),
                'TO_YEAR': data.get('TO_YEAR')
            })
            print(i)
        except Exception as e:
            print(f"Error with PLAYER_ID {player_id}: {e}")
        time.sleep(0.7)

    player_metadata_df = pd.DataFrame(player_metadata)
    return player_metadata_df


def load_to_csv(df: pd.DataFrame, file_path: str) -> None:
    df.to_csv(file_path, index=False)