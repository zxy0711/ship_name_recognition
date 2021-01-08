from Ship_name_recognition import *

PATH_R0 = os.path.abspath(os.path.dirname(__file__)) + "\\data\\"  # 数据地址
K = 100 # 相似度最小的K个行记录


#识别后纠错处理相关函数
'''*************************************************************************************'''
'''函数功能: 创建或更新中文字符字典与相似度矩阵                                                  '''
'''入参:             Old_chinesecharacter_dict：旧中文字符字典                              '''
'''                 Old_similarity_matrix：旧相似度矩阵                                    '''
'''                 Add_string：待添加字符串                                               '''
'''出参:                                                                                 '''
'''返回值:           cc_dict:新中文字符字典                                                 '''
'''                 similarity_matrix:新相似度矩阵                                         '''
'''*************************************************************************************'''
def make_similaritymatrix_of_chinesecharacter(Old_chinesecharacter_dict, Old_similarity_matrix, Add_string):
    # 功能：输入旧字典与旧相似度矩阵与待添加字符串，更新字典与相似度矩阵
    # 说明：make_similaritymatrix_of_chinesecharacter(老字典,老相似度矩阵,待添加字符串)
    #      1、输入字符串无要求
    #      2、当已经存在字典与相似度矩阵则进行更新,不存在就新建
    cc_dict = DeepCopy(Old_chinesecharacter_dict)
    similarity_matrix = DeepCopy(Old_similarity_matrix)
    add_string = DeepCopy(Add_string)

    if (len(cc_dict) == 0 and len(similarity_matrix) == 0):  # 判断是否没有字典与相似度矩阵
        # 制作字典
        cc_dict = {}  # 形近字字典
        cc_dict_len = 0
        for i in range(len(add_string)):
            if '\u4e00' <= add_string[i] <= '\u9fff':  # 判断是否是汉字
                if (add_string[i] in cc_dict):  # 是否字典中已经存在
                    continue
                cc_dict[add_string[i]] = cc_dict_len
                cc_dict_len = cc_dict_len + 1
        ##对角线为0的1数组
        similarity_matrix = ones((cc_dict_len, cc_dict_len))
        for j in range(len(similarity_matrix)):
            similarity_matrix[j][j] = 0
        print('建立新字典共 ' + str(len(similarity_matrix)) + '个字。')
    elif (len(cc_dict) != 0 and len(similarity_matrix) != 0):  # 判断是否已有字典与相似度矩阵
        # 扩充字典
        old_cc_dict_len = len(cc_dict)
        cc_dict_len = len(cc_dict)
        for i in range(len(add_string)):
            if '\u4e00' <= add_string[i] <= '\u9fff':  # 判断是否是汉字
                if (add_string[i] in cc_dict):  # 是否字典中已经存在
                    continue
                cc_dict[add_string[i]] = cc_dict_len
                cc_dict_len = cc_dict_len + 1
        similarity_matrix_add_col = ones((old_cc_dict_len, cc_dict_len - old_cc_dict_len))  # 需要补充的列
        similarity_matrix = hstack((similarity_matrix, similarity_matrix_add_col))
        similarity_matrix_add_row = ones((cc_dict_len - old_cc_dict_len, cc_dict_len))  # 需要补充的行
        similarity_matrix = vstack((similarity_matrix, similarity_matrix_add_row))
        for j in range(cc_dict_len - old_cc_dict_len):
            similarity_matrix[old_cc_dict_len + j][old_cc_dict_len + j] = 0
        if (cc_dict_len - old_cc_dict_len != 0):
            print('已新添加 ' + str(cc_dict_len - old_cc_dict_len) + '个字，共 ' + str(cc_dict_len) + '个字。')
    else:
        print('字典与相似度矩阵不匹配')
    return cc_dict, similarity_matrix

    '''*************************************************************************************'''
    '''函数功能: 更新字典及相似度矩阵                                                                 '''
    '''入参:             Old_chinesecharacter_dict：旧中文字符字典                              '''
    '''                 Old_similarity_matrix：旧相似度矩阵                                    '''
    '''                 Chinesechar1：中文字符1                                               '''
    '''                 Chinesechar2：中文字符2                                               '''
    '''出参:                                                                                 '''
    '''返回值:           cc_dict:新中文字符字典                                                 '''
    '''                 similarity_matrix:新相似度矩阵                                         '''
    '''*************************************************************************************'''
def update_sm_of_cc(Old_chinesecharacter_dict, Old_similarity_matrix, Chinesechar1, Chinesechar2):
    cc_dict = DeepCopy(Old_chinesecharacter_dict)
    similarity_matrix = DeepCopy(Old_similarity_matrix)
    cc1 = DeepCopy(Chinesechar1)
    cc2 = DeepCopy(Chinesechar2)

    if (len(cc1) == len(cc2) and len(cc2) == 1 and cc1 != cc2):
        cc_dict, similarity_matrix = make_similaritymatrix_of_chinesecharacter(cc_dict, similarity_matrix,
                                                                               cc1 + cc2)
        similarity_matrix[cc_dict[cc1]][cc_dict[cc2]] = 0.2
        similarity_matrix[cc_dict[cc2]][cc_dict[cc1]] = 0.2
    return cc_dict, similarity_matrix

    '''*************************************************************************************'''
    '''函数功能: 获取中文字符相似度                                                              '''
    '''入参:             Chinesecharacter_dict：中文字符字典                                   '''
    '''                 Similarity_matrix：相似度矩阵                                         '''
    '''                 Chinesechar1：中文字符1                                               '''
    '''                 Chinesechar2：中文字符2                                               '''
    '''出参:                                                                                 '''
    '''返回值:                                                                                '''
    '''*************************************************************************************'''
def get_similarity_of_cc(Chinesecharacter_dict, Similarity_matrix, Chinesechar1, Chinesechar2):
    cc_dict = DeepCopy(Chinesecharacter_dict)
    similarity_matrix = DeepCopy(Similarity_matrix)
    cc1 = DeepCopy(Chinesechar1)
    cc2 = DeepCopy(Chinesechar2)

    if (len(cc1) == len(cc2) and len(cc2) == 1 and cc1 != cc2):
        if (cc1 in cc_dict and cc2 in cc_dict):
            return similarity_matrix[cc_dict[cc1]][cc_dict[cc2]]
        else:
            # print('获取中文字符相似度失败：字典中不存在')
            return 1
    else:
        print('获取中文字符相似度失败：输入错误')

    '''*************************************************************************************'''
    '''函数功能: 根据标签和结果集更新字典和相似度矩阵                                                '''
    '''入参:             Old_chinesecharacter_dict：旧中文字符字典                              '''
    '''                 Old_similarity_matrix：旧相似度矩阵                                    '''
    '''                 Lstring：标签                                                        '''
    '''                 Rstring：结果集                                                       '''
    '''出参:                                                                                 '''
    '''返回值:           cc_dict：新中文字符字典                                                 '''
    '''                 similarity_matrix：新相似度矩阵                                        '''
    '''*************************************************************************************'''
