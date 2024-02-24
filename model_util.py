import numpy as np
import pandas as pd
import math
from tqdm import tqdm
from DATA import Data
from COST import Cost
from EMISSIONS import Emissions
import datetime
import json
import traceback


def creat_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def select_biomass_OnlyMiscanthus(item):
    select_ = None
    select_test_flag = 0
    if item['Miscanthus'] and item['biomass_dry'][5] != 0:
        select_ = (item['biomass_dry'][5] * Data.biomass_Carbon_con['Miscanthus'] * 44 / 12 -
                   (item['biomass_emissions'][5][0] + item['biomass_emissions'][5][2] / 35) / 1000) / \
                  item['biomass_cost'][5][0]
        select_test_flag = 3
        if select_ < 0:
            select_ = None
            select_test_flag = 0

    if item['LUC'] in [22] and item['biomass_dry'][2] != 0:
        select_test_4 = (item['biomass_dry'][2] * Data.biomass_Carbon_con['Forestry_residue'] * 44 / 12 -
                         (item['biomass_emissions'][2][0] + item['biomass_emissions'][2][2] / 35) / 1000) / \
                        item['biomass_cost'][2][0]
        if select_ != None:
            if select_test_4 < select_ and select_test_4 > 0:
                select_ = select_test_4
                select_test_flag = 4
        elif select_test_4 > 0:
            select_ = select_test_4
            select_test_flag = 4
    return select_, select_test_flag


def select_biomass(item):
    select_ = None
    select_test_flag = 0
    if item['Switchgrass'] and item['biomass_dry'][4] != 0:
        select_ = (item['biomass_dry'][4] * Data.biomass_Carbon_con['Switchgrass'] * 44 / 12 -
                   (item['biomass_emissions'][4][0] + item['biomass_emissions'][4][2] / 35) / 1000) / \
                  item['biomass_cost'][4][0]
        select_test_flag = 1
        if select_ < 0:
            select_ = None
            select_test_flag = 0
    if item['Sweet_sorghum'] and item['biomass_dry'][3] != 0:
        select_test_2 = (item['biomass_dry'][3] * Data.biomass_Carbon_con['Sweet_sorghum'] * 44 / 12 -
                         (item['biomass_emissions'][3][0] + item['biomass_emissions'][3][2] / 35) / 1000) / \
                        item['biomass_cost'][3][0]
        if select_ != None:
            if select_test_2 < select_ and select_test_2 > 0:
                select_ = select_test_2
                select_test_flag = 2
        elif select_test_2 > 0:
            select_ = select_test_2
            select_test_flag = 2

    if item['Miscanthus'] and item['biomass_dry'][5] != 0:
        select_test_3 = (item['biomass_dry'][5] * Data.biomass_Carbon_con['Miscanthus'] * 44 / 12 -
                         (item['biomass_emissions'][5][0] + item['biomass_emissions'][5][2] / 35) / 1000) / \
                        item['biomass_cost'][5][0]
        if select_ != None:
            if select_test_3 < select_ and select_test_3 > 0:
                select_ = select_test_3
                select_test_flag = 3
        elif select_test_3 > 0:
            select_ = select_test_3
            select_test_flag = 3

    if item['LUC'] in [22] and item['biomass_dry'][2] != 0:
        select_test_4 = (item['biomass_dry'][2] * Data.biomass_Carbon_con['Forestry_residue'] * 44 / 12 -
                         (item['biomass_emissions'][2][0] + item['biomass_emissions'][2][2] / 35) / 1000) / \
                        item['biomass_cost'][2][0]
        if select_ != None:
            if select_test_4 < select_ and select_test_4 > 0:
                select_ = select_test_4
                select_test_flag = 4
        elif select_test_4 > 0:
            select_ = select_test_4
            select_test_flag = 4
    return select_, select_test_flag


def biomass_sum(item, key_biomass_param, Carbon_con, sweet_sorghum='', biomass='Straw'):
    Solid_recovery = [0.98, 0.98, 0.98, 0.98, 0.95]
    biomass_origin = 0
    if biomass == 'Straw':
        biomass_origin = Straw_biomass_sum(item, key_biomass_param, Carbon_con)
    elif biomass == 'Forestry_residue':
        if item['forestry_residues'] != None:
            biomass_origin = item['forestry_residues'] * (1 - key_biomass_param['r_rs1'])
    elif biomass == 'Switchgrass':

        if item['Switchgrass_biomass_origin'] != None:
            biomass_origin = item['Switchgrass_biomass_origin'] * 100
    elif biomass == 'Sweet_sorghum':
        biomass_origin = Sweet_Sorghum_biomass_sum(land_item=item, sweet_sorghum=sweet_sorghum)
    elif biomass == 'Miscanthus':
        biomass_origin = Miscanthus_biomass_sum(land_item=item, key_biomass_param=key_biomass_param)
    Solid_rec = np.prod([pow(i, j) for i, j in zip(Solid_recovery, key_biomass_param['Solid_rec'])])
    biomass_dry = Solid_rec * biomass_origin
    biomass_wet = biomass_origin / (1 - key_biomass_param['moi_wet'])
    return biomass_dry, biomass_wet


