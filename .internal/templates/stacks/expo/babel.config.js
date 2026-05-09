module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          alias: {
            '@': './src',
            '@components': './src/components',
            '@services': './src/services',
            '@hooks': './src/hooks',
            '@context': './src/context',
            '@constants': './src/constants',
            '@utils': './src/utils',
          },
        },
      ],
      'react-native-reanimated/plugin',
    ],
  };
};
