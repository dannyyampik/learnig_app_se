// Component tests for the optimistic like button — the two moments that
// define optimistic UI:
//   1. the screen changes BEFORE the server answers
//   2. the screen changes BACK if the server says no

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../api.js', () => ({
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
}))
// LikeButton only needs to know *whether* someone is logged in.
vi.mock('../context/AuthContext.jsx', () => ({
  useAuth: () => ({ user: { id: 1, username: 'alice' } }),
}))

import { apiDelete, apiPut } from '../api.js'
import LikeButton from './LikeButton.jsx'

const post = { id: 42, likeCount: 0, likedByMe: false }

beforeEach(() => {
  vi.clearAllMocks()
})

describe('LikeButton', () => {
  it('updates the count before the server has answered', () => {
    // A promise that never settles = a server that never answers.
    apiPut.mockReturnValue(new Promise(() => {}))
    render(<LikeButton post={post} />)

    fireEvent.click(screen.getByRole('button'))

    // No await — the count changed synchronously. That's the optimism.
    expect(screen.getByRole('button').textContent).toContain('1')
    expect(apiPut).toHaveBeenCalledWith('/posts/42/like')
  })

  it('rolls back when the server refuses', async () => {
    apiPut.mockRejectedValue(new Error('nope'))
    render(<LikeButton post={post} />)

    fireEvent.click(screen.getByRole('button'))
    expect(screen.getByRole('button').textContent).toContain('1') // optimistic…

    await waitFor(() =>
      expect(screen.getByRole('button').textContent).toContain('0'),
    ) // …rolled back
  })

  it('unlikes with DELETE — the idempotent pair', async () => {
    apiDelete.mockResolvedValue(null)
    render(<LikeButton post={{ id: 42, likeCount: 3, likedByMe: true }} />)

    fireEvent.click(screen.getByRole('button'))

    expect(screen.getByRole('button').textContent).toContain('2')
    await waitFor(() => expect(apiDelete).toHaveBeenCalledWith('/posts/42/like'))
  })
})
