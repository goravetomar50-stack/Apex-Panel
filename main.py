# ============================================
# APEX NUMBER PANEL - SERVICE MANAGEMENT
# Channel: @ZeroFlux02
# Owner: @ApexVora
# ============================================

import time
import requests
import json
import re
import os
import traceback
from datetime import datetime, timedelta
import sqlite3
import telebot
from telebot import types
import threading
import random
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout, ConnectionError

# ============================================
# NUMBER PANEL API CONFIGURATION
# ============================================

NUMBERPANEL_BASE_URL = "https://numberpanel.tech"
NUMBERPANEL_API_KEY = "np_live_GiBRf5ynsn-Y_pQmzpibDIKUze7fJvW7L1hdYNiLf_Q"
NUMBERPANEL_HEADERS = {"Authorization": f"Bearer {NUMBERPANEL_API_KEY}"}
NUMBERPANEL_TIMEOUT = 15

# ✅ Persistent session (faster than new connection each time)
_np_session = requests.Session()
_np_session.headers.update(NUMBERPANEL_HEADERS)
_np_adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=1)
_np_session.mount("https://", _np_adapter)
_np_session.mount("http://", _np_adapter)

# ✅ Simple TTL caches
_countries_cache = {}
_countries_cache_time = {}
_stats_cache = {}
_stats_cache_time = {}
_services_cache = {"data": None, "time": 0}

# ============================================
# GENERAL SETTINGS
# ============================================

BOT_TOKEN = "8502203429:AAHM2lrMLcX-jBS2p8QBXxnUXxZEH-dyiso"
if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    raise SystemExit("❌ Please set a valid BOT_TOKEN in the script!")

CHAT_IDS = ["-1003890262370"]

REFRESH_INTERVAL = 3
DB_PATH = "bot.db"
BOT_ACTIVE = True
CHANNEL_USERNAME = "@ZeroFlux02"
BOT_NAME = "Apex Number Panel"
OWNER_USERNAME = "@ApexVora"
OTP_GROUP_LINK = "https://t.me/+VYISBBggOBIxNzk1"
SUPPORT_LINK = "https://t.me/ApexVora"
NUMBERS_PER_USER = 3
AUTO_EXPIRE_MINUTES = 20

BOT_PANEL_LINK = "https://t.me/ApexNumberPanelBot?start=start"
DEVELOPER_LINK = "https://t.me/ApexVora"
DEVELOPER_DISPLAY_NAME = "𓂃❛ ⟶𝐀ᴘᴇx𝐕ᴏʀᴀ❜ 🌙⤹🌸"

DEFAULT_ADMIN_IDS = [7166862111, 7950051505]

# ============================================
# COUNTRY CODES & FLAG MAPPINGS
# ============================================

# Numeric code -> (Full name, flag emoji)
COUNTRY_CODES = {
    "1": ("USA/Canada", "🇺🇸"),
    "7": ("Russia", "🇷🇺"),
    "20": ("Egypt", "🇪🇬"),
    "27": ("South Africa", "🇿🇦"),
    "30": ("Greece", "🇬🇷"),
    "31": ("Netherlands", "🇳🇱"),
    "32": ("Belgium", "🇧🇪"),
    "33": ("France", "🇫🇷"),
    "34": ("Spain", "🇪🇸"),
    "36": ("Hungary", "🇭🇺"),
    "39": ("Italy", "🇮🇹"),
    "40": ("Romania", "🇷🇴"),
    "41": ("Switzerland", "🇨🇭"),
    "43": ("Austria", "🇦🇹"),
    "44": ("United Kingdom", "🇬🇧"),
    "45": ("Denmark", "🇩🇰"),
    "46": ("Sweden", "🇸🇪"),
    "47": ("Norway", "🇳🇴"),
    "48": ("Poland", "🇵🇱"),
    "49": ("Germany", "🇩🇪"),
    "51": ("Peru", "🇵🇪"),
    "52": ("Mexico", "🇲🇽"),
    "53": ("Cuba", "🇨🇺"),
    "54": ("Argentina", "🇦🇷"),
    "55": ("Brazil", "🇧🇷"),
    "56": ("Chile", "🇨🇱"),
    "57": ("Colombia", "🇨🇴"),
    "58": ("Venezuela", "🇻🇪"),
    "60": ("Malaysia", "🇲🇾"),
    "61": ("Australia", "🇦🇺"),
    "62": ("Indonesia", "🇮🇩"),
    "63": ("Philippines", "🇵🇭"),
    "64": ("New Zealand", "🇳🇿"),
    "65": ("Singapore", "🇸🇬"),
    "66": ("Thailand", "🇹🇭"),
    "81": ("Japan", "🇯🇵"),
    "82": ("South Korea", "🇰🇷"),
    "84": ("Vietnam", "🇻🇳"),
    "86": ("China", "🇨🇳"),
    "90": ("Turkey", "🇹🇷"),
    "91": ("India", "🇮🇳"),
    "92": ("Pakistan", "🇵🇰"),
    "93": ("Afghanistan", "🇦🇫"),
    "94": ("Sri Lanka", "🇱🇰"),
    "95": ("Myanmar", "🇲🇲"),
    "98": ("Iran", "🇮🇷"),
    "212": ("Morocco", "🇲🇦"),
    "213": ("Algeria", "🇩🇿"),
    "216": ("Tunisia", "🇹🇳"),
    "218": ("Libya", "🇱🇾"),
    "220": ("Gambia", "🇬🇲"),
    "221": ("Senegal", "🇸🇳"),
    "222": ("Mauritania", "🇲🇷"),
    "223": ("Mali", "🇲🇱"),
    "224": ("Guinea", "🇬🇳"),
    "225": ("Ivory Coast", "🇨🇮"),
    "226": ("Burkina Faso", "🇧🇫"),
    "227": ("Niger", "🇳🇪"),
    "228": ("Togo", "🇹🇬"),
    "229": ("Benin", "🇧🇯"),
    "230": ("Mauritius", "🇲🇺"),
    "231": ("Liberia", "🇱🇷"),
    "232": ("Sierra Leone", "🇸🇱"),
    "233": ("Ghana", "🇬🇭"),
    "234": ("Nigeria", "🇳🇬"),
    "235": ("Chad", "🇹🇩"),
    "236": ("Central African Rep", "🇨🇫"),
    "237": ("Cameroon", "🇨🇲"),
    "238": ("Cape Verde", "🇨🇻"),
    "239": ("Sao Tome", "🇸🇹"),
    "240": ("Equatorial Guinea", "🇬🇶"),
    "241": ("Gabon", "🇬🇦"),
    "242": ("Congo", "🇨🇬"),
    "243": ("DR Congo", "🇨🇩"),
    "244": ("Angola", "🇦🇴"),
    "245": ("Guinea-Bissau", "🇬🇼"),
    "248": ("Seychelles", "🇸🇨"),
    "249": ("Sudan", "🇸🇩"),
    "250": ("Rwanda", "🇷🇼"),
    "251": ("Ethiopia", "🇪🇹"),
    "252": ("Somalia", "🇸🇴"),
    "253": ("Djibouti", "🇩🇯"),
    "254": ("Kenya", "🇰🇪"),
    "255": ("Tanzania", "🇹🇿"),
    "256": ("Uganda", "🇺🇬"),
    "257": ("Burundi", "🇧🇮"),
    "258": ("Mozambique", "🇲🇿"),
    "260": ("Zambia", "🇿🇲"),
    "261": ("Madagascar", "🇲🇬"),
    "262": ("Reunion", "🇷🇪"),
    "263": ("Zimbabwe", "🇿🇼"),
    "264": ("Namibia", "🇳🇦"),
    "265": ("Malawi", "🇲🇼"),
    "266": ("Lesotho", "🇱🇸"),
    "267": ("Botswana", "🇧🇼"),
    "268": ("Eswatini", "🇸🇿"),
    "269": ("Comoros", "🇰🇲"),
    "350": ("Gibraltar", "🇬🇮"),
    "351": ("Portugal", "🇵🇹"),
    "352": ("Luxembourg", "🇱🇺"),
    "353": ("Ireland", "🇮🇪"),
    "354": ("Iceland", "🇮🇸"),
    "355": ("Albania", "🇦🇱"),
    "356": ("Malta", "🇲🇹"),
    "357": ("Cyprus", "🇨🇾"),
    "358": ("Finland", "🇫🇮"),
    "359": ("Bulgaria", "🇧🇬"),
    "370": ("Lithuania", "🇱🇹"),
    "371": ("Latvia", "🇱🇻"),
    "372": ("Estonia", "🇪🇪"),
    "373": ("Moldova", "🇲🇩"),
    "374": ("Armenia", "🇦🇲"),
    "375": ("Belarus", "🇧🇾"),
    "376": ("Andorra", "🇦🇩"),
    "377": ("Monaco", "🇲🇨"),
    "378": ("San Marino", "🇸🇲"),
    "380": ("Ukraine", "🇺🇦"),
    "381": ("Serbia", "🇷🇸"),
    "382": ("Montenegro", "🇲🇪"),
    "383": ("Kosovo", "🇽🇰"),
    "385": ("Croatia", "🇭🇷"),
    "386": ("Slovenia", "🇸🇮"),
    "387": ("Bosnia", "🇧🇦"),
    "389": ("North Macedonia", "🇲🇰"),
    "420": ("Czech Republic", "🇨🇿"),
    "421": ("Slovakia", "🇸🇰"),
    "423": ("Liechtenstein", "🇱🇮"),
    "500": ("Falkland Islands", "🇫🇰"),
    "501": ("Belize", "🇧🇿"),
    "502": ("Guatemala", "🇬🇹"),
    "503": ("El Salvador", "🇸🇻"),
    "504": ("Honduras", "🇭🇳"),
    "505": ("Nicaragua", "🇳🇮"),
    "506": ("Costa Rica", "🇨🇷"),
    "507": ("Panama", "🇵🇦"),
    "509": ("Haiti", "🇭🇹"),
    "591": ("Bolivia", "🇧🇴"),
    "592": ("Guyana", "🇬🇾"),
    "593": ("Ecuador", "🇪🇨"),
    "595": ("Paraguay", "🇵🇾"),
    "597": ("Suriname", "🇸🇷"),
    "598": ("Uruguay", "🇺🇾"),
    "670": ("Timor-Leste", "🇹🇱"),
    "673": ("Brunei", "🇧🇳"),
    "674": ("Nauru", "🇳🇷"),
    "675": ("Papua New Guinea", "🇵🇬"),
    "676": ("Tonga", "🇹🇴"),
    "677": ("Solomon Islands", "🇸🇧"),
    "678": ("Vanuatu", "🇻🇺"),
    "679": ("Fiji", "🇫🇯"),
    "680": ("Palau", "🇵🇼"),
    "685": ("Samoa", "🇼🇸"),
    "686": ("Kiribati", "🇰🇮"),
    "687": ("New Caledonia", "🇳🇨"),
    "688": ("Tuvalu", "🇹🇻"),
    "689": ("French Polynesia", "🇵🇫"),
    "691": ("Micronesia", "🇫🇲"),
    "692": ("Marshall Islands", "🇲🇭"),
    "850": ("North Korea", "🇰🇵"),
    "852": ("Hong Kong", "🇭🇰"),
    "853": ("Macau", "🇲🇴"),
    "855": ("Cambodia", "🇰🇭"),
    "856": ("Laos", "🇱🇦"),
    "960": ("Maldives", "🇲🇻"),
    "961": ("Lebanon", "🇱🇧"),
    "962": ("Jordan", "🇯🇴"),
    "963": ("Syria", "🇸🇾"),
    "964": ("Iraq", "🇮🇶"),
    "965": ("Kuwait", "🇰🇼"),
    "966": ("Saudi Arabia", "🇸🇦"),
    "967": ("Yemen", "🇾🇪"),
    "968": ("Oman", "🇴🇲"),
    "970": ("Palestine", "🇵🇸"),
    "971": ("UAE", "🇦🇪"),
    "972": ("Israel", "🇮🇱"),
    "973": ("Bahrain", "🇧🇭"),
    "974": ("Qatar", "🇶🇦"),
    "975": ("Bhutan", "🇧🇹"),
    "976": ("Mongolia", "🇲🇳"),
    "977": ("Nepal", "🇳🇵"),
    "992": ("Tajikistan", "🇹🇯"),
    "993": ("Turkmenistan", "🇹🇲"),
    "994": ("Azerbaijan", "🇦🇿"),
    "995": ("Georgia", "🇬🇪"),
    "996": ("Kyrgyzstan", "🇰🇬"),
    "998": ("Uzbekistan", "🇺🇿"),
    "211": ("South Sudan", "🇸🇸"),
    "297": ("Aruba", "🇦🇼"),
    "298": ("Faroe Islands", "🇫🇴"),
    "299": ("Greenland", "🇬🇱"),
    "590": ("Guadeloupe", "🇬🇵"),
    "594": ("French Guiana", "🇬🇫"),
    "596": ("Martinique", "🇲🇶"),
    "599": ("Curacao", "🇨🇼"),
    "681": ("Wallis and Futuna", "🇼🇫"),
    "682": ("Cook Islands", "🇨🇰"),
    "683": ("Niue", "🇳🇺"),
    "684": ("American Samoa", "🇦🇸"),
    "690": ("Tokelau", "🇹🇰"),
    "880": ("Bangladesh", "🇧🇩"),
    "886": ("Taiwan", "🇹🇼"),
}

