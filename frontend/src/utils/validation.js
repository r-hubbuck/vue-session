import { parsePhoneNumber, isValidPhoneNumber } from 'libphonenumber-js'

/**
 * Shared validation utilities for consistent input validation across the app.
 */

// Standard email regex — RFC-aligned, max 254 chars
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/

export function isValidEmail(email) {
  if (!email) return true
  return EMAIL_REGEX.test(email) && email.length <= 254
}

/**
 * Validate a phone number using libphonenumber-js.
 * @param {string} phoneNumber - The phone number string
 * @param {string} countryCode - Country calling code like '+1', '+44'
 * @returns {{ valid: boolean, error: string|null }}
 */
export function validatePhone(phoneNumber, countryCode = '+1') {
  if (!phoneNumber) {
    return { valid: false, error: 'Phone number is required' }
  }

  const fullNumber = countryCode + phoneNumber.replace(/\D/g, '')

  try {
    if (!isValidPhoneNumber(fullNumber)) {
      return { valid: false, error: 'Please enter a valid phone number' }
    }
    return { valid: true, error: null }
  } catch {
    return { valid: false, error: 'Please enter a valid phone number' }
  }
}

/**
 * Strip non-alphanumeric characters from address fields to prevent
 * script injection while allowing legitimate address characters.
 * Allows letters, numbers, spaces, commas, periods, hyphens, slashes, #, and apostrophes.
 */
const ADDRESS_REGEX = /^[a-zA-Z0-9\s,.\-\/#']+$/

export function isValidAddressField(value) {
  if (!value) return true
  return ADDRESS_REGEX.test(value)
}
