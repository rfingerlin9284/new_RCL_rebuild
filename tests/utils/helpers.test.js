/**
 * Example test file for utility helpers
 * Demonstrates proper test structure and organization
 */

import {
  isValidEmail,
  formatDate,
  deepClone,
  sanitizeInput,
} from '../src/utils/helpers.js';

describe('Utility Helpers', () => {
  describe('isValidEmail', () => {
    test('should return true for valid email addresses', () => {
      expect(isValidEmail('user@example.com')).toBe(true);
      expect(isValidEmail('test.user@domain.co.uk')).toBe(true);
      expect(isValidEmail('name+tag@example.org')).toBe(true);
    });

    test('should return false for invalid email addresses', () => {
      expect(isValidEmail('not-an-email')).toBe(false);
      expect(isValidEmail('@example.com')).toBe(false);
      expect(isValidEmail('user@')).toBe(false);
      expect(isValidEmail('user @example.com')).toBe(false);
    });

    test('should return false for non-string inputs', () => {
      expect(isValidEmail(null)).toBe(false);
      expect(isValidEmail(undefined)).toBe(false);
      expect(isValidEmail(123)).toBe(false);
      expect(isValidEmail({})).toBe(false);
    });
  });

  describe('formatDate', () => {
    test('should format Date object correctly', () => {
      const date = new Date('2025-11-17');
      expect(formatDate(date)).toBe('2025-11-17');
    });

    test('should format date string correctly', () => {
      expect(formatDate('2025-11-17T12:00:00Z')).toBe('2025-11-17');
    });

    test('should format timestamp correctly', () => {
      const timestamp = new Date('2025-11-17').getTime();
      expect(formatDate(timestamp)).toBe('2025-11-17');
    });

    test('should throw error for invalid date', () => {
      expect(() => formatDate('invalid-date')).toThrow('Invalid date provided');
    });
  });

  describe('deepClone', () => {
    test('should clone primitive values', () => {
      expect(deepClone(42)).toBe(42);
      expect(deepClone('string')).toBe('string');
      expect(deepClone(null)).toBe(null);
      expect(deepClone(undefined)).toBe(undefined);
    });

    test('should clone arrays', () => {
      const arr = [1, 2, 3];
      const cloned = deepClone(arr);
      expect(cloned).toEqual(arr);
      expect(cloned).not.toBe(arr);
    });

    test('should clone nested objects', () => {
      const obj = { a: 1, b: { c: 2 } };
      const cloned = deepClone(obj);
      expect(cloned).toEqual(obj);
      expect(cloned).not.toBe(obj);
      expect(cloned.b).not.toBe(obj.b);
    });

    test('should clone Date objects', () => {
      const date = new Date('2025-11-17');
      const cloned = deepClone(date);
      expect(cloned).toEqual(date);
      expect(cloned).not.toBe(date);
    });
  });

  describe('sanitizeInput', () => {
    test('should sanitize HTML special characters', () => {
      expect(sanitizeInput('<script>alert("xss")</script>'))
        .toBe('&lt;script&gt;alert(&quot;xss&quot;)&lt;&#x2F;script&gt;');
    });

    test('should handle ampersands', () => {
      expect(sanitizeInput('Tom & Jerry')).toBe('Tom &amp; Jerry');
    });

    test('should handle quotes', () => {
      expect(sanitizeInput("It's a \"test\""))
        .toBe('It&#x27;s a &quot;test&quot;');
    });

    test('should return empty string for non-string inputs', () => {
      expect(sanitizeInput(null)).toBe('');
      expect(sanitizeInput(undefined)).toBe('');
      expect(sanitizeInput(123)).toBe('');
    });
  });
});
