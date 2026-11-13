// 天枢台 · 命理中心 前端核心业务逻辑 v2.0
// 包含：双模切换(小白/专家)、多主题切换、行动化解锦囊、双人合盘引擎、手机分享海报Canvas生成

let currentChartData = null;
let currentProfiles = [];
let currentCalendarMode = 'solar'; // 'solar' | 'lunar'
let currentViewMode = 'pro'; // 'simple' | 'pro'

// 全国主要省市经纬度数据库
const CITY_DATABASE = {
  "北京": [
    { name: "东城区", lng: 116.422, lat: 39.935 },
    { name: "西城区", lng: 116.372, lat: 39.918 },
    { name: "朝阳区", lng: 116.449, lat: 39.927 },
    { name: "海淀区", lng: 116.304, lat: 39.965 },
    { name: "丰台区", lng: 116.292, lat: 39.865 }
  ],
  "湖北": [
    { name: "随州", lng: 113.37, lat: 31.71 },
    { name: "鄂州", lng: 114.89, lat: 30.39 },
    { name: "武汉", lng: 114.30, lat: 30.59 },
    { name: "襄阳", lng: 112.14, lat: 32.04 },
    { name: "宜昌", lng: 111.28, lat: 30.69 },
    { name: "荆州", lng: 112.24, lat: 30.33 },
    { name: "黄冈", lng: 114.87, lat: 30.45 },
    { name: "孝感", lng: 113.92, lat: 30.93 },
    { name: "黄石", lng: 115.04, lat: 30.20 },
    { name: "十堰", lng: 110.79, lat: 32.65 },
    { name: "恩施", lng: 109.48, lat: 30.29 }
  ],
  "河南": [
    { name: "濮阳", lng: 115.03, lat: 35.76 },
    { name: "郑州", lng: 113.62, lat: 34.75 },
    { name: "洛阳", lng: 112.45, lat: 34.62 },
    { name: "开封", lng: 114.31, lat: 34.80 },
    { name: "南阳", lng: 112.53, lat: 32.99 },
    { name: "新乡", lng: 113.93, lat: 35.30 },
    { name: "安阳", lng: 114.38, lat: 36.10 }
  ],
  "上海": [
    { name: "黄浦区", lng: 121.48, lat: 31.23 },
    { name: "徐汇区", lng: 121.43, lat: 31.18 },
    { name: "浦东新区", lng: 121.54, lat: 31.22 },
    { name: "静安区", lng: 121.45, lat: 31.23 }
  ],
  "广东": [
    { name: "广州", lng: 113.26, lat: 23.13 },
    { name: "深圳", lng: 114.05, lat: 22.54 },
    { name: "东莞", lng: 113.75, lat: 23.02 },
    { name: "佛山", lng: 113.12, lat: 23.02 },
    { name: "珠海", lng: 113.57, lat: 22.27 },
    { name: "中山", lng: 113.38, lat: 22.52 }
  ],
  "浙江": [
    { name: "杭州", lng: 120.15, lat: 30.28 },
    { name: "宁波", lng: 121.55, lat: 29.87 },
    { name: "温州", lng: 120.70, lat: 28.00 },
    { name: "嘉兴", lng: 120.76, lat: 30.75 },
    { name: "绍兴", lng: 120.58, lat: 30.00 }
  ],
  "江苏": [
    { name: "南京", lng: 118.79, lat: 32.06 },
    { name: "苏州", lng: 120.58, lat: 31.30 },
    { name: "无锡", lng: 120.31, lat: 31.57 },
    { name: "常州", lng: 119.97, lat: 31.81 },
    { name: "南通", lng: 120.89, lat: 31.98 }
  ],
  "四川": [
    { name: "成都", lng: 104.06, lat: 30.67 },
    { name: "绵阳", lng: 104.74, lat: 31.46 },
    { name: "南充", lng: 106.08, lat: 30.79 },
    { name: "宜宾", lng: 104.64, lat: 28.75 }
  ],
  "山东": [
    { name: "济南", lng: 117.00, lat: 36.65 },
    { name: "青岛", lng: 120.38, lat: 36.07 },
    { name: "烟台", lng: 121.45, lat: 37.46 },
    { name: "潍坊", lng: 119.16, lat: 36.71 }
  ],
  "陕西": [
    { name: "西安", lng: 108.94, lat: 34.34 },
    { name: "咸阳", lng: 108.71, lat: 34.33 },
    { name: "宝鸡", lng: 107.24, lat: 34.36 }
  ],
  "湖南": [
    { name: "长沙", lng: 112.94, lat: 28.23 },
    { name: "株洲", lng: 113.13, lat: 27.83 },
    { name: "湘潭", lng: 112.94, lat: 27.83 },
    { name: "衡阳", lng: 112.57, lat: 26.89 }
  ]
};

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initTabNavigation();
  initDrawerChat();
  initLunarDropdowns();
  initCityCascade();
  initShortcuts();

  fetchProfiles().then(() => {
    triggerCalculate();
  });
});

// 1. 多主题切换
function initTheme() {
  const savedTheme = localStorage.getItem('tianshu_theme') || 'theme-cyber';
  changeTheme(savedTheme);
  const sel = document.getElementById('themeSelect');
  if (sel) sel.value = savedTheme;
}

function changeTheme(themeClass) {
  document.body.className = themeClass;
  localStorage.setItem('tianshu_theme', themeClass);
}

// 2. 双模切换 (小白模式 vs 专家模式)
function setViewMode(mode) {
  currentViewMode = mode;
  document.getElementById('btnModeSimple').classList.toggle('active', mode === 'simple');
  document.getElementById('btnModePro').classList.toggle('active', mode === 'pro');

  const smHero = document.getElementById('simpleModeHero');
  const proView = document.getElementById('proModeView');

  if (mode === 'simple') {
    if (smHero) smHero.style.display = 'block';
    if (proView) {
      proView.querySelector('.four-pillars-container').style.display = 'none';
      proView.querySelector('.chart-metrics-row').style.display = 'none';
    }
  } else {
    if (smHero) smHero.style.display = 'none';
    if (proView) {
      proView.querySelector('.four-pillars-container').style.display = 'grid';
      proView.querySelector('.chart-metrics-row').style.display = 'grid';
    }
  }
}

