import os
from copy import deepcopy
import re

# 工具函数
if (1 == 1):
    def DeepCopy(Objects):  # 深拷贝
        # 功能：对目标进行深拷贝
        # 版本：python3.7 原型
        objects = deepcopy(Objects)

        return objects


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


def extract_shipname_nonrepeat():
    Ship_label_list = txt_to_listsstr('labels1.txt')
    # print(Ship_label_list[2])
    Ship_nonrelabel_list = []
    Ship_nonrelabel_list_path = 'Ship_nonrepetitivelabel.txt'
    if not os.path.exists(Ship_nonrelabel_list_path):
        lists_to_txt(Ship_nonrelabel_list, Ship_nonrelabel_list_path, Spacer='   ', Mode='w')
    Ship_nonrelabel_list = txt_to_listsstr(Ship_nonrelabel_list_path)
    for i in range(len(Ship_label_list)):
        print(Ship_label_list[i])
        Ship_nonrelabel_list = make_ship_nonrepetitivelabel(Ship_nonrelabel_list, Ship_label_list[i])
    lists_to_txt(Ship_nonrelabel_list, 'Ship_nonrepetitivelabel.txt', Spacer='   ', Mode='w')

if __name__ == '__main__':
    extract_shipname_nonrepeat()