import pandas as pd
import streamlit as st
import boto3
import os
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc
from io import StringIO
from datetime import datetime
from dotenv import load_dotenv


font_path = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')
font_manager.fontManager.addfont(font_path)
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

plt.rcParams['axes.unicode_minus']=False

load_dotenv()
aws_access_key = os.getenv('AWS_ACCESS_KEY')
secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=secret_access_key)

# S3 버킷에서 파일 다운로드
bucket_name = 'chodang'
file_keys = {
    '550':'erp/550.csv',
    '콩국물':'erp/soup.csv'
}

selected_file = st.selectbox('제품을 선택하세요', list(file_keys.keys()))

file_key = file_keys[selected_file]

# S3에서 파일을 읽어 데이터프레임으로 변환
response = s3.get_object(Bucket=bucket_name, Key=file_key)
status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

if status == 200:
    data = response['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(data))
else:
    st.write(f"Error fetching file. HTTP status code: {status}")

weekdays = ['월', '화', '수', '목', '금', '토', '일']


# Streamlit 제목 및 설명 추가
st.title('매출 데이터 조회')
st.write('달력에서 날짜를 선택하고 해당 날짜의 몇째 주, 요일에 따른 평균 매출수량을 확인할 수 있습니다.')

# 사용자로부터 날짜 입력받기
selected_date = st.date_input("날짜를 선택하세요", datetime.now())

# 선택된 날짜로부터 ISO 주차 및 요일 계산
week_number = selected_date.isocalendar()[1]  # ISO 주차 계산
weekday_number = selected_date.weekday()        # 요일 계산 (월요일 = 0, 일요일 = 6)

weekday_korean = weekdays[weekday_number]


# 계산된 주차 및 요일 표시
st.write(f"선택한 날짜는 {week_number}주차, {weekday_korean}요일에 해당합니다.")

# 선택한 날짜의 주차와 요일에 해당하는 데이터 필터링
filtered_data = df[(df['week'] == week_number) & (df['weekday'] == weekday_number)]

# 필터링된 데이터 출력
if not filtered_data.empty:

    avg_sales = filtered_data['평균매출수량'].values[0]
    st.write(f"선택한 {week_number}주차, {weekday_korean}요일의 평균 매출수량은 {avg_sales}입니다.")
else:
    st.write("선택한 날짜에 대한 데이터가 없습니다.")

# 주차와 요일 기반 전후 5일을 계산하는 함수
def get_surrounding_weeks_and_days(week, weekday, days=5):
    dates = []
    for offset in range(-days, days + 1):
        new_week = week
        new_weekday = weekday + offset

        # 주차 넘치거나 부족할 때 처리 (한 주는 7일)
        if new_weekday < 0:
            new_week -= 1
            new_weekday = 7 + new_weekday
        elif new_weekday > 6:
            new_week += 1
            new_weekday = new_weekday - 7
        
        dates.append((new_week, new_weekday))
    
    return dates

surrounding_dates = get_surrounding_weeks_and_days(week_number, weekday_number)

filtered_data_range = df[(df[['week', 'weekday']].apply(tuple, axis=1).isin(surrounding_dates))]

# 전후 5일간의 매출수량 그래프 그리기
if not filtered_data_range.empty:
    st.write(f"선택한 날짜 기준 전후 5일간의 데이터를 그래프로 표시합니다.")
    
    # 그래프 그리기
    plt.figure(figsize=(10, 6))
    plt.plot(
        filtered_data_range['week'].astype(str) + '-' + filtered_data_range['weekday'].astype(str),
        filtered_data_range['평균매출수량'],
        marker='o',
        label='매출수량'
    )

       # 선택한 날짜에 해당하는 x축 값 계산
    selected_date_str = f'{week_number}-{weekday_number}'

    # 선택한 날짜에 수직선 표시
    plt.axvline(x=selected_date_str, color='red', linestyle='--', label='선택한 날짜')
    
    plt.title(f"전후 5일 간의 매출수량 (선택한 날짜: {selected_date})")
    plt.xlabel("주차-요일")
    plt.ylabel("매출수량")
    plt.xticks(rotation=45)
    plt.legend()
    
    st.pyplot(plt)
else:
    st.write("선택한 날짜 전후 7일 간의 데이터가 없습니다.")