// 3. Tab 导航
function initTabNavigation() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      btn.classList.add('active');

      const targetId = btn.getAttribute('data-tab');
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add('active');
      }

      if (targetId === 'tab-dayun' && currentChartData) {
        renderDayunCanvas(currentChartData);
      }
      if (targetId === 'tab-hepan') {
        populateHepanSelects();
      }
    });
  });
}

// 4. 历法切换与农历下拉填充
function setCalendarMode(mode) {
  currentCalendarMode = mode;
  document.getElementById('btnSolarMode').classList.toggle('active', mode === 'solar');
  document.getElementById('btnLunarMode').classList.toggle('active', mode === 'lunar');
  document.getElementById('solarInputBox').style.display = (mode === 'solar') ? 'block' : 'none';
  document.getElementById('lunarInputBox').style.display = (mode === 'lunar') ? 'block' : 'none';
}

function initLunarDropdowns() {
  const ySel = document.getElementById('lunarYearSelect');
  const mSel = document.getElementById('lunarMonthSelect');
  const dSel = document.getElementById('lunarDaySelect');

  for (let y = 1940; y <= 2030; y++) {
    const opt = document.createElement('option');
    opt.value = y; opt.innerText = `${y}年`;
    if (y === 2001) opt.selected = true;
    ySel.appendChild(opt);
  }

  const monthNames = ["正月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "冬月", "腊月"];
  monthNames.forEach((name, i) => {
    const opt = document.createElement('option');
    opt.value = i + 1; opt.innerText = name;
    if (i === 3) opt.selected = true;
    mSel.appendChild(opt);
  });

  const dayNames = [
    "初一","初二","初三","初四","初五","初六","初七","初八","初九","初十",
    "十一","十二","十三","十四","十五","十六","十七","十八","十九","二十",
    "廿一","廿二","廿三","廿四","廿五","廿六","廿七","廿八","廿九","三十"
  ];
  dayNames.forEach((name, i) => {
    const opt = document.createElement('option');
    opt.value = i + 1; opt.innerText = name;
    if (i === 0) opt.selected = true;
    dSel.appendChild(opt);
  });
}

function onShichenSelectChanged(val, mode) {
  if (mode === 'solar') {
    document.getElementById('inputSolarTime').value = val;
  }
}

// 5. 城市级联联动
function initCityCascade() {
  const provSelect = document.getElementById('provinceSelect');
  onProvinceChanged(provSelect.value);
}

function onProvinceChanged(prov) {
  const citySelect = document.getElementById('citySelect');
  citySelect.innerHTML = '';
  const cities = CITY_DATABASE[prov] || [];
  cities.forEach((c, idx) => {
    const opt = document.createElement('option');
    opt.value = `${prov} ${c.name}|${c.lng}|${c.lat}`;
    opt.innerText = c.name;
    if (idx === 0) opt.selected = true;
    citySelect.appendChild(opt);
  });
  if (cities.length > 0) {
    onCityOptionChanged(citySelect.value);
  }
}

function onCityOptionChanged(val) {
  if (!val) return;
  const parts = val.split('|');
  const lng = parts[1];
  const lat = parts[2];
  document.getElementById('coordDisplay').innerText = `${lng}, ${lat}`;
  document.getElementById('customLng').value = lng;
  document.getElementById('customLat').value = lat;
}

// 6. 快捷键
function initShortcuts() {
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      triggerCalculate();
    }
  });
}

// 7. 本地档案管理
async function fetchProfiles() {
  try {
    const res = await fetch('/api/profiles');
    currentProfiles = await res.json();
    document.getElementById('profilesCountText').innerText = `自动同步 共 ${currentProfiles.length} 盘`;
    renderProfilesList(currentProfiles);
  } catch (err) {
    console.warn("无法拉取本地档案列表:", err);
  }
}

function renderProfilesList(list) {
  const container = document.getElementById('profilesContainer');
  if (!container) return;
  container.innerHTML = '';

  list.forEach(item => {
    const card = document.createElement('div');
    card.className = 'profile-record-card';
    card.innerHTML = `
      <div class="p-name-line">
        <span>${item.name} (${item.gender})</span>
        <span class="badge-mini">${item.city || '未知城市'}</span>
      </div>
      <div class="p-date-line">📅 ${item.birth_solar}</div>
      <div class="p-note-line">${item.note || '无备注'}</div>
    `;
    card.onclick = () => loadProfileIntoForm(item);
    container.appendChild(card);
  });
}

function loadProfileIntoForm(p) {
  document.getElementById('inputName').value = p.name || '某某';
  const radios = document.getElementsByName('gender');
  radios.forEach(r => r.checked = (r.value === p.gender));

  setCalendarMode('solar');
  if (p.birth_solar) {
    const [d, t] = p.birth_solar.split(' ');
    document.getElementById('inputSolarDate').value = d;
    document.getElementById('inputSolarTime').value = t;
  }
  if (p.lng) document.getElementById('customLng').value = p.lng;
  if (p.lat) document.getElementById('customLat').value = p.lat;
  document.getElementById('inputNote').value = p.note || '';

  document.querySelector('.tab-btn[data-tab="tab-bazi"]').click();
  triggerCalculate();
}

async function saveCurrentToProfiles() {
  const name = document.getElementById('inputName').value.trim() || '未命名';
  const gender = document.querySelector('input[name="gender"]:checked').value;
  const note = document.getElementById('inputNote').value.trim();
  const city = document.getElementById('citySelect').value.split('|')[0];
  const lng = parseFloat(document.getElementById('customLng').value) || 116.422;
  const lat = parseFloat(document.getElementById('customLat').value) || 39.935;
  const true_solar_enabled = document.getElementById('trueSolarToggle').checked;

  let birth_solar = "";
  if (currentChartData && currentChartData.profile) {
    birth_solar = currentChartData.profile.birth_solar;
  } else {
    birth_solar = `${document.getElementById('inputSolarDate').value} ${document.getElementById('inputSolarTime').value}`;
  }

  const payload = {
    name, gender, birth_solar, city, lng, lat, true_solar_enabled, note
  };

  try {
    const res = await fetch('/api/profiles/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      alert(`已成功保存【${name}】档案至本地电脑！`);
      fetchProfiles();
    }
  } catch (err) {
    alert("保存档案失败：" + err);
  }
}

