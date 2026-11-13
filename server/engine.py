# -*- coding: utf-8 -*-
"""
天枢台 (Tianshu Workbench) 核心计算引擎 v2.0
包含完整的四柱八字、五行旺衰量化、十神分布、神煞系统、大运通俗深解、关键流年事件推演(带化解锦囊)、双人合盘引擎、场景深度解盘
"""

import math
from datetime import datetime
from lunar_python import Solar, Lunar

TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

GAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
}
ZHI_WUXING = {
    '寅': '木', '卯': '木', '巳': '火', '午': '火', '辰': '土',
    '戌': '土', '丑': '土', '未': '土', '申': '金', '酉': '金',
    '亥': '水', '子': '水'
}
WUXING_COLORS = {
    '木': '#4ade80', '火': '#f87171', '土': '#fbbf24', '金': '#facc15', '水': '#60a5fa'
}

ZHI_CANGGAN = {
    '子': [('癸', 1.0)],
    '丑': [('己', 0.6), ('癸', 0.3), ('辛', 0.1)],
    '寅': [('甲', 0.6), ('丙', 0.3), ('戊', 0.1)],
    '卯': [('乙', 1.0)],
    '辰': [('戊', 0.6), ('乙', 0.3), ('癸', 0.1)],
    '巳': [('丙', 0.6), ('庚', 0.3), ('戊', 0.1)],
    '午': [('丁', 0.7), ('己', 0.3)],
    '未': [('己', 0.6), ('丁', 0.3), ('乙', 0.1)],
    '申': [('庚', 0.6), ('壬', 0.3), ('戊', 0.1)],
    '酉': [('辛', 1.0)],
    '戌': [('戊', 0.6), ('辛', 0.3), ('丁', 0.1)],
    '亥': [('壬', 0.7), ('甲', 0.3)]
}

def get_shishen(day_gan, target_gan):
    tg_idx = {'甲':0,'乙':1,'丙':2,'丁':3,'戊':4,'己':5,'庚':6,'辛':7,'壬':8,'癸':9}
    me = tg_idx[day_gan]
    tar = tg_idx[target_gan]
    me_wx = me // 2
    tar_wx = tar // 2
    same_polarity = (me % 2) == (tar % 2)
    diff = (tar_wx - me_wx) % 5
    if diff == 0: return '比肩' if same_polarity else '劫财'
    elif diff == 1: return '食神' if same_polarity else '伤官'
    elif diff == 2: return '偏财' if same_polarity else '正财'
    elif diff == 3: return '七杀' if same_polarity else '正官'
    elif diff == 4: return '偏印' if same_polarity else '正印'
    return ''

CHANGSHENG_TABLE = {
    '甲': ['沐浴','冠带','临官','帝旺','衰','病','死','墓','绝','胎','养','长生'],
    '丙': ['胎','养','长生','沐浴','冠带','临官','帝旺','衰','病','死','墓','绝'],
    '戊': ['胎','养','长生','沐浴','冠带','临官','帝旺','衰','病','死','墓','绝'],
    '庚': ['死','墓','绝','胎','养','长生','沐浴','冠带','临官','帝旺','衰','病'],
    '壬': ['帝旺','衰','病','死','墓','绝','胎','养','长生','沐浴','冠带','临官'],
    '乙': ['病','衰','帝旺','临官','冠带','沐浴','长生','养','胎','绝','墓','死'],
    '丁': ['绝','墓','死','病','衰','帝旺','临官','冠带','沐浴','长生','养','胎'],
    '己': ['绝','墓','死','病','衰','帝旺','临官','冠带','沐浴','长生','养','胎'],
    '辛': ['胎','绝','墓','死','病','衰','帝旺','临官','冠带','沐浴','长生','养'],
    '癸': ['临官','冠带','沐浴','长生','养','胎','绝','墓','死','病','衰','帝旺']
}

def get_changsheng(gan, zhi):
    zhi_idx = DIZHI.index(zhi)
    return CHANGSHENG_TABLE.get(gan, ['']*12)[zhi_idx]

def get_kongwang(gan, zhi):
    g_idx = TIANGAN.index(gan)
    z_idx = DIZHI.index(zhi)
    diff = (z_idx - g_idx) % 12
    kw_map = {
        0: '甲子旬: 戌亥', 10: '甲寅旬: 子丑', 8: '甲辰旬: 寅卯',
        6: '甲午旬: 辰巳', 4: '甲申旬: 午未', 2: '甲戌旬: 申酉'
    }
    return kw_map.get(diff, '')

CHINA_DST_RANGES = [
    (datetime(1986, 5, 4), datetime(1986, 9, 14)),
    (datetime(1987, 4, 12), datetime(1987, 9, 13)),
    (datetime(1988, 4, 10), datetime(1988, 9, 11)),
    (datetime(1989, 4, 16), datetime(1989, 9, 17)),
    (datetime(1990, 4, 15), datetime(1990, 9, 16)),
    (datetime(1991, 4, 14), datetime(1991, 9, 15)),
]

def is_china_dst(dt: datetime) -> bool:
    for start, end in CHINA_DST_RANGES:
        if start <= dt <= end: return True
    return False

