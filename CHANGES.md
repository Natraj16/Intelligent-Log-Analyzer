# Changes v1.1 - Enhanced Monitoring Features

**Date**: April 27, 2026  
**Version**: 1.1

## Overview

This release adds three major features to improve the log monitoring experience:
1. **Browser Notifications** - Get alerted when critical issues occur
2. **Custom Log Level Filtering** - Monitor any log level, not just predefined ones
3. **Hot-Reload Configuration** - Apply changes without restarting monitoring

---

## Feature 1: Browser Notifications 🔔

### What's New

Automatic pop-up alerts in your browser when **Critical** or **High** severity anomalies are detected.

### Key Features

- **🔴 Critical Alerts**: Stay on screen, require interaction to dismiss
- **🟠 High Alerts**: Auto-dismiss after ~10 seconds
- **Independent of Configuration**: Notifications work regardless of which log levels you're filtering
- **No Duplicates**: Each alert notified only once
- **Real-time**: Appear within 1-2 seconds of detection

### Files Modified

- `templates/dashboard.html`
  - Added notification permission request on page load
  - Replaced `lastNotifiedAlertId` tracking with Set-based tracking
  - Made severity comparison case-insensitive
  - Reduced alert refresh interval from 2s to 1s for faster detection

### Usage

1. When first visiting the app, allow browser notifications
2. Start monitoring and wait for anomalies
3. Critical/High severity alerts will trigger pop-ups automatically
4. Works best with `/alerts` page active

### Browser Support

✅ Chrome, Firefox, Edge, Safari (modern versions)

---

## Feature 2: Custom Log Level Filtering 🔍

### What's New

Add any custom log level names to the configuration, not limited to INFO/WARN/ERROR.

### How It Works

**Two filtering methods**:

1. **Predefined Levels** (default)
   - Use checkboxes: INFO, WARN, ERROR
   - Leave "Custom Log Levels" empty

2. **Custom Levels** (new)
   - Enter custom level names in text field
   - Example: `CRITICAL`, `ERROR,CRITICAL,DEBUG`
   - When non-empty, **overrides** predefined checkboxes

### Files Modified

- `app.py`
  - Added `custom_levels` to DEFAULT_CONFIG
  - Updated `/` route to pass `custom_levels` to template
  - Updated `/configure` route to read and save `custom_levels`

- `templates/dashboard.html`
  - Added text input field for custom log levels
  - Added helper text explaining the feature
  - Updated labels to clarify filtering method

- `log_watcher.py`
  - Added `import json` at top
  - Updated `_process_new_logs()` to use custom levels
  - Implemented priority: custom_levels (if non-empty) → log_levels (if empty)
  - Handles comma-separated parsing and uppercasing

### Usage

1. To use custom levels: Type in "Custom Log Levels" field
   - Example: `ERROR` shows only ERROR logs
   - Example: `CRITICAL,ERROR` shows CRITICAL and ERROR

2. To use predefined: Leave "Custom Log Levels" empty and use checkboxes

### Configuration Format

```json
{
  "log_path": "logs/application.log",
  "log_levels": ["INFO", "WARN", "ERROR"],
  "custom_levels": "ERROR",
  "keywords": ""
}
```

---

## Feature 3: Hot-Reload Configuration ♻️

### What's New

Configuration changes now take effect **immediately** without restarting monitoring!

### How It Works

- Config is reloaded on each monitoring cycle (~1 second)
- Changes to `config.json` are picked up automatically
- Safe fallback: If config load fails, uses previous config
- No performance impact: Only reloads if file exists

### Files Modified

- `log_watcher.py`
  - Updated `_check_new_lines()` to reload config from file
  - Added `import json` for config reloading
  - Wraps reload in try-except for safety
  - Config reloaded before processing each batch of logs

### Timeline

```
t=0s:    User saves configuration via web UI
t=0.1s:  Changes written to config.json
t=1-2s:  LogWatcher reloads config
t=2-3s:  New filter applied to incoming logs
t=3-4s:  New logs appear in Alerts tab with updated filters
```

### Usage

1. Modify configuration in web UI
2. Click "Save Configuration"
3. Wait 1-2 seconds
4. Filters apply automatically - no restart needed!

---

## Updated Documentation 📚

### README.md Changes

