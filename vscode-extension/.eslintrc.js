module.exports = {
    root: true,
    parser: '@typescript-eslint/parser',
    parserOptions: {
        ecmaVersion: 6,
        sourceType: 'module'
    },
    plugins: [
        '@typescript-eslint'
    ],
    extends: [
        'eslint:recommended'
    ],
    rules: {
        'curly': 'warn',
        'eqeqeq': 'warn',
        'no-throw-literal': 'warn',
        'semi': 'warn',
        'no-unused-vars': 'off', // Turn off base rule as it can report incorrect errors
        '@typescript-eslint/no-unused-vars': ['warn', { 'argsIgnorePattern': '^_' }],
        'no-console': 'off', // Allow console for extension logging
        'prefer-const': 'warn',
        'no-var': 'error'
    },
    env: {
        node: true,
        es6: true
    },
    globals: {
        'Thenable': 'readonly',
        'NodeJS': 'readonly'
    },
    ignorePatterns: [
        'out',
        'dist',
        '**/*.d.ts',
        'node_modules',
        'src/test/**/*'
    ]
};