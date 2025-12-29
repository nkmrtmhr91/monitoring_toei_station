import urllib.request
import functions_framework
from google.transit import gtfs_realtime_pb2

from config import Config
import purser

@functions_framework.cloud_event
def main(cloud_event):
    
    config = Config()
    
    # -------
    # APIリクエスト
    # -------
    
    api_endpoint    = config.api_endpoint
    token           = config.api_token
    url_request     = api_endpoint + token
    
    feed = gtfs_realtime_pb2.FeedMessage()
    
    with urllib.request.urlopen(url_request) as res:
        feed.ParseFromString(res.read())
    
    # -------
    # APIレスポンスのDataFrame変換
    # -------
    
    df_api_responce = purser.json_to_df(feed)
    
    # -------
    # BigQueryへ書き込み
    # -------
    
    project_id  = config.bq_project_id
    dataset     = config.bq_datasets
    table       = config.bq_table
    destination = f"{dataset}.{table}"

    df_api_responce.to_gbq(
        destination_table   = destination,
        project_id          = project_id,
        if_exists           = "append",
    )   
        
    return str('success.')
