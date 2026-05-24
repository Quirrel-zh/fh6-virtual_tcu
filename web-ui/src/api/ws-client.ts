import type { WsInbound, WsOutbound } from '@/types/ws'

export type MessageHandler = (msg: WsInbound) => void
export type ConnectionHandler = (open: boolean) => void

export class TcuWsClient {
  private ws: WebSocket | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private handler: MessageHandler | null = null
  private connectionHandler: ConnectionHandler | null = null
  private url: string
  private gotInit = false

  constructor(url?: string) {
    this.url = url ?? TcuWsClient.defaultUrl()
  }

  setUrl(url: string) {
    if (url === this.url)
      return
    this.url = url
    this.gotInit = false
    this.disconnect()
    this.connect()
  }

  getUrl() {
    return this.url
  }

  static defaultUrl(): string {
    const isElectron = typeof window !== 'undefined' && (window as { isElectron?: boolean }).isElectron
    if (isElectron || location.protocol === 'file:' || !location.host)
      return 'ws://127.0.0.1:8765/ws'
    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    return `${proto}://${location.host}/ws`
  }

  onMessage(handler: MessageHandler) {
    this.handler = handler
  }

  onConnectionChange(handler: ConnectionHandler) {
    this.connectionHandler = handler
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING)
      return

    this.gotInit = false
    this.ws = new WebSocket(this.url)
    this.ws.onopen = () => {
      this.connectionHandler?.(true)
    }
    this.ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data as string) as WsInbound
        if (msg.type === 'init')
          this.gotInit = true
        this.handler?.(msg)
      }
      catch {
        /* ignore malformed */
      }
    }
    this.ws.onclose = () => {
      this.gotInit = false
      this.connectionHandler?.(false)
      this.scheduleReconnect()
    }
    this.ws.onerror = () => this.ws?.close()
  }

  send(msg: WsOutbound) {
    if (this.ws?.readyState === WebSocket.OPEN)
      this.ws.send(JSON.stringify(msg))
  }

  get connected() {
    return this.ws?.readyState === WebSocket.OPEN && this.gotInit
  }

  get socketOpen() {
    return this.ws?.readyState === WebSocket.OPEN
  }

  disconnect() {
    if (this.reconnectTimer)
      clearTimeout(this.reconnectTimer)
    this.reconnectTimer = null
    this.gotInit = false
    this.ws?.close()
    this.ws = null
  }

  private scheduleReconnect() {
    if (this.reconnectTimer)
      clearTimeout(this.reconnectTimer)
    this.reconnectTimer = setTimeout(() => this.connect(), 1500)
  }
}
