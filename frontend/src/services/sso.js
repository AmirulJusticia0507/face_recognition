import axios from 'axios'
import { push } from 'notivue'
import router from '../router'
import { useAuthStore } from '../stores/auth'

const tokenUrl = import.meta.env.VITE_SSO_TOKEN_URL || 'https://sso.jogjaprov.go.id/realms/aptika/protocol/openid-connect/token'
const userinfoUrl = import.meta.env.VITE_SSO_USERINFO_URL || 'https://sso.jogjaprov.go.id/realms/aptika/protocol/openid-connect/userinfo'
const scope = import.meta.env.VITE_SSO_SCOPE || 'openid'
const keycloakBase = import.meta.env.VITE_SSO_KEYCLOAK_BASE || 'https://sso.jogjaprov.go.id/realms/aptika/protocol/openid-connect'

export const getLoginRedirectUri = () => {
  if (typeof window !== 'undefined') {
    return new URL('/login', window.location.origin).toString()
  }
  return ''
}

/**
 * Resolve redirect path setelah login.
 * Hanya menerima path internal (dimulai dengan /) untuk mencegah open redirect.
 */
export function resolvePostLoginRedirect() {
  const params = new URLSearchParams(window.location.search)
  const redirect = params.get('redirect')
  if (redirect && redirect.startsWith('/') && !redirect.startsWith('//')) {
    return redirect
  }
  return '/'
}

export async function goGoogleLogin() {
  const redirectUri = getLoginRedirectUri()
  const params = new URLSearchParams({
    client_id: 'portal',
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: 'openid profile email',
    kc_idp_hint: 'google',
  })
  window.location.href = `${keycloakBase}/auth?${params.toString()}`
}

export async function submitSSOLogin(username, password, totp) {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  form.append('client_id', import.meta.env.VITE_SSO_CLIENT_ID || 'webopd')
  form.append('grant_type', 'password')
  form.append('scope', scope)
  if (totp && totp.trim()) {
    form.append('totp', totp.trim())
  }

  const tokenRes = await axios.post(tokenUrl, form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })

  const tokenData = tokenRes.data

  if (!tokenData?.access_token) {
    throw new Error('Gagal login: access_token tidak ditemukan di response.')
  }

  const now = Date.now()
  localStorage.setItem('access_token', tokenData.access_token)
  if (tokenData.refresh_token) {
    localStorage.setItem('refresh_token', tokenData.refresh_token)
  }
  if (tokenData.expires_in) {
    localStorage.setItem('expires_at', String(now + tokenData.expires_in * 1000))
  }
  if (tokenData.refresh_expires_in) {
    localStorage.setItem('refresh_expires_at', String(now + tokenData.refresh_expires_in * 1000))
  }
  localStorage.setItem('token_response', JSON.stringify(tokenData))

  const userinfoRes = await axios.get(userinfoUrl, {
    headers: { Authorization: `Bearer ${tokenData.access_token}` }
  })

  const userinfoData = userinfoRes.data

  const authStore = useAuthStore()
  authStore.setUser(userinfoData)

  push.success({ title: 'Login Berhasil', message: `Selamat datang, ${userinfoData.name || username}!` })

  const target = resolvePostLoginRedirect()
  router.push(target)
}

export async function handleGoogleCallback(code) {
  const redirectUri = getLoginRedirectUri()

  const body = new URLSearchParams()
  body.append('code', code)
  body.append('grant_type', 'authorization_code')
  body.append('client_id', 'portal')
  body.append('redirect_uri', redirectUri)

  const resp = await axios.post(`${keycloakBase}/token`, body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })

  const token = resp.data

  const msg = (token?.message || token?.error_description || token?.error || '')
    .toString()
    .toLowerCase()

  if (msg.includes('akun telah ada')) {
    push.info({ title: 'Info', message: 'Akun telah ada. Silakan login seperti biasa.' })
    await router.replace({ query: {} })
    return
  }

  if (!token?.access_token) {
    push.error({ title: 'Gagal Login', message: 'Login Google gagal: access_token tidak ditemukan.' })
    await router.replace({ query: {} })
    return
  }

  const now = Date.now()
  localStorage.setItem('access_token', token.access_token)
  if (token.refresh_token) {
    localStorage.setItem('refresh_token', token.refresh_token)
  }
  if (token.expires_in) {
    localStorage.setItem('expires_at', String(now + token.expires_in * 1000))
  }
  if (token.refresh_expires_in) {
    localStorage.setItem('refresh_expires_at', String(now + token.refresh_expires_in * 1000))
  }
  localStorage.setItem('token_response', JSON.stringify(token))

  const userinfoRes = await axios.get(userinfoUrl, {
    headers: { Authorization: `Bearer ${token.access_token}` }
  })

  const userinfoData = userinfoRes.data

  const authStore = useAuthStore()
  authStore.setUser(userinfoData)

  await router.replace({ query: {} })
  push.success({ title: 'Login Berhasil', message: `Berhasil login dengan Google. Selamat datang, ${userinfoData.name || 'User'}!` })
  router.push('/')
}

export async function performLogout() {
  const authStore = useAuthStore()
  await authStore.logout()
  sessionStorage.setItem('logout_success', 'true')
  window.location.replace('/')
}
