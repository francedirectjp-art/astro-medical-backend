"""
Anti-Gravity 占星術計算モジュール
Swiss Ephemerisを使用した高精度天体計算
"""

import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import math

# Swiss Ephemerisのデータパスを設定
swe.set_ephe_path('swe_data')

# =============================================================================
# 定数定義
# =============================================================================

# 星座の定義
SIGNS = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir', 'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']
SIGNS_JP = {
    'Ari': '牡羊座', 'Tau': '牡牛座', 'Gem': '双子座', 'Can': '蟹座',
    'Leo': '獅子座', 'Vir': '乙女座', 'Lib': '天秤座', 'Sco': '蠍座',
    'Sag': '射手座', 'Cap': '山羊座', 'Aqu': '水瓶座', 'Pis': '魚座'
}
SIGNS_EN = {
    'Ari': 'Aries', 'Tau': 'Taurus', 'Gem': 'Gemini', 'Can': 'Cancer',
    'Leo': 'Leo', 'Vir': 'Virgo', 'Lib': 'Libra', 'Sco': 'Scorpio',
    'Sag': 'Sagittarius', 'Cap': 'Capricorn', 'Aqu': 'Aquarius', 'Pis': 'Pisces'
}

# 元素の定義
ELEMENTS = {
    'fire': ['Ari', 'Leo', 'Sag'],
    'earth': ['Tau', 'Vir', 'Cap'],
    'air': ['Gem', 'Lib', 'Aqu'],
    'water': ['Can', 'Sco', 'Pis']
}

# 区分（モダリティ）の定義
MODALITIES = {
    'cardinal': ['Ari', 'Can', 'Lib', 'Cap'],
    'fixed': ['Tau', 'Leo', 'Sco', 'Aqu'],
    'mutable': ['Gem', 'Vir', 'Sag', 'Pis']
}

# 惑星の定義
PLANETS = {
    'sun': {'id': swe.SUN, 'name_jp': '太陽', 'name_en': 'Sun'},
    'moon': {'id': swe.MOON, 'name_jp': '月', 'name_en': 'Moon'},
    'mercury': {'id': swe.MERCURY, 'name_jp': '水星', 'name_en': 'Mercury'},
    'venus': {'id': swe.VENUS, 'name_jp': '金星', 'name_en': 'Venus'},
    'mars': {'id': swe.MARS, 'name_jp': '火星', 'name_en': 'Mars'},
    'jupiter': {'id': swe.JUPITER, 'name_jp': '木星', 'name_en': 'Jupiter'},
    'saturn': {'id': swe.SATURN, 'name_jp': '土星', 'name_en': 'Saturn'},
    'uranus': {'id': swe.URANUS, 'name_jp': '天王星', 'name_en': 'Uranus'},
    'neptune': {'id': swe.NEPTUNE, 'name_jp': '海王星', 'name_en': 'Neptune'},
    'pluto': {'id': swe.PLUTO, 'name_jp': '冥王星', 'name_en': 'Pluto'},
    'chiron': {'id': swe.CHIRON, 'name_jp': 'カイロン', 'name_en': 'Chiron'},
    'north_node': {'id': swe.MEAN_NODE, 'name_jp': 'ドラゴンヘッド', 'name_en': 'North Node'},
}

# アスペクトの定義
ASPECTS = {
    'conjunction': {'degree': 0, 'orb': 8, 'name_jp': '合', 'symbol': '☌'},
    'opposition': {'degree': 180, 'orb': 8, 'name_jp': '衝', 'symbol': '☍'},
    'trine': {'degree': 120, 'orb': 8, 'name_jp': '三分', 'symbol': '△'},
    'square': {'degree': 90, 'orb': 8, 'name_jp': '矩', 'symbol': '□'},
    'sextile': {'degree': 60, 'orb': 6, 'name_jp': '六分', 'symbol': '⚹'},
}