// 8. 核心排盘计算请求
async function triggerCalculate() {
  const name = document.getElementById('inputName').value.trim() || '某某';
  const gender = document.querySelector('input[name="gender"]:checked').value;
  const city = document.getElementById('citySelect').value.split('|')[0];
  const lng = parseFloat(document.getElementById('customLng').value) || 116.422;
  const lat = parseFloat(document.getElementById('customLat').value) || 39.935;
  const true_solar_enabled = document.getElementById('trueSolarToggle').checked;

  let payload = {
    name, gender, calendar_type: currentCalendarMode,
    city, lng, lat, true_solar_enabled
  };

  if (currentCalendarMode === 'lunar') {
    payload.lunar_year = parseInt(document.getElementById('lunarYearSelect').value);
    payload.lunar_month = parseInt(document.getElementById('lunarMonthSelect').value);
    payload.lunar_day = parseInt(document.getElementById('lunarDaySelect').value);
    payload.is_leap = document.getElementById('lunarIsLeap').checked;
    const timeParts = document.getElementById('lunarShichenSelect').value.split(':');
    payload.hour = parseInt(timeParts[0]);
    payload.minute = parseInt(timeParts[1]);
  } else {
    payload.solar_date = document.getElementById('inputSolarDate').value;
    payload.solar_time = document.getElementById('inputSolarTime').value;
  }

  try {
    const res = await fetch('/api/bazi/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.error) {
      alert("排盘异常: " + data.error);
      return;
    }
    currentChartData = data;
    renderFullChart(data);
  } catch (err) {
    console.error("排盘计算接口失败:", err);
  }
}

function recalcCurrent() {
  triggerCalculate();
}

// 9. 全盘数据渲染
function renderFullChart(data) {
  const p = data.profile;
  const hdr = data.header;
  const pillars = data.pillars;
  const strength = data.strength;

  // 顶部 Header
  document.getElementById('hdrName').innerText = p.name;
  document.getElementById('hdrBazi').innerText = hdr.bazi_str;
  document.getElementById('hdrDayMaster').innerText = `日主 ${hdr.day_master}·${hdr.status}`;
  document.getElementById('hdrDayun').innerText = `当前大运: ${hdr.current_dayun}`;

  // 小白模式画卷
  document.getElementById('smHeroTitle').innerText = `${hdr.day_master} · ${hdr.status === '偏弱' ? '内敛蓄势 · 洞察破局者' : '敢打敢拼 · 赛博开拓先锋'}`;
  document.getElementById('smHeroDesc').innerText = 
    `生于${p.lunar}。你做事富有耐性与变通谋略，骨子里不服输。命带贵人护佑，擅长发挥专业本事变现，属于大器晚成且福泽长久的命格。`;

  // 命盘横幅
  document.getElementById('bigBaziTitle').innerText = hdr.bazi_str;
  document.getElementById('metaProfileText').innerText = 
    `${p.name} ${p.gender} ${p.city} ${p.birth_solar} (${p.lunar}) 面板排盘`;
  document.getElementById('dmTitle').innerText = `日主 ${hdr.day_master}`;
  document.getElementById('dmStatus').innerText = hdr.status;
  document.getElementById('dmScore').innerText = hdr.score;

  // 四柱卡片
  pillars.forEach((col, idx) => {
    document.getElementById(`p${idx}-shishen`).innerText = col.shishen;
    document.getElementById(`p${idx}-gan`).innerText = col.gan;
    document.getElementById(`p${idx}-gan`).style.color = col.gan_color;
    document.getElementById(`p${idx}-zhi`).innerText = col.zhi;
    document.getElementById(`p${idx}-zhi`).style.color = col.zhi_color;
    document.getElementById(`p${idx}-wx`).innerText = `${col.gan_wuxing}·${col.zhi_wuxing}`;
    document.getElementById(`p${idx}-nayin`).innerText = col.nayin;
    document.getElementById(`p${idx}-changsheng`).innerText = col.changsheng;
    document.getElementById(`p${idx}-kongwang`).innerText = col.kongwang.split(':').pop().trim();

    const cgContainer = document.getElementById(`p${idx}-canggan`);
    cgContainer.innerHTML = '';
    col.canggan.forEach(cg => {
      const pill = document.createElement('span');
      pill.className = 'canggan-pill';
      pill.innerHTML = `<span class="char" style="color:${cg.color}">${cg.gan}</span><span>${cg.shishen}</span>`;
      cgContainer.appendChild(pill);
    });
  });

  // 五行环与进度条
  renderWuxingDonut(strength.percentages, pillars[2].gan, hdr.score);
  renderWuxingBars(strength.percentages, strength.counts);

  // 日主旺衰半圆 Gauge
  renderStrengthGauge(hdr.score, hdr.status, strength.yue_status);

  // 十神分布排行
  renderShishenList(data.shishen_dist);

  // 神煞矩阵
  renderShenshaGrid(data.shensha);

  // 大运系统
  renderDayunSection(data.dayun, data.current_dayun);

  // 关键流年历史事件 (带锦囊)
  renderTimelineEvents(data.timeline_events);

  // 现实场景解读
  renderScenariosSection(data.scenarios);

  // 紫微斗数
  if (data.ziwei) {
    renderZiweiChart(data.ziwei);
  }

  // 打印报告填充
  renderPrintableReport(data);
}

// 10. 五行环 SVG
function renderWuxingDonut(pcts, dayGan, score) {
  const svg = document.getElementById('wuxingDonutSvg');
  const legend = document.getElementById('wuxingLegendGrid');
  if (!svg || !legend) return;

  document.getElementById('centerGan').innerText = dayGan;
  document.getElementById('centerSub').innerText = `${score >= 45 ? '偏旺' : '偏弱'} ${score}`;

  svg.innerHTML = '';
  legend.innerHTML = '';

  const wxOrder = ['木', '火', '土', '金', '水'];
  const colors = {
    '木': '#4ade80', '火': '#f87171', '土': '#fbbf24', '金': '#facc15', '水': '#60a5fa'
  };

  const cx = 80, cy = 80, r = 60, strokeWidth = 14;
  const circumference = 2 * Math.PI * r;
  let accumulatedPercent = 0;

  wxOrder.forEach(wx => {
    const val = pcts[wx] || 0;
    const strokeDasharray = `${(val / 100) * circumference} ${circumference}`;
    const strokeDashoffset = -((accumulatedPercent / 100) * circumference);

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', cx); circle.setAttribute('cy', cy); circle.setAttribute('r', r);
    circle.setAttribute('fill', 'none'); circle.setAttribute('stroke', colors[wx]);
    circle.setAttribute('stroke-width', strokeWidth);
    circle.setAttribute('stroke-dasharray', strokeDasharray);
    circle.setAttribute('stroke-dashoffset', strokeDashoffset);
    circle.setAttribute('transform', `rotate(-90 ${cx} ${cy})`);
    svg.appendChild(circle);

    accumulatedPercent += val;

    const legRow = document.createElement('div');
    legRow.className = 'legend-row';
    legRow.innerHTML = `
      <span class="legend-dot" style="background:${colors[wx]}"></span>
      <span style="color:${colors[wx]}">${wx}</span>
      <span>${val}%</span>
    `;
    legend.appendChild(legRow);
  });
}

