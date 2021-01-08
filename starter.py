import Ship_name_recognition as ship_recognition
import Ship_name_recorrect as ship_recorrect
import configparser
import os
import argparse

## 全局变量
PATH_SHARE = os.path.abspath(os.path.dirname(__file__)) + "\\"
#未设置原始待识别图片文件夹路径时，默认采用当前目录下的data文件夹
PATH_R0 = os.path.abspath(os.path.dirname(__file__)) + "\\data\\"
FLAG = True
K = 10

# 程序入口
if __name__ == '__main__':
    if (1==0):
        ## 1.读取配置文件
        root_dir = os.path.abspath('.')
        configpath = os.path.join(root_dir, "config.ini")

        cf = configparser.ConfigParser()
        cf.read(configpath, encoding='utf-8')  # 读取配置文件
        secs = cf.sections()  # 获取文件中所有的section，并以列表的形式返回

        PATH_R0 = cf.get("work_dir", "PATH_R0")

        if len(PATH_R0) > 0:
            PATH_R0 = PATH_R0 + "\\"
        FLAG = cf.get("visualization", "FLAG")
        K = cf.get("similarK", "K")

    if (1==1):
        ## 2.argparse方法读取命令行参数
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-d',
            '--dir',
            type=str,
            default=os.path.abspath(os.path.dirname(__file__)) + "\\data\\new",
            help='The root directory of images')
        parser.add_argument(
            '-v',
            '--visual',
            type=str,
            default="true",
            help='Whether need visualization')

        parser.add_argument(
            '-k',
            type=str,
            default="10",
            help='K most similar results')

        args = parser.parse_args()
        PATH_R0 = args.dir + "\\"
        K = args.k
        FLAG = args.visual

    print("识别路径为：" + PATH_R0)
    ship_recognition.PATH_R0 = PATH_R0
    ship_recognition.PATH_R1 = PATH_R0 + 'Ship_name_database\\'  # 船原始数据库地址
    ship_recognition.PATH_W1 = PATH_R0 + 'Ship_regularizedname_database\\'  # 船规则名称数据库地址
    ship_recognition.PATH_W2 = PATH_R0 + 'Ship_number_database\\'  # 船编号数据库地址
    ship_recognition.PATH_W3 = PATH_R0 + 'Ship_preProcess_database\\'  # 预处理结果数据库地址
    ship_recorrect.PATH_R0 = PATH_R0
    ship_recognition.FLAG = FLAG
    ship_recorrect.K = K

    ship_recognition.rec_main()
    ship_recorrect.correct_main()



