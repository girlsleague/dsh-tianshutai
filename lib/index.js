/**
 * 天枢台 (dsh-tianshutai) — Host 半侧
 *
 * 在 DSH 宿主进程内：
 * 1) 拉起 Python 命理引擎子进程 (server/app.py)，监听一个内部端口；
 * 2) 通过 ctx.webServer 注册 /dsh-tianshutai/* 前缀路由，
 *    把请求反向代理到本地 Python 服务；
 * 3) 浏览器半侧 (./client) 负责在侧边栏注册入口与主面板 iframe。
 *
 * Python 依赖 (lunar_python) 若缺失，会在启动时给出清晰的诊断提示，
 * 而不影响 DSH 主进程。
 */

import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import http from 'node:http'

export const name = 'dsh-tianshutai'

/** 包根目录 */
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)))

/** Python 服务监听端口（可用环境变量覆盖） */
const PY_PORT = Number(process.env.TIANSHU_PORT || 58766)
/** 对外暴露的 HTTP 路由前缀 */
const ROUTE_PREFIX = '/dsh-tianshutai'

/** 已启动的 Python 子进程句柄 */
let pyProc = null
let pyReady = false
let pyError = ''

/** 解析可用的 python 解释器 */
function resolvePython() {
  const candidates = [
    process.env.TIANSHU_PYTHON,
    // DSH 运行时自带 python
    path.join(process.env.USERPROFILE || '', '.dsh', 'dsh-runtimes', 'dsh-primary-runtime', 'dependencies', 'python', 'python.exe'),
    'python',
    'python3',
  ].filter(Boolean)
  for (const c of candidates) {
    if (c === 'python' || c === 'python3') return c
    if (existsSync(c)) return c
  }
  return 'python'
}

/** 启动 Python 命理引擎 */
function startPython() {
  const script = path.join(ROOT, 'server', 'app.py')
  if (!existsSync(script)) {
    pyError = `未找到服务器脚本: ${script}`
    return
  }
  const py = resolvePython()
  const env = { ...process.env, TIANSHU_PORT: String(PY_PORT) }
  try {
    pyProc = spawn(py, [script], { env, cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] })
    pyProc.stdout?.on('data', (d) => console.log(`[tianshutai] ${d.toString().trim()}`))
    pyProc.stderr?.on('data', (d) => {
      const msg = d.toString()
      console.warn(`[tianshutai:py] ${msg.trim()}`)
      if (/ModuleNotFoundError|No module named/.test(msg)) {
        pyError = 'Python 依赖缺失：请执行 `pip install lunar_python` 后重启 DSH。'
      }
    })
    pyProc.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        console.warn(`[tianshutai] Python 引擎退出，code=${code}`)
        pyReady = false
      }
    })
    // 轮询等待就绪
    let tries = 0
    const probe = () => {
      const req = http.get({ host: '127.0.0.1', port: PY_PORT, path: '/api/status', timeout: 800 }, (res) => {
        res.resume()
        if (res.statusCode === 200) { pyReady = true; return }
        retry()
      })
      req.on('error', retry)
      req.on('timeout', () => { req.destroy(); retry() })
    }
    const retry = () => {
      tries += 1
      if (tries < 40 && !pyReady) setTimeout(probe, 300)
    }
    probe()
  } catch (e) {
    pyError = String(e)
  }
}

/** 反代到本地 Python 服务 */
function proxyHandler(request, response) {
  if (!pyReady) {
    response.writeHead(503, { 'content-type': 'application/json; charset=utf-8' })
    response.end(JSON.stringify({
      error: pyError || '天枢台引擎正在启动中，请稍候刷新…',
      hint: '首次启动约需 2~3 秒；若持续失败请确认已安装 lunar_python。'
    }))
    return
  }
  const url = request.url || '/'
  // 去掉前缀，转发到 Python 根路径
  const forwardPath = url.startsWith(ROUTE_PREFIX) ? url.slice(ROUTE_PREFIX.length) || '/' : url

  const proxyReq = http.request({
    host: '127.0.0.1',
    port: PY_PORT,
    path: forwardPath,
    method: request.method,
    headers: { ...request.headers, host: `127.0.0.1:${PY_PORT}` },
  }, (proxyRes) => {
    response.writeHead(proxyRes.statusCode || 502, proxyRes.headers)
    proxyRes.pipe(response)
  })
  proxyReq.on('error', (e) => {
    response.writeHead(502, { 'content-type': 'text/plain; charset=utf-8' })
    response.end(`天枢台代理错误: ${e.message}`)
  })
  request.pipe(proxyReq)
}

/**
 * Cordis 插件入口
 */
export function apply(ctx) {
  startPython()
  ctx.inject(['webServer'], (hostCtx) => {
    hostCtx.webServer.register({
      kind: 'prefix',
      path: ROUTE_PREFIX,
      handler: proxyHandler,
    })
    console.log('[tianshutai] 已注册路由前缀 ' + ROUTE_PREFIX)
  })

  ctx.effect(() => () => {
    if (pyProc && !pyProc.killed) {
      try { pyProc.kill() } catch { /* noop */ }
    }
  })
}