function renderWuxingBars(pcts, counts) {
  const container = document.getElementById('wuxingProgressList');
  if (!container) return;
  container.innerHTML = '';

  const colors = {
    '木': '#4ade80', '火': '#f87171', '土': '#fbbf24', '金': '#facc15', '水': '#60a5fa'
  };

  ['木', '火', '土', '金', '水'].forEach(wx => {
    const pct = pcts[wx] || 0;
    const row = document.createElement('div');
    row.className = 'bar-row';
    row.innerHTML = `
      <span class="bar-lbl" style="color:${colors[wx]}">${wx}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width:${pct}%; background:${colors[wx]}"></div>
      </div>
      <span class="bar-val">${pct}%</span>
    `;
    container.appendChild(row);
  });

  const formula = document.getElementById('wuxingCountsFooter');
  if (formula && counts) {
    formula.innerText = `surface + hidden = 木${counts['木'] || 0} 火${counts['火'] || 0} 土${counts['土'] || 0} 金${counts['金'] || 0} 水${counts['水'] || 0}`;
  }
}

// 11. 日主旺衰仪表盘 (Gauge)
function renderStrengthGauge(score, status, yueStatus) {
  document.getElementById('gaugeNum').innerText = score;
  document.getElementById('gaugeStatus').innerText = status;
  document.getElementById('gaugeSeason').innerText = yueStatus;

  const arc = document.getElementById('gaugeActiveArc');
  if (arc) {
    const totalLen = 220;
    const progress = Math.min(100, Math.max(0, score)) / 100;
    const activeLen = totalLen * progress;
    arc.setAttribute('stroke-dasharray', `${activeLen} ${totalLen}`);
    arc.setAttribute('stroke', score >= 45 ? '#4ade80' : '#ea5455');
  }
}

// 12. 十神分布排行
function renderShishenList(dist) {
  const container = document.getElementById('shishenBarList');
  const countTag = document.getElementById('shishenCountTag');
  if (!container) return;
  container.innerHTML = '';
  if (countTag) countTag.innerText = `共 ${dist.length} 条`;

  dist.forEach(s => {
    const row = document.createElement('div');
    row.className = 'shishen-row';
    row.innerHTML = `
      <span class="ss-name">${s.name}</span>
      <div class="ss-track">
        <div class="ss-fill" style="width:${s.percentage}%"></div>
      </div>
      <span class="ss-pct">${s.percentage}%</span>
    `;
    container.appendChild(row);
  });
}

// 13. 神煞矩阵
function renderShenshaGrid(shenshaData) {
  const container = document.getElementById('shenshaGrid');
  const tag = document.getElementById('shenshaCountTag');
  if (!container) return;
  container.innerHTML = '';
  if (tag) tag.innerText = `命中 ${shenshaData.hit_count} / ${shenshaData.total}`;

  shenshaData.list.forEach(sh => {
    const chip = document.createElement('div');
    chip.className = `shensha-chip ${sh.hit ? 'hit' : ''}`;
    chip.innerHTML = `
      <div class="chip-name">${sh.name}</div>
      <div class="chip-pos">${sh.hit ? sh.pos : '未命中'}</div>
    `;
    chip.title = sh.desc || '';
    container.appendChild(chip);
  });
}

