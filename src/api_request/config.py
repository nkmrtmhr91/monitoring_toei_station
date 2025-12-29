import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# タイムゾーンの生成
JST = timezone(timedelta(hours=+9), 'JST')

@dataclass(frozen=False)
class Config:
    
    load_dotenv()
    
    @property
    def ymd(self) -> str:
        return datetime.now(timezone(timedelta(hours=9))).strftime('%Y%m%d')
    
    @property
    def ymdhms(self) -> str:
        return datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d_%H%M%S")
     
    @property
    def api_endpoint(self) -> str:
        url='https://api.odpt.org/api/v4/gtfs/realtime/toei_odpt_train_vehicle'
        param='?acl:consumerKey='
        return url+param

    @property
    def api_token(self) -> str:
        token = os.environ["API_TOKEN"]
        return token

    @property
    def bq_project_id(self) -> str | None:
        return os.getenv("BQ_PROJECT_ID")
    
    @property
    def bq_datasets(self) -> str | None:
        return os.getenv("BQ_NAME_DARASET")
    
    @property
    def bq_table(self) -> str | None:
        return os.getenv("BG_NAME_TABLE")
        