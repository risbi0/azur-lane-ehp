import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

df = pd.read_excel('data/eHP2.xlsm', sheet_name='125 V eHP', engine='openpyxl')
details = pd.read_excel('data/eHP2.xlsm', sheet_name='125 V', engine='openpyxl'
                        )
def get_hull(ship_name):
    return details.loc[details['Ship'] == ship_name]['Type'].iloc[0]

def main():
	new_df = df[['Ship', 'Armor', 'SORT']]
	new_df['hull'] = new_df['Ship'].apply(get_hull)
	new_df['SORT'] = new_df['SORT'].astype(np.int16)
	new_df.rename(columns={'Ship': 'name', 'Armor': 'armor', 'SORT': 'ehp'}, inplace=True)
	new_df.sort_values('ehp', inplace=True)
	new_df.reset_index(drop=True, inplace=True)
	new_df.to_csv('data/vg.csv')

if __name__ == '__main__':
    main()
