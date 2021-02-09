import numpy as np
import pandas as pd

'''
input: filename
output: matrix(attributes * vertices)
Read .txt file of attributes and vertices at Ti
this function aims to remove the vertices with no attributes
'''

# load and preprocess vertices and attributes data file
def load_data_VaA(filename):
    # 读入数据，做预处理
    data = np.loadtxt(filename, dtype=np.int)
    data = data.transpose()
    print(data)

    #text1 = pd.read_table(filename, header=None)

    # 创建一个vertices & attributes 表格
    vertices = data[1:, :]
    matrix = vertices
    table = pd.DataFrame(matrix, columns=data[0, :])  # 创建一个dataframe;
    print(table)
    return table


# 删除元素全部为0的列 --> 即没有attribute的顶点
def pre_matrix(table):

    # print(len(table.columns))
    # print(table.columns)
    # print(sum(table[0]))
    # print(len(table.columns))
    # print(sum(table[2722]))

    index = []  # 记录全为0的列索引号
    print(table.columns)

    for i in table.columns:
        if sum(table[i]) == 0:
            index.append(i)
        #else:
            #print('第', i, '列不全为0')
    print('drop end')
    table.drop(index, axis=1, inplace=True)
    #print(index)
    #print(len(index))
    print("There are total " + str(len(index)) + " vertices do not have attributes" )

    return table

