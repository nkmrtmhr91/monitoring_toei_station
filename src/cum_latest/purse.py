from datetime import datetime, timedelta
import pandas as pd
import json

def json_to_df(feed) -> pd.DataFrame:
    """APIレスポンスをパースしてDFに変換

    Args:
        feed (json): APIレスポンス

    Returns:
        pd.DataFrame: パースして表形式になったAPIレスポンス
    """
    df_api_responce = pd.DataFrame()

    for entity in feed.entity:
        
        id                      = entity.id
        # vehicle.trip
        trip_id                 = entity.vehicle.trip.trip_id
        start_date              = entity.vehicle.trip.start_date
        schedule_relationship   = entity.vehicle.trip.schedule_relationship
        
        # vehicle.position
        latitude                = entity.vehicle.position.latitude
        longitude               = entity.vehicle.position.longitude
        
        current_stop_sequence   = entity.vehicle.current_stop_sequence
        current_status          = entity.vehicle.current_status
        timestamp               = entity.vehicle.timestamp
        
        # unix->datetime
        timestamp               = datetime.fromtimestamp(timestamp)+timedelta(hours=9)
        
        # vehicle.id
        vihicle_id              = entity.vehicle.vehicle.id
        
        df_entity = pd.DataFrame([{
            "id"                    : id,
            'trip_id'               : trip_id,
            'start_date'            : start_date,
            'schedule_relationship' : schedule_relationship,
            'latitude'              : latitude,
            'longitude'             : longitude,
            'currentStopSequence'   : current_stop_sequence,
            'currentStatus'         : current_status,
            'timestamp'             : timestamp,
            'vihicle_id'            : vihicle_id,
        }])
        
        df_api_responce = pd.concat([
            df_api_responce, 
            df_entity
        ], axis=0)
    
    return df_api_responce

def df_to_geojson(df_api_responce, path_output):
    """APIレスポンスをKeplerのTripレイヤー用GeoJSONに変換

    Args:
        df_api_responce (pd.DataFrame): APIレスポンスを束ねたDF
        path_output (str): KeplerのTripレイヤー用GeoJSONの出力先

    Returns:
        None
    """
    features = []
    
    for id, _df in df_api_responce.sort_values(["vihicle_id","timestamp"]).groupby("vihicle_id", sort=False):
        
        coords = [
            [float(x), float(y), 0, int(t)] for x,y,t in zip(_df["longitude"], _df["latitude"], _df["timestamp"])
        ]
        
        features.append({
            "type"      :"Feature",
            "properties":{"trip_id": id},
            "geometry"  :{"type":"LineString","coordinates": coords}
        })

    geo = {"type":"FeatureCollection","features": features}

    with open(path_output, "w", encoding="utf-8") as f:
        
        json.dump(geo, f, ensure_ascii=False, indent=2)

    return None
