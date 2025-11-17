/**
 * Example configuration loader
 * Demonstrates clean configuration management without scattered logic
 */

/**
 * Load configuration based on environment
 * @param {string} env - Environment name (development, production, test)
 * @returns {Object} Configuration object
 */
export const loadConfig = (env = process.env.NODE_ENV || 'development') => {
  const baseConfig = {
    appName: 'RCL',
    version: '1.0.0',
  };

  const envConfigs = {
    development: {
      ...baseConfig,
      debug: true,
      logLevel: 'debug',
      apiUrl: 'http://localhost:3000',
    },
    production: {
      ...baseConfig,
      debug: false,
      logLevel: 'error',
      apiUrl: process.env.API_URL || 'https://api.example.com',
    },
    test: {
      ...baseConfig,
      debug: false,
      logLevel: 'error',
      apiUrl: 'http://localhost:3001',
    },
  };

  return envConfigs[env] || envConfigs.development;
};

/**
 * Feature flag manager
 * Centralized feature toggle management instead of scattered if statements
 */
export const createFeatureManager = (config) => {
  const features = config.features || {};

  return {
    /**
     * Check if a feature is enabled
     * @param {string} featureName - Name of the feature
     * @returns {boolean} Whether the feature is enabled
     */
    isEnabled(featureName) {
      return features[featureName] === true;
    },

    /**
     * Get feature configuration
     * @param {string} featureName - Name of the feature
     * @returns {*} Feature configuration value
     */
    getFeatureConfig(featureName) {
      return features[featureName];
    },
  };
};

export default { loadConfig, createFeatureManager };
