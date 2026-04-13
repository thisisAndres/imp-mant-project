import { describe, it, expect, afterEach } from 'vitest'
import axiosInstance from './axiosInstance'

describe('axiosInstance interceptor', () => {
  afterEach(() => localStorage.clear())

  it('agrega Authorization header cuando hay token', async () => {
    localStorage.setItem('access_token', 'test-token-123')
    const handler = axiosInstance.interceptors.request.handlers[0].fulfilled
    const config = await handler({ headers: {} })
    expect(config.headers.Authorization).toBe('Bearer test-token-123')
  })

  it('no agrega Authorization header cuando no hay token', async () => {
    const handler = axiosInstance.interceptors.request.handlers[0].fulfilled
    const config = await handler({ headers: {} })
    expect(config.headers.Authorization).toBeUndefined()
  })
})
