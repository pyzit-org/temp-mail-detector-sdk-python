# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-07

### ⚠️ BREAKING CHANGES

This is a major architectural overhaul to align with the new Pyzit Temp Mail Detector (TMD) backend infrastructure. **This release is not backward compatible with 0.x versions.**

#### API Infrastructure
- **Base URL changed**: `https://api-tempmail.pyzit.com/v1` → `https://api.pyzit.com`
- **Endpoint paths changed**: `/v1/validate/...` → `/v1/tmd/...`
- **Token prefix changed**: `tmd_live_...` → `pyzit_live_...`

#### Exception Hierarchy Overhaul
- ❌ **Removed**: `PlanRequiredError`, `ScopeError`
- ✅ **Added**: `InsufficientScopeError`, `QuotaExceededError`, `BatchLimitExceededError`, `ValidationError`
- **Changed error behavior**:
  - HTTP 402 now raises `QuotaExceededError` (monthly quota exhausted)
  - HTTP 403 now raises `InsufficientScopeError` (token lacks required scope)
  - HTTP 400 can raise `BatchLimitExceededError` (bulk request exceeds plan limit)

#### Bulk Response Structure
- **Old**: `{"results": {email: bool}, "processed": int}`
- **New**: `{"total": int, "status": str, "disposable_count": int, "privacy_relay_count": int, "flagged_domains": [], "results": [BulkItemResult]}`
- Added helper methods: `clean_emails()`, `disposable_emails()`, `privacy_relay_emails()`

#### Model Changes
- ❌ **Removed**: `MxRecord` model (MX records now returned as flat list of strings)
- ✅ **Added**: `BulkItemResult` model for individual bulk results
- ✅ **Added**: Full Privacy Relay support (`is_privacy_relay`, `relay_provider`, `provider_name`) across `CheckResult`, `DetailedResult`, and `BulkResult`
- **DNS Intelligence**: Flat DNS structure in `DetailedDetails` (`has_mx`, `mx_records`, `has_a`, `a_records`, `has_spf`, `spf_record`, `has_dmarc`, `dmarc_record`)
- **Reputation Score**: Standardized to integer 0..100 scale

### ✨ New Features

#### Architecture & Access Control
- **Decoupled plans from endpoint access**: All plans can use all endpoints
- **Token scopes**: API tokens now use scopes (`tmd:basic`, `tmd:detailed`, `tmd:*`)
- **Unlimited API keys**: Users on all plans can generate unlimited API keys
- **Dual quota model**: Separate `simple_quota` and `detailed_quota` tracking

#### Client Configuration
- **`max_retries` parameter**: Configurable retry attempts for 429/5xx errors (default: 2)
- **`fail_open` parameter**: When enabled, returns clean result on network errors to prevent blocking user flows
- **Reduced default timeout**: Changed from 10.0s to 5.0s for faster failure detection

#### Retry Logic
- **Exponential backoff**: Automatic retry with exponential backoff for 429 and 5xx errors
- **Jitter**: Random jitter added to retry delays to prevent thundering herd
- **Smart retry**: Respects `Retry-After` header when provided by API

#### Model Enhancements
- **`DetailedResult.should_flag`**: Convenience property for flag recommendation
- **`DetailedResult.has_mx`**: Shorthand for DNS intelligence MX check
- **`BulkResult.flagged_domains`**: Deduplicated list of disposable domains from bulk results

#### Rate Limiting
- **Dual-window rate limiting**: Supports new burst (1s) and sustained (60s) rate limits
- **Header-based backoff**: Reads `Retry-After` header for precise backoff timing

### 📝 Documentation Updates

- Updated quota model documentation (separate simple/detailed quotas)
- Added bulk batch size limits per plan (Free=10, Pro=50, Scale=100)
- Documented token scope system and requirements
- Updated error handling examples with new exception types
- Added configuration documentation for new parameters
- Updated API token format documentation (`pyzit_live_` prefix)

### 🧪 Testing Updates

- All test fixtures updated to new API endpoints
- Test mocks updated for new error responses
- Bulk result tests updated for new response structure
- Exception tests updated for new exception hierarchy
- DNS intelligence tests updated for simplified MX record format

### 🔧 Internal Changes

- **Improved error parsing**: More robust extraction of error details from API responses
- **Better timeout handling**: Network errors now handled with retry logic
- **Cleaner import structure**: Removed unused `MxRecord` from exports
- **Type safety improvements**: Better type hints in exception classes

### 📊 Performance

- **Faster default timeout**: Reduced from 10s to 5s for quicker error detection
- **Efficient retry logic**: Prevents unnecessary retries on non-retryable errors
- **Optimized error parsing**: Faster error response processing

### 🚀 Migration Guide

To migrate from 0.x to 1.0.0:

1. **Update API token**: Ensure you're using tokens with `pyzit_live_` prefix
2. **Update exception handling**: Replace `PlanRequiredError` with `QuotaExceededError` or `InsufficientScopeError`
3. **Update bulk result handling**: Use new `BulkResult` structure and helper methods
4. **Update base URL**: No action needed if using default, but update custom base URLs
5. **Test token scopes**: Ensure your tokens have required scopes (`tmd:basic`, `tmd:detailed`)
6. **Review quota limits**: Check new quota model and plan limits

### 🐛 Bug Fixes

- Fixed MX record parsing to handle simplified string format
- Fixed bulk result helper methods to work with new array structure
- Fixed error parsing for quota exceeded messages
- Fixed scope extraction from error messages

## [0.1.2] - 2024-05-XX

### 📝 Documentation
- Updated README with better examples and structure

## [0.1.1] - 2024-05-XX

### 📝 Documentation
- Updated repository URLs in README
- Fixed package metadata

## [0.1.0] - 2024-05-XX

### 🎉 Initial Release
- Initial release of tempmail-pyzit SDK
- Basic email validation with `check()` method
- Detailed analysis with `detailed()` method
- Bulk validation with `bulk()` method
- Sync and async client support
- Comprehensive error handling
- Full test coverage

[1.0.0]: https://github.com/pyzit-org/temp-mail-detector-sdk-python/compare/v0.1.2...v1.0.0
[0.1.2]: https://github.com/pyzit-org/temp-mail-detector-sdk-python/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/pyzit-org/temp-mail-detector-sdk-python/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/pyzit-org/temp-mail-detector-sdk-python/releases/tag/v0.1.0