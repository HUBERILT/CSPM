import pickle
import math
import copy
from S1_attributesPattern.run_Slim import *
from S1_attributesPattern.Slim import *
from Transform.transform import *
from S2_structurePattern.str_attributes import *
import constant as cst
import time
import sys

# Load .pkl file(str_patterns\ codeTable)
def loadPklData(pklFilename):
    file = open(pklFilename, 'rb')
    str_patterns = pickle.load(file)
    return str_patterns

# get the leaf-values
def get_strPattern_list(transform_data):
    sp = []
    for key in transform_data.keys():
        sp.append(key)
    return sp

def count_pattern(corePattern, str_patterns):
    ls = str_patterns[corePattern]
    items = set()
    for s in ls:
        for i in s:
            items.add(i)
    return items

def get_corePattern_list(str_patterns):
    cp = []
    for key in str_patterns.keys():
        cp.append(key)
    # print('core patterns list = ', cp)
    return cp

def calculate_coreItems(database, method='str_patterns'):
    if method == 'str_patterns':
        count_core = {}
        for (k, v) in database.items():
            count = 0
            for i in range(len(v)):
                count += len(v[i])
            count_core.setdefault(k, count)
        print('Count_core using str_patterns = ', count_core)
    else:  # using transform_data --> Dict{ key : structured pattern ; value: Dict{ key2 : core pattern; value2 : Set( appear positions ) } }
        #### !!!! THIS PART MAY NOT CORRECTED!!!!!
        count_core = {}

        for c_key in range(len(cp_list)):
            count_c_key = 0
            for (k, v) in database.items():
                if c_key in v.keys():
                    count_c_key += len(v[c_key])
            count_core.setdefault(c_key, count_c_key)
        print('Count_core using transform_data = ', count_core)

    return count_core


'''
# Calculate_totalItems using two methods.
# The results of both two are the same.
# calcutateGain --> c_coreItems 
'''
def calculate_totalItems(dataset, method="transform_data"):
    count = 0
    if method == 'transform_data':
        for (k, v) in dataset.items():
            for (k2, v2) in v.items():
                count += len(v2)
        print('There are total', count, 'items calculated by transform_data')
    else:
        for (k, v) in dataset.items():
            for i in range(len(v)):
                count += len(v[i])
        print('There are total', count, 'items calculated by str_patterns')
    return count


'''
INPUT: transform_data ==> Dict{ key : structured pattern ; value: Dict{ key2 : core pattern; value2 : Set( appear positions ) } }
       c_coreItems ==> Dict{ key: core pattern; value: number of items } 
       s --> total number of items in transform_data #(11765)
OUTPUT: OriginalCost  
'''
def calculate_originalCost(transform_data, c_coreItems, method='derived formulation'):
    total_cost = 0
    if method == 'derived formulation':

        accum_P1 = 0  # part1 of formulation
        accum_P2 = 0  # part2 of formulation
        for (k, v) in c_coreItems.items():
            accum_P1 += v * math.log2(v)
        # method2 to calculate accum_P1
        # accum_P1 = math.log2(multiple_coreItems(c_coreItems))

        for (k, v) in transform_data.items():
            for (k2, v2) in v.items():
                if len(v2) > 0:
                    accum_P2 += len(v2) * math.log2(len(v2))
        total_cost = accum_P1 - accum_P2
        print('Total cost calculated by derived formultion is :', total_cost)

    else:  # CHECKED (total_items == s)
        # lines = 0
        # total_items = 0

        for (k, v) in transform_data.items():
            for (k2, v2) in v.items():
                # lines += 1
                # total_items += len(v2)
                if len(v2) > 0:
                    total_cost += -len(v2) * math.log2(len(v2) / c_coreItems[k2])
        # CHECK: whether
        # print('Total calculate', lines, 'lines || Total items(s) = ', total_items, '|| (CHECK) s = ', s)
        print('Total cost calculated by original formulation is : ', total_cost)

    return total_cost