def calc_true_solar_time(dt: datetime, lng: float, enable_dst=True) -> datetime:
    t = dt
    if enable_dst and is_china_dst(dt):
        t = datetime.fromtimestamp(t.timestamp() - 3600)
    lng_offset_sec = (lng - 120.0) * 240.0
    day_of_year = t.timetuple().tm_yday
    b = 2 * math.pi * (day_of_year - 81) / 365
    eot_minutes = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    eot_sec = eot_minutes * 60.0
    return datetime.fromtimestamp(t.timestamp() + lng_offset_sec + eot_sec)

def calc_bazi_strength(year_gz, month_gz, day_gz, time_gz):
    y_g, y_z = year_gz[0], year_gz[1]
    m_g, m_z = month_gz[0], month_gz[1]
    d_g, d_z = day_gz[0], day_gz[1]
    t_g, t_z = time_gz[0], time_gz[1]
    
    day_gan = d_g
    me_wx = GAN_WUXING[day_gan]
    
    scores = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
    counts = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
    
    for g in [y_g, m_g, d_g, t_g]:
        wx = GAN_WUXING[g]
        scores[wx] += 1.0
        counts[wx] += 1
        
    for zhi, is_month in [(y_z, False), (m_z, True), (d_z, False), (t_z, False)]:
        multiplier = 2.5 if is_month else 1.0
        cang = ZHI_CANGGAN.get(zhi, [])
        for cg, weight in cang:
            wx = GAN_WUXING[cg]
            scores[wx] += weight * multiplier
            counts[wx] += 1

    total_score = sum(scores.values())
    percentages = {k: round((v / total_score) * 100, 1) for k, v in scores.items()}
    
    wx_cycle = ['木', '火', '土', '金', '水']
    idx = wx_cycle.index(me_wx)
    parent_wx = wx_cycle[(idx - 1) % 5]
    child_wx = wx_cycle[(idx + 1) % 5]
    wealth_wx = wx_cycle[(idx + 2) % 5]
    officer_wx = wx_cycle[(idx + 3) % 5]
    
    same_party = scores[me_wx] + scores[parent_wx]
    strength_score = round((same_party / total_score) * 100, 1)
    
    if strength_score < 20: status = '从弱/极弱'
    elif strength_score < 42: status = '偏弱'
    elif strength_score <= 58: status = '中和平衡'
    elif strength_score <= 80: status = '偏旺'
    else: status = '极旺/专旺'
        
    month_wx = ZHI_WUXING[m_z]
    if month_wx == me_wx: yue_status = '月令当旺·' + me_wx
    elif month_wx == parent_wx: yue_status = '月令相生·' + month_wx
    else: yue_status = '月令相·' + month_wx

    return {
        'scores': {k: round(v, 2) for k, v in scores.items()},
        'percentages': percentages,
        'counts': counts,
        'strength_score': strength_score,
        'status': status,
        'yue_status': yue_status,
        'me_wx': me_wx,
        'parent_wx': parent_wx,
        'child_wx': child_wx,
        'wealth_wx': wealth_wx,
        'officer_wx': officer_wx
    }

