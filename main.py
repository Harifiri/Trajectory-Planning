#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os
import time
import math
import logging
import numpy as np
from model import *
import pygame
from pygame.locals import *
from generate_flow import generateCarFlow
from hybirdAstar import HybirdAstar
from STA import GetSTAPoint, STA
from bezier import Bezier1


def FCFS_Policy(Time, Path):
    selected_index = -1
    min_time = sys.maxsize

    for index in range(len(Time)):
        if Time[index] < min_time and Path[index] == []:
            min_time = Time[index]
            selected_index = index

    return selected_index


def HVsFirst(Time, Path, Type):
    selected_index = -1
    min_time = sys.maxsize

    for index in range(len(Path)):
        if Time[index] < min_time and Path[index] == [] and Type[index] == 0:
            min_time = Time[index]
            selected_index = index

    return selected_index


def cps(para):  # change point size
    x, y = para
    x = x * 10 + w / 2
    y = -(y * 10) + h / 2
    return x, y


def drawText(screen, text, posx, posy, textHeight=32, fontColor=(0, 0, 0)):
    myfont = pygame.font.Font(None, textHeight)
    textSurfaceObj = myfont.render(text, True, fontColor)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (posx, posy)
    screen.blit(textSurfaceObj, textRectObj.center)


def process_bar(num, total, t):
    rate = float(num) / total
    ratenum = int(100 * rate)
    r = '\r[{}{}]{}%{}{}{}'.format('-' * ratenum, ' ' * (100 - ratenum), ratenum, '   The estimated time is',
                                   round(t * 0.02, 1), 's')
    sys.stdout.write(r)
    sys.stdout.flush()


def DrawBackground(screen, t):
    screen.fill((255, 255, 255))
    text = "time: " + str(round((t - start_time) * dt, 1)) + ' s'
    drawText(screen, text, 50, 50)
    color = [0, 0, 0]
    width = 2

    colorParam = [[0, 255, 0], [255, 255, 0], [255, 0, 0]]
    colorIndex = [2, 2, 2, 2]

    i = int(t / PhaseTime) % 4

    if t % PhaseTime < GreenTime:
        colorIndex[i] = 0
    else:
        colorIndex[i] = 1

    for i in range(len(SignleParam)):
        pygame.draw.polygon(screen, colorParam[colorIndex[i]], SignleParam[i], 0)
    for Param in RoundParam:
        pygame.draw.arc(screen, color, Param[0], Param[1], Param[2], width)
    for Param in LineParam:
        pygame.draw.line(screen, color, Param[0], Param[1], width)


def Show(Time, Path, Type, run_time):
    pygame.init()
    screen = pygame.display.set_mode((w, h))
    screen.fill((255, 255, 255))
    pygame.display.update()
    pygame.display.flip()

    lasttime = time.time()
    for t in np.arange(0, run_time + 1, 1):
        DrawBackground(screen, t)
        # screen.fill((255, 255, 255))
        # text = "time: " + str(round(t * dt, 1)) + ' s'
        # drawText(screen, text, 50, 50)
        # color = [0, 0, 0]
        # width = 2
        # draw background
        # for i in range(4):
        #     pygame.draw.arc(screen, color, RoundParam[i][0], RoundParam[i][1], RoundParam[i][2], width)
        # Phase = int((t%CircleTime)/PhaseTime)

        for index0 in range(len(Path)):
            if t < Time[index0] or t - Time[index0] >= len(Path[index0]):
                continue
            index1 = int(t - Time[index0])

            p_temp = Point2Pol1(Path[index0][index1][0], Path[index0][index1][1], Path[index0][index1][2])

            polygon = [cps(p_temp[0]), cps(p_temp[1]), cps(p_temp[2]), cps(p_temp[3])]

            # 绘制已出现的轨迹
            if index1 != 0:
                temp_line = []
                for i in range(index1 + 1):
                    temp_line.append((Path[index0][i][0] * 10 + w / 2, -Path[index0][i][1] * 10 + h / 2))
                if Type[index0] == 1:
                    pygame.draw.aalines(screen, [255, 0, 0], False, temp_line)
                else:
                    pygame.draw.aalines(screen, [0, 0, 255], False, temp_line)

            if Type[index0] == 1:
                pygame.draw.polygon(screen, [255, 0, 0], polygon, 0)
            else:
                pygame.draw.polygon(screen, [0, 0, 255], polygon, 0)

        pygame.display.update()
        pygame.display.flip()
        # 8 - loop through the events
        for event in pygame.event.get():
            # check if the event is the X button
            if event.type == pygame.QUIT:
                # if it is quit the game
                pygame.quit()
                exit(0)

        delta_time = 0.05 - (time.time() - lasttime)
        time.sleep(max(delta_time, 0))
        lasttime = time.time()

    screen.fill((255, 255, 255))
    pygame.display.update()
    pygame.display.flip()
    time.sleep(0)


