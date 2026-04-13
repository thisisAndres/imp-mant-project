import { describe, it, expect, vi, beforeEach } from 'vitest'
import { downloadSalesReport } from './reports'

vi.mock('./axiosInstance', () => ({
  default: {
    get: vi.fn(),
  },
}))

import axiosInstance from './axiosInstance'

describe('downloadSalesReport', () => {
  beforeEach(() => vi.clearAllMocks())

  it('llama a GET /reports/sales con los params correctos', async () => {
    const fakeBlob = new Blob(['pdf content'], { type: 'application/pdf' })
    axiosInstance.get.mockResolvedValue({
      data: fakeBlob,
      headers: {},
    })

    const result = await downloadSalesReport({
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      format: 'pdf',
    })

    expect(axiosInstance.get).toHaveBeenCalledWith('/reports/sales', {
      params: { format: 'pdf', start_date: '2024-01-01', end_date: '2024-01-31' },
      responseType: 'blob',
    })
    expect(result.blob).toBe(fakeBlob)
    expect(result.filename).toBe('reporte_ventas.pdf')
  })
})
