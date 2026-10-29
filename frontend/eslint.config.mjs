import nextCoreWebVitals from 'eslint-config-next/core-web-vitals';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import prettierConfig from 'eslint-config-prettier';

export default [
  { ignores: ['.next', 'node_modules', 'coverage', '*.config.js', '*.config.mjs'] },
  ...nextCoreWebVitals,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module',
        project: './tsconfig.json',
        tsconfigRootDir: import.meta.dirname, // anchors './tsconfig.json' here, not the IDE's cwd
      },
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      // TypeScript's compiler already catches undefined identifiers, and
      // core no-undef can't see ambient lib types (e.g. DOM's RequestInit).
      'no-undef': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      'react/no-unescaped-entities': 'off',
      '@next/next/no-html-link-for-pages': 'error',
    },
  },
  prettierConfig,
];
