import pickle


# Load pkl file
def loadPklData(pklFilename):
    file = open(pklFilename,'rb')
    codeTable = pickle.load(file)
    return codeTable

'''
# CHECKED
'''
def loadTxtData(txtFilename):
    with open(txtFilename, 'r') as file_to_read:
        featureId_attributes = {}
        lineId = 0
        for line in file_to_read.readlines():
            featureId_attributes.setdefault(lineId, line.replace('\n', '').replace('\r', ''))
            lineId += 1
    print('featureId_attributes = ', featureId_attributes)
    return featureId_attributes

def get_mapping_strAttributes(codeTable, txtFilename):
    #codeTable = loadPklData(pklFilname)
    featureId_attributes = loadTxtData(txtFilename)
    str_attributes = {}

    for i in range(len(codeTable)):
        components = list(codeTable[i][2])
        for j in components:
            str_attributes.setdefault(codeTable[i][0], set()).add(featureId_attributes[j])

    return str_attributes

# if __name__ == '__main__':
#     pklFilename = 'codeTable.pkl'
#     txtFilename = 'attributes_mapping.txt'
#
#     str_attributes = get_mapping_strAttributes(pklFilename, txtFilename)
#     print(str_attributes)