def analyze_shishen_and_shensha(year_gz, month_gz, day_gz, time_gz):
    d_g = day_gz[0]
    all_pillars = [('年', year_gz), ('月', month_gz), ('日', day_gz), ('时', time_gz)]
    
    shishen_counts = {}
    total_items = 0
    for name, gz in all_pillars:
        if name != '日':
            ss = get_shishen(d_g, gz[0])
            shishen_counts[ss] = shishen_counts.get(ss, 0) + 1.0
            total_items += 1.0
            
    for name, gz in all_pillars:
        for cg, w in ZHI_CANGGAN[gz[1]]:
            ss = get_shishen(d_g, cg)
            shishen_counts[ss] = shishen_counts.get(ss, 0) + w
            total_items += w
            
    shishen_dist = []
    for ss, weight in sorted(shishen_counts.items(), key=lambda x: x[1], reverse=True):
        shishen_dist.append({
            'name': ss,
            'percentage': round((weight / total_items) * 100, 1),
            'weight': round(weight, 2)
        })
        
    shensha_list = []
    y_g, y_z = year_gz[0], year_gz[1]
    m_z = month_gz[1]
    d_z = day_gz[1]
    t_z = time_gz[1]
    all_zhis = [y_z, m_z, d_z, t_z]
    
    tianyi_map = {
        '甲': ['丑', '未'], '戊': ['丑', '未'], '庚': ['丑', '未'],
        '乙': ['子', '申'], '己': ['子', '申'], '丙': ['亥', '酉'],
        '丁': ['亥', '酉'], '壬': ['卯', '巳'], '癸': ['卯', '巳'], '辛': ['午', '寅']
    }
    tianyi_targets = set(tianyi_map.get(d_g, []) + tianyi_map.get(y_g, []))
    hit_tianyi = [z for z in all_zhis if z in tianyi_targets]
    shensha_list.append({
        'name': '天乙贵人',
        'hit': len(hit_tianyi) > 0,
        'pos': '、'.join([f"{['年','月','日','时'][i]}支" for i, z in enumerate(all_zhis) if z in tianyi_targets]),
        'desc': '逢凶化吉，一生近贵利达'
    })
    
    wenchang_map = {'甲':'巳','乙':'午','丙':'申','戊':'申','丁':'酉','己':'酉','庚':'亥','辛':'子','壬':'寅','癸':'卯'}
    wc_target = wenchang_map.get(d_g, '')
    hit_wc = [i for i, z in enumerate(all_zhis) if z == wc_target]
    shensha_list.append({
        'name': '文昌',
        'hit': len(hit_wc) > 0,
        'pos': '、'.join([f"{['年','月','日','时'][i]}支" for i in hit_wc]),
        'desc': '主聪明文雅，逢考必有助力'
    })
    
    yima_map = {
        '申':'寅','子':'寅','辰':'寅','寅':'申','午':'申','戌':'申',
        '巳':'亥','酉':'亥','丑':'亥','亥':'巳','卯':'巳','未':'巳'
    }
    ym_target = yima_map.get(d_z, yima_map.get(y_z, ''))
    hit_ym = [i for i, z in enumerate(all_zhis) if z == ym_target]
    shensha_list.append({
        'name': '驿马',
        'hit': len(hit_ym) > 0,
        'pos': '、'.join([f"{['年','月','日','时'][i]}支" for i in hit_ym]),
        'desc': '主奔驰走动，远行创业发财'
    })
    
    taohua_map = {
        '申':'酉','子':'酉','辰':'酉','寅':'卯','午':'卯','戌':'卯',
        '巳':'午','酉':'午','丑':'午','亥':'子','卯':'子','未':'子'
    }
    th_target = taohua_map.get(d_z, taohua_map.get(y_z, ''))
    hit_th = [i for i, z in enumerate(all_zhis) if z == th_target]
    shensha_list.append({
        'name': '桃花',
        'hit': len(hit_th) > 0,
        'pos': '、'.join([f"{['年','月','日','时'][i]}支" for i in hit_th]),
        'desc': '异性缘与人缘极佳，魅力出众'
    })
    
    huagai_map = {
        '申':'辰','子':'辰','辰':'辰','寅':'戌','午':'戌','戌':'戌',
        '巳':'丑','酉':'丑','丑':'丑','亥':'未','卯':'未','未':'未'
    }
    hg_target = huagai_map.get(d_z, huagai_map.get(y_z, ''))
    hit_hg = [i for i, z in enumerate(all_zhis) if z == hg_target]
    shensha_list.append({
        'name': '华盖',
        'hit': len(hit_hg) > 0,
        'pos': '、'.join([f"{['年','月','日','时'][i]}支" for i in hit_hg]),
        'desc': '超凡悟性与审美，利艺术哲思'
    })
    
    jiangxing_map = {
        '申':'子','子':'子','辰':'子','寅':'午','午':'午','戌':'午',
        '巳':'酉','酉':'酉','丑':'酉','亥':'卯','卯':'卯','未':'卯'
    }
    jx_target = jiangxing_map.get(d_z, jiangxing_map.get(y_z, ''))
    hit_jx = [i for i, z in enumerate(all_zhis) if z == jx_target]
    shensha_list.append({
        'name': '将星',
        'hit': len(hit_jx) > 0,
        'pos': '、'.join([f"{['年','月','日','时'][i]}支" for i in hit_jx]),
        'desc': '主领导力与威仪，事业能掌实权'
    })
    
    lu_map = {'甲':'寅','乙':'卯','丙':'巳','戊':'巳','丁':'午','己':'午','庚':'申','辛':'酉','壬':'亥','癸':'子'}
    lu_target = lu_map.get(d_g, '')
    hit_lu = [i for i, z in enumerate(all_zhis) if z == lu_target]
    shensha_list.append({
        'name': '禄神',
        'hit': len(hit_lu) > 0,
        'pos': '、'.join([f"{['年','月','日','时'][i]}支" for i in hit_lu]),
        'desc': '自食其力，丰衣足食，财源安稳'
    })
    
    yangren_map = {'甲':'卯','乙':'辰','丙':'午','戊':'午','丁':'未','己':'未','庚':'酉','辛':'戌','壬':'子','癸':'丑'}
    yr_target = yangren_map.get(d_g, '')
    hit_yr = [i for i, z in enumerate(all_zhis) if z == yr_target]
    shensha_list.append({
        'name': '羊刃',
        'hit': len(hit_yr) > 0,
        'pos': '、'.join([f"{['年','月','日','时'][i]}支" for i in hit_yr]),
        'desc': '意志坚韧，刚烈勇猛，需防性急'
    })

    kw_str = get_kongwang(day_gz[0], day_gz[1])
    kw_zhis = kw_str.split(':')[-1].strip().split() if kw_str else []
    hit_kw = [i for i, z in enumerate(all_zhis) if z in kw_zhis]
    shensha_list.append({
        'name': '空亡',
        'hit': len(hit_kw) > 0,
        'pos': '、'.join([f"{['年','月','日','时'][i]}支" for i in hit_kw]),
        'desc': '虚无玄妙之应，利修行不宜贪名'
    })
    
    tiande_map = {'寅':'丁','卯':'申','辰':'壬','巳':'辛','午':'亥','未':'甲','申':'癸','酉':'寅','戌':'丙','亥':'乙','子':'巳','丑':'庚'}
    td_target = tiande_map.get(m_z, '')
    hit_td = (td_target in [y_g, month_gz[0], d_g, time_gz[0]]) or (td_target in all_zhis)
    shensha_list.append({
        'name': '天德',
        'hit': hit_td,
        'pos': '月干' if td_target == month_gz[0] else '天干',
        'desc': '祖荫福庇，化险为夷'
    })
    
    yuede_map = {'寅':'丙','午':'丙','戌':'丙','申':'壬','子':'壬','辰':'壬','亥':'甲','卯':'甲','未':'甲','巳':'庚','酉':'庚','丑':'庚'}
    yd_target = yuede_map.get(m_z, '')
    hit_yd = yd_target in [y_g, month_gz[0], d_g, time_gz[0]]
    shensha_list.append({
        'name': '月德',
        'hit': hit_yd,
        'pos': '天干',
        'desc': '仁慈博爱，福寿双全'
    })
    
    jinyu_map = {'甲':'辰','乙':'巳','丙':'未','戊':'未','丁':'申','己':'申','庚':'戌','辛':'亥','壬':'丑','癸':'寅'}
    jy_target = jinyu_map.get(d_g, '')
    hit_jy = [i for i, z in enumerate(all_zhis) if z == jy_target]
    shensha_list.append({
        'name': '金舆',
        'hit': len(hit_jy) > 0,
        'pos': '、'.join([f"{['年','月','日','时'][i]}支" for i in hit_jy]),
        'desc': '金舆黄金车，主出入平安、贵人提拔'
    })

    return shishen_dist, shensha_list

