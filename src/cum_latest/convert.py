import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta

def adjust_lonlat_to_station(df_api_responce: pd.DataFrame, path_mst_station: str) -> pd.DataFrame:
    """列車の記録位置を駅座標に空間補正

    Args:
        df_api_responce (pd.DataFrame): 当該日のAPIレスポンス
        path_mst_station (str): 駅情報マスタのパス

    Returns:
        pd.DataFrame: 駅情報つきAPIレスポンス
    """

    # APIレスポンスをジオメトリ付きに
    gdf_api_responce = gpd.GeoDataFrame(
        df_api_responce, 
        geometry=gpd.points_from_xy(
            df_api_responce['longitude'], 
            df_api_responce['latitude']
        )
    )

    # 駅地点情報をジオメトリ付きに
    df_stations = pd.read_csv(
        path_mst_station
    )
    gdf_stations = gpd.GeoDataFrame(
        df_stations, 
        geometry=gpd.points_from_xy(
            df_stations['stop_lon'], 
            df_stations['stop_lat']
        )
    )

    # 駅地点別の列車毎到着時刻
    df_arrived_at = gpd.sjoin_nearest(
        gdf_api_responce,
        gdf_stations,
        how='left'
    )

    df_arrived_at = df_arrived_at[[
        'timestamp'             ,
        'zone_id'               ,
        'stop_id'               ,
        'stop_code'             ,
        'stop_name'             ,
        'trip_id'               ,
        'vihicle_id'            ,
        'current_stop_sequence' ,
        'current_status'        ,
        'stop_lat'              ,
        'stop_lon'              ,
    ]].rename(columns={
        'stop_lat'              : 'latitude',
        'stop_lon'              : 'longitude',    
    })
    
    return df_arrived_at

def count_station_arrived_5min(df_arrived_station_at):
    """駅ごとの到達台数を5分毎の累計に

    Args:
        df_arrived_station_at (pd.DataFrame): 駅ごとの5分ごとの到達台数

    Returns:
        pd.DataFrame: 駅ごとの5分累計の到達台数
    """
    df_arrived_station_at = df_arrived_station_at.drop_duplicates(
        subset=['vihicle_id', 'stop_id'],
        keep='last'
    )
    
    df_arrived_station_at['datetime'] = pd.to_datetime(
        df_arrived_station_at['timestamp'], unit="s"
    ) + timedelta(hours=9)

    # 5分切り上げ
    df_arrived_station_at['datetime_5min'] = (
        df_arrived_station_at['datetime'].dt.ceil('5min')
    )

    # 5分、駅ごとに到達列車数の集計
    df_arrived_num = df_arrived_station_at.groupby([
        'datetime_5min' ,
        'zone_id'       ,
        'stop_id'       ,
        'stop_code'     ,
        'stop_name'     ,
        'latitude'      ,
        'longitude'
    ]).size().reset_index(name='arrived_num')
    
    # 5分のごとの累計到達数に集計
    df_arrived_num = df_arrived_num.sort_values([
        'stop_id',
        'datetime_5min'
    ])
    df_arrived_num['arrived_cum'] = df_arrived_num.groupby(
        'stop_id'
    )['arrived_num'].cumsum()
    
    return df_arrived_num

def count_station_arrived_5min_truth(ymd, path_mst_stop_times, df_mst_trips):
    """1日累計5分毎の到着数実績を駅ごとに集計

    Args:
        ymd (str): 実行日の日付文字列
        path_mst_stop_times (str): 時刻マスタのパス
        df_mst_trips (pd.DataFrame): 当該曜日だけのトリップIDマスタ

    Returns:
        pd.DataFrame: 駅ごとの日累計5分毎の到着数実績
    """
    
    # ----------
    # 当該曜日に該当する実績だけにフィルタ
    # ----------

    # 当該曜日のトリップID群
    list_trip_id = df_mst_trips['trip_id'].unique().tolist()

    # 駅ごとの発着時刻マスタ
    df_mst_times = pd.read_csv(
        path_mst_stop_times,
        usecols=[
            'trip_id',
            'arrival_time',
            'stop_id'
        ]
    )
    
    # 実績を所定トリップID群だけにフィルタ
    df_mst_times = df_mst_times[
        df_mst_times['trip_id'].isin(list_trip_id)
    ]

    # ----------
    # 5分丸めの累計に
    # ----------

    # 時刻しかないので日付を宛がってdatetimeに
    df_mst_times["datetime_5min"] = (
        pd.to_datetime(ymd) + 
        pd.to_timedelta(df_mst_times["arrival_time"])
    ).dt.ceil('5min')

    # 5分粒度の出発台数を駅ごとに集計
    df_mst_times = df_mst_times.groupby([
        'datetime_5min',
        'stop_id'
    ]).size().reset_index(name='arrived_num')

    # ----------
    # 5分×地点でレコードを充足させる
    # ----------
    
    # 時刻を網羅
    datetimes_5min = pd.date_range(
        start=df_mst_times['datetime_5min'].min(), 
        end=df_mst_times['datetime_5min'].max(), 
        freq="5T"
    )

    # 充足レコードを用意
    df_fullfill_5min = pd.MultiIndex.from_product(
        [datetimes_5min, df_mst_times['stop_id'].unique().tolist()],
        names=["datetime_5min", "stop_id"]
    ).to_frame(
        index=False
    ).sort_values(
        ["stop_id", "datetime_5min"],
        ascending=True
    )
    
    # 充足させたレコードにマージ
    df_mst_times = pd.merge(
        df_fullfill_5min,
        df_mst_times,
        on=["stop_id", "datetime_5min"],
        how='left'
    ).fillna({
        'arrived_num':0
    }).astype({
        'arrived_num':int
    })
    
    # 5分粒度の出発台数を累計に
    df_mst_times = df_mst_times.sort_values([
        'stop_id',
        'datetime_5min'
    ])
    df_mst_times['arrived_cum'] = df_mst_times.groupby(
        'stop_id'
    )['arrived_num'].cumsum()    

    # ----------
    # 地点情報をマージ
    # ----------

    # 駅情報マスタをマージ
    df_stations = pd.read_csv(
        '../data/mst/csv/stops.csv',
        usecols=[
            'stop_id',
            'stop_code',
            'stop_name',
            'stop_lat',
            'stop_lon',
            'zone_id',
        ]
    ).rename(columns={
        'stop_lat':'latitude',
        'stop_lon':'longitude',
    })

    df_mst_times = pd.merge(
        df_mst_times,
        df_stations,
        on='stop_id',
        how='left'
    )

    return df_mst_times

