import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta
import requests
from dateutil.relativedelta import relativedelta

# TMDb 설정
API_KEY = '679ee114f2d24e97afb8b0bcb120a2f7'
BASE_URL = 'https://api.themoviedb.org/3'

# 영화 데이터 가져오기
def get_movie_ratings(start_date, end_date):
    url = f'{BASE_URL}/discover/movie'
    params = {
        'api_key': API_KEY,
        'language': 'en-US',
        'sort_by': 'vote_average.desc',  # 평점 높은 순으로 정렬
        'vote_count.gte': 20,            # 최소 20개의 평점이 있는 영화만 포함
        'primary_release_date.gte': start_date,
        'primary_release_date.lte': end_date,
    }
    response = requests.get(url, params=params)
    data = response.json()
    movies = data['results']
    return [{
        'date': movie['release_date'],
        'title': movie['title'],
        'rating': movie['vote_average']
    } for movie in movies]

# 영화 제목을 줄이기
def shorten_title(title, max_length=4):
    if len(title) > max_length:
        return title[:max_length] + '...'
    return title

# Streamlit 제목,css
st.markdown("""
    <style>
    .title-font {
        font-size: 30px;  /* 원하는 폰트 크기로 변경 */
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="title-font">TMDB API를 이용한 월별 영화 평점 분석 차트</h1>', unsafe_allow_html=True)

# 월 선택
today = datetime.now()
months = [(today - relativedelta(months=i)).strftime('%Y-%m') for i in range(12)]
selected_month = st.selectbox('월 선택', months)
start_date = datetime.strptime(selected_month, '%Y-%m')
end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)

movie_ratings = get_movie_ratings(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
df = pd.DataFrame(movie_ratings)

# Matplotlib 제목 줄이기
df['short_title'] = df['title'].apply(shorten_title)

# 날짜 변환
df['date'] = pd.to_datetime(df['date'])

# 평점 높은 상위 20개 추출
top_rated_movies = df.nlargest(20, 'rating')

# 차트 선택
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = 'Matplotlib'  # 기본값 설정

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button('◀️'):
        st.session_state.chart_type = 'Plotly' if st.session_state.chart_type == 'Matplotlib' else 'Matplotlib'
with col2:
    st.write("차트 선택")
with col3:
    if st.button('▶️'):
        st.session_state.chart_type = 'Plotly' if st.session_state.chart_type == 'Matplotlib' else 'Matplotlib'

# 차트 표시
if st.session_state.chart_type == 'Matplotlib':
    st.subheader('Matplotlib 차트')
    fig, ax = plt.subplots()
    ax.bar(top_rated_movies['short_title'], top_rated_movies['rating'], color='skyblue')
    ax.set_title('Monthly Movie Rating Chart (Matplotlib)')
    ax.set_xlabel('title')
    ax.set_ylabel('rating')
    st.pyplot(fig)
elif st.session_state.chart_type == 'Plotly':
    st.subheader('Plotly 차트')
    fig_plotly = px.bar(top_rated_movies, x='rating', y='title', orientation='h', title='Monthly Movie Rating Chart (Plotly)', text='rating')
    st.plotly_chart(fig_plotly)

st.write(top_rated_movies)
