const { defineConfig } = require('eslint/config');
const expoConfig = require('eslint-config-expo/flat');

const HEX_COLOR_RE = /#[0-9A-Fa-f]{3,8}\b/;

module.exports = defineConfig([
  expoConfig,
  {
    ignores: ['dist/*', 'node_modules/*', '.expo/*', 'android/*', 'ios/*'],
  },
  {
    files: ['src/**/*.{ts,tsx}', 'app/**/*.{ts,tsx}'],
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',

      'no-restricted-imports': [
        'error',
        {
          paths: [
            {
              name: 'react-native',
              importNames: ['TouchableOpacity', 'TouchableWithoutFeedback', 'TouchableHighlight'],
              message: 'Use Pressable instead.',
            },
          ],
        },
      ],

      'no-restricted-syntax': [
        'error',
        {
          selector: `Literal[value=/${HEX_COLOR_RE.source}/]`,
          message:
            'Hardcoded hex colors are forbidden. Import tokens from @constants/colors.',
        },
        {
          selector: `TemplateElement[value.raw=/${HEX_COLOR_RE.source}/]`,
          message:
            'Hardcoded hex colors are forbidden. Import tokens from @constants/colors.',
        },
      ],
    },
  },
  {
    files: ['src/constants/**/*.{ts,tsx}'],
    rules: {
      'no-restricted-syntax': 'off',
    },
  },
  {
    files: ['**/__tests__/**/*.{ts,tsx}', '**/*.test.{ts,tsx}'],
    rules: {
      'no-restricted-syntax': 'off',
    },
  },
]);
