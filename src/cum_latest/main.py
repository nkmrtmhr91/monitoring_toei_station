import functions_framework
import os
import warnings
from config import Config
import purse
import dataload as dl
import convert

warnings.simplefilter('ignore')

@functions_framework.cloud_event
def main(cloud_event):

    config = Config()

    # -------
    # 当該日のAPI集積結果を読み込み
    # -------

    df_api_response = dl.bq_to_df_target_date(
        project_id = config.project_id,
        dataset    = config.dataset,
        table      = config.table,
        ymd        = config.ymd
    )

    # -------
    # API集積結果の前処理
    # -------

    # APIとマスタの駅座標がずれてるのでマスタに合わせる
    df_arrived_at = convert.adjust_lonlat_to_station(
        df_api_response,
        config.path_mst_station
    )
    
    # API結果を5分累積に
    df_arrived_num = convert.count_station_arrived_5min(
        df_arrived_at
    )

    # -------
    # マスタの前処理
    # -------

    # 当該日のトリップIDだけを得る
    df_mst_trips_at_week = dl.get_mst_trips_at_week(
        config.target_datetime,
        config.path_mst_service_id,
        config.path_mst_trips
    )
    
    # 実績も5分累計に
    df_mst_times = convert.count_station_arrived_5min_truth(
        config.ymd,
        config.path_mst_stop_times,
        df_mst_trips_at_week
    )
    
    # -------
    # API結果とマスタをマージ
    # -------

    df_arrived_cum = convert.merge_station_arrived_5min(
        df_arrived_num,
        df_mst_times,
    )

    df_arrived_cum = convert.postprocess(
        df_arrived_cum,
        config.target_datetime,
        config.delay_minutes
    )

    df_arrived_cum.to_gbq(
        destination_table   = f'{config.project_id}.{config.dataset}.{config.table_cum_latest}',
        project_id          = config.project_id,
        if_exists           = "replace",
    )

    return str('---')
  