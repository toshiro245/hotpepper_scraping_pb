from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import requests


import gspread
from oauth2client.service_account import ServiceAccountCredentials


# ユーザー設定項目/////////////////////////////////////////////
SPREADSHEET_KEY = '###'

SERVICE_ACCOUNT_FILE = '###'

# 開きたいワークシートのインデックスを指定 ※ワークシートのインデックスは0から始まる
WORK_SHEET_NUMBER = 1

# 出力CSVファイル名 ※.csvを付ける
FILE_NAME = 'result.csv'

# //////////////////////////////////////////////////////////



# スプレッドシートの設定, ワークシート取得
def spread_sheet_setting():
    SCOPES = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
    gs = gspread.authorize(credentials)
    work_sheet = gs.open_by_key(SPREADSHEET_KEY).get_worksheet(WORK_SHEET_NUMBER)
    return work_sheet


# スクレイピング
def scraping(url_list):


    # 取得したタグがNoneかどうかの判別
    def none_check(tag):
        if tag is None:
            value = None
        else:
            value = tag.text.strip()

        return value


    d_list = []
    for url in url_list:
        url_detail = url + 'coupon/'
        r = requests.get(url_detail, timeout=8)
        r.raise_for_status()
        sleep(4)

        soup = BeautifulSoup(r.content, 'lxml')

        company_name = soup.select_one('div.sprtHeaderInner > p.detailTitle').text

        # クーポン情報取得
        coupons = soup.select('table.couponTbl')
        for coupon in coupons:
            # クーポンURL
            coupon_url = coupon.select_one('div.pV10 > div > a.fs13').get('href')

            # メニュー名
            menu_name_tag = coupon.select_one('p.couponMenuName')
            menu_name = none_check(menu_name_tag)

            # 価格
            price_tag = coupon.select_one('p.oh > span.usingPointDel')
            price = none_check(price_tag)

            # 説明文
            description_tag = coupon.select_one('div.mT10 > div.oh > p.fgGray')
            description = none_check(description_tag)

            # 来店日条件
            condition_tag = coupon.select_one('dl.mT10 > dd:first-of-type')
            condition = none_check(condition_tag)

            # 対象スタイリスト
            stylist_tag = coupon.select_one('dl.mT10 > dd:nth-of-type(2)')
            stylist = none_check(stylist_tag)

            # その他条件
            others_tag = coupon.select_one('dl.mT10 > dd:nth-of-type(3)')
            others = none_check(others_tag)

            # 画像URL
            image_tag = coupon.select_one('div.couponImgWrap > img')
            if image_tag:
                image_url = image_tag.get('src')
            else:
                image_url = None
            
            # 施術カテゴリ
            category_tag = coupon.select_one('ul.couponMenuIcons')
            category = none_check(category_tag)

            d = {
                '店舗URL': url,
                '店舗名': company_name,
                'クーポンURL': coupon_url,
                'メニュー名': menu_name,
                '価格': price,
                '説明文': description,
                '来店日条件': condition,
                '対象スタイリスト': stylist,
                'その他条件': others,
                '画像URL': image_url,
                'クーポンorメニュー': 'クーポン',
                '施術カテゴリー': category,
            }
            d_list.append(d)


        # メニュー情報取得
        menues = soup.select('table.menuTbl > tbody > tr')
        for menu in menues:
            # クーポンURL
            coupon_url_tag = menu.select_one('div.pV10 > div > a.fs11')
            if coupon_url_tag:
                coupon_url = coupon_url_tag.get('href')
            else:
                coupon_url = 'URLなし'

            # メニュー名
            menu_name_tag = menu.select_one('p.couponMenuName')
            menu_name = none_check(menu_name_tag)

            # 価格
            price_tag = menu.select_one('p.oh > span.fs16')
            price = none_check(price_tag)

            # 説明文
            description_tag = menu.select_one('div.pT10 > p.mT10')
            description = none_check(description_tag)

            d = {
                '店舗URL': url,
                '店舗名': company_name,
                'クーポンURL': coupon_url,
                'メニュー名': menu_name,
                '価格': price,
                '説明文': description,
                '来店日条件': None,
                '対象スタイリスト': None,
                'その他条件': None,
                '画像URL': None,
                'クーポンorメニュー': 'メニュー',
                '施術カテゴリー': None,
            }
            d_list.append(d)


    
    return d_list 



# csvへ出力
def output_to_csv(result_list):
    df = pd.DataFrame(result_list)
    df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')



def main():
    # スプレッドシート設定
    worksheet = spread_sheet_setting()

    # urlリスト取得
    url_list = worksheet.col_values(1)[1:]

    # スクレイピング実行
    result = scraping(url_list)

    # CSVファイルへ出力
    output_to_csv(result)
    


# 実行
if __name__ == '__main__':
    main()