def Straw_biomass_sum(item, key_biomass_param, Carbon_con):
    H_TL = item['straw']
    H_RS = H_TL * (1 - key_biomass_param['r_rc'])
    biomass_origin = H_RS
    return biomass_origin


def Miscanthus_biomass_sum(land_item, key_biomass_param):
    pre_name = ['pre_20201', 'pre_20202', 'pre_20203', 'pre_20204', 'pre_20205', 'pre_20206', 'pre_20207',
                'pre_20208', 'pre_20209', 'pre_202010', 'pre_202011', 'pre_202012']
    pre_init = 0
    for key_item in pre_name:
        if land_item[key_item] == None:
            pass
        else:
            pre_init += land_item[key_item] / 10
    if 1000 <= pre_init and land_item['min'] / 10 >= 1:
        H_t_ck = 1300
        a = 0.785
        b = 0.00210
        H_min = 560
        P_ck = pre_init
        Y_ck = 38
    elif 1000 > pre_init and 760 <= pre_init and land_item['min'] / 10 < 1 and land_item['min'] / 10 > -3:
        H_t_ck = 1500
        a = 0.803
        b = 0.00027
        H_min = 670
        P_ck = 1315
        Y_ck = 41.5
    elif 760 > pre_init and 400 < pre_init and land_item['min'] / 10 < -3 and land_item['min'] / 10 > -23:

        if land_item['flag'] == 1:
            H_t_ck = 1300
            a = 0.182
            b = 0.00129
            H_min = 1100
            P_ck = 550
            Y_ck = 37.5
        if land_item['flag'] == 2:
            H_t_ck = 1600
            a = 0.684
            b = 0.00155
            H_min = 950
            P_ck = 570
            Y_ck = 39.0
        if land_item['flag'] == 3:
            H_t_ck = 1600
            a = 0.684
            b = 0.00155
            H_min = 950
            P_ck = 800
            Y_ck = 43.8
        if land_item['flag'] == 0:
            return None, None
    else:
        return None, None
    P_n = pre_init
    H_n = land_item['sunshine_year'] * 0.1
    biomass_origin = ((1 + a * math.e ** (-b * (H_t_ck - H_min))) * P_n * Y_ck) / (
            (1 + a * math.e ** (-b * (H_n - H_min))) * P_ck)
    if land_item['LUC'] in [61]:
        biomass_origin = biomass_origin * 8.4 / 100
    if land_item['LUC'] in [65]:
        biomass_origin = biomass_origin * 9 / 100
    if land_item['LUC'] in [46, 63]:
        biomass_origin = biomass_origin * 60 / 100
    if land_item['LUC'] in [33]:
        biomass_origin = biomass_origin * 69 / 100

    biomass_origin = biomass_origin * 0.8
    return biomass_origin * 100


def Sweet_Sorghum_biomass_sum(land_item, sweet_sorghum):
    pre_name = ['pre_20206', 'pre_20207', 'pre_20208', 'pre_20209', 'pre_202010']

    pre_init = 0
    for key_item in pre_name:
        if land_item[key_item] == None:
            pass
        else:
            if key_item == 'pre_20210':
                pre_init += land_item[key_item] / 10 * 8 / 31
            else:
                pre_init += land_item[key_item] / 10

    temp_name = ['tmp_Layer201706', 'tmp_Layer201707', 'tmp_Layer201708', 'tmp_Layer201709', 'tmp_Layer201710']
    temp_days = [30, 31, 31, 30, 8]
    temp_init = 0
    temp_constr = False
    for key_item, days in zip(temp_name, temp_days):
        if land_item[key_item] == None:
            pass
        elif land_item[key_item] / 10 <= 10:
            temp_constr = True
            break
        else:
            temp_init += land_item[key_item] / 10 * days

    if land_item['PH_Layer'] == None or land_item['SA_Layer'] == None or land_item[
        'Slope_dem_1k2'] == None or temp_constr:
        return False
    biomass_origin = 0
    if temp_init >= 2500 and land_item['SA_Layer'] <= 85:

        if (pre_init <= 200 or pre_init >= 1500) and land_item['Slope_dem_1k2'] <= 25:
            biomass_origin = sweet_sorghum[str(int(land_item['ProvinceID']))] * 0.25 * 100

        elif pre_init >= 200 and pre_init <= 400 and land_item['Slope_dem_1k2'] <= 15:
            biomass_origin = sweet_sorghum[str(int(land_item['ProvinceID']))] * 0.8 * 100

        elif pre_init >= 400 and pre_init <= 1500 and land_item['Slope_dem_1k2'] <= 10:
            biomass_origin = sweet_sorghum[str(int(land_item['ProvinceID']))] * 1 * 100
    return biomass_origin


def Miscanthus(land_item):
    pre_name = ['pre_20201', 'pre_20202', 'pre_20203', 'pre_20204', 'pre_20205', 'pre_20206', 'pre_20207',
                'pre_20208', 'pre_20209', 'pre_202010', 'pre_202011', 'pre_202012']
    pre_init = 0
    for key_item in pre_name:
        if land_item[key_item] == None:

            pass
        else:
            pre_init += land_item[key_item] / 10
    try:
        if 400 <= pre_init and land_item['min'] / 10 >= -23:
            return True
        else:
            return False
    except:
        return False


