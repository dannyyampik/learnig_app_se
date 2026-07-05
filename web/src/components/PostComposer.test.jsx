// Component tests for the composer.
//
// The trick that makes these possible: vi.mock swaps the REAL api.js for
// a fake, so no server is needed and we control every response. This is
// the payoff of routing all requests through one seam — mock one file
// and any component can be tested in isolation.

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../api.js', () => ({
  apiPost: vi.fn(),
}))

import { apiPost } from '../api.js'
import PostComposer from './PostComposer.jsx'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('PostComposer', () => {
  it('disables Post while the textarea is empty', () => {
    render(<PostComposer onCreated={() => {}} />)

    expect(screen.getByRole('button', { name: 'Post' }).disabled).toBe(true)
  })

  it('counts down the remaining characters', () => {
    render(<PostComposer onCreated={() => {}} />)

    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'hello' },
    })

    expect(screen.getByText('275')).toBeTruthy()
  })

  it('sends the post and hands the server response to the parent', async () => {
    const created = { id: 1, body: 'hello', author: 'alice' }
    apiPost.mockResolvedValue(created)
    const onCreated = vi.fn()
    render(<PostComposer onCreated={onCreated} />)

    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'hello' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Post' }))

    await waitFor(() => expect(onCreated).toHaveBeenCalledWith(created))
    expect(apiPost).toHaveBeenCalledWith('/posts', { body: 'hello' })
    expect(screen.getByRole('textbox').value).toBe('') // cleared for the next post
  })

  it("shows the server's objection and keeps the draft", async () => {
    apiPost.mockRejectedValue(new Error('Invalid request.'))
    render(<PostComposer onCreated={() => {}} />)

    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'hello' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Post' }))

    await screen.findByText('Invalid request.')
    expect(screen.getByRole('textbox').value).toBe('hello') // draft survives
  })
})
