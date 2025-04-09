#DOMINUS DEFENSE SYSTEM COPYRIGHT 2025

#Modules
import json
import math
import random
import os

#dictionary
list_of_objects = {"Ball": [0.200, 500,  0.1256, 0.47, 1],
                   "Car": [23000, 15000, 3.0, 0.5, 0],
                   "Train": [60000, 30000, 15, 0.8, 0]}
#constant variables
R_E = 6371
T = 0
P0 = 1.225

#function for max velocity
def max_velocity(m, cw, a, P,g):
    return math.sqrt((2*m*g) / (cw * P * a))

#function for air resistance
def air_resistance(vs, cw, a, P):
    return 0.5 * P * vs * cw * a

#function for dynamic air resistance
def dynamic_air_resistance(v, h):
    Th = 15-0.0065 * h
    Ch = 331.3 + 0.6 * Th
    return v/Ch

#height depending gravity force
def height_dep_gravity(h, g):
    return g*math.sqrt(R_E / (R_E + h))

#function for wind profile
def wind_profile(h, href, base_wind=0.1, k=0.01):
    return base_wind * (1+k*(h/href))

#Turbulence
def turbulence(P):
        return random.uniform(-0.02, 0.02) * P / P0

#function for gravity pull
def gravity(m, h, a, cw, e):

    #Timestamps and start of time
    t = T
    dt = 0.01

    # velocity at start (VAS)
    vy = 0

    #height at start (HAS)
    y = h

    #X-Velocity at start (XVAS)
    vx = 0

    #X at start (XAT)
    x = 0

    #Windforce at start (WFAS)
    Fwind = 0

    while y > 0:
        t += dt

        #Dynamic P-Stat
        P = P0 * math.exp(-y / 8000)

        #Mach-Count calculating
        M = dynamic_air_resistance(vy, y)
        if M < 0.8:
            CwM = cw
        elif 0.8 <= M <= 1.2:
            CwM = cw * (1 + 0.5 * (M - 0.8))
        elif M > 1.2:
            CwM = cw * (1.25 - 0.2 * (M - 1.2))

        #gravity_dep
        G = 9.81
        G_h = height_dep_gravity(y, G)

        Fdrag_x = air_resistance(vx, CwM, a, P)
        Fdrag_y = air_resistance(vy, CwM, a, P)

        #if t is a even number, the function random_wind() gets called for wind change
        if int(t) != int(t - dt):  # Only update when crossing into a new whole second
            if int(t) % 2 == 0:
                base_wind = wind_profile(y, h)
                Fwind = base_wind + turbulence(P)

        vx = vx + (Fwind + Fdrag_x) * dt
        vx = max(min(vx, 100), -100)  # Limit vx to [-100, 100] m/s

        # max velocity at end (MVAE)
        vmax = max_velocity(m,  CwM, a, P,G_h)

        #If vy reaches vmax it caps at vmax, if not it continues accelerating
        if vy < vmax:
            vy += (G_h - Fdrag_y/m) * dt

        elif vy >= vmax:
            vy = vmax

        # Change of X-Direction due to drag
        x += vx * dt
        y -= vy * dt

        if y < 0:
            vy = -e * vy  # Geschwindigkeit umkehren und Energieverlust berücksichtigen
            if abs(vy) < 0.1:  # Falls die Geschwindigkeit sehr klein wird, stoppen
                vy = 0
                y = 0
            else:
                y += vy * dt  # Bewegung nach dem Aufprall

        print(f"HEIGHT AT START: {h:.2f} |HEIGHT AT END: {y:.2f} | DRIFT: {x:.2f} | VELOCITY-Y: {vy:.2f} | VELOCITY-X: {vx:.2f} | TIME: {t:.2f}")
    result = f"HEIGHT AT START: {h:.2f} |HEIGHT AT END: {y:.2f} | DRIFT: {x:.2f} | VELOCITY-Y: {vy:.2f} | VELOCITY-X: {vx:.2f} | TIME: {t:.2f}"

    #saving the results
    try:
        with open("Log/Simulation_Log.json", "r", encoding="utf-8") as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        os.makedirs("Log", exist_ok=True)
        log = {}

    if key_list in log:
        log[key_list].append(result)
    else:
        log[key_list] = [result]

    with open("Log/Simulation_Log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)


#User interactive
print("Welcome to Gravitation! In here you can simulate different objects falling from the sky.")
while True:
    print("--------------------------------------------------------------")
    print(f"Please choose one of the given items: {list(list_of_objects)}")
    choice = input()
    key_list = next((key for key in list_of_objects if key.lower() == choice.lower().strip()), None)
    if key_list:
        m, h, a, cw, e = list_of_objects[key_list]
        print(f"You chose {key_list}")
        gravity(m, h, a, cw, e)

    elif choice.lower().strip() == "exit":
        break

    else:
        print("Invalid input given!")