// 14. 大运演进与每步通俗详解
function renderDayunSection(dayuns, curDayun) {
  const strip = document.getElementById('dayunStrip');
  if (!strip) return;
  strip.innerHTML = '';

  dayuns.forEach(dy => {
    const card = document.createElement('div');
    card.className = `dayun-card ${curDayun && curDayun.gz === dy.gz ? 'active' : ''}`;
    card.innerHTML = `
      <div class="dy-gz">${dy.gz}</div>
      <div class="dy-age">${dy.start_age}岁起</div>
      <div class="dy-years">${dy.start_year}-${dy.start_year + 9}</div>
    `;
    card.onclick = () => {
      document.querySelectorAll('.dayun-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      renderDayunDeepCard(dy);
      renderLiunianBoxes(dy);
    };
    strip.appendChild(card);
  });

  if (curDayun) {
    renderDayunDeepCard(curDayun);
    renderLiunianBoxes(curDayun);
  }
}

function renderDayunDeepCard(dy) {
  const exp = dy.explanation;
  if (!exp) return;

  document.getElementById('deepDayunGz').innerText = `${exp.gz} (${exp.shishen}运)`;
  document.getElementById('deepDayunTitle').innerText = exp.title;
  document.getElementById('deepDayunSpan').innerText = exp.years_span;
  document.getElementById('deepDayunSummary').innerText = exp.summary;
  document.getElementById('deepDayunCareer').innerText = exp.career;
  document.getElementById('deepDayunWealth').innerText = exp.wealth;
  document.getElementById('deepDayunMindset').innerText = exp.mindset;
}

function renderLiunianBoxes(dayun) {
  const title = document.getElementById('currentSelectedDayunTitle');
  const grid = document.getElementById('liunianGrid');
  if (title) {
    title.innerText = `【${dayun.gz}运】(${dayun.start_year}–${dayun.start_year + 9}) 十年流年轮盘`;
  }
  if (!grid) return;
  grid.innerHTML = '';

  dayun.liunians.forEach(ln => {
    const box = document.createElement('div');
    box.className = 'liunian-box';
    box.innerHTML = `
      <div class="ln-year">${ln.year} (${ln.age}岁)</div>
      <div class="ln-gz">${ln.gz}</div>
      <div class="ln-ss">${ln.shishen}</div>
    `;
    grid.appendChild(box);
  });
}

function renderDayunCanvas(data) {
  const canvas = document.getElementById('dayunCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  ctx.strokeStyle = '#272832';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(40, h - 30);
  ctx.lineTo(w - 20, h - 30);
  ctx.stroke();

  const dayuns = data.dayun || [];
  if (dayuns.length === 0) return;

  const stepX = (w - 80) / Math.max(1, dayuns.length - 1);
  const points = [];

  dayuns.forEach((dy, i) => {
    const x = 50 + i * stepX;
    const scoreVal = 50 + Math.sin(i * 1.3) * 32 + (i % 2 === 0 ? 8 : -8);
    const y = h - 30 - (scoreVal / 100) * (h - 60);
    points.push({ x, y, gz: dy.gz, age: dy.start_age });
  });

  ctx.beginPath();
  points.forEach((pt, i) => {
    if (i === 0) ctx.moveTo(pt.x, pt.y);
    else {
      const prev = points[i - 1];
      const cx = (prev.x + pt.x) / 2;
      ctx.bezierCurveTo(cx, prev.y, cx, pt.y, pt.x, pt.y);
    }
  });
  ctx.strokeStyle = '#ea5455';
  ctx.lineWidth = 3;
  ctx.stroke();

  points.forEach(pt => {
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#8e909e';
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`${pt.gz}`, pt.x, pt.y - 12);
    ctx.fillText(`${pt.age}岁`, pt.x, h - 12);
  });
}

// 15. 关键流年历史事件推演 (带行动锦囊)
function renderTimelineEvents(events) {
  const container = document.getElementById('timelineEventsList');
  if (!container || !events) return;
  container.innerHTML = '';

  events.forEach((ev, idx) => {
    const card = document.createElement('div');
    card.className = 'timeline-event-card';

    const tagsHtml = ev.tags.map(t => `<span class="ev-tag">${t}</span>`).join(' ');

    // 渲染附带的化解锦囊
    let stratHtml = '';
    if (ev.strategies && ev.strategies.length > 0) {
      stratHtml = ev.strategies.map(st => `
        <div class="event-strategy-box">
          <div class="strategy-title">${st.title} · ${st.desc}</div>
          <ul class="strategy-list">
            ${st.actions.map(act => `<li>👉 ${act}</li>`).join('')}
          </ul>
        </div>
      `).join('');
    }

    card.innerHTML = `
      <div class="event-main-row">
        <div class="event-year-badge">
          <span class="ev-year">${ev.year}</span>
          <span class="ev-gz">${ev.gz}</span>
        </div>
        <div class="event-content-wrap">
          <div class="event-tags-row">
            <span style="font-size:11px; color:var(--text-sub);">大运: ${ev.dayun_gz || '--'} · 十神: ${ev.shishen}</span>
            ${tagsHtml}
          </div>
          <div class="ev-desc">${ev.event_description}</div>
        </div>
        <div class="event-feedback-group" id="fbGroup-${idx}">
          <button class="btn-fb" onclick="recordFeedback(${idx}, '准')">准</button>
          <button class="btn-fb" onclick="recordFeedback(${idx}, '部分准')">部分准</button>
          <button class="btn-fb" onclick="recordFeedback(${idx}, '不准')">不准</button>
        </div>
      </div>
      ${stratHtml}
    `;
    container.appendChild(card);
  });
}

function recordFeedback(idx, status) {
  const group = document.getElementById(`fbGroup-${idx}`);
  if (!group) return;
  const btns = group.querySelectorAll('.btn-fb');
  btns.forEach(b => {
    if (b.innerText === status) b.classList.add('active');
    else b.classList.remove('active');
  });

  const activeCount = document.querySelectorAll('.btn-fb.active').length;
  const accurateCount = Array.from(document.querySelectorAll('.btn-fb.active')).filter(b => b.innerText === '准' || b.innerText === '部分准').length;
  if (activeCount > 0) {
    const rate = Math.round((accurateCount / activeCount) * 100);
    document.getElementById('accRateText').innerText = `${rate}%`;
  }
}

// 16. 现实场景解读
function renderScenariosSection(sc) {
  if (!sc) return;

  document.getElementById('scWealthType').innerText = sc.wealth.type;
  document.getElementById('scWealthSummary').innerText = sc.wealth.summary;
  document.getElementById('scWealthCap').innerText = sc.wealth.details.capacity;
  document.getElementById('scWealthFirst').innerText = sc.wealth.details.first_bucket;
  document.getElementById('scWealthRisk').innerText = sc.wealth.details.partner_risk;
  document.getElementById('scWealthAsset').innerText = sc.wealth.details.asset_strategy;

  const careerGrid = document.getElementById('careerMatchGrid');
  if (careerGrid) {
    careerGrid.innerHTML = '';
    sc.wealth.careers.forEach(c => {
      const item = document.createElement('div');
      item.className = 'career-item';
      item.innerHTML = `
        <div class="wx-tag">【五行属${c.wuxing}】 契合度 ${c.match_rate}%</div>
        <div class="wx-fields">${c.fields}</div>
        <div class="wx-role">${c.role}</div>
      `;
      careerGrid.appendChild(item);
    });
  }

  document.getElementById('scSpouseZhi').innerText = `日支坐【${sc.marriage.spouse_zhi}】`;
  document.getElementById('scSpouseLooks').innerText = sc.marriage.spouse_looks;
  document.getElementById('scMarriageEncounter').innerText = sc.marriage.details.encounter;
  document.getElementById('scMarriagePersonality').innerText = sc.marriage.details.personality;
  document.getElementById('scMarriageCrisis').innerText = sc.marriage.details.crisis_cure;
  document.getElementById('scMarriageWindow').innerText = sc.marriage.details.golden_window;

  document.getElementById('scHealthWeak').innerText = `全盘五行偏弱：${sc.health.weak_wx}`;
  document.getElementById('scHealthOrgan').innerText = `对应脏腑潜伏病灶：${sc.health.organ}`;
  document.getElementById('scHealthLifestyle').innerText = `养生原则：${sc.health.lifestyle}`;
  document.getElementById('scHealthNishiTheory').innerText = sc.health.details.nishi_theory;
  document.getElementById('scHealthRiskYears').innerText = sc.health.details.risk_years;
  document.getElementById('scHealthFoodTherapy').innerText = sc.health.details.food_therapy;

  const mGrid = document.getElementById('monthsGrid');
  if (mGrid) {
    mGrid.innerHTML = '';
    sc.months_forecast.forEach((m) => {
      const mItem = document.createElement('div');
      mItem.className = 'month-item';
      mItem.innerHTML = `
        <div class="m-hdr">
          <span>${m.month}</span>
          <span class="m-score">${m.score}分</span>
        </div>
        <div class="m-desc">${m.desc}</div>
        <div class="m-detail">${m.detail}</div>
      `;
      mItem.onclick = () => mItem.classList.toggle('expanded');
      mGrid.appendChild(mItem);
    });
  }

  document.getElementById('scPlanWx').innerText = sc.fortune_plan.useful_wx.join(' / ');
  document.getElementById('scPlanColors').innerText = sc.fortune_plan.colors;
  document.getElementById('scPlanDirs').innerText = sc.fortune_plan.directions;
  document.getElementById('scPlanNums').innerText = sc.fortune_plan.numbers;
  document.getElementById('scPlanOrnaments').innerText = sc.fortune_plan.ornaments;
  document.getElementById('scPlanFengshui').innerText = sc.fortune_plan.fengshui_detail;
}

// 17. 双人合盘计算前端逻辑
function populateHepanSelects() {
  const selA = document.getElementById('hepanSelectA');
  const selB = document.getElementById('hepanSelectB');
  if (!selA || !selB) return;

  selA.innerHTML = '';
  selB.innerHTML = '';

  currentProfiles.forEach((p, idx) => {
    const optA = document.createElement('option');
    optA.value = idx; optA.innerText = `${p.name} (${p.gender})`;
    selA.appendChild(optA);

    const optB = document.createElement('option');
    optB.value = idx; optB.innerText = `${p.name} (${p.gender})`;
    if (idx === 1) optB.selected = true;
    selB.appendChild(optB);
  });
}

async function triggerHepanCalculate() {
  const idxA = parseInt(document.getElementById('hepanSelectA').value) || 0;
  const idxB = parseInt(document.getElementById('hepanSelectB').value) || 0;

  const profA = currentProfiles[idxA];
  const profB = currentProfiles[idxB];
  if (!profA || !profB) return;

  // 快捷发起两人的排盘再合盘
  try {
    const resA = await fetch('/api/bazi/calculate', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ solar_date: profA.birth_solar.split(' ')[0], solar_time: profA.birth_solar.split(' ')[1], gender: profA.gender })
    });
    const chartA = await resA.json();

    const resB = await fetch('/api/bazi/calculate', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ solar_date: profB.birth_solar.split(' ')[0], solar_time: profB.birth_solar.split(' ')[1], gender: profB.gender })
    });
    const chartB = await resB.json();

    const hepanRes = await fetch('/api/hepan/calculate', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ chart_a: chartA, chart_b: chartB })
    });
    const hpData = await hepanRes.json();

    renderHepanResult(hpData);
  } catch (err) {
    alert("合盘计算失败: " + err);
  }
}