# ISO 2-letter code -> (Full name, flag emoji)
ISO_TO_FLAG = {
    "AF": ("Afghanistan", "🇦🇫"),
    "AX": ("Aland Islands", "🇦🇽"),
    "AL": ("Albania", "🇦🇱"),
    "DZ": ("Algeria", "🇩🇿"),
    "AS": ("American Samoa", "🇦🇸"),
    "AD": ("Andorra", "🇦🇩"),
    "AO": ("Angola", "🇦🇴"),
    "AI": ("Anguilla", "🇦🇮"),
    "AQ": ("Antarctica", "🇦🇶"),
    "AG": ("Antigua and Barbuda", "🇦🇬"),
    "AR": ("Argentina", "🇦🇷"),
    "AM": ("Armenia", "🇦🇲"),
    "AW": ("Aruba", "🇦🇼"),
    "AU": ("Australia", "🇦🇺"),
    "AT": ("Austria", "🇦🇹"),
    "AZ": ("Azerbaijan", "🇦🇿"),
    "BS": ("Bahamas", "🇧🇸"),
    "BH": ("Bahrain", "🇧🇭"),
    "BD": ("Bangladesh", "🇧🇩"),
    "BB": ("Barbados", "🇧🇧"),
    "BY": ("Belarus", "🇧🇾"),
    "BE": ("Belgium", "🇧🇪"),
    "BZ": ("Belize", "🇧🇿"),
    "BJ": ("Benin", "🇧🇯"),
    "BM": ("Bermuda", "🇧🇲"),
    "BT": ("Bhutan", "🇧🇹"),
    "BO": ("Bolivia", "🇧🇴"),
    "BA": ("Bosnia and Herzegovina", "🇧🇦"),
    "BW": ("Botswana", "🇧🇼"),
    "BV": ("Bouvet Island", "🇧🇻"),
    "BR": ("Brazil", "🇧🇷"),
    "IO": ("British Indian Ocean Territory", "🇮🇴"),
    "BN": ("Brunei Darussalam", "🇧🇳"),
    "BG": ("Bulgaria", "🇧🇬"),
    "BF": ("Burkina Faso", "🇧🇫"),
    "BI": ("Burundi", "🇧🇮"),
    "KH": ("Cambodia", "🇰🇭"),
    "CM": ("Cameroon", "🇨🇲"),
    "CA": ("Canada", "🇨🇦"),
    "CV": ("Cape Verde", "🇨🇻"),
    "KY": ("Cayman Islands", "🇰🇾"),
    "CF": ("Central African Republic", "🇨🇫"),
    "TD": ("Chad", "🇹🇩"),
    "CL": ("Chile", "🇨🇱"),
    "CN": ("China", "🇨🇳"),
    "CX": ("Christmas Island", "🇨🇽"),
    "CC": ("Cocos (Keeling) Islands", "🇨🇨"),
    "CO": ("Colombia", "🇨🇴"),
    "KM": ("Comoros", "🇰🇲"),
    "CG": ("Congo", "🇨🇬"),
    "CD": ("Congo, Democratic Republic", "🇨🇩"),
    "CK": ("Cook Islands", "🇨🇰"),
    "CR": ("Costa Rica", "🇨🇷"),
    "CI": ("Cote D'Ivoire", "🇨🇮"),
    "HR": ("Croatia", "🇭🇷"),
    "CU": ("Cuba", "🇨🇺"),
    "CY": ("Cyprus", "🇨🇾"),
    "CZ": ("Czech Republic", "🇨🇿"),
    "DK": ("Denmark", "🇩🇰"),
    "DJ": ("Djibouti", "🇩🇯"),
    "DM": ("Dominica", "🇩🇲"),
    "DO": ("Dominican Republic", "🇩🇴"),
    "EC": ("Ecuador", "🇪🇨"),
    "EG": ("Egypt", "🇪🇬"),
    "SV": ("El Salvador", "🇸🇻"),
    "GQ": ("Equatorial Guinea", "🇬🇶"),
    "ER": ("Eritrea", "🇪🇷"),
    "EE": ("Estonia", "🇪🇪"),
    "ET": ("Ethiopia", "🇪🇹"),
    "FK": ("Falkland Islands (Malvinas)", "🇫🇰"),
    "FO": ("Faroe Islands", "🇫🇴"),
    "FJ": ("Fiji", "🇫🇯"),
    "FI": ("Finland", "🇫🇮"),
    "FR": ("France", "🇫🇷"),
    "GF": ("French Guiana", "🇬🇫"),
    "PF": ("French Polynesia", "🇵🇫"),
    "TF": ("French Southern Territories", "🇹🇫"),
    "GA": ("Gabon", "🇬🇦"),
    "GM": ("Gambia", "🇬🇲"),
    "GE": ("Georgia", "🇬🇪"),
    "DE": ("Germany", "🇩🇪"),
    "GH": ("Ghana", "🇬🇭"),
    "GI": ("Gibraltar", "🇬🇮"),
    "GR": ("Greece", "🇬🇷"),
    "GL": ("Greenland", "🇬🇱"),
    "GD": ("Grenada", "🇬🇩"),
    "GP": ("Guadeloupe", "🇬🇵"),
    "GU": ("Guam", "🇬🇺"),
    "GT": ("Guatemala", "🇬🇹"),
    "GG": ("Guernsey", "🇬🇬"),
    "GN": ("Guinea", "🇬🇳"),
    "GW": ("Guinea-Bissau", "🇬🇼"),
    "GY": ("Guyana", "🇬🇾"),
    "HT": ("Haiti", "🇭🇹"),
    "HM": ("Heard Island and Mcdonald Islands", "🇭🇲"),
    "VA": ("Holy See (Vatican City State)", "🇻🇦"),
    "HN": ("Honduras", "🇭🇳"),
    "HK": ("Hong Kong", "🇭🇰"),
    "HU": ("Hungary", "🇭🇺"),
    "IS": ("Iceland", "🇮🇸"),
    "IN": ("India", "🇮🇳"),
    "ID": ("Indonesia", "🇮🇩"),
    "IR": ("Iran, Islamic Republic of", "🇮🇷"),
    "IQ": ("Iraq", "🇮🇶"),
    "IE": ("Ireland", "🇮🇪"),
    "IM": ("Isle of Man", "🇮🇲"),
    "IL": ("Israel", "🇮🇱"),
    "IT": ("Italy", "🇮🇹"),
    "JM": ("Jamaica", "🇯🇲"),
    "JP": ("Japan", "🇯🇵"),
    "JE": ("Jersey", "🇯🇪"),
    "JO": ("Jordan", "🇯🇴"),
    "KZ": ("Kazakhstan", "🇰🇿"),
    "KE": ("Kenya", "🇰🇪"),
    "KI": ("Kiribati", "🇰🇮"),
    "KP": ("North Korea", "🇰🇵"),
    "KR": ("South Korea", "🇰🇷"),
    "KW": ("Kuwait", "🇰🇼"),
    "KG": ("Kyrgyzstan", "🇰🇬"),
    "LA": ("Lao People's Democratic Republic", "🇱🇦"),
    "LV": ("Latvia", "🇱🇻"),
    "LB": ("Lebanon", "🇱🇧"),
    "LS": ("Lesotho", "🇱🇸"),
    "LR": ("Liberia", "🇱🇷"),
    "LY": ("Libya", "🇱🇾"),
    "LI": ("Liechtenstein", "🇱🇮"),
    "LT": ("Lithuania", "🇱🇹"),
    "LU": ("Luxembourg", "🇱🇺"),
    "MO": ("Macao", "🇲🇴"),
    "MK": ("North Macedonia", "🇲🇰"),
    "MG": ("Madagascar", "🇲🇬"),
    "MW": ("Malawi", "🇲🇼"),
    "MY": ("Malaysia", "🇲🇾"),
    "MV": ("Maldives", "🇲🇻"),
    "ML": ("Mali", "🇲🇱"),
    "MT": ("Malta", "🇲🇹"),
    "MH": ("Marshall Islands", "🇲🇭"),
    "MQ": ("Martinique", "🇲🇶"),
    "MR": ("Mauritania", "🇲🇷"),
    "MU": ("Mauritius", "🇲🇺"),
    "YT": ("Mayotte", "🇾🇹"),
    "MX": ("Mexico", "🇲🇽"),
    "FM": ("Micronesia, Federated States of", "🇫🇲"),
    "MD": ("Moldova, Republic of", "🇲🇩"),
    "MC": ("Monaco", "🇲🇨"),
    "MN": ("Mongolia", "🇲🇳"),
    "ME": ("Montenegro", "🇲🇪"),
    "MS": ("Montserrat", "🇲🇸"),
    "MA": ("Morocco", "🇲🇦"),
    "MZ": ("Mozambique", "🇲🇿"),
    "MM": ("Myanmar", "🇲🇲"),
    "NA": ("Namibia", "🇳🇦"),
    "NR": ("Nauru", "🇳🇷"),
    "NP": ("Nepal", "🇳🇵"),
    "NL": ("Netherlands", "🇳🇱"),
    "AN": ("Netherlands Antilles", "🇦🇳"),
    "NC": ("New Caledonia", "🇳🇨"),
    "NZ": ("New Zealand", "🇳🇿"),
    "NI": ("Nicaragua", "🇳🇮"),
    "NE": ("Niger", "🇳🇪"),
    "NG": ("Nigeria", "🇳🇬"),
    "NU": ("Niue", "🇳🇺"),
    "NF": ("Norfolk Island", "🇳🇫"),
    "MP": ("Northern Mariana Islands", "🇲🇵"),
    "NO": ("Norway", "🇳🇴"),
    "OM": ("Oman", "🇴🇲"),
    "PK": ("Pakistan", "🇵🇰"),
    "PW": ("Palau", "🇵🇼"),
    "PS": ("Palestine, State of", "🇵🇸"),
    "PA": ("Panama", "🇵🇦"),
    "PG": ("Papua New Guinea", "🇵🇬"),
    "PY": ("Paraguay", "🇵🇾"),
    "PE": ("Peru", "🇵🇪"),
    "PH": ("Philippines", "🇵🇭"),
    "PN": ("Pitcairn", "🇵🇳"),
    "PL": ("Poland", "🇵🇱"),
    "PT": ("Portugal", "🇵🇹"),
    "PR": ("Puerto Rico", "🇵🇷"),
    "QA": ("Qatar", "🇶🇦"),
    "RE": ("Reunion", "🇷🇪"),
    "RO": ("Romania", "🇷🇴"),
    "RU": ("Russian Federation", "🇷🇺"),
    "RW": ("Rwanda", "🇷🇼"),
    "BL": ("Saint Barthelemy", "🇧🇱"),
    "SH": ("Saint Helena", "🇸🇭"),
    "KN": ("Saint Kitts and Nevis", "🇰🇳"),
    "LC": ("Saint Lucia", "🇱🇨"),
    "MF": ("Saint Martin", "🇲🇫"),
    "PM": ("Saint Pierre and Miquelon", "🇵🇲"),
    "VC": ("Saint Vincent and the Grenadines", "🇻🇨"),
    "WS": ("Samoa", "🇼🇸"),
    "SM": ("San Marino", "🇸🇲"),
    "ST": ("Sao Tome and Principe", "🇸🇹"),
    "SA": ("Saudi Arabia", "🇸🇦"),
    "SN": ("Senegal", "🇸🇳"),
    "RS": ("Serbia", "🇷🇸"),
    "SC": ("Seychelles", "🇸🇨"),
    "SL": ("Sierra Leone", "🇸🇱"),
    "SG": ("Singapore", "🇸🇬"),
    "SK": ("Slovakia", "🇸🇰"),
    "SI": ("Slovenia", "🇸🇮"),
    "SB": ("Solomon Islands", "🇸🇧"),
    "SO": ("Somalia", "🇸🇴"),
    "ZA": ("South Africa", "🇿🇦"),
    "GS": ("South Georgia and the South Sandwich Islands", "🇬🇸"),
    "SS": ("South Sudan", "🇸🇸"),
    "ES": ("Spain", "🇪🇸"),
    "LK": ("Sri Lanka", "🇱🇰"),
    "SD": ("Sudan", "🇸🇩"),
    "SR": ("Suriname", "🇸🇷"),
    "SJ": ("Svalbard and Jan Mayen", "🇸🇯"),
    "SZ": ("Eswatini", "🇸🇿"),
    "SE": ("Sweden", "🇸🇪"),
    "CH": ("Switzerland", "🇨🇭"),
    "SY": ("Syrian Arab Republic", "🇸🇾"),
    "TW": ("Taiwan, Province of China", "🇹🇼"),
    "TJ": ("Tajikistan", "🇹🇯"),
    "TZ": ("Tanzania, United Republic of", "🇹🇿"),
    "TH": ("Thailand", "🇹🇭"),
    "TL": ("Timor-Leste", "🇹🇱"),
    "TG": ("Togo", "🇹🇬"),
    "TK": ("Tokelau", "🇹🇰"),
    "TO": ("Tonga", "🇹🇴"),
    "TT": ("Trinidad and Tobago", "🇹🇹"),
    "TN": ("Tunisia", "🇹🇳"),
    "TR": ("Turkey", "🇹🇷"),
    "TM": ("Turkmenistan", "🇹🇲"),
    "TC": ("Turks and Caicos Islands", "🇹🇨"),
    "TV": ("Tuvalu", "🇹🇻"),
    "UG": ("Uganda", "🇺🇬"),
    "UA": ("Ukraine", "🇺🇦"),
    "AE": ("United Arab Emirates", "🇦🇪"),
    "GB": ("United Kingdom", "🇬🇧"),
    "US": ("United States", "🇺🇸"),
    "UM": ("United States Minor Outlying Islands", "🇺🇲"),
    "UY": ("Uruguay", "🇺🇾"),
    "UZ": ("Uzbekistan", "🇺🇿"),
    "VU": ("Vanuatu", "🇻🇺"),
    "VE": ("Venezuela, Bolivarian Republic of", "🇻🇪"),
    "VN": ("Viet Nam", "🇻🇳"),
    "VG": ("Virgin Islands, British", "🇻🇬"),
    "VI": ("Virgin Islands, U.S.", "🇻🇮"),
    "WF": ("Wallis and Futuna", "🇼🇫"),
    "EH": ("Western Sahara", "🇪🇭"),
    "YE": ("Yemen", "🇾🇪"),
    "ZM": ("Zambia", "🇿🇲"),
    "ZW": ("Zimbabwe", "🇿🇼"),
}

def get_country_flag_and_name(country_input):
    """Return (flag_emoji, full_name) for a given country name or ISO code."""
    if not country_input:
        return "🌍", "Unknown"
    country_input = str(country_input).strip()

    # If input is a 2-letter uppercase ISO code
    if len(country_input) == 2 and country_input.isupper():
        if country_input in ISO_TO_FLAG:
            name, flag = ISO_TO_FLAG[country_input]   # ✅ FIXED
            return flag, name
        else:
            return "🌍", country_input

    # Match by name in COUNTRY_CODES
    for code, (name, flag) in COUNTRY_CODES.items():
        if name.lower() == country_input.lower():
            return flag, name

    # Match by name in ISO_TO_FLAG
    for iso, (name, flag) in ISO_TO_FLAG.items():
        if name.lower() == country_input.lower():
            return flag, name

    return "🌍", country_input