'''
Input: 1. transform_data ==> Dict{ key : structured pattern ; value: Dict{ key2 : core pattern; value2 : Set( appear positions ) } }  
       2.3. patternX , patternY ==> structured pattern Ids ( to be merged )
       4. c_coreItems = calculate_coreItems(stru_patterns) # items number for each core pattern
                      ==> Dict{ key: core pattern; value: number of items } 
            PS . total number of items in transform_data #(11765)
                 type number of core patterns #(126) 
Inner parameters: 
       1. c_X, c_Y | c_XY --> line items number | intersection position(item) number
       2. tc_XY --> total decrease number of items
'''
def calculate_Gain(transform_data, s_patternX, s_patternY, c_coreItems):
    # m = len(transform_data.keys()) #准确来讲应该是core pattern的数量，这里求的组合pattern的数量，因为在DBLP数据集中二者相等（其他数据集通常也相等）
    gain = 0
    tc_XY = 0  # total decrease number after substitute original items in all core patterns into new structured patterns
    tc_XY_p = 0

    # posX, posY--> Dict{ key: core pattern, value: Set( positions ) }
    posX = transform_data[s_patternX]
    posY = transform_data[s_patternY]
    # keyX, keyY, keyXY --> core patterns
    keyX = posX.keys()
    keyY = posY.keys()
    # print('keyX = ', keyX, ' || keyY = ', keyY )

    keyXY = set(keyX).intersection(set(keyY))
    # print('intersection KEY XY:', set(keyXY))
    # print('len(keyXY) = ', len(set(keyXY)))

    if len(keyXY) > 0:
        # iter = 0
        for key in keyXY:
            # iter += 1
            # print('key = ', key)
            # key = 81

            c_X = len(posX[key])  # line item count
            c_Y = len(posY[key])
            c_XY = len(posX[key].intersection(posY[key]))

            tc_XY += c_XY

            # 判断相同key出现位置是否有交集
            if c_XY == 0:
                # print('There is no match!')
                continue
            # print('c_X = ', c_X, ' || c_Y = ', c_Y, ' || c_XY = ', c_XY)

            # Calculate the first part of gain formulation
            gaink_P1 = c_coreItems[key] * math.log2((c_coreItems[key])) - (c_coreItems[key] - c_XY) * math.log2(
                (c_coreItems[key] - c_XY))
            # print('key = ', key, ' || c_coreItems[key] = ', c_coreItems[key])

            # Calculate the second part of gain formulation
            if c_XY == c_X and c_XY == c_Y:
                # print('case 1')
                gaink_P2 = c_XY * math.log2(c_XY)
                tc_XY_p += c_XY

            elif c_XY == c_X and c_XY != c_Y:
                # gaink_P2 = c_X * math.log2(c_X) + c_Y * math.log2(c_Y) - (c_Y - c_XY) * math.log2(c_Y - c_XY) - c_XY * math.log2(c_XY)
                gaink_P2 = c_Y * math.log2(c_Y / (c_Y - c_XY)) + c_XY * math.log2(c_Y - c_XY)
                tc_XY_p += c_XY
                # print('case 2 ')

            elif c_XY != c_X and c_XY == c_Y:
                gaink_P2 = c_X * math.log2(c_X / (c_X - c_XY)) + c_XY * math.log2(c_X - c_XY)
                tc_XY_p += c_XY
                # print('case 3')

            else:
                gaink_P2 = c_X * math.log2(c_X / (c_X - c_XY)) + c_Y * math.log2(c_Y / (c_Y - c_XY)) + c_XY * math.log2(
                    (c_X - c_XY) * (c_Y - c_XY) / c_XY)
                # print('case 4')

            # Calculate the cost of the lines added to code table
            gaink_P3 = - math.log2(tc_XY / (c_coreItems[key]))

            # print('gaink_P1 = ', gaink_P1, 'gaink_P2 = ', gaink_P2)
            gaink = (gaink_P1 - gaink_P2) - gaink_P3
            # print('gaink = ', gaink)
            gain += gaink
            # if iter == 1:
            #     break
    gaink_P4 = st_cost[s_patternX] + st_cost[s_patternY]
    gain -= gaink_P4
    # print('tc_XY_p = ', tc_XY_p)
    return gain


