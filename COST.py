"""
Created on Fri Apr 30 13:55:41 2021

@author: linwh
"""

from DATA import Data


class Cost(object):
    def __init__(self, Data):
        self.Data = Data

    def land_cost(self, key_biomass_param, biomass_wet, biomass_dry, biomass_type, water=0):
        process_E = key_biomass_param['process_E']
        biomass_cost = key_biomass_param['biomass_cost']
        moi_wet = key_biomass_param['moi_wet']
        water_cost = self.biomass_water(water)
        process_cost = self.biomass_process(process_E, biomass_wet, biomass_dry, moi_wet)
        product_cost = self.biomass_plant_cost(biomass_cost)
        har_cost, pre_cost = self.biomass_preparation_harvesting(biomass_type, biomass_dry, n=1)
        transport_cost = self.biomass_transport(biomass_wet, biomass_dry)
        final_cost = water_cost + process_cost + product_cost + har_cost
        cost_all = [water_cost, process_cost, product_cost, har_cost, pre_cost, transport_cost]
        return final_cost, transport_cost, pre_cost, cost_all

    def biomass_water(self, water):

        biomass_water_cost = water * Data.water_cost['Irrigation']
        return biomass_water_cost

    def biomass_process(self, process_E, biomass_wet, biomass_dry, moi_wet):

        process_cost = process_E[0] * biomass_wet / self.Data.fuel_LHV['Diesel'] * self.Data.fuel_price['Diesel']
        biomass_wet = biomass_wet * 0.98
        for i in [1, 2, 3, 5]:
            energy_test = process_E[i] * biomass_wet
            process_cost += energy_test / self.Data.fuel_LHV['Natural_gas'] * self.Data.fuel_price['Natural_gas']
            biomass_wet = biomass_wet * 0.98

        return process_cost

    def biomass_plant_cost(self, biomass_cost):

        return sum(biomass_cost)

    def biomass_preparation_harvesting(self, biomass_type, biomass_dry, n=1):

        har_cost = (self.Data.H[biomass_type] * n) * self.Data.fuel_price['Diesel']
        pre_cost = (self.Data.SP[biomass_type]) * self.Data.fuel_price['Diesel']
        return har_cost, pre_cost

    def biomass_transport(self, biomass_wet, biomass_dry):

        Energy_efficiency = 0.044
        transport_cost = Energy_efficiency * biomass_wet * self.Data.fuel_price['Diesel']
        return transport_cost

    def CO2_trans_injection_cost(self, CO2_capture_plant_total, distance, save_land_type):

        if save_land_type == 17 or save_land_type == 18:

            trans_cost_unit = (Data.trans_Carbon_cost['offshore'] + Data.trans_Carbon_cost['onshore']) / 2
            injection_cost_unit = Data.storage_Carbon_cost['offshore']
        else:
            trans_cost_unit = Data.trans_Carbon_cost['onshore']
            injection_cost_unit = Data.storage_Carbon_cost['onshore']
        trans_cost = distance * CO2_capture_plant_total * trans_cost_unit
        injection_cost = CO2_capture_plant_total * injection_cost_unit
        trans_injection_cost = trans_cost + injection_cost
        return trans_injection_cost


AllCost = Cost(Data)
