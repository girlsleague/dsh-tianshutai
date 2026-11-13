# -*- coding: utf-8 -*-
"""
天枢台服务端 v2.0
集成：八字排盘、紫微排盘、双模数据、化解锦囊、双人合盘API、档案管理、问命盘师
"""

import os
import sys
import json
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from lunar_python import Solar, Lunar

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import engine

ZIWEI_CLI_DIR = r"C:\Users\LH\.dsh\skills\ziwei-doushu\scripts"
if os.path.exists(ZIWEI_CLI_DIR):
    sys.path.append(ZIWEI_CLI_DIR)
    try:
        import ziwei_cli
    except Exception as e:
        ziwei_cli = None
else:
    ziwei_cli = None

PORT = int(os.environ.get("TIANSHU_PORT", "58765"))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")

os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(PROFILES_FILE):
    default_profiles = [
        {
            "id": "demo-001",
            "name": "某某 (截图示例盘)",
            "gender": "男",
            "calendar_type": "solar",
            "birth_solar": "2001-04-23 23:40",
            "city": "北京市 东城区",
            "lng": 116.422,
            "lat": 39.935,
            "true_solar_enabled": True,
            "note": "2001辛巳年标准盘",
            "createdAt": "2026-11-12T12:00:00"
        },
        {
            "id": "demo-002",
            "name": "刘红",
            "gender": "男",
            "calendar_type": "solar",
            "birth_solar": "1995-10-31 06:45",
            "city": "湖北 随州",
            "lng": 113.37,
            "lat": 31.71,
            "true_solar_enabled": True,
            "note": "乙亥 丙戌 乙未 己卯",
            "createdAt": "2026-11-12T12:05:00"
        },
        {
            "id": "demo-003",
            "name": "湖北鄂州女命",
            "gender": "女",
            "calendar_type": "solar",
            "birth_solar": "1990-10-09 06:00",
            "city": "湖北 鄂州",
            "lng": 114.89,
            "lat": 30.39,
            "true_solar_enabled": True,
            "note": "庚午 丙戌 丁未 癸卯",
            "createdAt": "2026-11-12T12:10:00"
        }
    ]
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(default_profiles, f, ensure_ascii=False, indent=2)

