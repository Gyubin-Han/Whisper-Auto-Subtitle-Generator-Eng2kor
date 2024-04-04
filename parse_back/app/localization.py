import pytz
from datetime import datetime, timezone

# 사용자의 현재 시간대 정보를 가져옵니다.
def get_current_date() -> str:
    user_timezone = pytz.timezone('Asia/Seoul')

    # 현재 시간을 UTC 시간으로 가져옵니다.
    utc_now = datetime.now(tz=timezone.utc)

    # 사용자의 시간대로 변환합니다.
    user_now = utc_now.astimezone(user_timezone)

    date_string = user_now.strftime('%y%m%d')

    # 출력
    # print(f"현재 시간 (서울/한국 시간대, YYMMDD 형식): {date_string}")
    
    return date_string