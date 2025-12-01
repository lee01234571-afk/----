import sqlite3
import random
from datetime import datetime

# 데이터베이스 연결 함수
def create_connection():
    """데이터베이스 연결을 생성하고 반환합니다."""
    conn = sqlite3.connect('lunch_menu.db')
    return conn

def create_table():
    """메뉴 테이블이 없으면 생성하고 초기 데이터를 삽입합니다."""
    conn = create_connection()
    cursor = conn.cursor()
    
    # 메뉴 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price INTEGER DEFAULT 0
    )
    ''')
    
    # 초기 데이터 삽입 (없는 경우에만)
    initial_menus = [
        # 한식
        ('김치찌개', '한식', 8000),
        ('된장찌개', '한식', 7500),
        ('제육볶음', '한식', 8500),
        ('비빔밥', '한식', 8000),
        ('불고기', '한식', 12000),
        # 중식
        ('짜장면', '중식', 6000),
        ('짬뽕', '중식', 7000),
        ('탕수육', '중식', 15000),
        ('볶음밥', '중식', 6500),
        ('마파두부', '중식', 7500),
        # 일식
        ('초밥', '일식', 12000),
        ('라멘', '일식', 8500),
        ('우동', '일식', 7000),
        ('돈카츠', '일식', 11000),
        ('오니기리', '일식', 5000)
    ]
    
    # 중복 체크 후 데이터 삽입
    for menu in initial_menus:
        cursor.execute('SELECT id FROM menus WHERE name = ?', (menu[0],))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO menus (name, category, price) VALUES (?, ?, ?)', menu)
    
    conn.commit()
    conn.close()

def get_random_menu(category='all'):
    """카테고리에 맞는 랜덤 메뉴를 반환합니다."""
    conn = create_connection()
    cursor = conn.cursor()
    
    if category == 'all':
        cursor.execute('SELECT name, category, price FROM menus')
    else:
        cursor.execute('SELECT name, category, price FROM menus WHERE category = ?', (category,))
    
    menus = cursor.fetchall()
    conn.close()
    
    if menus:
        return random.choice(menus)
    return None

def get_menus_by_category(category):
    """카테고리별 메뉴 목록을 반환합니다."""
    conn = create_connection()
    cursor = conn.cursor()
    
    if category == 'all':
        cursor.execute('SELECT name, category, price FROM menus')
    else:
        cursor.execute('SELECT name, category, price FROM menus WHERE category = ?', (category,))
    
    menus = cursor.fetchall()
    conn.close()
    return menus
