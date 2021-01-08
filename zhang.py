import shutil
import time
from copy import deepcopy
import os
from PIL import Image, ImageFont, ImageDraw
from numpy import *
import numpy as np
import paddlehub as hub
import re
import json
import scipy.io as sio
import sys
import cv2 as cv
from ESRGAN import test

PATH_SHARE = os.path.abspath(os.path.dirname(__file__)) + "\\"
FLAG = True
PATH_R0 = os.path.abspath(os.path.dirname(__file__)) + "\\zhang\\"  # 数据地址
PATH_R1 = PATH_R0 + 'Ship_name_database\\'  # 船原始数据库地址
PATH_W1 = PATH_R0 + 'Ship_regularizedname_database\\'  # 船规则名称数据库地址
PATH_W2 = PATH_R0 + 'Ship_number_database\\'  # 船编号数据库地址
PATH_W3 = PATH_R0 + 'Ship_preProcess_database\\'  # 预处理结果数据库地址

# 工具函数
if (1 == 1):
    '''*************************************************************************************'''
    '''函数功能: 整行文字投影检验                                                                '''
    '''入参:             image：待检验图像                                                     '''
    '''出参:                                                                                 '''
    '''返回值:           True,division:检验出多行以及分割坐标数组                                  '''
    '''                 False,division:未检验出多行                                            '''
    '''*************************************************************************************'''
    # 整行文字投影检验
    def detect_rows_full(image):
        img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        bigNumber = 2  # 高度拉伸倍数
        height, width = img.shape[:2]
        resized_img = cv.resize(img, (width, bigNumber * height), interpolation=cv.INTER_LINEAR)
        # 二值化
        (_, thresh) = cv.threshold(resized_img, 150, 255, cv.THRESH_BINARY)
        # 扩大黑色面积，使效果更明显
        kernel1 = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
        kernel2 = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
        handled = cv.erode(thresh, kernel1, iterations=1)  # 先腐蚀
        handled = cv.dilate(thresh, kernel2, iterations=1)  # 再膨胀
        # cv.imshow("img", handled)
        # cv.waitKey(0)
        height, width = handled.shape[:2]
        # 记录每个y坐标遇到的有值的像素点的数量
        z = [0] * height

        # 水平投影并统计每一行的黑点数
        a = 0
        for y in range(0, height):
            for x in range(0, width):
                if handled[y, x] == 255:
                    a = a + 1
                else:
                    continue
            z[y] = a
            a = 0
        print("full ")
        print(z)
        begin = False
        lastH = 0
        h_list = []
        division = []
        for y in range(0, height):
            if (z[y] > 0):
                begin = True
            elif (begin):
                h_list.append(y - lastH)
                lastH = y
                division.append(y)
                begin = False
        if (z[height - 1] > 0):
            h_list.append(height - lastH)

        if (len(h_list) > 1):
            return True, division
        else:
            return False, division

    '''*************************************************************************************'''
    '''函数功能: 图片文本倾斜矫正                                                                '''
    '''入参:             image：待矫正图像                                                     '''
    '''出参:                                                                                 '''
    '''返回值:           rotated:经过仿射变换后矫正的图像                                         '''
    '''*************************************************************************************'''
    # 图片文本倾斜矫正
    def rotate_img(image):
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        gray = cv.bitwise_not(gray)  # 将图片转成白字黑底
        thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)[1]  # 将字都转成255，背景转成0
        # 探索所有像素值大于0的坐标，使用坐标来计算包含所有这些坐标的旋转边框
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv.minAreaRect(coords)[-1]  # 该函数返回[-90, 0]的角度
        # 对角度进行处理
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        # 进行旋转
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv.warpAffine(image, M, (w, h), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)
        return rotated
    '''*************************************************************************************'''
    '''函数功能: 锐化图像                                                                      '''
    '''入参:             image：待锐化图像                                                     '''
    '''出参:                                                                                 '''
    '''返回值:           dst:锐化后的图像                                                       '''
    '''*************************************************************************************'''
    # 锐化
    def sharpen(image):
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32)  # 定义一个核
        dst = cv.filter2D(image, -1, kernel=kernel)
        return dst


    '''*************************************************************************************'''
    '''函数功能: 检测图片是否包含多行文字                                                                      '''
    '''入参:             image：待检测图像                                                     '''
    '''出参:                                                                                 '''
    '''返回值:           image:待检测图像, cut_imgs:切割后的图像                                                      '''
    '''*************************************************************************************'''
    def detect_divite_multi_row(image):
        rotated = rotate_img(image)
        cut_imgs = []
        # 判断多行
        is_multi, division = detect_rows_full(rotated)

        if (is_multi):
            print("检测到多行文本,执行归一化处理...")
            last_h = 0
            for i, line in enumerate(division):
                # 分割多行
                print(str(i) + " " + str(line))
                cutImg = rotated[last_h:line]
                cut_imgs.append(cutImg)
                last_h = line
            cutImg = rotated[last_h:rotated.shape[0]]
            cut_imgs.append(cutImg)

        return image,cut_imgs

    '''*************************************************************************************'''
    '''函数功能: 将图像数据解码为图像                                                             '''
    '''入参:             file_path：待解码图像数据的路径                                         '''
    '''出参:                                                                                 '''
    '''返回值:           cv_img:解码后的图像                                                    '''
    '''*************************************************************************************'''
    def cv_imread(file_path):
        cv_img = cv.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
        return cv_img

    '''*************************************************************************************'''
    '''函数功能: 将图像编码为流数据保存                                                           '''
    '''入参:             path：保存路径                                                        '''
    '''                 img：待编码图像                                                        '''
    '''出参:                                                                                 '''
    '''返回值:                                                                               '''
    '''*************************************************************************************'''
    def cv_imwrite(path,img):
        suffix = os.path.splitext(path)[-1]
        cv.imencode(suffix, img)[1].tofile(path)


    '''*************************************************************************************'''
    '''函数功能: 对目标进行深拷贝                                                                '''
    '''入参:             Objects:待拷贝目标                                                    '''
    '''出参:                                                                                 '''
    '''返回值:           objects:深拷贝后的副本                                                 '''
    '''*************************************************************************************'''
    def DeepCopy(Objects):  # 深拷贝
        # 功能：对目标进行深拷贝
        # 版本：python3.7 原型
        objects = deepcopy(Objects)

        return objects

    '''*************************************************************************************'''
    '''函数功能: 将一维列表，二维列表写到txt                                                      '''
    '''入参:             Lists:列表                                                          '''
    '''                 Txt_path_and_name:文本路径与名                                        '''
    '''                 Spacer:间隔符                                                        '''
    '''                 Mode:模式                                                            '''
    '''出参:                                                                                 '''
    '''返回值:                                                                               '''
    '''*************************************************************************************'''
    def lists_to_txt(Lists, Txt_path_and_name, Spacer='   ', Mode='w'):  # 列表转换成文本文件
        # 功能：将一维列表，二维列表写到txt
        # 说明：lists_to_txt(列表,文本路径与名,间隔符,模式)
        #      1、间隔符用来间隔矩阵型二维列表行中的每个元素
        #      2、矩阵型二维列表、非矩阵型二维列表都通用
        #      3、w:覆盖模式、a:追加模式
        # 版本：python3.7 原型

        lists = DeepCopy(Lists)
        txt_path_and_name = DeepCopy(Txt_path_and_name)
        spacer = DeepCopy(Spacer)
        mode = DeepCopy(Mode)
        # print('列表开始转换成文本文件...')
        line_number = len(lists)  # 列长
        if (line_number > 0 and isinstance(lists[0], list)):  # 判断是否为二维list
            with open(txt_path_and_name, mode, encoding='utf-8') as object:
                for lines in lists:
                    column_number = len(lines)  # 行长
                    column_order = 0
                    for elements in lines:
                        column_order = column_order + 1
                        object.write(str(elements))
                        if (column_order != column_number):  # 判断是否不是每行最后一个元素
                            object.write(spacer)  ####
                    object.write('\n')
        else:
            with open(txt_path_and_name, mode, encoding='utf-8') as object:
                for elements in lists:
                    object.write(str(elements))
                    object.write('\n')

    '''*************************************************************************************'''
    '''函数功能: 将txt按行读取，转换成一、二维列表                                                 '''
    '''入参:             Txt_path_and_name:文本路径与名                                        '''
    '''                 Spacer:间隔符                                                        '''
    '''                 Mode:模式                                                            '''
    '''出参:                                                                                 '''
    '''返回值:           list:字符列表                                                                    '''
    '''*************************************************************************************'''
    def txt_to_listsstr(Txt_path_and_name, Spacer='   ',Mode='r'):  # 文本文件转换成字符列表
        # 功能：将txt按行读取，转换成一、二维列表
        # 说明：txt_to_lists(文本名)
        #      1、txt中空行不读取
        #      2、txt每行末尾换行符、与空格符自动去除
        # 版本：python3.7
        txt_path_and_name = DeepCopy(Txt_path_and_name)
        mode = DeepCopy(Mode)

        lists = []
        with open(txt_path_and_name, mode, encoding='utf-8') as object:
            for line in object:
                if line != '\n':
                    if (Spacer in line):
                        lists.append(line.replace('\n', '').rstrip().split(Spacer))
                    else:
                        lists.append((line.replace('\n', '').rstrip()))  # 使用replace去掉末尾换行符，使用rstrip去掉末尾空格
        # print('文本文件已经转换成字符列表。')
        return lists
    '''*************************************************************************************'''
    '''函数功能: 拼接图片                                                                      '''
    '''入参:             image1:待拼接图片1                                                    '''
    '''                 image2:待拼接图片2                                                    '''
    '''出参:                                                                                 '''
    '''返回值:           image3:拼接后的图片                                                 '''
    '''*************************************************************************************'''
    #拼接图片
    def merge(image1, image2):
        h1, w1, c1 = image1.shape
        h2, w2, c2 = image2.shape
        if c1 != c2:
            print("channels NOT match, cannot merge")
            return
        else:
            if h1 > h2:
                tmp = np.zeros([h1 - h2, w2, c1])
                image3 = np.vstack([image2, tmp])
                image3 = np.hstack([image1, image3])
            elif h1 == h2:
                image3 = np.hstack([image1, image2])
            else:
                tmp = np.zeros([h2 - h1, w1, c2])
                image3 = np.vstack([image1, tmp])
                image3 = np.hstack([image3, image2])

        return image3


    def super_resolution(img):
        img = img * 1.0 / 255
        img = test.torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        img_LR = img.unsqueeze(0)
        img_LR = img_LR.to(test.device)

        with test.torch.no_grad():
            output = test.model(img_LR).data.squeeze().float().cpu().clamp_(0, 1).numpy()
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round()
        return output

