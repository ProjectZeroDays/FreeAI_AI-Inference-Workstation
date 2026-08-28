# OpenRouter Configuration for Codex CLI

## API Endpoint
- **Base URL**: https://openrouter.ai/api/v1
- **Alternative endpoints**:
  - https://openrouter.ai/api/v1/chat/completions
  - https://openrouter.ai/api/v1/models

## Authentication
- **API Key Format**: REDACTED_API_KEY
- **Header**: Authorization: Bearer REDACTED
- **Environment Variable**: OPENAI_API_KEY (Codex uses OpenAI-compatible env vars)

## Model Specification
- **Full Model String**: nvidia/nemotron-3-super-120b-a12b:free
- **Alternative**: nemotron-3-super (if available)
- **Free Tier Models**: Look for ":free" suffix

## Configuration Examples

### 1. Environment Variables (Recommended)
```bash
export OPENAI_API_BASE_URL="https://openrouter.ai/api/v1"
export OPENAI_API_KEY="REDACTED"
```

### 2. Config File (~/.codex/config.toml)
```toml
[model]
name = "nvidia/nemotron-3-super-120b-a12b:free"
provider = "openrouter" 
base_url = "https://openrouter.ai/api/v1"
api_key = "REDACTED"
```

### 3. Command-line Override
```bash
codex -c model.name="nvidia/nemotron-3-super-120b-a12b:free" \\
      -c model.provider="openrouter" \\
      -c model.base_url="https://openrouter.ai/api/v1" \\
      -c model.api_key="REDACTED" \\
      exec "your prompt here"
```

## Headers Required by OpenRouter
When making requests to OpenRouter, Codex should send:
- Authorization: Bearer [API_KEY]
- Content-Type: application/json
- HTTP-Referer: https://hermes.ai (optional but recommended)
- X-Title: Hermes-Agent (optional but recommended)

## Rate Limits & Usage
- Free tier models have rate limits
- Check usage at https://openrouter.ai/settings/usage
- Some models may require payment for heavy usage

## Troubleshooting
### 401 Unauthorized
- Check API key is correct
- Ensure OPENAI_API_KEY is set (not OPENROUTER_API_KEY)
- Verify no extra whitespace in key

### 404 Not Found
- Verify model name is correct and available
- Check if model requires payment
- Try without :free suffix if needed

### Connection Issues
- Verify network connectivity to openrouter.ai
- Check firewall/proxy settings
- Ensure DNS resolution works

## Verification
Test configuration with:
```bash
codex -c model.name="nvidia/nemotron-3-super-120b-a12b:free" \\
      -c model.provider="openrouter" \\
      -c model.base_url="https://openrouter.ai/api/v1" \\
      -c model.api_key="REDACTED" \\
      exec "Say 'Hello World' in Python"
```