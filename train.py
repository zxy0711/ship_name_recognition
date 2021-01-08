import os
import re
import argparse
from numpy import *
from copy import deepcopy
from PIL import Image, ImageFont, ImageDraw

PATH_SHARE = os.path.abspath(os.path.dirname(__file__)) + "\\"
PATH_R0 = os.path.abspath(os.path.dirname(__file__)) + "\\data\\new\\"  # 数据地址
PATH_R1 = PATH_R0 + "Ship_name_database\\"  # 数据地址
TRAIN_DATA = PATH_R0 + "train\\"


def DeepCopy(Objects):  # 深拷贝
    # 功能：对目标进行深拷贝
    # 版本：python3.7 原型
    objects = deepcopy(Objects)

    return objects


def extract_train_shipname(type):
    if type != "test" and type != "train":
        print("没有给定正确的参数！必须为train或test其中之一")
        return
    global TRAIN_DATA
    TRAIN_DATA = PATH_R0 + type + "\\"
    Ship_label_list = make_ship_regularizedname_label(PATH_R1, type)

    ## 以下舍弃,由gen_ship_dict()函数实现
    # # 读取原来的船名汉字字典
    # ship_character_list = []
    # ship_character_list_path = PATH_SHARE + 'ship_character_dict.txt'
    # if not os.path.exists(ship_character_list_path):
    #     lists_to_txt(ship_character_list, ship_character_list_path, Spacer='   ', Mode='w')
    # #读取出来的原字典先转化为set
    # ship_character_set = set(txt_to_listsstr(ship_character_list_path))
    #
    # #新增的船名文字先去重
    # ship_name_list = []
    # for label in Ship_label_list:
    #     ship_name_list.append(label.split('\t')[-1].strip(' '))
    #
    # #再加入总的字典库中需要再检验一次去重
    # for ship_name in ship_name_list:
    #     for i in range(len(ship_name)):
    #         ship_character_set.add(ship_name[i])
    #
    # # 最后转化为list写入txt文件
    # ship_character_list = list(ship_character_set)
    # lists_to_txt(ship_character_list, ship_character_list_path, Spacer='   ', Mode='w')

    # 生成标签文本
    lists_to_txt(Ship_label_list, PATH_R0 + 'rec_gt_' + type + '.txt', Spacer='   ', Mode='w')

    print("数据库中共有" + str(shape(Ship_label_list)[0]) + "张图片")


# 提取船名标签
def make_ship_regularizedname_label(Input_path, name):
    input_path = DeepCopy(Input_path)

    ship_label_list = []
    files = os.listdir(input_path)
    i = 0
    for file in files:  # 遍历文件夹
        if (file[-3:] == 'jpg'):
            i = i + 1
            print("生成第" + str(i) + "张" + name + "图片...")
            im = Image.open(input_path + file)
            file_name_list = file[:-4].split('_')
            file_newname = name + "_" + str(i).zfill(4) + file[-4:]
            im = im.convert('RGB')

            if not os.path.exists(TRAIN_DATA):
                os.makedirs(TRAIN_DATA)
            im.save(TRAIN_DATA + file_newname)

            ship_name_cc = "".join(re.findall('[\u4e00-\u9fa5]', file_name_list[-1]))
            ship_name_dc = re.sub("\D", "", file_name_list[-1])
            # 856阜阳港->阜阳港856
            new_name = ship_name_cc + ship_name_dc

            ship_label_list.append(name + "/" + file_newname + "\t" + new_name)
    return ship_label_list


# 批量将识别路径图片放入Ship_name_database文件夹下
def move_to_Ship_name_database(Input_path, Output_path):
    input_path = DeepCopy(Input_path)
    output_path = DeepCopy(Output_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    files = os.listdir(input_path)
    for file in files:  # 遍历文件夹
        if (file[-3:] == 'jpg'):
            shutil.move(input_path + file, output_path + file)


def txt_to_listsstr(Txt_path_and_name, Spacer='   ', Mode='r'):  # 文本文件转换成字符列表
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
                        object.write(spacer)
                object.write('\n')
    else:
        with open(txt_path_and_name, mode, encoding='utf-8') as object:
            for elements in lists:
                object.write(str(elements))
                object.write('\n')


# 生成自定义船名汉字字典
def gen_ship_dict():
    ship_character_list = []
    ship_character_set = set()

    # 读取船名总库
    Ship_nonrelabel_list = []
    Ship_nonrelabel_list_path = PATH_SHARE + 'Ship_nonrepetitivelabel.txt'
    if not os.path.exists(Ship_nonrelabel_list_path):
        lists_to_txt(Ship_nonrelabel_list, Ship_nonrelabel_list_path, Spacer='   ', Mode='w')

    Ship_nonrelabel_list = txt_to_listsstr(Ship_nonrelabel_list_path)
    # 读入的为二维list
    for line in Ship_nonrelabel_list:
        # 加入总的字典库前需要再检验一次去重
        if isinstance(line, list):
            for ship_name in line:
                for i in range(len(ship_name)):
                    ship_character_set.add(ship_name[i])

        # 若船名库中只有船名，这时此条记录为string而不是list类型
        elif isinstance(line, str):
            for i in range(len(line)):
                ship_character_set.add(line[i])

    # 最后转化为list写入txt文件
    ship_character_list = list(ship_character_set)
    print("字典中共有" + str(len(ship_character_list)) + "个字符")
    lists_to_txt(ship_character_list, PATH_SHARE + 'ship_character_dict.txt', Spacer='   ', Mode='w')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--dir',
        type=str,
        default=os.path.abspath(os.path.dirname(__file__)) + "\\data\\new",
        help='The root directory of source images')
    parser.add_argument(
        '-t',
        '--type',
        type=str,
        default="train",
        help='Whether train or test')

    args = parser.parse_args()
    PATH_R0 = args.dir + "\\"
    PATH_R1 = PATH_R0 + "Ship_name_database\\"
    TYPE = args.type

    #move_to_Ship_name_database(PATH_R0, PATH_R1)
    #extract_train_shipname(TYPE)
    gen_ship_dict()