def Switchgrass(land_item):
    pre_name = ['pre_20205', 'pre_20206', 'pre_20207', 'pre_20208', 'pre_20209']
    pre_init = 0
    for key_item in pre_name:
        if land_item[key_item] == None:
            pass
        else:
            if key_item == 'pre_20209':
                pre_init += land_item[key_item] / 10 * 12 / 30
            else:
                pre_init += land_item[key_item] / 10
    temp_name = ['tmp_Layer201705', 'tmp_Layer201706', 'tmp_Layer201707', 'tmp_Layer201708', 'tmp_Layer201709']
    temp_days = [31, 30, 31, 31, 12]
    temp_init = 0
    temp_constr = False
    for key_item, days in zip(temp_name, temp_days):
        if land_item[key_item] == None:
            pass
        elif land_item[key_item] / 10 <= 10:
            temp_constr = True
            break
        else:
            temp_init += land_item[key_item] / 10 * days

    if land_item['PH_Layer'] == None or land_item['AP_Layer'] == None or temp_constr:
        return False
    if 200 <= pre_init and temp_init >= 1777 and land_item['PH_Layer'] >= 4.9 and land_item[
        'PH_Layer'] <= 8.0:
        return True
    else:
        return False


def Sweet_sorghum(land_item):
    pre_name = ['pre_20206', 'pre_20207', 'pre_20208', 'pre_20209', 'pre_202010']

    pre_init = 0
    for key_item in pre_name:
        if land_item[key_item] == None:
            pass
        else:
            if key_item == 'pre_20210':
                pre_init += land_item[key_item] / 10 * 8 / 31
            else:
                pre_init += land_item[key_item] / 10

    temp_name = ['tmp_Layer201706', 'tmp_Layer201707', 'tmp_Layer201708', 'tmp_Layer201709', 'tmp_Layer201710']
    temp_days = [30, 31, 31, 30, 8]
    temp_init = 0
    temp_constr = False
    for key_item, days in zip(temp_name, temp_days):
        if land_item[key_item] == None:
            pass
        elif land_item[key_item] / 10 <= 10:
            temp_constr = True
            break
        else:
            temp_init += land_item[key_item] / 10 * days

    if land_item['PH_Layer'] == None or land_item['SA_Layer'] == None or land_item[
        'Slope_dem_1k2'] == None or temp_constr:
        return False
    if pre_init >= 200 and temp_init >= 2500 and land_item['PH_Layer'] >= 5.0 and land_item['PH_Layer'] <= 8.5 and \
            land_item['SA_Layer'] <= 85 and land_item['Slope_dem_1k2'] <= 25:
        return True
    else:
        return False


def rad(d):
    return d * math.pi / 180


def distance_cal(first_long_lat, second_long_lat):
    radlat1 = rad(first_long_lat[1])
    radlat2 = rad(second_long_lat[1])
    a = radlat1 - radlat2
    b = rad(first_long_lat[0]) - rad(second_long_lat[0])
    s = 2 * math.asin(
        math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(radlat1) * math.cos(radlat2) * math.pow(math.sin(b / 2), 2)))
    earth_radius = 6378.137
    distance = s * earth_radius
    if distance < 0:
        return -distance
    else:
        return distance


def local_ele_ProvinceID(ele_item, point_pop_pm25, city_code_json):
    try:
        point_pop_pm25_item = land_pre_selected(ele_item=ele_item, land_total=point_pop_pm25, dist_constr=100,
                                                flag=5)
        if point_pop_pm25_item['city'] == 310200:
            CityCode = 310100
        elif point_pop_pm25_item['city'] == 500200:
            CityCode = 500100
        elif point_pop_pm25_item['city'] == 120200:
            CityCode = 120100
        elif point_pop_pm25_item['city'] == 110200:
            CityCode = 110100
        elif point_pop_pm25_item['city'] in [710000]:
            CityCode = None
        else:
            CityCode = point_pop_pm25_item['city']

        if CityCode == 810100:
            ProvinceID_select = 810000
        elif CityCode == 469000:
            ProvinceID_select = 460000
        elif CityCode == 659000:
            ProvinceID_select = 650000
        elif CityCode == 419000:
            ProvinceID_select = 410000
        else:
            ProvinceID_select = city_code_json[str(CityCode)]['ProvinceID']

    except BaseException as e:

        print(f"{creat_time()} final error: {traceback.format_exc()}")
    return ProvinceID_select