function renderHepanResult(data) {
  const box = document.getElementById('hepanResultBox');
  if (!box) return;
  box.style.display = 'block';

  document.getElementById('hpScoreVal').innerText = data.score;
  document.getElementById('hpLevelVal').innerText = data.level;
  document.getElementById('hpAdviceVal').innerText = data.advice;

  const prosList = document.getElementById('hpProsList');
  prosList.innerHTML = data.pros.map(p => `<li>${p}</li>`).join('');

  const consList = document.getElementById('hpConsList');
  consList.innerHTML = data.cons.map(c => `<li>${c}</li>`).join('');
}

// 18. 紫微斗数十二宫星盘
function renderZiweiChart(ziwei) {
  const grid = document.getElementById('ziweiGrid');
  if (!grid) return;
  grid.innerHTML = '';

  const wuxingJu = ziwei.wuxing_ju || {};
  const mingGong = ziwei.ming_gong || {};
  document.getElementById('zwJuName').innerText = `${wuxingJu.name || '五行局'} · 命宫坐${mingGong.branch || '未'}`;

  const palaces = ziwei.palaces || [];
  const layoutOrder = [
    5, 6, 7, 8,
    4, -1, -1, 9,
    3, -1, -1, 10,
    2, 1, 0, 11
  ];

  layoutOrder.forEach(idx => {
    if (idx === -1) {
      if (!grid.querySelector('.center-placeholder')) {
        const center = document.createElement('div');
        center.className = 'ziwei-palace-cell center-placeholder';
        center.innerHTML = `
          <div style="font-family:'Noto Serif SC',serif; font-size:17px; color:var(--text-main); font-weight:700;">天枢台 · 紫微中宫</div>
          <div style="font-size:10.5px; color:var(--text-sub); margin-top:3px;">倪海厦《天纪》正宗斗数星盘</div>
          <div style="font-size:10px; color:var(--accent-gold); margin-top:6px;">命主: ${ziwei.ming_zhu || '武曲'} | 身主: ${ziwei.shen_zhu || '天相'}</div>
        `;
        grid.appendChild(center);
      }
      return;
    }

    const p = palaces[idx] || {};
    const cell = document.createElement('div');
    cell.className = 'ziwei-palace-cell';
    
    const majorStars = (p.major_stars || []).map(s => `<span style="color:#f87171; font-weight:600;">${s}</span>`).join(' ');
    const minorStars = (p.minor_stars || []).slice(0, 3).map(s => `<span style="color:#facc15;">${s}</span>`).join(' ');
    
    let sihuaBadge = '';
    if (p.sihua && p.sihua.length > 0) {
      sihuaBadge = p.sihua.map(sh => `<span style="background:var(--accent-red); color:#fff; font-size:9px; padding:1px 3px; border-radius:2px; margin-left:2px;">${sh.type}</span>`).join('');
    }

    cell.innerHTML = `
      <div class="p-name">${p.name || '宫位'} (${p.branch || ''}) ${sihuaBadge}</div>
      <div class="p-stars">${majorStars || '<span style="color:var(--text-sub);">空宫</span>'} ${minorStars}</div>
      <div class="p-footer">
        <span>${p.stem || ''}${p.branch || ''}</span>
        <span>${p.decadal ? p.decadal.start_age + '岁起' : ''}</span>
      </div>
    `;

    cell.onclick = () => {
      document.querySelectorAll('.ziwei-palace-cell').forEach(c => c.classList.remove('active'));
      cell.classList.add('active');
      showZiweiPalaceDetail(p, ziwei);
    };

    grid.appendChild(cell);
  });
}

