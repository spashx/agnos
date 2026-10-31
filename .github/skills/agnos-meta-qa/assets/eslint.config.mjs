// agnos-meta-qa: SonarQube's JavaScript rules from the command line, each a warning as in VS Code; a parsing error alone
// is an error (RQ-QLT-002, DEC-QLT-002, DEC-QLT-006).
import sonarjs from "eslint-plugin-sonarjs";

const OFF = "off";
const WARN = "warn";
const asWarning = (level) => {
  if (Array.isArray(level)) return level[0] === OFF ? level : [WARN, ...level.slice(1)];
  return level === OFF ? level : WARN;
};
const recommended = sonarjs.configs.recommended;

export default [{
  files: ["**/*.js"],
  ...recommended,
  languageOptions: { sourceType: "script", ecmaVersion: "latest" },
  rules: Object.fromEntries(Object.entries(recommended.rules).map(([rule, level]) => [rule, asWarning(level)])),
}];
