# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Best Practices

### API Key Management

**CRITICAL: Never commit API keys to version control**

1. **Use environment variables only**

   ```bash
   export ANTHROPIC_API_KEY='your-key'
   export OPENAI_API_KEY='your-key'
   export GEMINI_API_KEY='your-key'
   ```

2. **Secure storage**
   - Use secret management tools (AWS Secrets Manager, HashiCorp Vault, etc.)
   - For local development, use `.env` files (ensure `.gitignore` includes them)
   - For CI/CD, use encrypted secrets

3. **Key rotation**
   - Rotate API keys every 90 days
   - Immediately rotate if compromised
   - Use different keys for dev/staging/prod

4. **Access control**
   - Limit key permissions to minimum required
   - Set spending limits on API keys
   - Monitor API usage for anomalies

### Code Privacy

#### What gets sent to LLM providers

- Code snippets for review (max 50KB per request)
- Pattern descriptions and examples
- User prompts and questions

#### What does NOT get sent

- Your entire codebase
- Environment variables or secrets
- File paths or system information
- API keys or credentials

#### For sensitive codebases

1. **Disable LLM features**: Set `use_llm=False` in code generator
2. **Self-host models**: Use local LLMs (Code Llama, Mistral, etc.)
3. **Use on-premises solutions**: Deploy private LLM infrastructure
4. **Code sanitization**: Review prompts before sending to external APIs

### Input Validation

All user inputs are validated:

- Code size limits (50KB for review, 5KB for chat)
- Message length limits (5000 characters for chat)
- Sanitized before sending to LLM APIs

### Dependencies

### Password Security

For the cloud backend API (`api/main.py`), passwords are hashed using PBKDF2-HMAC-SHA256:

- **Default iterations**: 210,000 (exceeds NIST minimum of 100,000)
- **Configurable via**: `FEEDBACK_LOOP_PASSWORD_ITERATIONS` environment variable
- **Minimum enforced**: 100,000 iterations (values below this fall back to default)
- **Per-user salt**: Each password uses a unique random salt

```bash
# Use default (210,000 iterations)
python api/main.py

# Custom iteration count
export FEEDBACK_LOOP_PASSWORD_ITERATIONS=250000
python api/main.py
```

#### Keeping dependencies secure

```bash
# Check for known vulnerabilities
pip install safety
safety check -r requirements.txt

# Update dependencies regularly
pip list --outdated
pip install --upgrade -r requirements.txt
```

#### Core dependencies

- `anthropic` - Official Anthropic SDK (regularly updated)
- `openai` - Official OpenAI SDK (regularly updated)
- `google-genai` - New Google AI SDK (recommended over deprecated package)
- `pygls` - Language Server Protocol library
- `fastapi` - Web framework with built-in security features

### Rate Limiting & Cost Control

The framework includes:

- Built-in caching to reduce API calls
- Configurable request limits
- Automatic fallback to template mode

**Additional protection:**

1. Set spending alerts in your LLM provider dashboard
2. Configure `FL_MAX_REQUESTS_PER_HOUR` environment variable
3. Monitor `metrics_data.json` for usage patterns

### Language Server Protocol (LSP) Security

The LSP server:

- Runs as local process (not exposed to network)
- Only analyzes files in workspace
- No file system writes (read-only analysis)
- Communication via stdin/stdout only

### CI/CD Security

#### GitHub Actions

```yaml
# Use encrypted secrets
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

# Limit permissions
permissions:
  contents: read

# Review third-party actions
uses: actions/checkout@v4  # Use specific versions
```

#### Best practices

- Never log API keys or secrets
- Use separate keys for CI/CD
- Enable branch protection rules
- Require code review before merge

## Reporting a Vulnerability

**DO NOT open public issues for security vulnerabilities.**

Instead:

1. Email security concerns to: <security@feedback-loop.dev> (or open a private security advisory on GitHub)
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

**Response timeline:**

- Initial response: Within 48 hours
- Status update: Within 7 days
- Fix timeline: Varies by severity

**Severity levels:**

- **Critical**: Remote code execution, credential exposure
- **High**: Data leakage, authentication bypass
- **Medium**: DoS, information disclosure
- **Low**: Minor issues with limited impact

## Security Features

### Built-in protections

1. **Input sanitization**: All user inputs validated
2. **API key isolation**: Keys never logged or exposed
3. **Rate limiting**: Prevents excessive API usage
4. **Error handling**: Graceful degradation without exposing internals
5. **Caching**: Reduces external API calls

### Secure defaults

- LLM features require explicit API key setup
- No telemetry or data collection without consent
- Local-first operation by default
- Minimal network exposure

## Compliance Considerations

### For regulated industries

**HIPAA/Healthcare:**

- Review data residency requirements
- Consider Azure OpenAI (BAA available)
- Implement audit logging
- Avoid sending PHI to external APIs

**GDPR/Privacy:**

- No personal data sent to LLMs by default
- User consent required for LLM features
- Data processing agreements with providers
- Right to erasure (clear conversation history)

**Financial Services:**

- Review your organization's AI policies
- Consider on-premises deployment
- Implement access controls
- Maintain audit trails

## Security Checklist

Before deploying to production:

- [ ] API keys stored securely (not in code)
- [ ] Different keys for dev/staging/prod
- [ ] Spending limits configured
- [ ] Dependencies updated and scanned
- [ ] `.env` files in `.gitignore`
- [ ] Security policies reviewed with team
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery plan in place
- [ ] Access controls implemented
- [ ] Audit logging enabled (if required)

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Anthropic Security](https://docs.anthropic.com/en/docs/security)
- [OpenAI Security](https://platform.openai.com/docs/guides/safety-best-practices)

## Updates

This security policy is reviewed and updated quarterly.

**Last update**: 2026-01-09
**Changes**: Added password hashing details for cloud backend API

---

**Remember: Security is everyone's responsibility. When in doubt, ask!**
