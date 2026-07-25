// src/lib/api/host.ts — host-side process + network introspection.
import { jsonFetch } from './base';

export interface HostProcess {
  pid: number;
  user: string;
  pcpu: number;
  pmem: number;
  rss_mb: number;
  comm: string;
  cmd: string;
}

export interface HostProcessesResponse {
  processes: HostProcess[];
  ts: string;
  ok: boolean;
  error?: string | null;
}

export interface TailscalePeer {
  hostname?: string;
  dns_name?: string;
  os?: string;
  ip?: string;
  online?: boolean;
  last_seen?: string;
  rx_bytes?: number;
  tx_bytes?: number;
}

export interface HostInterface {
  name: string;
  state?: string;
  addrs: string[];
  mac?: string;
  mtu?: number;
}

export interface HostNetworkResponse {
  tailscale: {
    self: TailscalePeer;
    peers: TailscalePeer[];
    raw?: string | null;
    ok: boolean;
    error?: string | null;
  };
  interfaces: HostInterface[];
  ts: string;
}

export function hostProcesses(limit = 40): Promise<HostProcessesResponse> {
  return jsonFetch(`/zeus-os/sys/processes?limit=${limit}`);
}

export function hostNetwork(): Promise<HostNetworkResponse> {
  return jsonFetch('/zeus-os/sys/network');
}