def update_sm_of_cc_basedon_label_and_result(Old_chinesecharacter_dict, Old_similarity_matrix, Lstring, Rstring):
    cc_dict = DeepCopy(Old_chinesecharacter_dict)
    similarity_matrix = DeepCopy(Old_similarity_matrix)
    lstring = DeepCopy(Lstring)
    rstring = DeepCopy(Rstring)

    cc_dict, similarity_matrix = make_similaritymatrix_of_chinesecharacter(cc_dict, similarity_matrix,
                                                                           lstring + rstring)
    lstring_cc = "".join(re.findall('[\u4e00-\u9fa5]', lstring))
    rstring_cc = "".join(re.findall('[\u4e00-\u9fa5]', rstring))
    if (Lstring != '未能识别' and rstring != '未能识别'):

        # 两字符串相同字符位置
        same_char_pair_list = []
        for i in range(len(lstring_cc)):
            for j in range(len(rstring_cc)):
                if (lstring_cc[i] == rstring_cc[j]):
                    same_char_pair = []
                    same_char_pair.append(i)
                    same_char_pair.append(j)
                    same_char_pair_list.append(same_char_pair)
        if (len(same_char_pair_list) == 0 and len(lstring_cc) == len(rstring_cc)):
            for i in range(len(lstring_cc)):
                # if(lstring_cc[i]=='川' and rstring_cc[i]=='团'):
                # print(lstring_cc)
                # print(rstring_cc)
                cc_dict, similarity_matrix = update_sm_of_cc(cc_dict, similarity_matrix, lstring_cc[i],
                                                             rstring_cc[i])
        if (len(same_char_pair_list) == 1):  # 一个字符相同
            if (same_char_pair_list[0][0] == same_char_pair_list[0][1] and same_char_pair_list[0][
                1] != 0):  # 相同字符前有可匹配字符
                for i in range(same_char_pair_list[0][1]):
                    # if(lstring_cc[i]=='川' and rstring_cc[i]=='团'):
                    # print(lstring_cc)
                    # print(rstring_cc)
                    cc_dict, similarity_matrix = update_sm_of_cc(cc_dict, similarity_matrix, lstring_cc[i],
                                                                 rstring_cc[i])
            if (len(lstring_cc) - 1 - same_char_pair_list[0][0] == len(rstring_cc) - 1 - same_char_pair_list[0][
                1] and len(rstring_cc) - 1 - same_char_pair_list[0][1] != 0):  # 相同字符后有可匹配字符
                for i in range(len(lstring_cc) - 1 - same_char_pair_list[0][0]):
                    # if(lstring_cc[i]=='川' and rstring_cc[i]=='团'):
                    # print(lstring_cc)
                    # print(rstring_cc)
                    cc_dict, similarity_matrix = update_sm_of_cc(cc_dict, similarity_matrix,
                                                                 lstring_cc[len(lstring_cc) - 1 - i],
                                                                 rstring_cc[len(rstring_cc) - 1 - i])
        if (len(same_char_pair_list) >= 2):  # 多于两个字符相同
            if (same_char_pair_list[0][0] == same_char_pair_list[0][1] and same_char_pair_list[0][
                1] != 0):  # 第一个相同字符前有可匹配字符
                for i in range(same_char_pair_list[0][1]):
                    # if(lstring_cc[i]=='川' and rstring_cc[i]=='团'):
                    # print(lstring_cc)
                    # print(rstring_cc)
                    cc_dict, similarity_matrix = update_sm_of_cc(cc_dict, similarity_matrix, lstring_cc[i],
                                                                 rstring_cc[i])
            if (len(lstring_cc) - 1 - same_char_pair_list[-1][0] == len(rstring_cc) - 1 - same_char_pair_list[-1][
                1] and len(rstring_cc) - 1 - same_char_pair_list[-1][1] != 0):  # 最后一个相同字符后有可匹配字符
                for i in range(len(lstring_cc) - 1 - same_char_pair_list[-1][0]):
                    # if(lstring_cc[i]=='川' and rstring_cc[i]=='团'):
                    # print(lstring_cc)
                    # print(rstring_cc)
                    cc_dict, similarity_matrix = update_sm_of_cc(cc_dict, similarity_matrix,
                                                                 lstring_cc[len(lstring_cc) - 1 - i],
                                                                 rstring_cc[len(rstring_cc) - 1 - i])
            for i in range(len(same_char_pair_list) - 1):  # 遍历中间间隔
                if (same_char_pair_list[i + 1][0] - same_char_pair_list[i][0] == same_char_pair_list[i + 1][1] -
                        same_char_pair_list[i][1] and same_char_pair_list[i + 1][1] - same_char_pair_list[i][
                            1] > 1):  # 如果间隔相等且有间隔，则配对间隔中字符
                    for j in range(same_char_pair_list[i + 1][0] - same_char_pair_list[i][0] - 1):
                        # if(lstring_cc[i]=='川' and rstring_cc[i]=='团'):
                        # print(lstring_cc)
                        # print(rstring_cc)
                        cc_dict, similarity_matrix = update_sm_of_cc(cc_dict, similarity_matrix,
                                                                     lstring_cc[same_char_pair_list[i][0] + j + 1],
                                                                     rstring_cc[same_char_pair_list[i][1] + j + 1])
    return cc_dict, similarity_matrix

    '''*************************************************************************************'''
    '''函数功能: 输出中文字符相似度列表                                                           '''
    '''入参:             Chinesecharacter_dict：中文字符字典                                   '''
    '''                 Similarity_matrix：相似度矩阵                                         '''
    '''出参:                                                                                 '''
    '''返回值:           similar_cc_pair_list：中文字符相似列表                                '''
    '''*************************************************************************************'''
