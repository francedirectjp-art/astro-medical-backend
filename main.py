from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# 47都道府県の座標データ
PREFECTURES = {
    '北海道札幌市': (43.0642, 141.3469),
    '青森県青森市': (40.8244, 140.7400),
    '岩手県盛岡市': (39.7036, 141.1527),
    '宮城県仙台市': (38.2682, 140.8694),
    '秋田県秋田市': (39.7186, 140.1024),
    '山形県山形市': (38.2404, 140.3633),
    '福島県福島市': (37.7608, 140.4747),
    '茨城県水戸市': (36.3418, 140.4468),
    '栃木県宇都宮市': (36.5658, 139.8836),
    '群馬県前橋市': (36.3911, 139.0608),
    '埼玉県さいたま市': (35.8617, 139.6455),
    '千葉県千葉市': (35.6074, 140.1065),
    '東京都新宿区': (35.6938, 139.7036),
    '神奈川県横浜市': (35.4478, 139.6425),
    '新潟県新潟市': (37.9161, 139.0364),
    '富山県富山市': (36.6959, 137.2139),
    '石川県金沢市': (36.5946, 136.6256),
    '福井県福井市': (36.0652, 136.2217),
    '山梨県甲府市': (35.6642, 138.5683),
    '長野県長野市': (36.6513, 138.1811),
    '岐阜県岐阜市': (35.3912, 136.7223),
    '静岡県静岡市': (34.9756, 138.3828),
    '愛知県名古屋市': (35.1815, 136.9066),
    '三重県津市': (34.7303, 136.5086),
    '滋賀県大津市': (35.0045, 135.8686),
    '京都府京都市': (35.0116, 135.7681),
    '大阪府大阪市': (34.6937, 135.5023),
    '兵庫県神戸市': (34.6901, 135.1956),
    '奈良県奈良市': (34.6851, 135.8048),
    '和歌山県和歌山市': (34.2261, 135.1675),
    '鳥取県鳥取市': (35.5014, 134.2378),
    '島根県松江市': (35.4723, 133.0505),
    '岡山県岡山市': (34.6617, 133.9341),
    '広島県広島市': (34.3853, 132.4553),
    '山口県山口市': (34.1858, 131.4706),
    '徳島県徳島市': (34.0658, 134.5594),
    '香川県高松市': (34.3401, 134.0431),
    '愛媛県松山市': (33.8416, 132.7658),
    '高知県高知市': (33.5597, 133.5311),
    '福岡県福岡市': (33.6064, 130.4181),
    '佐賀県佐賀市': (33.2494, 130.2989),
    '長崎県長崎市': (32.7503, 129.8779),
    '熊本県熊本市': (32.7898, 130.7417),
    '大分県大分市': (33.2382, 131.6126),
    '宮崎県宮崎市': (31.9077, 131.4202),
    '鹿児島県鹿児島市': (31.5966, 130.5571),
    '沖縄県那覇市': (26.2124, 127.6792)
}

def get_coordinates(birth_place):
    """出生地から座標を取得"""
    for place, coords in PREFECTURES.items():
        if birth_place in place or place in birth_place:
            return coords
    # デフォルトは東京
    return PREFECTURES['東京都新宿区']

def get_sign_japanese(sign_abbr):
    """星座の略称を日本語に変換"""
    signs = {
        'Ari': '牡羊座', 'Tau': '牡牛座', 'Gem': '双子座', 'Can': '蟹座',
        'Leo': '獅子座', 'Vir': '乙女座', 'Lib': '天秤座', 'Sco': '蠍座',
        'Sag': '射手座', 'Cap': '山羊座', 'Aqu': '水瓶座', 'Pis': '魚座'
    }
    return signs.get(sign_abbr, sign_abbr)

