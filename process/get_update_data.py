import pandas as pd
from dotenv import load_dotenv
from process.in_and_out import get_input_data, get_offer_data_file
import os

load_dotenv()


def get_offer_price_and_stock_data():

    offer_data_file = get_offer_data_file()
    update_data_file = get_input_data()

    print('offer file: ', offer_data_file)
    print('update file: ', update_data_file)
    offer_data = pd.read_csv(offer_data_file, sep=';', encoding='UTF-8', low_memory=False)

    update_req_cols = ['Prefiks', 'Indeks', 'Cena sprzedaży netto', 'Stawka VAT', 'Stan magazynowy']

    update_data = pd.read_csv(
        update_data_file, sep=';', encoding='ISO 8859-2', low_memory=False, usecols=update_req_cols)
    update_data['sku'] = update_data['Prefiks'].fillna(value='') + update_data['Indeks'].fillna(value='')
    print('update data: ', len(update_data))
    print('offer data: ', len(offer_data))
    update_rel_cols = ['sku', 'Cena sprzedaży netto', 'Stawka VAT', 'Stan magazynowy']
    update_data = update_data[update_rel_cols]
    update_data.set_index('sku', inplace=True, drop=True)
    merge_df = offer_data.merge(update_data, how='left', on='sku')
    number_cols = ['stock', 'Stan magazynowy', 'Cena sprzedaży netto', 'price']
    for column in number_cols:
        merge_df[column] = merge_df[column].astype(str).str.replace(',', '.').astype(float)

    merge_df['VAT'] = merge_df['Stawka VAT'].str.replace('%', '').astype(float) / 100
    merge_df['delta_stock'] = merge_df['stock'] - merge_df['Stan magazynowy']
    price_modifier = float(os.environ['price_modifier_%'])/100
    merge_df['Cena sprzedaży brutto'] = merge_df['Cena sprzedaży netto']*(1 + merge_df['VAT'])*price_modifier
    merge_df['ratio_price'] = abs(merge_df['price'] - merge_df['Cena sprzedaży brutto']) / merge_df['price']
    threshold_ratio = float(os.environ['difference_tolerance_%']) / 100
    merge_df = merge_df.loc[(merge_df.delta_stock != 0.0) | (merge_df.ratio_price > threshold_ratio)]
    merge_df = merge_df.loc[~merge_df['check']]
    merge_df = merge_df.loc[~((merge_df['stock'] == 0.0) & (merge_df['Stan magazynowy'] == 0.0))]
    merge_df = merge_df.loc[~((merge_df['Stan magazynowy'] == 0.0) & (merge_df['publication'] == 'ENDED'))]

    merge_cols = ['offer_id', 'Cena sprzedaży brutto', 'Stan magazynowy']
    print('merge :', len(merge_df))

    return merge_df[merge_cols]


# if __name__ == "__main__":
#
#     price_df = get_offer_price_and_stock_data()
#
#     # print(price_df[['offer_id', 'Cena sprzedaży netto']])