function showZiweiPalaceDetail(palace, ziwei) {
  document.getElementById('zwDetailPalaceName').innerText = `【${palace.name}】(${palace.stem}${palace.branch}宫)`;
  const stars = (palace.major_stars || []).concat(palace.minor_stars || []).join('、');
  document.getElementById('zwDetailStars').innerText = `汇聚星宿：${stars || '无主星 (借对宫看)'}`;

  const palaceTexts = {
    '命宫': "《紫微斗数全书》云：命宫为一生荣辱之总领。倪师在《天纪》中强调：命宫代表先天气度与秉赋，若会吉星则格局清贵，纵逢煞曜亦能绝处逢生，重在修心行善化解刚煞。",
    '财帛': "财帛宫主管一生进财与用度。若坐禄存或化禄，主经商求财丰厚；若坐武曲天府，为财库充盈之象；若逢火星擎羊，谨防过手钱财虚浮。",
    '官禄': "官禄宫主事业志向与功名职位。倪师云：‘官禄宫有天梁天相者利公职，有杀破狼者利开辟江山’，凡事顺应天时，必能名扬四方。",
    '夫妻': "夫妻宫主正缘伴侣与婚姻造化。坐天同主配偶温和贤淑，坐七杀主另一半威严有主见。倪师提醒：婚姻若遇煞星莫惊慌，聚少离多或晚婚即可巧妙化煞。",
    '迁移': "迁移宫主远行差旅与外境贵人。见天马、天魁者，离乡创业大有作为，在外人缘极广。",
    '福德': "福德宫主精神世界与晚年福禄。紫微天相坐守主心宽体胖，思维开阔；逢化忌者易多思忧虑，宜多近山水自然。",
    '疾厄': "疾厄宫结合宫位地支与杀星，透视先天体质薄弱处。倪师天纪法门主‘调其阴阳，避其偏枯’，日常饮食规律即是良方。"
  };

  const exp = palaceTexts[palace.name] || `此宫为【${palace.name}】，干支为${palace.stem}${palace.branch}。在倪师《天纪》体系中，需结合其三方四正综合研判，相生则吉，相克则需以人事修持弥补。`;
  document.getElementById('zwDetailExplanation').innerText = exp;
}

// 19. 手机海报长图生成 (Canvas)
function openSharePosterModal() {
  document.getElementById('posterModal').classList.add('open');
  drawSharePosterCanvas();
}

function closeSharePosterModal() {
  document.getElementById('posterModal').classList.remove('open');
}

function drawSharePosterCanvas() {
  const canvas = document.getElementById('sharePosterCanvas');
  if (!canvas || !currentChartData) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  // 背景渐变
  const grad = ctx.createLinearGradient(0, 0, w, h);
  grad.addColorStop(0, '#0c0d10');
  grad.addColorStop(1, '#1b1c24');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);

  // 外边框线与古典边角
  ctx.strokeStyle = '#e5a952';
  ctx.lineWidth = 2;
  ctx.strokeRect(20, 20, w - 40, h - 40);

  // 标题
  ctx.fillStyle = '#ea5455';
  ctx.font = 'bold 22px "Noto Serif SC", serif';
  ctx.textAlign = 'center';
  ctx.fillText('天 枢 台 · 命 理 中 心', w / 2, 70);

  ctx.fillStyle = '#8e909e';
  ctx.font = '12px sans-serif';
  ctx.fillText('赛 博 命 运 使 用 说 明 书', w / 2, 95);

  // 姓名与四柱
  const p = currentChartData.profile;
  const hdr = currentChartData.header;
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 20px "Noto Serif SC", serif';
  ctx.fillText(`命主：${p.name} (${p.gender})`, w / 2, 140);

  ctx.fillStyle = '#e5a952';
  ctx.font = 'bold 24px "Noto Serif SC", serif';
  ctx.fillText(hdr.bazi_str, w / 2, 175);

  // 分隔线
  ctx.strokeStyle = '#272832';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(40, 205); ctx.lineTo(w - 40, 205);
  ctx.stroke();

  // 命运型号
  ctx.fillStyle = '#ea5455';
  ctx.font = 'bold 15px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('⚡ 核心命运型号：', 50, 240);

  ctx.fillStyle = '#ffffff';
  ctx.font = '14px sans-serif';
  ctx.fillText(`${hdr.day_master} · ${hdr.status === '偏弱' ? '内敛蓄势 · 洞察破局型' : '自燃开拓 · 赛博先锋型'}`, 50, 270);

  // 核心天赋
  ctx.fillStyle = '#e5a952';
  ctx.font = 'bold 15px sans-serif';
  ctx.fillText('🌟 三大人生命格配置：', 50, 320);

  ctx.fillStyle = '#cccccc';
  ctx.font = '13px sans-serif';
  ctx.fillText('1. 偏财有根：商业与副业商机嗅觉极高', 50, 350);
  ctx.fillText('2. 文昌入命：善于借才艺、技术、名誉变现', 50, 375);
  ctx.fillText('3. 岁运流通：逆境耐力强，后劲绵延大器晚成', 50, 400);

  // 避坑锦囊
  ctx.fillStyle = '#f87171';
  ctx.font = 'bold 15px sans-serif';
  ctx.fillText('⚠️ 待机运行戒律 (避坑锦囊)：', 50, 450);

  ctx.fillStyle = '#cccccc';
  ctx.font = '13px sans-serif';
  ctx.fillText('• 严禁借贷担保，合伙生意必须财务日结', 50, 480);
  ctx.fillText('• 遇动荡对冲年份，宜主动买房置产以应破财', 50, 505);
  ctx.fillText('• 凡事留有余地，修心戒急躁可长享福禄', 50, 530);

  // 开运磁场
  ctx.fillStyle = '#4ade80';
  ctx.font = 'bold 15px sans-serif';
  ctx.fillText('🔮 专属开运磁场：', 50, 580);

  ctx.fillStyle = '#cccccc';
  ctx.font = '13px sans-serif';
  const sc = currentChartData.scenarios;
  if (sc) {
    ctx.fillText(`• 幸运穿搭：${sc.fortune_plan.colors}`, 50, 610);
    ctx.fillText(`• 吉利方位：${sc.fortune_plan.directions}`, 50, 635);
    ctx.fillText(`• 幸运数理：${sc.fortune_plan.numbers}`, 50, 660);
  }

  // 底部印章与二维码说明
  ctx.fillStyle = '#606270';
  ctx.font = '11px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('承 传 经 典 · 知 命 达 观 · 天 枢 台 敬 呈', w / 2, 730);
  ctx.fillText('DeepSeek Harness · Cyber Mingli Engine', w / 2, 750);
}

