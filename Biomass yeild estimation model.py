import json
from DATA import Data
import pandas as pd
from model_util import creat_time, Sweet_sorghum, Switchgrass, Miscanthus, land_def, select_biomass
from tqdm import tqdm
import numpy as np
import gc
import time
from sklearn.cluster import MiniBatchKMeans
from sklearn import preprocessing

path = ''
name_target = 'new'
data_land_dataframe_json = pd.DataFrame(json.load(open(path + 'data/data_land_selectbiomass_all_new.json', 'rb')))

land_tag = []
Miscanthus_count = 0
Switchgrass_count = 0
Sweet_sorghum_count = 0
for land_item in tqdm(data_land_dataframe_json):
    land_tag_item = {'Miscanthus': False, 'Sweet_sorghum': False, 'Switchgrass': False}
    try:
        if Miscanthus(land_item):
            land_tag_item['Miscanthus'] = True
            if land_item['LUC'] in [22, 23, 31, 32, 33, 46, 45, 61, 63, 65]:  # [33, 46, 45, 61, 63, 65]
                Miscanthus_count += 1
    except:
        pass
    try:
        if Switchgrass(land_item):
            land_tag_item['Switchgrass'] = True
            if land_item['LUC'] in [22, 23, 31, 32, 33, 46, 45, 61, 63, 65]:
                Switchgrass_count += 1
    except:
        pass
    try:
        if Sweet_sorghum(land_item):
            land_tag_item['Sweet_sorghum'] = True
            if land_item['LUC'] in [22, 23, 31, 32, 33, 46, 45, 61, 63, 65]:
                Sweet_sorghum_count += 1
    except:
        pass
    land_tag_item['pointid'] = land_item['pointid']
    land_tag.append(land_tag_item)

land_attribute_rice, land_attribute_Wheat_Corn, land_attribute_Forestry_residue, land_attribute_three_biomass, land_attribute_fail, land_analysis_all = land_def(
    data_land=data_land_dataframe_json,  path=path)
del data_land_dataframe_json
gc.collect()

land_attribute = land_attribute_rice + land_attribute_Wheat_Corn + land_attribute_Forestry_residue + land_attribute_three_biomass
del land_attribute_rice, land_attribute_Wheat_Corn, land_attribute_Forestry_residue, land_attribute_three_biomass, land_attribute_fail
gc.collect()


land_attribute = json.loads(
    pd.merge(pd.DataFrame(land_attribute), pd.DataFrame(land_tag), on='pointid').dropna(axis=0, ).reset_index(
        drop=True).to_json(
        orient="records"))

data_land = pd.DataFrame(land_attribute)[
    ['pointid', 'LUC', 'POINT_X', 'POINT_Y', 'NPP', 'biomass_dry', 'biomass_wet', 'biomass_energy', 'biomass_emissions',
     'biomass_cost', 'water', 'Miscanthus', 'Sweet_sorghum', 'Switchgrass']]
del land_attribute
gc.collect()
data_1 = data_land[['POINT_Y', 'POINT_X']]
min_max_scaler = preprocessing.MinMaxScaler()
train_x = min_max_scaler.fit_transform(data_1)
start = time.time()
cluster_num_1 = 10
k_model = MiniBatchKMeans(n_clusters=cluster_num_1)
result = k_model.fit(train_x)
predict_y = k_model.predict(train_x)
dis = result.inertia_
data_new = pd.concat((data_land, pd.DataFrame(predict_y)), axis=1)
del data_land
gc.collect()
data_new.rename({0: u'cluster_1'}, axis=1, inplace=True)

data_new_test = None
cluster_num_2_list = []
label_total = 0
for i in range(cluster_num_1):

    data_2 = data_new[data_new['cluster_1'] == i].reset_index(drop=True)
    data_selec = data_2[['POINT_Y', 'POINT_X']]
    min_max_scaler = preprocessing.MinMaxScaler()
    train_x = min_max_scaler.fit_transform(data_selec)
    cluster_num_2 = round(data_2.shape[0] / 10)
    cluster_num_2_list.append(cluster_num_2)
    k_model = MiniBatchKMeans(n_clusters=cluster_num_2, max_iter=100, n_init=1,
                              reassignment_ratio=0.001)
    result = k_model.fit(train_x)
    predict_y = k_model.predict(train_x)
    if i == 0:
        data_new_test = pd.concat((data_2, pd.DataFrame(predict_y)), axis=1)
        data_new_test.rename({0: u'cluster_2'}, axis=1, inplace=True)
    else:
        data_new_test_1 = pd.concat((data_2, pd.DataFrame(predict_y + label_total)), axis=1)
        data_new_test_1.rename({0: u'cluster_2'}, axis=1, inplace=True)
        data_new_test = pd.concat((data_new_test, data_new_test_1), axis=0)
    label_total += cluster_num_2