def Debug1(Time, Path, Type, t):
    pygame.init()
    screen = pygame.display.set_mode((w, h))
    screen.fill((255, 255, 255))
    pygame.display.update()
    pygame.display.flip()

    screen.fill((255, 255, 255))
    pygame.display.update()
    pygame.display.flip()
    time.sleep(0)

    DrawBackground(screen, t)
    # screen.fill((255, 255, 255))
    # text = "time: " + str(round(t * dt, 1)) + ' s'
    # drawText(screen, text, 50, 50)
    # color = [0, 0, 0]
    # width = 2
    # draw background
    # for i in range(4):
    #     pygame.draw.arc(screen, color, RoundParam[i][0], RoundParam[i][1], RoundParam[i][2], width)
    # Phase = int((t%CircleTime)/PhaseTime)

    for index0 in range(len(Path)):
        if t < Time[index0] or t - Time[index0] >= len(Path[index0]):
            continue
        index1 = int(t - Time[index0])

        p_temp = Point2Pol1(Path[index0][index1][0], Path[index0][index1][1], Path[index0][index1][2])

        polygon = [cps(p_temp[0]), cps(p_temp[1]), cps(p_temp[2]), cps(p_temp[3])]

        # 绘制已出现的轨迹
        # if index1 != 0:
        #     temp_line = []
        #     for i in range(index1 + 1):
        #         temp_line.append((Path[index0][i][0]*10 + w/2, -Path[index0][i][1]*10 + h/2))
        #     if Type[index0] == 1:
        #         pygame.draw.aalines(screen, [255, 0, 0], False, temp_line)
        #     else:
        #         pygame.draw.aalines(screen, [0, 0, 255], False, temp_line)

        if Type[index0] == 1:
            pygame.draw.polygon(screen, [255, 0, 0], polygon, 0)
        else:
            pygame.draw.polygon(screen, [0, 0, 255], polygon, 0)

    pygame.display.update()
    pygame.display.flip()
    # 8 - loop through the events
    for event in pygame.event.get():
        # check if the event is the X button
        if event.type == pygame.QUIT:
            # if it is quit the game
            pygame.quit()
            exit(0)