'''
INPUT : 1. transform_data: inverted table before merging ==> Dict{ key : structured pattern ; value: Dict{ key2 : core pattern; value2 : Set( appear positions ) } } 
        2.3. spatternX, spatternY: structured patterns need to be merged ==> int
OUTPUT: new_transform_data: the new inverted database after generate new structured pattern {s_patternX, s_patternY}
        new_c_coreItems
'''
def apply(transform_data, s_patternX, s_patternY, c_coreItems):
    new_featureId = str(s_patternX) + '+' + str(s_patternY)

    # Update st_cost（更新str_pattern 与 cost 映射） & str_attributes(更新 sp 与真实属性的映射)
    st_cost.setdefault(new_featureId, st_cost[s_patternX] + st_cost[s_patternY])
    # str_attributes.setdefault(new_featureId, str_attributes[s_patternX] | str_attributes[s_patternY])

    # Core patterns Dict of structured pattern X and Y ==> Dict{ key2 : core pattern; value2 : Set( appear positions ) }
    posX = transform_data[s_patternX]
    posY = transform_data[s_patternY]

    # keyX, keyY, keyXY --> core patterns
    keyX = posX.keys()
    keyY = posY.keys()

    # keys of core patterns that could be merged
    keyXY = set(keyX).intersection(set(keyY))

    new_sPattern = {}  # line need to be added
    # iter = 0
    for key in keyXY:
        # iter += 1
        # key = 81

        set_X = posX[key]
        set_Y = posY[key]
        set_XY = posX[key].intersection(posY[key])

        c_XY = len(set_XY)

        if len(set_XY) == 0:
            continue

        new_setX = set_X - set_XY
        new_setY = set_Y - set_XY
        # print('Core pattern = ', key, '  In this case:')
        # print('     setXY = ', set_XY)
        # print('   setX = ', set_X, ' setY = ', set_Y)
        # print('   new_setX = ', new_setX, ' new_setY = ', new_setY)

        # 替换原 core pattern里的 value
        # 不移除空集
        transform_data[s_patternX][key] = new_setX
        transform_data[s_patternY][key] = new_setY

        # Remove the key with set() value
        if len(new_setX) == 0:
            del transform_data[s_patternX][key]
        if len(new_setY) == 0:
            del transform_data[s_patternY][key]

        # 添加新pattern / Add the new structured pattern { s_patternX, s_patternY }
        # Dict{ key: new structured pattern; value: Dict{ key: core pattern; value: co-occurrence positions }}
        transform_data.setdefault(new_featureId, {}).setdefault(key, set_XY)

        # Update c_coreItems
        c_coreItems[key] -= c_XY

    # If the dict of s_patternX or s_patternY is Null after apply, then remove the structure pattern(s)
    if len(transform_data[s_patternX]) == 0:
        del transform_data[s_patternX]
    if len(transform_data[s_patternY]) == 0:
        del transform_data[s_patternY]

    # print(new_transform_data['test'])
    # print(' len(new) = ', len(new_transform_data['test'].keys()))
    return transform_data, c_coreItems


'''
INPUT: features_dict ==>{ key: featureId, value: calss Fature(featureId, components, mergeSet{featureIds} ) }
       s_pattern_Id ==> int (the featureId need to be deleted in features_dict, NOTES: both featureId and item in mergeSet)
OUTPUT: features_dict(after deleting s_pattern_Id in all mergeSets)
'''
def delete_mergeSet_items(features_dict, s_pattern_Id):
    test = features_dict[s_pattern_Id].mergeSet
    for item in features_dict[s_pattern_Id].mergeSet:
        test2 = features_dict[item].mergeSet
        if not (s_pattern_Id in features_dict[item].mergeSet):
            print("WARNNING: the pairs based on mergeSet are not symmetric! item is :", item)
            continue
        else:
            features_dict[item].mergeSet.remove(s_pattern_Id)
    return features_dict


'''
INPUT : 1. transform_data: inverted table before merging ==> Dict{ key : structured pattern ; value: Dict{ key2 : core pattern; value2 : Set( appear positions ) } } 
        2.3. spatternX_Id, spatternY_Id: structured patterns need to be merged 
OUTPUT: transform_data: the new inverted database after generate new structured pattern {s_patternX, s_patternY}
        c_coreItems
        features_dict: added new_feature( if original feature merged perfectly, remove) 
'''
def apply2(transform_data, s_patternX_Id, s_patternY_Id, c_coreItems, features_dict):
    new_featureId = str(s_patternX_Id) + '+' + str(s_patternY_Id)

    # Update st_cost & str_attributes
    st_cost.setdefault(new_featureId, st_cost[s_patternX_Id] + st_cost[s_patternY_Id])
    # str_attributes.setdefault(new_featureId, str_attributes[s_patternX_Id] | str_attributes[s_patternY_Id])

    # Core patterns Dict of structured pattern X and Y ==> Dict{ key2 : core pattern; value2 : Set( appear positions ) }
    posX = transform_data[s_patternX_Id]
    posY = transform_data[s_patternY_Id]

    # keyX, keyY, keyXY --> core patterns
    keyX = posX.keys()
    keyY = posY.keys()

    # keys of core patterns that could be merged
    keyXY = set(keyX).intersection(set(keyY))

    new_sPattern = {}  # line need to be added
    # iter = 0
    for key in keyXY:
        # iter += 1
        # key = 81

        set_X = posX[key]
        set_Y = posY[key]
        set_XY = posX[key].intersection(posY[key])

        c_XY = len(set_XY)

        if len(set_XY) == 0:
            continue

        new_setX = set_X - set_XY
        new_setY = set_Y - set_XY

        # Substitute the value in original core pattern
        # Don't remove the empty set
        transform_data[s_patternX_Id][key] = new_setX
        transform_data[s_patternY_Id][key] = new_setY

        # Remove the key with set() value
        if len(new_setX) == 0:
            del transform_data[s_patternX_Id][key]
        if len(new_setY) == 0:
            del transform_data[s_patternY_Id][key]

        # Add the new structured pattern { s_patternX, s_patternY }
        # Dict{ key: new structured pattern; value: Dict{ key: core pattern; value: co-occurrence positions }}
        transform_data.setdefault(new_featureId, {}).setdefault(key, set_XY)

        # Update c_coreItems
        c_coreItems[key] -= c_XY

    # *******************  ADD features_dict[new_featureId]，new_feature.mergeList ************************************************
    # fx,fy --> SpFeature with s_patternX_Id & s_patternY_Id
    fx = features_dict[s_patternX_Id]
    fy = features_dict[s_patternY_Id]
    new_components = set()

    new_components = new_components | fx.components | fy.components
    new_mergeSet = fx.mergeSet & fy.mergeSet

    f = SpFeature(new_featureId, new_components, new_mergeSet)
    features_dict.setdefault(new_featureId, f)

    # *******************  DEL transform_data && features_dict *****************************************
    # If the dict of s_patternX or s_patternY is Null after apply, then remove the structure pattern(s)

    if len(transform_data[s_patternX_Id]) == 0:
        del transform_data[s_patternX_Id]

        features_dict = delete_mergeSet_items(features_dict, s_patternX_Id)  # delete mergeSet -> s_patternX_Id
        # features_dict[new_featureId].mergeSet.remove(s_patternX_Id)
        del features_dict[s_patternX_Id]  # delete featureId --> s_patternY_Id

    if len(transform_data[s_patternY_Id]) == 0:
        del transform_data[s_patternY_Id]

        features_dict = delete_mergeSet_items(features_dict, s_patternY_Id)  # delete mergeSet -> s_patternY_Id
        # features_dict[new_featureId].mergeSet.remove(s_patternY_Id)
        del features_dict[s_patternY_Id]

    # print(new_transform_data['test'])
    # print(' len(new) = ', len(new_transform_data['test'].keys()))
    return c_coreItems, new_featureId