# 47都道府県の座標データ
PREFECTURES = {
    '北海道札幌市': (43.0642, 141.3469, 9),
    '青森県青森市': (40.8244, 140.7400, 9),
    '岩手県盛岡市': (39.7036, 141.1527, 9),
    '宮城県仙台市': (38.2682, 140.8694, 9),
    '秋田県秋田市': (39.7186, 140.1024, 9),
    '山形県山形市': (38.2404, 140.3633, 9),
    '福島県福島市': (37.7608, 140.4747, 9),
    '茨城県水戸市': (36.3418, 140.4468, 9),
    '栃木県宇都宮市': (36.5658, 139.8836, 9),
    '群馬県前橋市': (36.3911, 139.0608, 9),
    '埼玉県さいたま市': (35.8617, 139.6455, 9),
    '千葉県千葉市': (35.6074, 140.1065, 9),
    '東京都': (35.6762, 139.6503, 9),
    '東京都新宿区': (35.6938, 139.7036, 9),
    '神奈川県横浜市': (35.4478, 139.6425, 9),
    '新潟県新潟市': (37.9161, 139.0364, 9),
    '富山県富山市': (36.6959, 137.2139, 9),
    '石川県金沢市': (36.5946, 136.6256, 9),
    '福井県福井市': (36.0652, 136.2217, 9),
    '山梨県甲府市': (35.6642, 138.5683, 9),
    '長野県長野市': (36.6513, 138.1811, 9),
    '岐阜県岐阜市': (35.3912, 136.7223, 9),
    '静岡県静岡市': (34.9756, 138.3828, 9),
    '愛知県名古屋市': (35.1815, 136.9066, 9),
    '三重県津市': (34.7303, 136.5086, 9),
    '滋賀県大津市': (35.0045, 135.8686, 9),
    '京都府京都市': (35.0116, 135.7681, 9),
    '大阪府大阪市': (34.6937, 135.5023, 9),
    '兵庫県神戸市': (34.6901, 135.1956, 9),
    '奈良県奈良市': (34.6851, 135.8048, 9),
    '和歌山県和歌山市': (34.2261, 135.1675, 9),
    '鳥取県鳥取市': (35.5014, 134.2378, 9),
    '島根県松江市': (35.4723, 133.0505, 9),
    '岡山県岡山市': (34.6617, 133.9341, 9),
    '広島県広島市': (34.3853, 132.4553, 9),
    '山口県山口市': (34.1858, 131.4706, 9),
    '徳島県徳島市': (34.0658, 134.5594, 9),
    '香川県高松市': (34.3401, 134.0431, 9),
    '愛媛県松山市': (33.8416, 132.7658, 9),
    '高知県高知市': (33.5597, 133.5311, 9),
    '福岡県福岡市': (33.6064, 130.4181, 9),
    '佐賀県佐賀市': (33.2494, 130.2989, 9),
    '長崎県長崎市': (32.7503, 129.8779, 9),
    '熊本県熊本市': (32.7898, 130.7417, 9),
    '大分県大分市': (33.2382, 131.6126, 9),
    '宮崎県宮崎市': (31.9077, 131.4202, 9),
    '鹿児島県鹿児島市': (31.5966, 130.5571, 9),
    '沖縄県那覇市': (26.2124, 127.6792, 9),
}

# サビアンシンボル（完全版は別ファイルで管理）
# ここでは構造のみ定義
SABIAN_SYMBOLS = {}  # sabian_symbols.json から読み込む

# =============================================================================
# ユーティリティ関数
# =============================================================================

def get_coordinates(birth_place: str) -> Tuple[float, float, int]:
    """出生地から座標とタイムゾーンを取得"""
    for place, data in PREFECTURES.items():
        if birth_place in place or place in birth_place:
            return data
    # デフォルトは東京
    return PREFECTURES['東京都']


def julian_day_from_datetime(dt: datetime, timezone_offset: int = 9) -> float:
    """datetimeからユリウス日を計算（UTCに変換）"""
    utc_dt = dt - timedelta(hours=timezone_offset)
    time_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, time_decimal)