def land_pre_selected(ele_item, land_total, exce_list=[], dist_low=0, dist_constr=1000, flag=0):
    select_land = []
    dist_list = []
    if flag == 0:
        select_land = {}

        for land_key in tqdm(land_total):
            land_item = land_total[land_key]
            dist = distance_cal(first_long_lat=[ele_item['lng'], ele_item['lat']],
                                second_long_lat=[land_item['POINT_X'], land_item['POINT_Y']])
            if dist <= dist_constr:
                select_land[land_key] = land_item


    elif flag == 1:
        select_land = {'use': [], 'unuse': []}
        JW_constr = round(dist_constr / 111)
        JW_constr_2000 = round(2000 / 111)
        JW_low = round(dist_low / 111)

        for land_item in land_total:

            lng = abs(land_item['POINT_X'] - ele_item['lng'])
            lat = abs(land_item['POINT_Y'] - ele_item['lat'])

            if (lng < JW_constr or lat < JW_constr) and (lng > JW_low or lat > JW_low):
                dist = distance_cal(first_long_lat=[ele_item['lng'], ele_item['lat']],
                                    second_long_lat=[land_item['POINT_X'], land_item['POINT_Y']])
                if dist <= dist_constr and dist > dist_low:
                    select_land['use'].append(land_item)
                elif dist <= 2000:
                    select_land['unuse'].append(land_item)
            elif lng < JW_constr_2000 or lat < JW_constr_2000:
                select_land['unuse'].append(land_item)
    elif flag == 'pop':
        select_land = {'use': [], 'unuse': [], 'pop': 0}
        JW_constr = round(dist_constr / 111) + 0.1
        JW_constr_2000 = round(2000 / 111) + 0.1
        JW_low = round(dist_low / 111) + 0.1

        for land_item in land_total:
            lng = abs(land_item['POINT_X'] - ele_item['lng'])
            lat = abs(land_item['POINT_Y'] - ele_item['lat'])
            if land_item['pop_2020'] != 0:
                if (lng < JW_constr or lat < JW_constr) and (lng > JW_low or lat > JW_low):
                    dist = distance_cal(first_long_lat=[ele_item['lng'], ele_item['lat']],
                                        second_long_lat=[land_item['POINT_X'], land_item['POINT_Y']])
                    if dist <= dist_constr and dist > dist_low:
                        select_land['use'].append(land_item)
                        select_land['pop'] += land_item['pop_2020']
                    elif dist <= 2000:
                        select_land['unuse'].append(land_item)
                elif lng < JW_constr_2000 or lat < JW_constr_2000:
                    select_land['unuse'].append(land_item)
    elif flag == 2:
        for land_item in land_total:
            if abs(land_item['lng'] - ele_item['lng']) > 2 or abs(land_item['lat'] - ele_item['lat']) > 10:
                pass
            else:
                dist = distance_cal(first_long_lat=[ele_item['lng'], ele_item['lat']],
                                    second_long_lat=[land_item['lng'], land_item['lat']])
                if dist <= dist_constr:
                    select_land.append(land_item)
    elif flag == 3:
        dist = dist_constr
        for land_item in land_total:
            if land_item['status'] in ['operating', 'Operating']:
                dist = distance_cal(first_long_lat=[ele_item['lng'], ele_item['lat']],
                                    second_long_lat=[land_item['lng'], land_item['lat']])
                if dist <= dist_constr:
                    select_land.append(land_item)
                    dist_constr = dist
    elif flag == 4:
        for land_item in land_total:
            if abs(land_item['lng'] - ele_item['lng']) > 1 or abs(land_item['lat'] - ele_item['lat']) > 1:
                pass
            else:
                dist = distance_cal(first_long_lat=[ele_item['lng'], ele_item['lat']],
                                    second_long_lat=[land_item['lng'], land_item['lat']])
                if dist <= dist_constr:
                    select_land.append(land_item)
    elif flag == 5:

        select_land = {}
        for land_item in land_total:
            if abs(land_item['POINT_X'] - ele_item['lng']) > 1 or abs(land_item['POINT_Y'] - ele_item['lat']) > 1:
                pass
            else:
                dist = distance_cal(first_long_lat=[ele_item['lng'], ele_item['lat']],
                                    second_long_lat=[land_item['POINT_X'], land_item['POINT_Y']])
                if dist <= dist_constr:
                    select_land = land_item
                    dist_constr = dist
    elif flag == 'prec':

        select_land = {}
        select_land = {'use': [], 'unuse': []}
        for land_item in land_total:
            if land_item['pointid'] not in exce_list and (abs(land_item['POINT_X'] - ele_item['lng']) < 2 or abs(
                    land_item['POINT_Y'] - ele_item['lat']) < 2):
                dist = distance_cal(first_long_lat=[ele_item['lng'], ele_item['lat']],
                                    second_long_lat=[land_item['POINT_X'], land_item['POINT_Y']])
                if dist <= dist_constr:
                    select_land['use'] = land_item
                    dist_constr = dist
                select_land['unuse'].append(land_item)
    return select_land