def combine_candidateId(s_patternId_l, s_patternId_r):
    if str(s_patternId_l) > str(s_patternId_r):
        tem = s_patternId_r
        s_patternId_r = s_patternId_l
        s_patternId_l = tem
    return '(' + str(s_patternId_l) + ',' + str(s_patternId_r) + ')'


# Find the candidate with candidateId = id
def get_target_candidate(candidates_list, id):
    for cd in candidates_list:
        if cd.candidateId == id:
            return cd
    return None
    # update gain of (s_patternX_Id, ix) in candidates


# Delete all candidates contian the Feature with featureId = id
def delete_specific_candidates(candidates_list, id):
    for cd in candidates_list[:]:
        if cd.s_patternX.featureId == id or cd.s_patternY.featureId == id:
            candidates_list.remove(cd)
    return None

def update_target_candidate(candidates_list, id, gain):
    for cd in candidates_list:
        if cd.candidateId == id:
            cd.gain = gain
            delete_specific_candidates(candidates_list, id)
            candidates_list.append(cd)
    return candidates_list


'''
INPUT: transform_data, c_coreItems -> used to calculate_Gain
       new_featureId, s_patternX_Id, s_patternY_Id --> Ids help us to update gains in candidates list & mergeSets
       feature_dict, candidates_lis --> mergeSets , gains need to be removed or updated
OUTPUT: feature_dict(with symmetric mergeSet) && candidates_list (all pairs with gain > 0)
'''
def update(transform_data, c_coreItems, features_dict, candidates_list, new_featureId, s_patternX_Id, s_patternY_Id):
    # *************** (1) 针对 new_feature **********************************
    # Symmetric + update gain(add / not add into candidates_list)
    merge_pair = 0
    useful = 0
    for i in list(features_dict[new_featureId].mergeSet)[:]:
        if i == s_patternX_Id:  # 防止重复操作
            continue
        if i == s_patternY_Id:
            continue

        g_new_old = calculate_Gain(transform_data, new_featureId, features_dict[i].featureId, c_coreItems)
        merge_pair += 1
        if g_new_old > cst.GAIN:
            # symmetric: add new_featureId to i's mergeSet
            features_dict[i].mergeSet.add(new_featureId)

            # add new pair into candidates_list
            cd = SpCandidate(features_dict[i], features_dict[new_featureId], g_new_old)
            candidates_list.append(cd)
            useful += 1
        else:
            # remove(delete) i in new_feature.mergeSet
            nmg = features_dict[new_featureId].mergeSet
            nmg.remove(i)

    # *************** (2) 针对 s_patternX(Y) **********************************
    # Remove existing candidates, Updating(modifying) existing candidate gains
    ## 如果s_patternX(Y)_Id  在apply 之后已经被移除，则删除所有candidates_list 中所有相关pair
    ## 如果 s_patternX(Y).mergeSet 为空，证明其没有实际作用，删除包括s_patternX(Y)的candidate pairs in candidates_list, 并在features_dict中删除
    if s_patternX_Id in features_dict.keys():
        x_mgl = features_dict[s_patternX_Id].mergeSet
        # Update gains according to s_patternX.mergeSet & s_patternY.mergeSet
        if len(x_mgl) > 0:
            for ix in list(x_mgl)[:]:  # s_patternX.mergeSet
                if ix == new_featureId:
                    continue
                g_x_old = calculate_Gain(transform_data, s_patternX_Id, ix, c_coreItems)
                merge_pair += 1

                ixId = combine_candidateId(s_patternX_Id, ix)
                cd = get_target_candidate(candidates_list, ixId)
                if cd is None: continue
                candidates_list.remove(cd)

                if g_x_old > cst.GAIN:
                    cd.gain = g_x_old  # update gain of (s_patternX_Id, ix) in candidates
                    candidates_list.append(cd)
                    useful += 1
                else:
                    # candidates_list.remove(cd)  # 只删除该candidate
                    # 互相删除元素
                    x_mgl.remove(ix)
                    i_mgl = features_dict[ix].mergeSet
                    i_mgl.remove(s_patternX_Id)

        # feature 还在, mergeSet 为空
        else:  # 这种情况只存在于 x.mergeSet == [y] and y.mergeSet == [x] and one is perfectly merged one is not perfectly merged
            del features_dict[s_patternX_Id]
            delete_specific_candidates(candidates_list, s_patternX_Id)
    else:  # feature 已经不在了
        delete_specific_candidates(candidates_list, s_patternX_Id)

    if s_patternY_Id in features_dict.keys():
        y_mgl = features_dict[s_patternY_Id].mergeSet
        # Update gains according to s_patternX.mergeSet & s_patternY.mergeSet
        if len(y_mgl) > 0:
            for iy in list(y_mgl)[:]:  # s_patternX.mergeSet
                if iy == new_featureId:
                    continue
                g_y_old = calculate_Gain(transform_data, s_patternY_Id, iy, c_coreItems)
                merge_pair += 1

                iyId = combine_candidateId(s_patternY_Id, iy)
                cd = get_target_candidate(candidates_list, iyId)
                if cd is None: continue
                candidates_list.remove(cd)

                if g_y_old > cst.GAIN:
                    cd.gain = g_y_old  # update gain of (s_patternY_Id, iy) in candidates
                    candidates_list.append(cd)
                    useful += 1
                else:
                    # 互相删除元素
                    y_mgl.remove(iy)
                    i_mgl = features_dict[iy].mergeSet
                    i_mgl.remove(s_patternY_Id)

        # feature 还在, mergeSet 为空
        else:  # 这种情况只存在于 x.mergeSet == [y] and y.mergeSet == [x] and one is perfectly merged one is not perfectly merged
            del features_dict[s_patternY_Id]
            delete_specific_candidates(candidates_list, s_patternY_Id)
    else:  # feature 已经不在了
        delete_specific_candidates(candidates_list, s_patternY_Id)
    return c_coreItems, merge_pair, useful


