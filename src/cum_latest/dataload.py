import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import utils

def bq_to_df_target_date(project_id, dataset, table, ymd):
    """指定日のAPIレスポンスをBQから取得してDataFrameに変換
    Args:
        path_creds (str): 認証ファイルのパス
        project_id (str): GCPプロジェクトID
        dataset (str)   : データセット名
        table (str)     : テーブル名
        ymd (str)       : 取得対象日付(YYYYMMDD)
    Returns:
        pd.DataFrame    : 指定日のAPIレスポンス
    """

    # 認証情報を直接ロード
    # creds = service_account.Credentials.from_service_account_file(
    #     path_creds
    # )

    # Client に渡す
    client = bigquery.Client(
        # credentials=creds,
        # project=creds.project_id,
    )

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset}.{table}-{ymd}`
    """

    df_api_response_date_1min = client.query(query).to_dataframe()
    
    return df_api_response_date_1min

def get_mst_trips_at_week(target_datetime, path_mst_service_id, path_mst_trips):
    """当該曜日に運行するトリップIDを取得

    Args:
        target_datetime (datetime): 実行時間のdatetimeオブジェクト
        path_mst_service_id (str): サービスIDマスタのパス
        path_mst_trips (str): トリップIDマスタのパス

    Returns:
        pd.DataFrame: 当該曜日だけのトリップIDマスタ
    """
    # ----
    # 当該曜日が該当するサービスIDの特定
    # ----
    
    #サービスIDマスタ読み込み
    df_service_id = pd.read_csv(
        path_mst_service_id
    )
    
    # 実行日の曜日名を取得
    week_name = utils.get_week_name(target_datetime)
    
    # 該当サービスID群を取得
    list_service_id = df_service_id[
        df_service_id[week_name] == 1
    ]['service_id'].tolist()

    # ----
    # 当該曜日のトリップIDマスタを得る
    # ----
    
    # トリップIDマスタ読み込み
    df_mst_trips = pd.read_csv(
        path_mst_trips
    )

    # サービスIDを基準に当該曜日のトリップIDに絞り込み
    df_mst_trips_at_week = df_mst_trips[
        df_mst_trips['service_id'].isin(list_service_id)
    ]

    return df_mst_trips_at_week
