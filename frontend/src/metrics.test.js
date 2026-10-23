import assert from 'node:assert/strict'
import test from 'node:test'

import { diagonalTotal, formatInteger, formatPercent } from './metrics.js'

test('formatPercent displays a French percentage', () => {
  assert.match(formatPercent(0.8109), /81,1\s*%/)
})

test('formatInteger groups large counts', () => {
  assert.match(formatInteger(12000), /12.?000/)
})

test('diagonalTotal counts correct predictions', () => {
  assert.equal(diagonalTotal([[3, 1], [2, 4]]), 7)
})
