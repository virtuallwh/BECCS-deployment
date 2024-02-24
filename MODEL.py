"""
Created on Tue Aug 10 13:11:09 2021
BPCM model
@author: linwh
"""
import sys
import os
import numpy as np
import pandas as pd
import traceback
import json
import gc
from tqdm import tqdm
import gurobipy as gp
from gurobipy import GRB
from model_util import distance_cal, coal_consumption, land_pre_selected, creat_time, ele_max_capture
from DATA import Data
from COST import AllCost
import multiprocessing
import math

module_path_string = ""
sys.path.append(module_path_string)


def create_all_vars(data_save, land_attribute_test, ele_cluster_attribute, year_n):
    from data_util import Data
    def harvest_rate_cal(biomass_item, year_n):
        year_base = Data.biomass_growth[biomass_item]
        rate_base = 0.9
        if biomass_item == 'Miscanthus':
            rate_base = 0.85
        remainder_num = year_n % year_base
        total_num = year_n // year_base
        if remainder_num == 1:
            harvest_rate = (year_base + rate_base - 2) * total_num + 0.21
        elif remainder_num == 2:
            harvest_rate = (year_base + rate_base - 2) * total_num + rate_base
        else:
            harvest_rate = (year_base + rate_base - 2) * total_num + remainder_num - 2 + rate_base
        return harvest_rate

    def land_preparation_time_calc(year_n, biomass_item):
        return math.ceil(year_n / Data.biomass_growth[biomass_item])

    biomass_total = ['Rice', 'Wheat_Corn', 'Forestry_residue', 'Sweet_sorghum', 'Switchgrass', 'Miscanthus']
    all_Vars = {}
    biomass_type = [0, 1, 2, 3, 4, 5]
    harvest_rate = year_n

    for land_key in land_attribute_test:
        try:
            land_item = land_attribute_test[land_key]

            if sum([land_item['biomass_dry'][item] for item in biomass_type]) == 0:
                continue
            for ele_item in ele_cluster_attribute:

                dist_land_ele = distance_cal([land_item['POINT_X'], land_item['POINT_Y']],
                                             [ele_item['lng'], ele_item['lat']])

                emissions = 0
                energy = 0
                water = 0
                water_cost = 0
                cost = 0
                land_preparation_cost = 0
                land_preparation_emissions = 0
                land_preparation_energy = 0
                LUC_emissions = 0
                biomass_CO2_capture = 0
                biomass_Replace_coal = 0
                biomass_dry = 0
                for x in biomass_type:

                    if x in [0, 1, 2]:

                        biomass_item = 'only_crop'
                        biomass_dry_now = land_item['biomass_dry'][x] * year_n
                        biomass_wet_now = land_item['biomass_wet'][x] * year_n
                    else:
                        if x == 3:
                            biomass_item = 'Sweet_sorghum'
                            harvest_rate = year_n
                            biomass_dry_now = land_item['biomass_dry'][x] * year_n
                            biomass_wet_now = land_item['biomass_wet'][x] * year_n

                            land_preparation_cost += year_n * land_item['pre_cost'][x]
                            land_preparation_emissions += year_n * land_item['pre_emissions'][x]
                            land_preparation_energy += year_n * land_item['pre_energy'][x]
                            LUC_emissions += land_item['LUC_'][x]

                        if x == 4:
                            biomass_item = 'Switchgrass'
                            harvest_rate = harvest_rate_cal(biomass_item, year_n)
                            land_preparation_time = land_preparation_time_calc(year_n, biomass_item)

                            land_preparation_cost += land_preparation_time * land_item['pre_cost'][x]
                            land_preparation_emissions += land_preparation_time * land_item['pre_emissions'][x]
                            land_preparation_energy += land_preparation_time * land_item['pre_energy'][x]
                            LUC_emissions += land_item['LUC_'][x]

                        if x == 5:
                            biomass_item = 'Miscanthus'
                            harvest_rate = harvest_rate_cal(biomass_item, year_n)
                            land_preparation_time = land_preparation_time_calc(year_n, biomass_item)

                            land_preparation_cost += land_preparation_time * land_item['pre_cost'][x]
                            land_preparation_emissions += land_preparation_time * land_item['pre_emissions'][x]
                            land_preparation_energy += land_preparation_time * land_item['pre_energy'][x]
                            LUC_emissions += land_item['LUC_'][x]

                        biomass_dry_now = land_item['biomass_dry'][x] * harvest_rate
                        biomass_wet_now = land_item['biomass_wet'][x] * harvest_rate
                    biomass_dry += biomass_dry_now
                    biomass_CO2_capture += biomass_dry_now * Data.biomass_Carbon_con[biomass_total[x]] * 44 / 12
                    biomass_Replace_coal += biomass_dry_now * Data.biomass_LHV[biomass_total[x]] / Data.coal_LHV

                    if land_item['biomass_emissions'][x] != 0:
                        emissions += (dist_land_ele * land_item['biomass_emissions'][x][1] +
                                      land_item['biomass_emissions'][x][0]) * year_n
                    if land_item['biomass_energy'][x] != 0:
                        energy += (dist_land_ele * land_item['biomass_energy'][x][1] + land_item['biomass_energy'][x][
                            0]) * year_n

                    if land_item['biomass_cost'][x] != 0:
                        cost += dist_land_ele * Data.transport * biomass_wet_now + land_item['biomass_cost'][x][
                            0] * year_n

                cost += land_preparation_cost

                emissions += land_preparation_emissions + LUC_emissions

                energy += land_preparation_energy

                water += sum([land_item['water'][x] for x in biomass_type]) * year_n

                water_cost += sum([land_item['water'][x] for x in biomass_type]) * year_n * Data.water_cost[
                    'Irrigation']

                all_Vars[(str(land_item['land_cluster_id']), str(ele_item['id']))] = [
                    [biomass_dry,
                     biomass_CO2_capture,
                     biomass_Replace_coal,
                     emissions / 1000,
                     energy,
                     cost,
                     water,
                     water_cost]]
        except:
            print(f"{creat_time()} final error: {traceback.format_exc()}")
    return all_Vars


