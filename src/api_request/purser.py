import pandas as pd

def json_to_df(feed) -> pd.DataFrame:
    
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
        
        # vehicle.id
        vihicle_id              = entity.vehicle.vehicle.id
        
        df_entity = pd.DataFrame([{
            'timestamp'             : timestamp,
            'id'                    : id,
            'vihicle_id'            : vihicle_id,
            'trip_id'               : trip_id,
            'start_date'            : start_date,
            'schedule_relationship' : schedule_relationship,
            'current_stop_sequence' : current_stop_sequence,
            'current_status'        : current_status,
            'latitude'              : latitude,
            'longitude'             : longitude,
        }])
        
        df_api_responce = pd.concat([df_api_responce, df_entity], axis=0)
    
    return df_api_responce