class SpFeature:
    def __init__(self, featureId, components, mergeSet):
        self.featureId = featureId
        self.components = components
        self.mergeSet = mergeSet

    def __hash__(self):
        return hash(self.featureId)

    def __eq__(self, that):
        return self.featureId == that.featureId

    def __copy__(self):
        return Feature(self.featureId, self.components, self.mergeSet)

    def __str__(self):
        return "[featureId: " + str(self.featureId) + "/components: " + str(self.components) + "/mergeSet: " + str(
            self.mergeSet) + "]"


class SpCandidate:
    def __init__(self, s_patternX, s_patternY, gain):
        if str(s_patternY.featureId) < str(s_patternX.featureId):
            self.s_patternX = s_patternY
            self.s_patternY = s_patternX
        else:
            self.s_patternX = s_patternX
            self.s_patternY = s_patternY
        self.gain = gain
        self.candidateId = '(' + str(self.s_patternX.featureId) + ',' + str(self.s_patternY.featureId) + ')'

    def __lt__(self, that):
        val = self.gain - that.gain
        # val = val if val != 0 else self.s_patternX.featureId - that.s_patternY.featureId
        return val < 0

    def __hash__(self):
        return hash(self.s_patternX.featureId) + hash(self.s_patternY.featureId)

    def __eq__(self, that):
        return True \
            if (
                       self.s_patternX.featureId == that.s_patternX.featureId and self.s_patternY.featureId == that.s_patternY.featureId) \
               or (
                       self.s_patternX.featureId == that.s_patternY.featureId and self.s_patternY.featureId == that.s_patternX.featureId) \
               or ( self.candidateId == that.candidateId) \
            else False

    def __str__(self):
        return '(' + str(self.s_patternX.featureId) + ", " + str(self.s_patternY.featureId) + "): " + str(self.gain)