def mip_test_(data_save, land_attribute_test, ele_cluster_attribute, save_land_capacity, CRF, CI, year_n=1):
    all_Vars = {}
    create_all_vars_res = create_all_vars(data_save, land_attribute_test, ele_cluster_attribute, year_n)
    all_Vars.update(create_all_vars_res)

    arcs, data = gp.multidict(all_Vars)

    model = gp.Model('test')
    Vars = model.addVars(list(arcs), vtype=GRB.BINARY, name="Vars")

    CO2_capture_biomass_total_list = []
    CO2_emissions_list = []
    CO2_capture_plant_total_list = []
    plant_cost_total_list = []
    biomass_dry_total_list = []

    trans_injection_cost_list = []
    Reduce_coal_list = []

    Replace_coal_list = []
    water_use_list = []
    water_cost_list = []
    total_CO2_before_list = []
    total_coal_after_list = []
    plant_investment_list = []
    HBE_list = []
    HBE_lost_list = []
    revenue_list = []
    for ele_item in ele_cluster_attribute:
        ele_id = str(ele_item['id'])
        plant_investment = (((1457 * 1.07 + 990 * 1.17 * CI) * CRF + 58.2 * 1.12) * 1000 + 6.6 * 1.12) * \
                           ele_item['capacity'] \
                           + ele_item['capacity'] * Data.water_power_plant * Data.water_cost['industrial'] * \
                           Data.power_plant_hours_Province[ele_item['ProvinceID']]
        plant_investment_list.append(plant_investment * year_n)

        HBE = ele_item['HBE_PM25']
        HBE_lost = ele_item['HBE_BECCS_PM25'] * year_n
        HBE_list.append(HBE)
        HBE_lost_list.append(HBE_lost)
        revenue = ele_item['revenue'] * year_n
        revenue_list.append(revenue)
        save_land_id = data_save['save_land_type'][0]
        biomass_dry, biomass_CO2_capture, biomass_Replace_coal, emissions, energy, cost, water, water_cost = np.array(
            data.select('*', ele_id)).T

        Vars_use = np.array(Vars.select('*', ele_id))

        biomass_dry_total = gp.quicksum(biomass_dry * Vars_use)
        biomass_dry_total_list.append(biomass_dry_total)

        CO2_capture = gp.quicksum(biomass_CO2_capture * Vars_use)

        Replace_coal = gp.quicksum(biomass_Replace_coal * Vars_use)
        Replace_coal_list.append(Replace_coal)

        ele_plant_cost = gp.quicksum(cost * Vars_use)

        CO2_emissions = gp.quicksum(emissions * Vars_use)
        CO2_emissions_list.append(CO2_emissions)

        water_use = gp.quicksum(water * Vars_use)
        water_use_list.append(water_use)
        water_cost = gp.quicksum(water_cost * Vars_use)
        water_cost_list.append(water_cost)

        total_coal_after = coal_consumption(TC=ele_item['capacity'],
                                            OH=Data.power_plant_hours_Province[ele_item['ProvinceID']]) * year_n
        total_coal_after_list.append(total_coal_after)

        total_coal_before = ele_item['ele_coal'] * year_n

        total_CO2_before_list.append(ele_item['ele_CO2'] * year_n)
        Reduce_coal = total_coal_before - (total_coal_after - Replace_coal)
        Reduce_coal_list.append(Reduce_coal)

        model.addConstr(total_coal_after >= Replace_coal, name='coal' + str(ele_id))

        CO2_capture_plant_total = ((total_coal_after - Replace_coal) * Data.coal_Carbon_con * 44 / 12 + CO2_capture) \
                                  * Data.R_CCS
        CO2_capture_biomass_plant_total = CO2_capture * Data.R_CCS

        trans_injection_cost = AllCost.CO2_trans_injection_cost(
            CO2_capture_plant_total=CO2_capture_plant_total,
            distance=data_save['dist'][0],
            save_land_type=save_land_id)

        CO2_capture_biomass_total_list.append(CO2_capture_biomass_plant_total)

        CO2_capture_plant_total_list.append(CO2_capture_plant_total)

        plant_cost_total_list.append(ele_plant_cost - Reduce_coal * Data.fuel_price['coal'])

        trans_injection_cost_list.append(trans_injection_cost)

        model.addConstr(CO2_capture_plant_total <= save_land_capacity[save_land_id], name='save_land_constr')

        model.addConstr((total_coal_after - Replace_coal + biomass_dry_total) <= biomass_dry_total / CI,
                        name='co_firing_constr_1')

    CO2_emissions_total = gp.quicksum(CO2_emissions_list)

    CO2_capture_biomass_total = gp.quicksum(CO2_capture_biomass_total_list)

    biomass_dry_total = gp.quicksum(biomass_dry_total_list)
    Reduce_coal_total = gp.quicksum(Reduce_coal_list)
    Replace_coal_total = gp.quicksum(Replace_coal_list)

    total_CO2_before_total = gp.quicksum(total_CO2_before_list)
    total_coal_after_total = gp.quicksum(total_coal_after_list)

    CO2_capture_total = gp.quicksum(CO2_capture_plant_total_list)

    target_CO2 = CO2_capture_biomass_total \
                 + total_CO2_before_total \
                 - (total_coal_after_total - Replace_coal_total) * Data.coal_Carbon_con * 44 / 12 * (1 - Data.R_CCS) \
                 - CO2_emissions_total

    water_cost_total = gp.quicksum(water_cost_list)

    water_use_total = gp.quicksum(water_use_list)

    plant_investment_total = sum(plant_investment_list)
    HBE_total = sum(HBE_list)
    HBE_lost_total = sum(HBE_lost_list)
    revenue_total = sum(revenue_list)

    plant_cost_total = CO2_capture_total * Data.MEA + plant_investment_total \
                       + (gp.quicksum(trans_injection_cost_list) + gp.quicksum(plant_cost_total_list)) \
                       + water_cost_total + HBE_lost_total \
                       - HBE_total - revenue_total

    res_data = {'biomass_dry_total': biomass_dry_total,
                'Reduce_coal_total': Reduce_coal_total,
                'Replace_coal_total': Replace_coal_total,
                'CO2_capture_total': CO2_capture_total,
                'CO2_capture_biomass_total': CO2_capture_biomass_total,
                'CO2_emissions_total': CO2_emissions_total,
                'target_CO2': target_CO2,
                'plant_cost_total': plant_cost_total,
                'water_cost_total': water_cost_total,
                'water_use_total': water_use_total,
                'plant_investment_total': plant_investment_total,
                'HBE_total': HBE_total,
                'HBE_lost_total': HBE_lost_total,
                'revenue_total': revenue_total,

                'Vars': Vars}
    return model, res_data


