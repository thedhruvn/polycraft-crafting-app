import pandas as pd
import re
from util.exceptions import *
import util.constants as CONST

class Cleaner:

    @staticmethod
    def clean_raw_csv(in_csv):
        in_csv_name, in_csv_ext = in_csv.split(".")
        if in_csv_ext != "csv":
            return None

        dummydf = pd.read_csv(f"{CONST.RAW_FILE_PATH}{in_csv}")

        #get column headers:
        list_of_columns = dummydf.columns.tolist()

        # get the column headers we want
        all_r = re.compile(r"Input*|Output*|I\d|O\d")
        groupby_r = re.compile(r"Input*|Output*")
        sum_r = re.compile(r"I\d")
        selected_columns = list(filter(all_r.match, list_of_columns))
        groupby_columns = list(filter(groupby_r.match, list_of_columns))
        sum_columns = list(filter(sum_r.match, list_of_columns))

        dummydf = dummydf.fillna(0.0)

        idx = dummydf.groupby(groupby_columns)['I1'].transform(max) == dummydf['I1']

        filtered_data = dummydf[idx]

        #filtered_data = filtered_data[selected_columns]
        return filtered_data[selected_columns]

        # filtered_data.to_csv(f"{in_csv_name}_filtered.csv")

    @staticmethod
    def stage_filtered_csv(in_csv, process_type, modifier=0):
        filtered = Cleaner.clean_raw_csv(in_csv)
        if filtered is None:
            raise BadExtensionException(f"input is not csv: {in_csv}")

        filtered['rank_value'] = 0.0
        filtered['process'] = process_type
        for idx, row in filtered.iterrows():

            # get count of "Inputs"
            headers = [i for i in row.index]
            r = re.compile(r"I\d")
            input_ct = list(filter(r.match, headers))
            truth = [row[i] > 0 for i in input_ct]
            count = len(input_ct) # Count of Inputs
            rk = sum(truth) # Count of actually used inputs

            filtered.at[idx, 'rank_value'] = rk + count/10. + modifier

        in_csv_name = in_csv.split('.')[0]
        filtered.to_csv(f"{in_csv_name}{CONST.FILTERED_FILENAME_ENDING}")


    @staticmethod
    def craft_conversions(items):
        list_of_items = list(items)

        conversions = pd.read_csv(f'{CONST.RAW_FILE_PATH}{CONST.CONVERSIONS_CSV_NAME}')
        conversions['rank_value'] = CONST.CRAFT_CONVERSION_RANK_VALUE

        df = pd.DataFrame()
        df['Input 1'] = pd.Series()
        df['iType'] = pd.Series()
        for it in list_of_items:
            it = str(it)
            #Are there any substring matches to our "AVAILABLE CONV" list?
            if any(sub in it for sub in CONST.AVAILABLE_CONV):
                #If so, identify the matches (TODO: is there a better way to do this?)
                vals = [i for i, val in enumerate(sub in it for sub in CONST.AVAILABLE_CONV) if val]
                df = df.append({'Input 1': it, 'iType': CONST.AVAILABLE_CONV[int(vals[0])]}, ignore_index=True)

        # merge in the conversions table:
        temp = df.merge(conversions, how='left', left_on='iType', right_on='Input')

        #create the "output 1" column
        temp['Output 1'] = temp.apply(lambda x: x['Input 1'].replace(x['iType'], str(x['Output'])), axis=1)

        #filter down to useful commands
        temp = temp.rename(columns={'Output': 'oType', 'Type': 'process'})[['Input 1', 'I1', 'iType', 'Output 1',
                                                                           'O1', 'oType', 'process', 'rank_value']]

        # Get Secondary Matches
        temp2 = temp[['Output 1', 'oType']].drop_duplicates().rename(columns={'Output 1': 'Input 1', 'oType': 'iType'})
        temp2 = temp2.merge(conversions, how='left', left_on='iType', right_on='Input')

        temp2['Output 1'] = temp2.apply(lambda x: x['Input 1'].replace(str(x['iType']), str(x['Output'])), axis=1)

        temp2 = temp2.rename(columns={'Output': 'oType', 'Type': 'process'})[['Input 1', 'I1', 'iType', 'Output 1',
                                                                              'O1', 'oType', 'process', 'rank_value']]
        temp2 = temp2[temp2['Input 1'] != temp2['Output 1']]
        return pd.concat([temp, temp2]).drop_duplicates().fillna(0.0)

if __name__ == '__main__':
    Cleaner.stage_filtered_csv('DistillationColumnRaw - Sheet1.csv', 'distillation')
    Cleaner.stage_filtered_csv('SteamCrackerRaw - Sheet1.csv', 'steam crack')
    Cleaner.stage_filtered_csv('MeroxTreatmentRaw - Sheet1.csv', 'merox')
    Cleaner.stage_filtered_csv('ChemicalProcessorRaw - Sheet1.csv', 'chemical processor')
    Cleaner.stage_filtered_csv('CraftingRaw - Sheet1.csv', 'craft', 100)
    Cleaner.stage_filtered_csv('SmeltingRaw - Sheet1.csv', 'smelt', 100)