function downloadSharePoster() {
  const canvas = document.getElementById('sharePosterCanvas');
  if (!canvas) return;
  const link = document.createElement('a');
  link.download = `天枢台_命运说明书_${currentChartData ? currentChartData.profile.name : '命主'}.jpg`;
  link.href = canvas.toDataURL('image/jpeg', 0.95);
  link.click();
}

// 20. 打印报告
function renderPrintableReport(data) {
  const p = data.profile;
  const hdr = data.header;
  const pillars = data.pillars;

  document.getElementById('repSubTitle').innerText = 
    `${hdr.bazi_str} · ${p.name} (${p.gender}) 命造全书详鉴`;

  const tbl = document.getElementById('repBaziTable');
  if (tbl) {
    tbl.innerHTML = `
      <table>
        <tr><th>四柱</th><th>年柱</th><th>月柱</th><th>日柱 (元神)</th><th>时柱</th></tr>
        <tr><td><strong>十神</strong></td><td>${pillars[0].shishen}</td><td>${pillars[1].shishen}</td><td>日主</td><td>${pillars[3].shishen}</td></tr>
        <tr><td><strong>干支</strong></td><td>${pillars[0].gz}</td><td>${pillars[1].gz}</td><td>${pillars[2].gz}</td><td>${pillars[3].gz}</td></tr>
        <tr><td><strong>纳音</strong></td><td>${pillars[0].nayin}</td><td>${pillars[1].nayin}</td><td>${pillars[2].nayin}</td><td>${pillars[3].nayin}</td></tr>
        <tr><td><strong>星运</strong></td><td>${pillars[0].changsheng}</td><td>${pillars[1].changsheng}</td><td>${pillars[2].changsheng}</td><td>${pillars[3].changsheng}</td></tr>
      </table>
    `;
  }

  document.getElementById('repStrengthAnalysis').innerText = 
    `日元【${pillars[2].gan}木】得令于${pillars[1].zhi}月，全局五行能量比值为：木 ${data.strength.percentages['木']}%、火 ${data.strength.percentages['火']}%、土 ${data.strength.percentages['土']}%、金 ${data.strength.percentages['金']}%、水 ${data.strength.percentages['水']}%。综合评分 ${hdr.score}，归属于【${hdr.status}】格局。以${data.strength.parent_wx}为印星生身，以${data.strength.wealth_wx}为财星流转，生化有情。`;

  if (data.scenarios) {
    document.getElementById('repWealthText').innerText = data.scenarios.wealth.summary;
    document.getElementById('repMarriageText').innerText = 
      `配偶坐于【${pillars[2].zhi}】位，主伴侣${data.scenarios.marriage.spouse_looks}。相处真言：${data.scenarios.marriage.details.crisis_cure}`;
    document.getElementById('repHealthText').innerText = 
      `全盘五行偏弱于【${data.scenarios.health.weak_wx}】，主要需预防${data.scenarios.health.organ}等方面的虚劳。${data.scenarios.health.details.nishi_theory}`;
    document.getElementById('repDayunText').innerText = 
      `当前正行【${hdr.current_dayun}】大运。大运乃十年之总枢纽，顺之则事半功倍，逆之则耗心劳力。近三年当乘天枢吉照，深耕专业。`;
  }
}

// 21. 问命盘师 (AI 抽屉)
function initDrawerChat() {
  const openBtn = document.getElementById('openChatBtn');
  const closeBtn = document.getElementById('closeChatBtn');
  const drawer = document.getElementById('chatDrawer');

  if (openBtn) {
    openBtn.addEventListener('click', () => drawer.classList.add('open'));
  }
  if (closeBtn) {
    closeBtn.addEventListener('click', () => drawer.classList.remove('open'));
  }
}

function handleChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendChatMessage();
  }
}

function sendQuickQuestion(q) {
  document.getElementById('chatInput').value = q;
  sendChatMessage();
}

async function sendChatMessage() {
  const input = document.getElementById('chatInput');
  const msgText = input.value.trim();
  if (!msgText) return;

  const msgContainer = document.getElementById('chatMessages');

  const userDiv = document.createElement('div');
  userDiv.className = 'chat-msg user';
  userDiv.innerHTML = `<div class="msg-bubble">${msgText}</div>`;
  msgContainer.appendChild(userDiv);

  input.value = '';
  msgContainer.scrollTop = msgContainer.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: msgText,
        chart: currentChartData || {}
      })
    });
    const data = await res.json();

    const aiDiv = document.createElement('div');
    aiDiv.className = 'chat-msg ai';

    let citationsHtml = '';
    if (data.citations && data.citations.length > 0) {
      const cite = data.citations[Math.floor(Math.random() * data.citations.length)];
      citationsHtml = `<div class="citation-card"><strong>【古籍引证】</strong> ${cite.book}：${cite.text}</div>`;
    }

    aiDiv.innerHTML = `
      <div class="msg-bubble">
        ${data.reply.replace(/\n/g, '<br>')}
        ${citationsHtml}
      </div>
    `;
    msgContainer.appendChild(aiDiv);
    msgContainer.scrollTop = msgContainer.scrollHeight;
  } catch (err) {
    const errDiv = document.createElement('div');
    errDiv.className = 'chat-msg ai';
    errDiv.innerHTML = `<div class="msg-bubble" style="color:#ff8585;">通讯受阻，请稍后再试。</div>`;
    msgContainer.appendChild(errDiv);
  }
}

// 22. 示例选择弹窗
function showExamplePicker() {
  const names = currentProfiles.map((p, i) => `${i + 1}. ${p.name} (${p.city || ''}) - ${p.note || ''}`).join('\n');
  const choice = prompt(`请选择要载入的档案序号：\n${names}\n\n请输入数字 (如 1 或 2)：`, "1");
  if (choice) {
    const idx = parseInt(choice) - 1;
    if (currentProfiles[idx]) {
      loadProfileIntoForm(currentProfiles[idx]);
    }
  }
}