def Simulate(qr, T, s, mtd, ratio):
    TimeInfo, CarInfo, TypeInfo = generateCarFlow(qr, T, s, mtd, ratio)
    # TimeInfo, CarInfo, TypeInfo = [481],[2],[1]
    # print(TimeInfo)
    # print(CarInfo)
    # print(TypeInfo)

    total = len(CarInfo)
    PathInfo = [[] for i in range(total)]

    run_time = 0
    planned_num = 0

    nums_All = 0
    nums_AVs = 0
    nums_HVs = 0
    TimeInfo1 = []
    for time in TimeInfo:
        TimeInfo1.append(time)
    Delay_HVs = []
    Delay_AVs = []
    Delay_All = []

    print('vehicle nums=', total)

    while planned_num < total:
        # if not HVsFinishFlag:
        #     car_index = HVsFirst(TimeInfo, PathInfo, TypeInfo)
        #     if car_index == -1:
        #         HVsFinishFlag = True
        #         continue
        # else:
        car_index = FCFS_Policy(TimeInfo, PathInfo)

        # print("planned:",planned_num)
        # print(TimeInfo[car_index],CarInfo[car_index])
        # if TimeInfo[car_index] == 508:
        #     Show(TimeInfo, PathInfo, TypeInfo, run_time)
        # Debug1(TimeInfo, PathInfo, TypeInfo, TimeInfo[car_index])
        if TypeInfo[car_index] == 0:
            path = STA(CarInfo[car_index], TimeInfo[car_index], PathInfo, TimeInfo)
        else:
            path = HybirdAstar(CarInfo[car_index], TimeInfo[car_index], PathInfo, TimeInfo, TypeInfo)

        if path == -1:
            TimeInfo[car_index] += 1
            continue

        # PathInfo[car_index] = path
        # print(len(path))
        PathInfo[car_index] = Bezier1(path, len(path) - 1)

        planned_num += 1
        temp_time = TimeInfo[car_index] + len(PathInfo[car_index])

        if TimeInfo[car_index] >= start_time:
            nums_All += 1
            if TypeInfo[car_index] == 0:
                nums_HVs += 1
                temp_delay = (temp_time - TimeInfo1[car_index] - minTime_HV[CarInfo[car_index] % 3]) * dt
                Delay_HVs.append(temp_delay)
                Delay_All.append(temp_delay)
            else:
                nums_AVs += 1
                temp_delay = (temp_time - TimeInfo1[car_index] - minTime_AV[CarInfo[car_index] % 3]) * dt
                Delay_AVs.append(temp_delay)
                Delay_All.append(temp_delay)

        if temp_time > run_time:
            run_time = temp_time
        process_bar(planned_num, total, run_time)

    # print('\r\n',len(CarInfo), 'vehicles passed the intersection in', str(run_time * dt), 'seconds')
    #
    # print(Delay_HVs)
    # print(Delay_AVs)

    # file_name = 's'+str(s)+'qr'+str(qr)+'ratio'+str(int(10*ratio))+'.txt'

    # AverageDelay_HVs = 0
    # AverageDelay_AVs = 0
    AverageDelay_All = 0
    # if len(Delay_HVs)!=0:
    #     AverageDelay_HVs = np.mean(Delay_HVs)
    # if len(Delay_AVs) != 0:
    #     AverageDelay_AVs = np.mean(Delay_AVs)
    if len(Delay_All) != 0:
        AverageDelay_All = np.mean(Delay_All)

    # file = open('/home/PJLAB/chihaifei/Desktop/Prj/result/'+file_name, 'a')
    # file.write(str(AverageDelay_HVs)+'\r\n')
    # file.write(str(AverageDelay_AVs)+'\r\n')
    # file.write(str(Delay_HVs) + '\r\n')
    # file.write(str(Delay_AVs) + '\r\n')
    # file.close()

    # Show(TimeInfo, PathInfo, TypeInfo, run_time)
    return AverageDelay_All


PATH = '/home/PJLAB/chihaifei/Desktop/Result/'

if __name__ == '__main__':
    # for s in range(10):
    #     for i in np.arange(100,2000+100,100):
    #         f = PATH+'s'+str(s)+'qr'+str(i)+'.txt'
    #         Data = np.zeros(11, dtype=float)
    #         np.savetxt(f, Data, fmt='%.3e', delimiter=",")

    GetSTAPoint()

    qr = 100  # car flow (veh/h)
    T = 150 + start_time * dt  # amount of simulation time
    s = 0  # random seed
    mtd = 1  # minimum time headway
    ratio = 0.5  # ratio of AVs


    for s in range(10):
        for qr in np.arrage(100,1500+100,100):
            for ratio in range(10+1):
                file_name = PATH + 's' + str(s) + 'qr' + str(qr) + '.txt'
                Data = np.loadtxt(file_name, delimiter=",")
                if Data[ratio]<0.00001:
                    print('\r\n', "----", 's =', str(s), '  qr =', str(qr), '  ratio =', str(round(ratio, 2)),
                          "------------")
                    Data[ratio] = Simulate(qr, T, s, mtd, ratio / 10)
                else:
                    continue
                np.savetxt(file_name, Data, fmt='%.3e', delimiter=",")
                print('\r\n', "----", 's =', str(s), '  qr =', str(qr), '  ratio =', str(round(ratio, 2)),
                      "------------")




