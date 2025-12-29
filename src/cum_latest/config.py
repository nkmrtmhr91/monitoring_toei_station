import os
from dotenv import load_dotenv
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone, timedelta

@dataclass(frozen=False)
class Config:
    
    load_dotenv()
    
    @property
    def target_datetime(self) -> datetime:
        return datetime.now(timezone(timedelta(hours=9)))
        
    @property
    def ymd(self) -> str:
        return datetime.now(timezone(timedelta(hours=9))).strftime('%Y%m%d')
    
    @property
    def ymdhms(self) -> str:
        return datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d_%H%M%S")
    
    @property
    def api_endpoint(self) -> str:
        url     = 'https://api.odpt.org/api/v4/gtfs/realtime/toei_odpt_train_vehicle'
        param   = '?acl:consumerKey='
        return url+param

    @property
    def api_token(self) -> str | None:
        return os.getenv("API_TOKEN")

    @property
    def path_credentials(self) -> str | None:
        return os.getenv("PATH_CREDENTIALS")

    @property
    def project_id(self) -> str | None:
        return os.getenv("BQ_PROJECT_ID")
    
    @property
    def dataset(self) -> str | None:
        return os.getenv("BQ_NAME_DARASET")
    
    @property
    def table(self) -> str | None:
        return os.getenv("BG_NAME_TABLE")

    @property
    def table_cum_latest(self) -> str | None:
        return os.getenv("BG_NAME_TABLE_CUM_LATEST")

    @property
    def path_mst_station(self) -> str:
        return '../data/mst/csv/stops.csv'

    @property
    def path_mst_stop_times(self) -> str:
        return '../data/mst/csv/stop_times.csv'    
    
    @property
    def path_mst_service_id(self) -> str:
        return '../data/mst/csv/calendar.csv'   

    @property
    def path_mst_trips(self) -> str:
        return '../data/mst/csv/trips.csv'
    
    @property
    def delay_minutes(self) -> int:
        return 10
    
    # --------
    # 出力関連
    # --------
    
    @property
    def path_output_api_response(self) -> str:
        dir_output = f'./output/{self.ymd}/'
        if not os.path.exists(dir_output): 
            os.makedirs(dir_output)
        return f'{dir_output}{self.ymdhms}_api_response.csv'

    @property
    def path_output_trip_geojson(self) -> str:
        return f'./output/{self.ymd}_trip.geojson'
