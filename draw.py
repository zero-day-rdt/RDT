import json

from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def graphing():
    filename = 'C:\projects\pythonProjects\cs305\\100K_c_l_10k (2).json'
    with open(filename) as f:
        reader = json.loads(f.read())
    BASE_RTT = [x['BASE-RTT'] for x in reader]
    RTT = [x['RTT'] for x in reader]
    WINDOW = [x['WINDOW']for x in reader]
    x_axis = [i for i in range(len(RTT))]
    # reader = csv.reader(f)
    # header_row = next(reader)

    # dates, culmulated_deaths, culmulated_discharged = [], [], []
    # for row in reader:
    #     try:
    #         current_date = datetime.strptime(row[0], "%Y/%m/%d")
    #         death = int(row[4])
    #         discharged = int(row[3])
    #     except ValueError:
    #         print(current_date, 'missing culmulated confirmed data')
    #     else:
    #         dates.append(current_date)
    #         culmulated_deaths.append(death)
    #         culmulated_discharged.append(discharged)
    # plt.bar(x_axis, height=WINDOW, label='单位时间发车间隔', width=0.5,
    #         facecolor='#9999ff', edgecolor='white')

    # plt.xlim((0, len(RTT)))
    # # plt.xticks()
    # plt.yticks(np.arange(0, 16, 2))

    # # y轴设置名称
    # plt.ylabel("单位时段发车间隔")
    # # 显示图例
    # plt.legend()
    # # 画折线图
    # plt.plot(x, y3, "r", ms=8, marker='*', label="理想发车次数")
    # # 在折线图上显示具体数值, ha参数控制水平对齐方式, va控制垂直对齐方式
    # for x1, yy in zip(x, y2):
    #     plt.text(x1, 4*yy + 0.2, str(yy), ha='center',
    #              va='bottom', fontsize=10, rotation=0)
    # plt.legend(loc="upper left")
    # plt.show()

    fig = plt.figure(dpi=120, figsize=(9, 6))
    plt.plot(x_axis, BASE_RTT, label='base RTT', c='#28A745')
    plt.plot(x_axis, RTT, label='RTT', c='#FFa3ef')

    # for a, b in zip(x_axis, BASE_RTT):
    #     plt.text(a, b, b, ha='center', va='bottom',
    #              fontsize='8', rotation='-45')
    # for a, b in zip(x_axis, RTT):
    #     plt.text(a, b, b, ha='center', va='top', fontsize='8', rotation='45')

    plt.title("Monitor RTT in Single Connection", fontsize=24)
    plt.xlabel('count', fontsize=16)
    plt.ylabel("Time/s", fontsize=16)
    # ax2 = plt.twinx()
    # ax2.plot(x_axis, WINDOW, label='Window size', c='red')
    # ax2.set_ylabel("Window size", fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.legend(loc='best')
    plt.show()
    # fig.savefig('culmulated_death_and_discharged_cases.png')


if __name__ == "__main__":
    graphing()