def main_solve(data_save, total_coal, land_attribute_test, ele_cluster_attribute, roun, ele_id, save_land_capacity, CRF,
               path_dir,
               year_n=1,
               CI=0.3):
    model, res_data = mip_test_(data_save=data_save, land_attribute_test=land_attribute_test,
                                ele_cluster_attribute=ele_cluster_attribute, save_land_capacity=save_land_capacity,
                                CRF=CRF, CI=CI, year_n=year_n)

    for land_key in tqdm(land_attribute_test):
        model.addConstr(gp.quicksum(res_data['Vars'].select(str(land_key), '*')) <= 1,
                        name='0-1' + str(land_key))

    model.setObjective(res_data['plant_cost_total'])

    model.Params.Threads = 6
    model.optimize()
    if model.status == GRB.OPTIMAL:
        Status_target = 0
    else:

        if ele_cluster_attribute[0]['dist_land_ele'] > 5000:
            best_res = {'ele_id': ele_id, 'flag_drop': True, 'Status_target': 1}
        else:

            best_res = {'ele_id': ele_id, 'flag_drop': False, 'dist_land_ele_new': 5001, 'Status_target': 1}
        res_name = 'best_res' + str(ele_id)
        out_file = open(path_dir + f"data/res/{res_name}.json", "w")
        json.dump(best_res, out_file)
        out_file.close()

        return res_name

    Vars_list = list(res_data['Vars'].keys())

    Vars_select_recreate = []
    count = 0
    for item in tqdm(Vars_list):
        if round(res_data['Vars'][item].x) == 1:
            Vars_select_recreate.append(item[0])
            count += 1

    biomass_dry_total = float(res_data['biomass_dry_total'].getValue())
    Replace_coal_total = float(res_data['Replace_coal_total'].getValue())
    Reduce_coal_total = float(res_data['Reduce_coal_total'].getValue())
    target_CO2 = float(res_data['target_CO2'].getValue())
    plant_cost_total = float(res_data['plant_cost_total'].getValue())
    CI_new = biomass_dry_total / (total_coal * year_n - Replace_coal_total + biomass_dry_total)

    plant_investment = res_data['plant_investment_total']
    HBE = res_data['HBE_total']
    HBE_lost = res_data['HBE_lost_total']
    revenue = res_data['revenue_total']

    dist_land_ele = 0
    for land_key in tqdm(Vars_select_recreate):
        land_item = land_attribute_test[int(land_key)]
        first_long_lat = [ele_cluster_attribute[0]['lng'], ele_cluster_attribute[0]['lat']]
        second_long_lat = [land_item['POINT_X'], land_item['POINT_Y']]
        dist_current = distance_cal(first_long_lat, second_long_lat)

        if dist_land_ele < dist_current:
            dist_land_ele = dist_current

    best_res = {'ele_id': ele_id,
                'Vars_select': Vars_select_recreate,
                'water_total': float(res_data['water_use_total'].getValue()),
                'water_power_plant': ele_cluster_attribute[0]['capacity'] * Data.water_power_plant *
                                     Data.power_plant_hours_Province[ele_cluster_attribute[0]['ProvinceID']] * year_n,
                'CO2_capture_total': float(res_data['CO2_capture_total'].getValue()),
                'CO2_capture_biomass_total': float(res_data['CO2_capture_biomass_total'].getValue()),
                'plant_cost_total': plant_cost_total,
                'plant_investment': plant_investment,
                'HBE': HBE,
                'HBE_lost': HBE_lost,
                'revenue': revenue,
                'unit_CO2_cost': (plant_cost_total - HBE_lost + HBE + revenue) / target_CO2,
                'unit_CO2_cost_HBE': (plant_cost_total + HBE) / target_CO2,
                'unit_CO2_cost_HBE_revenue': (plant_cost_total) / target_CO2,
                'plant_cost_no_ele_base': plant_cost_total - plant_investment + HBE + revenue,
                'CO2_emissions_total': float(res_data['CO2_emissions_total'].getValue()),
                'target_CO2': target_CO2,
                'biomass_dry_total': biomass_dry_total,
                'total_coal': total_coal * year_n,
                'Replace_coal_total': Replace_coal_total,
                'Reduce_coal_total': Reduce_coal_total,
                'CI': CI_new,
                'dist_land_ele_old': ele_cluster_attribute[0]['dist_land_ele'],
                'dist_land_ele_new': dist_land_ele,
                'Status_target': Status_target,
                'save_land_type': int(data_save['save_land_type'][0])}

    res_name = 'best_res' + str(ele_id)
    out_file = open(path_dir + f"data/res/{res_name}.json", "w")
    json.dump(best_res, out_file)
    out_file.close()

    return res_name