def merge_station_arrived_5min(df_arrived_cum_api, df_mst_arrived_cum):
    """APIレスポンスと実績で時刻別の累計到達台数をマージ

    Args:
        df_arrived_cum_api (pd.DataFrame): APIレスポンスの5分毎累計到達台数
        df_mst_arrived_cum (pd.DataFrame): マスタの5分毎累計到達台数

    Returns:
        pd.DataFrame: APIレスポンスとマスタの5分毎累計到達台数
    """
    df_arrived_cum = pd.merge(
        df_mst_arrived_cum,
        df_arrived_cum_api,
        on=[
            'datetime_5min', 
            'zone_id', 
            'stop_id', 
            'stop_code', 
            'stop_name',  
            'latitude', 
            'longitude',   
        ],
        how='left',
        suffixes=['_mst', '_api']
    ).fillna({
        'arrived_num_api'   : 0,
    })
    
    df_arrived_cum = df_arrived_cum[[
        'datetime_5min'     , 
        'zone_id'           , 
        'stop_id'           , 
        'stop_code'         , 
        'stop_name'         ,
        'arrived_num_mst'   ,
        'arrived_num_api'   ,
        'arrived_cum_mst'   ,  
        'arrived_cum_api'   ,
        'latitude'          , 
        'longitude'         , 
    ]]
    
    return df_arrived_cum

def postprocess(df_arrived_cum, target_datetime, delay_minutes):
    """ダッシュボーディング前の雑多な後処理

    Args:
        df_arrived_cum (pd.DataFrame): 実績とAPI結果で突合済みな5分累計通過台数
        target_datetime (datetime): 実行時刻
        delay_minutes (int): 実行時刻から遅らせたい所定分

    Returns:
        pd.DataFrame: ダッシュボーディングの用意が整ったDF
    """
    # --------
    # APIレスポンス側の出発台数を再度累計に
    # --------
    # 実績側の時刻レコード頻度にAPIを追いつかせる

    # cumsum()前に一番早い時刻の空白を埋める
    dt_earliest = df_arrived_cum['datetime_5min'].min()
    
    # 一番早い時刻にAPI結果がなければ0埋めしてからcumsum()
    df_arrived_cum.loc[
        (df_arrived_cum['datetime_5min'] == dt_earliest) & (df_arrived_cum['arrived_cum_api'].isna()),
        'arrived_cum_api'
    ] = 0

    # 5分粒度の出発台数を再度累計に
    df_arrived_cum = df_arrived_cum.sort_values([
        'stop_id',
        'datetime_5min'
    ])
    df_arrived_cum['arrived_cum_api'] = df_arrived_cum.groupby(
        'stop_id'
    )['arrived_num_api'].cumsum()   
    
    # --------
    # ダッシュボーディング用に最新時刻から少し遅らせる
    # --------
    # 都度APIを叩く処理側のペースを超えないように
    
    # DF側の時刻をタイムゾーン付きに
    df_arrived_cum['datetime_5min'] = pd.to_datetime(
        df_arrived_cum['datetime_5min']
    ).dt.tz_localize('Asia/Tokyo')
    
    # 実行時刻から任意分ぶん出力を切り捨てる
    df_arrived_cum = df_arrived_cum[
        df_arrived_cum['datetime_5min'] <= (target_datetime - timedelta(minutes=delay_minutes))
    ]
    
    # 時刻情報からタイムゾーンを取り除く
    df_arrived_cum['datetime_5min'] = df_arrived_cum['datetime_5min'].dt.tz_localize(None)

    df_arrived_cum = df_arrived_cum[[
        'datetime_5min'     , 
        'zone_id'           , 
        'stop_id'           , 
        'stop_code'         , 
        'stop_name'         ,
        'arrived_num_mst'   , 
        'arrived_num_api'   , 
        'arrived_cum_mst'   ,
        'arrived_cum_api'   , 
        'latitude'          , 
        'longitude'         ,
    ]].astype({
        'datetime_5min'     : 'datetime64[s]', 
        'zone_id'           : int, 
        'stop_id'           : int,
        'stop_code'         : str,
        'stop_name'         : str,
        'arrived_num_mst'   : int,
        'arrived_num_api'   : int,
        'arrived_cum_mst'   : int,
        'arrived_cum_api'   : int,
        'latitude'          : float, 
        'longitude'         : float, 
    })

    return df_arrived_cum
