const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuration - customize these values
const API_KEY = process.env.OPENROUTER_API_KEY || 'YOUR_API_KEY_HERE';
const MODELS = [
  'poolside/laguna-xs.2:free',
  'baidu/cobuddy:free',
  'nvidia/nemotron-3-super-120b-a12b:free',
  'baidu/qianfan-ocr-fast:free'
];
const DEFAULT_MODEL = MODELS[0];

// Paths
const CONFIG_DIR = path.join(os.homedir(), '.codex');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.toml');

console.log('🔧 Patching Codex configuration for OpenRouter...');

// 1. Ensure the .codex directory exists
if (!fs.existsSync(CONFIG_DIR)) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  console.log(`📁 Created config directory: ${CONFIG_DIR}`);
}

// 2. Read existing config or start fresh
let configContent = '';
if (fs.existsSync(CONFIG_FILE)) {
  configContent = fs.readFileSync(CONFIG_FILE, 'utf-8');
}

// 3. Helper function to update or add a TOML key-value pair within a section
function patchConfig(content, sectionName, key, value) {
  const sectionRegex = new RegExp(`\\[${sectionName}\\]([\\s\\S]*?)(?=\\[|$)`);
  const keyRegex = new RegExp(`^${key}\\s*=\\s*["'].*["']`, 'm');
  
  const sectionMatch = content.match(sectionRegex);
  
  if (sectionMatch) {
    const sectionContent = sectionMatch[0];
    const keyMatch = sectionContent.match(keyRegex);
    
    if (keyMatch) {
      const newSectionContent = sectionContent.replace(keyRegex, `${key} = "${value}"`);
      content = content.replace(sectionRegex, newSectionContent);
    } else {
      const newSectionContent = sectionContent.trimEnd() + `\n${key} = "${value}"\n`;
      content = content.replace(sectionRegex, newSectionContent);
    }
  } else {
    content += `\n[${sectionName}]\n${key} = "${value}"\n`;
  }
  
  return content;
}

// 4. Apply Patches
configContent = patchConfig(configContent, 'model_provider_configs.openrouter', 'api_key', API_KEY);
configContent = patchConfig(configContent, 'model_provider_configs.openrouter', 'base_url', 'https://openrouter.ai/api/v1');
configContent = patchConfig(configContent, 'profiles.openrouter-free', 'model', DEFAULT_MODEL);
configContent = patchConfig(configContent, 'profiles.openrouter-free', 'model_provider', 'openrouter');

// 5. Add comment block for reference
const commentBlock = `\n# OpenRouter Models:\n# ${MODELS.join('\n# ')}\n`;
if (!configContent.includes('OpenRouter Models')) {
  configContent += commentBlock;
}

// 6. Write the configuration
fs.writeFileSync(CONFIG_FILE, configContent.trim() + '\n');

console.log('✅ Patching complete.');
console.log(`📝 Configuration updated at: ${CONFIG_FILE}`);
console.log(`🤖 Default Model set to: ${DEFAULT_MODEL}`);
console.log(`🔑 API Key has been configured.`);