def del_land_ele(land_attribute_test, ele_cluster_attribute_, save_land_capacity, old_res, flag=0):
    delete_land_item = []
    delete_ele_item = []
    if flag == 0:
        for key_item in tqdm(old_res):
            best_res = old_res[key_item]

            save_land_capacity[best_res['save_land_type']] = save_land_capacity[best_res['save_land_type']] - best_res[
                'CO2_capture_total']

            delete_ele_item.append(int(key_item))

            for x in best_res['Vars_select']:
                delete_land_item.append(x)
    elif flag == 1:
        for ele_item in tqdm(old_res['ele_shut_down_select']):
            delete_ele_item.append(int(ele_item[1]))
        for key_item in old_res:
            try:
                ProvinceID = int(key_item)
                Vars_select = old_res[key_item]['Vars_select']
                save_land_capacity[old_res[key_item]['save_land_type']] = save_land_capacity[
                                                                              old_res[key_item]['save_land_type']] - \
                                                                          old_res[key_item][
                                                                              'CO2_capture_total']
                for x in Vars_select:
                    delete_land_item.append(x)
            except:
                pass

    ele_cluster_attribute_temporary = []
    for ele_item in ele_cluster_attribute_:
        if int(ele_item['id']) in delete_ele_item:
            continue
        else:
            ele_cluster_attribute_temporary.append(ele_item)

    land_attribute_test_temporary = {}

    for land_key in tqdm(land_attribute_test):
        item = land_attribute_test[land_key]
        if str(item['land_cluster_id']) in delete_land_item:
            pass
        else:
            land_attribute_test_temporary[land_key] = item

    land_attribute_test = land_attribute_test_temporary.copy()
    ele_cluster_attribute_ = ele_cluster_attribute_temporary.copy()
    return land_attribute_test, ele_cluster_attribute_, save_land_capacity


