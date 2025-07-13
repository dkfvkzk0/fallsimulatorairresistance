import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 도시별 공기 밀도 (고도 10km 기준, 단위: kg/m^3)
city_air_density = {
    "Seoul": 0.4135,
    "Busan": 0.4120,
    "Daegu": 0.4140,
    "Incheon": 0.4115,
    "Gwangju": 0.4130,
    "Daejeon": 0.4125,
    "Ulsan": 0.4145
}

GRAVITY = 9.8
DRAG_COEFF = 0.47  # 구의 항력 계수

def air_resistance_model(t, v, g, k, mass):
    return g - (k / mass) * v

def air_resistance_model_squared(t, v, g, k, mass):
    return g - (k / mass) * v**2

def simulate(city, model, area, mass=1.0, t_max=100, n_points=1000):
    rho = city_air_density[city]
    k = 0.5 * rho * area * DRAG_COEFF

    times = np.linspace(0, t_max, n_points)
    init_v = [0.0]
    if model == 'linear':
        sol = solve_ivp(air_resistance_model, (0, t_max), init_v,
                        args=(GRAVITY, k, mass), t_eval=times)
    else:
        sol = solve_ivp(air_resistance_model_squared, (0, t_max), init_v,
                        args=(GRAVITY, k, mass), t_eval=times)
    return sol.t, sol.y[0]

def plot_with_energy(times, velocities, mass=1.0, h0=100.0):

    # 높이 변화: h(t) = h0 - ∫v dt
    dt = times[1] - times[0]
    heights = h0 - np.cumsum(velocities) * dt

    # 에너지 계산
    U = mass * GRAVITY * heights              # 위치에너지
    K = 0.5 * mass * velocities**2            # 운동에너지
    E = U + K                                  # 총 에너지

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

    # 속도–시간
    ax1.plot(times, velocities, label='속도 v(t)', color='blue')
    ax1.axhline(velocities[-1], linestyle='--', color='red', label='종단 속도')
    ax1.set_ylabel('속도 (m/s)')
    ax1.legend()
    ax1.grid(True)

    # 에너지–시간
    ax2.plot(times, U, label='위치에너지 E_p(t)', color='green')
    ax2.plot(times, K, label='운동에너지 E_k(t)', color='orange')
    ax2.plot(times, E, label='총에너지 E(t)', color='purple')
    ax2.set_xlabel('시간 (s)')
    ax2.set_ylabel('에너지 (J)')
    ax2.legend()
    ax2.grid(True)

    fig.suptitle('자유 낙하 운동의 속도 및 에너지 변화')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

def run_simulation():
    city = city_var.get()
    model = model_var.get()
    area_str = entry_area.get()
    try:
        area = float(area_str)
        if area <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("입력 오류", "단면적에 양수를 입력하세요.")
        return

    try:
        t, v = simulate(city, model, area)
        plot_with_energy(t, v)
    except Exception as e:
        messagebox.showerror("시뮬레이션 오류", str(e))

# --- GUI 구성 ---
root = tk.Tk()
root.title("공기 저항을 적용한 자유 낙하 운동 시뮬레이터")
root.geometry("400x220")
root.resizable(False, False)

# 도시 선택
tk.Label(root, text="도시").grid(row=0, column=0, padx=10, pady=8, sticky='e')
city_var = tk.StringVar(value="Seoul")
ttk.Combobox(root, textvariable=city_var, values=list(city_air_density.keys()), state="readonly")\
    .grid(row=0, column=1, padx=10, pady=8)

# 모델 선택
tk.Label(root, text="항력 모델").grid(row=1, column=0, padx=10, pady=8, sticky='e')
model_var = tk.StringVar(value="linear")
ttk.Combobox(root, textvariable=model_var, values=["linear", "quadratic"], state="readonly")\
    .grid(row=1, column=1, padx=10, pady=8)

# 구의 단면적 입력
tk.Label(root, text="단면적 (m²)").grid(row=2, column=0, padx=10, pady=8, sticky='e')
entry_area = tk.Entry(root)
entry_area.grid(row=2, column=1, padx=10, pady=8)

# 실행 버튼
tk.Button(root, text="실행", command=run_simulation)\
    .grid(row=3, column=0, columnspan=2, pady=20)

root.mainloop()