# CSPM-Baseline
def eclat_baseline(transform_data, sp_list, c_coreItems, iter_whole = 0, iter_ccandidates=None):
    gain_list = {} # Dict{key: gain, value:list( set(pairs) )}
    if iter_ccandidates is None:
        iter_ccandidates ={}

    for i in range(len(sp_list)):
        for j in range((i+1), len(sp_list), 1):
            gain = calculate_Gain(transform_data, sp_list[i], sp_list[j], c_coreItems)
            if gain > 0:
                pair = {sp_list[i], sp_list[j]}
                gain_list.setdefault(gain, []).append(pair)
    iter_ccandidates[iter_whole] = len(gain_list)

    if len(gain_list) == 0:
        return transform_data, sp_list, c_coreItems, iter_ccandidates

    if max(gain_list.keys()) <= 0:
        return transform_data, sp_list, c_coreItems, iter_ccandidates

    # applied items
    used_items = set()

    sorted_gain = sorted(gain_list)


    if len(sorted_gain) ==0:
        return transform_data, sp_list, c_coreItems, iter_ccandidates


    lp = list(gain_list[sorted_gain.pop()][0])

    transform_data, c_coreItems = apply(transform_data, lp[0], lp[1], c_coreItems)
    iter_whole += 1
    sp_list = get_strPattern_list(transform_data)
    transform_data, sp_list, c_coreItems, iter_ccandidates = eclat_baseline(transform_data, sp_list, c_coreItems, iter_whole, iter_ccandidates)

    return transform_data, sp_list, c_coreItems, iter_ccandidates


# CSPM-Partial
def eclat_optimized(transform_data, sp_list, c_coreItems):
    features_dict = {}
    # ****** Initialize: SpFeature, generate features_dict ******
    # features_dict: Dict{key: featureId; value: class Feature(featureId, components, mergeSet{featureId})}
    for i in range(len(sp_list)):
        components = set()
        components.add(sp_list[i])
        f = SpFeature(sp_list[i], components, set())
        features_dict.setdefault(sp_list[i], f)

    # ******************** Initialize: SpCandidate, generate candidate_list *****************************************
    candidates_list = []
    xLs = list(features_dict.keys())

    for i in range(len(xLs)):
        for j in range((i + 1), len(xLs), 1):
            gain = calculate_Gain(transform_data, xLs[i], xLs[j], c_coreItems)
            if gain > cst.GAIN:
                c = SpCandidate(features_dict[xLs[i]], features_dict[xLs[j]], gain)
                candidates_list.append(c)
                # print(c)

    candidates_list = sorted(candidates_list)
    # #PRINT:candidates_list; len(candidates_list)
    # for i in range(len(candidates_list)):
    #     print(candidates_list[i])
    print('Initialized candidates_list length: ', len(candidates_list))

    # Update SpFeature list的 mergeSet --> 只选 gain > 0

    for i in range(len(candidates_list)):
        # fx, fy --> featureId of s_patternX, s_patternY
        fx = candidates_list[i].s_patternX.featureId
        fy = candidates_list[i].s_patternY.featureId

        # ffx, ffy --> Feature with id fx, fy
        ffx = features_dict[fx]
        ffy = features_dict[fy]

        ffx.mergeSet.add(fy)
        ffy.mergeSet.add(fx)

        features_dict[fx] = ffx
        features_dict[fy] = ffy

    # **************************** Apply && Update ********************************************************************
    ite = 0
    ite_candidates = {}
    ite_merge_pair = {}
    ite_useful = {}

    while len(candidates_list) > cst.CANDIDATES_LEN:

        ite_candidates[ite] = len(candidates_list)

        pair = candidates_list.pop()
        # features_keysSet = set()

        # Delete pair with odd featureId
        if not (pair.s_patternX.featureId in features_dict.keys()):
            continue
        if not (pair.s_patternY.featureId in features_dict.keys()):
            continue

        c_coreItems, new_featureId = apply2(transform_data, pair.s_patternX.featureId, pair.s_patternY.featureId,
                                            c_coreItems, features_dict)
        c_coreItems, merge_pair, useful = update(transform_data, c_coreItems, features_dict, candidates_list, new_featureId,
                             pair.s_patternX.featureId,
                             pair.s_patternY.featureId)
        candidates_list = sorted(candidates_list)
        ite_merge_pair[ite] = merge_pair
        ite_useful[ite] = useful
        ite += 1
    print('Total ite = ', ite)

    return transform_data, sp_list, c_coreItems, ite_candidates, ite_merge_pair, ite_useful



'''
Build inverted database
# INPUT: str_patterns ==> Dict{ key : core pattern; value: List[ Set( structured patterns ) ] }
# OUTPUT : transform_data / data ==> Dict{ key : structured pattern ; value: Dict{ key2 : core pattern; value2 : Set( appear positions ) } }
'''
def inverted_database(str_patterns, min_support=1):
    data = {}
    '''
    MAY NEED To BE CHANGED!
    '''
    # !!初始化可以，有了新sp之后 不可以： key --> core patterns 与 structured patterns 所含元素相同
    # 这里的key 遍历 core patterns 中的所有 pattern，但含义是 遍历 structured patterns
    for key in str_patterns.keys():
        for (k, v) in str_patterns.items():
            trans_num = 0
            trans_pos = set()
            # core pattern 中 structured patterns(items) transactions
            for trans in v:
                trans_num += 1
                if key in trans:
                    trans_pos.add(trans_num)
            if len(trans_pos) > 0:
                data.setdefault(key, {}).setdefault(k, trans_pos)
    # print(data)
    sp_patterns = get_strPattern_list(data)
    # sp_patterns = eclat([], sorted(data.items(), key=lambda item: len(item[1]), reverse=True), min_support, sp_patterns)
    return data


