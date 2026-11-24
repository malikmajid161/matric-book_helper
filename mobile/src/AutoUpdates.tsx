import {useEffect} from 'react';
import {AppState} from 'react-native';
import NetInfo from '@react-native-community/netinfo';
import * as Updates from 'expo-updates';

const CHECK_INTERVAL = 30 * 60 * 1000;
let lastCheck = 0;
let checking = false;

/** Fetch compatible updates quietly; apply on the next launch, never during study. */
export function AutoUpdates() {
  useEffect(() => {
    if (__DEV__ || !Updates.isEnabled) return;
    let mounted = true;
    async function check() {
      if (!mounted || checking || AppState.currentState !== 'active' || Date.now() - lastCheck < CHECK_INTERVAL) return;
      checking = true;
      try {
        const network = await NetInfo.fetch();
        if (!mounted || !network.isConnected || network.isInternetReachable === false) return;
        lastCheck = Date.now();
        const update = await Updates.checkForUpdateAsync();
        if (mounted && update.isAvailable) await Updates.fetchUpdateAsync();
      } catch {
        // An unavailable update service must never block downloaded textbooks.
      } finally {
        checking = false;
      }
    }
    const app = AppState.addEventListener('change', state => {if (state === 'active') void check();});
    const network = NetInfo.addEventListener(state => {
      if (state.isConnected && state.isInternetReachable !== false) void check();
    });
    return () => {mounted = false; app.remove(); network();};
  }, []);
  return null;
}
