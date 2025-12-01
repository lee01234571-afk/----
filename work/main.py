import tkinter as tk
from tkinter import ttk, messagebox, font
import random
import time
import threading
from datetime import datetime
import json
import os

class Server:
    def __init__(self, name, cpu_usage, cost_per_hour):
        self.name = name
        self.cpu_usage = cpu_usage
        self.cost_per_hour = cost_per_hour
        self.running = True
        self.last_updated = datetime.now().strftime("%H:%M:%S")
    
    def update_usage(self):
        """서버 사용량을 업데이트합니다."""
        self.cpu_usage = random.uniform(5, 80)  # 기본적으로 5~80% 사이의 랜덤한 CPU 사용률
        self.last_updated = datetime.now().strftime("%H:%M:%S")
    
    def stop_server(self):
        """서버를 중지합니다."""
        self.running = False
        self.cpu_usage = 0
        self.last_updated = datetime.now().strftime("%H:%M:%S")

class FinOpsDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("FinOps Cloud Cost Optimizer")
        self.root.geometry("1000x600")
        self.root.configure(bg='#2c3e50')
        
        # 서버 데이터 초기화
        self.servers = [
            Server(f"Server-{i+1}", 
                  random.uniform(40, 80) if i >= 2 else random.uniform(1, 5),  # 처음 2개는 저사용 서버
                  random.uniform(5, 15))  # 시간당 $5~15 비용
            for i in range(5)
        ]
        
        # UI 초기화
        self.setup_ui()
        
        # 5초마다 서버 상태 업데이트
        self.update_server_status()
    
    def setup_ui(self):
        """UI 컴포넌트를 설정합니다."""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(
            main_frame, 
            text="FinOps Cloud Cost Optimization Dashboard",
            font=('Helvetica', 16, 'bold'),
            foreground='white',
            background='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # 중앙 프레임 (좌우 분할)
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(fill=tk.BOTH, expand=True)
        
        # 좌측 프레임 - 서버 리스트
        left_frame = ttk.LabelFrame(center_frame, text="서버 리소스 현황", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 서버 리스트 헤더
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="서버명", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Label(header_frame, text="CPU 사용률", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Label(header_frame, text="시간당 비용", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Label(header_frame, text="상태", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=5, expand=True)
        
        # 서버 리스트
        self.server_frames = []
        for i, server in enumerate(self.servers):
            frame = ttk.Frame(left_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=server.name).pack(side=tk.LEFT, padx=5, expand=True)
            
            cpu_label = ttk.Label(frame, text=f"{server.cpu_usage:.1f}%")
            cpu_label.pack(side=tk.LEFT, padx=5, expand=True)
            
            cost_label = ttk.Label(frame, text=f"${server.cost_per_hour:.2f}/h")
            cost_label.pack(side=tk.LEFT, padx=5, expand=True)
            
            status_label = ttk.Label(frame, text="실행 중", foreground="green")
            status_label.pack(side=tk.LEFT, padx=5, expand=True)
            
            self.server_frames.append({
                'frame': frame,
                'cpu': cpu_label,
                'cost': cost_label,
                'status': status_label
            })
        
        # 우측 프레임 - 비용 분석
        right_frame = ttk.LabelFrame(center_frame, text="비용 분석", padding=10, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        # 현재 월 청구액
        ttk.Label(right_frame, text="현재 예상 월 청구액", font=('Helvetica', 10)).pack(pady=(10, 5))
        
        self.monthly_cost_label = ttk.Label(
            right_frame, 
            text="$0.00", 
            font=('Helvetica', 24, 'bold'),
            foreground='red'
        )
        self.monthly_cost_label.pack(pady=(0, 20))
        
        # 절감 가능 금액
        ttk.Label(right_frame, text="AI 분석 결과", font=('Helvetica', 10, 'bold')).pack(pady=(10, 5))
        
        self.saving_label = ttk.Label(
            right_frame, 
            text="최적화를 실행해주세요",
            font=('Helvetica', 10),
            wraplength=250
        )
        self.saving_label.pack(pady=(0, 20))
        
        # 최적화 버튼
        self.optimize_btn = ttk.Button(
            right_frame,
            text="🔍 AI 비용 최적화 실행",
            command=self.run_optimization,
            style="Accent.TButton"
        )
        self.optimize_btn.pack(pady=10, fill=tk.X)
        
        # 스타일 설정
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 12, 'bold'))
        
        # 초기 비용 계산
        self.update_cost_display()
    
    def update_server_status(self):
        """서버 상태를 업데이트합니다."""
        for i, server in enumerate(self.servers):
            if server.running:
                server.update_usage()
                
                # UI 업데이트
                frame = self.server_frames[i]
                frame['cpu'].config(text=f"{server.cpu_usage:.1f}%")
                
                # CPU 사용량에 따라 색상 변경
                if server.cpu_usage < 10:
                    frame['cpu'].config(foreground='orange')
                else:
                    frame['cpu'].config(foreground='black')
        
        # 비용 표시 업데이트
        self.update_cost_display()
        
        # 5초 후에 다시 업데이트
        self.root.after(5000, self.update_server_status)
    
    def update_cost_display(self):
        """비용 정보를 업데이트합니다."""
        total_hourly_cost = sum(
            server.cost_per_hour 
            for server in self.servers 
            if server.running
        )
        
        # 월간 비용 계산 (30일 기준)
        monthly_cost = total_hourly_cost * 24 * 30
        self.monthly_cost_label.config(text=f"${monthly_cost:,.2f}")
    
    def run_optimization(self):
        """비용 최적화를 실행합니다."""
        # 최적화 중 버튼 비활성화
        self.optimize_btn.config(state=tk.DISABLED, text="최적화 실행 중...")
        
        # 애니메이션을 위해 별도의 스레드에서 실행
        threading.Thread(target=self._optimize_servers, daemon=True).start()
    
    def _optimize_servers(self):
        """저사용 서버를 찾아 중지합니다."""
        # 1초 대기 (로딩 효과)
        time.sleep(1)
        
        # 저사용 서버 찾기 (CPU 사용률 10% 미만)
        low_usage_servers = [
            (i, server) for i, server in enumerate(self.servers) 
            if server.running and server.cpu_usage < 10
        ]
        
        if not low_usage_servers:
            self.root.after(0, self._show_optimization_result, 0, "최적화할 서버가 없습니다.")
            return
        
        # 저사용 서버 중지
        savings = 0
        for i, server in low_usage_servers:
            savings += server.cost_per_hour * 24 * 30  # 월간 절감액
            server.stop_server()
            
            # UI 업데이트
            self.root.after(0, self._update_server_ui, i, server)
        
        # 결과 표시
        self.root.after(0, self._show_optimization_result, savings, f"월 ${savings:,.2f} 절감 성공!")
    
    def _update_server_ui(self, index, server):
        """서버 UI를 업데이트합니다."""
        frame = self.server_frames[index]
        frame['cpu'].config(text=f"{server.cpu_usage:.1f}%")
        frame['status'].config(text="중지됨", foreground="red")
        frame['frame'].configure(style='Inactive.TFrame')
    
    def _show_optimization_result(self, savings, message):
        """최적화 결과를 표시합니다."""
        # 비용 표시 업데이트
        self.update_cost_display()
        
        # 결과 메시지 표시
        if savings > 0:
            self.saving_label.config(
                text=message,
                foreground="green",
                font=('Helvetica', 12, 'bold')
            )
        else:
            self.saving_label.config(
                text=message,
                foreground="orange"
            )
        
        # 버튼 상태 복원
        self.optimize_btn.config(state=tk.NORMAL, text="🔍 AI 비용 최적화 실행")

if __name__ == "__main__":
    root = tk.Tk()
    
    # 윈도우를 화면 중앙에 배치
    window_width = 1000
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    # 다크 테마 스타일 적용
    style = ttk.Style()
    style.theme_use('clam')
    
    # 배경색 설정
    style.configure('.', background='#2c3e50', foreground='white')
    style.configure('TFrame', background='#2c3e50')
    style.configure('TLabel', background='#2c3e50', foreground='white')
    style.configure('TButton', background='#3498db', foreground='white')
    style.configure('TLabelFrame', background='#34495e')
    style.configure('TLabelFrame.Label', background='#34495e', foreground='white')
    style.configure('TLabelframe', background='#34495e')
    
    # 비활성화된 프레임 스타일
    style.configure('Inactive.TFrame', background='#3d4f5e')
    
    # 애플리케이션 실행
    app = FinOpsDashboard(root)
    root.mainloop()

class LunchRoulette:
    def __init__(self, root):
        self.root = root
        self.root.title("점심 메뉴 추천 룰렛")
        self.root.geometry("600x500")
        self.root.configure(padx=30, pady=20, bg='#f0f0f0')
        
        # 데이터베이스 초기화
        database.create_table()
        
        # 애니메이션 관련 변수
        self.animation_running = False
        self.selected_category = tk.StringVar(value='all')
        
        # 스타일 설정
        self.setup_styles()
        
        # UI 생성
        self.create_widgets()
    
    def setup_styles(self):
        """위젯 스타일을 설정합니다."""
        style = ttk.Style()
        style.configure('TRadiobutton', font=('맑은 고딕', 12), background='#f0f0f0')
        style.configure('TButton', font=('맑은 고딕', 12, 'bold'))
        
    def create_widgets(self):
        """GUI 위젯들을 생성하고 배치합니다."""
        # 상단 프레임 - 카테고리 선택
        category_frame = ttk.LabelFrame(self.root, text="메뉴 카테고리", padding=10)
        category_frame.pack(fill="x", pady=(0, 20))
        
        # 라디오 버튼 생성 (데이터베이스와 일치하는 카테고리 값 사용)
        categories = [
            ('한식', '한식'),
            ('중식', '중식'),
            ('일식', '일식'),
            ('전체', 'all')
        ]
        
        for i, (text, value) in enumerate(categories):
            rb = ttk.Radiobutton(
                category_frame,
                text=text,
                value=value,
                variable=self.selected_category
            )
            rb.grid(row=0, column=i, padx=10, pady=5, ipadx=10, ipady=5)
        
        # 중앙 프레임 - 메뉴 표시
        menu_frame = ttk.Frame(self.root, style='Menu.TFrame')
        menu_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # 메뉴 표시 레이블 (가운데 정렬, 큰 글씨)
        self.menu_label = ttk.Label(
            menu_frame,
            text="메뉴를 추천해드릴게요! 🍽️",
            font=('맑은 고딕', 24, 'bold'),
            anchor='center',
            background='#ffffff',
            relief='solid',
            padding=20
        )
        self.menu_label.pack(fill="both", expand=True)
        
        # 하단 프레임 - 시작 버튼
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x")
        
        self.start_button = ttk.Button(
            button_frame,
            text="🍴 랜덤 추천 START! 🍴",
            command=self.start_roulette,
            style='Start.TButton'
        )
        self.start_button.pack(fill="x", pady=10)
        
        # 결과 표시 레이블 (가격 정보 등)
        self.result_label = ttk.Label(
            button_frame,
            text="",
            font=('맑은 고딕', 10),
            foreground='#666666'
        )
        self.result_label.pack()
    
    def start_roulette(self):
        """룰렛 애니메이션을 시작합니다."""
        if self.animation_running:
            return
            
        self.animation_running = True
        self.start_button.config(state='disabled')
        self.result_label.config(text="")
        
        # 애니메이션 스레드 시작
        threading.Thread(target=self.animate_roulette, daemon=True).start()
    
    def animate_roulette(self):
        """룰렛 애니메이션을 표시합니다."""
        start_time = time.time()
        duration = 2.0  # 2초간 애니메이션
        
        # 초기 딜레이 (0.1초 간격)
        interval = 0.05
        
        # 애니메이션 루프
        while time.time() - start_time < duration:
            if not self.animation_running:
                return
                
            try:
                # 랜덤 메뉴 선택 (카테고리 필터링 적용)
                selected_category = self.selected_category.get()
                menu = database.get_random_menu(selected_category)
                
                if menu:
                    name, category, price = menu
                    self.root.after(0, self.update_menu_display, name, category, price)
                else:
                    # 메뉴를 가져오지 못한 경우 기본 메시지 표시
                    self.root.after(0, self.menu_label.config, 
                                 {"text": "메뉴를 찾을 수 없습니다.", "foreground": "red"})
                    break
                
                # 점점 느려지게 하기
                interval = min(0.3, interval * 1.1)
                time.sleep(interval)
                
            except Exception as e:
                print(f"애니메이션 오류: {e}")
                break
        
        # 최종 메뉴 선택
        self.select_final_menu()
    
    def update_menu_display(self, name, category, price):
        """메뉴 표시를 업데이트합니다."""
        self.menu_label.config(text=name)
        self.result_label.config(text=f"{category} • {price:,}원")
    
    def select_final_menu(self):
        """최종 메뉴를 선택하고 결과를 표시합니다."""
        menu = database.get_random_menu(self.selected_category.get())
        if menu:
            name, category, price = menu
            self.menu_label.config(text=f"🎉 {name} 🎉", foreground='#e74c3c')
            self.result_label.config(text=f"🎊 오늘의 추천 메뉴는 {category} {name} ({price:,}원) 입니다! 🎊",
                                  font=('맑은 고딕', 12, 'bold'),
                                  foreground='#2c3e50')
        
        self.animation_running = False
        self.start_button.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    
    # 폰트 설정 (Windows용)
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        root.tk.call('tk', 'scaling', 1.5)  # 고해상도 디스플레이 대응
    except:
        pass
    
    # 애플리케이션 실행
    app = LunchRoulette(root)
    
    # 윈도우를 화면 중앙에 배치
    window_width = 600
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    # 창 크기 조절 방지
    root.resizable(False, False)
    
    # 메인 루프 시작
    root.mainloop()