'''
INPUT: transform_data ==> Dict{ key : structured pattern ; value: Dict{ key2 : core pattern; value2 : Set( appear positions ) } }
GOAL: Trace back to str_patterns database : used as gain check & result interpretation  
OUTPUT str_patterns database ==> Dict{ key : core pattern; value: List[ Set( structured patterns ) ] } 
'''
def traceback_strPatterns(transform_data):
    str_patterns_buff = {}
    str_patterns = {}

    count_trans = 0
    for core_key in transform_data.keys():  # for key in sp，含义是cp， 因为 new sp 不包含在 transform_data 的core pattern列当中，所以对结果没有影响
        pos_sp = {}  # Dict in core_key { key: position; value: structured patterns }
        for (k, v) in transform_data.items():
            if core_key in v.keys():  # 如果 查询的 core pattern 为第二列的键
                # print('k = ', k, ' || core_k = ', core_key ,' || v[core_k] = ', v[core_key])
                for i in v[core_key]:  # 遍历 sp 出现的每一行
                    pos_sp.setdefault(i, set()).add(k)
        for key in pos_sp.keys():
            str_patterns.setdefault(core_key, []).append(pos_sp[key])
    return str_patterns


'''
INPUT: codeTable getting from Step1
OUTPUT:st_cost: Dict{ key: st_pattern; value: code length of step1 }
'''
def standard_cost(codeTable):
    st_cost = {}
    totalElement = 0
    for i in range(len(codeTable)):
        totalElement += codeTable[i][1]

    for i in range(len(codeTable)):
        if codeTable[i][1] == 0:
            st_cost[codeTable[i][0]] = 0
            continue
        st_cost.setdefault(codeTable[i][0], -math.log2(codeTable[i][1] / totalElement))

    return st_cost

# Get the total frequency for each core-value in inverted_database
def get_c_coreItems(transform_data, c_set):
    c_coreItems = {}
    for k in c_set:
        sum_c = 0
        for l_value in transform_data:
            if k in transform_data[l_value].keys():
                sum_c += len(transform_data[l_value][k])
        if sum_c > 0:
            c_coreItems.setdefault(k, sum_c)
    return c_coreItems

# Calculate the cost of each pattern
def print_result(new_transform_data, st_cost):
    sorted_result_con = {}
    sorted_total_cost = {}
    new_c_coreItems = get_c_coreItems(new_transform_data, st_cost.keys())
    for k in new_transform_data.keys():
        for k2 in new_transform_data[k].keys():
            cond_entro = -math.log2(len(new_transform_data[k][k2]) / new_c_coreItems[k2])
            total_cost = st_cost[k2] + cond_entro
            sorted_result_con.setdefault('(' + str(k) + ',' + str(k2) + ')', cond_entro)
            sorted_total_cost.setdefault('(' + str(k) + ',' + str(k2) + ')', total_cost)
    return sorted_result_con, sorted_total_cost


