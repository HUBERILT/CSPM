# from src.Inverted_Index import *
import numpy as np
import pickle
import csv


# 加载pkl文件(vertices 与 pattern set 映射文件)
def loadPklData(pklFilename):
    file = open(pklFilename, 'rb')
    VaA_dict = pickle.load(file)
    return VaA_dict


# 写struPattern
def writePklData(struPattern, struPatternFilename):
    struPattern_file = open(struPatternFilename, 'wb')
    pickle.dump(struPattern, struPattern_file)
    struPattern_file.close()


# 加载 txt 顶点文件，并移除isolated  (DBLP 980个顶点)
def loadVerticesData(txtFilename):
    f = open(txtFilename, "r")  # 设置文件对象
    vData = {}
    edges_num = 0
    # j = 0
    for line in f.readlines():
        data = line.strip('\n')
        # print(line)
        data = data.strip().split(' ')
        for i in range(1, len(data)):
            vData.setdefault(int(data[0]), set()).add(data[i])
            edges_num += 1
        if int(data[0]) in vData and len(vData.get(int(data[0]), set())) == 0:
            vData.pop(int(data[0]))
            # print(vData)
            # j += 1
    # print('Vertices adjacent data (after removing isolated nodes): ', vData)
    print('edges number:', str(edges_num))
    print('There are totally ', len(vData), 'vertices left')
    return vData


# find adjacent vertices of each attributes pattern
# def find_adjacentVertex(vertex, vData):
#     return vData.get(vertex)

def cons_adjacentPatterns(pattern_vertices, vData, vertex_patterns):
    stru_patterns = {}
    key_set1 = set(vData.keys())
    key_set2 = set(vertex_patterns.keys())

    key_set = key_set1.intersection(key_set2)
    # print('key_set = ', key_set)

    for (k, v) in pattern_vertices.items():  # 遍历Pattern出现的顶点
        for i in v:  # 遍历中心Pattern对应的每一个顶点
            result = vData.get(int(i), set())  # 找到中心pattern相连的顶点
            # print(' S1: The adjacent Vertices of Pattern ', k, ' in Vertex ', i, 'are :', result)
            adjacent_patterns = set()
            for r in result:  # 每一个相连顶点替换为该顶点的pattern
                if r == '': continue
                if int(r) in key_set:
                    # print('     S2: The Patterns of adjacent Vertex ', r, ' are ', vertex_patterns[int(r)])
                    for elem in set(vertex_patterns[int(r)]):
                        adjacent_patterns.add(elem)
                # print('   S3: The adjacent Patterns of Pattern ', k, 'of Vertex ', i,'are ', adjacent_patterns)
            if len(adjacent_patterns) > 0:
                stru_patterns.setdefault(k, []).append(adjacent_patterns)
    # print('S4: Structured patterns table:', stru_patterns)
    return stru_patterns


# calculate the number of lines of stru_patterns
def count_len_struPatterns(stru_patterns):
    count = 0
    for (k, v) in str_patterns.items():
        count += len(v)
    print('There are total ', count, ' lines in stru_patterns')
    return count


# list struPatterns
def list_struPatterns(stru_patterns):
    print('The structured pattern database could be shown as follows:')
    for (k, v) in str_patterns.items():
        for i in range(len(v)):
            print(k, 'th : ', v[i])


def write_medFile(invertedIndex, med_filename_pv, new_database, med_filename_vp):
    with open(med_filename_pv, 'w') as f:
        for key in invertedIndex.keys():
            f.write(str(key) + ': ' + str(invertedIndex[key]) + '\n')

    with open(med_filename_vp, 'w') as f:
        for key in new_database.keys():
            f.write(str(key) + ': ' + str(new_database[key]) + '\n')


def write_medFile_str(str_patterns, med_filename_str):
    med_file = open(med_filename_str, 'wb')
    pickle.dump(str_patterns, med_file)
    med_file.close()



if __name__ == '__main__':
    txtFilename = 'vertices.txt'
    vData = loadVerticesData(txtFilename)

    pklFilename1 = 'pattern_vertices.pkl'
    pklFilename2 = 'vertex_patterns.pkl'
    pattern_vertices = loadPklData(pklFilename1)  # invertedIndex
    vertex_patterns = loadPklData(pklFilename2)  # new_database

    print('pattern_vertices = ', pattern_vertices)

    '''
    # 将 vertices替换成 attributes patterns
    # 创建 Dict key 为 Pattern index; value 为 List of pattern set
    # total 1411 lines in stru_patterns of DBLP
    '''
    str_patterns = cons_adjacentPatterns(pattern_vertices, vData, vertex_patterns)

    ''' Show the input of Step2 '''
    # count_len_struPatterns(str_patterns)
    # list_struPatterns(str_patterns)
    # print(str_patterns)

    # struPattern_File = 'struPattern.pkl'
    # writePklData(str_patterns, struPattern_File)