def degree_to_sign_and_degree(longitude):
    """経度を星座と度数に変換"""
    signs = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir', 'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']
    sign_index = int(longitude // 30)
    degree = longitude % 30
    return signs[sign_index], degree

def julian_day_from_date(year, month, day, hour, minute):
    """日付と時刻からユリウス日を計算"""
    time_decimal = hour + minute / 60.0
    return swe.julday(year, month, day, time_decimal)

def is_retrograde(planet_id, jd):
    """惑星が逆行しているかチェック"""
    try:
        # 現在の位置
        current_pos = swe.calc_ut(jd, planet_id)[0][3]
        # 1日後の位置
        next_pos = swe.calc_ut(jd + 1, planet_id)[0][3]
        # 経度の変化が負の場合は逆行
        return next_pos < current_pos
    except:
        return False

@app.route('/api/astrology/calculate', methods=['POST'])
def calculate_astrology():
    try:
        data = request.get_json()
        
        # 入力データの取得
        name = data.get('name', '')
        birth_date = data.get('birthDate', '')
        birth_time = data.get('birthTime', '12:00')
        birth_place = data.get('birthPlace', '東京都新宿区')
        
        print(f"計算開始: {name}, {birth_date}, {birth_time}, {birth_place}")
        
        # 日付の解析
        year, month, day = map(int, birth_date.split('-'))
        hour, minute = map(int, birth_time.split(':'))
        
        # 座標の取得
        latitude, longitude = get_coordinates(birth_place)
        print(f"座標: {latitude}, {longitude}")
        
        # ユリウス日の計算
        jd = julian_day_from_date(year, month, day, hour, minute)
        print(f"ユリウス日: {jd}")
        
        # Swiss Ephemerisの設定
        swe.set_ephe_path('')  # デフォルトの天体暦を使用
        
        # 惑星の計算
        planets = [
            (swe.SUN, '太陽', 'Sun'),
            (swe.MOON, '月', 'Moon'),
            (swe.MERCURY, '水星', 'Mercury'),
            (swe.VENUS, '金星', 'Venus'),
            (swe.MARS, '火星', 'Mars'),
            (swe.JUPITER, '木星', 'Jupiter'),
            (swe.SATURN, '土星', 'Saturn'),
            (swe.MEAN_NODE, 'ドラゴンヘッド', 'North Node')
        ]
        
        planets_data = []
        
        for planet_id, name_jp, name_en in planets:
            try:
                # 惑星の位置を計算
                result = swe.calc_ut(jd, planet_id)
                planet_longitude = result[0][0]
                
                # 星座と度数に変換
                sign, degree = degree_to_sign_and_degree(planet_longitude)
                
                # 逆行チェック
                retrograde = is_retrograde(planet_id, jd) if planet_id != swe.MEAN_NODE else False
                
                planets_data.append({
                    'name_jp': name_jp,
                    'name_en': name_en,
                    'sign': sign,
                    'sign_jp': get_sign_japanese(sign),
                    'degree': round(degree, 2),
                    'longitude': round(planet_longitude, 2),
                    'retrograde': retrograde
                })
                
                print(f"{name_jp}: {sign} {degree:.2f}度 (逆行: {retrograde})")
                
            except Exception as e:
                print(f"{name_jp}の計算エラー: {str(e)}")
                continue
        
        # アセンダントとミッドヘブンの計算
        try:
            houses = swe.houses(jd, latitude, longitude, b'P')  # Placidus house system
            asc_longitude = houses[1][0]  # アセンダント
            mc_longitude = houses[1][1]   # ミッドヘブン
            
            asc_sign, asc_degree = degree_to_sign_and_degree(asc_longitude)
            mc_sign, mc_degree = degree_to_sign_and_degree(mc_longitude)
            
            print(f"アセンダント: {asc_sign} {asc_degree:.2f}度")
            print(f"ミッドヘブン: {mc_sign} {mc_degree:.2f}度")
            
        except Exception as e:
            print(f"ハウス計算エラー: {str(e)}")
            # デフォルト値
            asc_longitude = 0
            mc_longitude = 90
            asc_sign, asc_degree = 'Ari', 0
            mc_sign, mc_degree = 'Can', 0
        
        # ミッドヘブンを惑星データに追加
        planets_data.append({
            'name_jp': 'ミッドヘブン',
            'name_en': 'Midheaven',
            'sign': mc_sign,
            'sign_jp': get_sign_japanese(mc_sign),
            'degree': round(mc_degree, 2),
            'longitude': round(mc_longitude, 2),
            'retrograde': False
        })
        
        ascendant = {
            'sign': asc_sign,
            'sign_jp': get_sign_japanese(asc_sign),
            'degree': round(asc_degree, 2),
            'longitude': round(asc_longitude, 2)
        }
        
        result = {
            'name': name,
            'birth_info': {
                'date': f"{year}年{month:02d}月{day:02d}日",
                'time': birth_time,
                'place': birth_place
            },
            'calculation_method': 'Swiss Ephemeris (High Precision)',
            'planets': planets_data,
            'ascendant': ascendant
        }
        
        print(f"計算完了: {len(planets_data)}個の天体")
        return jsonify(result)
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Swiss Ephemeris Astrology API'})