def main_def(sort_key, k_test, roun_all, pool_num, return_dict, roun_one_res_dict, roun_each_res_dict, ele_attribute_,
             land_attribute_test,
             save_land_capacity, year_n=10, CI=60.0, dist_select=200, time_select='_notaiwan'):
    path_dir = ''
    roun_one_res = {}
    ele_num = len(ele_attribute_)
    total_round = len(ele_attribute_)
    CRF = 0.07 * (1 + 0.07) ** 35 / ((1 + 0.07) ** 35 - 1) * ((1 + 0.07) ** 3)

    try:
        while ele_num > 0:
            roun = total_round - ele_num
            pool = multiprocessing.Pool(pool_num)
            results = []
            k = 0
            for i in range(len(ele_attribute_)):
                ele_cluster_attribute = [ele_attribute_[i]]
                ele_id = ele_cluster_attribute[0]['id']
                if roun_all == 0:
                    if ele_cluster_attribute[0]['dist_land_ele'] == None:
                        dist_select = 2000
                    else:
                        dist_select = 2000
                    ele_cluster_attribute[0]['dist_land_ele'] = dist_select
                    select_land = land_pre_selected(ele_item=ele_cluster_attribute[0], land_total=land_attribute_test,
                                                    dist_constr=dist_select)
                else:
                    if dist_select <= 5000:
                        if ele_cluster_attribute[0]['dist_land_ele'] <= dist_select:
                            dist_select = ele_cluster_attribute[0]['dist_land_ele'] + 50
                        else:
                            dist_select = ele_cluster_attribute[0]['dist_land_ele'] + 100
                        ele_cluster_attribute[0]['dist_land_ele'] = dist_select
                        select_land = land_pre_selected(ele_item=ele_cluster_attribute[0],
                                                        land_total=land_attribute_test,
                                                        dist_constr=dist_select)
                    else:
                        dist_select = ele_cluster_attribute[0]['dist_land_ele'] + 50
                        ele_cluster_attribute[0]['dist_land_ele'] = dist_select
                        select_land = land_attribute_test

                total_coal = coal_consumption(ele_cluster_attribute[0]['capacity'], OH=Data.power_plant_hours_Province[
                    ele_cluster_attribute[0]['ProvinceID']])
                ele_save_land = pd.DataFrame(ele_cluster_attribute[0]['save_land_select']).sort_values(by="dist")
                data_save = {'save_land_type': [], 'dist': []}

                ele_plant_origin_save_CO2 = ele_max_capture(total_coal) * year_n
                CO2 = ele_plant_origin_save_CO2

                for idx, line in tqdm(ele_save_land.iterrows()):

                    if CO2 <= save_land_capacity[line['save_land_type']]:
                        data_save['dist'].append(line['dist'])
                        data_save['save_land_type'].append(line['save_land_type'])
                    if len(data_save['save_land_type']) == 1:
                        break
                if len(data_save['save_land_type']) == 0:
                    continue
                result = pool.apply_async(func=main_solve,
                                          args=(data_save,
                                                total_coal,
                                                select_land,
                                                ele_cluster_attribute,
                                                roun_all,
                                                ele_id,
                                                save_land_capacity,
                                                CRF,
                                                path_dir,
                                                year_n,
                                                CI / 100))
                results.append(result)

            pool.close()
            pool.join()

            first_i = 0
            for i in tqdm(range(len(results))):
                result = results[i]
                if result.ready() and result.successful():
                    res = json.load(open(path_dir + f'data/res/{result.get()}.json', 'rb'))
                    roun_each_res_dict[res['ele_id']] = res
                    if roun_all == 0:
                        roun_one_res_dict[res['ele_id']] = res
                        roun_one_res[res['ele_id']] = res
                    try:
                        if res['Status_target'] == 0:
                            if first_i == 0:
                                best_res = res
                            else:
                                try:
                                    if best_res[sort_key] >= res[sort_key]:
                                        best_res = res
                                    else:
                                        pass
                                except BaseException as e:
                                    print(f'{creat_time()} error is {e}')

                            path = path_dir + f'data/res/{result.get()}.json'
                            if (os.path.exists(path)):
                                os.remove(path)
                            first_i += 1
                        else:
                            print(f"{creat_time()} plant {res['ele_id']} result is {res['Status_target']}")
                    except BaseException as e:

                        print(f'{creat_time()} error is {e}')
                else:
                    print('error')

            if roun_all == 0:
                out_file = open(
                    path_dir + f"data/roun_one_res_nocoalcost_nobiomass_tag_{time_select}_{year_n}_{k_test}.json",
                    "w")
                json.dump(roun_one_res, out_file)
                out_file.close()

            return_dict[best_res['ele_id']] = best_res
            break

    except BaseException as e:
        print(f"{creat_time()} final error: {traceback.format_exc()} and {e}")


