"""
Created on Fri Apr 30 13:55:41 2021

@author: linwh
"""

from DATA import Data


class Emissions(object):
    def __init__(self, Data):
        self.Data = Data

    def land_emissions(self, key_biomass_param, biomass_wet, biomass_dry, biomass_type, land_item):
        process_E = key_biomass_param['process_E']
        biomass_product = key_biomass_param['biomass_product']
        moi_wet = key_biomass_param['moi_wet']
        process_emissions = self.biomass_process(process_E, biomass_wet, biomass_dry, moi_wet)
        product_emissions = self.biomass_product(biomass_product, biomass_dry, area=1)
        har_emissions, pre_emissions = self.biomass_preparation_harvesting(biomass_type, biomass_dry, n=1)
        transport_emissions = self.biomass_transport(biomass_wet, biomass_dry)
        LUC_ = self.LUC_emissions(land_item, biomass_dry, biomass_type)
        final_emissions = process_emissions + product_emissions + har_emissions
        emissions_all = [process_emissions, product_emissions, har_emissions, pre_emissions, transport_emissions, LUC_]
        return final_emissions, transport_emissions, LUC_, pre_emissions, emissions_all

    def biomass_process(self, process_E, biomass_wet, biomass_dry, moi_wet):

        process_emissions = (process_E[0] * biomass_wet / self.Data.fuel_LHV['Diesel']) * self.Data.fuel_EF[
            'Diesel']
        biomass_wet = biomass_wet * 0.98
        for i in [1, 2, 3, 5]:
            energy_test = process_E[i] * biomass_wet

            process_emissions += (energy_test / self.Data.fuel_LHV['Natural_gas']) * 2.3 * self.Data.fuel_EF[
                'Natural_gas']

            biomass_wet = biomass_wet * 0.98

        return process_emissions

    def biomass_product(self, biomass_product, biomass_dry, area=1):

        key_list = list(biomass_product.keys())
        product_emissions = 0
        for key_item in key_list:
            emissions_test = biomass_product[key_item] * area * self.Data.biomass_product_emissions[key_item]
            product_emissions += emissions_test

        return product_emissions

    def biomass_preparation_harvesting(self, biomass_type, biomass_dry, n=1):

        har_emissions = (self.Data.H[biomass_type] * n) * self.Data.fuel_EF[
            'Diesel']
        pre_emissions = (self.Data.SP[biomass_type]) * self.Data.fuel_EF[
            'Diesel']

        return har_emissions, pre_emissions

    def LUC_emissions(self, land_item, biomass_dry, biomass_type):

        NPP = land_item['NPP'] * 0.0001 * 1000

        LUC_ = 0
        if land_item['LUC'] in [22, 23, 31, 32, 33, 46, 45, 61, 63, 65]:
            biomass_dry_CO2 = biomass_dry * self.Data.biomass_Carbon_con[biomass_type] * 44 / 12

            if land_item['LUC'] in [22]:
                LUC_ += self.Data.LUC_ILUC_emissions['forest']
            if land_item['LUC'] in [31, 32]:
                LUC_ += self.Data.LUC_ILUC_emissions['grassland']
            if land_item['LUC'] in [45, 46]:
                LUC_ += self.Data.LUC_ILUC_emissions['wetland']
            if land_item['LUC'] in [23, 33, 46, 45, 61, 63, 65]:
                LUC_ += self.Data.LUC_ILUC_emissions['marginal_land']
        return LUC_

    def biomass_transport(self, biomass_wet, biomass_dry):

        Energy_efficiency = 0.044

        transport_emissions = Energy_efficiency * biomass_wet * self.Data.fuel_EF['Diesel']

        return transport_emissions
