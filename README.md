# Ship_name_recognition
### 环境配置
python版本低于3.8

#### 1.安装PaddlePaddle v2.0
```
python3 -m pip install --upgrade pip

如果您的机器安装的是CUDA9或CUDA10，请运行以下命令安装
python3 -m pip install paddlepaddle-gpu==2.0.0b0 -i https://mirror.baidu.com/pypi/simple

如果您的机器是CPU，请运行以下命令安装

python3 -m pip install paddlepaddle==2.0.0b0 -i https://mirror.baidu.com/pypi/simple
```
#### 2.安装第三方库
```
python3 -m pip install -r requirements.txt
```
然后根据提示安装缺失的库 ```python3 -m pip install [缺失库]```



### 目录结构
```
Ship_name_recognition.py - 船名识别模块
Ship_name_reccorrect.py - 船名纠错模块
starter.py - 项目启动模块，务必运行此文件开始识别程序
config.ini - 程序配置文件，详细配置见内
msyh.ttc - 可视化所用字体
Ship_nonrepetitivelabel.txt - 目前已知所有船名总库，包括从船名图片提取和从txt去重提取
```
识别目录下生成的文件
```
Ship_name_database - 原始待识别文件夹，该文件夹是在对指定目录下的图片运行识别程序后生成，自动将原始图片收纳进来，下次对相同路径执行运行识别程序，则自动从该文件夹读取
Ship_number_database - 图片按照数字顺序生成的文件夹
Ship_preProcess_database - 预处理图片结果文件夹
Ship_regularizedname_database - 图片规则化命名文件夹
tmp_pic - 临时图片文件夹
ocr_result - 可视化结果文件夹

**************************************************
Error3.txt - 首次识别结果（未纠正）中未正确识别的部分
Output3 - 首次识别的所有结果（未纠正）

其中各列含义如下：
序号     预期正确结果   识别结果      置信度                        是否识别正确标志位      截至目前识别正确总数       截至目前识别图片总数
000001   济宁港        济宁         0.9090464115142822             False                     0                      1
*****************************************************

*****************************************************
Error4.txt - 识别并纠正后仍错误的部分
Output4.txt - 识别并纠正后的所有结果

其中各列含义如下：
序号     预期正确结果   识别结果   纠正后结果     识别置信度                纠正置信度                    最终结果是否正确标志位      截至目前正确总数       截至目前图片总数
000001   济宁港        济宁      济           0.9090464115142822   0.30119421191220214     False                                       0                               1
******************************************************
Ship_labels.txt - 本次识别路径下的所有船名标签
Ocr_results.txt - 原始识别输出
```

### 快速使用
```
python3 starter.py
```

### 模型训练

训练须在linux下进行：
#### 1.train.py用来生成数据集
```
git clone https://github.com/PaddlePaddle/PaddleOCR
```
##### 生成训练数据
    1）train文件夹（train_0001.jpg等）
    2）rec_gt_train.txt  （将图片路径和图片标签用 \t 分割）
        图像文件名                       图像标注信息
        train/train_0003.jpg	       苏运货068
##### 生成测试数据
    1）test文件夹（test_0001.jpg等）
    2）rec_gt_test.txt  （将图片路径和图片标签用 \t 分割）
        图像文件名                       图像标注信息
        test/test_0003.jpg	           苏运货068

#### 2. 文件结构
    将train文件夹和rec_gt_train.txt放至PaddleOCR/train_data文件夹下
    将test文件夹和rec_gt_test.txt放至PaddleOCR/train_data文件夹下
		
	最终训练集应有如下文件结构：
    |-train_data
        |- rec_gt_train.txt
        |- train
            |- train_001.jpg
            |- train_002.jpg
            |- train_003.jpg
            | ...
    
    最终测试集应有如下文件结构：
    |-train_data
        |- rec_gt_test.txt
        |- test
            |- test_001.jpg
            |- test_002.jpg
            |- test_003.jpg
            | ...



#### 3.开始训练
```

cd PaddleOCR/
# 下载MobileNetV3的预训练模型
wget -P ./pretrain_models/ https://paddleocr.bj.bcebos.com/ch_models/ch_rec_mv3_crnn_enhance.tar
# 解压模型参数
cd pretrain_models
tar -xf ch_rec_mv3_crnn_enhance.tar && rm -rf ch_rec_mv3_crnn_enhance.tar

python3 tools/train.py -c configs/rec/rec_chinese_lite_train.yml 2>&1 | tee train_rec.log

如果安装的是cpu版本，请将配置文件rec_chinese_lite_train.yml中的 use_gpu 字段修改为false
```

```
依赖丢失解决：
sudo apt-get install python3-pip
sudo apt-get install python3-yaml

pip3 install 安装运行过程中提示缺少的module
```


> 本项目自带的训练模型`modules/rec_crnn`所用训练集为`data/new`，测试集为`data1/new` 
>
> 生成数据的同时需要生成自定义汉字字典`ship_character_dict.txt` 并修改训练配置文件`rec_chinese_lite_train.yml`中的`character_dict_path`字段指向自己生成的字典

#### 4.模型转换
```
python3 tools/export_model.py -c configs/rec/rec_chinese_lite_train.yml -o Global.checkpoints=./output/rec_CRNN/best_accuracy Global.save_inference_dir=./inference/rec_crnn/
```

#### 5.自训练模型的使用

将转换后生成的所有文件（model params）放入`modules/rec_crnn`文件夹中