def ele_coal_CO2(ele_item):
    if ele_item['type'] in ['subcritical', 'Subcritical', 'Subcritical / Supercritical',
                            'Subcritical / Unknown', 'Unknown', 'Unknown / Subcritical', 'subcritical']:
        type_is = 'Subcritical'
    elif ele_item['type'] in ['Supercritical', 'Supercritical / Subcritical', 'supercritical']:
        type_is = 'Supercritical'
    elif ele_item['type'] in ['Ultra-super']:
        type_is = 'Ultra_supercritical'
    elif ele_item['type'] in ['CFB']:
        type_is = 'Subcritical_fluidized_bed'
    elif ele_item['type'] in ['IGCC']:
        type_is = 'IGCC'
    else:
        type_is = None

    if float(ele_item['capacity']) >= 600 and float(ele_item['capacity']) < 1000:
        theta = 1.05
    elif float(ele_item['capacity']) >= 300 and float(ele_item['capacity']) < 600:
        theta = 1.1
    elif float(ele_item['capacity']) < 300:
        theta = 1.2
    else:
        theta = 1

    if ele_item['year'] != '':
        eff_adj = ((2021 - int(ele_item['year'])) / 100 - 0.1)
        age = 2021 - int(ele_item['year'])
        year_flag = 1
    else:

        eff_adj = 0
        age = 0
        year_flag = 0
    if type_is != 'IGCC' and type_is != 'None':

        real_Efficiencies = Data.Efficiencies[type_is] / theta + eff_adj
    else:
        real_Efficiencies = Data.Efficiencies[type_is] + eff_adj

    ele_coal = coal_consumption(TC=ele_item['capacity'],
                                plant_efficiency=real_Efficiencies,
                                OH=Data.power_plant_hours_Province[ele_item['ProvinceID']])
    ele_CO2 = ele_coal * Data.coal_Carbon_con * 44 / 12
    return ele_coal, ele_CO2, year_flag, age


def coal_consumption(TC, plant_efficiency=0.249, OH=7800):
    if OH == 7800:
        # 这个时候考虑的是运行小时数，运行小时数指发电机并网到解列这段运行期间的天然小时数
        capacity_factor = 0.8
        coal_con = ((TC * capacity_factor / plant_efficiency) * OH * 3600) / Data.coal_LHV
    else:
        # 这时考虑的是利用小时数，发电机组利用小时数等于全年发电量除以机组核定的铭牌出力，此时不需要考虑capacity_factor
        coal_con = ((TC / plant_efficiency) * OH * 3600) / Data.coal_LHV
    return coal_con


def water_sum(ETM, pre):
    water = ((ETM - pre / 10) / 1000) * 1000
    if water >= 0:

        return water
    else:
        return 0


def MJ_TO_KWh(MJ, OH, plant_efficiency=0.264, flag=True):
    if flag == 2:
        kwh = (MJ / 3600) * 1000 * plant_efficiency
        plant_capacity = kwh / OH / 1000
        return kwh, plant_capacity
    elif flag == 1:
        return MJ * 1000 * OH
    else:
        plant_capacity = MJ * 100000000 / OH / 1000
        return plant_capacity


