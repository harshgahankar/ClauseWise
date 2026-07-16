module.exports = function override(config) {
  config.module.rules = config.module.rules.map((rule) => {
    if (
      rule.enforce === 'pre' &&
      rule.loader &&
      rule.loader.includes('source-map-loader')
    ) {
      const originalExclude = rule.exclude;
      rule.exclude = [originalExclude, /node_modules[/\\]dompurify/];
    }
    return rule;
  });
  return config;
};
