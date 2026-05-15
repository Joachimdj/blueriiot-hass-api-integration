# HACS Submission Guide

This document provides instructions for submitting the Blueriot Blue Connect integration to HACS (Home Assistant Community Store).

## Prerequisites

Before submitting, ensure:

1. **Repository is Public**: The GitHub repository must be publicly accessible
2. **License**: Include a LICENSE file (MIT license recommended)
3. **Documentation**: Complete README.md with installation and configuration instructions
4. **Proper Structure**: Follow Home Assistant integration structure
5. **manifest.json**: Properly formatted with all required fields

## Pre-Submission Checklist

- [ ] Repository created on GitHub
- [ ] `manifest.json` is properly formatted with:
  - `domain`: "blueriot_blue_connect"
  - `name`: "Blueriot Blue Connect"
  - `codeowners`: Your GitHub username
  - `documentation`: Link to your GitHub repository or documentation
  - `version`: Semantic version (e.g., "1.0.0")
- [ ] README.md includes:
  - Clear description of functionality
  - Installation instructions (both HACS and manual)
  - Configuration steps
  - List of supported entities
  - Troubleshooting section
- [ ] LICENSE file exists (MIT or compatible)
- [ ] CHANGELOG.md documents version history
- [ ] Code quality:
  - Follows Home Assistant code style
  - Proper error handling
  - No hardcoded secrets
  - Type hints where applicable

## Repository Setup

### 1. Create GitHub Repository

```bash
# Create a new repository on GitHub
# Name it: blueriot-hass
# Description: Blueriot Blue Connect integration for Home Assistant
# Make it PUBLIC
```

### 2. Initialize Local Repository

```bash
git init
git add .
git commit -m "Initial commit: Blueriot Blue Connect integration"
git branch -M main
git remote add origin https://github.com/yourusername/blueriot-hass.git
git push -u origin main
```

### 3. Update manifest.json

Update the following fields with your actual information:

```json
{
  "domain": "blueriot_blue_connect",
  "name": "Blueriot Blue Connect",
  "codeowners": ["@yourusername"],
  "documentation": "https://github.com/yourusername/blueriot-hass",
  "issue_tracker": "https://github.com/yourusername/blueriot-hass/issues",
  "version": "1.0.0"
}
```

## HACS Registration Process

### Step 1: Create a GitHub Release

```bash
# Tag your version
git tag v1.0.0
git push origin v1.0.0
```

Then create a release on GitHub:

1. Go to your repository on GitHub
2. Click **Releases** → **Create a new release**
3. Select tag v1.0.0
4. Title: "Release v1.0.0"
5. Description: Changelog entry
6. Publish release

### Step 2: Submit to HACS Repository

1. Visit https://github.com/hacs/default/issues/new/choose
2. Select "New integration"
3. Fill in the form:
   - **Repository URL**: https://github.com/yourusername/blueriot-hass
   - Leave other fields as default
4. Submit the issue

### Step 3: Wait for Review

HACS maintainers will review your submission. They typically check:

- Repository structure and standards
- Code quality and security
- Documentation completeness
- manifest.json validity
- manifest.json version matches release tag

Common reasons for rejection:

- Missing or incomplete documentation
- Code quality issues
- Non-standard integration structure
- Invalid manifest.json
- Missing LICENSE file

## After Acceptance

Once accepted, your integration will be available in HACS:

1. Users can install via HACS UI
2. Automatic updates when new releases are created
3. Integration appears in HACS directory

## Updating Your Integration

To publish updates:

1. Update version in `manifest.json`
2. Update `CHANGELOG.md`
3. Commit changes:
   ```bash
   git add .
   git commit -m "v1.1.0: Add feature XYZ"
   ```
4. Create a new tag and release:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
5. Create release on GitHub with changelog

HACS will automatically detect the new version and offer it to users.

## Community Support

### Getting Help

- **HACS Discord**: https://discord.gg/hacs
- **Home Assistant Forums**: https://community.home-assistant.io
- **Integration Testing**: Test on clean Home Assistant installation before release

### Best Practices

1. **Version Numbering**: Use semantic versioning (MAJOR.MINOR.PATCH)
2. **Changelog**: Keep detailed changelog for users
3. **Testing**: Test on latest Home Assistant before release
4. **Documentation**: Keep docs up-to-date with changes
5. **Issues**: Respond to user issues promptly

## Example manifest.json (Final)

```json
{
  "domain": "blueriot_blue_connect",
  "name": "Blueriot Blue Connect",
  "codeowners": ["@joachimdittman"],
  "config_flow": true,
  "documentation": "https://github.com/joachimdittman/blueriot-hass",
  "requirements": ["aiohttp>=3.8.0"],
  "version": "1.0.0",
  "issue_tracker": "https://github.com/joachimdittman/blueriot-hass/issues",
  "integration_type": "hub"
}
```

## Useful Resources

- [Home Assistant Integration Development](https://developers.home-assistant.io/docs/integration_index/)
- [HACS Documentation](https://hacs.xyz/)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale/)
- [Manifest File Format](https://developers.home-assistant.io/docs/creating_integration_manifest/)
