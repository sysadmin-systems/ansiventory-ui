export interface Workspace {
  id: number
  slug: string
  name: string
  created_at: string
}

export interface Host {
  id: number
  workspace_id: number
  hostname: string
  ip_address: string | null
  municipio: string | null
  ambiente: 'azure' | 'digitalocean' | 'onprem' | null
  ativo: boolean
  vars: Record<string, unknown>
  updated_at: string
  grupos: string[]
}

export interface Grupo {
  id: number
  workspace_id: number
  nome: string
  vars: Record<string, unknown>
  updated_at: string
}

export interface VarDetail {
  value: unknown
  source: 'host' | 'group'
  group?: string      // grupo de origem (quando source = 'group')
  overrides?: string  // grupo que está sendo sobrescrito (quando source = 'host')
}

export interface HostVars {
  hostname: string
  vars_final: Record<string, unknown>
  vars_detail: Record<string, VarDetail>
}

export interface AuditLog {
  id: number
  host_id: number | null
  action: 'create' | 'update' | 'delete'
  diff: Record<string, unknown> | null
  changed_by: string
  changed_at: string
}
