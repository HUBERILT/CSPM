import os
import csv
import re
import numpy as np
import scipy.sparse
from S1_attributesPattern.Slim import *
from sklearn.utils.estimator_checks import check_estimator
from timeit import default_timer as timer
import pickle

def loadData(csvFilename):
    indptr = [0]
    indices = []
    data = []

    # filePath = os.path.join(os.path.dirname(__file__), csvFilename)
    with open(csvFilename, mode="r") as infile:
        r = csv.reader(infile, delimiter = ' ')
        for row in r:
            for elem in row:
                if (len(elem) > 0):
                    indices.append(int(elem))
                    data.append(1)
            indptr.append(len(indices))

    return scipy.sparse.csr_matrix((data, indices, indptr))

# 加载顶点index数据，用于替换database行号
def loadVerticesIndexData(csvVerticesFilename):
    indices = []
    with open(csvVerticesFilename, mode="r") as infile:
        r = csv.reader(infile, delimiter = ' ')
        #print('r = ', r)
        for row in r:
            for elem in row:
                #print('elem = ', elem)
                indices.append(elem)
    #删除文件最后一个‘ ’空元素
    indices.pop()
    return indices


def codeTableSize(ct):
    size = 0
    for f in ct:
        size += 2
        size += len(f[2])
    return size


def compute_total_size(slim, compressedMatrix):
    codeTable = slim.get_code_table()
    xref = slim.get_feature_cross_reference()
    compressedSize = matrixSize(compressedMatrix)
    codetableSize = codeTableSize(codeTable)
    xrefSize = len(xref) * 3
    totalSize = compressedSize + codetableSize + xrefSize
    return totalSize

# 获取codetable中每个属性出现的顶点号
def codeTable_details(codeTable2, vIndices):
    invertedIndex = {}
    for f in codeTable2:
        for i in f[3]:
            invertedIndex.setdefault(f[0], set()).add(vIndices[i])
    return invertedIndex


# 从invertedIndex中得到用Pattern替换后的数据集
def sorted_new_database(invertedIndex):
    new_database = {}
    sorted_new_database = {}
    # 从inverted index中获得new_database
    for (k, v) in invertedIndex.items():
        for i in v:
            new_database.setdefault(i, set()).add(k)

    sort_key = []
    for key in sorted(new_database.keys()):
        sort_key.append(int(key))

    # 按照Key排序
    count = 0
    for i in sorted(sort_key):
        count += len(new_database[str(int(i))])
        sorted_new_database.setdefault(i, new_database[str(int(i))])
    return sorted_new_database


def calculate_totalItems(dataset):
    i = 0
    for (key,values) in dataset.items():
        for v in values:
            i += 1
    return i


def calculate_frequncy(codeTable):
    f = 0
    for i in range(len(codeTable)):
        f += codeTable[i][1]
    return f


if __name__ == '__main__':
    datasetName = 'T0'
    filename = datasetName + '-test-transform.csv'
    csvVerticesData = datasetName + '-test-vertices-index.csv'

    csr = loadData(filename)
    vIndices = loadVerticesIndexData(csvVerticesData)

    s = Slim()
    compressed = s.fit_transform(csr)
    codeTable = s.get_code_table()
    print('codeTable is :', codeTable)

    # 获得invertedIndex（key: pattern , value: set of vertices）
    # codeTable2 是含有pattern出现顶点信息的codetable
    codeTable2 = s.get_code_table2()
    invertedIndex = codeTable_details(codeTable2, vIndices)
    print('invertedIndex = ', invertedIndex)
    print('len(invertedIndex.key) is', len(invertedIndex.keys()))

    # new_database: key--> vertex; value --> set of patterns
    new_database = sorted_new_database(invertedIndex)
    print('new_database = ', new_database)
    print('len(new_database) is : ', len(new_database))

    # 用pickle保存新vertices -- attributes数据
    # new_database 是 attributes transaction database
    # vDatabase： key --> vertex Id; value --> attributes pattern set
    invertedIndex_file = open(datasetName + 'pattern_vertices.pkl','wb')
    pickle.dump(invertedIndex, invertedIndex_file)
    invertedIndex_file.close()

    new_database_file = open(datasetName + 'vertex_patterns.pkl','wb')
    pickle.dump(new_database, new_database_file)
    new_database_file.close()

    codeTable_file = open(datasetName + 'codeTable.pkl', 'wb')
    pickle.dump(codeTable, codeTable_file)
    codeTable_file.close()

    # 将新attributes pattern数据存储为.txt文件
    # key 是vertex，value 是vertex对应的 attributes patterns
    f = open(datasetName + 'pattern_vertices.txt', 'w')
    for key in invertedIndex.keys():
        f.write(str(key) + ': ' + str(invertedIndex[key]) + '\n')
    f.close()

    f2 = open('vertex_patterns.txt', 'w')
    for key in new_database.keys():
        f2.write(str(key) + ': ' + str(new_database[key]) + '\n')
    f2.close()

    # 结果对比
    print('len(codeTable) is : ', len(codeTable))
    totalSize = compute_total_size(s, compressed)
    originalSize = matrixSize(csr)
    print("original size", originalSize, "total compressed size", totalSize)

