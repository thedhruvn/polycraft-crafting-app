import logging

LOG_LEVEL = logging.DEBUG
RAW_FILE_PATH = "./resources/"
FILTERED_FILENAME_ENDING = "_filtered.csv"
CONVERSIONS_CSV_NAME = "ConversionsRaw - Sheet1.csv"
CRAFT_CONVERSION_RANK_VALUE = 201.9

AVAILABLE_CONV = [
            # 'Compressed Block'
            #'Block ('
            'Bag'
            ,'Vial'
            ,'Flask'
            # ,'Sack'
            # ,'Beaker'
            # ,'Cartridge'
            # ,'Sack'
            #'Beaker'
            # Cartridge
            ,'Powder Keg'
            ,'Drum'
            ,'Canister'
            # Chemical Silo
            # Chemical Vat
            # Chemical Tank
            # Mold
            # Mold
            # MC Tool
            # Pogo Stick
            ,'Nugget'
            ,'Ingot'
        ]

BASE_ITEM_LIST_CSV = "NaturallyOccuringItemsRaw - Sheet1.csv"
FILTER_SCALE = 2.0

ADDITIONAL_BASE_ITEM_SEARCH = [
    'HOSE',
    'GASKET',
    'SOLE',
    'POLYISOPRENE PELLETS',
    'FLASK (NITROGEN)',
    'VIAL (SALT WATER)'
]