if __name__ == '__main__':
    start_time = creat_time()
    from multiprocessing import Process
    from multiprocessing import Manager

    manager = Manager()
    path_dir = ''

    ele_attribute_ = json.load(open(path_dir + '/ele_attribute_reconstruct.json', 'rb'))
    land_attribute_test = {}
    for land_item in json.load(open(path_dir + '/land_attribute_cluster_tag_new.json', 'rb')):
        land_attribute_test[land_item['land_cluster_id']] = land_item
    save_land_capacity = Data.CO2_capacity_constr.copy()
    ele_cluster_attribute_current = ele_attribute_.copy()
    best_res_total = {}
    roun_one_res = {}
    Specify_constr = []
    ele_CO2 = 0
    res_select_tag = 0
    res_select = []
    CO2_total = 0
    CO2_capture_biomass_total = 0
    ele_num = len(ele_attribute_)
    total_round = len(ele_attribute_)
    len_old_ele_num = len(ele_attribute_)
    year_n = 35
    CI = 99
    pool_num = 2
    roun_all_num = 3
    dist_select = 1000
    roun_one_is = True
    time_select = '20240215'
    sort_key = 'unit_CO2_cost_HBE_revenue'
    results = []
    try:
        while ele_num > 0:
            roun_all = total_round - ele_num
            if len(ele_cluster_attribute_current) < 10:
                num = 1
            elif len(ele_cluster_attribute_current) < 50:
                num = 2
            elif len(ele_cluster_attribute_current) < 100:
                num = 3
            else:
                num = 4
            if roun_all == 0:
                num = roun_all_num
            interval = round(len(ele_cluster_attribute_current) / num)
            k_test = 1
            return_dict = manager.dict()
            roun_one_res_dict = manager.dict()
            roun_each_res_dict = manager.dict()
            if roun_all == 0 and roun_one_is:
                roun_one_res = {}
                roun_one_res_ = json.load(
                    open(
                        path_dir + 'data/roun_one_res.json',
                        'rb'))
                for key_item in roun_one_res_:
                    res_item = roun_one_res_[key_item]
                    roun_one_res[res_item['ele_id']] = res_item

            else:
                for i in range(num):
                    start = interval * i
                    if i < num - 1:
                        end = interval * (i + 1)
                    else:
                        end = len(ele_cluster_attribute_current)
                    ele_attribute_item = ele_cluster_attribute_current[start:end]
                    p = Process(name=f'{time_select}_{k_test}', target=main_def,
                                args=(sort_key, k_test, roun_all, pool_num, return_dict, roun_one_res_dict,
                                      roun_each_res_dict,
                                      ele_attribute_item, land_attribute_test, save_land_capacity, year_n, CI,
                                      dist_select, time_select))
                    results.append(p)
                    p.start()
                    k_test += 1

                for proc in results:
                    proc.join()

            roun_one_res_list = roun_one_res_dict.values()
            roun_each_res_list = roun_each_res_dict.values()
            ele_id_list = []
            Vars_select_list = []
            if roun_all == 0 and len(roun_one_res) == 0:

                roun_one_res_current = {}
                for roun_one_res_list_item in roun_one_res_list:
                    roun_one_res_current[roun_one_res_list_item['ele_id']] = roun_one_res_list_item
                roun_one_res = roun_one_res_current
            roun_each_res = {}
            roun_each_is = True
            if roun_all == 0 and roun_one_is:
                roun_each_is = False

            dist_land_ele_update = {}
            if len(roun_each_res_list) > 0 and roun_each_is:
                for roun_each_res_list_item in roun_each_res_list:

                    if len(roun_each_res_list_item) > 0 and roun_each_res_list_item.get('flag_drop') == None:
                        dist_land_ele_update[str(roun_each_res_list_item['ele_id'])] = roun_each_res_list_item[
                            'dist_land_ele_new']
                        roun_each_res[roun_each_res_list_item['ele_id']] = roun_each_res_list_item
                    elif len(roun_each_res_list_item) > 0 and roun_each_res_list_item.get('flag_drop') != None:
                        if roun_each_res_list_item['flag_drop'] == True:

                            ele_id_list.append(roun_each_res_list_item['ele_id'])
                            if roun_one_res.get(roun_each_res_list_item['ele_id']) != None:
                                del roun_one_res[roun_each_res_list_item['ele_id']]
                                gc.collect()
                        else:

                            dist_land_ele_update[str(roun_each_res_list_item['ele_id'])] = roun_each_res_list_item[
                                'dist_land_ele_new']
                            roun_each_res[roun_each_res_list_item['ele_id']] = roun_each_res_list_item

            for ele_item in ele_attribute_:
                if str(ele_item['id']) in dist_land_ele_update.keys():
                    ele_item['dist_land_ele'] = dist_land_ele_update[str(ele_item['id'])]

            for ele_key in roun_one_res:
                ele_item = roun_one_res[ele_key]
                if str(ele_item['ele_id']) in dist_land_ele_update.keys():
                    ele_item['dist_land_ele'] = dist_land_ele_update[str(ele_item['ele_id'])]
            print(f'{creat_time()} roun_one_res_dict内容为：return_dict内容为：{return_dict.values()}')

            if len(return_dict.values()) == 0 and roun_all != 0:
                if len(roun_one_res) == 0:
                    break
                else:

                    best_res = {sort_key: 10000}
                    for roun_one_res_item in roun_one_res:

                        if roun_one_res[roun_one_res_item]['ele_id'] not in [item['id'] for item in
                                                                             ele_cluster_attribute_current]:

                            if best_res[sort_key] >= roun_one_res[roun_one_res_item][sort_key]:
                                best_res = roun_one_res[roun_one_res_item].copy()
            elif len(return_dict.values()) == 0 and len(roun_one_res) != 0 and roun_all == 0 and roun_one_is:
                print(f'{creat_time()} roun_one_res长度1为{len(roun_one_res)}')
                best_res = {sort_key: 10000}
                for roun_one_res_item in roun_one_res:
                    res = roun_one_res[roun_one_res_item].copy()
                    if best_res[sort_key] >= res[sort_key]:
                        best_res = res.copy()
                    else:
                        pass

            else:
                best_res = json.loads(
                    pd.DataFrame(return_dict.values()).sort_values(by=sort_key, axis=0, ascending=True).to_json(
                        orient="records"))[0]


            def creat_new_compare_res(roun_each_res, roun_one_res, best_res, ele_cluster_attribute_, dist_select, CI,
                                      save_land_capacity, best_res_total):

                for roun_each_res_item in roun_each_res:
                    roun_one_res[roun_each_res_item] = roun_each_res[roun_each_res_item].copy()
                for roun_one_res_item in roun_one_res:
                    if roun_one_res[roun_one_res_item].get('flag_drop') == None:
                        try:
                            if best_res['target_CO2'] < 0:
                                best_res = {sort_key: 10000}
                            if best_res[sort_key] >= roun_one_res[roun_one_res_item][
                                sort_key] and roun_one_res[roun_one_res_item]['target_CO2'] > 0:

                                best_res = roun_one_res[roun_one_res_item].copy()
                            else:
                                pass
                        except:
                            print(f"{creat_time()} error: {traceback.format_exc()}")

                del roun_one_res[best_res['ele_id']]
                gc.collect()

                ele_cluster_attribute_current = []
                current_ele_id = []
                for roun_one_res_item in roun_one_res:
                    if str(roun_one_res_item) != str(best_res['ele_id']):

                        if roun_one_res[roun_one_res_item].get('flag_drop') == None:

                            if len(list(set(roun_one_res[roun_one_res_item]['Vars_select']).intersection(
                                    set(best_res['Vars_select'])))) > 0:
                                current_ele_id.append(str(roun_one_res_item))
                        else:
                            if roun_one_res[roun_one_res_item]['flag_drop'] == False:
                                current_ele_id.append(str(roun_one_res_item))

                for ele_cluster_attribute_item in ele_cluster_attribute_:
                    if str(ele_cluster_attribute_item['id']) in current_ele_id:
                        ele_cluster_attribute_current.append(ele_cluster_attribute_item)

                flag_res = True
                flag_solve = True
                try:
                    if abs(best_res['dist_land_ele_new'] - best_res['dist_land_ele_old']) < 1:
                        dist_select += 50
                        flag_res = False
                except:
                    if dist_select <= 5000:
                        dist_select += 50
                    else:
                        if CI == 99.5:
                            CI = 90
                        else:
                            CI -= 10
                        if CI <= 20:
                            flag_solve = False
                    flag_res = False

                if flag_res and flag_solve:
                    best_res_total[best_res['ele_id']] = best_res
                    out_file = open(path_dir + f"data/Current_optimal_result.json", "w")
                    json.dump(best_res_total, out_file)
                    out_file.close()

                    ele_CO2_current = best_res['target_CO2']
                    CO2_total_current = best_res['target_CO2']
                    CO2_capture_biomass_total_current = best_res['CO2_capture_biomass_total']

                    save_land_capacity[best_res['save_land_type']] = save_land_capacity[best_res['save_land_type']] - \
                                                                     best_res['CO2_capture_total']
                else:
                    ele_CO2_current = 0
                    CO2_total_current = 0
                    CO2_capture_biomass_total_current = 0
                return dist_select, CI, flag_res, flag_solve, best_res_total, best_res, roun_one_res, ele_cluster_attribute_current, ele_CO2_current, CO2_total_current, CO2_capture_biomass_total_current, save_land_capacity


            if len(best_res) == 0:
                break
            dist_select, CI, flag_res, flag_solve, best_res_total, best_res, roun_one_res, ele_cluster_attribute_current, ele_CO2_current, CO2_total_current, CO2_capture_biomass_total_current, save_land_capacity = creat_new_compare_res(
                roun_each_res,
                roun_one_res,
                best_res,
                ele_attribute_,
                dist_select,
                CI, save_land_capacity, best_res_total)
            if flag_res == False:
                ele_cluster_attribute_current = ele_attribute_.copy()
                continue
            if flag_solve == False:
                break
            roun_each_res = {}
            ele_CO2 += ele_CO2_current
            CO2_total += CO2_total_current
            CO2_capture_biomass_total += CO2_capture_biomass_total_current
            ele_id_list.append(best_res['ele_id'])
            Vars_select_list.extend(best_res['Vars_select'])

            flag = 0
            if len(ele_cluster_attribute_current) == 0 and len(roun_one_res) != 0:
                flag = 1

            while flag == 1:

                best_res = {sort_key: 100000}
                for roun_one_res_item in roun_one_res:

                    if roun_one_res[roun_one_res_item].get('flag_drop') == None:

                        if best_res[sort_key] >= roun_one_res[roun_one_res_item][sort_key]:

                            best_res = roun_one_res[roun_one_res_item]
                        else:
                            pass

                if len(best_res) == 1:
                    break
                dist_select, CI, flag_res, flag_solve, best_res_total, best_res, roun_one_res, ele_cluster_attribute_current, ele_CO2_current, CO2_total_current, CO2_capture_biomass_total_current, save_land_capacity = creat_new_compare_res(
                    roun_each_res,
                    roun_one_res,
                    best_res,
                    ele_attribute_,
                    dist_select,
                    CI, save_land_capacity, best_res_total)
                if flag_res and flag_solve:
                    ele_CO2 += ele_CO2_current
                    CO2_total += CO2_total_current
                    CO2_capture_biomass_total += CO2_capture_biomass_total_current
                    ele_id_list.append(best_res['ele_id'])
                    Vars_select_list.extend(best_res['Vars_select'])
                else:
                    flag = 0
                if len(ele_cluster_attribute_current) == 0:
                    flag = 1
                else:
                    flag = 0

            for item in range(len(ele_attribute_)):
                if ele_attribute_[item]['id'] in ele_id_list:
                    del ele_attribute_[item]

                    break
            if len(ele_cluster_attribute_current) == 0:
                ele_cluster_attribute_current = ele_attribute_.copy()

            if len_old_ele_num == len(ele_attribute_):
                continue
            else:
                len_old_ele_num = len(ele_attribute_)
            land_attribute_test_temporary = {}
            delete_item = []
            for x in Vars_select_list:
                delete_item.append(x)
            for land_key in tqdm(land_attribute_test):
                if str(land_key) in delete_item:
                    pass
                else:
                    land_attribute_test_temporary[land_key] = land_attribute_test[land_key]
            print(len(land_attribute_test_temporary))
            land_attribute_test = land_attribute_test_temporary.copy()
            del land_attribute_test_temporary
            gc.collect()
            ele_num -= len(ele_id_list)
            if len(land_attribute_test) == 0 or len(ele_attribute_) == 0:
                break
            out_file = open(
                path_dir + f"data/Current_roun_one_res.json", "w")
            json.dump(roun_one_res, out_file)
            out_file.close()
    except BaseException as e:
        print(f"{creat_time()} final error: {traceback.format_exc()}")
    out_file = open(path_dir + f"data/best_res_total.json", "w")
    json.dump(best_res_total, out_file)
    out_file.close()
