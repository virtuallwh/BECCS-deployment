# -*- coding: utf-8 -*-
"""
Created on Tue May 30 10:43:10 2023
Health-benefits estimation model
@author: linwh
"""
import json
from tqdm import tqdm
from model_util import creat_time, land_pre_selected, ele_emission_rate
from data_util import Data
import gc
path = ''
print(f'{creat_time()} begain data read')
data = json.load(open(path + "data/data_for_ele_pm25_HBE.json", 'rb'))
Mortality_json, ele_attribute, point_pop_pm25 = data['Mortality_json'], data['ele_attribute'], data['point_pop_pm25']
PRE_json, GDP_city_code_json, pop_city = data['PRE_json'], data['GDP_city_code_json'], data['pop_city']
ele_attribute_reconstruct = data['ele_attribute_reconstruct']
del data
gc.collect()

print(f'{creat_time()} end data read')

prec_list = ['pre_20201', 'pre_20202', 'pre_20203', 'pre_20204', 'pre_20205', 'pre_20206', 'pre_20207',
             'pre_20208', 'pre_20209', 'pre_202010', 'pre_202011', 'pre_202012']
mon_day_dict = {'pre_20201': 31, 'pre_20202': 28, 'pre_20203': 31, 'pre_20204': 30, 'pre_20205': 31,
                'pre_20206': 30, 'pre_20207': 31,
                'pre_20208': 31, 'pre_20209': 30, 'pre_202010': 31, 'pre_202011': 30, 'pre_202012': 31}

