import React from 'react'
import { describe, it, expect, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ProtectedRoute from './ProtectedRoute'

describe('ProtectedRoute', () => {
  afterEach(() => localStorage.clear())

  it('redirige a /login cuando no hay token', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <ProtectedRoute><p>Contenido protegido</p></ProtectedRoute>
      </MemoryRouter>
    )
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument()
  })

  it('renderiza children cuando hay token', () => {
    localStorage.setItem('access_token', 'valid-token')
    render(
      <MemoryRouter>
        <ProtectedRoute><p>Contenido protegido</p></ProtectedRoute>
      </MemoryRouter>
    )
    expect(screen.getByText('Contenido protegido')).toBeInTheDocument()
  })
})
