const localePercent = new Intl.NumberFormat('fr-FR', {
  style: 'percent',
  maximumFractionDigits: 1,
})

export function formatPercent(value) {
  if (!Number.isFinite(value)) return '—'
  return localePercent.format(value)
}

export function formatInteger(value) {
  if (!Number.isFinite(value)) return '—'
  return new Intl.NumberFormat('fr-FR').format(value)
}

export function diagonalTotal(matrix) {
  return matrix.reduce((total, row, index) => total + (row[index] ?? 0), 0)
}