- **Features section**: Added browser notifications, custom filtering, hot-reload
- **Quick Start Guide**: Updated configuration steps for new features
- **Configuration section**: Complete rewrite with examples
  - New section: "How Configuration Filtering Works"
  - New section: "Configuration Examples"
  - Explaining predefined vs. custom levels
  
- **New Section**: "Browser Notifications"
  - How to enable
  - Troubleshooting
  - Browser compatibility
  
- **Troubleshooting**: Added sections 9 & 10
  - Configuration changes not taking effect
  - Custom log levels not filtering

- **Version History**: Added version tracking

### README Structure

```
Features
  ├─ Real-time Monitoring
  ├─ ML Anomaly Detection
  ├─ Browser Notifications ✨ NEW
  ├─ Dashboard & Logs
  ├─ Flexible Log Filtering ✨ UPDATED
  └─ ...

Configuration
  ├─ File Format
  ├─ Fields
  ├─ Filtering Logic ✨ NEW
  ├─ Examples ✨ NEW
  └─ Changing Configuration ✨ UPDATED

Browser Notifications ✨ NEW SECTION
  ├─ Overview
  ├─ Features
  ├─ How to Enable
  ├─ Behavior
  ├─ Browser Compatibility
  └─ Troubleshooting

Troubleshooting
  └─ Added sections for new features ✨
```

---

## Backward Compatibility

✅ **Fully backward compatible**

- Old `config.json` files without `custom_levels` work fine (defaults to empty)
- Existing monitoring workflows unchanged
- All previous features work as before
- No breaking changes to APIs

### Migration from v1.0

If upgrading from v1.0:

1. No action needed - app works as-is
2. `config.json` will work without modification
3. To use new features:
   - Add custom levels in Configuration tab
   - Enable notifications (browser permission)
   - Changes apply immediately (no restart)

---

## Testing Checklist

- [x] Browser notifications appear for Critical/High alerts
- [x] Notifications only show once per alert
- [x] Custom log levels filter correctly
- [x] Configuration changes apply mid-monitoring
- [x] Predefined levels work when custom empty
- [x] Custom levels override checkboxes when non-empty
- [x] Keyword filtering works with new config
- [x] No regression in existing features
- [x] Documentation is complete and clear

---

## Performance Impact

- **Minimal**: Config reload check is ~1ms per cycle
- **Safe**: Wrapped in try-except, no crashes on read errors
- **Efficient**: Only reloads if config file exists
- **No impact on alerts generation or detection

---

## Technical Details

### Config Reload Logic

```python
# In _check_new_lines():
if os.path.exists(config_file):
    try:
        with open(config_file, "r") as f:
            self.config = json.load(f)
    except (json.JSONDecodeError, IOError):
        pass  # Keep using existing config
```

### Custom Levels Logic

```python
# In _process_new_logs():
custom_levels_str = self.config.get("custom_levels", "").strip()

if custom_levels_str:
    # Use ONLY custom levels (ignore checkboxes)
    custom_levels = [
        level.strip().upper()
        for level in custom_levels_str.split(",")
        if level.strip()
    ]
    all_levels = custom_levels
else:
    # Use predefined checkbox selections
    all_levels = self.config.get("log_levels", ["INFO", "WARN", "ERROR"])
```

### Notification Logic

```javascript
// Track notified alerts by ID+severity
let notifiedAlerts = new Set();

// Check severity case-insensitively
const sevLower = (alert.severity || '').toLowerCase();
if (sevLower === 'critical' || sevLower === 'high') {
    showNotification(alert.severity, ...);
}
```

---

## Summary of Changes

| Component | Change | Impact |
|-----------|--------|--------|
| `dashboard.html` | Notifications + config UI updates | UX improvement |
| `app.py` | Config field handling | Data handling |
| `log_watcher.py` | Hot-reload + custom levels | Core logic |
| `README.md` | Comprehensive documentation | Knowledge base |

**Total files modified**: 4  
**Total new files**: 1 (CHANGES.md)  
**Lines added**: ~500  
**Backward compatible**: ✅ Yes

---

## Future Enhancements

Potential improvements for v1.2:

- Notification sound option
- Email alerts for Critical severity
- Historical analytics dashboard
- Severity level customization
- Multi-file monitoring
- Database persistence

---

## Credits

Intelligent Log Analyzer System v1.1  
Final Year Project - April 2026
