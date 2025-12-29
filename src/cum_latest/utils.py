import os
from datetime import datetime
import pandas as pd
import geopandas as gpd

def txt_to_df_mst():

    dir_mst_txt  = '../data/mst/txt/'
    dir_mst_csv  = '../data/mst/csv/'
    
    # TXTファイルをループ
    for file_name in os.listdir(dir_mst_txt):
        
        path_mst_txt = os.path.join(dir_mst_txt, file_name)

        # TXT -> DataFrame
        df = pd.read_csv(path_mst_txt)
        
        name, _ = os.path.splitext(file_name)

        df.to_csv(
            f'{dir_mst_csv}{name}.csv', 
            index=False,
            encoding='utf-8-sig'
        )

    return None

def preprocess_network():
    """国交省が整備している駅路線のジオメトリの雑多な前処理
    """

    # --------
    # 駅範囲のジオメトリ
    # --------
    gdf_station = gpd.read_file(
        '../data/network/N02-23_Station.geojson', 
        encoding='cp932'
    )

    # 管理者が東京都のジオメトリだけに
    gdf_station = gdf_station[gdf_station['N02_004']=='東京都']
    # 文字化けがこうしないと治らない
    gdf_station['N02_003'] = gdf_station['N02_003'].copy(deep=True)

    gdf_station.to_file(
        '../data/network/n02_23_station_toei.geojson'
    )

    # --------
    # 路線区間のジオメトリ
    # --------
    gdf_section = gpd.read_file(
        '../data/network/N02-23_RailroadSection.geojson', 
        encoding='cp932'
    )

    # 管理者が東京都のジオメトリだけに
    gdf_section = gdf_section[gdf_section['N02_004']=='東京都']
    # 文字化けがこうしないと治らない
    gdf_section['N02_003'] = gdf_section['N02_003'].copy(deep=True)

    gdf_section.to_file(
        '../data/network/n02_23_section_toei.geojson'
    )
    
    return None

def get_week_name(datetime: datetime) -> str:
    """実行日の曜日文字列を取得

    Args:
        datetime (datetime): 実行時間のdatetimeオブジェクト

    Returns:
        str: 曜日名
    """
    
    week_cd = datetime.weekday()
    
    print(week_cd)
    
    if week_cd == 0:
        return 'monday'
    elif week_cd == 1:
        return 'tuesday'
    elif week_cd == 2:
        return 'wednesday'
    elif week_cd == 3:
        return 'thursday'
    elif week_cd == 4:
        return 'friday'
    elif week_cd == 5:
        return 'saturday'
    elif week_cd == 6:
        return 'sunday'
    else:
        raise ValueError()