# ----------------- 4. 大运通俗深解系统 -----------------
def generate_dayun_explanation(dayun_gz, dayun_shishen, day_master_gan, strength_info, start_age, start_year):
    score = strength_info['strength_score']
    is_weak = score < 45
    
    shishen_interpretations = {
        '比肩': {
            'title': '同辈合力 · 开拓争锋期',
            'summary': '这十年人脉与同辈交往热闹，自主创业心强烈，适合携手同侪打天下。',
            'career': '事业上独立性变强，有自立门户或与伙伴联手开拓新版图的契机；但也意味着竞争格外激烈。' if is_weak else '同行竞逐多，容易遇到理念不合的合伙人分权，宜独当一面。',
            'wealth': '钱财流通快，赚钱机会多但开支也大。' if is_weak else '比劫重重防破财！特别注意严防合伙纠纷、借钱给朋友打水漂，投资务必谨慎。',
            'mindset': '守正防争，做事分清权责边界，白纸黑字胜过口头情义。'
        },
        '劫财': {
            'title': '风云变幻 · 披荆斩棘期',
            'summary': '气场刚猛，魄力与野心极大的一段时期，机遇与风险并存。',
            'career': '敢打敢拼，能打硬仗，能在变局中异军突起；需防行事冲动与上司权威冲突。',
            'wealth': '财富进出大起大落。切忌高杠杆投机，切忌替他人担保，容易因亲友情面破耗大笔资金。',
            'mindset': '戒骄戒躁，遇事冷三分，防贪防冲动，稳住基本盘才是赢家。'
        },
        '食神': {
            'title': '才华生财 · 闲适丰盈期',
            'summary': '思路开阔、才艺绽放，口福与生活享受提升，是一段体感较为舒适从容的好运。',
            'career': '适合发挥个人技术、专业才干、自媒体输出或内容创意，以才华赢取声誉，事业步入顺流。',
            'wealth': '食神生财，财运稳中有升，多属于靠专业本事、个人名誉赚来的干净钱，细水长流。',
            'mindset': '保持身心愉悦，多做知识与技能沉淀，防贪安逸发胖或行动力滞后。'
        },
        '伤官': {
            'title': '灵感井喷 · 破局革新期',
            'summary': '才思敏捷，叛逆不羁，极具创新精神和商业敏锐度，也是人生容易有重大转折的十年。',
            'career': '极利突破瓶颈、跨界转型或创业；但伤官克官，容易对旧体制感到厌倦，注意职场人际。',
            'wealth': '财源丰厚，善于抓住冷门商机赚大钱；但花销随性，容易大手大脚。',
            'mindset': '收敛傲气，得理亦要饶人；将才智专注于做事，切勿在人际是非上耗费心神。'
        },
        '偏财': {
            'title': '商机涌现 · 资本积累期',
            'summary': '对金钱与财富机会格外敏感，人脉四通八达，副业与轻资产投资机会极多。',
            'career': '利于从事实务经营、商务洽谈、销售贸易或自由职业，能把握时代风口迅速起势。',
            'wealth': '偏财运旺盛，常有意料之外的进账或红利；但若身弱不胜财，容易因求财过度劳累伤身。',
            'mindset': '知足常乐，见好就收，避免将战线拉得太长，财富重在留得住。'
        },
        '正财': {
            'title': '勤俭立业 · 稳健复利期',
            'summary': '踏实务实，按部就班，属于凭借持续辛勤付出换来阶梯式上升的黄金积累期。',
            'career': '职场晋升明确，在正统行业深耕能获得长期稳定的报酬与信赖，平台给予的回报稳固。',
            'wealth': '正财充盈，现金流稳定，最适合买房置产、储蓄复利，财富呈现滚雪球之势。',
            'mindset': '坚守长期主义，不羡慕暴富神话，守好主业就是最大的捷径。'
        },
        '七杀': {
            'title': '迎风破浪 · 执掌权柄期',
            'summary': '压力与权势齐飞，危机中蕴含逆天改命的转机，是人生脱胎换骨的试炼场。',
            'career': '能在高压环境中展现决断魄力，战胜挑战即能执掌大权或跻身行业领袖；需注意小人构陷与官非。',
            'wealth': '险中求财，收益伴随巨大责任；谨防合约漏洞与法律风险。',
            'mindset': '以刚克刚易折，以柔克刚能久；强身健体，保持充足睡眠，身体是扛住七杀的基石。'
        },
        '正官': {
            'title': '青云直上 · 名望亨通期',
            'summary': '声誉、地位、公信力大幅提升，得官方或权威认可，行事堂堂正正的一段正道光阴。',
            'career': '极利公职考录、大厂晋升、考取职称或取得行业权威地位，组织内威信建立。',
            'wealth': '薪酬福利待遇水涨船高，多为正当名利双收之财，受人敬仰。',
            'mindset': '克己奉公，行事遵纪守法，珍惜名声如羽毛，切莫走灰色捷径。'
        },
        '偏印': {
            'title': '玄思独悟 · 技能深造期',
            'summary': '灵感独具，喜钻研冷门学术、哲学、艺术或专业壁垒技能，内心趋于内敛深刻。',
            'career': '适合做研发、幕后策划、咨询顾问或专精技术；职场上略带孤僻感，不喜随波逐流。',
            'wealth': '财源多来自独家手艺或非主流渠道；易因多疑多思而错失明面上的投资良机。',
            'mindset': '多与积极阳光之人相处，走出思维死胡同，学会将深邃思考落地为现实行动。'
        },
        '正印': {
            'title': '贵人福庇 · 养精蓄锐期',
            'summary': '仁厚安详，诸事逢凶化吉，有长辈扶持与政策红利眷顾，是一生福报兑现的温厚时光。',
            'career': '利于考学深造、发表作品、获得大贵人提携，职场环境包容，阻力大幅减轻。',
            'wealth': '得祖荫或不动产增值，有车房之喜；不求横财而自然衣食无忧。',
            'mindset': '常怀感恩利他之心，多做善事积阴德，借贵人之力顺势而上。'
        }
    }
    
    interp = shishen_interpretations.get(dayun_shishen, {
        'title': f'{dayun_shishen}主导 · 承转行运期',
        'summary': '气机运化，天干地支交织，人生进入新的生活轨迹。',
        'career': '立足根本，因时而变。',
        'wealth': '稳字当头，勤俭为本。',
        'mindset': '心怀坦荡，顺应天道。'
    })
    
    return {
        'gz': dayun_gz,
        'shishen': dayun_shishen,
        'title': interp['title'],
        'summary': interp['summary'],
        'career': interp['career'],
        'wealth': interp['wealth'],
        'mindset': interp['mindset'],
        'years_span': f"{start_year}–{start_year + 9} 年 (虚岁 {start_age}–{start_age + 9} 岁)"
    }