def generate_scenario_reading(bazi_data):
    pillars = bazi_data['pillars']
    strength = bazi_data['strength']
    me_wx = strength['me_wx']
    percentages = strength['percentages']
    score = strength['strength_score']
    shishen_dist = bazi_data['shishen_dist']
    
    has_piancai = any(s['name'] == '偏财' for s in shishen_dist[:4])
    has_zhengcai = any(s['name'] == '正财' for s in shishen_dist[:4])
    
    if has_piancai and score >= 35:
        wealth_type = "多元副业与敏锐商机型"
        wealth_summary = "你对市场和金钱嗅觉极强，不满足于死守一份工资，具有敏锐的商业洞察力和轻资产变现天赋。"
    elif has_zhengcai or score < 35:
        wealth_type = "稳健专业与长线复利型"
        wealth_summary = "你的正财根基比暴富偏财更稳健，宜在大平台、核心技术或专业壁垒领域深耕，口碑带来长久现金流。"
    else:
        wealth_type = "才艺技能转化为财富型"
        wealth_summary = "食伤生财，你的才华、创意、口才与独门手艺就是聚宝盆，靠输出作品和本事赚钱最安心从容。"

    wealth_details = {
        'capacity': "【财富体量上限】命局财气通门户，且有地支藏干支持，属于中产向上可攀登高净值的命造。但能否发大财取决于大运是否行到喜用神运（身弱逢印比，身旺逢财官）。若行逆运时，应以守为攻，以保全现金流为核心。",
        'first_bucket': "【第一桶金应期】通常在逢食伤生财或大运天干透出偏财的流年（如 24–28 岁或 34–38 岁阶段），往往通过一次关键项目操盘、新技能变现或抓住行业风口迎来财富的第一次跃升。",
        'partner_risk': "【合伙投资戒律】天干或地支见比肩劫财者，一生需严防‘因情破财’！切忌因为同学朋友情面合伙开店或借贷担保。合伙必须实行股权独立、财务日结，切勿混同私账。",
        'asset_strategy': "【资产配置指南】建议将流动收益的 40% 以上及时转换为抗风险的重资产（如核心城市不动产、黄金、稳健债券），防止偏财‘来得快去得也快’的耗散效应。"
    }

    careers = [
        {'wuxing': '木', 'fields': '教育培训、文化出版、农林医药、软硬件研发、创意策划', 'match_rate': 88 if me_wx in ['水','木'] else 72, 'role': '适合：教研骨干、主创主编、产品架构师'},
        {'wuxing': '火', 'fields': '互联网科技、传媒直播、AI应用、光电新能源、设计美学', 'match_rate': 92 if me_wx in ['木','火'] else 75, 'role': '适合：项目操盘手、独立IP、技术布道者'},
        {'wuxing': '土', 'fields': '不动产运营、基础建设、工程管理、资产顾问、仓储物流', 'match_rate': 80 if me_wx in ['火','土'] else 68, 'role': '适合：运营总监、资产顾问、供应链主管'},
        {'wuxing': '金', 'fields': '金融财会、法律风控、精密仪器、硬件工程、黄金珠宝', 'match_rate': 86 if me_wx in ['土','金'] else 70, 'role': '适合：风控专家、注册会计师、审计法务'},
        {'wuxing': '水', 'fields': '跨境出海、国际贸易、流动型商业、现代物流、咨询服务', 'match_rate': 90 if me_wx in ['金','水'] else 76, 'role': '适合：国际买手、跨国商务、首席咨询顾问'}
    ]

    spouse_pillar = pillars[2]
    spouse_zhi = spouse_pillar['zhi']
    spouse_looks = {
        '子': "肤色偏白，清秀灵动，眼神清澈，善于交流，性格多才多艺",
        '丑': "敦厚稳重，身型匀称，为人质朴持家，处事务实而讲原则",
        '寅': "身材修长挺拔，气质清贵，有领导风范与独立主见",
        '卯': "身段秀丽，眉清目秀，富有艺术情调，性格温柔体贴细腻",
        '辰': "端庄大气，气场从容，为人圆融周到，做事有格局有担当",
        '巳': "面色红润，眼神明亮有神，性格热情直爽，做事风风火火",
        '午': "容貌出众引人注目，谈吐爽朗大方，富有感染力与魅力",
        '未': "温和包容，骨肉匀亭，处事低调，懂得持家体贴照顾人",
        '申': "轮廓分明，神采奕奕，机敏干练，现代感强且富有幽默感",
        '酉': "五官精致，皮肤白皙，审美讲究，注重个人仪表与生活品质",
        '戌': "沉稳成熟，做事严谨踏实，极具责任心，包容力极强",
        '亥': "性格宽厚温润，为人智慧且富有同理心，人缘口碑极好"
    }

    marriage_details = {
        'encounter': "【正缘相识场景】最常结识于工作协作环境、业务往来差旅、长辈亲友慎重介绍，或是在专业培训、学术研讨会等‘带有共同目标’的严肃场合中相识。",
        'personality': f"【伴侣性格深描】对方外表看似从容不迫，实则骨子里极有主意。在家庭和重大决策上能撑得住场面，对待感情忠诚度高，但偶尔带有一定执拗与固执。",
        'crisis_cure': "【感情暗礁与化解】若日支被月令或流年相冲克时，两人容易因家庭琐事或双方长辈介入而产生冷战摩擦。化解真言：凡事多私下倾听商议，多夸赞肯定对方付出的辛劳，切忌在亲友面前驳对方面子。",
        'golden_window': "【黄金婚恋窗口】凡逢流年天干透出配偶星（男逢正财偏财、女逢正官七杀），或是地支合动夫妻宫（如三合、六合），皆是感情实质升温、领证办酒成家的黄金年份（重点关注 2022、2024、2026–2027 年）。"
    }

    min_wx = min(percentages.items(), key=lambda x: x[1])[0]
    organs = {
        '木': ("肝胆、筋骨、经络、眼目疲劳", "宜疏肝理气，防熬夜伤阴，多食深绿叶菜", "酸入肝，可常饮枸杞决明子茶、菊花茶以清肝明目。"),
        '火': ("心脏、小肠、血压、睡眠与眼部", "防心火亢盛、心烦失眠，宜平复情绪戒急躁", "苦入心，宜食苦瓜、莲子心、百合，午间小憩养心气。"),
        '土': ("脾胃、消化吸收、湿气代谢", "注意少食生冷油腻，防腹胀脾虚与水肿", "甘入脾，推荐茯苓、白术、芡实煮粥，常温水泡脚祛寒湿。"),
        '金': ("呼吸道、肺气、咽喉、皮毛过敏", "秋冬防燥咳，宜润肺生津，加强有氧锻炼", "辛入肺，宜多食白萝卜、百合银耳羹、雪梨，晨起深呼吸。"),
        '水': ("肾脏、泌尿生殖、腰脊耳窍", "多饮温水少憋尿，早睡固肾气，防下焦受寒", "咸入肾，适量食用黑芝麻、黑豆、核桃、桑葚，冬日重在藏精。")
    }

    health_details = {
        'nishi_theory': "【倪师《天纪》杀星脏腑对应法】倪师在《天纪》中传授医易同源：八字或斗数中杀星集结地支，即为人身最脆弱之脏腑病根所在。全盘火旺土燥则津液枯竭，金水衰弱则肾肺失养。治未病之核心在于顺应阴阳，凡事不可用尽过度。",
        'risk_years': "【生命周期易感岁运】凡逢地支剧烈相冲克（如子午冲心肾、寅申冲肝胆、卯酉冲经络、辰戌丑未相刑伤脾胃）之流年大运，身体极易发出疲劳信号，应提前做好全身体检与作息调整。",
        'food_therapy': organs[min_wx][2]
    }

    months_forecast = [
        {"month": "正月 (庚寅)", "score": 78, "desc": "开门见机，利于筹备规划新业务", "detail": "立春之始，木气萌动。宜与团队明确全年战略目标，不宜仓促启动大额投资，稳步积累人脉。", "tag": "规划月"},
        {"month": "二月 (辛卯)", "score": 82, "desc": "贵人照应，人际合作顺利拓展", "detail": "惊蛰春分，贵人星动。多参加行业社交与洽谈，容易遇到能给予资源支持的前辈提携。", "tag": "贵人月"},
        {"month": "三月 (壬辰)", "score": 75, "desc": "事务繁琐，防文书合同细节疏漏", "detail": "水土杂合，案头琐碎事务堆积。在签订关键合同协议时必须字斟句酌，防法务疏漏。", "tag": "细心月"},
        {"month": "四月 (癸巳)", "score": 85, "desc": "才华展现，业务进项有明显提升", "detail": "巳火生财，才智灵感爆发。此月适合推出新产品、做关键提案汇报，容易斩获可观业务报酬。", "tag": "进财月"},
        {"month": "五月 (甲午)", "score": 70, "desc": "岁运合火，注意情绪与睡眠作息", "detail": "芒种夏至，火气最盛。容易出现心浮气躁、失眠上火现象。职场宜避开无谓口角争端。", "tag": "调养月"},
        {"month": "六月 (乙未)", "score": 76, "desc": "稳中有进，家庭置产或长辈利好", "detail": "小暑大暑，土厚承载。有利于处理房屋置业、装修、家庭资助等长久安稳之事。", "tag": "平稳月"},
        {"month": "七月 (丙申)", "score": 88, "desc": "驿马走动，外出差旅利开拓新局面", "detail": "立秋申金动，驿马星照。外出拜访远方客户、考察新市场、异地出差大有斩获。", "tag": "突破月"},
        {"month": "八月 (丁酉)", "score": 84, "desc": "收获期，前期投入开始兑现成果", "detail": "白露秋分，金坚成器。前期辛苦跟进的项目进入结算回报期，正财稳定进账。", "tag": "收获月"},
        {"month": "九月 (戊戌)", "score": 68, "desc": "花销增大，防非必要冲动大额消费", "detail": "寒露霜降，燥土重叠。资金进出剧烈，容易有突发的人情支出或设备更新，宜捂紧钱袋子。", "tag": "守财月"},
        {"month": "十月 (己亥)", "score": 89, "desc": "水气渐润，财源与灵感双双回归", "detail": "立冬水旺，滋润全局。思维敏捷开阔，商业谈判顺风顺水，为一年中综合运势最高峰之一。", "tag": "转旺月"},
        {"month": "冬月 (庚子)", "score": 80, "desc": "冲克微显，宜收拢战线做好总结", "detail": "大雪冬至，子水冲合。适宜盘点全年收支，回收应收账款，不宜盲目扩张新战线。", "tag": "总结月"},
        {"month": "腊月 (辛丑)", "score": 83, "desc": "岁末吉庆，亲友团聚筹备来年大计", "detail": "小寒大寒，湿土生金。岁末平安喜乐，适合拜访恩师长辈，蓄力谋划来年新开局。", "tag": "吉庆月"}
    ]

    lucky_colors = {
        '木': '青绿、碧蓝、墨绿', '火': '朱红、赤橘、粉紫', '土': '米黄、焦糖、暖驼',
        '金': '白金、银灰、乳白', '水': '玄黑、深海蓝、烟灰'
    }
    lucky_dirs = {
        '木': '正东、东南方', '火': '正南方', '土': '本地中宫、东北西南', '金': '正西、西北方', '水': '正北方'
    }
    lucky_nums = {'木': '3、8', '火': '2、7', '土': '5、0', '金': '4、9', '水': '1、6'}
    
    if score < 45: useful_wx = [strength['parent_wx'], me_wx]
    else: useful_wx = [strength['child_wx'], strength['wealth_wx']]
        
    fortune_plan = {
        'useful_wx': useful_wx,
        'colors': ' / '.join([lucky_colors[w] for w in useful_wx]),
        'directions': ' / '.join([lucky_dirs[w] for w in useful_wx]),
        'numbers': ' / '.join([lucky_nums[w] for w in useful_wx]),
        'ornaments': f"建议多佩戴与【{'、'.join(useful_wx)}】属性相关的材质（如木质香珠、沉香、水晶玉石、金银配饰），居家与办公桌面朝向{'、'.join([lucky_dirs[w] for w in useful_wx])}更为得利。",
        'fengshui_detail': f"【环境气场调优】建议办公桌左手青龙位摆放生旺五行属【{useful_wx[0]}】的吉祥绿植或矿物摆件；手机尾号选用含 {lucky_nums[useful_wx[0]]} 的数字磁场；卧室床头宜朝向 {' / '.join([lucky_dirs[w] for w in useful_wx])}，有助于睡眠质量与元气恢复。"
    }

    return {
        'wealth': {
            'type': wealth_type, 'summary': wealth_summary, 'details': wealth_details, 'careers': careers
        },
        'marriage': {
            'spouse_looks': spouse_looks.get(spouse_zhi, "气质出众，为人端正"),
            'spouse_zhi': spouse_zhi, 'details': marriage_details
        },
        'health': {
            'weak_wx': min_wx, 'organ': organs[min_wx][0], 'lifestyle': organs[min_wx][1], 'details': health_details
        },
        'months_forecast': months_forecast,
        'fortune_plan': fortune_plan
    }

class TianshuHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/profiles":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            if os.path.exists(PROFILES_FILE):
                with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            else:
                self.wfile.write(b"[]")
            return
        elif url.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "running", "version": "2.0.0"}).encode("utf-8"))
            return
        return super().do_GET()

    def do_POST(self):
        url = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try: req_data = json.loads(body)
        except Exception: req_data = {}

        if url.path == "/api/bazi/calculate":
            try:
                name = req_data.get("name", "某某")
                gender = req_data.get("gender", "男")
                calendar_type = req_data.get("calendar_type", "solar")
                city = req_data.get("city", "湖北 随州")
                lng = float(req_data.get("lng", 113.37))
                lat = float(req_data.get("lat", 31.71))
                enable_true_solar = bool(req_data.get("true_solar_enabled", True))
                
                if calendar_type == "lunar":
                    ly = int(req_data.get("lunar_year", 1995))
                    lm = int(req_data.get("lunar_month", 6))
                    ld = int(req_data.get("lunar_day", 20))
                    is_leap = bool(req_data.get("is_leap", False))
                    lh = int(req_data.get("hour", 7))
                    lmin = int(req_data.get("minute", 30))
                    lunar_obj = Lunar.fromYmdHms(ly, -lm if is_leap else lm, ld, lh, lmin, 0)
                    solar_obj = lunar_obj.getSolar()
                    s_year, s_month, s_day, s_hour, s_minute = solar_obj.getYear(), solar_obj.getMonth(), solar_obj.getDay(), lh, lmin
                else:
                    solar_date = req_data.get("solar_date", "2001-04-23")
                    solar_time = req_data.get("solar_time", "23:40")
                    parts_d = [int(p) for p in solar_date.split("-")]
                    parts_t = [int(p) for p in solar_time.split(":")]
                    s_year, s_month, s_day, s_hour, s_minute = parts_d[0], parts_d[1], parts_d[2], parts_t[0], parts_t[1]

                chart = engine.generate_full_bazi_chart(
                    name=name, gender=gender, year=s_year, month=s_month, day=s_day, hour=s_hour, minute=s_minute,
                    city=city, lng=lng, lat=lat, enable_true_solar=enable_true_solar
                )
                chart['scenarios'] = generate_scenario_reading(chart)
                
                if ziwei_cli is not None:
                    try:
                        zw_payload = {
                            "calendar_type": "solar",
                            "birth_time": f"{s_year:04d}-{s_month:02d}-{s_day:02d} {s_hour:02d}:{s_minute:02d}",
                            "gender": "male" if gender == "男" else "female"
                        }
                        zw_res = ziwei_cli.build_output(zw_payload)
                        chart['ziwei'] = zw_res.get('chart', {})
                        chart['ziwei_calendar'] = zw_res.get('calendar', {})
                    except Exception as ze:
                        chart['ziwei_error'] = str(ze)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(chart, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "traceback": traceback.format_exc()}).encode("utf-8"))
            return

        elif url.path == "/api/hepan/calculate":
            try:
                chart_a = req_data.get("chart_a")
                chart_b = req_data.get("chart_b")
                hepan_res = engine.calculate_hepan_engine(chart_a, chart_b)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(hepan_res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif url.path == "/api/profiles/save":
            try:
                profiles = []
                if os.path.exists(PROFILES_FILE):
                    with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                        profiles = json.load(f)
                
                new_p = req_data
                if not new_p.get("id"):
                    new_p["id"] = f"p-{int(datetime.now().timestamp()*1000)}"
                new_p["createdAt"] = datetime.now().isoformat()
                
                found = False
                for i, p in enumerate(profiles):
                    if p.get("id") == new_p["id"]:
                        profiles[i] = new_p
                        found = True
                        break
                if not found:
                    profiles.insert(0, new_p)
                    
                with open(PROFILES_FILE, "w", encoding="utf-8") as f:
                    json.dump(profiles, f, ensure_ascii=False, indent=2)
                    
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "profile": new_p}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif url.path == "/api/chat":
            user_msg = req_data.get("message", "")
            chart = req_data.get("chart", {})
            bazi_str = chart.get('header', {}).get('bazi_str', '')
            day_master = chart.get('header', {}).get('day_master', '')
            
            quotes = [
                {"book": "《滴天髓》", "text": "五气顺行，吉凶存乎动静；五行和顺，福寿归于和平。"},
                {"book": "《穷通宝鉴》", "text": "十干各有专司，春木夏火秋金冬水，贵在得时得势，调候为先。"},
                {"book": "《三命通会》", "text": "夫命有格局，气有纯驳。格局清纯者，富贵由心生；驳杂无制者，劳碌经坎坷。"},
                {"book": "倪海厦《天纪》", "text": "命盘是先天定数，人事是后天修持。善用其长，避其锋芒，知命方能改命。"}
            ]
            
            reply_text = f"针对你的生辰四柱【{bazi_str}】（日主 {day_master}）：\n\n关于你提到的“{user_msg}”，从盘面来看："
            if "财" in user_msg or "钱" in user_msg or "工作" in user_msg or "事业" in user_msg:
                reply_text += "你命局中食伤与财星流通有情，凡遇水木旺相之流年（如遇印星生身或岁运生财），事业多有上升契机。建议不宜盲目跟风重资产投入，发挥个人才干与专业长处，偏财自见成效。"
            elif "婚" in user_msg or "感情" in user_msg or "对象" in user_msg or "正缘" in user_msg:
                reply_text += "配偶宫坐生旺之地，伴侣为人有担当且具备一定持家能力。近三年内逢红鸾、天喜或官杀星透出之年份，正是感情实质升温与缔结良缘的黄金窗口。"
            elif "健康" in user_msg or "身体" in user_msg or "病" in user_msg:
                reply_text += "全盘五行中偏弱之脏腑需多加关照。倪师在《天纪》中强调‘天道贵冲和’，平时注意作息节奏、少思寡虑，配合适度食养即可固本培元。"
            else:
                reply_text += "当前大运走势稳健，只要顺应五行喜用神方位与行业赛道，戒急用忍，必能在人生关键节点顺水行舟。"

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply_text, "citations": quotes}, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server():
    server = HTTPServer(('127.0.0.1', PORT), TianshuHandler)
    print(f"=== 天枢台服务 v2.0 已启动: http://127.0.0.1:{PORT} ===")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    server.server_close()

if __name__ == "__main__":
    run_server()
