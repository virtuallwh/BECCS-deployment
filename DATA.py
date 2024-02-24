"""
Created on Fri Apr 30 13:55:41 2021

@author: linwh
"""


class AllData(object):
    def __init__(self):
        self.VSL = 11040000 * 0.15501 * 0.95
        self.power_trans_price = 47.46451613 / 1000 * 0.145
        self.power_plant_contributions = {
            'NAA': 9.8 / 100,
            'NEC': 10.4 / 100,
            'NC': 12.0 / 100,
            'YRD': 9.8 / 100,
            'MYR': 10.1 / 100,
            'SCB': 7.6 / 100,
            'PRD': 7.5 / 100,
        }

        self.Regional_division = {

            'NEC': {'E1': 123,
                    'E2': 128,
                    'N1': 41,
                    'N2': 47},

            'NC': {'E1': 113,
                   'E2': 119,
                   'N1': 33,
                   'N2': 40},

            'YRD': {'E1': 119,
                    'E2': 122,
                    'N1': 29.5,
                    'N2': 32.5},

            'MYR': {'E1': 111,
                    'E2': 115,
                    'N1': 27,
                    'N2': 32.5},

            'SCB': {'E1': 103,
                    'E2': 107,
                    'N1': 28,
                    'N2': 32},

            'PRD': {'E1': 112,
                    'E2': 114,
                    'N1': 22,
                    'N2': 24},
        }

        self.power_plant_hours_Province = {110000: 3939,
                                           120000: 4471,
                                           130000: 5090,
                                           140000: 4318,
                                           150000: 5124,
                                           210000: 4199,
                                           220000: 3590,
                                           230000: 3886,
                                           310000: 3571,
                                           320000: 4576,
                                           330000: 4201,
                                           340000: 5005,
                                           350000: 4507,
                                           360000: 5269,
                                           370000: 4707,
                                           410000: 3893,
                                           420000: 4527,
                                           430000: 4058,
                                           440000: 4096,
                                           450000: 3500,
                                           460000: 4549,
                                           500000: 3510,
                                           510000: 2713,
                                           520000: 3938,
                                           530000: 1850,
                                           540000: 304,
                                           610000: 4428,
                                           620000: 4178,
                                           630000: 3153,
                                           640000: 4865,
                                           650000: 4639,

                                           }

        self.Province_name_en = {'beijing': 110000,
                                 'tianjin': 120000,
                                 'hebei': 130000,
                                 'shanxi': 140000,
                                 'neimenggu': 150000,
                                 'liaoning': 210000,
                                 'jilin': 220000,
                                 'heilongjiang': 230000,
                                 'shanghai': 310000,
                                 'jiangsu': 320000,
                                 'zhejiang': 330000,
                                 'anhui': 340000,
                                 'fujian': 350000,
                                 'jiangxi': 360000,
                                 'shandong': 370000,
                                 'henan': 410000,
                                 'hubei': 420000,
                                 'hunan': 430000,
                                 'guangdong': 440000,
                                 'guangxi': 450000,
                                 'hainan': 460000,
                                 'chongqing': 500000,
                                 'sichuan': 510000,
                                 'guizhou': 520000,
                                 'yunnan': 530000,
                                 'tibet': 540000,
                                 'shaanxi': 610000,
                                 'gansu': 620000,
                                 'qinghai': 630000,
                                 'ningxia': 640000,
                                 'xinjiang': 650000,
                                 'taiwan': 710000,
                                 'hongkong': 810000,
                                 'macau': 820000,
                                 }
        self.Province_name_code_to_en = {
            110000: 'beijing',
            120000: 'tianjin',
            130000: 'hebei',
            140000: 'shanxi',
            150000: 'neimenggu',
            210000: 'liaoning',
            220000: 'jilin',
            230000: 'heilongjiang',
            310000: 'shanghai',
            320000: 'jiangsu',
            330000: 'zhejiang',
            340000: 'anhui',
            350000: 'fujian',
            360000: 'jiangxi',
            370000: 'shandong',
            410000: 'henan',
            420000: 'hubei',
            430000: 'hunan',
            440000: 'guangdong',
            450000: 'guangxi',
            460000: 'hainan',
            500000: 'chongqing',
            510000: 'sichuan',
            520000: 'guizhou',
            530000: 'yunnan',
            540000: 'tibet',
            610000: 'shaanxi',
            620000: 'gansu',
            630000: 'qinghai',
            640000: 'ningxia',
            650000: 'xinjiang',
            710000: 'taiwan',
            810000: 'hongkong',
            820000: 'macau',
        }

        self.Provinces_cluster = {110000: 'NorthChina',
                                  120000: 'NorthChina',
                                  130000: 'NorthChina',
                                  140000: 'NorthChina',
                                  150000: 'NorthChina',
                                  210000: 'NorthEast',
                                  220000: 'NorthEast',
                                  230000: 'NorthEast',
                                  310000: 'EastChina',
                                  320000: 'EastChina',
                                  330000: 'EastChina',
                                  340000: 'EastChina',
                                  350000: 'EastChina',
                                  360000: 'EastChina',
                                  370000: 'EastChina',
                                  410000: 'CentralChina',
                                  420000: 'CentralChina',
                                  430000: 'CentralChina',
                                  440000: 'SouthChina',
                                  450000: 'SouthChina',
                                  460000: 'SouthChina',
                                  500000: 'SouthWest',
                                  510000: 'SouthWest',
                                  520000: 'SouthWest',
                                  530000: 'SouthWest',
                                  540000: 'SouthWest',
                                  610000: 'NorthWest',
                                  620000: 'NorthWest',
                                  630000: 'NorthWest',
                                  640000: 'NorthWest',
                                  650000: 'NorthWest',
                                  'taiwan': 710000,
                                  'hongkong': 810000,
                                  'macau': 820000,
                                  }

        self.regional_electricity_grids = {110000: 'North',
                                           120000: 'North',
                                           130000: 'North',
                                           140000: 'North',
                                           150000: 'North',
                                           370000: 'North',

                                           210000: 'NorthEast',
                                           220000: 'NorthEast',
                                           230000: 'NorthEast',

                                           310000: 'East',
                                           320000: 'East',
                                           330000: 'East',
                                           340000: 'East',
                                           350000: 'East',

                                           360000: 'Central',
                                           410000: 'Central',
                                           420000: 'Central',
                                           430000: 'Central',
                                           500000: 'Central',
                                           510000: 'Central',

                                           440000: 'South',
                                           450000: 'South',
                                           460000: 'South',
                                           520000: 'South',
                                           530000: 'South',

                                           540000: 'SouthWest',
                                           610000: 'NorthWest',
                                           620000: 'NorthWest',
                                           630000: 'NorthWest',
                                           640000: 'NorthWest',
                                           650000: 'NorthWest',
                                           }

        self.coal_benchmark_price = {110000: 0.3598 * 0.145,
                                     120000: 0.3655 * 0.145,
                                     130000: 0.372 * 0.145,
                                     140000: 0.3320 * 0.145,
                                     150000: (0.2829 + 0.3035) / 2 * 0.145,
                                     210000: 0.3749 * 0.145,
                                     220000: 0.3731 * 0.145,
                                     230000: 0.374 * 0.145,
                                     310000: 0.4155 * 0.145,
                                     320000: 0.391 * 0.145,
                                     330000: 0.4153 * 0.145,
                                     340000: 0.3844 * 0.145,
                                     350000: 0.3932 * 0.145,
                                     360000: 0.4143 * 0.145,
                                     370000: 0.3949 * 0.145,
                                     410000: 0.3779 * 0.145,
                                     420000: 0.4161 * 0.145,
                                     430000: 0.45 * 0.145,
                                     440000: 0.453 * 0.145,
                                     450000: 0.4207 * 0.145,
                                     460000: 0.4298 * 0.145,
                                     500000: 0.3964 * 0.145,
                                     510000: 0.4012 * 0.145,
                                     520000: 0.3515 * 0.145,
                                     530000: 0.3358 * 0.145,
                                     540000: 0,
                                     610000: 0.3545 * 0.145,
                                     620000: 0.3078 * 0.145,
                                     630000: 0.3247 * 0.145,
                                     640000: 0.2595 * 0.145,
                                     650000: 0.25 * 0.145,
                                     710000: 0,
                                     810000: 0,
                                     820000: 0,
                                     }

        self.forestry_residues = {110000: 141 * 10000,
                                  120000: 35 * 10000,
                                  130000: 1541 * 10000,
                                  140000: 364 * 10000,
                                  150000: 679 * 10000,
                                  210000: 987 * 10000,
                                  220000: 489 * 10000,
                                  230000: 595 * 10000,
                                  310000: 19 * 10000,
                                  320000: 459 * 10000,
                                  330000: 1263 * 10000,
                                  340000: 1180 * 10000,
                                  350000: 2113 * 10000,
                                  360000: 1364 * 10000,
                                  370000: 1198 * 10000,
                                  410000: 898 * 10000,
                                  420000: 998 * 10000,
                                  430000: 1635 * 10000,
                                  440000: 1908 * 10000,
                                  450000: 3834 * 10000,
                                  460000: 652 * 10000,
                                  500000: 405 * 10000,
                                  510000: 1743 * 10000,
                                  520000: 702 * 10000,
                                  530000: 2607 * 10000,
                                  540000: 506 * 10000,
                                  610000: 938 * 10000,
                                  620000: 314 * 10000,
                                  630000: 132 * 10000,
                                  640000: 44 * 10000,
                                  650000: 540 * 10000,
                                  710000: 0,
                                  810000: 0,
                                  820000: 0,
                                  }

        self.IF_param_pm1 = {
            100: 1.5 / 10000000,
            500: 2.3 / 100000000,
            1000: 1.1 / 100000000,
            2000: 3.9 / 1000000000,
            'prec': -1.7 / 1000000000,
        }
        self.IF_param_pm3 = {
            100: 1.4 / 10000000,
            500: 1.7 / 100000000,
            1000: 6.4 / 1000000000,
            2000: 3.0 / 1000000000,
            'prec': -2.4 / 1000000000,
        }

        self.IF_region_share = {
            100: 53 / 100,
            500: 27 / 100,
            1000: 6 / 100,
            2000: 14 / 100,
        }

        self.BR = 20 / 24 / 60 / 60

        self.coal_fired_plant_PM25_reduce_rate = 56.2 / 100
        self.coal_fired_plant_PM25_emissions_rate = {
            'North': 0.26 * self.coal_fired_plant_PM25_reduce_rate,
            'NorthEast': 0.55 * self.coal_fired_plant_PM25_reduce_rate,
            'East': 0.16 * self.coal_fired_plant_PM25_reduce_rate,
            'Central': 0.34 * self.coal_fired_plant_PM25_reduce_rate,
            'South': 0.2 * self.coal_fired_plant_PM25_reduce_rate,
            'NorthWest': 0.27 * self.coal_fired_plant_PM25_reduce_rate,
        }

        self.BECCS_plant_PM25_emissions_rate = 0.033

        self.RR = {

            'COPD': 1.13,
            'Lung cancer': 1.14,
        }

        self.VSL_base = 7400000 * 1.26

        self.pcUSGDP = 7.63

        self.Residue_to_product_ratio = {
            'Rice': 0.9 + 0.27,
            'Wheat': 1.1,
            'Maize': 1.2 + 0.25,
            'Other cereals': 1.6,
            'beans': 1.6,
            'Other beans': 2,
            'Tubers': 0.5,
            'Peanut': 0.8 + 0.313,
            'Rapeseed': 1.5,
            'Sesame': 2.2,
            'Other oil crops': 2.7,
            'Cotton': 9.2,
            'Fiber crops': 2.1,
            'Sugar cane': 0.24 + 0.06,
            'Sugar beet': 0.08 + 0.1,
            'Tobacco': 1.6,

        }
        self.power_plant_hours = 7800

        self.biomass_growth = {
            'only_crop': 1,
            'Sweet_sorghum': 1,
            'Switchgrass': 12,
            'Miscanthus': 18
        }

        self.transport = 0.3285 * 0.16059 * 1.07

        self.R_CCS = 0.9

        self.water_power_plant = 4.3

        self.kwh_to_MJ = 3.6

        self.MJ_to_EJ = 1000000000000

        self.trans_Gt_to_t = 1000000000

        self.CO2_capacity_constr = {
            1: 745.80 * self.trans_Gt_to_t,
            2: 256.50 * self.trans_Gt_to_t,
            3: 233.30 * self.trans_Gt_to_t,
            4: 227.80 * self.trans_Gt_to_t,
            5: 197.10 * self.trans_Gt_to_t,
            6: 21.50 * self.trans_Gt_to_t,
            7: 77.60 * self.trans_Gt_to_t,
            8: 89.90 * self.trans_Gt_to_t,
            9: 85.00 * self.trans_Gt_to_t,
            10: 54.30 * self.trans_Gt_to_t,
            11: 52.80 * self.trans_Gt_to_t,
            12: 44.90 * self.trans_Gt_to_t,
            13: 178.00 * self.trans_Gt_to_t,
            14: 29.00 * self.trans_Gt_to_t,
            15: 16.10 * self.trans_Gt_to_t,
            16: 7.50 * self.trans_Gt_to_t,
            17: 337.51 * self.trans_Gt_to_t,
            18: 341.80 * self.trans_Gt_to_t
        }

        self.MEA = 52.2 * 1.21

        self.water_cost = {
            'Irrigation': 0.27 * 1.07,
            'industrial': 1.25 * 1.07
        }

        self.storage_Carbon_cost = {
            'onshore': 5 * 1.18 * 1.12,
            'offshore': 14 * 1.18 * 1.12,
        }

        self.trans_Carbon_cost = {
            'onshore': (5.4 + 1.5) / 2 / 180 * 1.18 * 1.12,
            'offshore': (6.0) / 500 * 1.18 * 1.12,
        }

        self.biomass_Carbon_con = {
            'Rice': 47.55 / 100,
            'Wheat_Corn': 47.55 / 100,
            'Forestry_residue': 50.5 / 100,
            'Sweet_sorghum': 47.55 / 100,
            'Switchgrass': 45.6 / 100,
            'Miscanthus': 47.91 / 100
        }

        self.coal_Carbon_con = 65 / 100

        self.biomass_LHV = {
            'Rice': 16.25 * 1000,
            'Wheat_Corn': 16.25 * 1000,
            'Forestry_residue': 16.5 * 1000,
            'Sweet_sorghum': 16.25 * 1000,
            'Switchgrass': 16.295 * 1000,
            'Miscanthus': 17.77 * 1000
        }

        self.coal_LHV = 25.350 * 1000

        self.Efficiencies = {'Subcritical': 34.3 / 100,
                             'Supercritical': 38.5 / 100,
                             'Ultra_supercritical': 43.3 / 100,
                             'Subcritical_fluidized_bed': 34.8 / 100,
                             'IGCC': 45.56 / 100}

        self.fuel_EF = {
            'Diesel': 2.7,
            'Natural_gas': 3.4,
        }

        self.fuel_EE = {
            'Diesel': 4.7,
            'Natural_gas': 4.7,
        }

        self.fuel_LHV = {
            'Diesel': 37.4,
            'Natural_gas': 47
        }

        self.fuel_price = {
            'Diesel': 6.5 * 0.16059 * 1.07,

            'Natural_gas': 3.807 * 0.145,

            'coal': 555.3 * 0.145

        }

        self.biomass_product_energy = {
            'Nitrogen': 55.4,
            'Phosphate': 10.5,
            'Potash': 7.3,
            'Lime': 1,
            'Herbicide': 292.9,

            'Miscanthus_Rhizome': 6,
            'Switchgrass_seed': 14.7,
            'Sweet_sorghum_seed': 40.25,
        }

        self.biomass_product_emissions = {
            'Nitrogen': 3.6,
            'Phosphate': 1.1,
            'Potash': 0.64,
            'Lime': 1.1,
            'Herbicide': 20.3,
            'Miscanthus_Rhizome': 0.01,
            'Switchgrass_seed': 14.7,
            'Sweet_sorghum_seed': 0.86,
            'Natural_gas': 3.4,
            'Diesel': 2.7
        }

        self.LUC_ILUC_emissions = {'ILUC': 183025 * 100,
                                   'grassland': 136300 * 100,
                                   'cropland': 3750 * 100,
                                   'marginal_land': 25 * 100,
                                   'forest': 573200 * 100,
                                   'wetland': 2186500 * 100
                                   }

        self.SP = {
            'Straw': 0 * 100,
            'Sweet_sorghum': 12.3 * 100,
            'Miscanthus': 75.1 * 100,
            'Switchgrass': 15.7 * 100,
            'Forestry_residue': 0 * 100
        }

        self.H = {
            'Straw': 4.4 * 100,
            'Sweet_sorghum': 4.4 * 100,
            'Miscanthus': 51.6 * 100,
            'Switchgrass': 32.6 * 100,
            'Forestry_residue': 0 * 100
        }

        self.biomass_param = {
            'Rice': {'r_ag': 1, 'r_hv': 1, 'r_rc': 0.313, 'r_rs1': 0.50, 'r_rs2': 0.1,
                     'moi_wet': 0.102, 'moi_dry': 0.102, 'Solid_rec': [1, 0, 1, 2, 1],
                     'process_E': [6.46, 211.5, 359.5, 345, 0, 0],
                     'biomass_cost': [0, 0, 0, 0],
                     'biomass_product': {'Nitrogen': 185.5 * 100, }
                     },
            'Wheat_Corn': {'r_ag': 1, 'r_hv': 1, 'r_rc': 0.313, 'r_rs1': 0.50, 'r_rs2': 0.1,
                           'moi_wet': 0.102, 'moi_dry': 0.102, 'Solid_rec': [1, 0, 1, 2, 1],
                           'process_E': [6.46, 211.5, 359.5, 345, 0, 0],
                           'biomass_cost': [0, 0, 0, 0],
                           'biomass_product': {'Nitrogen': 185.5 * 100, }
                           },
            'Forestry_residue': {'r_ag': 1, 'r_hv': 0.1, 'r_rc': 0.8, 'r_rs1': 0.3, 'r_rs2': 1,
                                 'moi_wet': 0.2, 'moi_dry': 0.15, 'Solid_rec': [0, 1, 0, 0, 1],
                                 'process_E': [0, 0, 0, 0, 3734, 828],
                                 'biomass_cost': [0, 0, 0, 0],
                                 'biomass_product': {}
                                 },
            'Sweet_sorghum': {'r_ag': 0.8, 'r_hv': 0.9, 'r_rc': 0.21, 'r_rs1': 1, 'r_rs2': 0,
                              'moi_wet': 0.102, 'moi_dry': 0.102, 'Solid_rec': [1, 0, 1, 2, 1],
                              'process_E': [6.46, 211.5, 359.5, 345, 0, 0],
                              'biomass_cost': [119.6 * 100 * 1.21, 79.07 * 100 * 1.21, 37.07 * 100 * 1.21,
                                               67.39 * 100 * 1.21],

                              'biomass_product': {'Nitrogen': 224 * 100,
                                                  'Phosphate': 34 * 100,
                                                  'Potash': 8.4 * 100,
                                                  'Sweet_sorghum_seed': 8.2 * 100,
                                                  'Herbicide': 0.23 * 100, }
                              },
            'Switchgrass': {'r_ag': 0.85, 'r_hv': 0.9, 'r_rc': 0.42, 'r_rs1': 1, 'r_rs2': 0,
                            'moi_wet': 0.12, 'moi_dry': 0.12, 'Solid_rec': [1, 0, 1, 2, 1],
                            'process_E': [135, 124, 46, 345, 0, 0],
                            'biomass_cost': [57.39 * 100 * 1.36, 4.16 * 100 * 1.36, 15.69 * 100 * 1.36,
                                             222.44 * 100 * 1.36],

                            'biomass_product': {'Nitrogen': 80 * 100,
                                                'Phosphate': 87 * 100,
                                                'Potash': 166 * 100,
                                                'Lime': 150 * 100,
                                                'Herbicide': 13.9 * 100,
                                                'Switchgrass_seed': 0.8 * 100, }
                            },
            'Miscanthus': {'r_ag': 0.85, 'r_hv': 0.9, 'r_rc': 0.29, 'r_rs1': 1, 'r_rs2': 0,
                           'moi_wet': 0.172, 'moi_dry': 0.15, 'Solid_rec': [1, 1, 1, 2, 1],
                           'process_E': [108, 124, 579, 345, 3734, 0],
                           'biomass_cost': [40.42 * 100 * 1.36, 1.27 * 100 * 1.36, 23.69 * 100 * 1.36,
                                            673.59 * 100 * 1.36],

                           'biomass_product': {'Nitrogen': 78 * 100,
                                               'Phosphate': 63 * 100,
                                               'Potash': 124 * 100,
                                               'Lime': 643 * 100,
                                               'Herbicide': 0.88 * 100,
                                               'Miscanthus_Rhizome': 52.6 * 100, }
                           }
        }


Data = AllData()
