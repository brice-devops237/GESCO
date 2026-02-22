/**
 * Composable de validation de formulaires.
 * Règles réutilisables et messages d'erreur cohérents.
 */

export interface ValidationRule {
  (v: unknown): boolean | string
}

export function useFormValidation() {
  const required = (message = 'Champ obligatoire'): ValidationRule => {
    return (v: unknown) => {
      if (v === null || v === undefined) return message
      if (typeof v === 'string' && !v.trim()) return message
      if (Array.isArray(v) && v.length === 0) return message
      return true
    }
  }

  const minLength = (min: number, message?: string): ValidationRule => {
    return (v: unknown) => {
      const s = typeof v === 'string' ? v : String(v ?? '')
      return s.length >= min ? true : (message ?? `Minimum ${min} caractères`)
    }
  }

  const maxLength = (max: number, message?: string): ValidationRule => {
    return (v: unknown) => {
      const s = typeof v === 'string' ? v : String(v ?? '')
      return s.length <= max ? true : (message ?? `Maximum ${max} caractères`)
    }
  }

  const email = (message = 'Adresse e-mail invalide'): ValidationRule => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return (v: unknown) => {
      if (v === null || v === undefined || (typeof v === 'string' && !v.trim())) return true
      return re.test(String(v)) ? true : message
    }
  }

  const numberBetween = (min: number, max: number, message?: string): ValidationRule => {
    return (v: unknown) => {
      const n = Number(v)
      if (Number.isNaN(n)) return message ?? 'Valeur numérique attendue'
      return n >= min && n <= max ? true : (message ?? `Entre ${min} et ${max}`)
    }
  }

  const pattern = (regex: RegExp, message = 'Format invalide'): ValidationRule => {
    return (v: unknown) => {
      if (v === null || v === undefined || v === '') return true
      return regex.test(String(v)) ? true : message
    }
  }

  return {
    required,
    minLength,
    maxLength,
    email,
    numberBetween,
    pattern,
  }
}