data_new_test.reset_index(drop=True)
del data_new_test_1, data_2, predict_y, data_selec, train_x
gc.collect()

data_new_test_ = json.loads(data_new_test.to_json(orient="records"))
del data_new_test
gc.collect()

land_attribute_cluster_tag = []
cluster_result_list_tag = []
cluster_num_2_list = list(set(list(pd.DataFrame(data_new_test_)['cluster_2'])))
data_new_test_json = {}
for land_item in tqdm(data_new_test_):

    if int(land_item['cluster_2']) not in data_new_test_json.keys():
        data_new_test_json[int(land_item['cluster_2'])] = [land_item]
    else:
        data_new_test_json[int(land_item['cluster_2'])].append(land_item)
del data_new_test_
gc.collect()
no_biomass_plant_land = []
for i in tqdm(cluster_num_2_list):
    land_base = {'land_cluster_id': i}
    data_new_select = data_new_test_json[int(i)]
    land_base['pointid'] = [x['pointid'] for x in data_new_select]
    if len(land_base['pointid']) == 0:
        continue
    land_base['POINT_X'] = float(np.mean([x['POINT_X'] for x in data_new_select]))
    land_base['POINT_Y'] = float(np.mean([x['POINT_Y'] for x in data_new_select]))
    land_base['biomass_dry'] = [0, 0, 0, 0, 0, 0]
    land_base['biomass_wet'] = [0, 0, 0, 0, 0, 0]
    land_base['water'] = [0, 0, 0, 0, 0, 0]
    land_base['biomass_energy'] = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    land_base['biomass_emissions'] = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    land_base['biomass_cost'] = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    land_base['pre_energy'] = [0, 0, 0, 0, 0, 0]
    land_base['LUC_'] = [0, 0, 0, 0, 0, 0]
    land_base['pre_emissions'] = [0, 0, 0, 0, 0, 0]
    land_base['pre_cost'] = [0, 0, 0, 0, 0, 0]
    marginal_land_num = 0
    for item in data_new_select:
        if item['LUC'] in [22, 23, 31, 32, 33, 46, 45, 61, 63, 65]:
            marginal_land_num += 1
            select_, select_test_flag = select_biomass(item)
            if select_ != None:
                if select_ < 0:
                    break
            if item['Switchgrass'] and item['biomass_dry'][4] != 0 and select_test_flag == 1:

                biomass_dry = [0, 0, 0, 0, item['biomass_dry'][4], 0]
                biomass_wet = [0, 0, 0, 0, item['biomass_wet'][4], 0]
                water = [0, 0, 0, 0, item['water'][4], 0]
                biomass_energy = [0, 0, 0, 0, item['biomass_energy'][4][0:2], 0]
                biomass_emissions = [0, 0, 0, 0, item['biomass_emissions'][4][0:2], 0]
                biomass_cost = [0, 0, 0, 0, item['biomass_cost'][4][0:2], 0]
                pre_energy = [0, 0, 0, 0, item['biomass_energy'][4][2], 0]
                LUC_ = [0, 0, 0, 0, item['biomass_emissions'][4][2], 0]
                pre_emissions = [0, 0, 0, 0, item['biomass_emissions'][4][3], 0]
                pre_cost = [0, 0, 0, 0, item['biomass_cost'][4][2], 0]
            elif item['Sweet_sorghum'] and item['biomass_dry'][3] != 0 and select_test_flag == 2:

                biomass_dry = [0, 0, 0, item['biomass_dry'][3], 0, 0]
                biomass_wet = [0, 0, 0, item['biomass_wet'][3], 0, 0]
                water = [0, 0, 0, item['water'][3], 0, 0]
                biomass_energy = [0, 0, 0, item['biomass_energy'][3][0:2], 0, 0]
                biomass_emissions = [0, 0, 0, item['biomass_emissions'][3][0:2], 0, 0]
                biomass_cost = [0, 0, 0, item['biomass_cost'][3][0:2], 0, 0]
                pre_energy = [0, 0, 0, item['biomass_energy'][3][2], 0, 0]
                LUC_ = [0, 0, 0, item['biomass_emissions'][3][2], 0, 0]
                pre_emissions = [0, 0, 0, item['biomass_emissions'][3][3], 0, 0]
                pre_cost = [0, 0, 0, item['biomass_cost'][3][2], 0, 0]
            elif item['Miscanthus'] and item['biomass_dry'][5] != 0 and select_test_flag == 3:

                biomass_dry = [0, 0, 0, 0, 0, item['biomass_dry'][5]]
                biomass_wet = [0, 0, 0, 0, 0, item['biomass_wet'][5]]
                water = [0, 0, 0, 0, 0, item['water'][5]]
                biomass_energy = [0, 0, 0, 0, 0, item['biomass_energy'][5][0:2]]
                biomass_emissions = [0, 0, 0, 0, 0, item['biomass_emissions'][5][0:2]]
                biomass_cost = [0, 0, 0, 0, 0, item['biomass_cost'][5][0:2]]
                pre_energy = [0, 0, 0, 0, 0, item['biomass_energy'][5][2]]
                LUC_ = [0, 0, 0, 0, 0, item['biomass_emissions'][5][2]]
                pre_emissions = [0, 0, 0, 0, 0, item['biomass_emissions'][5][3]]
                pre_cost = [0, 0, 0, 0, 0, item['biomass_cost'][5][2]]
            elif item['biomass_dry'][2] != 0 and select_test_flag == 4:
                biomass_dry = item['biomass_dry']
                biomass_wet = item['biomass_wet']
                water = item['water']
                biomass_energy = [0, 0, item['biomass_energy'][2][0:2], 0, 0, 0]
                biomass_emissions = [0, 0, item['biomass_emissions'][2][0:2], 0, 0, 0]
                biomass_cost = [0, 0, item['biomass_cost'][2][0:2], 0, 0, 0]
                pre_energy = [0, 0, item['biomass_energy'][2][2], 0, 0, 0]
                LUC_ = [0, 0, item['biomass_emissions'][2][2], 0, 0, 0]
                pre_emissions = [0, 0, item['biomass_emissions'][2][3], 0, 0, 0]
                pre_cost = [0, 0, item['biomass_cost'][2][2], 0, 0, 0]
            else:

                biomass_dry = [0, 0, 0, 0, 0, 0]
                biomass_wet = [0, 0, 0, 0, 0, 0]
                water = [0, 0, 0, 0, 0, 0]
                biomass_energy = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
                biomass_emissions = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
                biomass_cost = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
                pre_energy = [0, 0, 0, 0, 0, 0]
                LUC_ = [0, 0, 0, 0, 0, 0]
                pre_emissions = [0, 0, 0, 0, 0, 0]
                pre_cost = [0, 0, 0, 0, 0, 0]
                no_biomass_plant_land.append(item)

        elif item['LUC'] == 11:
            select_test_6 = (item['biomass_dry'][0] * Data.biomass_Carbon_con['Rice'] * 44 / 12 -
                             (item['biomass_emissions'][0][0] + (item['biomass_emissions'][0][2]) / 35) / 1000) / \
                            (item['biomass_cost'][0][0])
            if select_test_6 < 0:
                continue
            biomass_dry = item['biomass_dry']
            biomass_wet = item['biomass_wet']
            water = item['water']
            biomass_energy = [item['biomass_energy'][0][0:2], 0, 0, 0, 0, 0]
            biomass_emissions = [item['biomass_emissions'][0][0:2], 0, 0, 0, 0, 0]
            biomass_cost = [item['biomass_cost'][0][0:2], 0, 0, 0, 0, 0]
            pre_energy = [item['biomass_energy'][0][2], 0, 0, 0, 0, 0]
            LUC_ = [item['biomass_emissions'][0][2], 0, 0, 0, 0, 0]
            pre_emissions = [item['biomass_emissions'][0][3], 0, 0, 0, 0, 0]
            pre_cost = [item['biomass_cost'][0][2], 0, 0, 0, 0, 0]

        elif item['LUC'] == 12:
            select_test_7 = (item['biomass_dry'][1] * Data.biomass_Carbon_con['Rice'] * 44 / 12 -
                             (item['biomass_emissions'][1][0] + (item['biomass_emissions'][1][2]) / 35) / 1000) / \
                            (item['biomass_cost'][1][0])
            if select_test_7 < 0:
                continue
            biomass_dry = item['biomass_dry']
            biomass_wet = item['biomass_wet']
            water = item['water']
            biomass_energy = [0, item['biomass_energy'][1][0:2], 0, 0, 0, 0]
            biomass_emissions = [0, item['biomass_emissions'][1][0:2], 0, 0, 0, 0]
            biomass_cost = [0, item['biomass_cost'][1][0:2], 0, 0, 0, 0]
            pre_energy = [0, item['biomass_energy'][1][2], 0, 0, 0, 0]
            LUC_ = [0, item['biomass_emissions'][1][2], 0, 0, 0, 0]
            pre_emissions = [0, item['biomass_emissions'][1][3], 0, 0, 0, 0]
            pre_cost = [0, item['biomass_cost'][1][2], 0, 0, 0, 0]

        elif item['LUC'] == 21:
            select_test_5 = (item['biomass_dry'][2] * Data.biomass_Carbon_con['Forestry_residue'] * 44 / 12 -
                             (item['biomass_emissions'][2][0] + item['biomass_emissions'][2][2] / 35) / 1000) / \
                            item['biomass_cost'][2][0]

            if select_test_5 < 0:
                continue
            biomass_dry = item['biomass_dry']
            biomass_wet = item['biomass_wet']
            water = item['water']
            biomass_energy = [0, 0, item['biomass_energy'][2][0:2], 0, 0, 0]
            biomass_emissions = [0, 0, item['biomass_emissions'][2][0:2], 0, 0, 0]
            biomass_cost = [0, 0, item['biomass_cost'][2][0:2], 0, 0, 0]
            pre_energy = [0, 0, item['biomass_energy'][2][2], 0, 0, 0]
            LUC_ = [0, 0, item['biomass_emissions'][2][2], 0, 0, 0]
            pre_emissions = [0, 0, item['biomass_emissions'][2][3], 0, 0, 0]
            pre_cost = [0, 0, item['biomass_cost'][2][2], 0, 0, 0]
        else:
            continue

        land_base['biomass_dry'] = [float(x) for x in
                                    list(np.array(land_base['biomass_dry']) + np.array(biomass_dry))]
        land_base['biomass_wet'] = [float(x) for x in
                                    list(np.array(land_base['biomass_wet']) + np.array(biomass_wet))]
        land_base['water'] = [float(x) for x in list(np.array(land_base['water']) + np.array(water))]
        land_base['biomass_energy'] = [np.array(land_base['biomass_energy'][i]) + np.array(biomass_energy[i])
                                       for i in range(6)]
        land_base['biomass_emissions'] = [
            np.array(land_base['biomass_emissions'][i]) + np.array(biomass_emissions[i]) for i in range(6)]
        land_base['biomass_cost'] = [np.array(land_base['biomass_cost'][i]) + np.array(biomass_cost[i]) for i in
                                     range(6)]
        land_base['pre_energy'] = [float(x) for x in
                                   list(np.array(land_base['pre_energy']) + np.array(pre_energy))]
        land_base['LUC_'] = [float(x) for x in
                             list(np.array(land_base['LUC_']) + np.array(LUC_))]
        land_base['pre_emissions'] = [float(x) for x in
                                      list(np.array(land_base['pre_emissions']) + np.array(pre_emissions))]
        land_base['pre_cost'] = [float(x) for x in
                                 list(np.array(land_base['pre_cost']) + np.array(pre_cost))]

        for i in range(6):
            try:
                land_base['biomass_energy'][i] = [float(x) for x in list(land_base['biomass_energy'][i])]
                land_base['biomass_emissions'][i] = [float(x) for x in list(land_base['biomass_emissions'][i])]
                land_base['biomass_cost'][i] = [float(x) for x in list(land_base['biomass_cost'][i])]
            except:
                print(f'{creat_time()} 报错了')
                land_base['biomass_energy'][i] = int(land_base['biomass_energy'][i])
                land_base['biomass_emissions'][i] = int(land_base['biomass_emissions'][i])
                land_base['biomass_cost'][i] = int(land_base['biomass_cost'][i])

    land_base['biomass_corbon'] = [x * Data.biomass_Carbon_con[item] for x, item in
                                   zip(land_base['biomass_dry'], Data.biomass_Carbon_con)]
    land_base['marginal_land_num'] = marginal_land_num
    if sum(land_base['biomass_dry']) == 0:
        continue
    if sum(land_base['biomass_dry'][3:6]) == 0:
        land_base['land_type'] = 0
    else:
        land_base['land_type'] = 1
    land_attribute_cluster_tag.append(land_base)
out_file = open(path + f"data/land_attribute_cluster_tag_new.json","w")
json.dump(land_attribute_cluster_tag, out_file)
out_file.close()
del no_biomass_plant_land, land_attribute_cluster_tag
gc.collect()