def output_similar_chinesecharacter(Chinesecharacter_dict, Similarity_matrix):
    cc_dict = DeepCopy(Chinesecharacter_dict)
    similarity_matrix = DeepCopy(Similarity_matrix)

    similar_cc_pair_list = []
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            if (similarity_matrix[i][j] == 0.2):
                similar_cc_pair = []
                similar_cc_pair.append(list(cc_dict.keys())[i])
                similar_cc_pair.append(list(cc_dict.keys())[j])
                similar_cc_pair_list.append(similar_cc_pair)
    return similar_cc_pair_list

    '''*************************************************************************************'''
    '''函数功能: 建立数字相似度矩阵  0-9 : 0-9                                                            '''
    '''入参:                                                                                 '''
    '''出参:                                                                                 '''
    '''返回值:           similarity_matrix：数字相似度矩阵                                       '''
    '''*************************************************************************************'''
def make_similaritymatrix_of_digitcharacter():
    # 功能：建立数字相似度矩阵
    # 说明：make_similaritymatrix_of_digitcharacter()
    similarity_matrix = array([[0, 1, 1, 1, 1, 1, 0.5, 1, 1, 1],
                               [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
                               [1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 0, 1, 1, 1, 1, 0.5, 1],
                               [1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
                               [0.5, 1, 1, 1, 1, 1, 0, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                               [1, 1, 1, 0.5, 1, 1, 1, 1, 0, 1],
                               [1, 1, 1, 1, 1, 1, 1, 1, 1, 0]])
    # print()
    return similarity_matrix

    '''*************************************************************************************'''
    '''函数功能: 计算中文字符DTW距离                                                             '''
    '''入参:             List1：列表1                                                         '''
    '''                 List2：列表2                                                         '''
    '''                 Cc_dict：中文字符字典                                                  '''
    '''                 Cc_similarity_matrix：中文字符相似度矩阵                                '''
    '''出参:                                                                                 '''
    '''返回值:           d[list1len][list2len]：DTW距离                                       '''
    '''*************************************************************************************'''
def chinesecharacter_dtw(List1, List2, Cc_dict, Cc_similarity_matrix):
    # dtw距离只与相似度有关，与长短无关，但长短相差大相似度变低。
    list1 = List1
    list2 = List2
    cc_dict = Cc_dict
    cc_similarity_matrix = Cc_similarity_matrix

    list1len = len(list1)
    list2len = len(list2)
    distaned = []
    for i in range(0, list1len):
        distaned_line = []
        for j in range(0, list2len):
            if list1[i] == list2[j]:
                distaned_line.append(0)
            else:
                if list1[i] not in cc_dict or list2[j] not in cc_dict:
                    distaned_line.append(1)
                else:
                    distaned_line.append(cc_similarity_matrix[cc_dict[list1[i]]][cc_dict[list2[j]]])
        distaned.append(distaned_line)
    d = [[0 for i in range(0, list2len + 1)] for j in range(0, list1len + 1)]
    d[0][0] = 0
    for i in range(1, list2len + 1):
        d[0][i] = sys.maxsize
    for j in range(1, list1len + 1):
        d[j][0] = sys.maxsize
    for i in range(1, list1len + 1):
        for j in range(1, list2len + 1):
            d[i][j] = distaned[i - 1][j - 1] + min(d[i - 1][j], d[i][j - 1],
                                                   d[i - 1][j - 1] + distaned[i - 1][j - 1])
    return d[list1len][list2len]

    '''*************************************************************************************'''
    '''函数功能: 计算数字字符DTW距离                                                             '''
    '''入参:             List1：列表1                                                         '''
    '''                 List2：列表2                                                         '''
    '''                 Dc_similarity_matrix：数字字符相似度矩阵                                '''
    '''出参:                                                                                 '''
    '''返回值:           d[list1len][list2len]：DTW距离                                       '''
    '''*************************************************************************************'''
def digitcharacter_dtw(List1, List2, Dc_similarity_matrix):
    # dtw距离只与相似度有关，与长短无关，但长短相差大相似度变低。
    list1 = List1
    list2 = List2
    dc_similarity_matrix = Dc_similarity_matrix

    list1len = len(list1)
    list2len = len(list2)
    distaned = []
    for i in range(0, list1len):
        distaned_line = []
        for j in range(0, list2len):
            if list1[i] == list2[j]:
                distaned_line.append(0)
            else:
                distaned_line.append(dc_similarity_matrix[int(list1[i])][int(list2[j])])
        distaned.append(distaned_line)
    d = [[0 for i in range(0, list2len + 1)] for j in range(0, list1len + 1)]
    d[0][0] = 0
    for i in range(1, list2len + 1):
        d[0][i] = sys.maxsize
    for j in range(1, list1len + 1):
        d[j][0] = sys.maxsize
    for i in range(1, list1len + 1):
        for j in range(1, list2len + 1):
            d[i][j] = distaned[i - 1][j - 1] + min(d[i - 1][j], d[i][j - 1],
                                                   d[i - 1][j - 1] + distaned[i - 1][j - 1])
    return d[list1len][list2len]

    '''*************************************************************************************'''
    '''函数功能: 计算DTW距离                                                                   '''
    '''入参:             List1：列表1                                                         '''
    '''                 List2：列表2                                                         '''
    '''出参:                                                                                 '''
    '''返回值:           d[list1len][list2len]：DTW距离                                       '''
    '''*************************************************************************************'''
def dtw(List1, List2):
    # dtw距离只与相似度有关，与长短无关，但长短相差大相似度变低。
    list1 = DeepCopy(List1)
    list2 = DeepCopy(List2)

    list1len = len(list1)
    list2len = len(list2)
    distaned = []
    for i in range(0, list1len):
        distaned_line = []
        for j in range(0, list2len):
            if list1[i] == list2[j]:
                distaned_line.append(0)
            else:

                distaned_line.append(1)
        distaned.append(distaned_line)
    d = [[0 for i in range(0, list2len + 1)] for j in range(0, list1len + 1)]
    d[0][0] = 0
    for i in range(1, list2len + 1):
        d[0][i] = sys.maxsize
    for j in range(1, list1len + 1):
        d[j][0] = sys.maxsize
    for i in range(1, list1len + 1):
        for j in range(1, list2len + 1):
            d[i][j] = distaned[i - 1][j - 1] + min(d[i - 1][j], d[i][j - 1],
                                                   d[i - 1][j - 1] + distaned[i - 1][j - 1])
    return d[list1len][list2len]

    '''*************************************************************************************'''
    '''函数功能: 船名匹配                                                                      '''
    '''入参:             Ship_nonrepetitivelabel：非重复船名标签集                              '''
    '''                 Match_shipname：待匹配船名                                            '''
    '''出参:                                                                                 '''
    '''返回值:           match_result：匹配结果                                                '''
    '''                 confidence：正确程度                                                  '''
    '''*************************************************************************************'''
def shipname_matching(Ship_nonrepetitivelabel, Match_shipname):
    ship_nonrepetitivelabel = DeepCopy(Ship_nonrepetitivelabel)
    match_shipname = DeepCopy(Match_shipname)

    cc = "".join(re.findall('[\u4e00-\u9fa5]', match_shipname))
    dc = re.sub("\D", "", match_shipname)

    min_dis = sys.maxsize

    for i in range(len(ship_nonrepetitivelabel)):
        if (cc == ''):  # w未检测到汉字
            dis1 = 100
        else:
            if (ship_nonrepetitivelabel[i][0] == cc):
                dis1 = 0
            else:
                dis1 = dtw(ship_nonrepetitivelabel[i][0], cc)
        if (dc == ''):  # w未检测到数字
            dis2 = 100
            dis = dis1 + dis2
            if (dis < min_dis):
                local_1 = i
                local_2 = 1
                min_dis = dis
        else:
            for j in range(len(ship_nonrepetitivelabel[i]) - 1):
                if (ship_nonrepetitivelabel[i][j + 1] == dc):
                    dis2 = 0
                    dis = dis1 + dis2
                    if (dis < min_dis):
                        local_1 = i
                        local_2 = j + 1
                        min_dis = dis
                    break
                else:
                    dis2 = dtw(ship_nonrepetitivelabel[i][j + 1], dc)
                dis = dis1 + dis2
                if (dis < min_dis):
                    local_1 = i
                    local_2 = j + 1
                    min_dis = dis
    # print(min_dis)
    confidence = exp(-min_dis / 10)
    match_result = ship_nonrepetitivelabel[local_1][0] + ship_nonrepetitivelabel[local_1][local_2]
    return match_result, confidence

    '''*************************************************************************************'''
    '''函数功能: 船名匹配_1                                                                    '''
    '''入参:             Ship_nonrepetitivelabel：非重复船名标签集                              '''
    '''                 Match_shipname：待匹配船名                                            '''
    '''出参:                                                                                 '''
    '''返回值:           match_result：匹配结果                                                '''
    '''                 confidence：正确程度                                                  '''
    '''*************************************************************************************'''
def shipname_matching_1(Ship_nonrepetitivelabel, Match_shipname):
    ship_nonrepetitivelabel = DeepCopy(Ship_nonrepetitivelabel)
    match_shipname = DeepCopy(Match_shipname)

    cc = "".join(re.findall('[\u4e00-\u9fa5]', match_shipname))
    dc = re.sub("\D", "", match_shipname)

    min_dis = sys.maxsize

    for i in range(len(ship_nonrepetitivelabel)):
        if (cc == ''):  # w未检测到汉字
            dis1 = 100
        else:
            if (ship_nonrepetitivelabel[i][0] == cc):
                dis1 = 0
            else:
                dis1 = dtw(ship_nonrepetitivelabel[i][0], cc) + 10
        if (dc == ''):  # w未检测到数字
            dis2 = 100
            dis = dis1 + dis2
            if (dis < min_dis):
                local_1 = i
                local_2 = 1
                min_dis = dis
        else:
            for j in range(len(ship_nonrepetitivelabel[i]) - 1):
                if (ship_nonrepetitivelabel[i][j + 1] == dc):
                    dis2 = 0
                    dis = dis1 + dis2
                    if (dis < min_dis):
                        local_1 = i
                        local_2 = j + 1
                        min_dis = dis
                    break
                elif (dc.endswith(ship_nonrepetitivelabel[i][j + 1])):  # 串前多识别
                    if (len(dc) >= 5):
                        dis2 = 5
                    else:
                        dis2 = dtw(ship_nonrepetitivelabel[i][j + 1], dc) + 10
                elif (ship_nonrepetitivelabel[i][j + 1].startswith(dc)):  # 串后漏识别
                    if (len(dc) >= 3):
                        dis2 = 5
                    else:
                        dis2 = dtw(ship_nonrepetitivelabel[i][j + 1], dc) + 10
                else:
                    dis2 = dtw(ship_nonrepetitivelabel[i][j + 1], dc) + 10
                dis = dis1 + dis2
                if (dis < min_dis):
                    local_1 = i
                    local_2 = j + 1
                    min_dis = dis
    # print(min_dis)
    confidence = exp(-min_dis / 10)
    match_result = ship_nonrepetitivelabel[local_1][0] + ship_nonrepetitivelabel[local_1][local_2]
    return match_result, confidence

    '''*************************************************************************************'''
    '''函数功能: 船名匹配_2                                                                    '''
    '''入参:             Ship_nonrepetitivelabel：非重复船名标签集                              '''
    '''                 Match_shipname：待匹配船名                                            '''
    '''                 Cc_dict：中文字符字典                                                  '''
    '''                 Cc_similarity_matrix：中文字符相似度矩阵                                '''
    '''                 Dc_similarity_matrix：数字字符相似度矩阵                                '''
    '''出参:                                                                                 '''
    '''返回值:           match_result：匹配结果                                                '''
    '''                 confidence：正确程度                                                  '''
    '''*************************************************************************************'''
def shipname_matching_2(Ship_nonrepetitivelabel, Match_shipname, Cc_dict, Cc_similarity_matrix,
                        Dc_similarity_matrix):
    global K
    ship_nonrepetitivelabel = Ship_nonrepetitivelabel
    match_shipname = Match_shipname
    cc_dict = Cc_dict
    cc_sm = Cc_similarity_matrix
    dc_sm = Dc_similarity_matrix

    cc = "".join(re.findall('[\u4e00-\u9fa5]', match_shipname))
    dc = re.sub("\D", "", match_shipname)
    # print(dc)

    min_dis = sys.maxsize
    dis1 = 0
    # 是否含有船名编号，1：含有，0：不含有
    has_digit = 1
    local_1 = 0
    local_2 = 0
    if 1==1:#先匹配最相似的船名，再从中进行船编号的匹配
        ####
        # 汉字相似度结果列表
        mindis1_ships = []
        K = int(K)
        if len(ship_nonrepetitivelabel) < K:
            K = len(ship_nonrepetitivelabel)
        print("当前K设置为：" + str(K))
        for i in range(len(ship_nonrepetitivelabel)):
            if (cc == ''):  # w未检测到汉字
                dis1 = 10
            else:
                if (ship_nonrepetitivelabel[i][0] == cc):
                    dis1 = 0

                else:
                    dis1 = chinesecharacter_dtw(ship_nonrepetitivelabel[i][0], cc, cc_dict, cc_sm) + 1
            #保存行下标和对应相似度
            mindis1_ships.append([i, dis1])
        #根据dis1排序
        mindis1_ships.sort(key = takeSecond)
        mindis1_K_ships = mindis1_ships[:K]
        print("船名最相似的" + str(K) + "行：" + str(mindis1_K_ships))

        for kk in range(K):
            i = mindis1_K_ships[kk][0]
            dis1 = mindis1_K_ships[kk][1]
            if (dc == ''):  # w未检测到数字
                dis2 = 10
                dis = dis1 + dis2
                if (dis < min_dis):
                    local_1 = i
                    local_2 = 1
                    min_dis = dis
                    has_digit = 0
            else:
                for j in range(len(ship_nonrepetitivelabel[i]) - 1):
                    ddcc = ship_nonrepetitivelabel[i][j + 1]
                    if not ddcc.isdigit():
                        continue

                    if (ddcc == dc):
                        dis2 = 0
                        dis = dis1 + dis2
                        if (dis < min_dis):
                            local_1 = i
                            local_2 = j + 1
                            min_dis = dis
                        break
                    elif (dc.endswith(ddcc)):  # 串前多识别
                        if (len(dc) >= 5):
                            dis2 = 0.5
                        else:
                            dis2 = digitcharacter_dtw(ddcc, dc, dc_sm) + 1
                    elif (ship_nonrepetitivelabel[i][j + 1].endswith(dc)):  # 串前多识别
                        if (len(dc) >= 4):
                            dis2 = 0.5
                        else:
                            dis2 = digitcharacter_dtw(ddcc, dc, dc_sm) + 1
                    elif (ship_nonrepetitivelabel[i][j + 1].startswith(dc)):  # 串后漏识别
                        if (len(dc) >= 3):
                            dis2 = 0.5
                        else:
                            dis2 = digitcharacter_dtw(ddcc, dc, dc_sm) + 1
                    elif (dc.startswith(ship_nonrepetitivelabel[i][j + 1])):  # 串后多识别
                        if (len(dc) >= 6):
                            dis2 = 0.5
                        else:
                            dis2 = digitcharacter_dtw(ddcc, dc, dc_sm) + 1
                    else:
                        dis2 = digitcharacter_dtw(ddcc, dc, dc_sm) + 1
                    dis = dis1 + dis2
                    if (dis < min_dis):
                        local_1 = i
                        local_2 = j + 1
                        min_dis = dis
                        #print(ship_nonrepetitivelabel[local_1][0]+ship_nonrepetitivelabel[local_1][local_2])
        print("最小距离：" + str(min_dis))
    ####
    if 1==0:#船名和船编号一起匹配

        for i in range(len(ship_nonrepetitivelabel)):
            if (cc == ''):  # w未检测到汉字
                dis1 = 10
            else:
                if (ship_nonrepetitivelabel[i][0] == cc):
                    dis1 = 0

                else:
                    dis1 = chinesecharacter_dtw(ship_nonrepetitivelabel[i][0], cc, cc_dict, cc_sm) + 1
            if (dc == ''):  # w未检测到数字
                dis2 = 10
                dis = dis1 + dis2
                if (dis < min_dis):
                    local_1 = i
                    local_2 = 1
                    min_dis = dis
                    has_digit = 0
            else:
                for j in range(len(ship_nonrepetitivelabel[i]) - 1):
                    if (ship_nonrepetitivelabel[i][j + 1] == dc):
                        dis2 = 0
                        dis = dis1 + dis2
                        if (dis < min_dis):
                            local_1 = i
                            local_2 = j + 1
                            min_dis = dis
                        break
                    elif (dc.endswith(ship_nonrepetitivelabel[i][j + 1])):  # 串前多识别
                        if (len(dc) >= 5):
                            dis2 = 0.5
                        else:
                            dis2 = digitcharacter_dtw(ship_nonrepetitivelabel[i][j + 1], dc, dc_sm) + 1
                    elif (ship_nonrepetitivelabel[i][j + 1].endswith(dc)):  # 串前多识别
                        if (len(dc) >= 4):
                            dis2 = 0.5
                        else:
                            dis2 = digitcharacter_dtw(ship_nonrepetitivelabel[i][j + 1], dc, dc_sm) + 1
                    elif (ship_nonrepetitivelabel[i][j + 1].startswith(dc)):  # 串后漏识别
                        if (len(dc) >= 3):
                            dis2 = 0.5
                        else:
                            dis2 = digitcharacter_dtw(ship_nonrepetitivelabel[i][j + 1], dc, dc_sm) + 1
                    elif (dc.startswith(ship_nonrepetitivelabel[i][j + 1])):  # 串后多识别
                        if (len(dc) >= 6):
                            dis2 = 0.5
                        else:
                            dis2 = digitcharacter_dtw(ship_nonrepetitivelabel[i][j + 1], dc, dc_sm) + 1
                    else:
                        dis2 = digitcharacter_dtw(ship_nonrepetitivelabel[i][j + 1], dc, dc_sm) + 1
                    dis = dis1 + dis2
                    if (dis < min_dis):
                        local_1 = i
                        local_2 = j + 1
                        min_dis = dis
                        #print(ship_nonrepetitivelabel[local_1][0]+ship_nonrepetitivelabel[local_1][local_2])
        #print(min_dis)
    confidence = exp(-min_dis / 10)
    if has_digit == 0:
        # 原船名库中只有船名，这时此条记录为string而不是list类型 原因在于txt_to_list函数
        if isinstance(ship_nonrepetitivelabel[local_1], list):
            match_result = ship_nonrepetitivelabel[local_1][0]
        elif isinstance(ship_nonrepetitivelabel[local_1], str):
            match_result = ship_nonrepetitivelabel[local_1]
    else:
        match_result = ship_nonrepetitivelabel[local_1][0] + ship_nonrepetitivelabel[local_1][local_2]
    return match_result, confidence
    '''*************************************************************************************'''
    '''函数功能: 生成文字图形                                                                   '''
    '''入参:             width：宽度                                                          '''
    '''                 white：白底黑字或黑底白字                                               '''
    '''                 Cc_dict：中文字符字典                                                  '''
    '''                 text：文本内容                                                        '''
    '''                 font：字体                                                           '''
    '''                 save_path：保存路径                                                   '''
    '''                 mode="rgb"：mode为RGB形式                                             '''
    '''出参:                                                                                 '''
    '''返回值:                                                                               '''
    '''*************************************************************************************'''
def make_text_image(width, white, text, font, save_path, mode="rgb"):
    """
    生成一个文字图形, white=1，表示白底黑字，否则为黑底白字
    """

    # 字体可能要改
    # linux查看支持的汉字字体 # fc-list :lang=zh
    ft = font
    w, h = ft.getsize(text)

    # 计算要几行
    lines = math.ceil(w / width) + 1
    height = h * lines + h

    # 一个汉字的宽度
    one_zh_width, h = ft.getsize("中")

    if len(mode) == 1:  # L, 1
        background = (255)
        color = (0)
    if len(mode) == 3:  # RGB
        background = (255, 255, 255)
        color = (0, 0, 0)
    if len(mode) == 4:  # RGBA, CMYK
        background = (255, 255, 255, 255)
        color = (0, 0, 0, 0)

    newImage = Image.new(mode, (width, height), background if white else color)
    draw = ImageDraw.Draw(newImage)

    # 分割行
    text = text + " "  # 处理最后少一个字问题
    text_list = []
    text_list = text.split('\n')

    # start = 0
    # end = len(text) - 1
    # while start < end:
    #     for n in range(end):
    #         try_text = text[start:start + n]
    #         w, h = ft.getsize(try_text)
    #         if w + 2 * one_zh_width > width:
    #             break
    #     text_list.append(try_text[0:-1])
    #     start = start + n - 1

    print(text_list)

    i = 0
    for t in text_list:
        draw.text((one_zh_width, i * h), t, color if white else background, font=ft)
        i = i + 1

    newImage.save(save_path)


def resize_canvas(org_image, add_image, new_image_path, text, font, mode):

    org_im = Image.open(org_image)
    org_width, org_height = org_im.size

    mode = org_im.mode

    make_text_image(org_width, 0, text, font, add_image, mode)

    add_im = Image.open(add_image)
    add_width, add_height = add_im.size

    mode = org_im.mode

    newImage = Image.new(mode, (org_width, org_height + add_height))

    newImage.paste(org_im, (0, 0, org_width, org_height))
    newImage.paste(add_im, (0, org_height, add_width, add_height + org_height))
    newImage.save(new_image_path)


def ocr_visualization(Input_path1, Input_path2, Output_path, Tmp_Path):
    input_path1 = DeepCopy(Input_path1)
    input_path2 = DeepCopy(Input_path2)
    output_path = DeepCopy(Output_path)
    tmp_path = DeepCopy(Tmp_Path)

    final_res = txt_to_listsstr(input_path1 + 'Output4.txt')
    files = os.listdir(input_path2)

    for i in range(len(files)):  # 遍历文件夹
        print("输出第" + str(i + 1) + "张图片")
        if files[i].split('_')[0] == final_res[i][0]:
            font = ImageFont.truetype("./msyh.ttc", 10)
            if final_res[i][5] != 'False':
                text = final_res[i][1] + '_' + final_res[i][6] + '\n' + final_res[i][2] + '_' + str(
                    round(float(final_res[i][4]), 4)) + '\n' + final_res[i][3] + '_' + str(
                    round(float(final_res[i][5]), 4))
            elif final_res[i][3] == '未能识别':
                text = final_res[i][1] + '_' + 'False' + '\n' + final_res[i][2] + '_' + str(
                    round(float(final_res[i][4]), 4)) + '\n' + final_res[i][3] + '_' + '0'
            else:
                text = final_res[i][1] + '_' + final_res[i][6] + '\n' + final_res[i][2] + '_' + str(
                    round(float(final_res[i][4]), 4)) + '\n' + final_res[i][3] + '_' + '0'
            img_path = input_path2 + files[i]

            re_path = output_path + final_res[i][0] + '_' + final_res[i][1] + '_' + final_res[i][3] + '_' + \
                      final_res[i][4] + '_' + final_res[i][6] + files[i][-4:]
            add_img = tmp_path + files[i]
            resize_canvas(img_path, add_img, re_path, text, font, 'rgb')

'''*************************************************************************************'''
'''函数功能: 建立字典与相似度矩阵                                                             '''
'''*************************************************************************************'''
# 建立字典与相似度矩阵
if (1 == 1):
    def gen_simatrix():
        if (1 == 1):  # 建立数字相似度矩阵
            dc_matrix = make_similaritymatrix_of_digitcharacter()  # 建立数字相似度矩阵
            sio.savemat(PATH_R0 + 'Dc_similaritmatrix.mat', {'data': dc_matrix})
            data = sio.loadmat(PATH_R0 + 'Dc_similaritmatrix.mat')
            Dc_similaritmatrix = data['data']
            print(Dc_similaritmatrix)

        if (1 == 1):  # 建立汉字字典与相似度矩阵
            # Dict=load(PATH_R0+'Cc_dict.npy',allow_pickle=True).item()
            # data=sio.loadmat(PATH_R0+'Cc_similaritmatrix.mat')
            # cc_matrix=data['data']
            Dict = []
            cc_matrix = []
            # 更新标签汉字
            Ship_label_list = txt_to_listsstr(PATH_R0 + 'Ship_labels.txt')
            for i in range(len(Ship_label_list)):
                Dict, cc_matrix = make_similaritymatrix_of_chinesecharacter(Dict, cc_matrix, Ship_label_list[i][1])
            # 更新ocr识别结果汉字
            Ocr_results_list = txt_to_listsstr(PATH_R0 + 'Ocr_results.txt')
            for i in range(len(Ship_label_list)):
                Dict, cc_matrix = make_similaritymatrix_of_chinesecharacter(Dict, cc_matrix, Ocr_results_list[i][1])
            sio.savemat(PATH_R0 + 'Cc_similaritmatrix.mat', {'data': cc_matrix})
            data = sio.loadmat(PATH_R0 + 'Cc_similaritmatrix.mat')
            Cc_similaritmatrix = data['data']
            print(len(Cc_similaritmatrix))

            save(PATH_R0 + 'Cc_dict.npy', Dict)
            cc_dict = load(PATH_R0 + 'Cc_dict.npy', allow_pickle=True)
            if cc_dict != None:
                Cc_dict = cc_dict.item()
                print(len(Cc_dict))

'''*************************************************************************************'''
'''函数功能: 根据数据库识别结果更新汉字字典与相似度矩阵                                           '''
'''*************************************************************************************'''
# 根据数据库识别结果更新汉字字典与相似度矩阵
if (1 == 1):
    def update_simatrix():
        Dict = []
        cc_dict = load(PATH_R0 + 'Cc_dict.npy', allow_pickle=True)
        if cc_dict != None:
            Dict = cc_dict.item()
            print('更新前字典字数：' + str(len(Dict)))
        data = sio.loadmat(PATH_R0 + 'Cc_similaritmatrix.mat')
        cc_matrix = data['data']
        print('更新前汉字相似度矩阵宽度：' + str(len(cc_matrix)))
        Similar_cc_pair_list = output_similar_chinesecharacter(Dict, cc_matrix)
        print('更新前形近字对数：' + str(len(Similar_cc_pair_list)))
        # Dict,cc_matrix=make_similaritymatrix_of_chinesecharacter([],[],'但是公司的是东方化工')
        Output = txt_to_listsstr(PATH_R0 + 'Error3.txt')
        # Ocr_results_list=txt_to_listsstr(PATH_R0+'Ocr_results.txt')
        for i in range(len(Output)):
            if (i > -1):
                if (i % 100 == 0):
                    print(i)
                # print(Ship_label_list[i][1])
                # print(Ocr_results_list[i][1])
                Dict, cc_matrix = update_sm_of_cc_basedon_label_and_result(Dict, cc_matrix, Output[i][1], Output[i][2])
                # Similar_cc_pair_list=output_similar_chinesecharacter(Dict,cc_matrix)
                # print(len(Similar_cc_pair_list))
        Similar_cc_pair_list = output_similar_chinesecharacter(Dict, cc_matrix)
        lists_to_txt(Similar_cc_pair_list, PATH_R0 + 'Similar_cc_pair_list.txt', Spacer='   ', Mode='w')
        print('更新后形近字对数：' + str(len(Similar_cc_pair_list)))
        sio.savemat(PATH_R0 + 'Cc_similaritmatrix.mat', {'data': cc_matrix})
        save(PATH_R0 + 'Cc_dict.npy', Dict)
        cc_dict = load(PATH_R0 + 'Cc_dict.npy', allow_pickle=True)
        if cc_dict != None:
            Dict = cc_dict.item()
            print('更新后字典字数：' + str(len(Dict)))
        data = sio.loadmat(PATH_R0 + 'Cc_similaritmatrix.mat')
        cc_matrix = data['data']
        print('更新后汉字相似度矩阵宽度：' + str(len(cc_matrix)))

'''*************************************************************************************'''
'''函数功能: 最初识别率                                                                     '''
'''*************************************************************************************'''
# 最初识别率
if (1 == 1):
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
# 去拼音识别率
if (1 == 0):
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
        label_cc = "".join(re.findall('[\u4e00-\u9fa5]', Ship_label_list[i][1]))
        label_dc = re.sub("\D", "", Ship_label_list[i][1])
        result_cc = "".join(re.findall('[\u4e00-\u9fa5]', Ocr_results_list[i][1]))
        result_dc = re.sub("\D", "", Ocr_results_list[i][1])

        List.append(Ship_label_list[i][0])
        List.append(label_cc + label_dc)
        List.append(result_cc + result_dc)
        List.append(Ocr_results_list[i][2])

        #if label_cc == result_cc and label_dc == result_dc
        if  label_dc == result_dc:
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
    lists_to_txt(Output, PATH_R0 + 'Output2.txt', Spacer='   ', Mode='w')
    lists_to_txt(error, PATH_R0 + 'Error2.txt', Spacer='   ', Mode='w')
# 0-1dtw识别率
if (1 == 0):
    Ship_label_list = txt_to_listsstr(PATH_R0 + 'Ship_labels.txt')
    Ocr_results_list = txt_to_listsstr(PATH_R0 + 'Ocr_results.txt')
    Ship_nonrepetitivelabel = txt_to_listsstr(PATH_SHARE + 'Ship_nonrepetitivelabel.txt')
    # print(Ship_label_list[0])
    # print(Ocr_results_list[0])
    Output = []
    error = []
    true_number = 0
    # f1 = open(PATH_R0+'Output.txt', 'a', encoding='utf-8')
    # f2 = open(PATH_R0+'error.txt', 'a', encoding='utf-8')
    for i in range(len(Ocr_results_list)):
        print(i)
        # if(i==100): break
        List = []
        label_cc = "".join(re.findall('[\u4e00-\u9fa5]', Ship_label_list[i][1]))
        label_dc = re.sub("\D", "", Ship_label_list[i][1])
        label = label_cc + label_dc
        result_cc = "".join(re.findall('[\u4e00-\u9fa5]', Ocr_results_list[i][1]))
        result_dc = re.sub("\D", "", Ocr_results_list[i][1])
        result = result_cc + result_dc
        # print(result)
        if (result != '未能识别'):
            match_result, confidence = shipname_matching(Ship_nonrepetitivelabel, result)
            List.append(Ship_label_list[i][0])  # 样本编号
            List.append(label_cc + label_dc)  # 标签
            List.append(result_cc + result_dc)  # ocr识别结果
            List.append(match_result)  # 匹配结果
            List.append(Ocr_results_list[i][2])  # ocr识别结果置信度
            List.append(confidence)  # 匹配结果置信度

            if (label == match_result):
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
        else:
            List.append(Ship_label_list[i][0])
            List.append(label_cc + label_dc)
            List.append('未能识别')
            List.append('未能识别')
            List.append(str(0))
            List.append('False')
            List.append(str(true_number))
            List.append(str(i + 1))
            Output.append(List)
            error.append(List)
    lists_to_txt(Output, PATH_R0 + 'Output2.txt', Spacer='   ', Mode='w')
    lists_to_txt(error, PATH_R0 + 'Error2.txt', Spacer='   ', Mode='w')
# 数字段前段后增强0-1dtw识别率
if (1 == 0):
    Ship_label_list = txt_to_listsstr(PATH_R0 + 'Ship_labels.txt')
    Ocr_results_list = txt_to_listsstr(PATH_R0 + 'Ocr_results.txt')
    Ship_nonrepetitivelabel = txt_to_listsstr(PATH_SHARE + 'Ship_nonrepetitivelabel.txt')
    # print(Ship_label_list[0])
    # print(Ocr_results_list[0])
    Output = []
    error = []
    true_number = 0
    # f1 = open(PATH_R0+'Output.txt', 'a', encoding='utf-8')
    # f2 = open(PATH_R0+'error.txt', 'a', encoding='utf-8')
    for i in range(len(Ocr_results_list)):

        if (i > -1):
            print(i)
            List = []
            label_cc = "".join(re.findall('[\u4e00-\u9fa5]', Ship_label_list[i][1]))
            label_dc = re.sub("\D", "", Ship_label_list[i][1])
            label = label_cc + label_dc
            result_cc = "".join(re.findall('[\u4e00-\u9fa5]', Ocr_results_list[i][1]))
            result_dc = re.sub("\D", "", Ocr_results_list[i][1])
            result = result_cc + result_dc
            # print(label)
            # print(result)
            if (result != '未能识别'):
                match_result, confidence = shipname_matching_1(Ship_nonrepetitivelabel, result)
                # print(match_result)
                List.append(Ship_label_list[i][0])  # 样本编号
                List.append(label_cc + label_dc)  # 标签
                List.append(result_cc + result_dc)  # ocr识别结果
                List.append(match_result)  # 匹配结果
                List.append(Ocr_results_list[i][2])  # ocr识别结果置信度
                List.append(confidence)  # 匹配结果置信度

                if (label == match_result):
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
            else:
                List.append(Ship_label_list[i][0])
                List.append(label_cc + label_dc)
                List.append('未能识别')
                List.append('未能识别')
                List.append(str(0))
                List.append('False')
                List.append(str(true_number))
                List.append(str(i + 1))
                Output.append(List)
                error.append(List)
    lists_to_txt(Output, PATH_R0 + 'Output3.txt', Spacer='   ', Mode='w')
    lists_to_txt(error, PATH_R0 + 'Error3.txt', Spacer='   ', Mode='w')
# 数字段前段后增强相似度dtw识别率
if (1 == 1):
    def final_accuracy():
        Ship_label_list = txt_to_listsstr(PATH_R0 + 'Ship_labels.txt')
        Ocr_results_list = txt_to_listsstr(PATH_R0 + 'Ocr_results.txt')
        Ship_nonrepetitivelabel = txt_to_listsstr(PATH_SHARE + 'Ship_nonrepetitivelabel.txt')
        Dict = []
        cc_dict = load(PATH_R0 + 'Cc_dict.npy', allow_pickle=True)
        if cc_dict != None:
            Dict = cc_dict.item()
        data = sio.loadmat(PATH_R0 + 'Cc_similaritmatrix.mat')
        Cc_matrix = data['data']

        data = sio.loadmat(PATH_R0 + 'Dc_similaritmatrix.mat')
        Dc_matrix = data['data']

        # print(Ship_label_list[0])
        # print(Ocr_results_list[0])
        Output = []
        error = []
        true_number = 0
        # f1 = open(PATH_R0+'Output.txt', 'a', encoding='utf-8')
        # f2 = open(PATH_R0+'error.txt', 'a', encoding='utf-8')
        for i in range(len(Ocr_results_list)):

            if (i > -1):
                print(i)
                List = []
                label_cc = "".join(re.findall('[\u4e00-\u9fa5]', Ship_label_list[i][1]))
                label_dc = re.sub("\D", "", Ship_label_list[i][1])
                label = label_cc + label_dc
                result_cc = "".join(re.findall('[\u4e00-\u9fa5]', Ocr_results_list[i][1]))
                result_dc = re.sub("\D", "", Ocr_results_list[i][1])
                result = result_cc + result_dc
                # print(label)
                # print(result)
                if (result != '未能识别'):
                    #正向文字匹配一次
                    match_result, confidence = shipname_matching_2(Ship_nonrepetitivelabel, result, Dict, Cc_matrix,
                                                                   Dc_matrix)

                    ##识别结果中可能会有倒序
                    # 反向文字匹配一次
                    match_result2, confidence2 = shipname_matching_2(Ship_nonrepetitivelabel, result[::-1], Dict, Cc_matrix,
                                                                   Dc_matrix)
                    if len(match_result2) == len(result) and confidence2 > confidence:
                        confidence = confidence2
                        match_result = match_result2
                    # 最匹配的结果也可能有倒序
                    match_result = reverse_name(match_result)
                    # print(match_result)
                    List.append(Ship_label_list[i][0])  # 样本编号
                    List.append(label_cc + label_dc)  # 标签
                    List.append(result_cc + result_dc)  # ocr识别结果
                    List.append(match_result)  # 匹配结果
                    List.append(Ocr_results_list[i][2])  # ocr识别结果置信度
                    List.append(confidence)  # 匹配结果置信度

                    if (label == match_result):
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
                else:
                    List.append(Ship_label_list[i][0])
                    List.append(label_cc + label_dc)
                    List.append('未能识别')
                    List.append('未能识别')
                    List.append(str(0))
                    List.append(str(0))
                    List.append('False')
                    List.append(str(true_number))
                    List.append(str(i + 1))
                    Output.append(List)
                    error.append(List)
        lists_to_txt(Output, PATH_R0 + 'Output4.txt', Spacer='   ', Mode='w')
        lists_to_txt(error, PATH_R0 + 'Error4.txt', Spacer='   ', Mode='w')
'''*************************************************************************************'''
'''函数功能: 识别结果可视化                                                                 '''
'''*************************************************************************************'''
# 识别结果可视化
if (1 == 1):
    def viualize_result(FLAG):
        if FLAG:
            Ocr_Visualization_Path = PATH_R0 + 'ocr_result\\'
            Tmp_Path = PATH_R0 + 'tmp_pic\\'
            if not os.path.exists(Tmp_Path):
                os.makedirs(Tmp_Path)
            if not os.path.exists(Ocr_Visualization_Path):
                os.makedirs(Ocr_Visualization_Path)
            ocr_visualization(PATH_R0, PATH_R0 + 'Ship_regularizedname_database\\', Ocr_Visualization_Path, Tmp_Path)
'''*************************************************************************************'''
'''函数功能: 纠错主函数                                                                     '''
'''*************************************************************************************'''
# 纠错主程序
def correct_main():
    print("开始执行纠错程序...")
    # 最初识别率
    initial_accuracy()
    # 建立字典与相似度矩阵
    gen_simatrix()
    # 根据数据库识别结果更新汉字字典与相似度矩阵
    update_simatrix()
    # 数字段前段后增强相似度dtw识别率
    final_accuracy()
    # 识别结果可视化
    viualize_result(FLAG)