# 功能函数
if (1 == 1):
    '''*************************************************************************************'''
    '''函数功能: 预处理                                                                        '''
    '''入参:             Input_path：输入路径                                                  '''
    '''                 Output_path：输出路径                                                 '''
    '''出参:                                                                                 '''
    '''返回值:                                                                               '''
    '''*************************************************************************************'''
    # 预处理
    def preProcess(Input_path, Output_path):
        input_path = DeepCopy(Input_path)
        output_path = DeepCopy(Output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        files = os.listdir(input_path)
        file_count = 0
        for file in files:
            file_count = file_count + 1
            print("预处理第" + str(file_count) + "张图片...")
            image = cv_imread(input_path + file)
            #多行检测
            image,cut_imgs = detect_divite_multi_row(image)
            newImge = image
            # if len(cut_imgs) > 0:
            #     #取出切割的图像水平拼接
            #     newImge = cut_imgs[0]
            #     for i in range(1,len(cut_imgs)):
            #         newImge = merge(newImge,cut_imgs[i])

            # 超分
            print("超分...")
            image = super_resolution(newImge)
            # 锐化
            #print("边缘增强...")
            #image = sharpen(image)

            cv_imwrite(output_path + file, image)


    '''*************************************************************************************'''
    '''函数功能: 获取列表的第二个元素                                                             '''
    '''入参:             elem：列表                                                           '''
    '''出参:                                                                                 '''
    '''返回值:           elem[1]:列表第二个元素                                                 '''
    '''*************************************************************************************'''
    # 获取列表的第二个元素
    def takeSecond(elem):
        return elem[1]
    '''*************************************************************************************'''
    '''函数功能: 批量将识别路径图片放入Ship_name_database文件夹下                                   '''
    '''入参:             Input_path：输入路径                                                  '''
    '''                 Output_path：输出路径                                                 '''
    '''出参:                                                                                 '''
    '''返回值:                                                                               '''
    '''*************************************************************************************'''
    # 批量将识别路径图片放入Ship_name_database文件夹下
    def move_to_Ship_name_database(Input_path, Output_path):
        input_path = DeepCopy(Input_path)
        output_path = DeepCopy(Output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        files = os.listdir(input_path)
        for file in files:  # 遍历文件夹
            if (file[-3:] == 'jpg'):
                shutil.move(input_path+file,output_path+file)

    '''*************************************************************************************'''
    '''函数功能: 数据库船名规则化                                                                '''
    '''入参:             Input_path：输入路径                                                  '''
    '''                 Output_path：保存路径                                                 '''
    '''出参:                                                                                 '''
    '''返回值:                                                                               '''
    '''*************************************************************************************'''
    # 数据库船名规则化
    def make_ship_regularizedname_database(Input_path, Output_path):
        # 功能：将原始数据库(1_安航机00268.jpg)整理成规则化数字编号+船名数据库(00001_安航机00268.jpg)
        # 说明：make_ship_regularizedname_database(输入文件夹地址,输出文件夹地址)
        input_path = DeepCopy(Input_path)
        output_path = DeepCopy(Output_path)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        files = os.listdir(input_path)
        # i=0
        file_count = 0
        for file in files:  # 遍历文件夹
            if (file[-3:] == 'jpg'):
                # i=i+1
                # if(i>0):
                ###读取jpg
                im = Image.open(input_path + file)
                ###规则化命名
                file_oldname_list = file.split('_')

                # if(1<=int(file_oldname_list[0])<10):
                # file_newname='0000'+file_oldname_list[0]+'_'+file_oldname_list[1]
                # if(10<=int(file_oldname_list[0])<100):
                # file_newname='000'+file_oldname_list[0]+'_'+file_oldname_list[1]
                # print(new_file)
                # if(100<=int(file_oldname_list[0])<1000):
                # file_newname='00'+file_oldname_list[0]+'_'+file_oldname_list[1]
                # print(new_file)
                # if(1000<=int(file_oldname_list[0])<10000):
                # file_newname='0'+file_oldname_list[0]+'_'+file_oldname_list[1]
                # if(10000<=int(file_oldname_list[0])<100000):
                # file_newname=file

                ###存储
                file_count = file_count + 1
                print("规则化命名第" + str(file_count) + "张图片...")

                pattern = re.compile('[0-9]+')
                # findall是返回所有符合匹配的项，返回形式为数组
                match = pattern.findall(file_oldname_list[-1])

                #### 判断原始图片文件名是否倒序
                # if match and len(file_oldname_list[-1].replace(" ", "")) > 4 and '\u4e00' <= \
                #         file_oldname_list[-1].replace(" ", "")[-5] <= '\u9fa5':
                #     file_oldname_list[-1] = file_oldname_list[-1][-5::-1] + file_oldname_list[-1][-4:]

                file_newname = str(file_count).zfill(6) + '_' + file_oldname_list[-1]
                im = im.convert('RGB')
                im.save(output_path + file_newname)

    '''*************************************************************************************'''
    '''函数功能: 数据库船名数字化                                                                '''
    '''入参:             Input_path：输入路径                                                  '''
    '''                 Output_path：保存路径                                                 '''
    '''出参:                                                                                 '''
    '''返回值:                                                                               '''
    '''*************************************************************************************'''
    # 数据库船名数字化
    def make_shipnumber_database(Input_path, Output_path):
        # 功能：将原始数据库(1_安航机00268.jpg)整理成规则化数字编号数据库(00001.jpg)
        # 说明：make_ship_number_database(输入文件夹地址,输出文件夹地址)
        input_path = DeepCopy(Input_path)
        output_path = DeepCopy(Output_path)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        files = os.listdir(input_path)
        # i=0
        for file in files:  # 遍历文件夹
            if (file[-3:] == 'jpg'):
                # i=i+1
                # if(i>0):
                ###读取jpg
                im = Image.open(input_path + file)
                ###规则化命名
                file_oldname_list = file.split('_')

                file_newname = file_oldname_list[0]
                ###存储
                im = im.convert('RGB')
                im.save(output_path + file_newname + '.jpg')

    '''*************************************************************************************'''
    '''函数功能: 提取船名标签                                                                   '''
    '''入参:             Input_path：输入路径                                                  '''
    '''出参:                                                                                 '''
    '''返回值:            ship_label_list:船名标签列表                                          '''
    '''*************************************************************************************'''
    # 提取船名标签
    def make_ship_regularizedname_label(Input_path):
        # 功能：对规则化数字编号+船名数据库(00001_安航机00268.jpg)提取标签(00001_安航机00268)存txt
        # 说明：make_ship_regularizedname_label(输入文件夹地址)

        input_path = DeepCopy(Input_path)

        ship_label_list = []
        files = os.listdir(input_path)
        # i=0
        for file in files:  # 遍历文件夹
            if (file[-3:] == 'jpg'):
                # i=i+1
                # if(i>0):
                file_name_list = file[:-4].split('_')

                ship_label_list.append(file_name_list)
        return ship_label_list

    '''*************************************************************************************'''
    '''函数功能: 提取非重复船名标签库                                                             '''
    '''入参:             Old_ship_nonrepetitivelabel：当前非重复性船名标签库                      '''
    '''                 Add_ship_name:待添加船名                                              '''
    '''出参:                                                                                 '''
    '''返回值:            ship_nonrelabel_list:更新后的非重复性船名标签库                          '''
    '''*************************************************************************************'''
    # 提取非重复船名标签库
    def make_ship_nonrepetitivelabel(Old_ship_nonrepetitivelabel, Add_ship_name):

        ship_nonrelabel_list = DeepCopy(Old_ship_nonrepetitivelabel)
        add_ship_name = DeepCopy(Add_ship_name)

        add_ship_name_cc = "".join(re.findall('[\u4e00-\u9fa5]', add_ship_name))
        add_ship_name_dc = re.sub("\D", "", add_ship_name)

        if (len(ship_nonrelabel_list) == 0):  # 原标签为空
            ship_nonrelabel_list = []
            ship_nonrelabel = []
            ship_nonrelabel.append(add_ship_name_cc)
            ship_nonrelabel.append(add_ship_name_dc)
            ship_nonrelabel_list.append(ship_nonrelabel)
        else:  # 原标签不为空
            mark1 = 0
            for i in range(len(ship_nonrelabel_list)):
                if isinstance(ship_nonrelabel_list[i], list) and ship_nonrelabel_list[i][0] == add_ship_name_cc:  # 是否存在船厂名
                    mark1 = 1
                    mark2 = 0
                    for j in range(len(ship_nonrelabel_list[i]) - 1):
                        if ship_nonrelabel_list[i][j + 1] == add_ship_name_dc:  # 是否存在船编号
                            mark2 = 1
                            break
                    if mark2 == 0:
                        ship_nonrelabel_list[i].append(add_ship_name_dc)
                    break
                elif isinstance(ship_nonrelabel_list[i], str) and ship_nonrelabel_list[i][0] == add_ship_name_cc:
                    # 原船名库中只有船名，这时此条记录为string而不是list类型
                    mark1 = 1
                    list(ship_nonrelabel_list[i]).append(add_ship_name_dc)
                    break
            if mark1 == 0:
                ship_nonrelabel = []
                ship_nonrelabel.append(add_ship_name_cc)
                ship_nonrelabel.append(add_ship_name_dc)
                ship_nonrelabel_list.append(ship_nonrelabel)

        return ship_nonrelabel_list

    '''*************************************************************************************'''
    '''函数功能: 船名识别                                                                      '''
    '''入参:             Input_path：输入路径                                                  '''
    '''出参:                                                                                 '''
    '''返回值:            ocr_result_list:识别结果列表                                          '''
    '''*************************************************************************************'''
    # 识别
    def file_ocr(Input_path):
        # 功能：船名识别
        # 说明：ocr(输入文件夹地址)
        input_path = DeepCopy(Input_path)
        # paddleocr
        ocr = hub.Module(name="chinese_ocr_db_crnn_server")  # 模型导入
        # ocr = hub.Module(directory=PATH_SHARE + "chinese_ocr_db_crnn_server\\")  # 模型导入
        ocr_result_list = []
        files = os.listdir(input_path)
        i = 0
        for file in files:  # 遍历文件夹
            if (file[-3:] == 'jpg'):
                i = i + 1
                if (i > 0):
                    print("正在识别第" + str(i) + "张图片...")

                    results = ocr.recognize_text(paths=[input_path + file], visualization=True)

                    ocr_result = []
                    if len(results[0]['data']) != 0:  # 判断是否有识别结果
                        rec_name = ''
                        confidence_sum = 0
                        for j in range(len(results[0]['data'])):  # 所有识别框拼接
                            rec_name = rec_name + results[0]['data'][j]['text']

                            pattern = re.compile('[0-9]+')
                            # findall是返回所有符合匹配的项，返回形式为数组
                            match = pattern.findall(rec_name)

                            if match and '\u4e00' <= rec_name.replace(" ", "")[-1] <= '\u9fa5':
                                rec_name = rec_name[::-1]
                            confidence_sum = confidence_sum + results[0]['data'][j]['confidence']
                        confidence = confidence_sum / len(results[0]['data'])  # 平均置信度

                        ocr_result.append(file[:-4])  # 编号
                        ocr_result.append(rec_name)  # 识别结果
                        ocr_result.append(confidence)  # 置信度
                        ocr_result_list.append(ocr_result)
                    else:
                        ocr_result.append(file[:-4])
                        ocr_result.append('未能识别')
                        ocr_result.append(0)
                        ocr_result_list.append(ocr_result)
        return ocr_result_list
    '''*************************************************************************************'''
    '''函数功能: 提取船名标签                                                                   '''
    '''*************************************************************************************'''
# 提取船名标签
if (1 == 1):
    def extract_shipname():
        Ship_label_list = make_ship_regularizedname_label(PATH_W1)
        lists_to_txt(Ship_label_list, PATH_R0 + 'Ship_labels.txt', Spacer='   ', Mode='w')
        print("数据库中共有" + str(shape(Ship_label_list)[0]) + "张图片")
    '''*************************************************************************************'''
    '''函数功能: 提取非重复船名标签库                                                             '''
    '''*************************************************************************************'''
# 提取非重复船名标签库
if (1 == 1):
    def extract_shipname_nonrepeat():
        Ship_label_list = txt_to_listsstr(PATH_R0 + 'Ship_labels.txt')
        # print(Ship_label_list[2])
        Ship_nonrelabel_list = []
        Ship_nonrelabel_list_path = PATH_SHARE + 'Ship_nonrepetitivelabel.txt'
        if not os.path.exists(Ship_nonrelabel_list_path):
            lists_to_txt(Ship_nonrelabel_list, Ship_nonrelabel_list_path, Spacer='   ', Mode='w')
        Ship_nonrelabel_list = txt_to_listsstr(Ship_nonrelabel_list_path)
        for i in range(len(Ship_label_list)):
            # print(Ship_label_list[i][1])
            Ship_nonrelabel_list = make_ship_nonrepetitivelabel(Ship_nonrelabel_list, Ship_label_list[i][1])
        lists_to_txt(Ship_nonrelabel_list, PATH_SHARE + 'Ship_nonrepetitivelabel.txt', Spacer='   ', Mode='w')
    '''*************************************************************************************'''
    '''函数功能: 对数据库中图片进行文字识别                                                        '''
    '''入参:             Input_path：输入路径                                                  '''
    '''出参:                                                                                 '''
    '''返回值:                                                                                '''
    '''*************************************************************************************'''
# 对数据库中图片进行文字识别
if (1 == 1):
    def ocr_to_txt(Input_path):
        input_path = DeepCopy(Input_path)
        Ocr_results = file_ocr(input_path)
        lists_to_txt(Ocr_results, PATH_R0 + 'Ocr_results.txt', Spacer='   ', Mode='w')


def initial_accuracy():
    Ship_label_list = txt_to_listsstr(PATH_R0 + 'Ship_labels.txt')
    Ocr_results_list = txt_to_listsstr(PATH_R0 + 'Ocr_results.txt')
    # print(Ship_label_list[0])
    # print(Ocr_results_list[0])
    Output = []
    error = []
    true_number = 0
    # f1 = open(PATH_R0+'Output.txt', 'a', encoding='utf-8')
    # f2 = open(PATH_R0+'error.txt', 'a', encoding='utf-8')
    for i in range(len(Ship_label_list)):
        List = []
        List.append(Ship_label_list[i][0])
        List.append(Ship_label_list[i][1])
        List.append(Ocr_results_list[i][1])
        List.append(Ocr_results_list[i][2])
        if (Ship_label_list[i][1] == Ocr_results_list[i][1]):
            List.append('True')
            true_number = true_number + 1
            List.append(str(true_number))
            List.append(str(i + 1))
            Output.append(List)
        else:
            List.append('False')
            List.append(str(true_number))
            List.append(str(i + 1))
            Output.append(List)
            error.append(List)
    # print(len(Output))
    # print(Output[0])
    # print(Output[3])
    # print(type(Output[0])=='List')
    lists_to_txt(Output, PATH_R0 + 'Output3.txt', Spacer='   ', Mode='w')
    lists_to_txt(error, PATH_R0 + 'Error3.txt', Spacer='   ', Mode='w')

    '''*************************************************************************************'''
    '''函数功能: 识别主程序                                                                     '''
    '''*************************************************************************************'''
# 识别主程序
def rec_main():
    print("开始执行识别程序...")
    # 批量将识别路径图片放入Ship_name_database文件夹下
    move_to_Ship_name_database(PATH_R0,PATH_R1)
    # 数据库船名规则化
    make_ship_regularizedname_database(PATH_R1, PATH_W1)
    # 数据库船名数字化
    make_shipnumber_database(PATH_W1, PATH_W2)
    # 提取船名标签
    extract_shipname()
    # 提取非重复船名标签库
    # extract_shipname_nonrepeat()
    # 图片预处理
    #preProcess(PATH_W2, PATH_W3)
    # 对数据库中图片进行文字识别
    ocr_to_txt(PATH_W2)

if __name__ == '__main__':
    rec_main()
    initial_accuracy()