if __name__ == '__main__':

    # dblp
    datasetName = sys.argv[1]
    sl = sys.argv[2]
    methodName = sys.argv[3]

    input_dir = './Dataset/' + datasetName + '/Input/'
    filename = input_dir + 'test-transform.csv'
    csvVerticesData = input_dir + 'test-vertices-index.csv'

    # Preprocessing
    intermediate_dir = './Dataset/' + datasetName + '/IntermediateResult/'
    med_filename_pv = intermediate_dir + 'pattern_vertices.txt'
    med_filename_vp = intermediate_dir + 'vertex_patterns.txt'

    # without Step1
    med_filename_pv2 = intermediate_dir + '2-pattern_vertices.txt'
    med_filename_vp2 = intermediate_dir + '2-vertex_patterns.txt'

    csr = loadData(filename)
    vIndices = loadVerticesIndexData(csvVerticesData)


    '''
    # Step1 : Slim
    '''
    if sl == 1:
        s = Slim()
        compressed = s.fit_transform(csr)
        codeTable = s.get_code_table()
        print('codeTable is :', codeTable)
        print('There are total', len(codeTable), 'attributes')

        # Transform
        # 获得invertedIndex（key: pattern , value: set of vertices）
        # codeTable2 是含有pattern出现顶点信息的codetable
        codeTable2 = s.get_code_table2()
        invertedIndex = codeTable_details(codeTable2, vIndices)

        # new_database: key--> vertex; value --> set of patterns
        new_database = sorted_new_database(invertedIndex)
    else:
        '''
        PREPROCES: without Step1
        '''
        s2 = Slim()
        cdo = s2.original_codeTable(csr)
        codeTable = s2.get_code_table2()
        invertedIndex = codeTable_details(codeTable, vIndices)
        new_database = sorted_new_database(invertedIndex)

    '''
    # WRITE: write codeTable and new_database to IntermediateResult folder
    '''
    # 将新attributes pattern数据存储为.txt文件
    # key 是vertex，value 是vertex对应的 attributes patterns
    write_medFile(invertedIndex, med_filename_pv2, new_database, med_filename_vp2)

    '''
    # Transform
    '''
    verticesFilename = input_dir + 'vertices.txt'
    vData = loadVerticesData(verticesFilename)
    str_patterns = cons_adjacentPatterns(invertedIndex, vData, new_database)

    '''

   #  # Step2 : Conditional entropy
   #  '''
   #  apFilename = input_dir + 'attributes_mapping.txt'
   #  str_attributes = get_mapping_strAttributes(codeTable, apFilename)

    # calculate_totalItems(transform_data)

    Orig_transform_data = inverted_database(str_patterns)
    Orig_c_coreItems = calculate_coreItems(str_patterns)

    transform_data = inverted_database(str_patterns)

    c_coreItems = calculate_coreItems(str_patterns)
    st_cost = standard_cost(codeTable)
    cp_list = get_corePattern_list(str_patterns)
    sp_list = get_strPattern_list(transform_data)

    # Timer
    time_start = time.time()

    if methodName == 'CSPM-Basic':
        r1, r2, r3, r4 = eclat_baseline(transform_data, sp_list, c_coreItems)
    elif methodName == 'CSPM-Partial':
        r1, r2, r3, r4, r5, r6 = eclat_optimized(transform_data, sp_list, c_coreItems)

    # Timer
    time_end = time.time()


    '''
    # PRINT: final database represented by real attributes
    '''
    # print('str_attributes = ', str_attributes)
    # print('RESULT-1: show attributesd')
    # count_r2 = 0
    # for (k, v) in r1.items():
    #     for (k2, v2) in sorted(v.items(), key=lambda x: len(x[1]), reverse=True):
    #         if len(v2) > 60:
    #             # print('sp:', str_attributes[k], '--> cp:', str_attributes[k2], '--> pos:', v2, '==> freq:', len(v2))
    #             print('sp:', str_attributes[k], '--> cp:', str_attributes[k2], '==> freq:', len(v2))
    #         # print('sp:', str_attributes[k], '--> cp:', str_attributes[k2], '--> pos:', v2, '==> freq:', len(v2))
    #         count_r2 += 1

    # Do not show the attributes result
    # print('RESULT-2: do not show attributesd')
    # count_r2 = 0
    # for (k, v) in r1.items():
    #     for (k2, v2) in sorted(v.items(), key=lambda x: len(x[1]), reverse=True):
    #         if len(v2) > 0:
    #             # print('sp:', str_attributes[k], '--> cp:', str_attributes[k2], '--> pos:', v2, '==> freq:', len(v2))
    #             print('sp:', k, '--> cp:', k2, '==> freq:', len(v2))
    #         # print('sp:', str_attributes[k], '--> cp:', str_attributes[k2], '--> pos:', v2, '==> freq:', len(v2))
    #         count_r2 += 1

    # print('Sp pattern number = ', len(r2), '  / Total result lines number  = ', count_r2)
    n = 50

    st_cost_original = standard_cost(codeTable)
    final_result_con, final_result_cost = print_result(r1, st_cost_original)

    s1 = sorted(final_result_con.items(), key=lambda x: x[1], reverse=False)
    s2 = sorted(final_result_cost.items(), key = lambda x:x[1], reverse = False)

    s1 = s1[:n]
    s2 = s2[:n]

    print('Sorted by conditional entropy:')
    for result in s1:
        print(result)

    print('Sorted by total cost:')
    for result in s2:
        print(result)

    # '''
    # # 分析（Analysis）:
    # # (1) Compression ratio of step 2
    # # (2) Overall compression ratio (+ cost of code table)
    # '''
    before = calculate_originalCost(Orig_transform_data, Orig_c_coreItems)
    after = calculate_originalCost(r1, r3)
    compression_ratio = after / before
    print('The compression ratio of Step2 is: ', compression_ratio)

    # overall_before = before + sum(standard_cost(codeTable).values())
    # overall_after = after + sum(st_cost.values())
    #
    # overall_compression_ratio = overall_after / overall_before
    # print('The overall compression ratio of Step2 is: ', overall_compression_ratio)

    print('Time cost:', time_end - time_start, 's')


