import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False


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
DRAG_COEFF = 0.47

# 속도에 비례
def air_resistance_model(t, v, g, k, mass):
    return g - (k / mass) * v

# 속도의 제곱에 비례
def air_resistance_model_squared(t, v, g, k, mass):
    return g - (k / mass) * v ** 2


def simulate(city, model, sphere_area, time_span=(0, 100), num_points=1000):

    if city not in city_air_density:
        raise ValueError(f"'{city}' 는 주어진 도시가 아닙니다.")
    air_density = city_air_density[city]

    # 공기 저항 계수 k 계산
    k = 0.5 * air_density * sphere_area * DRAG_COEFF

    initial_velocity = 0
    times = np.linspace(time_span[0], time_span[1], num_points)

    # 모델 선택
    if model == 'linear':
        sol = solve_ivp(
            air_resistance_model, time_span, [initial_velocity],
            args=(GRAVITY, k, 1.0), t_eval=times
        )
    elif model == 'quadratic':
        sol = solve_ivp(
            air_resistance_model_squared, time_span, [initial_velocity],
            args=(GRAVITY, k, 1.0), t_eval=times
        )
    else:
        raise ValueError("모델은 반드시 'linear' 또는 'quadratic'이어야 합니다.")

    return sol.t, sol.y[0]


def plot_results(times, velocities, city, model):
    plt.figure(figsize=(10, 6))
    plt.plot(times, velocities, label="속도(m/s)", color='blue')
    plt.axhline(y=velocities[-1], color='red', linestyle='--', label="종단 속도")
    plt.title(f"{city} 내 공기 저항을 적용한 자유 낙하 운동의 v-t 그래프(공기 저항 모델 : {'Linear' if model == 'linear' else 'Quadratic'})")
    plt.xlabel("t(초)")
    plt.ylabel("v(m/s)")
    plt.legend()
    plt.grid(True)
    plt.show()


def run_simulation():
    city = city_var.get()
    model = model_var.get()
    area_input = entry_area.get()

    try:
        sphere_area = float(area_input)
        if sphere_area <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("입력 오류", "정확한 값을 입력하십시요.")
        return

    try:
        times, velocities = simulate(city, model, sphere_area)
        plot_results(times, velocities, city, model)
    except Exception as e:
        messagebox.showerror("시뮬레이션 오류", str(e))


# GUI
root = tk.Tk()
root.title("공기 저항을 적용한 자유 낙하 운동 시뮬레이터")
root.geometry("400x250")  # Set fixed window size (width x height)
root.resizable(False, False)  # Prevent resizing

tk.Label(root, text="도시").grid(row=0, column=0, padx=10, pady=10)
city_var = tk.StringVar(value="Seoul")
city_menu = ttk.Combobox(root, textvariable=city_var, values=list(city_air_density.keys()), state="readonly")
city_menu.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="공기 저항 모델").grid(row=1, column=0, padx=10, pady=10)
model_var = tk.StringVar(value="linear")
model_menu = ttk.Combobox(root, textvariable=model_var, values=["linear", "quadratic"], state="readonly")
model_menu.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="구의 단면적").grid(row=2, column=0, padx=10, pady=10)
entry_area = tk.Entry(root)
entry_area.grid(row=2, column=1, padx=10, pady=10)

run_button = tk.Button(root, text="실행", command=run_simulation)
run_button.grid(row=3, column=0, columnspan=2, pady=20)

root.mainloop()
