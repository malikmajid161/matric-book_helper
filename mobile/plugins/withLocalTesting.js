const { withAndroidManifest } = require('@expo/config-plugins');

// HTTP is enabled only for this explicitly configured LAN testing build.
module.exports = config => withAndroidManifest(config, config => {
  const app = config.modResults.manifest.application[0];
  app.$['android:usesCleartextTraffic'] = process.env.EXPO_PUBLIC_API_URL?.startsWith('http://') ? 'true' : 'false';
  return config;
});