# ----------------- 5. 关键流年事件推演 + 真实可落地的【天枢化解锦囊】 -----------------
STRATEGY_KIT = {
    '冲配偶宫': {
        'title': '⚡【婚恋/居住动荡 · 破局锦囊】',
        'desc': '地支逢冲，能量剧烈激荡。老祖宗讲“逢冲不破即立”，关键在于【主动应冲】。',
        'actions': [
            '【主动应房动】：此年非常适合主动买房、租房、重新装修、更换卧室床位，把动荡应在砖石居住空间上。',
            '【夫妻聚少离多化解】：若已婚且摩擦增多，主动申请出差、短期异地培训或分被而眠，形成物理距离自然化煞。',
            '【未婚者抓紧升华】：未婚谈恋爱者，可借冲动之机主动订婚、买房同居或领证，化冲为喜！'
        ]
    },
    '冲月令': {
        'title': '⚡【职场跃迁/换岗 · 进取锦囊】',
        'desc': '月令为事业提纲，逢冲必主环境动迁、团队重组或换赛道。',
        'actions': [
            '【顺势动迁】：切忌在死胡同里硬熬，此年正是跳槽大厂、换新部门、申请外派的黄金契机，越动越活。',
            '【长辈健康关照】：顺带带父母做一次系统全身体检，主动破点医药钱以应长辈小耗。'
        ]
    },
    '岁运并临': {
        'title': '⚡【岁运并临 · 重大转折定海神针】',
        'desc': '“岁运并临，不死自己死他人”是古书夸大之语，实则是五行能量叠加翻倍，人生迎来一次结构性大洗牌。',
        'actions': [
            '【立大愿成大业】：主动承担一件极具挑战性的大事（如考博、创业、生娃、置业），将宏大能量引流到正途。',
            '【多行善事护生】：岁初主动洗牙、献血、行善捐赠，修口德戒杀生，能极大安抚躁动气场。'
        ]
    },
    '官杀克身': {
        'title': '⚡【压力山大 · 借力化煞锦囊】',
        'desc': '官杀为泰山压顶，容易遇到严苛领导、甲方刁难或身心透支。',
        'actions': [
            '【用印通关】：印者，学习与长辈也。遇刁难莫硬刚，多向德高望重的前辈请教，以柔克刚。',
            '【按部就班】：所有重要决定留痕留字据，严守合规底线，小人自然无从下口。'
        ]
    },
    '比劫夺财': {
        'title': '⚡【破财预警 · 破财消灾锦囊】',
        'desc': '比劫夺财之年，钱财如开闸流水，极易因朋友、亲戚借贷或合伙投机血亏。',
        'actions': [
            '【主动大额消费】：年初主动做有价值的确定性开销（如交一年房租、购买黄金、支付学费、全身体检）。',
            '【闭紧借贷闸门】：借钱一律推脱“钱在定期理财/老婆管账”，任谁游说绝不合伙盲目开店。'
        ]
    }
}

