import { existsSync, readFileSync } from 'node:fs'
import { networkInterfaces } from 'node:os'
import { join } from 'node:path'
import { app } from 'electron'

const DEFAULT_HOST = '127.0.0.1'
const DEFAULT_PORT = 8765

export interface BackendEndpoints {
  bindHost: string
  port: number
  url: string
  wsUrl: string
  lanUrl?: string
  udpPort?: number
}

/** Repo root (parent of electron/) — matches Python dev backend cwd. */
export function projectRoot(): string {
  return join(__dirname, '..', '..', '..')
}

function validIpv4(host: string): boolean {
  const parts = host.split('.')
  if (parts.length !== 4)
    return false
  return parts.every((p) => {
    const n = Number(p)
    return Number.isInteger(n) && n >= 0 && n <= 255
  })
}

function localLanIp(): string | undefined {
  const nets = networkInterfaces()
  for (const entries of Object.values(nets)) {
    for (const net of entries ?? []) {
      if (net.family === 'IPv4' && !net.internal)
        return net.address
    }
  }
  return undefined
}

function configCandidates(backendCwd?: string): string[] {
  const paths: string[] = []
  if (app.isPackaged) {
    paths.push(join(process.resourcesPath, 'backend', 'tcu_config.json'))
    const appData = process.env.APPDATA
    if (appData)
      paths.push(join(appData, 'VirtualTCU', 'tcu_config.json'))
  }
  paths.push(join(projectRoot(), 'tcu_config.json'))
  if (backendCwd)
    paths.push(join(backendCwd, 'tcu_config.json'))
  paths.push(join(process.cwd(), 'tcu_config.json'))
  return [...new Set(paths)]
}

function readStoredConfig(backendCwd?: string): {
  web_host?: string
  web_port?: number
  udp_port?: number
} {
  for (const path of configCandidates(backendCwd)) {
    if (!existsSync(path))
      continue
    try {
      const raw = readFileSync(path, 'utf-8')
      const parsed = JSON.parse(raw) as {
        web_host?: string
        web_port?: number
        udp_port?: number
      }
      return parsed
    }
    catch {
      /* try next */
    }
  }
  return {}
}

export function parseWebUiUrl(text: string): string | null {
  // Matches both startup ("Web UI at ...") and rebind ("Web UI rebound at
  // ...") log lines so cached endpoints stay fresh after the user changes the
  // bind from the settings panel.
  const match = text.match(/\[OK\] Web UI(?: rebound)? at (https?:\/\/[^\s,]+)/i)
  return match?.[1] ?? null
}

export function endpointsFromHttpUrl(httpUrl: string, fallback?: BackendEndpoints): BackendEndpoints {
  const u = new URL(httpUrl)
  const port = u.port ? Number(u.port) : DEFAULT_PORT
  const clientHost = u.hostname
  const bindHost = fallback?.bindHost ?? clientHost
  const wsUrl = `ws://${clientHost}:${port}/ws`

  let lanUrl: string | undefined
  if (bindHost === '0.0.0.0') {
    const lanIp = localLanIp()
    if (lanIp)
      lanUrl = `http://${lanIp}:${port}`
  }
  else if (bindHost !== '127.0.0.1') {
    lanUrl = `http://${bindHost}:${port}`
  }

  return {
    bindHost,
    port,
    url: httpUrl,
    wsUrl,
    lanUrl,
    udpPort: fallback?.udpPort,
  }
}

export function resolveBackendEndpoints(backendCwd?: string): BackendEndpoints {
  const stored = readStoredConfig(backendCwd)
  let bindHost = String(stored.web_host ?? DEFAULT_HOST).trim()
  if (!validIpv4(bindHost))
    bindHost = DEFAULT_HOST

  let port = Number(stored.web_port ?? DEFAULT_PORT)
  if (!Number.isInteger(port) || port < 1024 || port > 65535)
    port = DEFAULT_PORT

  const clientHost = bindHost === '0.0.0.0' ? '127.0.0.1' : bindHost
  const url = `http://${clientHost}:${port}`
  const endpoints = endpointsFromHttpUrl(url)
  endpoints.bindHost = bindHost
  endpoints.udpPort = stored.udp_port
  return endpoints
}
