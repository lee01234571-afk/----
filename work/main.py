import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
from datetime import datetime

class Server:
    def __init__(self, name, cpu_usage, cost_per_hour):
        self.name = name
        self.cpu_usage = cpu_usage
        self.cost_per_hour = cost_per_hour
        self.running = True
        self.last_updated = datetime.now().strftime("%H:%M:%S")
    
    def update_usage(self):
        """서버 사용량을 업데이트합니다."""
        # 서버가 실행 중일 때만 업데이트
        if self.running:
            # 현재 CPU 사용률을 기반으로 약간의 변동을 줌
            if self.cpu_usage < 5:  # 저부하 서버는 1-10% 사이에서 변동
                self.cpu_usage = random.uniform(1, 10)
            else:  # 일반 서버는 5-30% 사이에서 변동
                self.cpu_usage = random.uniform(5, 30)
            self.last_updated = datetime.now().strftime("%H:%M:%S")
    
    def stop_server(self):
        """서버를 중지합니다."""
        if self.running:  # 실행 중인 서버만 중지
            self.running = False
            self.cpu_usage = 0
            self.last_updated = datetime.now().strftime("%H:%M:%S")
            return True
        return False
        
    def start_server(self):
        """서버를 시작합니다."""
        if not self.running:  # 중지된 서버만 시작
            self.running = True
            self.cpu_usage = random.uniform(1, 10)  # 시작 시 저부하 상태로 시작
            self.last_updated = datetime.now().strftime("%H:%M:%S")
            return True
        return False

class FinOpsDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("FinOps Cloud Cost Optimizer")
        self.root.geometry("1000x600")
        self.root.configure(bg='#2c3e50')
        
        # 서버 데이터 초기화
        self.servers = [
            Server(f"Server-{i+1}", 
                  random.uniform(5, 15) if i >= 2 else random.uniform(1, 5),  # 처음 2개는 저사용 서버 (1-5%)
                  random.uniform(5, 15))  # 시간당 $5~15 비용
            for i in range(5)
        ]
        
        # UI 초기화
        self.setup_ui()
        
        # 5초마다 서버 상태 업데이트
        self.update_server_status()
    
    def setup_ui(self):
        """UI 컴포넌트들을 설정합니다."""
        # 메인 프레임
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목 라벨
        title_label = ttk.Label(
            self.main_frame, 
            text="클라우드 비용 최적화 대시보드",
            font=('Helvetica', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 왼쪽 프레임 (서버 목록)
        self.left_frame = ttk.LabelFrame(self.main_frame, text="서버 상태 모니터링", padding=10)
        self.left_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # 서버 상태 표시를 위한 Treeview
        self.tree = ttk.Treeview(
            self.left_frame, 
            columns=('name', 'cpu', 'cost', 'status', 'last_updated'),
            show='headings',
            height=5
        )
        
        # 컬럼 설정
        self.tree.heading('name', text='서버명')
        self.tree.heading('cpu', text='CPU 사용률 (%)')
        self.tree.heading('cost', text='시간당 비용 ($)')
        self.tree.heading('status', text='상태')
        self.tree.heading('last_updated', text='마지막 업데이트')
        
        # 컬럼 너비 설정
        self.tree.column('name', width=100)
        self.tree.column('cpu', width=100, anchor=tk.CENTER)
        self.tree.column('cost', width=100, anchor=tk.CENTER)
        self.tree.column('status', width=100, anchor=tk.CENTER)
        self.tree.column('last_updated', width=150, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 오른쪽 프레임 (비용 정보)
        self.right_frame = ttk.LabelFrame(self.main_frame, text="비용 분석", padding=10)
        self.right_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # 현재 월간 예상 비용
        self.monthly_cost_label = ttk.Label(
            self.right_frame, 
            text="현재 예상 월 청구액",
            font=('Helvetica', 10)
        )
        self.monthly_cost_label.pack(pady=(10, 5))
        
        self.cost_value = tk.StringVar()
        self.cost_display = ttk.Label(
            self.right_frame, 
            textvariable=self.cost_value,
            font=('Helvetica', 24, 'bold'),
            foreground='red'
        )
        self.cost_display.pack(pady=(0, 20))
        
        # AI 최적화 결과 메시지
        self.optimization_result = tk.StringVar()
        self.optimization_label = ttk.Label(
            self.right_frame, 
            textvariable=self.optimization_result,
            font=('Helvetica', 10),
            foreground='green'
        )
        self.optimization_label.pack(pady=10)
        
        # 버튼 프레임
        button_frame = ttk.Frame(self.right_frame)
        button_frame.pack(pady=10, fill=tk.X)
        
        # AI 비용 최적화 버튼
        self.optimize_btn = ttk.Button(
            button_frame,
            text="AI 비용 최적화 실행",
            command=self.start_optimization,
            style='Accent.TButton'
        )
        self.optimize_btn.pack(side=tk.LEFT, expand=True, padx=5, pady=5, fill=tk.X)
        
        # 서버 재시작 버튼
        self.restart_btn = ttk.Button(
            button_frame,
            text="서버 재시작",
            command=self.start_all_servers,
            style='Success.TButton'
        )
        self.restart_btn.pack(side=tk.RIGHT, expand=True, padx=5, pady=5, fill=tk.X)
        
        # 그리드 가중치 설정
        self.main_frame.columnconfigure(0, weight=2)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # 스타일 설정
        self.setup_styles()
        
        # 초기 서버 상태 업데이트
        self.update_server_display()
    
    def setup_styles(self):
        """위젯 스타일을 설정합니다."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 기본 스타일 설정
        style.configure('.', 
                      background='#2c3e50', 
                      foreground='white',
                      font=('Helvetica', 10))
        
        # 프레임 스타일
        style.configure('TFrame', background='#2c3e50')
        
        # 라벨 스타일
        style.configure('TLabel', 
                      background='#2c3e50', 
                      foreground='white')
        
        # 라벨프레임 스타일
        style.configure('TLabelframe', 
                      background='#2c3e50', 
                      foreground='white')
        style.configure('TLabelframe.Label', 
                      background='#2c3e50', 
                      foreground='white')
        
        # 버튼 스타일
        style.configure('TButton', 
                      background='#3498db', 
                      foreground='white',
                      font=('Helvetica', 10, 'bold'))
        style.map('TButton',
                background=[('active', '#2980b9')],
                foreground=[('active', 'white')])
        
        # 버튼 스타일
        style.configure('Accent.TButton', 
                      font=('Helvetica', 11, 'bold'),
                      background='#e74c3c',  # 빨간색
                      foreground='white')
        style.map('Accent.TButton',
                background=[('active', '#c0392b')],
                foreground=[('active', 'white')])
                
        style.configure('Success.TButton',
                      font=('Helvetica', 11, 'bold'),
                      background='#2ecc71',  # 초록색
                      foreground='white')
        style.map('Success.TButton',
                background=[('active', '#27ae60')],
                foreground=[('active', 'white')])
        
        # Treeview 스타일
        style.configure('Treeview', 
                      fieldbackground='#34495e',
                      background='#34495e',
                      foreground='white',
                      rowheight=30,
                      font=('Helvetica', 10))
        style.configure('Treeview.Heading', 
                      background='#2c3e50',
                      foreground='white',
                      font=('Helvetica', 10, 'bold'))
        style.map('Treeview', 
                background=[('selected', '#3498db')],
                foreground=[('selected', 'white')])
    
    def update_server_status(self):
        """서버 상태를 주기적으로 업데이트합니다."""
        for server in self.servers:
            if server.running:
                server.update_usage()
        
        self.update_server_display()
        
        # 5초마다 업데이트
        self.root.after(5000, self.update_server_status)
    
    def update_server_display(self):
        """서버 상태를 화면에 표시합니다."""
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 서버 상태 업데이트
        total_cost = 0
        for server in self.servers:
            status = "실행 중" if server.running else "중지됨"
            self.tree.insert('', 'end', values=(
                server.name,
                f"{server.cpu_usage:.1f}%",
                f"${server.cost_per_hour:.2f}",
                status,
                server.last_updated
            ))
            
            if server.running:
                total_cost += server.cost_per_hour
        
        # 월간 예상 비용 업데이트 (30일 기준)
        monthly_cost = total_cost * 24 * 30
        self.cost_value.set(f"${monthly_cost:,.2f}")
    
    def start_optimization(self):
        """AI 비용 최적화를 시작합니다."""
        # 버튼 비활성화
        self.optimize_btn['state'] = 'disabled'
        self.optimization_result.set("AI가 서버를 분석 중입니다...")
        
        # 별도 스레드에서 최적화 실행
        threading.Thread(target=self.optimize_costs, daemon=True).start()
    
    def start_all_servers(self):
        """중지된 모든 서버를 재시작합니다."""
        started_servers = []
        
        for server in self.servers:
            if server.start_server():
                started_servers.append(server.name)
        
        self.update_server_display()
        
        if started_servers:
            message = f"{len(started_servers)}개의 서버를 재시작했습니다."
            self.optimization_result.set(message)
            messagebox.showinfo("서버 재시작 완료", 
                              f"{len(started_servers)}개의 서버가 재시작되었습니다.")
        else:
            self.optimization_result.set("재시작할 서버가 없습니다.")
    
    def optimize_costs(self):
        """저사용 서버를 식별하고 중지합니다."""
        # 시뮬레이션을 위한 딜레이
        time.sleep(2)
        
        # 1. 현재 실행 중인 서버 수 확인
        running_servers = [s for s in self.servers if s.running]
        
        # 최소 1개의 서버는 항상 실행되도록 유지
        if len(running_servers) <= 1:
            self.optimization_result.set("최소 1개 이상의 서버가 필요합니다.")
            self.optimize_btn['state'] = 'normal'
            return
        
        # 2. CPU 사용률이 10% 미만이고, 비용이 가장 높은 서버 1개만 중지
        target_server = None
        max_cost = 0
        
        for server in running_servers:
            if server.cpu_usage < 10 and server.cost_per_hour > max_cost:
                target_server = server
                max_cost = server.cost_per_hour
        
        # 3. 서버 중지 및 결과 처리
        if target_server and target_server.stop_server():
            monthly_savings = target_server.cost_per_hour * 24 * 30
            message = f"서버 '{target_server.name}'을(를) 중지했습니다.\n"
            message += f"월간 예상 절감액: ${monthly_savings:,.2f}"
            
            self.optimization_result.set(message)
            messagebox.showinfo("최적화 완료", 
                              f"서버 '{target_server.name}'이(가) 중지되었습니다.\n"
                              f"월간 예상 절감액: ${monthly_savings:,.2f}")
        else:
            self.optimization_result.set("최적화할 서버가 없습니다.")
        
        self.update_server_display()
        
        # UI 업데이트
        self.root.after(0, self.update_server_display)
        
        # 결과 메시지 표시
        if stopped_servers:
            message = f"성공적으로 {len(stopped_servers)}개의 서버를 중지했습니다.\n"
            message += f"월간 예상 절감액: ${total_savings:,.2f}"
            
            self.root.after(0, lambda: self.optimization_result.set(message))
            self.root.after(0, lambda: messagebox.showinfo("최적화 완료", 
                f"{len(stopped_servers)}개의 저사용 서버가 중지되었습니다.\n"
                f"월간 예상 절감액: ${total_savings:,.2f}"))
        else:
            self.root.after(0, lambda: self.optimization_result.set(
                "최적화가 필요 없는 서버 상태입니다."))
        
        # 버튼 다시 활성화
        self.root.after(0, lambda: self.optimize_btn.configure(state='normal'))

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
    
    # 스타일 초기화
    
    # 애플리케이션 실행
    app = FinOpsDashboard(root)
    root.mainloop()