def generate_key_timeline_events(day_gan, year_gz, month_gz, day_gz, time_gz, gender, dayuns):
    timeline_events = []
    years_to_check = [
        (2012, '壬辰'), (2013, '癸巳'), (2014, '甲午'), (2015, '乙未'),
        (2016, '丙申'), (2017, '丁酉'), (2018, '戊戌'), (2019, '己亥'),
        (2020, '庚子'), (2021, '辛丑'), (2022, '壬寅'), (2023, '癸卯'),
        (2024, '甲辰'), (2025, '乙巳'), (2026, '丙午')
    ]
    
    y_z = year_gz[1]
    m_z = month_gz[1]
    d_z = day_gz[1]
    t_z = time_gz[1]
    chong_map = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅','卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}
    
    for yr, gz in years_to_check:
        ln_g, ln_z = gz[0], gz[1]
        ss = get_shishen(day_gan, ln_g)
        
        active_dayun = None
        for dy in dayuns:
            if dy['start_year'] <= yr < dy['start_year'] + 10:
                active_dayun = dy
                break
                
        events = []
        tags = []
        strategies = []
        impact_level = "中"
        
        # 1. 岁运并临
        if active_dayun and active_dayun['gz'] == gz:
            events.append("【岁运并临】此年流年干支与正在行的大运完全重合，天干地支能量倍增，主人生迎来一次极剧烈的结构性大变动（环境迁移、身份转换或家中重大转折）。")
            tags.append("岁运并临")
            strategies.append(STRATEGY_KIT['岁运并临'])
            impact_level = "极高"

        # 2. 冲克配偶宫 (日支)
        if chong_map.get(ln_z) == d_z:
            events.append(f"【日支逢冲】流年地支{ln_z}对冲夫宫/妻宫【{d_z}】，婚姻宫剧烈晃动。未婚者主感情出现实质性突破、同居、领证成家或重大分合；已婚者主居所搬迁、买房置地或夫妻间因事聚少离多。")
            tags.append("婚恋/居住大变动")
            strategies.append(STRATEGY_KIT['冲配偶宫'])
            impact_level = "高"

        # 3. 冲月支
        if chong_map.get(ln_z) == m_z:
            events.append(f"【月令逢冲】冲动父母宫与成长宫【{m_z}】，主职场换岗、城市迁移、搬迁租房或工作环境重大重组。")
            tags.append("职场/环境跃迁")
            strategies.append(STRATEGY_KIT['冲月令'])

        # 4. 冲年支
        if chong_map.get(ln_z) == y_z:
            events.append(f"【年支逢冲】流年{ln_z}冲犯年支太岁【{y_z}】，主离家求学、远行出差、外地工作或长辈健康有需照应之事。")
            tags.append("离家/远行变动")

        # 5. 十神触发
        if ss in ['正印', '偏印']:
            events.append(f"【印星透干】得贵人、长辈或文书庇佑，主考学升学、考取编制/证书、买车买房、取得重要名誉授权，或有充电深造之象。")
            tags.append("贵人/考学置业")
        elif ss in ['正官', '七杀']:
            if gender == '女':
                events.append(f"【官杀透出】女命官杀为夫星，主异性缘旺盛，极易在这年确立恋爱关系或商谈婚嫁；同时在事业上承担重大责任，挑起大梁。")
                tags.append("感情突破/挑起重任")
            else:
                events.append(f"【官杀透出】男命官杀主权位与事业风浪，主职场迎来重要考验、换部门、升职或面对大客户，责任压力大。")
                tags.append("职场大考/权位晋升")
            strategies.append(STRATEGY_KIT['官杀克身'])
        elif ss in ['偏财', '正财']:
            events.append(f"【财星照命】财务现金流进出活跃，容易有大宗商业交易、副业收入翻倍，或为了置产、结婚、投资而有一笔巨大开销。")
            tags.append("财务大动/大额进出")
        elif ss in ['比肩', '劫财']:
            events.append(f"【比劫争锋】同辈朋友聚集，开支花销暴增，有合作开拓新局之象，但必须提防借贷受骗与分财。")
            tags.append("同辈社交/防分财")
            strategies.append(STRATEGY_KIT['比劫夺财'])
        elif ss in ['食神', '伤官']:
            events.append(f"【食伤泄秀】灵感井喷，才华得以对外展现，极利于做自媒体、技术攻坚、自由创作或跳出旧体制另起炉灶；注意口舌是非。")
            tags.append("才华展现/破旧立新")

        timeline_events.append({
            'year': yr,
            'gz': gz,
            'shishen': ss,
            'dayun_gz': active_dayun['gz'] if active_dayun else '',
            'tags': tags[:3] if tags else ['平稳演进'],
            'impact_level': impact_level,
            'event_description': '；'.join(events) if events else f"流年干支【{gz}】，属于{ss}运化之年，全局五行相对平顺，主要在既定轨道上稳步积累经验与资源。",
            'strategies': strategies[:2]  # 最多给2条最核心化解对策
        })
        
    return timeline_events