def longitude_to_sign(longitude: float) -> Tuple[str, float]:
    """経度を星座と度数に変換"""
    sign_index = int(longitude // 30)
    degree = longitude % 30
    return SIGNS[sign_index], degree


def get_sabian_degree(degree: float) -> int:
    """サビアンシンボル用の度数を取得（切り上げ）"""
    return math.ceil(degree) if degree > 0 else 1


def normalize_degree(degree: float) -> float:
    """度数を0-360の範囲に正規化"""
    while degree < 0:
        degree += 360
    while degree >= 360:
        degree -= 360
    return degree


def calculate_aspect_angle(long1: float, long2: float) -> float:
    """2つの経度間の角度を計算"""
    diff = abs(long1 - long2)
    if diff > 180:
        diff = 360 - diff
    return diff


# =============================================================================
# 天体計算クラス
# =============================================================================

class AstroCalculator:
    """占星術計算を行うメインクラス"""
    
    def __init__(self, birth_datetime: datetime, birth_place: str, name: str = ""):
        """
        初期化
        
        Args:
            birth_datetime: 出生日時
            birth_place: 出生地
            name: 名前（オプション）
        """
        self.name = name
        self.birth_datetime = birth_datetime
        self.birth_place = birth_place
        
        # 座標とタイムゾーンを取得
        self.latitude, self.longitude, self.timezone = get_coordinates(birth_place)
        
        # ユリウス日を計算
        self.julian_day = julian_day_from_datetime(birth_datetime, self.timezone)
        
        # 計算結果を格納
        self.planets_data: Dict[str, Dict] = {}
        self.houses_data: Dict[int, Dict] = {}
        self.angles_data: Dict[str, Dict] = {}
        self.aspects_data: List[Dict] = []
        
        # 分析結果
        self.element_balance: Dict[str, int] = {}
        self.modality_balance: Dict[str, int] = {}
    
    def calculate_all(self) -> Dict[str, Any]:
        """全ての計算を実行"""
        self._calculate_planets()
        self._calculate_houses()
        self._calculate_aspects()
        self._analyze_element_balance()
        self._analyze_modality_balance()
        
        return self.get_full_chart()
    
    def _calculate_planets(self):
        """全天体の位置を計算"""
        for key, planet_info in PLANETS.items():
            try:
                result = swe.calc_ut(self.julian_day, planet_info['id'])
                longitude = result[0][0]
                latitude = result[0][1]
                speed = result[0][3]
                
                sign, degree = longitude_to_sign(longitude)
                sabian_degree = get_sabian_degree(degree)
                
                # 逆行判定（速度が負なら逆行）
                retrograde = speed < 0 if key not in ['sun', 'moon', 'north_node'] else False
                
                self.planets_data[key] = {
                    'name_jp': planet_info['name_jp'],
                    'name_en': planet_info['name_en'],
                    'longitude': round(longitude, 4),
                    'latitude': round(latitude, 4),
                    'sign': sign,
                    'sign_jp': SIGNS_JP[sign],
                    'sign_en': SIGNS_EN[sign],
                    'degree': round(degree, 4),
                    'degree_formatted': f"{int(degree)}°{int((degree % 1) * 60):02d}'",
                    'sabian_degree': sabian_degree,
                    'retrograde': retrograde,
                    'speed': round(speed, 4),
                }
                
            except Exception as e:
                print(f"Error calculating {key}: {e}")
                continue
        
        # サウスノード（ドラゴンテイル）を計算
        if 'north_node' in self.planets_data:
            nn_long = self.planets_data['north_node']['longitude']
            sn_long = normalize_degree(nn_long + 180)
            sign, degree = longitude_to_sign(sn_long)
            
            self.planets_data['south_node'] = {
                'name_jp': 'ドラゴンテイル',
                'name_en': 'South Node',
                'longitude': round(sn_long, 4),
                'latitude': 0,
                'sign': sign,
                'sign_jp': SIGNS_JP[sign],
                'sign_en': SIGNS_EN[sign],
                'degree': round(degree, 4),
                'degree_formatted': f"{int(degree)}°{int((degree % 1) * 60):02d}'",
                'sabian_degree': get_sabian_degree(degree),
                'retrograde': False,
                'speed': 0,
            }
    
    def _calculate_houses(self):
        """ハウスとアングルを計算"""
        try:
            # Placidusハウスシステムを使用
            houses, ascmc = swe.houses(self.julian_day, self.latitude, self.longitude, b'P')
            
            # 12ハウスのカスプを計算
            for i in range(12):
                house_num = i + 1
                cusp_long = houses[i]
                sign, degree = longitude_to_sign(cusp_long)
                
                self.houses_data[house_num] = {
                    'cusp_longitude': round(cusp_long, 4),
                    'sign': sign,
                    'sign_jp': SIGNS_JP[sign],
                    'degree': round(degree, 4),
                    'sabian_degree': get_sabian_degree(degree),
                }
            
            # アングルを計算
            angles = {
                'asc': {'long': ascmc[0], 'name_jp': 'アセンダント', 'name_en': 'Ascendant'},
                'mc': {'long': ascmc[1], 'name_jp': 'ミッドヘブン', 'name_en': 'Midheaven'},
                'ic': {'long': normalize_degree(ascmc[1] + 180), 'name_jp': 'イムムコエリ', 'name_en': 'Imum Coeli'},
                'dc': {'long': normalize_degree(ascmc[0] + 180), 'name_jp': 'ディセンダント', 'name_en': 'Descendant'},
            }
            
            for key, angle_info in angles.items():
                sign, degree = longitude_to_sign(angle_info['long'])
                self.angles_data[key] = {
                    'name_jp': angle_info['name_jp'],
                    'name_en': angle_info['name_en'],
                    'longitude': round(angle_info['long'], 4),
                    'sign': sign,
                    'sign_jp': SIGNS_JP[sign],
                    'sign_en': SIGNS_EN[sign],
                    'degree': round(degree, 4),
                    'degree_formatted': f"{int(degree)}°{int((degree % 1) * 60):02d}'",
                    'sabian_degree': get_sabian_degree(degree),
                }
            
            # 各天体がどのハウスにあるか計算
            self._assign_planets_to_houses()
            
        except Exception as e:
            print(f"Error calculating houses: {e}")
    
    def _assign_planets_to_houses(self):
        """各天体のハウス配置を計算"""
        house_cusps = [self.houses_data[i]['cusp_longitude'] for i in range(1, 13)]
        
        for planet_key, planet_data in self.planets_data.items():
            planet_long = planet_data['longitude']
            house = 12  # デフォルト
            
            for i in range(12):
                cusp_current = house_cusps[i]
                cusp_next = house_cusps[(i + 1) % 12]
                
                # 境界をまたぐ場合（例：350度〜10度）
                if cusp_next < cusp_current:
                    if planet_long >= cusp_current or planet_long < cusp_next:
                        house = i + 1
                        break
                else:
                    if cusp_current <= planet_long < cusp_next:
                        house = i + 1
                        break
            
            self.planets_data[planet_key]['house'] = house
    
    def _calculate_aspects(self):
        """天体間のアスペクトを計算"""
        planet_keys = list(self.planets_data.keys())
        
        for i, key1 in enumerate(planet_keys):
            for key2 in planet_keys[i+1:]:
                long1 = self.planets_data[key1]['longitude']
                long2 = self.planets_data[key2]['longitude']
                
                angle = calculate_aspect_angle(long1, long2)
                
                for aspect_name, aspect_info in ASPECTS.items():
                    diff = abs(angle - aspect_info['degree'])
                    if diff <= aspect_info['orb']:
                        self.aspects_data.append({
                            'planet1': key1,
                            'planet1_jp': self.planets_data[key1]['name_jp'],
                            'planet2': key2,
                            'planet2_jp': self.planets_data[key2]['name_jp'],
                            'aspect': aspect_name,
                            'aspect_jp': aspect_info['name_jp'],
                            'symbol': aspect_info['symbol'],
                            'angle': round(angle, 2),
                            'orb': round(diff, 2),
                            'exact_degree': aspect_info['degree'],
                        })
                        break
    
    def _analyze_element_balance(self):
        """4元素のバランスを分析"""
        counts = {'fire': 0, 'earth': 0, 'air': 0, 'water': 0}
        
        # 主要10天体のみカウント
        main_planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 
                       'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
        
        for planet_key in main_planets:
            if planet_key in self.planets_data:
                sign = self.planets_data[planet_key]['sign']
                for element, signs in ELEMENTS.items():
                    if sign in signs:
                        counts[element] += 1
                        break
        
        self.element_balance = counts
        
        # 優位と不足を判定
        max_element = max(counts, key=counts.get)
        min_element = min(counts, key=counts.get)
        
        self.element_analysis = {
            'counts': counts,
            'dominant': max_element,
            'dominant_count': counts[max_element],
            'lacking': min_element,
            'lacking_count': counts[min_element],
        }
    
    def _analyze_modality_balance(self):
        """3区分のバランスを分析"""
        counts = {'cardinal': 0, 'fixed': 0, 'mutable': 0}
        
        main_planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 
                       'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
        
        for planet_key in main_planets:
            if planet_key in self.planets_data:
                sign = self.planets_data[planet_key]['sign']
                for modality, signs in MODALITIES.items():
                    if sign in signs:
                        counts[modality] += 1
                        break
        
        self.modality_balance = counts
        
        max_modality = max(counts, key=counts.get)
        min_modality = min(counts, key=counts.get)
        
        self.modality_analysis = {
            'counts': counts,
            'dominant': max_modality,
            'dominant_count': counts[max_modality],
            'lacking': min_modality,
            'lacking_count': counts[min_modality],
        }
    
    def get_planet_in_house(self, house_number: int) -> List[Dict]:
        """指定ハウスにある天体のリストを取得"""
        planets_in_house = []
        for key, data in self.planets_data.items():
            if data.get('house') == house_number:
                planets_in_house.append({
                    'key': key,
                    **data
                })
        return planets_in_house
    
    def get_aspects_for_planet(self, planet_key: str) -> List[Dict]:
        """指定天体のアスペクトを取得"""
        return [
            asp for asp in self.aspects_data 
            if asp['planet1'] == planet_key or asp['planet2'] == planet_key
        ]
    
    def get_full_chart(self) -> Dict[str, Any]:
        """完全なホロスコープデータを返す"""
        return {
            'meta': {
                'name': self.name,
                'birth_datetime': self.birth_datetime.isoformat(),
                'birth_place': self.birth_place,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'timezone': self.timezone,
                'julian_day': self.julian_day,
                'calculation_method': 'Swiss Ephemeris (Placidus House System)',
            },
            'planets': self.planets_data,
            'houses': self.houses_data,
            'angles': self.angles_data,
            'aspects': self.aspects_data,
            'analysis': {
                'elements': self.element_analysis,
                'modalities': self.modality_analysis,
            }
        }
    
    def get_variables_for_step(self, step_id: str) -> Dict[str, Any]:
        """
        特定のステップに必要な変数を取得
        
        Args:
            step_id: ステップID（例: "1-A", "2-A"）
        
        Returns:
            そのステップで使用する変数の辞書
        """
        variables = {}
        
        if step_id == "1-A":
            # 4元素分析用
            variables = {
                'fire_count': self.element_balance.get('fire', 0),
                'earth_count': self.element_balance.get('earth', 0),
                'air_count': self.element_balance.get('air', 0),
                'water_count': self.element_balance.get('water', 0),
                'dominant_element': self.element_analysis.get('dominant', ''),
                'lacking_element': self.element_analysis.get('lacking', ''),
            }
        
        elif step_id == "1-B":
            # 3区分・アングル用
            variables = {
                'cardinal_count': self.modality_balance.get('cardinal', 0),
                'fixed_count': self.modality_balance.get('fixed', 0),
                'mutable_count': self.modality_balance.get('mutable', 0),
                'asc_sign': self.angles_data.get('asc', {}).get('sign_jp', ''),
                'mc_sign': self.angles_data.get('mc', {}).get('sign_jp', ''),
                'ic_sign': self.angles_data.get('ic', {}).get('sign_jp', ''),
                'dc_sign': self.angles_data.get('dc', {}).get('sign_jp', ''),
                'asc_degree': self.angles_data.get('asc', {}).get('degree_formatted', ''),
                'mc_degree': self.angles_data.get('mc', {}).get('degree_formatted', ''),
            }
        
        elif step_id == "2-A":
            # 太陽・月用
            sun = self.planets_data.get('sun', {})
            moon = self.planets_data.get('moon', {})
            sun_moon_aspects = [
                asp for asp in self.aspects_data 
                if ('sun' in [asp['planet1'], asp['planet2']] and 
                    'moon' in [asp['planet1'], asp['planet2']])
            ]
            
            variables = {
                'sun_sign': sun.get('sign_jp', ''),
                'sun_house': sun.get('house', 0),
                'sun_degree': sun.get('degree_formatted', ''),
                'sun_sabian_degree': sun.get('sabian_degree', 1),
                'sun_sabian_symbol': '',  # サビアンシンボルDBから取得
                'moon_sign': moon.get('sign_jp', ''),
                'moon_house': moon.get('house', 0),
                'moon_degree': moon.get('degree_formatted', ''),
                'moon_sabian_degree': moon.get('sabian_degree', 1),
                'moon_sabian_symbol': '',  # サビアンシンボルDBから取得
                'sun_moon_aspect': sun_moon_aspects[0]['aspect_jp'] if sun_moon_aspects else 'なし',
                'sun_moon_aspect_orb': sun_moon_aspects[0]['orb'] if sun_moon_aspects else 0,
            }
        
        elif step_id == "2-B":
            # 水星・金星・火星用
            mercury = self.planets_data.get('mercury', {})
            venus = self.planets_data.get('venus', {})
            mars = self.planets_data.get('mars', {})
            
            variables = {
                'mercury_sign': mercury.get('sign_jp', ''),
                'mercury_house': mercury.get('house', 0),
                'mercury_sabian_symbol': '',
                'mercury_retrograde': mercury.get('retrograde', False),
                'venus_sign': venus.get('sign_jp', ''),
                'venus_house': venus.get('house', 0),
                'venus_sabian_symbol': '',
                'venus_retrograde': venus.get('retrograde', False),
                'mars_sign': mars.get('sign_jp', ''),
                'mars_house': mars.get('house', 0),
                'mars_sabian_symbol': '',
                'mars_retrograde': mars.get('retrograde', False),
            }
        
        # 他のステップも同様に追加...
        
        return variables


# =============================================================================
# プログレス計算クラス
# =============================================================================

class ProgressedCalculator:
    """セカンダリー・プログレッション計算"""
    
    def __init__(self, natal_chart: AstroCalculator, target_date: datetime):
        """
        初期化
        
        Args:
            natal_chart: ネイタルチャート
            target_date: プログレスを計算する対象日
        """
        self.natal = natal_chart
        self.target_date = target_date
        
        # 出生日からの経過年数を計算
        birth_dt = natal_chart.birth_datetime
        delta = target_date - birth_dt
        self.years_elapsed = delta.days / 365.25
        
        # プログレス日（1日=1年）
        progressed_days = delta.days / 365.25  # 年数 = 日数
        self.progressed_datetime = birth_dt + timedelta(days=progressed_days)
        self.progressed_jd = julian_day_from_datetime(
            self.progressed_datetime, 
            natal_chart.timezone
        )
        
        self.progressed_planets: Dict[str, Dict] = {}
    
    def calculate(self) -> Dict[str, Any]:
        """プログレス天体を計算"""
        for key, planet_info in PLANETS.items():
            try:
                result = swe.calc_ut(self.progressed_jd, planet_info['id'])
                longitude = result[0][0]
                
                sign, degree = longitude_to_sign(longitude)
                
                self.progressed_planets[key] = {
                    'name_jp': planet_info['name_jp'],
                    'name_en': planet_info['name_en'],
                    'longitude': round(longitude, 4),
                    'sign': sign,
                    'sign_jp': SIGNS_JP[sign],
                    'degree': round(degree, 4),
                    'sabian_degree': get_sabian_degree(degree),
                }
                
            except Exception as e:
                print(f"Error calculating progressed {key}: {e}")
                continue
        
        return {
            'target_date': self.target_date.isoformat(),
            'years_elapsed': round(self.years_elapsed, 2),
            'progressed_datetime': self.progressed_datetime.isoformat(),
            'planets': self.progressed_planets,
        }


# =============================================================================
# トランジット計算クラス
# =============================================================================

class TransitCalculator:
    """トランジット計算"""
    
    def __init__(self, natal_chart: AstroCalculator):
        """
        初期化
        
        Args:
            natal_chart: ネイタルチャート
        """
        self.natal = natal_chart
    
    def calculate_for_date(self, target_date: datetime) -> Dict[str, Any]:
        """特定日のトランジット天体を計算"""
        jd = julian_day_from_datetime(target_date, self.natal.timezone)
        
        transit_planets = {}
        
        for key, planet_info in PLANETS.items():
            try:
                result = swe.calc_ut(jd, planet_info['id'])
                longitude = result[0][0]
                speed = result[0][3]
                
                sign, degree = longitude_to_sign(longitude)
                
                transit_planets[key] = {
                    'name_jp': planet_info['name_jp'],
                    'name_en': planet_info['name_en'],
                    'longitude': round(longitude, 4),
                    'sign': sign,
                    'sign_jp': SIGNS_JP[sign],
                    'degree': round(degree, 4),
                    'retrograde': speed < 0 if key not in ['sun', 'moon', 'north_node'] else False,
                }
                
            except Exception as e:
                print(f"Error calculating transit {key}: {e}")
                continue
        
        return {
            'date': target_date.isoformat(),
            'planets': transit_planets,
        }
    
    def find_aspects_to_natal(self, transit_date: datetime) -> List[Dict]:
        """トランジット天体とネイタル天体のアスペクトを検出"""
        transit_data = self.calculate_for_date(transit_date)
        aspects = []
        
        for t_key, t_planet in transit_data['planets'].items():
            for n_key, n_planet in self.natal.planets_data.items():
                angle = calculate_aspect_angle(t_planet['longitude'], n_planet['longitude'])
                
                for aspect_name, aspect_info in ASPECTS.items():
                    diff = abs(angle - aspect_info['degree'])
                    # トランジットは狭いオーブで判定
                    orb = aspect_info['orb'] / 2 if t_key in ['uranus', 'neptune', 'pluto'] else aspect_info['orb']
                    
                    if diff <= orb:
                        aspects.append({
                            'transit_planet': t_key,
                            'transit_planet_jp': t_planet['name_jp'],
                            'natal_planet': n_key,
                            'natal_planet_jp': n_planet['name_jp'],
                            'aspect': aspect_name,
                            'aspect_jp': aspect_info['name_jp'],
                            'orb': round(diff, 2),
                        })
                        break
        
        return aspects
    
    def forecast_year(self, year: int) -> Dict[str, Any]:
        """1年間の主要トランジットイベントを予測"""
        events = []
        
        # 毎月1日のトランジットをチェック
        for month in range(1, 13):
            date = datetime(year, month, 1, 12, 0)
            aspects = self.find_aspects_to_natal(date)
            
            # 重要なアスペクトのみフィルタ
            important_aspects = [
                asp for asp in aspects 
                if asp['transit_planet'] in ['jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
            ]
            
            if important_aspects:
                events.append({
                    'date': date.isoformat(),
                    'month': month,
                    'aspects': important_aspects,
                })
        
        return {
            'year': year,
            'events': events,
        }


# =============================================================================
# ユーティリティ関数
# =============================================================================

def create_chart(
    name: str,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    birth_minute: int,
    birth_place: str
) -> Dict[str, Any]:
    """
    ホロスコープを作成する便利関数
    
    Args:
        name: 名前
        birth_year: 出生年
        birth_month: 出生月
        birth_day: 出生日
        birth_hour: 出生時
        birth_minute: 出生分
        birth_place: 出生地
    
    Returns:
        完全なホロスコープデータ
    """
    birth_datetime = datetime(birth_year, birth_month, birth_day, birth_hour, birth_minute)
    calculator = AstroCalculator(birth_datetime, birth_place, name)
    return calculator.calculate_all()


# =============================================================================
# テスト用
# =============================================================================

if __name__ == "__main__":
    # テスト実行
    test_chart = create_chart(
        name="テストユーザー",
        birth_year=1990,
        birth_month=1,
        birth_day=15,
        birth_hour=10,
        birth_minute=30,
        birth_place="東京都"
    )
    
    print(json.dumps(test_chart, ensure_ascii=False, indent=2))
