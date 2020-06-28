#-*- coding:utf-8 -*-

import os
import sys
import re
import string
import zhon.hanzi
import jieba

def getNewSougouQData(path = 'sougou/SogouQ/'):
    # 检查处理之后的文件夹，不存在则创建
    dealt_dir = 'dealt/'
    dealt_dir_path = os.path.join(path, dealt_dir)
    if os.path.exists(dealt_dir_path):
        pass
        # return
    else:
        os.mkdir(dealt_dir_path)

    # 处理原始文件
    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)
        # 过滤掉文件夹
        if os.path.isdir(file_path):
            continue
        dealt_file_path = os.path.join(dealt_dir_path, file+'.dealt')
        if os.path.exists(dealt_file_path):
            continue
        with open(dealt_file_path, 'w', encoding = 'utf-8') as f_w:
            print(file)
            with open(file_path, 'r', encoding = 'ansi') as f_r:
                for item in f_r:
                    item = item.replace(' ', '\t');
                    f_w.write(item)


def deal_str(sstring = ''):
    # sstring = '[FIFA2006好看 ，+《soul》 北京欢迎]'
    # print('原始词：', sstring)
    #包含.认为是网址，包括高级搜索url:
    if '.' in sstring:
        return 
    result = []
    # 去除 []
    sstring = sstring.replace('[', '').replace(']', '')
    # sstring = re.search(r'(?<=\[)(.*)(?=\])', sstring).group()
    # print('去掉[]之后：', sstring)

    # 处理书籍或者影视作品
    str1 = re.findall(r'《(.*?)》', sstring)
    if str1:
        # 处理作品中一些不规范的搜索，各种标点符号，包括中文和英文：
        str1 = [re.sub(r'[{}]+'.format(zhon.hanzi.punctuation), '', s) for s in str1] 
        str1 = [re.sub(r'[{}]+'.format(string.punctuation), '', s) for s in str1]   
        result.extend(str1)
        # 去掉《》和作品
        sstring = re.sub(r'《.*?》', '', sstring) 

    # 处理高级搜索+
    str_list = sstring.split('+')
    # 过滤掉空字符串
    str_list = list(filter(None, str_list))

    #处理空格
    temp = []
    for s in str_list:
        temp.extend(s.split(' '))
    temp = list(filter(None, temp))
    str_list = temp

    # 处理一些不规范的搜索，各种标点符号，包括中文和英文：
    str_list = [re.sub(r'[{}]+'.format(zhon.hanzi.punctuation), '', s) for s in str_list] 
    str_list = [re.sub(r'[{}]+'.format(string.punctuation), '', s) for s in str_list]     
    # 过滤掉空字符串
    str_list = list(filter(None, str_list))
    result.extend(str_list)

    # 规范化处理之后将英文数字和中文分开
    temp_result = result[:]
    for item in temp_result:
        eng_num = re.search(r'([a-zA-Z0-9]+)', item)
        if eng_num:
            # 删去原词
            result.remove(item)
            # 加入英文和数字
            result.extend(eng_num.groups())
            # 找出剩下的中文词
            chinese = re.sub(r'[a-zA-Z0-9]+', '', item)
            result.append(chinese)

    result = list(filter(None, result))
    # print('预处理之后：', result, '\n')
    # return result

    temp_result = result[:]
    for item in temp_result:
        eng_num = re.search(r'([a-zA-Z0-9]+)', item)
        #如果是中文则分词
        if not eng_num:
            # 删去原词
            result.remove(item)
            # words= jieba.lcut_for_search(item) #搜索引擎模式
            words = jieba.lcut(item,cut_all=False,HMM=True) # 精确模式
            result.extend(words)
            # # 如果原查询词没在分词列表里，则加入
            # if item not in words:
            #     result.append(item) 
   
    # 过滤掉空字符串
    result = list(filter(None, result))
    # print('分词之后：', result, '\n\n')
    return result

def loadSougouQData(path = 'sougou/SogouQ/dealt/'):
    user=[]
    keyword=[]
    rank=[]
    order=[]
    url=[]
    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            continue
        with open(file_path, 'r', encoding = 'utf-8') as f:
            for item in f:
                item = item.split('\t')
                # print(item)
                #格式不正确丢弃
                if len(item) != 5:
                    continue
                # print(item)
                word_list = deal_str(item[1])
                if not word_list:
                    continue
                keyword.append(word_list)
                user.append(item[0])
                rank.append(item[2])
                order.append(item[3])
                url.append(item[4])
    return user, keyword, rank, order, url

if __name__ == '__main__':
    # path 是查询文件路径
    getNewSougouQData(path = 'sougou/SogouQ/')
    # sys.exit()

    # path是处理之后的文件路径
    user, keyword, rank, order, url = loadSougouQData(path = 'sougou/SogouQ/dealt/')