# ----------------- 6. 双人合盘计算引擎 (合婚与合伙) -----------------
def calculate_hepan_engine(chart_a, chart_b):
    p_a = chart_a['pillars']
    p_b = chart_b['pillars']
    day_g_a, day_z_a = p_a[2]['gan'], p_a[2]['zhi']
    day_g_b, day_z_b = p_b[2]['gan'], p_b[2]['zhi']
    
    score = 65
    pros = []
    cons = []
    
    # 1. 天干相合 (甲己、乙庚、丙辛、丁壬、戊癸)
    tian_he = [('甲','己'),('乙','庚'),('丙','辛'),('丁','壬'),('戊','癸')]
    if (day_g_a, day_g_b) in tian_he or (day_g_b, day_g_a) in tian_he:
        score += 18
        pros.append(f"【天干夫妻正合】日主干支【{day_g_a}】与【{day_g_b}】形成天作之合，主两人初识便极具吸引力，心意相通，彼此能包容对方缺点。")
        
    # 2. 地支六合 (子丑、寅亥、卯戌、辰酉、巳申、午未)
    di_he = [('子','丑'),('寅','亥'),('卯','戌'),('辰','酉'),('巳','申'),('午','未')]
    if (day_z_a, day_z_b) in di_he or (day_z_b, day_z_a) in di_he:
        score += 15
        pros.append(f"【地支夫妻宫合】日支【{day_z_a}】与【{day_z_b}】暗结六合，主两人生活习惯、家庭观念与三观高度默契，婚后生活甜美长久。")
        
    # 3. 地支六冲
    di_chong = [('子','午'),('丑','未'),('寅','申'),('卯','酉'),('辰','戌'),('巳','亥')]
    if (day_z_a, day_z_b) in di_chong or (day_z_b, day_z_a) in di_chong:
        score -= 15
        cons.append(f"【配偶宫地支相冲】日支【{day_z_a}】与【{day_z_b}】形成对冲，主两人相处时性格脾气容易硬碰硬，因家庭小事引发冷战或争执。")
        
    # 4. 五行互补
    pct_a = chart_a['strength']['percentages']
    pct_b = chart_b['strength']['percentages']
    weak_a = min(pct_a.items(), key=lambda x: x[1])[0]
    strong_b = max(pct_b.items(), key=lambda x: x[1])[0]
    if weak_a == strong_b:
        score += 12
        pros.append(f"【五行互补平衡】甲方命中极度缺少【{weak_a}】，而乙方命局恰好【{strong_b}】旺盛，彼此如同甘霖滋润枯木，能给对方带来好运与安定感。")
        
    score = max(40, min(98, score))
    if score >= 85: level = "天作之合 · 上上吉"
    elif score >= 75: level = "良缘相配 · 中上吉"
    elif score >= 60: level = "平稳相持 · 中平"
    else: level = "需磨合调适 · 谨防冲动"
    
    advice = "夫妻/合伙之道在互相敬重包容。多欣赏对方的长处，遇冲克时懂得一方退让，便能把八字合化为现实中的福禄双全。"
    if cons:
        advice = "两人性格中有较强的自主性，建议在财务与家庭决策上明确分工，切忌在盛怒之下翻旧账，通过聚少离多或各自保留独立空间能大幅化解冲克。"

    return {
        'score': score,
        'level': level,
        'pros': pros if pros else ["两造八字气局平顺，既无大冲亦无大刑，属于细水长流相敬如宾的踏实组合。"],
        'cons': cons if cons else ["全盘无明显剧烈对冲，仅需在柴米油盐琐碎中多些耐心沟通即可。"],
        'advice': advice
    }