def land_def(data_land, select_22=None, path='D:/BECCS_', Data=Data):
    sweet_sorghum_data = pd.read_csv(path + 'data/sweet_sorghum.csv')
    sweet_sorghum_data.index = sweet_sorghum_data['Pro']
    sweet_sorghum = json.loads(sweet_sorghum_data[['2020']].T.to_json(orient="records"))[0]
    cost = Cost(Data)
    emissions = Emissions(Data)
    land_analysis_all = []
    land_attribute_rice = []
    land_attribute_Wheat_Corn = []
    land_attribute_Forestry_residue = []
    land_attribute_three_biomass = []
    land_attribute_fail = []
    for item in tqdm(data_land):

        if item.get('ProvinceID') == None and item['LUC'] in [31, 32]:
            item['ProvinceID'] = '000000'
        if item['LUC'] in [11, 12, 21, 22, 23, 33, 46, 45, 61, 63, 65] or (
                item['LUC'] in [31, 32] and int(item['ProvinceID']) not in [630000, 650000, 540000, 150000]):

            land_base = {

                "pointid": item['pointid'],
                "LUC": item['LUC'],
                "POINT_X": item['POINT_X'],
                "POINT_Y": item['POINT_Y'],
                "NPP": item['NPP'],

            }
            if item.get('Sweet_sorghum') != None:
                land_base['Sweet_sorghum'] = item['Sweet_sorghum']
                land_base['Switchgrass'] = item['Switchgrass']
                land_base['Miscanthus'] = item['Miscanthus']
            land_analysis = {
                "pointid": item['pointid'],
                "LUC": item['LUC'],

            }
            try:

                if item['LUC'] == 11:

                    if item['NPP'] > 65500:
                        land_attribute_fail.append(item)
                        continue
                    key_biomass_param = Data.biomass_param['Rice']
                    Rice_dry, Rice_wet = biomass_sum(item=item, key_biomass_param=key_biomass_param,
                                                     Carbon_con=Data.biomass_Carbon_con['Rice'], biomass='Straw')

                    Rice_emissions, Rice_trans_emissions, Rice_LUC_, Rice_pre_emissions, Rice_emissions_all = emissions.land_emissions(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Rice_wet,
                        biomass_dry=Rice_dry,
                        biomass_type='Straw',
                        land_item=item)

                    Rice_cost, Rice_trans_cost, Rice_pre_cost, Rice_cost_all = cost.land_cost(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Rice_wet,
                        biomass_dry=Rice_dry,
                        biomass_type='Straw')
                    land_base['biomass_dry'] = [Rice_dry, 0, 0, 0, 0, 0]
                    land_base['biomass_wet'] = [Rice_wet, 0, 0, 0, 0, 0]
                    land_base['biomass_emissions'] = [
                        [Rice_emissions, Rice_trans_emissions, Rice_LUC_, Rice_pre_emissions], 0, 0, 0, 0, 0]
                    land_base['biomass_cost'] = [[Rice_cost, Rice_trans_cost, Rice_pre_cost], 0, 0, 0, 0, 0]
                    land_base['water'] = [0, 0, 0, 0, 0, 0]
                    land_analysis['emissions_all'] = [Rice_emissions_all, 0, 0, 0, 0, 0]
                    land_analysis['cost_all'] = [Rice_cost_all, 0, 0, 0, 0, 0]
                    if sum(land_base['biomass_dry']) == 0:
                        land_attribute_fail.append(item)
                        continue
                    else:
                        land_attribute_rice.append(land_base)
                        land_analysis_all.append(land_analysis)
                        continue
            except BaseException as e:

                pass
            try:

                if item['LUC'] == 12:

                    if item['NPP'] == None or item['NPP'] > 65500:
                        land_attribute_fail.append(item)
                        continue
                    key_biomass_param = Data.biomass_param['Wheat_Corn']
                    Wheat_Corn_dry, Wheat_Corn_wet = biomass_sum(item=item, key_biomass_param=key_biomass_param,
                                                                 Carbon_con=Data.biomass_Carbon_con['Wheat_Corn'],
                                                                 biomass='Straw')

                    Wheat_Corn_emissions, Wheat_Corn_trans_emissions, Wheat_Corn_LUC_, Wheat_Corn_pre_emissions, Wheat_Corn_emissions_all = emissions.land_emissions(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Wheat_Corn_wet,
                        biomass_dry=Wheat_Corn_dry,
                        biomass_type='Straw',
                        land_item=item)

                    Wheat_Corn_cost, Wheat_Corn_trans_cost, Wheat_Corn_pre_cost, Wheat_Corn_cost_all = cost.land_cost(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Wheat_Corn_wet,
                        biomass_dry=Wheat_Corn_dry,
                        biomass_type='Straw')

                    land_base['biomass_dry'] = [0, Wheat_Corn_dry, 0, 0, 0, 0]
                    land_base['biomass_wet'] = [0, Wheat_Corn_wet, 0, 0, 0, 0]

                    land_base['biomass_emissions'] = [0, [Wheat_Corn_emissions, Wheat_Corn_trans_emissions,
                                                          Wheat_Corn_LUC_, Wheat_Corn_pre_emissions], 0, 0, 0, 0]
                    land_base['biomass_cost'] = [0, [Wheat_Corn_cost, Wheat_Corn_trans_cost, Wheat_Corn_pre_cost], 0, 0,
                                                 0, 0]
                    land_base['water'] = [0, 0, 0, 0, 0, 0]
                    land_analysis['emissions_all'] = [0, Wheat_Corn_emissions_all, 0, 0, 0, 0]
                    land_analysis['cost_all'] = [0, Wheat_Corn_cost_all, 0, 0, 0, 0]
                    if sum(land_base['biomass_dry']) == 0:
                        land_attribute_fail.append(item)
                        continue
                    else:
                        land_attribute_Wheat_Corn.append(land_base)
                        land_analysis_all.append(land_analysis)
                        continue
            except BaseException as e:

                pass
            try:

                if item['LUC'] in [21, select_22]:
                    key_biomass_param = Data.biomass_param['Forestry_residue']
                    Forestry_residue_dry, Forestry_residue_wet = biomass_sum(item=item,
                                                                             key_biomass_param=key_biomass_param,
                                                                             Carbon_con=Data.biomass_Carbon_con[
                                                                                 'Forestry_residue'],
                                                                             biomass='Forestry_residue'
                                                                             )

                    Forestry_residue_emissions, Forestry_residue_trans_emissions, Forestry_residue_LUC_, Forestry_residue_pre_emissions, Forestry_residue_emissions_all = emissions.land_emissions(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Forestry_residue_wet,
                        biomass_dry=Forestry_residue_dry,
                        biomass_type='Forestry_residue',
                        land_item=item)

                    Forestry_residue_cost, Forestry_residue_trans_cost, Forestry_residue_pre_cost, Forestry_residue_cost_all = cost.land_cost(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Forestry_residue_wet,
                        biomass_dry=Forestry_residue_dry,
                        biomass_type='Forestry_residue')

                    land_base['biomass_dry'] = [0, 0, Forestry_residue_dry, 0, 0, 0]
                    land_base['biomass_wet'] = [0, 0, Forestry_residue_wet, 0, 0, 0]
                    land_base['biomass_emissions'] = [0, 0,
                                                      [Forestry_residue_emissions, Forestry_residue_trans_emissions,
                                                       Forestry_residue_LUC_, Forestry_residue_pre_emissions], 0, 0, 0]
                    land_base['biomass_cost'] = [0, 0, [Forestry_residue_cost, Forestry_residue_trans_cost,
                                                        Forestry_residue_pre_cost], 0, 0, 0]
                    land_base['water'] = [0, 0, 0, 0, 0, 0]
                    land_analysis['emissions_all'] = [0, 0, Forestry_residue_emissions_all, 0, 0, 0]
                    land_analysis['cost_all'] = [0, 0, Forestry_residue_cost_all, 0, 0, 0]
                    if sum(land_base['biomass_dry']) == 0:
                        land_attribute_fail.append(item)
                        continue
                    else:
                        land_attribute_Forestry_residue.append(land_base)
                        land_analysis_all.append(land_analysis)
                        continue
            except:

                pass

            if item['LUC'] in [22, 23, 33, 46, 45, 61, 63, 65] or (
                    item['LUC'] in [31, 32] and int(item['ProvinceID']) not in [630000, 650000, 540000, 150000]):
                try:

                    key_biomass_param = Data.biomass_param['Sweet_sorghum']
                    Sweet_sorghum_dry, Sweet_sorghum_wet = biomass_sum(item=item, key_biomass_param=key_biomass_param,
                                                                       Carbon_con=Data.biomass_Carbon_con[
                                                                           'Sweet_sorghum'],
                                                                       sweet_sorghum=sweet_sorghum,
                                                                       biomass='Sweet_sorghum',
                                                                       )

                    pre = 0
                    pre_date_list = ['pre_20206', 'pre_20207', 'pre_20208', 'pre_20209', 'pre_202010']
                    for idx in range(len(pre_date_list)):
                        pre_date = pre_date_list[idx]
                        if item[pre_date] == None and idx != len(pre_date_list) - 1:
                            pre_date = pre_date_list[idx + 1]
                        elif item[pre_date] == None and idx == len(pre_date_list) - 1:
                            pre_date = pre_date_list[idx - 1]
                        if idx == len(pre_date_list) - 1:
                            pre += item[pre_date] * 8 / 31
                        else:
                            pre += item[pre_date]
                    water_sweet = water_sum(ETM=item['sweet'], pre=pre)

                    Sweet_sorghum_emissions, Sweet_sorghum_trans_emissions, Sweet_sorghum_LUC_, Sweet_sorghum_pre_emissions, Sweet_sorghum_emissions_all = emissions.land_emissions(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Sweet_sorghum_wet,
                        biomass_dry=Sweet_sorghum_dry,
                        biomass_type='Sweet_sorghum',
                        land_item=item)

                    Sweet_sorghum_cost, Sweet_sorghum_trans_cost, Sweet_sorghum_pre_cost, Sweet_sorghum_cost_all = cost.land_cost(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Sweet_sorghum_wet,
                        biomass_dry=Sweet_sorghum_dry,
                        water=water_sweet,
                        biomass_type='Sweet_sorghum')
                except:

                    Sweet_sorghum_dry = 0
                    Sweet_sorghum_wet = 0

                    Sweet_sorghum_emissions = 0
                    Sweet_sorghum_trans_emissions = 0
                    Sweet_sorghum_LUC_ = 0
                    Sweet_sorghum_cost = 0
                    Sweet_sorghum_trans_cost = 0

                    Sweet_sorghum_pre_emissions = 0
                    Sweet_sorghum_pre_cost = 0

                    Sweet_sorghum_emissions_all = [0, 0, 0, 0, 0, 0]
                    Sweet_sorghum_cost_all = [0, 0, 0, 0, 0, 0]
                    water_sweet = 0
                try:

                    key_biomass_param = Data.biomass_param['Switchgrass']
                    Switchgrass_dry, Switchgrass_wet = biomass_sum(item=item, key_biomass_param=key_biomass_param,
                                                                   Carbon_con=Data.biomass_Carbon_con['Switchgrass'],
                                                                   biomass='Switchgrass')

                    pre = 0
                    pre_date_list = ['pre_20205', 'pre_20206', 'pre_20207', 'pre_20208', 'pre_20209']
                    for idx in range(len(pre_date_list)):
                        pre_date = pre_date_list[idx]
                        if item[pre_date] == None and idx != len(pre_date_list) - 1:
                            pre_date = pre_date_list[idx + 1]
                        elif item[pre_date] == None and idx == len(pre_date_list) - 1:
                            pre_date = pre_date_list[idx - 1]
                        if idx == len(pre_date_list) - 1:
                            pre += item[pre_date] * 12 / 30
                        else:
                            pre += item[pre_date]

                    water_Swit = water_sum(ETM=item['Swit'], pre=pre)

                    Switchgrass_emissions, Switchgrass_trans_emissions, Switchgrass_LUC_, Switchgrass_pre_emissions, Switchgrass_emissions_all = emissions.land_emissions(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Switchgrass_wet,
                        biomass_dry=Switchgrass_dry,
                        biomass_type='Switchgrass',
                        land_item=item)

                    Switchgrass_cost, Switchgrass_trans_cost, Switchgrass_pre_cost, Switchgrass_cost_all = cost.land_cost(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Switchgrass_wet,
                        biomass_dry=Switchgrass_dry,
                        water=water_Swit,
                        biomass_type='Switchgrass')
                except:

                    Switchgrass_dry = 0
                    Switchgrass_wet = 0

                    Switchgrass_emissions = 0
                    Switchgrass_trans_emissions = 0
                    Switchgrass_LUC_ = 0
                    Switchgrass_cost = 0
                    Switchgrass_trans_cost = 0

                    Switchgrass_pre_emissions = 0
                    Switchgrass_pre_cost = 0

                    Switchgrass_emissions_all = [0, 0, 0, 0, 0, 0]
                    Switchgrass_cost_all = [0, 0, 0, 0, 0, 0]
                    water_Swit = 0
                try:

                    key_biomass_param = Data.biomass_param['Miscanthus']

                    Miscanthus_dry, Miscanthus_wet = biomass_sum(item=item, key_biomass_param=key_biomass_param,
                                                                 Carbon_con=Data.biomass_Carbon_con['Miscanthus'],
                                                                 biomass='Miscanthus')
                    if Miscanthus_dry == None:
                        raise BaseException('Miscanthus error')

                    pre = 0
                    pre_date_list = ['pre_20207', 'pre_20208', 'pre_20209', 'pre_202010', 'pre_202011',
                                     'pre_202012', 'pre_20201',
                                     'pre_20202', 'pre_20203']
                    for idx in range(len(pre_date_list)):
                        pre_date = pre_date_list[idx]
                        if item[pre_date] == None and idx != len(pre_date_list) - 1:
                            pre_date = pre_date_list[idx + 1]
                        elif item[pre_date] == None and idx == len(pre_date_list) - 1:
                            pre_date = pre_date_list[idx - 1]
                        pre += item[pre_date]

                    water_mc = water_sum(ETM=item['mc'], pre=pre)

                    Miscanthus_emissions, Miscanthus_trans_emissions, Miscanthus_LUC_, Miscanthus_pre_emissions, Miscanthus_emissions_all = emissions.land_emissions(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Miscanthus_wet,
                        biomass_dry=Miscanthus_dry,
                        biomass_type='Miscanthus',
                        land_item=item)

                    Miscanthus_cost, Miscanthus_trans_cost, Miscanthus_pre_cost, Miscanthus_cost_all = cost.land_cost(
                        key_biomass_param=key_biomass_param,
                        biomass_wet=Miscanthus_wet,
                        biomass_dry=Miscanthus_dry,
                        water=water_mc,
                        biomass_type='Miscanthus')

                except BaseException as e:

                    Miscanthus_dry = 0
                    Miscanthus_wet = 0

                    Miscanthus_emissions = 0
                    Miscanthus_trans_emissions = 0
                    Miscanthus_LUC_ = 0
                    Miscanthus_cost = 0
                    Miscanthus_trans_cost = 0

                    Miscanthus_pre_emissions = 0
                    Miscanthus_pre_cost = 0

                    Miscanthus_emissions_all = [0, 0, 0, 0, 0, 0]
                    Miscanthus_cost_all = [0, 0, 0, 0, 0, 0]
                    water_mc = 0
                land_base['biomass_dry'] = [0, 0, 0, Sweet_sorghum_dry, Switchgrass_dry, Miscanthus_dry]
                land_base['biomass_wet'] = [0, 0, 0, Sweet_sorghum_wet, Switchgrass_wet, Miscanthus_wet]

                land_base['biomass_emissions'] = [0, 0, 0, [Sweet_sorghum_emissions, Sweet_sorghum_trans_emissions,
                                                            Sweet_sorghum_LUC_, Sweet_sorghum_pre_emissions],
                                                  [Switchgrass_emissions, Switchgrass_trans_emissions,
                                                   Switchgrass_LUC_, Switchgrass_pre_emissions],
                                                  [Miscanthus_emissions, Miscanthus_trans_emissions, Miscanthus_LUC_,
                                                   Miscanthus_pre_emissions]]
                land_base['biomass_cost'] = [0, 0, 0,
                                             [Sweet_sorghum_cost, Sweet_sorghum_trans_cost, Sweet_sorghum_pre_cost],
                                             [Switchgrass_cost, Switchgrass_trans_cost, Switchgrass_pre_cost],
                                             [Miscanthus_cost, Miscanthus_trans_cost, Miscanthus_pre_cost]]
                land_base['water'] = [0, 0, 0, water_sweet, water_Swit, water_mc]

                land_analysis['emissions_all'] = [0, 0, 0, Sweet_sorghum_emissions_all, Switchgrass_emissions_all,
                                                  Miscanthus_emissions_all]
                land_analysis['cost_all'] = [0, 0, 0, Sweet_sorghum_cost_all, Switchgrass_cost_all, Miscanthus_cost_all]
                if sum(land_base['biomass_dry']) == 0:

                    land_attribute_fail.append(item)
                    continue
                else:
                    land_attribute_three_biomass.append(land_base)
                    land_analysis_all.append(land_analysis)
                    continue

    return land_attribute_rice, land_attribute_Wheat_Corn, land_attribute_Forestry_residue, land_attribute_three_biomass, land_attribute_fail, land_analysis_all
