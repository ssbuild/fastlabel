#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

'''
fastlabel 标注数据批量导出及合并工具
'''


import argparse
import re
import json
import time
import os
import sys
import sqlite3

# 定义一个类，用于导出sqlite3数据库
class ExportTool():
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)

    def export_data(self, project_name, file_name, fidlists=None):
        '''
        查询项目名
        select id, project_name, type from project where project_name = 'name'

        查询实体字典
        select id, label_name from label_entity where project_id = pid

        查询项目总样本数
        select count(*) from sentense where project_id = pid

        查询样本句子
        select id, sentense from sentense where project_id = pid and id >= fidlist[0] and id<=fidlist[1]

        查询单条样本标注结果
        select id, label_entity_id, start_pos, end_pos
        from label_sentense where project_id = pid and sentense_id = sid
        order by start_pos

        截取位置: ner = txt[start_pos: end_pos]
        '''

        cur_proj = self.conn.execute("select id from project where project_name = '%s'" % project_name)    
        pid = cur_proj.fetchone()[0]

        cur_label = self.conn.execute("select id, label_name from label_entity where project_id = %d" % pid)
        label_dict = {}
        for label in cur_label:
            label_dict[label[0]] = label[1]

        #if fidlists is None:
        #    sqltxt = "select id, sentense from sentense where project_id = %d " % (pid)
        #else:
        dats = []
        for fidlist in fidlists:
            sqltxt = "select id, sentense from sentense where project_id = %d  and id >= %d and id<=%d " % (pid, fidlist[0], fidlist[1])
            cur_sentense = self.conn.execute(sqltxt)

            # 遍历 cur_sentense 数据表
            for sentense in cur_sentense:
                dat = {}
                sid = sentense[0]
                txt = sentense[1]
                #f.write('%d\t%s\t' % (sid, txt))
                dat['id'] = sid
                dat['text'] = txt

                # 查询样本标注结果
                sql = ("select id, label_entity_id, start_pos, " + 
                        "end_pos from label_sentense "+
                        "where project_id = %d and sentense_id = %d order by start_pos") % (pid, sid)
                cur_label_sentense = self.conn.execute(sql)

                # 遍历样本标注结果
                labels = {}
                for label_sentense in cur_label_sentense:
                    lid = label_sentense[0]
                    label_entity_id = label_sentense[1]
                    start_pos = label_sentense[2]
                    end_pos = label_sentense[3]

                    # 截取位置: ner = txt[start_pos: end_pos]
                    ner = txt[start_pos: end_pos]
                    
                    # 根据标注结果的id，查询标注结果的名称
                    label_name = label_dict[label_entity_id]

                    if label_name in labels:
                        # labels[label_name].append((start_pos, end_pos, ner))
                        if ner in labels[label_name]:
                            if not (start_pos, end_pos) in labels[label_name][ner]:
                                labels[label_name][ner].append((start_pos, end_pos))
                        else:
                            labels[label_name][ner] =[(start_pos, end_pos)]
                    else:
                        labels[label_name] = {ner:[(start_pos, end_pos)]}

                #dat['entities'] = json.loads(json.dumps(labels,sort_keys=True))
                dat['label'] = json.loads(json.dumps(labels,sort_keys=True))
                dats.append(dat)

        self.conn.close()
        return dats
       

'''
# 把下列格式的数据拆分成多个列表：
'24001-24300' ==> [[24001, 24300]]
'21601-22200、26401-27000、30001-30600' ==> [[21601, 22200],[26401, 27000], [30001, 30600]]
'27601-27810,28801-29400' ==> [[27601, 27810], [28801, 29400]]
'''
def split_range(range_str):
    range_str = range_str.replace('、', ',').replace('，', ',')
    range_list = range_str.split(',')
    range_list = [r.split('-') for r in range_list]
    range_list = [[int(r[0]), int(r[1])] for r in range_list]
    return range_list

# 提取文件名中的 号码段
# 'O:\中开\工作日志\2022年\数据标注\团队数据标注\signed-data\21001-21600\data.db' ==> '21001-21600'
def extract_dir_name(file_name):
    dir_name = file_name.split('\\')[-2]
    return dir_name

# 遍历文件夹中的子目录，返回子目录下的*.db文件名，返回一个生成器
def get_db_file_list(dir_name): 
    for root, dirs, files in os.walk(dir_name):
        for file in files:
            if file.endswith('.db'):
                yield os.path.join(root, file)

'''
# 批量导出数据
    参数： dir_name 目录名

先遍历目录，提取目录中的*.db文件名
再遍历*.db文件，提取文件名中的号码段fid，比如： 'O:\中开\工作日志\2022年\数据标注\团队数据标注\signed-data\21001-21600\data.db' ==> '21001-21600'
*.db文件即为sqlite3数据库名；
提取的号码段fid为要导出的数据ID范围
使用ExportTool类中的export_data()方法，导出ID范围的数据，
提取后的文件保存到当前目录下，文件名为：'21001-21600.txt'

'''
def export_datas(dir_name, project_name='', outfname='alldata.txt'):
    start = time.time()
    print('开始导出[%s]项目数据...%s'% (project_name, dir_name))
    file_list = get_db_file_list(dir_name)
    
    alldat = []

    for file_name in file_list:
        print('正在导出: %s' % file_name)
        # 提取文件名中的号码段
        fid = extract_dir_name(file_name)
        # 提取号码段
        range_list = split_range(fid)
        print('号码段: %s' % range_list)
        
        # 导出数据
        export_tool = ExportTool(file_name)
        #outfname = '%s.txt' % range_list
        #print('导出文件名：%s' % outfname)
        
        dat = export_tool.export_data(project_name, outfname, range_list)
        alldat.extend(dat)

    # todo: 过滤重复的记录
    '''
    '''
    tdat = map(str, alldat)
    tdat = list(set(tdat))
    alldat = map(eval, tdat)

    def dict2list(dat):
        ret = []
        for k in sorted(dat.keys()):
            v = dat[k]
            if type(v)==dict:
                v = dict2list(v)
            if type(v)==list:
                v = tuple(v)
            ret.append((k, v))
        return tuple(ret)

    '''
    tlist = [dict2list(d) for d in alldat]
    print(tlist[0])

    tdat = [dict(d) for d in set(tlist)]
    print(tdat[0])
    '''

    # alldat 按照号码段排序
    alldat = sorted(alldat, key=lambda x: x['id'])

    # 写入文件
    with open(outfname, 'w', encoding='utf-8') as f:
        for dat in alldat:
            f.write(json.dumps(dat, ensure_ascii=False))
            f.write('\n')            
        
    print('数据导出成功！')
    estime = round((time.time() - start),3)
    print('用时:%f 秒' % estime )


if __name__ == '__main__':
    pass
    #export_datas('./signed-data', project_name, outfname='alldata.txt')

    parser = argparse.ArgumentParser(description='fastlabel数据批量导出工具')
    parser.add_argument('--task', type=str, required=True, default="", help='处理命令')
    parser.add_argument('--fname', type=str, default="", help='处理文件或者目录')
    parser.add_argument('--outpath', type=str, default="", help='输出文件或目录')
    parser.add_argument('--project', type=str, default="", help='项目名称')

    args = parser.parse_args()
    task = args.task
    fname = args.fname
    outpath = args.outpath
    project = args.project

    if task=='export':
        export_datas(fname, project, outfname=outpath)