# ============================================
# DATABASE FUNCTIONS
# ============================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        country_code TEXT,
        assigned_numbers TEXT,
        assigned_timestamps TEXT,
        is_banned INTEGER DEFAULT 0,
        private_combo_country TEXT DEFAULT NULL,
        assigned_service_id INTEGER,
        number_source TEXT DEFAULT 'api',
        otp_count INTEGER DEFAULT 0,
        join_date TEXT DEFAULT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS otp_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT,
        otp TEXT,
        full_message TEXT,
        timestamp TEXT,
        assigned_to INTEGER
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bot_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS force_sub_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_url TEXT UNIQUE NOT NULL,
        description TEXT DEFAULT '',
        enabled INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        emoji TEXT,
        enabled INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS otp_tracking (
        phone_number TEXT PRIMARY KEY,
        last_processed TEXT,
        assigned_at TEXT,
        processed_cache TEXT
    )''')

    c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('force_sub_channel', '')")
    c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('force_sub_enabled', '0')")

    default_services = [
        (1, "WhatsApp", "💬", 1),
        (2, "Telegram", "✈️", 1),
        (3, "Instagram", "📸", 1),
        (4, "TikTok", "🎵", 1),
        (5, "Facebook", "👍", 1),
        (6, "IMO", "💙", 1),
        (7, "ChatGPT", "🤖", 1),
        (8, "Google", "🔍", 1),
        (9, "Twitter/X", "🐦", 1),
        (10, "Snapchat", "👻", 1),
        (11, "Discord", "🎮", 1),
        (12, "Spotify", "🎧", 1),
        (13, "Amazon", "🛒", 1),
        (14, "Uber", "🚗", 1),
        (15, "PayPal", "💰", 1),
        (16, "Netflix", "🎬", 1),
        (17, "Microsoft", "💻", 1),
        (18, "Apple", "🍎", 1),
        (19, "LinkedIn", "💼", 1),
        (20, "Reddit", "🤡", 1),
    ]
    for sid, name, emoji, enabled in default_services:
        c.execute("INSERT OR IGNORE INTO services (id, name, emoji, enabled) VALUES (?, ?, ?, ?)",
                  (sid, name, emoji, enabled))

    # Update emojis for existing default services if they are empty
    for sid, name, emoji, enabled in default_services:
        c.execute("UPDATE services SET emoji = ? WHERE id = ? AND (emoji IS NULL OR emoji = '')",
                  (emoji, sid))
    c.execute("UPDATE services SET emoji = '📱' WHERE emoji IS NULL OR emoji = ''")

    for admin_id in DEFAULT_ADMIN_IDS:
        c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (admin_id,))

    c.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in c.fetchall()]

    if 'assigned_number' in cols and 'assigned_numbers' not in cols:
        c.execute("ALTER TABLE users RENAME COLUMN assigned_number TO assigned_numbers")
        c.execute("UPDATE users SET assigned_numbers = '[]' WHERE assigned_numbers IS NULL OR assigned_numbers = ''")
        c.execute("UPDATE users SET assigned_numbers = json_array(assigned_numbers) WHERE assigned_numbers IS NOT NULL AND assigned_numbers != '' AND assigned_numbers != '[]'")
        c.execute("PRAGMA table_info(users)")
        cols = [row[1] for row in c.fetchall()]

    if 'assigned_numbers' not in cols:
        c.execute("ALTER TABLE users ADD COLUMN assigned_numbers TEXT DEFAULT '[]'")
    if 'assigned_timestamps' not in cols:
        c.execute("ALTER TABLE users ADD COLUMN assigned_timestamps TEXT DEFAULT '[]'")
    if 'assigned_service_id' not in cols:
        c.execute("ALTER TABLE users ADD COLUMN assigned_service_id INTEGER")
    if 'number_source' not in cols:
        c.execute("ALTER TABLE users ADD COLUMN number_source TEXT DEFAULT 'api'")
    if 'otp_count' not in cols:
        c.execute("ALTER TABLE users ADD COLUMN otp_count INTEGER DEFAULT 0")
    if 'join_date' not in cols:
        c.execute("ALTER TABLE users ADD COLUMN join_date TEXT DEFAULT NULL")

    cleanup_duplicate_services()
    
    conn.commit()
    conn.close()
    print("✅ Database initialized & migrated")

def cleanup_duplicate_services():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT LOWER(TRIM(name)) as name_lower, MIN(id) as keep_id
            FROM services
            GROUP BY LOWER(TRIM(name))
            HAVING COUNT(*) > 1
        """)
        duplicates = c.fetchall()
        for dup in duplicates:
            name_lower, keep_id = dup
            c.execute("""
                DELETE FROM services 
                WHERE LOWER(TRIM(name)) = ? AND id != ?
            """, (name_lower, keep_id))
            print(f"✅ Cleaned duplicate services for: {name_lower}")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[!] Cleanup error: {e}")

init_db()

# ============================================
# GET SETTINGS FROM DB
# ============================================

def get_setting(key, default=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return default

def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def refresh_settings():
    global BOT_NAME, CHANNEL_USERNAME, OWNER_USERNAME, REFRESH_INTERVAL, AUTO_EXPIRE_MINUTES, NUMBERS_PER_USER
    global OTP_GROUP_LINK, SUPPORT_LINK, BOT_PANEL_LINK, DEVELOPER_LINK, DEVELOPER_DISPLAY_NAME
    BOT_NAME = get_setting('bot_name', 'Apex Number Panel')
    CHANNEL_USERNAME = get_setting('channel_username', '@ZeroFlux02')
    OWNER_USERNAME = get_setting('owner_username', '@ApexVora')
    REFRESH_INTERVAL = int(get_setting('refresh_interval', '3'))
    AUTO_EXPIRE_MINUTES = int(get_setting('auto_expire_minutes', '20'))
    NUMBERS_PER_USER = int(get_setting('numbers_per_user', '3'))
    OTP_GROUP_LINK = get_setting('otp_group_link', 'https://t.me/+VYISBBggOBIxNzk1')
    SUPPORT_LINK = get_setting('support_link', 'https://t.me/ApexVora')
    BOT_PANEL_LINK = get_setting('bot_panel_link', 'https://t.me/ApexNumberPanelBot?start=start')
    DEVELOPER_LINK = get_setting('developer_link', 'https://t.me/ApexVora')
    DEVELOPER_DISPLAY_NAME = get_setting('developer_display_name', '𓂃❛ ⟶𝐀ᴘᴇx𝐕ᴏʀᴀ❜ 🌙⤹🌸')

refresh_settings()

# ============================================
# OTP TRACKING FUNCTIONS
# ============================================

def get_number_state(phone):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT last_processed, assigned_at, processed_cache FROM otp_tracking WHERE phone_number=?", (phone,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "last_processed": row[0],
            "assigned_at": row[1],
            "processed_cache": json.loads(row[2]) if row[2] else []
        }
    return None

def upsert_number_state(phone, last_processed=None, assigned_at=None, processed_cache=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    existing = get_number_state(phone)
    if existing:
        last_processed = last_processed or existing.get("last_processed")
        assigned_at = assigned_at if assigned_at is not None else existing.get("assigned_at")
        processed_cache = processed_cache if processed_cache is not None else existing.get("processed_cache")
    else:
        last_processed = last_processed or None
        assigned_at = assigned_at if assigned_at is not None else None
        processed_cache = processed_cache or []
    
    c.execute("""REPLACE INTO otp_tracking (phone_number, last_processed, assigned_at, processed_cache)
                 VALUES (?, ?, ?, ?)""",
              (phone, last_processed, assigned_at, json.dumps(processed_cache)))
    conn.commit()
    conn.close()

def clear_number_state(phone):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM otp_tracking WHERE phone_number=?", (phone,))
    conn.commit()
    conn.close()

def increment_user_otp_count(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET otp_count = otp_count + 1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_top_users(limit=15):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name, otp_count FROM users WHERE otp_count > 0 ORDER BY otp_count DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

# ============================================
# SERVICE FUNCTIONS
# ============================================

def get_services(enabled_only=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if enabled_only:
        c.execute("SELECT id, name, emoji, enabled FROM services WHERE enabled=1 ORDER BY name")
    else:
        c.execute("SELECT id, name, emoji, enabled FROM services ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return rows

def get_service(service_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, emoji, enabled FROM services WHERE id=?", (service_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_service_by_name(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, emoji, enabled FROM services WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))", (name,))
    row = c.fetchone()
    conn.close()
    return row

def add_service(name, emoji):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO services (name, emoji, enabled) VALUES (?, ?, 1)", (name.strip(), emoji.strip()))
    conn.commit()
    conn.close()

def delete_service(service_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM services WHERE id=?", (service_id,))
    conn.commit()
    conn.close()
    return True, 0

def toggle_service(service_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE services SET enabled = 1 - enabled WHERE id=?", (service_id,))
    conn.commit()
    conn.close()

# ============================================
# USER DATABASE FUNCTIONS
# ============================================

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        row = list(row)
        if row[5] and isinstance(row[5], str):
            try:
                row[5] = json.loads(row[5]) if row[5] else []
            except Exception as e:
                print(f"[!] Error parsing assigned_numbers: {e}")
                row[5] = []
        if row[6] and isinstance(row[6], str):
            try:
                row[6] = json.loads(row[6]) if row[6] else []
            except Exception as e:
                print(f"[!] Error parsing assigned_timestamps: {e}")
                row[6] = []
    return row

def save_user(user_id, username="", first_name="", last_name="", country_code=None, assigned_numbers=None, assigned_timestamps=None, private_combo_country=None, assigned_service_id=None, number_source='api', otp_count=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    existing = get_user(user_id)
    join_date = None
    if existing:
        if country_code is None:
            country_code = existing[4]
        if assigned_numbers is None:
            assigned_numbers = existing[5]
        if assigned_timestamps is None:
            assigned_timestamps = existing[6] if len(existing) > 6 else []
        if private_combo_country is None:
            private_combo_country = existing[7]
        if assigned_service_id is None:
            assigned_service_id = existing[8]
        if number_source is None:
            number_source = existing[9] if len(existing) > 9 else 'api'
        if otp_count is None:
            otp_count = existing[10] if len(existing) > 10 else 0
        if len(existing) > 11:
            join_date = existing[11]
    else:
        join_date = datetime.now().strftime("%Y-%m-%d")
    
    if assigned_numbers is None:
        assigned_numbers = []
    if assigned_timestamps is None:
        assigned_timestamps = []
    if isinstance(assigned_numbers, list):
        assigned_numbers = json.dumps(assigned_numbers)
    if isinstance(assigned_timestamps, list):
        assigned_timestamps = json.dumps(assigned_timestamps)
    
    c.execute("""
        REPLACE INTO users (user_id, username, first_name, last_name, country_code, assigned_numbers, assigned_timestamps, is_banned, private_combo_country, assigned_service_id, number_source, otp_count, join_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT is_banned FROM users WHERE user_id=?), 0), ?, ?, ?, ?, ?)
    """, (
        user_id,
        username,
        first_name,
        last_name,
        country_code,
        assigned_numbers,
        assigned_timestamps,
        user_id,
        private_combo_country,
        assigned_service_id,
        number_source,
        otp_count if otp_count is not None else 0,
        join_date
    ))
    conn.commit()
    conn.close()

def ban_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def is_banned(user_id):
    user = get_user(user_id)
    return user and user[7] == 1

def is_maintenance_mode():
    return not BOT_ACTIVE

def set_maintenance_mode(status):
    global BOT_ACTIVE
    BOT_ACTIVE = not status

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned=0")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def assign_numbers_to_user(user_id, numbers, service_id, source='api'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    existing = get_user(user_id)
    if existing and existing[5]:
        for num in existing[5]:
            np_release_number(num)
            clear_number_state(num)
    now = datetime.now().isoformat()
    timestamps = [now for _ in numbers]
    numbers_json = json.dumps(numbers)
    timestamps_json = json.dumps(timestamps)
    c.execute("UPDATE users SET assigned_numbers=?, assigned_timestamps=?, assigned_service_id=?, number_source=? WHERE user_id=?", 
              (numbers_json, timestamps_json, service_id, source, user_id))
    conn.commit()
    conn.close()
    for num in numbers:
        upsert_number_state(num, assigned_at=now)

def get_user_by_number(number):
    """Robust match: direct, suffix, or prefix (if OTP missing country code)"""
    if not number:
        return None
    number = str(number).replace('+', '').replace(' ', '').replace('-', '').strip()
    if not number:
        return None
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, assigned_numbers FROM users WHERE assigned_numbers IS NOT NULL AND assigned_numbers != '[]'")
    rows = c.fetchall()
    conn.close()
    
    for uid, nums_json in rows:
        try:
            if not nums_json:
                continue
            nums = json.loads(nums_json)
            # Handle double-encoded JSON or single string
            if isinstance(nums, str):
                try:
                    nums = json.loads(nums)
                except Exception:
                    nums = [nums]
            if not isinstance(nums, list):
                nums = [nums]
            
            for stored in nums:
                if not stored:
                    continue
                stored_clean = str(stored).replace('+', '').replace(' ', '').replace('-', '').strip()
                if not stored_clean:
                    continue
                if stored_clean == number:
                    return uid
                if number.endswith(stored_clean):
                    return uid
                if stored_clean.endswith(number):
                    return uid
        except Exception as e:
            print(f"[!] Error in get_user_by_number for uid {uid}: {e}")
            continue
    return None

def log_otp(number, otp, full_message, assigned_to=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO otp_logs (number, otp, full_message, timestamp, assigned_to) VALUES (?, ?, ?, ?, ?)",
              (number, otp, full_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), assigned_to))
    log_id = c.lastrowid
    conn.commit()
    conn.close()
    return log_id

def update_number_timestamp(user_id, number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT assigned_numbers, assigned_timestamps FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row:
        numbers = json.loads(row[0]) if row[0] else []
        timestamps = json.loads(row[1]) if row[1] else []
        if number in numbers:
            idx = numbers.index(number)
            timestamps[idx] = datetime.now().isoformat()
            c.execute("UPDATE users SET assigned_timestamps=? WHERE user_id=?", (json.dumps(timestamps), user_id))
            conn.commit()
    conn.close()

def release_single_number(user_id, number):
    np_release_number(number)
    clear_number_state(number)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT assigned_numbers, assigned_timestamps FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row:
        numbers = json.loads(row[0]) if row[0] else []
        timestamps = json.loads(row[1]) if row[1] else []
        if number in numbers:
            idx = numbers.index(number)
            numbers.pop(idx)
            if timestamps and idx < len(timestamps):
                timestamps.pop(idx)
            c.execute("UPDATE users SET assigned_numbers=?, assigned_timestamps=? WHERE user_id=?", 
                      (json.dumps(numbers), json.dumps(timestamps), user_id))
            conn.commit()
    conn.close()

def release_all_numbers(user_id):
    user = get_user(user_id)
    if user and user[5]:
        for num in user[5]:
            np_release_number(num)
            clear_number_state(num)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_numbers='[]', assigned_timestamps='[]', assigned_service_id=NULL WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def release_all_numbers_global():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, assigned_numbers FROM users WHERE assigned_numbers IS NOT NULL AND assigned_numbers != '[]'")
    rows = c.fetchall()
    total = 0
    errors = 0
    for uid, nums_json in rows:
        try:
            nums = json.loads(nums_json) if nums_json else []
            for num in nums:
                if np_release_number(num):
                    total += 1
                    clear_number_state(num)
                else:
                    errors += 1
        except Exception as e:
            print(f"[!] Error releasing numbers for user {uid}: {e}")
            errors += 1
    c.execute("UPDATE users SET assigned_numbers='[]', assigned_timestamps='[]', assigned_service_id=NULL")
    conn.commit()
    conn.close()
    return total, errors

def get_user_info(user_id):
    return get_user(user_id)

def get_otp_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM otp_logs")
    logs = c.fetchall()
    conn.close()
    return logs

# ============================================
# NUMBER PANEL API WRAPPER FUNCTIONS
# ============================================

def np_api_request(method, endpoint, params=None, data=None):
    url = f"{NUMBERPANEL_BASE_URL}{endpoint}"
    try:
        if method.upper() == 'GET':
            resp = _np_session.get(url, params=params, timeout=NUMBERPANEL_TIMEOUT)
        elif method.upper() == 'POST':
            resp = _np_session.post(url, json=data, timeout=NUMBERPANEL_TIMEOUT)
        else:
            return None
        if resp.status_code != 200:
            print(f"[!] API Error {resp.status_code}: {resp.text[:200]}")
            return {"success": False, "error": f"HTTP {resp.status_code}"}
        return resp.json()
    except Exception as e:
        print(f"[!] API Request failed: {e}")
        return {"success": False, "error": str(e)}

def np_get_countries(service):
    now = time.time()
    if service in _countries_cache and now - _countries_cache_time.get(service, 0) < 45:
        return _countries_cache[service]
    params = {"service": service}
    resp = np_api_request('GET', '/api/countries', params=params)
    if resp and resp.get('success'):
        countries = resp.get('countries', [])
        _countries_cache[service] = countries
        _countries_cache_time[service] = now
        return countries
    return []

def np_get_services():
    now = time.time()
    if _services_cache["data"] is not None and now - _services_cache["time"] < 90:
        return _services_cache["data"]
    resp = np_api_request('GET', '/api/services')
    if resp and resp.get('success'):
        data = resp.get('services', [])
        _services_cache["data"] = data
        _services_cache["time"] = now
        return data
    return []

def np_get_stats_detailed(period="daily"):
    now = time.time()
    if period in _stats_cache and now - _stats_cache_time.get(period, 0) < 20:
        return _stats_cache[period]
    params = {"period": period}
    resp = np_api_request('GET', '/api/stats/detailed', params=params)
    if resp and resp.get('success'):
        _stats_cache[period] = resp
        _stats_cache_time[period] = now
        return resp
    return None

def np_request_number(service, country):
    data = {"service": service, "country": country}
    resp = np_api_request('POST', '/api/request_number', data=data)
    if resp and resp.get('success'):
        number = resp.get('number')
        if number:
            return number
    return None

def np_release_number(number):
    if not number:
        return True
    data = {"number": number}
    resp = np_api_request('POST', '/api/release_number', data=data)
    return resp and resp.get('success', False)

def np_get_latest_otp(number=None):
    params = {}
    if number:
        params["number"] = number
    resp = np_api_request('GET', '/api/latest_otp', params=params)
    if resp and resp.get('success'):
        return resp.get('otp_code')
    return None

def np_get_otp_list(count=200):
    params = {"count": count}
    resp = np_api_request('GET', '/api/otp', params=params)
    if resp and isinstance(resp, list):
        return resp
    print(f"[!] /api/otp returned unexpected format: {type(resp)}")
    return []

def np_get_my_numbers():
    resp = np_api_request('GET', '/api/my_numbers')
    if resp and resp.get('success'):
        numbers = resp.get('numbers')
        if numbers is None:
            return []
        if isinstance(numbers, list):
            return numbers
    return []

# ============================================
# ADMIN MANAGEMENT
# ============================================

def get_admin_ids():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM admins")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_admin(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def is_admin(user_id):
    return user_id in get_admin_ids()

# ============================================
# FORCE SUBSCRIPTION FUNCTIONS
# ============================================

def get_all_force_sub_channels(enabled_only=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if enabled_only:
        c.execute("SELECT id, channel_url, description FROM force_sub_channels WHERE enabled = 1 ORDER BY id")
    else:
        c.execute("SELECT id, channel_url, description FROM force_sub_channels ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def add_force_sub_channel(channel_url, description=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO force_sub_channels (channel_url, description, enabled) VALUES (?, ?, 1)",
                  (channel_url.strip(), description.strip()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_force_sub_channel(channel_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM force_sub_channels WHERE id = ?", (channel_id,))
    changed = c.rowcount > 0
    conn.commit()
    conn.close()
    return changed

def toggle_force_sub_channel(channel_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE force_sub_channels SET enabled = 1 - enabled WHERE id = ?", (channel_id,))
    conn.commit()
    conn.close()

def force_sub_check(user_id):
    channels = get_all_force_sub_channels(True)
    if not channels:
        return True
    for _, url, _ in channels:
        try:
            channel_username = url
            if url.startswith("https://t.me/"):
                channel_username = "@" + url.split("/")[-1]
            elif url.startswith("@"):
                channel_username = url
            else:
                channel_username = f"@{url}"
            member = bot.get_chat_member(channel_username, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            print(f"[!] Force sub check error: {e}")
            return False
    return True

def force_sub_required_message():
    return (
        "🔐 𝗔𝗖𝗖𝗘𝗦𝗦 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗\n\n"
        "⚠️ 𝗬𝗼𝘂 𝗺𝘂𝘀𝘁 𝗷𝗼𝗶𝗻 𝗮𝗹𝗹 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁:\n\n"
        "🔁 𝗖𝗹𝗶𝗰𝗸 𝘁𝗵𝗲 𝗯𝘂𝘁𝘁𝗼𝗻𝘀 𝘁𝗼 𝗷𝗼𝗶𝗻, 𝘁𝗵𝗲𝗻 𝗰𝗹𝗶𝗰𝗸 ✅ 𝗩𝗲𝗿𝗶𝗳𝘆."
    )

def send_force_sub_required(cid):
    mk = force_sub_markup()
    if mk:
        try:
            bot.send_message(cid, force_sub_required_message(), parse_mode="HTML", reply_markup=mk, disable_web_page_preview=True)
        except Exception as e:
            print(f"[!] Error sending force sub message: {e}")

def force_sub_markup():
    channels = get_all_force_sub_channels(True)
    if not channels:
        return None
    markup = types.InlineKeyboardMarkup()
    for _, url, desc in channels:
        button_url = url
        if url.startswith("@"):
            button_url = f"https://t.me/{url[1:]}"
        elif not url.startswith("http"):
            button_url = f"https://t.me/{url}"
        text = f"📢 {desc}" if desc else "📢 Subscribe"
        markup.add(types.InlineKeyboardButton(text, url=button_url))
    markup.add(types.InlineKeyboardButton("✅ Verify", callback_data="check_sub"))
    return markup

# ============================================
# MAIN MENU (ReplyKeyboardMarkup)
# ============================================

def main_menu_markup(uid=None):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    btn1 = types.KeyboardButton("📱 Get Number")
    btn2 = types.KeyboardButton("📊 Live Traffic")
    btn3 = types.KeyboardButton("📈 Stats")
    btn4 = types.KeyboardButton("🏆 Leaderboard")
    btn5 = types.KeyboardButton("💬 Support")
    
    markup.row(btn1)
    markup.row(btn2, btn3)
    markup.row(btn4, btn5)
    
    if uid and is_admin(uid):
        btn_admin = types.KeyboardButton("🔐 Admin Panel")
        markup.row(btn_admin)
    
    return markup

def short_welcome(user_first_name):
    return f"""🌟 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 {BOT_NAME}, {user_first_name}!

𝗬𝗼𝘂𝗿 𝘂𝗹𝘁𝗶𝗺𝗮𝘁𝗲 𝗱𝗲𝘀𝘁𝗶𝗻𝗮𝘁𝗶𝗼𝗻 𝗳𝗼𝗿 𝘁𝗲𝗺𝗽𝗼𝗿𝗮𝗿𝘆 𝗽𝗵𝗼𝗻𝗲 𝗻𝘂𝗺𝗯𝗲𝗿𝘀 𝗮𝗻𝗱 𝗢𝗧𝗣 𝘃𝗲𝗿𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻.

🔹 📱 𝗚𝗲𝘁 𝗡𝘂𝗺𝗯𝗲𝗿 → Instantly receive a virtual number for any service.
🔹 📊 𝗟𝗶𝘃𝗲 𝗧𝗿𝗮𝗳𝗳𝗶𝗰 → See real‑time OTP activity across countries and services.
🔹 📈 𝗦𝘁𝗮𝘁𝘀 → View platform statistics and number availability.
🔹 🏆 𝗟𝗲𝗮𝗱𝗲𝗿𝗯𝗼𝗮𝗿𝗱 → Check who's the most active user.
🔹 💬 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 → Get help or contact the developer.

📌 Use the buttons below to get started."""

# ============================================
# UI HELPER FUNCTIONS
# ============================================

def format_number_card(numbers, country_name, flag, service_name, service_emoji, status="⏳ Waiting", source="api"):
    num_list = "\n".join([f"  • <code>+{num}</code>" for num in numbers])
    card = (
        f"📱 𝗡𝘂𝗺𝗯𝗲𝗿𝘀 𝗔𝘀𝘀𝗶𝗴𝗻𝗲𝗱  ( {len(numbers)} )\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"{num_list}\n"
        f"🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆  →  {flag} {country_name}\n"
        f"🔧 𝗦𝗲𝗿𝘃𝗶𝗰𝗲   →  {service_emoji or '📱'} {service_name}\n"
        f"⏳ 𝗦𝘁𝗮𝘁𝘂𝘀    →  {status}\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"📋 𝗧𝗮𝗽 𝘁𝗼 𝗰𝗼𝗽𝘆 𝗻𝘂𝗺𝗯𝗲𝗿\n"
        f"⏳ 𝗪𝗮𝗶𝘁𝗶𝗻𝗴 𝗳𝗼𝗿 𝗢𝗧𝗣… 𝗶𝗳 𝗿𝗲𝗰𝗲𝗶𝘃𝗲𝗱, 𝗮𝗽𝗽𝗲𝗮𝗿𝘀 𝗵𝗲𝗿𝗲."
    )
    return card

def progress_bar(progress, total, bar_length=10):
    """Return a progress bar string like '[██████░░░░] 60%'"""
    percent = (progress / total) * 100
    filled = int(bar_length * progress / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    return f"[{bar}] {int(percent)}%"

def loading_message(action="assigning", progress=0, total=NUMBERS_PER_USER):
    """Generate loading message with progress bar"""
    bar = progress_bar(progress, total)
    text = f"⏳ {action.capitalize()} numbers...\n{bar}"
    return text

# ============================================
# TELEGRAM BOT INITIALIZATION
# ============================================

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

# ============================================
# GLOBAL OTP DEDUPLICATION (persisted to disk)
# ============================================

SEEN_OTPS_FILE = "seen_otps.json"
processed_otps = set()

def load_seen_otps():
    global processed_otps
    try:
        if os.path.exists(SEEN_OTPS_FILE):
            with open(SEEN_OTPS_FILE, "r") as f:
                data = json.load(f)
                processed_otps = set(data)
                print(f"✅ Loaded {len(processed_otps)} previously seen OTPs from {SEEN_OTPS_FILE}")
        else:
            processed_otps = set()
            print("✅ No seen_otps.json found, starting fresh.")
    except Exception as e:
        print(f"[!] Error loading seen OTPs: {e}")
        processed_otps = set()

def save_seen_otps():
    try:
        items = list(processed_otps)
        if len(items) > 20000:
            items = items[-20000:]
        with open(SEEN_OTPS_FILE, "w") as f:
            json.dump(items, f)
    except Exception as e:
        print(f"[!] Error saving seen OTPs: {e}")

def add_to_seen(unique_id):
    processed_otps.add(unique_id)
    if len(processed_otps) % 50 == 0:
        threading.Thread(target=save_seen_otps, daemon=True).start()

# Load on startup
load_seen_otps()

# ============================================
# HELPER: Safe send with retry
# ============================================

def safe_send_message(chat_id, text, parse_mode="HTML", reply_markup=None, max_retries=3, disable_web_page_preview=False):
    for attempt in range(max_retries):
        try:
            return bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup, timeout=30, disable_web_page_preview=disable_web_page_preview)
        except telebot.apihelper.ApiTelegramException as e:
            if "429" in str(e) and attempt < max_retries - 1:
                retry_after = 5
                try:
                    match = re.search(r'retry after (\d+)', str(e))
                    if match:
                        retry_after = int(match.group(1)) + 1
                except Exception as ex:
                    print(f"[!] Error parsing retry: {ex}")
                time.sleep(retry_after)
                continue
            raise e
        except (ReadTimeout, ReadTimeoutError, ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"[!] Timeout, retrying in {wait_time}s... ({attempt+1}/{max_retries})")
                time.sleep(wait_time)
                continue
            raise e
    return None

def delete_message_safe(chat_id, message_id):
    try:
        if message_id:
            bot.delete_message(chat_id, message_id)
            return True
    except Exception as e:
        print(f"[!] Failed to delete message: {e}")
    return False

def safe_edit_message(chat_id, message_id, text, parse_mode="HTML", reply_markup=None):
    try:
        bot.edit_message_text(text, chat_id, message_id, parse_mode=parse_mode, reply_markup=reply_markup)
        return True
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" in str(e):
            return False
        else:
            raise e
    except Exception as e:
        print(f"[!] Error editing message: {e}")
        raise e

# ============================================
# BOT COMMAND HANDLERS
# ============================================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    try:
        uid = message.from_user.id
        cid = message.chat.id
        
        if is_maintenance_mode() and not is_admin(uid):
            safe_send_message(cid, "🔧 𝗕𝗼𝘁 𝘂𝗻𝗱𝗲𝗿 𝗺𝗮𝗶𝗻𝘁𝗲𝗻𝗮𝗻𝗰𝗲. 𝗧𝗿𝘆 𝗹𝗮𝘁𝗲𝗿.", parse_mode="HTML")
            return
        
        if is_banned(uid):
            safe_send_message(cid, "🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗯𝗮𝗻𝗻𝗲𝗱.", parse_mode="HTML")
            return
        
        if not force_sub_check(uid):
            send_force_sub_required(cid)
            return
        
        if not get_user(uid):
            save_user(uid, message.from_user.username or "", message.from_user.first_name or "", message.from_user.last_name or "")
        
        markup = main_menu_markup(uid)
        safe_send_message(cid, short_welcome(message.from_user.first_name or "User"), parse_mode="HTML", reply_markup=markup)
        
    except Exception as e:
        print(f"[!] Error in start_cmd: {e}")
        traceback.print_exc()
        try:
            safe_send_message(message.chat.id, "❌ An internal error occurred. Please try again later.")
        except Exception as ex:
            print(f"[!] Error sending error message: {ex}")

# ============================================
# REPLY KEYBOARD HANDLERS
# ============================================

@bot.message_handler(func=lambda m: m.text == "📱 Get Number")
def get_number_handler(message):
    try:
        uid = message.from_user.id
        cid = message.chat.id
        if is_banned(uid):
            return
        if not force_sub_check(uid):
            send_force_sub_required(cid)
            return
        
        services_from_api = np_get_services()
        if services_from_api:
            markup = types.InlineKeyboardMarkup(row_width=2)
            for svc in services_from_api:
                name = svc.get('name')
                count = svc.get('count', 0)
                if not name:
                    continue
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT id, emoji FROM services WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))", (name,))
                row = c.fetchone()
                conn.close()
                if row:
                    sid, emoji = row
                else:
                    emoji = "📱"
                    add_service(name, emoji)
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("SELECT id FROM services WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))", (name,))
                    result = c.fetchone()
                    if result:
                        sid = result[0]
                    else:
                        c.execute("INSERT INTO services (name, emoji, enabled) VALUES (?, ?, 1)", (name.strip(), emoji))
                        sid = c.lastrowid
                    conn.commit()
                    conn.close()
                if not emoji:
                    emoji = "📱"
                btn_text = f"{emoji} {name} — {count} 📦"
                markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"service_{sid}"))
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu"))
            safe_send_message(cid, "🌍 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝘀𝗲𝗿𝘃𝗶𝗰𝗲:", parse_mode="HTML", reply_markup=markup)
        else:
            services = get_services(True)
            markup = types.InlineKeyboardMarkup(row_width=2)
            for sid, name, emoji, _ in services:
                if not emoji:
                    emoji = "📱"
                markup.add(types.InlineKeyboardButton(f"{emoji} {name}", callback_data=f"service_{sid}"))
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu"))
            safe_send_message(cid, "🌍 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝘀𝗲𝗿𝘃𝗶𝗰𝗲:", parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        print(f"[!] Error in get_number_handler: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data == "back_to_main_menu")
def back_to_main_menu_cb(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        mid = call.message.message_id
        
        delete_message_safe(cid, mid)
        markup = main_menu_markup(uid)
        safe_send_message(cid, short_welcome("User"), parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"[!] Error in back_to_main_menu_cb: {e}")
        traceback.print_exc()

# ============================================
# LIVE TRAFFIC (now showing percentages)
# ============================================

@bot.message_handler(func=lambda m: m.text == "📊 Live Traffic")
def live_traffic_handler(message):
    try:
        uid = message.from_user.id
        cid = message.chat.id
        if is_banned(uid):
            return
        if not force_sub_check(uid):
            send_force_sub_required(cid)
            return
        stats = np_get_stats_detailed("daily")
        if not stats or not stats.get('success'):
            safe_send_message(cid, "❌ Failed to fetch live traffic data. Please try again later.", reply_markup=main_menu_markup(uid))
            return

        total_otp = stats.get('otp_count', 0)
        period_label = (stats.get('period') or 'daily').capitalize()
        msg = f"📊 𝗟𝗶𝘃𝗲 𝗧𝗿𝗮𝗳𝗳𝗶𝗰 ({period_label})\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"

        best_country = stats.get('best_country')
        if best_country:
            count = best_country.get('count', 0)
            pct = (count / total_otp * 100) if total_otp > 0 else 0
            c_name = best_country.get('name', 'Unknown')
            flag = best_country.get('flag', '🌍')
            if c_name and c_name != 'Unknown':
                f, _ = get_country_flag_and_name(c_name)
                if f and f != "🌍":
                    flag = f
            msg += f"🏆 𝗧𝗼𝗽 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {flag} {c_name} — {pct:.1f}%\n\n"

        top_hits = stats.get('top_hits', [])
        if top_hits:
            msg += "🔥 𝗧𝗼𝗽 𝗦𝗲𝗿𝘃𝗶𝗰𝗲/𝗖𝗼𝘂𝗻𝘁𝗿𝘆 𝗛𝗶𝘁𝘀:\n"
            for i, hit in enumerate(top_hits[:10], 1):
                service = hit.get('service', 'Unknown')
                country = hit.get('country', 'Unknown')
                # ✅ API sends 'percentage' directly
                pct = float(hit.get('percentage', 0) or 0)

                flag = "🌍"
                if country and country != 'Unknown':
                    f, _ = get_country_flag_and_name(country)
                    if f and f != "🌍":
                        flag = f

                service_emoji = "📱"
                svc = get_service_by_name(service)
                if svc:
                    service_emoji = svc[2] if svc[2] else "📱"

                msg += f"{i}. {service_emoji} {service} — {flag} {country} ({pct:.1f}%)\n"
        else:
            msg += "No traffic data available.\n"

        msg += f"\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_live_traffic"))
        mk.add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main_menu"))
        safe_send_message(cid, msg, parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in live_traffic_handler: {e}")
        safe_send_message(cid, "❌ Error fetching live traffic. Please try again later.", reply_markup=main_menu_markup(uid))

@bot.callback_query_handler(func=lambda c: c.data == "refresh_live_traffic")
def refresh_live_traffic_cb(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        mid = call.message.message_id
        stats = np_get_stats_detailed("daily")
        if not stats or not stats.get('success'):
            safe_edit_message(cid, mid, "❌ Failed to fetch live traffic data. Please try again later.", reply_markup=call.message.reply_markup)
            return

        total_otp = stats.get('otp_count', 0)
        period_label = (stats.get('period') or 'daily').capitalize()
        msg = f"📊 𝗟𝗶𝘃𝗲 𝗧𝗿𝗮𝗳𝗳𝗶𝗰 ({period_label})\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"

        best_country = stats.get('best_country')
        if best_country:
            count = best_country.get('count', 0)
            pct = (count / total_otp * 100) if total_otp > 0 else 0
            c_name = best_country.get('name', 'Unknown')
            flag = best_country.get('flag', '🌍')
            if c_name and c_name != 'Unknown':
                f, _ = get_country_flag_and_name(c_name)
                if f and f != "🌍":
                    flag = f
            msg += f"🏆 𝗧𝗼𝗽 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {flag} {c_name} — {pct:.1f}%\n\n"

        top_hits = stats.get('top_hits', [])
        if top_hits:
            msg += "🔥 𝗧𝗼𝗽 𝗦𝗲𝗿𝘃𝗶𝗰𝗲/𝗖𝗼𝘂𝗻𝘁𝗿𝘆 𝗛𝗶𝘁𝘀:\n"
            for i, hit in enumerate(top_hits[:10], 1):
                service = hit.get('service', 'Unknown')
                country = hit.get('country', 'Unknown')
                pct = float(hit.get('percentage', 0) or 0)

                flag = "🌍"
                if country and country != 'Unknown':
                    f, _ = get_country_flag_and_name(country)
                    if f and f != "🌍":
                        flag = f

                service_emoji = "📱"
                svc = get_service_by_name(service)
                if svc:
                    service_emoji = svc[2] if svc[2] else "📱"

                msg += f"{i}. {service_emoji} {service} — {flag} {country} ({pct:.1f}%)\n"
        else:
            msg += "No traffic data available.\n"

        msg += f"\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_live_traffic"))
        mk.add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main_menu"))
        safe_edit_message(cid, mid, msg, parse_mode="HTML", reply_markup=mk)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"[!] Error in refresh_live_traffic_cb: {e}")
        safe_edit_message(cid, mid, "❌ Error refreshing traffic.", reply_markup=call.message.reply_markup)

# ============================================
# STATS (showing daily)
# ============================================

@bot.message_handler(func=lambda m: m.text == "📈 Stats")
def stats_handler(message):
    try:
        uid = message.from_user.id
        cid = message.chat.id
        if is_banned(uid):
            return
        if not force_sub_check(uid):
            send_force_sub_required(cid)
            return
        stats = np_get_stats_detailed("daily")
        if not stats or not stats.get('success'):
            safe_send_message(cid, "❌ Failed to fetch stats. Please try again later.", reply_markup=main_menu_markup(uid))
            return

        otp_count = stats.get('otp_count', 0)
        available_numbers = stats.get('available_numbers', 0)
        countries_count = stats.get('countries_count', 0)
        services_count = stats.get('services_count', 0)
        period_label = (stats.get('period') or 'daily').capitalize()

        best_country = stats.get('best_country')
        if best_country:
            c_name = best_country.get('name', 'N/A')
            flag = best_country.get('flag', '🌍')
            if c_name and c_name != 'N/A':
                f, _ = get_country_flag_and_name(c_name)
                if f and f != "🌍":
                    flag = f
            best_country_str = f"{flag} {c_name} ({best_country.get('count', 0)})"
        else:
            best_country_str = "N/A"

        msg = (
            f"📈 𝗣𝗹𝗮𝘁𝗳𝗼𝗿𝗺 𝗦𝘁𝗮𝘁𝗶𝘀𝘁𝗶𝗰𝘀 ({period_label})\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            f"🔢 𝗧𝗼𝘁𝗮𝗹 𝗢𝗧𝗣𝘀         →  <code>{otp_count}</code>\n"
            f"📞 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗡𝘂𝗺𝗯𝗲𝗿𝘀  →  <code>{available_numbers}</code>\n"
            f"🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝗶𝗲𝘀 𝗔𝗰𝘁𝗶𝘃𝗲   →  <code>{countries_count}</code>\n"
            f"🔧 𝗦𝗲𝗿𝘃𝗶𝗰𝗲𝘀          →  <code>{services_count}</code>\n"
            f"🏆 𝗧𝗼𝗽 𝗖𝗼𝘂𝗻𝘁𝗿𝘆       →  {best_country_str}\n"
            f"\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        )
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats"))
        mk.add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main_menu"))
        safe_send_message(cid, msg, parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in stats_handler: {e}")
        safe_send_message(cid, "❌ Error fetching stats. Please try again later.", reply_markup=main_menu_markup(uid))

@bot.callback_query_handler(func=lambda c: c.data == "refresh_stats")
def refresh_stats_cb(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        mid = call.message.message_id
        stats = np_get_stats_detailed("daily")
        if not stats or not stats.get('success'):
            safe_edit_message(cid, mid, "❌ Failed to fetch stats. Please try again later.", reply_markup=call.message.reply_markup)
            return

        otp_count = stats.get('otp_count', 0)
        available_numbers = stats.get('available_numbers', 0)
        countries_count = stats.get('countries_count', 0)
        services_count = stats.get('services_count', 0)
        period_label = (stats.get('period') or 'daily').capitalize()

        best_country = stats.get('best_country')
        if best_country:
            c_name = best_country.get('name', 'N/A')
            flag = best_country.get('flag', '🌍')
            if c_name and c_name != 'N/A':
                f, _ = get_country_flag_and_name(c_name)
                if f and f != "🌍":
                    flag = f
            best_country_str = f"{flag} {c_name} ({best_country.get('count', 0)})"
        else:
            best_country_str = "N/A"

        msg = (
            f"📈 𝗣𝗹𝗮𝘁𝗳𝗼𝗿𝗺 𝗦𝘁𝗮𝘁𝗶𝘀𝘁𝗶𝗰𝘀 ({period_label})\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            f"🔢 𝗧𝗼𝘁𝗮𝗹 𝗢𝗧𝗣𝘀         →  <code>{otp_count}</code>\n"
            f"📞 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗡𝘂𝗺𝗯𝗲𝗿𝘀  →  <code>{available_numbers}</code>\n"
            f"🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝗶𝗲𝘀 𝗔𝗰𝘁𝗶𝘃𝗲   →  <code>{countries_count}</code>\n"
            f"🔧 𝗦𝗲𝗿𝘃𝗶𝗰𝗲𝘀          →  <code>{services_count}</code>\n"
            f"🏆 𝗧𝗼𝗽 𝗖𝗼𝘂𝗻𝘁𝗿𝘆       →  {best_country_str}\n"
            f"\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        )
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats"))
        mk.add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main_menu"))
        safe_edit_message(cid, mid, msg, parse_mode="HTML", reply_markup=mk)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"[!] Error in refresh_stats_cb: {e}")
        safe_edit_message(cid, mid, "❌ Error refreshing stats.", reply_markup=call.message.reply_markup)

# ============================================
# LEADERBOARD (unchanged)
# ============================================

@bot.message_handler(func=lambda m: m.text == "🏆 Leaderboard")
def leaderboard_handler(message):
    try:
        uid = message.from_user.id
        cid = message.chat.id
        if is_banned(uid):
            return
        if not force_sub_check(uid):
            send_force_sub_required(cid)
            return
        top_users = get_top_users(15)
        if not top_users:
            safe_send_message(cid, "🏆 No OTP activity yet. Be the first!", reply_markup=main_menu_markup(uid))
            return
        
        msg = f"🏆 𝗟𝗲𝗮𝗱𝗲𝗿𝗯𝗼𝗮𝗿𝗱 (𝗧𝗼𝗽 𝟭𝟱)\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        for idx, (user_id, username, first_name, count) in enumerate(top_users, 1):
            # First name priority, fallback to username, then user_id
            display_name = first_name if first_name else (f"@{username}" if username else f"User {user_id}")
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            # HTML mention link
            mention = f'<a href="tg://user?id={user_id}">{display_name}</a>'
            msg += f"{medal} {mention} — {count} OTPs\n"
        
        msg += f"\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n👆 𝗧𝗮𝗽 𝗮 𝗻𝗮𝗺𝗲 𝘁𝗼 𝗼𝗽𝗲𝗻 𝗽𝗿𝗼𝗳𝗶𝗹𝗲"
        
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_leaderboard"))
        mk.add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main_menu"))
        safe_send_message(cid, msg, parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in leaderboard_handler: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data == "refresh_leaderboard")
def refresh_leaderboard_cb(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        mid = call.message.message_id
        top_users = get_top_users(15)
        if not top_users:
            safe_edit_message(cid, mid, "🏆 No OTP activity yet. Be the first!", reply_markup=call.message.reply_markup)
            return
        
        msg = f"🏆 𝗟𝗲𝗮𝗱𝗲𝗿𝗯𝗼𝗮𝗿𝗱 (𝗧𝗼𝗽 𝟭𝟱)\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        for idx, (user_id, username, first_name, count) in enumerate(top_users, 1):
            display_name = first_name if first_name else (f"@{username}" if username else f"User {user_id}")
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            mention = f'<a href="tg://user?id={user_id}">{display_name}</a>'
            msg += f"{medal} {mention} — {count} OTPs\n"
        
        msg += f"\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n👆 𝗧𝗮𝗽 𝗮 𝗻𝗮𝗺𝗲 𝘁𝗼 𝗼𝗽𝗲𝗻 𝗽𝗿𝗼𝗳𝗶𝗹𝗲"
        
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_leaderboard"))
        mk.add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main_menu"))
        safe_edit_message(cid, mid, msg, parse_mode="HTML", reply_markup=mk)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"[!] Error in refresh_leaderboard_cb: {e}")
        traceback.print_exc()

# ============================================
# SUPPORT (unchanged)
# ============================================

@bot.message_handler(func=lambda m: m.text == "💬 Support")
def support_handler(message):
    try:
        uid = message.from_user.id
        cid = message.chat.id
        if is_banned(uid):
            return
        if not force_sub_check(uid):
            send_force_sub_required(cid)
            return
        
        msg = (
            f"💬 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 𝗖𝗲𝗻𝘁𝗲𝗿\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            f"Welcome to the support section.\n\n"
            f"If you encounter any issues, have questions, or need assistance with the bot, please reach out to the developer directly.\n\n"
            f"👤 𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿: <a href='{DEVELOPER_LINK}'>{DEVELOPER_DISPLAY_NAME}</a>\n"
            f"📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: {CHANNEL_USERNAME}\n\n"
            f"You can also use the buttons below to contact the developer or refresh the main menu.\n"
            f"\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        )
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton(f"👤 {DEVELOPER_DISPLAY_NAME}", url=DEVELOPER_LINK))
        mk.add(types.InlineKeyboardButton("🔄 Main Menu", callback_data="back_to_main_menu"))
        safe_send_message(cid, msg, parse_mode="HTML", reply_markup=mk, disable_web_page_preview=True)
    except Exception as e:
        print(f"[!] Error in support_handler: {e}")
        traceback.print_exc()

# ============================================
# ADMIN PANEL (Reply Keyboard)
# ============================================

@bot.message_handler(func=lambda m: m.text == "🔐 Admin Panel")
def admin_panel_reply(message):
    try:
        uid = message.from_user.id
        if not is_admin(uid):
            safe_send_message(message.chat.id, "⛔ Access denied.")
            return
        mk = admin_menu()
        safe_send_message(message.chat.id, f"🔐 𝗔𝗱𝗺𝗶𝗻 𝗣𝗮𝗻𝗲𝗹\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in admin_panel_reply: {e}")
        traceback.print_exc()

# ============================================
# EXISTING SERVICE SELECTION FLOW
# ============================================

@bot.callback_query_handler(func=lambda c: c.data == "back_to_services")
def back_to_services_cb(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        mid = call.message.message_id
        
        delete_message_safe(cid, mid)
        markup = main_menu_markup(uid)
        safe_send_message(cid, short_welcome("User"), parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"[!] Error in back_to_services_cb: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data.startswith("service_") and not c.data.startswith("service_toggle_") and not c.data.startswith("service_delete_") and not c.data.startswith("service_add"))
def service_selected(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        mid = call.message.message_id
        if is_banned(uid):
            return
        if not force_sub_check(uid):
            delete_message_safe(cid, mid)
            send_force_sub_required(cid)
            return
        try:
            sid = int(call.data.split("_")[1])
        except Exception as e:
            print(f"[!] Error parsing service id: {e}")
            return
        service = get_service(sid)
        if not service:
            bot.answer_callback_query(call.id, "❌ Service not found")
            return
        service_name = service[1]
        countries = np_get_countries(service_name)
        if not countries:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu"))
            delete_message_safe(cid, mid)
            safe_send_message(cid, "❌ No countries available for this service. Please try again later.", reply_markup=markup, parse_mode="HTML")
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        for country in countries:
            cname = country.get('name', 'Unknown')
            count = country.get('count', 0)
            flag, full_name = get_country_flag_and_name(cname)
            display_name = full_name if full_name else cname
            markup.add(types.InlineKeyboardButton(f"{flag} {display_name} — {count} 📦", callback_data=f"country_{sid}_{cname}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu"))
        delete_message_safe(cid, mid)
        safe_send_message(cid, f"🌍 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗖𝗼𝘂𝗻𝘁𝗿𝗶𝗲𝘀 𝗳𝗼𝗿 {service[1]}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        print(f"[!] Error in service_selected: {e}")
        traceback.print_exc()

# ============================================
# COUNTRY SELECTION WITH PROGRESS BAR
# ============================================

@bot.callback_query_handler(func=lambda c: c.data.startswith("country_"))
def country_cb(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        mid = call.message.message_id
        if is_banned(uid):
            return
        if not force_sub_check(uid):
            delete_message_safe(cid, mid)
            send_force_sub_required(cid)
            return
        parts = call.data.split("_")
        sid = int(parts[1])
        country_name = "_".join(parts[2:]).replace("_", " ")
        service = get_service(sid)
        if not service:
            bot.answer_callback_query(call.id, "❌ Service not found")
            return
        service_name = service[1]

        # Delete the country selection message
        delete_message_safe(cid, mid)

        # Send initial loading message
        loading_msg = safe_send_message(cid, loading_message("assigning", 0, NUMBERS_PER_USER), parse_mode="HTML")
        if not loading_msg:
            return
        load_msg_id = loading_msg.message_id

        # Request numbers with progress updates
        numbers = []
        for i in range(NUMBERS_PER_USER):
            num = np_request_number(service_name, country_name)
            if num:
                numbers.append(num.replace('+', ''))
            # Update progress bar (even if failed, we still count)
            progress = i + 1
            safe_edit_message(cid, load_msg_id, loading_message("assigning", progress, NUMBERS_PER_USER), parse_mode="HTML")

        # After loop, if no numbers, show error
        if not numbers:
            safe_edit_message(cid, load_msg_id, "❌ Failed to get any numbers. Please try again or choose another country.",
                              reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main_menu")))
            return

        # Release old numbers and assign new ones
        release_all_numbers(uid)
        assign_numbers_to_user(uid, numbers, sid, source='api')

        flag, full_name = get_country_flag_and_name(country_name)
        display_country = full_name if full_name else country_name

        s_name = service[1]
        s_emoji = service[2] if service[2] else "📱"
        card = format_number_card(numbers, display_country, flag, s_name, s_emoji, "⏳ Waiting", source='api')

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(
            types.InlineKeyboardButton("🔄 Change & Delete", callback_data=f"change_num_{sid}_{country_name}"),
            types.InlineKeyboardButton("🌍 Change Country", callback_data=f"change_country_{sid}")
        )
        markup.row(
            types.InlineKeyboardButton("📢 OTP Group", url=OTP_GROUP_LINK),
            types.InlineKeyboardButton("👤 Support", url=SUPPORT_LINK)
        )
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data=f"back_to_country_{sid}"))

        safe_edit_message(cid, load_msg_id, card, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id, f"✅ {len(numbers)} numbers assigned")

    except Exception as e:
        print(f"[!] Error in country_cb: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data.startswith("change_num_"))
def change_num_cb(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        mid = call.message.message_id
        if is_banned(uid):
            return
        if not force_sub_check(uid):
            delete_message_safe(cid, mid)
            send_force_sub_required(cid)
            return
        parts = call.data.split("_")
        sid = int(parts[2])
        country_name = "_".join(parts[3:]).replace("_", " ")
        service = get_service(sid)
        if not service:
            bot.answer_callback_query(call.id, "❌ Service not found")
            return
        service_name = service[1]

        # Update to loading with progress
        safe_edit_message(cid, mid, loading_message("changing", 0, NUMBERS_PER_USER), parse_mode="HTML")

        # Release old numbers
        release_all_numbers(uid)

        # Request new numbers with progress
        numbers = []
        for i in range(NUMBERS_PER_USER):
            num = np_request_number(service_name, country_name)
            if num:
                numbers.append(num.replace('+', ''))
            progress = i + 1
            safe_edit_message(cid, mid, loading_message("changing", progress, NUMBERS_PER_USER), parse_mode="HTML")

        if not numbers:
            safe_edit_message(cid, mid, "❌ Failed to get new numbers", 
                              reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main_menu")))
            bot.answer_callback_query(call.id, "❌ Failed to get new numbers", show_alert=True)
            return

        assign_numbers_to_user(uid, numbers, sid, source='api')

        flag, full_name = get_country_flag_and_name(country_name)
        display_country = full_name if full_name else country_name

        s_name = service[1]
        s_emoji = service[2] if service[2] else "📱"
        card = format_number_card(numbers, display_country, flag, s_name, s_emoji, "⏳ Waiting", source='api')

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(
            types.InlineKeyboardButton("🔄 Change & Delete", callback_data=f"change_num_{sid}_{country_name}"),
            types.InlineKeyboardButton("🌍 Change Country", callback_data=f"change_country_{sid}")
        )
        markup.row(
            types.InlineKeyboardButton("📢 OTP Group", url=OTP_GROUP_LINK),
            types.InlineKeyboardButton("👤 Support", url=SUPPORT_LINK)
        )
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data=f"back_to_country_{sid}"))

        safe_edit_message(cid, mid, card, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id, f"✅ Numbers changed ({len(numbers)})")
    except Exception as e:
        print(f"[!] Error in change_num_cb: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data.startswith("change_country_"))
def change_country_cb(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        mid = call.message.message_id
        if is_banned(uid):
            return
        if not force_sub_check(uid):
            delete_message_safe(cid, mid)
            send_force_sub_required(cid)
            return
        sid = int(call.data.split("_")[2])
        # Release numbers with progress animation
        safe_edit_message(cid, mid, loading_message("changing country", 0, 1), parse_mode="HTML")
        release_all_numbers(uid)
        # Show progress after release
        time.sleep(0.5)
        safe_edit_message(cid, mid, loading_message("loading countries", 1, 1), parse_mode="HTML")
        service = get_service(sid)
        if not service:
            return
        service_name = service[1]
        countries = np_get_countries(service_name)
        if not countries:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_services"))
            safe_edit_message(cid, mid, "❌ No countries available.", reply_markup=markup, parse_mode="HTML")
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        for country in countries:
            cname = country.get('name', 'Unknown')
            count = country.get('count', 0)
            flag, full_name = get_country_flag_and_name(cname)
            display_name = full_name if full_name else cname
            markup.add(types.InlineKeyboardButton(f"{flag} {display_name} — {count} 📦", callback_data=f"country_{sid}_{cname}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_services"))
        safe_edit_message(cid, mid, f"🌍 𝗦𝗲𝗹𝗲𝗰𝘁 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 𝗳𝗼𝗿 {service[1]}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        print(f"[!] Error in change_country_cb: {e}")
        traceback.print_exc()

# ============================================
# Other callbacks unchanged
# ============================================

@bot.callback_query_handler(func=lambda c: c.data.startswith("back_to_country_"))
def back_to_country_cb(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        if is_banned(uid):
            return
        if not force_sub_check(uid):
            send_force_sub_required(cid)
            return
        sid = int(call.data.split("_")[3])
        fake_call = call
        fake_call.data = f"change_country_{sid}"
        change_country_cb(fake_call)
    except Exception as e:
        print(f"[!] Error in back_to_country_cb: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_sub_cb(call):
    try:
        if force_sub_check(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Verified", show_alert=True)
            delete_message_safe(call.message.chat.id, call.message.message_id)
            start_cmd(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Not subscribed", show_alert=True)
    except Exception as e:
        print(f"[!] Error in check_sub_cb: {e}")
        traceback.print_exc()

# ============================================
# ADMIN PANEL (Inline) - unchanged except safe_edit usage
# ============================================

def admin_menu():
    mk = types.InlineKeyboardMarkup()
    st = "🟢 Online" if not is_maintenance_mode() else "🔴 Maintenance"
    mk.add(types.InlineKeyboardButton(f"{st}", callback_data="toggle_maintenance"))
    mk.row(
        types.InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
        types.InlineKeyboardButton("📄 Report", callback_data="admin_full_report")
    )
    mk.row(
        types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("📨 To User", callback_data="admin_broadcast_user")
    )
    mk.row(
        types.InlineKeyboardButton("🚫 Ban", callback_data="admin_ban"),
        types.InlineKeyboardButton("✅ Unban", callback_data="admin_unban"),
        types.InlineKeyboardButton("👤 Info", callback_data="admin_user_info")
    )
    mk.row(
        types.InlineKeyboardButton("🔗 Force Sub", callback_data="admin_force_sub"),
        types.InlineKeyboardButton("➕ Add Admin", callback_data="admin_add_admin"),
        types.InlineKeyboardButton("➖ Remove Admin", callback_data="admin_remove_admin")
    )
    mk.row(
        types.InlineKeyboardButton("🗑️ Delete All Numbers", callback_data="admin_delete_all"),
        types.InlineKeyboardButton("⚙️ Config", callback_data="admin_config")
    )
    mk.row(
        types.InlineKeyboardButton("⚙️ Services", callback_data="admin_services")
    )
    mk.add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main_menu"))
    return mk

@bot.callback_query_handler(func=lambda c: c.data == "admin_panel")
def admin_panel_cb(call):
    try:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⚠️ Admins only", show_alert=True)
            return
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, f"🔐 𝗔𝗱𝗺𝗶𝗻 𝗣𝗮𝗻𝗲𝗹\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", parse_mode="HTML", reply_markup=admin_menu())
    except Exception as e:
        print(f"[!] Error in admin_panel_cb: {e}")
        traceback.print_exc()

# ============================================
# ADMIN CONFIGURATION (unchanged)
# ============================================

@bot.callback_query_handler(func=lambda c: c.data == "admin_config")
def admin_config_cb(call):
    try:
        if not is_admin(call.from_user.id):
            return
        mk = types.InlineKeyboardMarkup(row_width=1)
        mk.add(types.InlineKeyboardButton("📝 Bot Name", callback_data="config_bot_name"))
        mk.add(types.InlineKeyboardButton("📢 Channel", callback_data="config_channel"))
        mk.add(types.InlineKeyboardButton("👤 Owner", callback_data="config_owner"))
        mk.add(types.InlineKeyboardButton("⏱️ Refresh Interval", callback_data="config_refresh"))
        mk.add(types.InlineKeyboardButton("⏳ Auto-Expire (min)", callback_data="config_expire"))
        mk.add(types.InlineKeyboardButton("🔢 Numbers per User", callback_data="config_numbers"))
        mk.add(types.InlineKeyboardButton("🔗 OTP Group Link", callback_data="config_otp_group"))
        mk.add(types.InlineKeyboardButton("🔗 Support Link", callback_data="config_support"))
        mk.add(types.InlineKeyboardButton("🔗 Bot Panel Link", callback_data="config_bot_panel"))
        mk.add(types.InlineKeyboardButton("🔗 Developer Link", callback_data="config_dev_link"))
        mk.add(types.InlineKeyboardButton("👤 Developer Display Name", callback_data="config_dev_display"))
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, f"⚙️ 𝗕𝗼𝘁 𝗖𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗮𝘁𝗶𝗼𝗻\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\nSelect a setting to change:", parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in admin_config_cb: {e}")
        traceback.print_exc()

def config_set_step(call, key, prompt):
    try:
        if not is_admin(call.from_user.id):
            return
        user_states[call.from_user.id] = f"config_set_{key}"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_config"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, f"{prompt}\nCurrent: {get_setting(key, 'Not set')}", parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in config_set_step: {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("config_") and c.data != "admin_config")
def config_choice(call):
    key_map = {
        "config_bot_name": ("bot_name", "Send new Bot Name:"),
        "config_channel": ("channel_username", "Send new Channel Username (e.g., @channel):"),
        "config_owner": ("owner_username", "Send new Owner Username (e.g., @owner):"),
        "config_refresh": ("refresh_interval", "Send new Refresh Interval (seconds, integer):"),
        "config_expire": ("auto_expire_minutes", "Send new Auto-Expire Minutes (integer):"),
        "config_numbers": ("numbers_per_user", "Send new Numbers per User (integer):"),
        "config_otp_group": ("otp_group_link", "Send new OTP Group Link (URL):"),
        "config_support": ("support_link", "Send new Support Link (URL):"),
        "config_bot_panel": ("bot_panel_link", "Send new Bot Panel Link (URL):"),
        "config_dev_link": ("developer_link", "Send new Developer Link (URL):"),
        "config_dev_display": ("developer_display_name", "Send new Developer Display Name (text):"),
    }
    key, prompt = key_map.get(call.data, (None, None))
    if key:
        config_set_step(call, key, prompt)
    else:
        bot.answer_callback_query(call.id, "Invalid option")

@bot.message_handler(func=lambda m: isinstance(user_states.get(m.from_user.id), str) and user_states[m.from_user.id].startswith("config_set_"))
def config_set_value(msg):
    try:
        key = user_states[msg.from_user.id].replace("config_set_", "")
        value = msg.text.strip()
        if not value:
            safe_send_message(msg.chat.id, "❌ Value cannot be empty.")
            return
        if key in ["refresh_interval", "auto_expire_minutes", "numbers_per_user"]:
            try:
                value = int(value)
            except Exception as e:
                print(f"[!] Error converting value: {e}")
                safe_send_message(msg.chat.id, "❌ Please enter a valid integer.")
                return
        set_setting(key, str(value))
        refresh_settings()
        safe_send_message(msg.chat.id, f"✅ Setting updated successfully!\nNew value: {value}")
        del user_states[msg.from_user.id]
    except Exception as e:
        print(f"[!] Error in config_set_value: {e}")
        safe_send_message(msg.chat.id, f"❌ Error: {e}")
        del user_states[msg.from_user.id]

# ============================================
# SERVICE MANAGEMENT ADMIN HANDLERS (unchanged)
# ============================================

@bot.callback_query_handler(func=lambda c: c.data == "admin_services")
def services_menu(call):
    try:
        if not is_admin(call.from_user.id):
            return
        services = get_services(False)
        txt = f"⚙️ 𝗦𝗲𝗿𝘃𝗶𝗰𝗲 𝗠𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        mk = types.InlineKeyboardMarkup()
        for sid, name, emoji, enabled in services:
            emoji = emoji or "📱"
            status = "✅" if enabled else "❌"
            txt += f"{status} {emoji} {name} (ID:{sid})\n"
            mk.add(types.InlineKeyboardButton(f"{status} {emoji} {name}", callback_data=f"service_toggle_{sid}"))
            mk.add(types.InlineKeyboardButton(f"🗑️", callback_data=f"service_delete_{sid}"))
        mk.add(types.InlineKeyboardButton("➕ Add Service", callback_data="service_add"))
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, txt, parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in services_menu: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data.startswith("service_toggle_"))
def service_toggle(call):
    try:
        if not is_admin(call.from_user.id):
            return
        sid = int(call.data.split("_")[2])
        toggle_service(sid)
        bot.answer_callback_query(call.id, "✅ Toggled", show_alert=True)
        delete_message_safe(call.message.chat.id, call.message.message_id)
        services_menu(call)
    except Exception as e:
        print(f"[!] Error in service_toggle: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data.startswith("service_delete_"))
def service_delete(call):
    try:
        if not is_admin(call.from_user.id):
            return
        sid = int(call.data.split("_")[2])
        delete_service(sid)
        bot.answer_callback_query(call.id, "🗑️ Deleted", show_alert=True)
        delete_message_safe(call.message.chat.id, call.message.message_id)
        services_menu(call)
    except Exception as e:
        print(f"[!] Error in service_delete: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data == "service_add")
def service_add_step1(call):
    try:
        if not is_admin(call.from_user.id):
            return
        user_states[call.from_user.id] = "service_add_name"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_services"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, "Send the 𝗻𝗮𝗺𝗲 of the new service:", parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in service_add_step1: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "service_add_name")
def service_add_step2(msg):
    try:
        name = msg.text.strip()
        if not name:
            safe_send_message(msg.chat.id, "❌ Name cannot be empty.")
            return
        user_states[msg.from_user.id] = {"step": "service_add_emoji", "name": name}
        safe_send_message(msg.chat.id, "Now send the 𝗲𝗺𝗼𝗷𝗶 for this service (e.g., 💬, 🔍):", parse_mode="HTML")
    except Exception as e:
        print(f"[!] Error in service_add_step2: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: isinstance(user_states.get(m.from_user.id), dict) and user_states[m.from_user.id].get("step") == "service_add_emoji")
def service_add_step3(msg):
    try:
        data = user_states[msg.from_user.id]
        emoji = msg.text.strip()
        if not emoji:
            safe_send_message(msg.chat.id, "❌ Emoji cannot be empty.")
            return
        add_service(data["name"], emoji)
        safe_send_message(msg.chat.id, f"✅ Service {data['name']} {emoji} added successfully.", parse_mode="HTML")
        del user_states[msg.from_user.id]
    except Exception as e:
        print(f"[!] Error in service_add_step3: {e}")
        traceback.print_exc()

# ============================================
# FORCE SUB ADMIN (unchanged)
# ============================================

@bot.callback_query_handler(func=lambda c: c.data == "admin_force_sub")
def force_sub_menu_cb(call):
    try:
        if not is_admin(call.from_user.id):
            return
        chs = get_all_force_sub_channels(False)
        txt = f"⚙️ 𝗙𝗼𝗿𝗰𝗲 𝗦𝘂𝗯 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀: {len(chs)}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        mk = types.InlineKeyboardMarkup()
        for cid, url, desc in chs:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT enabled FROM force_sub_channels WHERE id=?", (cid,))
            en = cur.fetchone()[0]
            conn.close()
            st = "✅" if en else "❌"
            mk.add(types.InlineKeyboardButton(f"{st} {desc or url[:20]}", callback_data=f"edit_fc_{cid}"))
        mk.add(types.InlineKeyboardButton("➕ Add", callback_data="add_fc"))
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, txt, parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in force_sub_menu_cb: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data == "add_fc")
def add_fc_step1(call):
    try:
        if not is_admin(call.from_user.id):
            return
        user_states[call.from_user.id] = "add_fc_url"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_force_sub"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, "Send channel link (@ or https):", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in add_fc_step1: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "add_fc_url")
def add_fc_step2(msg):
    try:
        url = msg.text.strip()
        if url.startswith("https://t.me/"):
            pass
        elif url.startswith("@"):
            url = f"https://t.me/{url[1:]}"
        elif not url.startswith("http"):
            url = f"https://t.me/{url}"
        else:
            safe_send_message(msg.chat.id, "❌ Invalid link! Must be @channel or https://t.me/channel")
            return
        user_states[msg.from_user.id] = {"step": "add_fc_desc", "url": url}
        safe_send_message(msg.chat.id, "Enter description for the channel (or leave empty):")
    except Exception as e:
        print(f"[!] Error in add_fc_step2: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: isinstance(user_states.get(m.from_user.id), dict) and user_states[m.from_user.id].get("step") == "add_fc_desc")
def add_fc_step3(msg):
    try:
        data = user_states[msg.from_user.id]
        if add_force_sub_channel(data["url"], msg.text.strip()):
            safe_send_message(msg.chat.id, f"✅ Channel added\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
        else:
            safe_send_message(msg.chat.id, "❌ Already exists")
        del user_states[msg.from_user.id]
    except Exception as e:
        print(f"[!] Error in add_fc_step3: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data.startswith("edit_fc_"))
def edit_fc_cb(call):
    try:
        if not is_admin(call.from_user.id):
            return
        cid = int(call.data.split("_")[2])
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT channel_url, description, enabled FROM force_sub_channels WHERE id=?", (cid,))
        url, desc, en = cur.fetchone()
        conn.close()
        txt = f"𝗘𝗱𝗶𝘁 𝗖𝗵𝗮𝗻𝗻𝗲𝗹\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\nLink: {url}\nDesc: {desc or '-'}\nStatus: {'Enabled' if en else 'Disabled'}\n\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("✏️ Edit Desc", callback_data=f"edit_desc_{cid}"))
        mk.add(types.InlineKeyboardButton("❌ Disable" if en else "✅ Enable", callback_data=f"toggle_fc_{cid}"))
        mk.add(types.InlineKeyboardButton("🗑️ Delete", callback_data=f"del_fc_{cid}"))
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_force_sub"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, txt, parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in edit_fc_cb: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data.startswith("toggle_fc_"))
def toggle_fc_cb(call):
    try:
        cid = int(call.data.split("_")[2])
        toggle_force_sub_channel(cid)
        bot.answer_callback_query(call.id, "✅ Toggled", show_alert=True)
        delete_message_safe(call.message.chat.id, call.message.message_id)
        force_sub_menu_cb(call)
    except Exception as e:
        print(f"[!] Error in toggle_fc_cb: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data.startswith("del_fc_"))
def del_fc_cb(call):
    try:
        cid = int(call.data.split("_")[2])
        if delete_force_sub_channel(cid):
            bot.answer_callback_query(call.id, "✅ Deleted", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ Failed", show_alert=True)
        delete_message_safe(call.message.chat.id, call.message.message_id)
        force_sub_menu_cb(call)
    except Exception as e:
        print(f"[!] Error in del_fc_cb: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data.startswith("edit_desc_"))
def edit_desc_cb(call):
    try:
        cid = int(call.data.split("_")[2])
        user_states[call.from_user.id] = f"edit_desc_{cid}"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data=f"edit_fc_{cid}"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, "Send new description:", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in edit_desc_cb: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: isinstance(user_states.get(m.from_user.id), str) and user_states[m.from_user.id].startswith("edit_desc_"))
def edit_desc_final(msg):
    try:
        cid = int(user_states[msg.from_user.id].split("_")[2])
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE force_sub_channels SET description=? WHERE id=?", (msg.text.strip(), cid))
        conn.commit()
        conn.close()
        safe_send_message(msg.chat.id, f"✅ Updated\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    except Exception as e:
        print(f"[!] Error in edit_desc_final: {e}")
        safe_send_message(msg.chat.id, "❌ Error")
    del user_states[msg.from_user.id]

# ============================================
# ADMIN STATS & REPORT (unchanged)
# ============================================

@bot.callback_query_handler(func=lambda c: c.data == "admin_stats")
def stats_cb(call):
    try:
        if not is_admin(call.from_user.id):
            return
        users = len(get_all_users())
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE assigned_numbers IS NOT NULL AND assigned_numbers != '[]'")
        active_users = c.fetchone()[0]
        conn.close()
        otp = len(get_otp_logs())
        txt = f"📊 𝗦𝘁𝗮𝘁𝘀:\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n👥 Users: {users}\n📞 Active Users: {active_users}\n🔑 OTPs Logged: {otp}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, txt, reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in stats_cb: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data == "admin_full_report")
def report_cb(call):
    try:
        if not is_admin(call.from_user.id):
            return
        txt = "📊 Full Report\n" + "="*40 + "\n\n"
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        for u in cur.fetchall():
            st = "Banned" if u[7] else "Active"
            nums = json.loads(u[5]) if u[5] else []
            num_str = ", ".join(nums) if nums else "None"
            txt += f"ID: {u[0]} | @{u[1] or 'N/A'} | Numbers: {num_str} | {st}\n"
        txt += "\n" + "="*40 + "\n\n"
        cur.execute("SELECT * FROM otp_logs")
        for log in cur.fetchall():
            ui = get_user_info(log[5]) if log[5] else None
            tag = f"@{ui[1]}" if ui and ui[1] else f"ID:{log[5] or 'N/A'}"
            txt += f"Num: {log[1]} | OTP: {log[2]} | User: {tag} | Time: {log[4]}\n"
        conn.close()
        with open("report.txt", "w", encoding="utf-8") as f:
            f.write(txt)
        with open("report.txt", "rb") as f:
            bot.send_document(call.from_user.id, f)
        os.remove("report.txt")
        bot.answer_callback_query(call.id, "✅ Sent", show_alert=True)
    except Exception as e:
        print(f"[!] Error in report_cb: {e}")
        bot.answer_callback_query(call.id, f"❌ {e}", show_alert=True)

# ============================================
# ADMIN BAN/UNBAN/INFO (unchanged)
# ============================================

@bot.callback_query_handler(func=lambda c: c.data == "admin_ban")
def ban1(call):
    try:
        if not is_admin(call.from_user.id):
            return
        user_states[call.from_user.id] = "ban"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, f"Enter user ID:\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in ban1: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "ban")
def ban2(msg):
    try:
        uid = int(msg.text)
        ban_user(uid)
        release_all_numbers(uid)
        safe_send_message(msg.chat.id, f"✅ Banned {uid}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    except Exception as e:
        print(f"[!] Error in ban2: {e}")
        safe_send_message(msg.chat.id, "❌ Invalid")
    del user_states[msg.from_user.id]

@bot.callback_query_handler(func=lambda c: c.data == "admin_unban")
def unban1(call):
    try:
        if not is_admin(call.from_user.id):
            return
        user_states[call.from_user.id] = "unban"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, f"Enter user ID:\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in unban1: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "unban")
def unban2(msg):
    try:
        uid = int(msg.text)
        unban_user(uid)
        safe_send_message(msg.chat.id, f"✅ Unbanned {uid}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    except Exception as e:
        print(f"[!] Error in unban2: {e}")
        safe_send_message(msg.chat.id, "❌ Invalid")
    del user_states[msg.from_user.id]

@bot.callback_query_handler(func=lambda c: c.data == "admin_user_info")
def inf1(call):
    try:
        if not is_admin(call.from_user.id):
            return
        user_states[call.from_user.id] = "info"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, f"Enter user ID:\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in inf1: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "info")
def inf2(msg):
    try:
        uid = int(msg.text)
        u = get_user_info(uid)
        if not u:
            safe_send_message(msg.chat.id, "❌ Not found")
            return
        st = "Banned" if u[7] else "Active"
        nums = json.loads(u[5]) if u[5] else []
        num_str = ", ".join(nums) if nums else "None"
        txt = f"👤 𝗨𝘀𝗲𝗿 𝗜𝗻𝗳𝗼\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\nID: {u[0]}\n@: {u[1] or 'N/A'}\nName: {u[2]} {u[3]}\nNumbers: {num_str}\nStatus: {st}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        safe_send_message(msg.chat.id, txt, parse_mode="HTML")
    except Exception as e:
        print(f"[!] Error in inf2: {e}")
        safe_send_message(msg.chat.id, f"❌ {e}")
    del user_states[msg.from_user.id]

# ============================================
# ADD/REMOVE ADMIN (unchanged)
# ============================================

@bot.callback_query_handler(func=lambda c: c.data == "admin_add_admin")
def add_admin_cb(call):
    try:
        if not is_admin(call.from_user.id):
            return
        user_states[call.from_user.id] = "add_admin_wait"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, f"Send the user ID to add as admin:\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in add_admin_cb: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "add_admin_wait")
def add_admin_final(msg):
    try:
        uid = int(msg.text.strip())
        add_admin(uid)
        safe_send_message(msg.chat.id, f"✅ User {uid} is now an admin.\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    except Exception as e:
        print(f"[!] Error in add_admin_final: {e}")
        safe_send_message(msg.chat.id, "❌ Invalid user ID.")
    del user_states[msg.from_user.id]

@bot.callback_query_handler(func=lambda c: c.data == "admin_remove_admin")
def remove_admin_cb(call):
    try:
        if not is_admin(call.from_user.id):
            return
        user_states[call.from_user.id] = "remove_admin_wait"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, f"Send the user ID to remove from admin:\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in remove_admin_cb: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "remove_admin_wait")
def remove_admin_final(msg):
    try:
        uid = int(msg.text.strip())
        admins = get_admin_ids()
        if len(admins) == 1 and admins[0] == uid:
            safe_send_message(msg.chat.id, "⚠️ Cannot remove the only admin. Add another first.")
        else:
            remove_admin(uid)
            safe_send_message(msg.chat.id, f"✅ User {uid} is no longer an admin.\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    except Exception as e:
        print(f"[!] Error in remove_admin_final: {e}")
        safe_send_message(msg.chat.id, "❌ Invalid user ID.")
    del user_states[msg.from_user.id]

# ============================================
# BROADCAST FEATURE (unchanged)
# ============================================

@bot.callback_query_handler(func=lambda c: c.data == "admin_broadcast")
def broadcast_init(call):
    try:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⚠️ Admins only", show_alert=True)
            return
        user_states[call.from_user.id] = "broadcast_wait_content"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(
            call.message.chat.id,
            f"📢 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗠𝗲𝘀𝘀𝗮𝗴𝗲\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            "Send the content you want to broadcast to all users.\n"
            "You can send text, photo, video, document, etc.\n"
            "After sending, you will get a confirmation prompt.\n\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            parse_mode="HTML",
            reply_markup=mk
        )
    except Exception as e:
        print(f"[!] Error in broadcast_init: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "broadcast_wait_content")
def broadcast_content_received(msg):
    try:
        admin_id = msg.from_user.id
        user_states[admin_id] = {"step": "broadcast_confirm", "msg_id": msg.message_id, "chat_id": msg.chat.id}
        mk = types.InlineKeyboardMarkup()
        mk.row(
            types.InlineKeyboardButton("✅ Confirm Broadcast", callback_data="broadcast_confirm"),
            types.InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
        )
        safe_send_message(msg.chat.id, f"📢 You are about to broadcast this message to all users. Confirm or Cancel.\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in broadcast_content_received: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data == "broadcast_confirm")
def broadcast_confirm(call):
    try:
        admin_id = call.from_user.id
        state = user_states.get(admin_id)
        if not state or state.get("step") != "broadcast_confirm":
            bot.answer_callback_query(call.id, "❌ Session expired. Start again.")
            return
        msg_id = state["msg_id"]
        chat_id = state["chat_id"]
        users = get_all_users()
        if not users:
            bot.answer_callback_query(call.id, "❌ No users to broadcast.", show_alert=True)
            return
        delete_message_safe(call.message.chat.id, call.message.message_id)
        sent_msg = safe_send_message(call.message.chat.id, "⏳ Broadcasting... Please wait.")
        def broadcast_job():
            sent = 0
            failed = 0
            total = len(users)
            for uid in users:
                try:
                    bot.copy_message(uid, chat_id, msg_id)
                    sent += 1
                except Exception as e:
                    print(f"[!] Broadcast failed for {uid}: {e}")
                    failed += 1
                time.sleep(0.05)
            summary = f"📢 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n✅ Sent: {sent}\n❌ Failed: {failed}\n👥 Total Users: {total}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
            if sent_msg:
                delete_message_safe(call.message.chat.id, sent_msg.message_id)
            safe_send_message(admin_id, summary, parse_mode="HTML")
            if user_states.get(admin_id):
                del user_states[admin_id]
        threading.Thread(target=broadcast_job, daemon=True).start()
        bot.answer_callback_query(call.id, "✅ Broadcast started in background.")
    except Exception as e:
        print(f"[!] Error in broadcast_confirm: {e}")
        bot.answer_callback_query(call.id, f"❌ Error: {e}", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data == "broadcast_cancel")
def broadcast_cancel(call):
    try:
        admin_id = call.from_user.id
        if user_states.get(admin_id):
            del user_states[admin_id]
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, "❌ Broadcast cancelled.")
        bot.answer_callback_query(call.id, "Cancelled.")
    except Exception as e:
        print(f"[!] Error in broadcast_cancel: {e}")
        traceback.print_exc()

@bot.callback_query_handler(func=lambda c: c.data == "admin_broadcast_user")
def bcu1(call):
    try:
        if not is_admin(call.from_user.id):
            return
        user_states[call.from_user.id] = "bcu_id"
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        delete_message_safe(call.message.chat.id, call.message.message_id)
        safe_send_message(call.message.chat.id, f"Enter user ID:\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", reply_markup=mk)
    except Exception as e:
        print(f"[!] Error in bcu1: {e}")
        traceback.print_exc()

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "bcu_id")
def bcu2(msg):
    try:
        uid = int(msg.text)
        user_states[msg.from_user.id] = f"bcu_msg_{uid}"
        safe_send_message(msg.chat.id, f"Send message:\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    except Exception as e:
        print(f"[!] Error in bcu2: {e}")
        safe_send_message(msg.chat.id, "❌ Invalid")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, "").startswith("bcu_msg_"))
def bcu3(msg):
    try:
        uid = int(user_states[msg.from_user.id].split("_")[2])
        safe_send_message(uid, msg.text)
        safe_send_message(msg.chat.id, f"✅ Sent to {uid}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    except Exception as e:
        print(f"[!] Error in bcu3: {e}")
        safe_send_message(msg.chat.id, f"❌ {e}")
    del user_states[msg.from_user.id]

# ============================================
# OTP FUNCTIONS (unchanged)
# ============================================

def extract_otp_from_message(message):
    if not message:
        return None
    msg = ' '.join(message.split())
    patterns = [
        r'(?:code|kode|otp|pin|verification|verifikasi)?\s*[:\-]?\s*(\d{3}[\s\-]?\d{3})',
        r'(?:code|kode|otp|pin|verification|verifikasi)?\s*[:\-]?\s*(\d{4,8})',
        r'\b(\d{4,8})\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, msg, re.IGNORECASE)
        if match:
            raw = match.group(1)
            if len(raw) == 6 and raw[3] in (' ', '-'):
                return raw.replace(' ', '').replace('-', '')
            return raw.replace(' ', '').replace('-', '')
    return None

def get_country_info(num):
    num = num.replace("+", "").replace(" ", "")
    for code, (name, flag) in COUNTRY_CODES.items():
        if num.startswith(code):
            return name, flag
    return "Unknown", "🌍"

def mask_number_for_group(num: str) -> str:
    num = num.replace('+', '').strip()
    if len(num) <= 8:
        return num
    return num[:4] + '***' + num[-4:]

def delete_message_after_delay(chat_id, msg_id, delay=1800):
    time.sleep(delay)
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",
                     data={"chat_id": chat_id, "message_id": msg_id}, timeout=10)
    except Exception as e:
        print(f"[!] Error deleting message after delay: {e}")

def send_to_telegram_group(otp_code, country_name, flag, number, service_name, service_emoji, timestamp):
    masked_num = mask_number_for_group(number)
    masked_display = f"+{masked_num}"

    message = (
        f"📬 𝗡𝗲𝘄 𝗖𝗼𝗱𝗲 𝗥𝗲𝗰𝗲𝗶𝘃𝗲𝗱 ✨\n\n"
        f"🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆  →  {flag} {country_name}\n"
        f"📞 𝗡𝘂𝗺𝗯𝗲𝗿→ <code>{masked_display}</code>\n"
        f"🔧 𝗦𝗲𝗿𝘃𝗶𝗰𝗲  →  {service_emoji or '📱'} {service_name}\n"
        f"⏰ 𝗧𝗶𝗺𝗲     →  {timestamp}\n\n"
        f"🔐 𝗩𝗲𝗿𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻 𝗖𝗼𝗱𝗲 →  <code>{otp_code}</code>\n\n"
        f"📌 Tap the button below to copy the code."
    )

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    try:
        from telebot.types import CopyTextButton
        copy_btn = types.InlineKeyboardButton(f"📋 {otp_code}", copy_text=CopyTextButton(otp_code))
    except (ImportError, TypeError, AttributeError):
        copy_btn = types.InlineKeyboardButton(f"📋 {otp_code}", callback_data=f"copy_{otp_code}")
    
    bot_btn = types.InlineKeyboardButton("🤖 Bot Panel", url=BOT_PANEL_LINK)
    dev_btn = types.InlineKeyboardButton("👤 Developer", url=DEVELOPER_LINK)
    
    keyboard.add(copy_btn)
    keyboard.add(bot_btn, dev_btn)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        for attempt in range(3):
            try:
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "reply_markup": keyboard.to_json(),
                    "disable_web_page_preview": True
                }
                resp = requests.post(url, json=payload, timeout=30)
                if resp.status_code == 200:
                    print(f"[+] OTP feed sent to group: {chat_id}")
                    msg_id = resp.json()["result"]["message_id"]
                    threading.Thread(
                        target=delete_message_after_delay,
                        args=(chat_id, msg_id, 1800),
                        daemon=True
                    ).start()
                    break
                else:
                    print(f"[!] Failed to send to {chat_id}: {resp.status_code} - {resp.text}")
            except (ReadTimeout, ReadTimeoutError, ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < 2:
                    wait = (attempt + 1) * 3
                    print(f"[!] Timeout sending to group, retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                print(f"[!] Error sending to {chat_id}: {e}")
            except Exception as e:
                print(f"[!] Error sending to {chat_id}: {e}")
                traceback.print_exc()
                break

def send_otp_to_user_and_group(date_str, number, otp, service_name, api_service_name=None):
    cn, cf = get_country_info(number)
    uid = get_user_by_number(number)
    print(f"[DEBUG] OTP process: number={number}, otp={otp}, uid={uid}")
    log_otp(number, otp, "", uid)
    
    if uid:
        print(f"[+] Found user {uid} for number {number}")
        update_number_timestamp(uid, number)
        increment_user_otp_count(uid)
    else:
        print(f"[!] No user found for number {number}. Skipping private DM.")
    
    final_service_name = service_name
    final_service_emoji = "📱"
    
    if uid:
        user = get_user(uid)
        if user and user[8]:
            serv = get_service(user[8])
            if serv:
                final_service_name = serv[1]
                final_service_emoji = serv[2] if serv[2] else "📱"
    
    if (not final_service_name or final_service_name == "Unknown") and api_service_name:
        final_service_name = api_service_name
        final_service_emoji = "📱"
    
    if uid:
        try:
            private_msg = (
                f"🚀 𝑵𝒆𝒘 𝑶𝒕𝒑 𝑹𝒆𝒄𝒆𝒊𝒗𝒆𝒅 ✨\n\n"
                f"🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆  →  {cf} {cn}\n"
                f"📞 𝗡𝘂𝗺𝗯𝗲𝗿   →  <code>+{number}</code>\n"
                f"🔧 𝗦𝗲𝗿𝘃𝗶𝗰𝗲  →  {final_service_emoji} {final_service_name}\n"
                f"⏰ 𝗧𝗶𝗺𝗲     →  {date_str}\n\n"
                f"🔐 𝗢𝗧𝗣 𝗖𝗼𝗱𝗲 →  <code>{otp}</code>"
            )
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            try:
                from telebot.types import CopyTextButton
                copy_otp_btn = types.InlineKeyboardButton(f"📋 {otp}", copy_text=CopyTextButton(otp))
            except (ImportError, TypeError, AttributeError):
                copy_otp_btn = types.InlineKeyboardButton(f"📋 {otp}", callback_data=f"copy_{otp}")
            owner_btn = types.InlineKeyboardButton("👤 Owner", url=f"tg://user?id={DEFAULT_ADMIN_IDS[0]}")
            channel_btn = types.InlineKeyboardButton("📢 Channel", url=CHANNEL_USERNAME)
            keyboard.add(copy_otp_btn)
            keyboard.add(owner_btn, channel_btn)
            safe_send_message(uid, private_msg, reply_markup=keyboard, parse_mode="HTML")
            print(f"[+] OTP sent to user {uid}")
        except Exception as e:
            print(f"[!] Failed to send private OTP to {uid}: {e}")
            traceback.print_exc()

    send_to_telegram_group(otp, cn, cf, number, final_service_name, final_service_emoji, date_str)

@bot.callback_query_handler(func=lambda c: c.data.startswith("copy_"))
def copy_cb(call):
    try:
        code = call.data.split("_", 1)[1]
        bot.answer_callback_query(call.id, f"✅ Code: {code}", show_alert=True)
    except Exception as e:
        print(f"[!] Error in copy_cb: {e}")

# ============================================
# MAIN LOOP (with global OTP skip)
# ============================================

def main_loop():
    print("="*50)
    print(f"🚀 {BOT_NAME} RUNNING (Persistent OTP State)")
    print(f"📢 Channel: {CHANNEL_USERNAME}")
    print("="*50)

    errs = 0

    while True:
        try:
            otp_list = np_get_otp_list(count=200)
            if otp_list and isinstance(otp_list, list):
                new_otps = 0
                for entry in otp_list:
                    if not isinstance(entry, list) or len(entry) < 5:
                        continue

                    service_name = entry[0] if entry[0] else "Unknown"
                    phone = entry[1] if entry[1] else ""
                    full_message = entry[2] if entry[2] else ""
                    timestamp_str = entry[3] if entry[3] else ""
                    country_name = entry[4] if entry[4] else "Unknown"

                    if not phone or not full_message:
                        continue

                    phone = phone.replace('+', '').strip()
                    otp_code = extract_otp_from_message(full_message)
                    if not otp_code:
                        print(f"[!] Could not extract OTP from: {full_message[:50]}...")
                        continue

                    try:
                        if " ago" in timestamp_str:
                            otp_time = datetime.now()
                        else:
                            otp_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    except Exception as e:
                        print(f"[!] Error parsing timestamp: {timestamp_str} - {e}")
                        otp_time = datetime.now()

                    state = get_number_state(phone)
                    last_processed = None
                    assigned_at = None
                    cache = []
                    if state:
                        last_processed = state.get("last_processed")
                        assigned_at = state.get("assigned_at")
                        cache = state.get("processed_cache")

                    # 1. Check per-number cache
                    if last_processed:
                        try:
                            last_dt = datetime.fromisoformat(last_processed)
                        except ValueError:
                            last_dt = None
                        if last_dt and otp_time <= last_dt:
                            print(f"⏳ OLD OTP (per-number) {phone} {otp_time} <= {last_dt} - SKIPPED")
                            continue

                    if assigned_at:
    try:
        assigned_dt = datetime.fromisoformat(assigned_at)
    except ValueError:
        assigned_dt = None
    if assigned_dt:
        buffer_dt = assigned_dt - timedelta(minutes=5)
        if otp_time < buffer_dt:
            print(f"🔒 ASSIGNMENT FILTERED {phone} {otp_time} < {buffer_dt} - SKIPPED")
            continue
                    unique_key = f"{phone}_{otp_time.isoformat()}_{otp_code}"
                    
                    # 2. Check global set (persisted to disk)
                    if unique_key in processed_otps:
                        print(f"🔄 DUPLICATE (global) {phone} {otp_time} - SKIPPED")
                        continue

                    # 3. Check per-number cache (in case global missed)
                    if unique_key in cache:
                        print(f"🔄 DUPLICATE (cache) {phone} {otp_time} - SKIPPED")
                        continue

                    print(f"🆕 NEW OTP {phone} {otp_time} - SENDING")

                    try:
                        # Get service emoji for this OTP
                        service_emoji_final = "📱"
                        if service_name and service_name != "Unknown":
                            service_row = get_service_by_name(service_name)
                            if service_row:
                                service_emoji_final = service_row[2] if service_row[2] else "📱"
                        
                        send_otp_to_user_and_group(
                            timestamp_str,
                            phone,
                            otp_code,
                            service_name,
                            service_name
                        )
                        # Mark as seen globally
                        add_to_seen(unique_key)
                        # Also update per-number cache
                        cache.append(unique_key)
                        if len(cache) > 500:
                            cache = cache[-500:]
                        upsert_number_state(
                            phone,
                            last_processed=timestamp_str if "ago" not in timestamp_str else otp_time.isoformat(),
                            assigned_at=assigned_at,
                            processed_cache=cache
                        )
                        new_otps += 1
                    except Exception as e:
                        print(f"[!] Failed to send OTP for {phone}: {e}")
                        traceback.print_exc()

                if new_otps:
                    print(f"[+] New OTPs sent: {new_otps}")
            else:
                print("[!] /api/otp returned empty or invalid.")

            errs = 0
        except Exception as e:
            errs += 1
            print(f"[!] Main loop error: {e}")
            traceback.print_exc()
            if errs >= 5:
                print("[!] Too many errors, resetting...")
                errs = 0

        time.sleep(REFRESH_INTERVAL)

# ============================================
# AUTO-EXPIRE CHECKER (unchanged)
# ============================================

def auto_expire_checker():
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT user_id, assigned_numbers, assigned_timestamps FROM users WHERE assigned_numbers IS NOT NULL AND assigned_numbers != '[]'")
            rows = c.fetchall()
            conn.close()
            
            now = datetime.now()
            expire_minutes = AUTO_EXPIRE_MINUTES
            expired_count = 0
            
            for uid, nums_json, timestamps_json in rows:
                try:
                    numbers = json.loads(nums_json) if nums_json else []
                    timestamps = json.loads(timestamps_json) if timestamps_json else []
                    if len(numbers) != len(timestamps):
                        continue
                    if not numbers:
                        continue
                    oldest_time = min(datetime.fromisoformat(ts) for ts in timestamps)
                    if (now - oldest_time).total_seconds() > expire_minutes * 60:
                        release_all_numbers(uid)
                        try:
                            safe_send_message(
                                uid,
                                f"⏳ 𝗬𝗼𝘂𝗿 𝗮𝘀𝘀𝗶𝗴𝗻𝗲𝗱 𝗻𝘂𝗺𝗯𝗲𝗿𝘀 𝗵𝗮𝘃𝗲 𝗲𝘅𝗽𝗶𝗿𝗲𝗱.\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\nPlease use /start to assign new numbers.\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
                                parse_mode="HTML"
                            )
                            expired_count += len(numbers)
                            print(f"[+] Auto-expired {len(numbers)} numbers for user {uid}")
                        except Exception as e:
                            print(f"[!] Failed to send expiry message to {uid}: {e}")
                except Exception as e:
                    print(f"[!] Auto-expire error for user {uid}: {e}")
                    traceback.print_exc()
                    
            if expired_count > 0:
                print(f"[+] Auto-expired {expired_count} numbers")
                
        except Exception as e:
            print(f"[!] Auto-expire checker error: {e}")
            traceback.print_exc()
        
        time.sleep(60)

# ============================================
# RUN BOT
# ============================================

def run_bot():
    print("[*] Starting Telegram bot with infinity polling...")
    try:
        bot.remove_webhook()
        time.sleep(0.5)
        bot.get_me()
        bot.infinity_polling(timeout=20, long_polling_timeout=10, interval=0)
    except telebot.apihelper.ApiTelegramException as e:
        if "401" in str(e):
            print("❌ Invalid bot token! Please check BOT_TOKEN.")
        else:
            print(f"❌ Telegram API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print(f"""
    ╔════════════════════════╗
    ║    {BOT_NAME}   ║
    ║    Channel: {CHANNEL_USERNAME}  ║
    ║    Owner: {OWNER_USERNAME}     ║
    ╚════════════════════════╝
    """)
    
    try:
        bot.get_me()
    except telebot.apihelper.ApiTelegramException as e:
        if "401" in str(e):
            raise SystemExit("❌ Invalid bot token! Please check BOT_TOKEN.")
        else:
            raise SystemExit(f"❌ Telegram API error: {e}")
    
    auto_expire_thread = threading.Thread(target=auto_expire_checker, daemon=True)
    auto_expire_thread.start()
    
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    main_loop()