# ----------------- 7. 完整排盘主函数 -----------------
def generate_full_bazi_chart(name: str, gender: str, year: int, month: int, day: int, hour: int, minute: int,
                             city: str = '随州', lng: float = 113.37, lat: float = 31.71,
                             enable_true_solar: bool = True):
    raw_dt = datetime(year, month, day, hour, minute)
    if enable_true_solar:
        calc_dt = calc_true_solar_time(raw_dt, lng)
    else:
        calc_dt = raw_dt
        
    s = Solar.fromYmdHms(calc_dt.year, calc_dt.month, calc_dt.day, calc_dt.hour, calc_dt.minute, calc_dt.second)
    l = s.getLunar()
    ba = l.getEightChar()
    
    y_gz = ba.getYear()
    m_gz = ba.getMonth()
    d_gz = ba.getDay()
    t_gz = ba.getTime()
    day_gan = d_gz[0]
    
    pillars = []
    labels = ['祖辈/早年', '父母/成长', '自我/亲密', '子女/晚年']
    gzs = [y_gz, m_gz, d_gz, t_gz]
    nayin_list = [ba.getYearNaYin(), ba.getMonthNaYin(), ba.getDayNaYin(), ba.getTimeNaYin()]
    
    for i in range(4):
        g, z = gzs[i][0], gzs[i][1]
        canggan_data = []
        for cg, w in ZHI_CANGGAN[z]:
            canggan_data.append({
                'gan': cg,
                'wuxing': GAN_WUXING[cg],
                'color': WUXING_COLORS[GAN_WUXING[cg]],
                'shishen': get_shishen(day_gan, cg),
                'weight': w
            })
        
        pillars.append({
            'label': labels[i],
            'pillar_name': ['年柱', '月柱', '日柱', '时柱'][i],
            'gan': g,
            'zhi': z,
            'gz': gzs[i],
            'gan_wuxing': GAN_WUXING[g],
            'zhi_wuxing': ZHI_WUXING[z],
            'gan_color': WUXING_COLORS[GAN_WUXING[g]],
            'zhi_color': WUXING_COLORS[ZHI_WUXING[z]],
            'shishen': '日主' if i == 2 else get_shishen(day_gan, g),
            'canggan': canggan_data,
            'nayin': nayin_list[i],
            'changsheng': get_changsheng(day_gan, z),
            'kongwang': get_kongwang(g, z),
            'is_day_master': (i == 2)
        })
        
    strength_info = calc_bazi_strength(y_gz, m_gz, d_gz, t_gz)
    shishen_dist, shensha_list = analyze_shishen_and_shensha(y_gz, m_gz, d_gz, t_gz)
    
    is_male = (gender == '男')
    yun = ba.getYun(1 if is_male else 0, 2)
    start_age = yun.getStartYear()
    
    dayun_list = []
    for dy in yun.getDaYun()[:9]:
        gz = dy.getGanZhi()
        if not gz: continue
        g, z = gz[0], gz[1]
        ss = get_shishen(day_gan, g)
        
        deep_exp = generate_dayun_explanation(
            dayun_gz=gz, dayun_shishen=ss, day_master_gan=day_gan,
            strength_info=strength_info, start_age=dy.getStartAge(), start_year=dy.getStartYear()
        )
        
        ln_list = []
        for ln in dy.getLiuNian():
            ln_gz = ln.getGanZhi()
            ln_list.append({
                'year': ln.getYear(),
                'age': ln.getAge(),
                'gz': ln_gz,
                'shishen': get_shishen(day_gan, ln_gz[0])
            })
            
        dayun_list.append({
            'index': dy.getIndex(),
            'start_year': dy.getStartYear(),
            'start_age': dy.getStartAge(),
            'gz': gz,
            'gan': g,
            'zhi': z,
            'shishen': ss,
            'changsheng': get_changsheng(day_gan, z),
            'explanation': deep_exp,
            'liunians': ln_list
        })
        
    cur_year = datetime.now().year
    current_dayun = dayun_list[0] if dayun_list else None
    for dy in dayun_list:
        if dy['start_year'] <= cur_year < dy['start_year'] + 10:
            current_dayun = dy
            break

    hit_shensha_count = sum(1 for s in shensha_list if s['hit'])
    
    timeline_events = generate_key_timeline_events(
        day_gan=day_gan, year_gz=y_gz, month_gz=m_gz, day_gz=d_gz, time_gz=t_gz,
        gender=gender, dayuns=dayun_list
    )
    
    return {
        'profile': {
            'name': name,
            'gender': gender,
            'birth_solar': f"{raw_dt.strftime('%Y-%m-%d %H:%M')}",
            'true_solar': f"{calc_dt.strftime('%Y-%m-%d %H:%M')}",
            'lunar': f"农历{l.getYearInChinese()}年 {l.getMonthInChinese()}月 {l.getDayInChinese()} {t_gz[1]}时",
            'city': city,
            'lng': lng,
            'lat': lat,
            'true_solar_enabled': enable_true_solar
        },
        'header': {
            'bazi_str': f"{y_gz} {m_gz} {d_gz} {t_gz}",
            'day_master': f"{day_gan}·{strength_info['me_wx']}",
            'status': strength_info['status'],
            'score': strength_info['strength_score'],
            'current_dayun': f"{current_dayun['gz'] if current_dayun else ''}"
        },
        'pillars': pillars,
        'strength': strength_info,
        'shishen_dist': shishen_dist,
        'shensha': {
            'total': len(shensha_list),
            'hit_count': hit_shensha_count,
            'list': shensha_list
        },
        'dayun': dayun_list,
        'current_dayun': current_dayun,
        'timeline_events': timeline_events
    }
