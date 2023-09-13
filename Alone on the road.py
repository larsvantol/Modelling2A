import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from scipy.stats import norm, gamma, lognorm


x0 = 0
spMean = 100/3.6 # m/s
spStd_ind = 2/3.6 # m/s
spStd_dep = 1/3.6
roadLength = 5e3 # m

dt = 1 # s

def independent(spMean, spStd):
    xs = [x0]
    while xs[-1] < 5e3:
        v = np.random.normal(spMean, spStd)
        while v < 0:
            v = np.random.normal(spMean, spStd)
        xNew = xs[-1] + dt*v
        xs.append(xNew)
    final_step = (roadLength - xs[-2]) / v
    T = (len(xs)-2)*dt + final_step
    return np.array(xs), T


# def dependent(spMean, spStd0, spStd):
#     v = np.random.normal(spMean, spStd0)
#     while v < 0:
#         v = np.random.normal(spMean, spStd0)
#     xs = [x0, x0+dt*v]
#     while xs[-1] < 5e3:
#         while True:
#             v = np.random.normal(v, spStd)
#             if v > 0:
#                 break
#         xNew = xs[-1] + dt*v
#         xs.append(xNew)
#     final_step = (roadLength - xs[-2]) / v
#     T = (len(xs)-2)*dt + final_step
#     return np.array(xs), T


def dependent(spMean, spStd0, spStd):
    while True:
        v = np.random.normal(spMean, spStd0)
        xs = [x0, x0+dt*v]
        while xs[-1] < 5e3:
            v = np.random.normal(v, spStd)
            if v < 0:  # Check if speed is negative
                break  # Exit the inner loop
            xNew = xs[-1] + dt*v
            xs.append(xNew)
        else:  # This block executes if the inner loop completed normally (i.e., no negative speed was encountered)
            final_step = (roadLength - xs[-2]) / v
            T = (len(xs)-2)*dt + final_step
            return np.array(xs), T  # Return results and exit the infinite loop

# def random_walk(spMean, spStd0, spStd):
#     v = np.random.normal(spMean, spStd0)
#     xs = [x0, x0+dt*v]
#     while xs[-1] < 5e3:
#         v += np.random.normal(0, spStd)
#         while v < 0:
#             v = np.random.normal(0, spStd)
#         xNew = xs[-1] + dt*v
#         xs.append(xNew)
#     final_step = (roadLength - xs[-2]) / v
#     T = (len(xs)-2)*dt + final_step
#     return np.array(xs), T

def random_walk(spMean, spStd0, spStd):
    while True:  # Start an infinite loop
        v = np.random.normal(spMean, spStd0)
        xs = [x0, x0+dt*v]
        while xs[-1] < 5e3:
            v += np.random.normal(0, spStd)
            if v < 0:  # Check if speed is negative
                break  # Exit the inner loop
            xNew = xs[-1] + dt*v
            xs.append(xNew)
        else:  # This block executes if the inner loop completed normally (i.e., no negative speed was encountered)
            final_step = (roadLength - xs[-2]) / v
            T = (len(xs)-2)*dt + final_step
            return np.array(xs), T  # Return results and exit the infinite loop

xsInd, T_ind = independent(spMean, spStd_ind)
xsDep, T_dep = dependent(spMean, spStd_ind, spStd_dep)
xsRnd, T_rnd = random_walk(spMean, spStd_ind, spStd_dep)


def animateCar(fig, ax, xs):
    
    road = patches.Rectangle((0, -0.5), 5e3, 1, fc='gray')
    car = patches.Rectangle((0, -0.1), 500, 0.2, fc='lightblue') # Adjusted size

    ax.add_patch(road)
    ax.add_patch(car)
    ax.set_xlim(0, 5e3)
    ax.set_ylim(-1, 1)
    ax.get_yaxis().set_visible(False)

    def animate(i):
        car.set_x(xsInd[i])

    ani = FuncAnimation(fig, animate, frames=len(xsInd), interval=dt*100)
    return ani
    
# fig, ax = plt.subplots()
# ani = animateCar(fig, ax, xsRnd)
# plt.show()

def Tdistr(N, func, *args):
    Ts = []
    for i in range(N):
        #if i%500: print(f"LOOP {i}")
        Ts.append(func(*args)[-1])
    return np.array(Ts)

# independent
# Ts = Tdistr(10000, independent, spMean, spStd_ind)

# T_meanEst = roadLength/spMean
# T_stdEst = np.sqrt(np.sum((Ts-T_meanEst)**2)/(len(Ts)-1))

# x = np.linspace(min(Ts), max(Ts), 100)
# y = norm.pdf(x, T_meanEst, T_stdEst)

# plt.hist(Ts, bins=50, color='blue', edgecolor='black', density=True)
# plt.plot(x, y, color='red')

# plt.title("Distribution of Travel Times")
# plt.xlabel("Travel Time (s)")
# plt.ylabel("Density")

# plt.show()

# dependent
# Ts = Tdistr(30000, dependent, spMean/3, spStd_ind, spStd_dep)

# alpha1, loc1, beta1= gamma.fit(Ts, floc = 0)
# sigma2, loc2, scale2 = lognorm.fit(Ts, floc=0)
# print(alpha1, beta1)

# x = np.linspace(min(Ts), max(Ts), 100)
# y1 = gamma.pdf(x, alpha1, loc1, beta1)
# y2 = lognorm.pdf(x, sigma2, loc2, scale2)

# plt.hist(Ts, bins=50, color='blue', edgecolor='black', density=True)
# plt.plot(x, y1, color='red', label = "gamma")
# plt.plot(x, y2, color='tab:blue', label = "lognormal")

# plt.title("Distribution of Travel Times")
# plt.xlabel("Travel Time (s)")
# plt.ylabel("Density")
# plt.legend()

# plt.show()

# random walk 
# Ts = Tdistr(10000, random_walk, spMean, spStd_ind, spStd_dep)

# alpha1, loc1, beta1= gamma.fit(Ts, floc = 0)
# sigma2, loc2, scale2 = lognorm.fit(Ts, floc=0)

# x = np.linspace(min(Ts), max(Ts), 100)
# y1 = gamma.pdf(x, alpha1, loc1, beta1)
# y2 = lognorm.pdf(x, sigma2, loc2, scale2)

# plt.hist(Ts, bins=50, color='blue', edgecolor='black', density=True)
# plt.plot(x, y1, color='red', label = "gamma")
# plt.plot(x, y2, color='tab:blue', label = "lognormal")

# plt.title("Distribution of Travel Times")
# plt.xlabel("Travel Time (s)")
# plt.ylabel("Density")
# plt.legend()

# plt.show()



    