ele_attribute_reconstruct_test = []
for ele_item in tqdm(ele_attribute_reconstruct[100:101]):
    flag = True
    exce_list = []
    prec_init = {}
    select_land_PRE = PRE_json
    while flag:
        prec_init = {}
        k = 0
        prec_land_select = land_pre_selected(ele_item=ele_item, land_total=select_land_PRE, exce_list=exce_list,
                                             dist_low=0, dist_constr=200, flag='prec')
        prec_land = prec_land_select['use']
        for key_prec in prec_list:
            if prec_land[key_prec] != None:
                prec_init[key_prec] = prec_land[key_prec] / 10 / mon_day_dict[key_prec]
            else:
                k += 1
        if k == 0:
            flag = False
        else:
            print(f'{creat_time()} k={k}')
            exce_list.append(prec_land['pointid'])
            select_land_PRE = prec_land_select['unuse']

    ele_item['prec_init'] = prec_init
    select_ele_update = land_pre_selected(ele_item=ele_item, land_total=ele_attribute,
                                          dist_constr=0, flag=4)
    if len(select_ele_update) == 1:
        ele_item['plant'] = select_ele_update[0]['plant']

    pop_data_dict = {}
    select_land = land_pre_selected(ele_item=ele_item, land_total=point_pop_pm25,
                                    dist_low=1000, dist_constr=2000, flag='pop')
    select_land_2000 = select_land['use']
    ele_item['pop_2000'] = select_land['pop']
    pop_data_dict[2000] = select_land['pop']
    select_land = land_pre_selected(ele_item=ele_item, land_total=select_land['unuse'],
                                    dist_low=500, dist_constr=1000, flag='pop')
    select_land_1000 = select_land['use']
    ele_item['pop_1000'] = select_land['pop']
    pop_data_dict[1000] = select_land['pop']
    select_land = land_pre_selected(ele_item=ele_item, land_total=select_land['unuse'],
                                    dist_low=100, dist_constr=500, flag='pop')
    select_land_500 = select_land['use']
    ele_item['pop_500'] = select_land['pop']
    pop_data_dict[500] = select_land['pop']
    select_land = land_pre_selected(ele_item=ele_item, land_total=select_land['unuse'],
                                    dist_low=0, dist_constr=100, flag='pop')
    select_land_100 = select_land['use']
    ele_item['pop_100'] = select_land['pop']
    pop_data_dict[100] = select_land['pop']

    # 做IFs分区
    IFs_PM25_dict = {}
    IFs_PM25_total = 0
    prec_init = ele_item['prec_init']
    for key_pre in prec_init:
        # Population variable in millions of people.
        IFs_PM1 = (pop_data_dict[100] * Data.IF_param_pm1[100] + pop_data_dict[500] * Data.IF_param_pm1[500] +
                   pop_data_dict[
                       1000] * Data.IF_param_pm1[1000] + pop_data_dict[2000] * Data.IF_param_pm1[2000]) / 1000000 + \
                  prec_init[key_pre] * Data.IF_param_pm1['prec']
        IFs_PM3 = (pop_data_dict[100] * Data.IF_param_pm3[100] + pop_data_dict[500] * Data.IF_param_pm3[500] +
                   pop_data_dict[
                       1000] * Data.IF_param_pm3[1000] + pop_data_dict[2000] * Data.IF_param_pm3[2000]) / 1000000 + \
                  prec_init[key_pre] * Data.IF_param_pm3['prec']

        IFs_PM25 = (IFs_PM1 + IFs_PM3) / 2
        IFs_PM25_dict[key_pre] = IFs_PM25
        IFs_PM25_total += IFs_PM25
    ele_item['IFs_PM25_dict'] = IFs_PM25_dict

    ele_item['IFs_PM25'] = IFs_PM25_total / 12

    ele_item['IF_100_PM25'] = ele_item['IFs_PM25'] * Data.IF_region_share[100]
    ele_item['IF_500_PM25'] = ele_item['IFs_PM25'] * Data.IF_region_share[500]
    ele_item['IF_1000_PM25'] = ele_item['IFs_PM25'] * Data.IF_region_share[1000]
    ele_item['IF_2000_PM25'] = ele_item['IFs_PM25'] * Data.IF_region_share[2000]

    for key_ in [100, 500, 1000, 2000]:
        if pop_data_dict[key_] <= 0:
            ele_item[f'delta_pm25_{key_}_PM25'] = 0
            ele_item[f'delta_pm25_{key_}_SO'] = 0
            ele_item[f'delta_pm25_{key_}_NO3'] = 0
        else:
            # 原始污染
            PM25, SO, NO3 = ele_emission_rate(ele_item)  # 返回的单位是ug/s
            ele_item[f'delta_pm25_{key_}_PM25'] = ele_item[f'IF_{key_}_PM25'] * PM25 / (
                    pop_data_dict[key_] * Data.BR)

            ele_item[f'delta_pm25_{key_}_BECCS_PM25'] = ele_item[f'IF_{key_}_PM25'] * ele_item[
                'capacity'] * 1000 * Data.BECCS_plant_PM25_emissions_rate / (
                                                                ele_item[f'pop_{key_}'] * Data.BR) * 1000000 / 3600

    delta_Y_total_PM25 = 0
    HBE_total_PM25 = 0
    ele_item['HBE_BECCS_PM25'] = 0
    ele_item['delta_Y_BECCS_PM25'] = 0
    delta_Y_total_BECCS_PM25 = 0
    HBE_total_BECCS_PM25 = 0
    for select_land, key_ in zip([select_land_100, select_land_500, select_land_1000, select_land_2000],
                                 [100, 500, 1000, 2000]):

        delta_Y_test_PM25 = 0
        HBE_test_PM25 = 0
        delta_Y_test_BECCS_PM25 = 0
        HBE_test_BECCS_PM25 = 0
        for item in select_land:
            Mortality_select = Mortality_json[
                Data.Province_name_code_to_en[GDP_city_code_json[str(item['CityCode'])]['ProvinceID']]]
            sex_ratio = (Mortality_select['Sex ratio'] / 100) / (1 + Mortality_select['Sex ratio'] / 100)
            pop_Men = item['pop'] * sex_ratio
            pop_Women = item['pop'] * (1 - sex_ratio)
            pop_GDP_dus_select = GDP_city_code_json[str(item['CityCode'])]['pop_GDP_dus'] ** 0.5
            for key_RR in Data.RR:
                if key_RR == 'COPD':
                    RR = Data.RR['COPD']
                    multiple = 2
                    Mortality_Men = (Mortality_select['Men COPD'] + Mortality_select[
                        'Men Ischaemic heart disease']) / 100000
                    Mortality_Women = (Mortality_select['Women COPD'] + Mortality_select[
                        'Women Ischaemic heart disease']) / 100000
                else:
                    RR = Data.RR['Lung cancer']
                    multiple = 1
                    Mortality_Men = Mortality_select['Men Lung cancer'] / 100000
                    Mortality_Women = Mortality_select['Women Lung cancer'] / 100000

                def HBE_delta(ele_item, pollu):
                    RR_test_PM25 = RR ** (ele_item[f'delta_pm25_{key_}_{pollu}'] / 10)
                    PAF_PM25 = (RR_test_PM25 - 1) / RR_test_PM25
                    delta_Y_PM25 = (pop_Men * Mortality_Men * PAF_PM25 +
                                    pop_Women * Mortality_Women * PAF_PM25)
                    HBE_PM25 = Data.VSL_base * pop_GDP_dus_select * delta_Y_PM25
                    return HBE_PM25, delta_Y_PM25

                # PM25
                HBE_PM25, delta_Y_PM25 = HBE_delta(ele_item, 'PM25')
                delta_Y_total_PM25 += delta_Y_PM25
                delta_Y_test_PM25 += delta_Y_PM25
                HBE_test_PM25 += HBE_PM25
                HBE_total_PM25 += HBE_PM25
                # PM2.5 lost
                HBE_BECCS_PM25, delta_Y_BECCS_PM25 = HBE_delta(ele_item, 'BECCS_PM25')
                delta_Y_total_BECCS_PM25 += delta_Y_BECCS_PM25
                delta_Y_test_BECCS_PM25 += delta_Y_BECCS_PM25
                HBE_test_BECCS_PM25 += HBE_BECCS_PM25
                HBE_total_BECCS_PM25 += HBE_BECCS_PM25
        ele_item[f'HBE_' + str(key_) + '_PM25'] = HBE_test_PM25
        ele_item[f'delta_Y_' + str(key_) + '_PM25'] = delta_Y_test_PM25
        ele_item[f'HBE_' + str(key_) + '_BECCS_PM25'] = HBE_test_BECCS_PM25
        ele_item[f'delta_Y_' + str(key_) + '_BECCS_PM25'] = delta_Y_test_BECCS_PM25

    ele_item['HBE_100_3_PM25'] = ele_item['HBE_100_PM25'] * 3 + ele_item['HBE_500_PM25'] + ele_item['HBE_1000_PM25'] + \
                                 ele_item['HBE_2000_PM25']
    ele_item['HBE_PM25'] = HBE_total_PM25
    ele_item['delta_Y_PM25'] = delta_Y_total_PM25
    ele_item['HBE'] = ele_item['HBE_PM25'] + ele_item['HBE_SO'] + ele_item['HBE_NO3']
    ele_item['delta_Y'] = ele_item['delta_Y_PM25'] + ele_item['delta_Y_SO'] + ele_item['delta_Y_NO3']
    ele_item['HBE_100_3_BECCS_PM25'] = ele_item['HBE_100_BECCS_PM25'] * 3 + ele_item['HBE_500_BECCS_PM25'] + ele_item[
        'HBE_1000_BECCS_PM25'] + ele_item['HBE_2000_BECCS_PM25']
    ele_item['HBE_BECCS_PM25'] = HBE_total_BECCS_PM25
    ele_item['delta_Y_BECCS_PM25'] = delta_Y_total_BECCS_PM25
    ele_attribute_reconstruct_test.append(ele_item)
