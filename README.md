# Intelligent Log Analyzer System

> 🚀 A Python Flask web application that monitors log files in real-time, detects anomalies using machine learning, and generates severity-based alerts.

**Key Insight**: This system automatically identifies unusual patterns in logs using an ML-based Isolation Forest algorithm, converting raw logs into actionable alerts with intelligent severity classification.

## ✨ Features

- **Real-time Log Monitoring** 📊: Continuously monitors log files for new entries with efficient file polling
- **ML-based Anomaly Detection** 🤖: Uses scikit-learn's IsolationForest algorithm to detect statistical anomalies
- **Intelligent Severity Classification** ⚠️: Maps anomaly scores to 4-level severity (Critical, High, Medium, Low) using multi-factor risk scoring
- **Browser Notifications** 🔔: Automatic pop-up alerts for Critical and High severity anomalies
- **Web Dashboard** 💻: User-friendly Flask interface with real-time auto-refreshing alerts and logs viewer
- **Demo Log Generator** 📝: Built-in realistic log generator for testing and demonstration (5 services, 3 log levels)
- **Flexible Log Filtering** 🔍: 
  - Filter by predefined levels (INFO, WARN, ERROR)
  - Add custom log level categories
  - Filter by keywords (comma-separated)
  - **Hot-reload configuration**: Changes take effect immediately without restarting monitoring
- **RESTful API** 🔌: JSON endpoints for programmatic access to alerts and logs
- **Thread-Safe Architecture** 🔒: Concurrent processing with proper locking mechanisms

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

**What gets installed:**
- Flask 3.0.0+ (web framework)
- scikit-learn 1.4.0+ (machine learning)
- NumPy 1.26.0+ (numerical computing)

### 2️⃣ Run the Application
```bash
python app.py
```

**What happens:**
- Loads ML model from `model.pkl` (or trains a new one on first run)
- Starts Flask web server on `http://localhost:5000`
- Automatically opens your browser to the configuration page
- Initializes background threads for monitoring

### 3️⃣ Configure and Start Monitoring

#### Step 1: Configure Settings (`/` home page)
1. Set the log file path (default: `logs/application.log`)
2. Choose filtering method:

   **Option A: Use Predefined Log Levels (Default)**
   - ☐ INFO (informational messages)
   - ☐ WARN (warning messages)
   - ☐ ERROR (error messages)
   - Leave "Custom Log Levels" empty
   
   **Option B: Use Custom Log Levels**
   - Type custom level names in "Custom Log Levels" field (comma-separated)
   - Examples: `ERROR`, `CRITICAL, ERROR, DEBUG`, `INFO`
   - **Note**: When custom levels are provided, predefined checkboxes are ignored
   - This allows monitoring custom log levels not in the predefined list

3. Optionally add keywords to filter logs (comma-separated)
   - Example: `failed, timeout, error`
   - Applied after log level filtering
4. Click **"Save Configuration"**

#### Step 2: Start Monitoring
1. Click **"Start Monitoring"** button
2. System starts two background threads:
   - **LogWatcher**: Polls log file every 1 second for new entries
   - **DemoLogGenerator**: Creates realistic test logs every 2 seconds
3. Monitor runs until you click **"Stop Monitoring"**

#### Step 3: View Results
- **📊 Dashboard** (`/alerts`): 
  - Real-time alert counts by severity
  - List of detected anomalies with timestamps
  - Browser pop-up notifications for Critical/High alerts 🔔
  - Auto-refreshes every 1 second
  
- **📋 Logs Viewer** (`/logs`):
  - Table of all parsed logs
  - Filter by level, service, or message content
  - Shows timestamps, services, and messages

#### Step 4: Stop Monitoring
- Click **"Stop Monitoring"** to pause analysis
- Alerts are preserved; logs are retained in memory

## 📁 Project Structure

```
d:\Final Year Project\
├── 📄 app.py                      # Main Flask application (entry point)
├── 📄 log_generator.py            # Demo log generator (background thread)
├── 📄 log_watcher.py              # Real-time log file monitoring
├── 📄 parser.py                   # Log parsing with regex patterns
├── 📄 feature_engineering.py      # Extract ML features from logs
├── 📄 model.py                    # ML model wrapper (IsolationForest)
├── 📄 model_training.py           # Model initialization and training
├── 📄 alerts_storage.py           # In-memory alert queue (thread-safe)
├── 📄 logs_storage.py             # In-memory log storage (thread-safe)
├── 📄 requirements.txt            # Python dependencies
├── 📄 README.md                   # This file
│
├── ⚙️ config.json                 # User configuration (auto-generated)
├── 🤖 model.pkl                   # Trained ML model (auto-generated)
├── 📝 application.log             # Application logs (auto-generated)
│
├── 📁 templates/                  # HTML web pages
│   ├── index.html                 # Configuration page
│   ├── alerts.html                # Alert dashboard
│   └── logs.html                  # Logs viewer
│
└── 📁 logs/                       # Log directory
    └── application.log            # Monitor target log file
```

### Core Modules at a Glance

| File | Purpose | Type |
|------|---------|------|
| `app.py` | Flask server, routes, global state | Web Framework |
| `log_generator.py` | Generate demo logs | Background Thread |
| `log_watcher.py` | Monitor file for new logs | Background Thread |
| `parser.py` | Parse raw log lines | Utility |
| `feature_engineering.py` | Convert logs to ML features | Utility |
| `model.py` | ML anomaly detection | ML Model |
| `alerts_storage.py` | In-memory alert queue | Data Structure |
| `logs_storage.py` | In-memory log queue | Data Structure |

## 📋 Log Format

The system expects logs in a specific format. Any other format will be silently ignored (not parsed).

### Expected Format
```
YYYY-MM-DD HH:MM:SS LEVEL SERVICE message
```

### Field Descriptions
- **YYYY-MM-DD**: Date (ISO 8601)
- **HH:MM:SS**: Time in 24-hour format
- **LEVEL**: One of `INFO`, `WARN`, `ERROR`, or `WARNING` (WARNING → WARN)
- **SERVICE**: Single word identifying the source (e.g., PaymentService, UserService)
- **message**: Free-form text (may contain spaces)

### Valid Examples
```log
2026-04-20 10:30:45 ERROR PaymentService Transaction failed
2026-04-20 10:30:46 WARN DatabaseService Slow query detected
2026-04-20 10:30:47 INFO AuthService User login success
2026-04-20 10:30:48 WARNING CacheService Cache miss ratio high
```

### Invalid Examples (will be skipped)
```log
April 20, 2026 10:30:45 ERROR PaymentService ...  # Wrong date format
10:30:45 ERROR PaymentService ...                  # Missing date
2026-04-20 10:30:45 ERROR PaymentService          # Missing message
2026-04-20 10:30:45 ERROR Payment Service ...     # Service has space
```

## 🔬 How It Works: The Complete Pipeline

This section explains the journey of a log from raw text to an actionable alert.

### Step 1: Log Generation 📝
**File**: `log_generator.py`

```
Time: Every 2 seconds
┌─────────────────────────────────┐
│ Generate random log entry       │
├─────────────────────────────────┤
│ Service: Random from 5 services │
│ Level: Weighted distribution    │
│   • 60% INFO                    │
│   • 30% WARN                    │
│   • 10% ERROR                   │
└─────────────────────────────────┘
         ↓
  Write to log file
  (logs/application.log)
```

### Step 2: File Monitoring 👀
**File**: `log_watcher.py`

```
Polling Interval: Every 1 second
┌──────────────────────────────────────┐
│ Open log file and seek to last       │
│ known position (efficient!)          │
├──────────────────────────────────────┤
│ Read only NEW lines since last check │
│ (avoids reprocessing)                │
└──────────────────────────────────────┘
         ↓
  Pass raw lines to parser
```

### Step 3: Parsing 🔍
**File**: `parser.py`

```
Input:  "2026-04-20 10:30:45 ERROR PaymentService Transaction failed"

Regex Extraction:
  Date: 2026-04-20
  Time: 10:30:45
  Level: ERROR
  Service: PaymentService
  Message: Transaction failed

Output: Dictionary
{
  "timestamp": "2026-04-20 10:30:45",
  "level": "ERROR",
  "service": "PaymentService",
  "message": "Transaction failed"
}
```

### Step 4: Filtering 🔗
**File**: `log_watcher.py`

```
Apply user-configured filters:

Filter 1 - Log Levels
  Keep only: INFO, WARN, ERROR (user-selected)

Filter 2 - Keywords (optional)
  Keep only if message contains: failed, timeout, error

Output: Filtered logs that pass both filters
```

### Step 5: Feature Engineering 🧮
**File**: `feature_engineering.py`

```
Convert logs into numerical features for ML:

For each log, extract 4 features:

Feature 1: Log Level (numeric)
  INFO → 0 | WARN → 1 | ERROR → 2

Feature 2: Message Length
  Character count of message text
  Example: "Transaction failed" → 18

Feature 3: Error Frequency (rolling window)
  Count of ERROR logs in recent 10 logs
  Example: 3 errors in last 10 logs

Feature 4: Message Repetition
  How many times has this exact message appeared?
  Example: "Timeout" appeared 5 times

Output: NumPy array
[
  [2.0, 18.0, 3.0, 1.0],   ← Log 1 features
  [1.0, 25.0, 2.0, 2.0],   ← Log 2 features
  [2.0, 22.0, 4.0, 1.0],   ← Log 3 features
]
```

### Step 6: Anomaly Detection 🤖
**File**: `model.py`

```
Algorithm: IsolationForest (scikit-learn)

Concept:
  • Randomly isolates data points
  • Points isolated quickly = anomalies
  • Points isolated slowly = normal

For each feature set:

Prediction:
  -1 = ANOMALY (unusual pattern detected)
   1 = NORMAL (expected pattern)

Anomaly Score:
  Negative value = how anomalous
  Example: -0.35 (very anomalous)
           -0.05 (slightly anomalous)
            0.10 (normal)

Output: Prediction (-1 or 1) + Score (float)
```

### Step 7: Severity Mapping 📊
**File**: `model.py`

```
Combine anomaly score with context to calculate risk:

Risk Score Formula:
═══════════════════════════════════════

risk = 0.0

Component 1: Anomaly Intensity (max 4.0)
  if score <= -0.20: risk += 4.0 (very anomalous)
  elif score <= -0.10: risk += 3.0 (moderately)
  elif score <= -0.05: risk += 2.0 (slightly)
  else: risk += 1.0 (baseline)

Component 2: Log Level (max 3.0)
  risk += level_value × 1.5
  INFO (0):  +0.0
  WARN (1):  +1.5
  ERROR (2): +3.0

Component 3: Error Frequency (max 3.0)
  risk += min(error_count, 5) × 0.6
  1 error:  +0.6
  5+ errors: +3.0

Component 4: Message Repetition (max 2.0)
  risk += min(repeat_count, 5) × 0.4
  1 repeat:  +0.4
  5+ repeats: +2.0

═══════════════════════════════════════

Severity Assignment:
  if risk >= 8.0:  "Critical" 🔴
  if risk >= 6.0:  "High"     🟠
  if risk >= 4.0:  "Medium"   🟡
  else:            "Low"      🟢

Example Calculation:
  Anomaly score: -0.35 (very anomalous)  → 4.0
  Log level: ERROR (2)                   → 3.0
  Error frequency: 3 in window           → 1.8
  Message repeats: 2                     → 0.8
  ───────────────────────────────────────
  TOTAL RISK: 9.6  →  "Critical" 🔴
```

### Step 8: Alert Creation 🚨
**File**: `alerts_storage.py`

```
Only triggered for anomalies (prediction == -1)

Create Alert Object:
{
  "id": 0,
  "timestamp": "2026-04-20T10:30:45.123456",
  "log_timestamp": "2026-04-20 10:30:45",
  "service": "PaymentService",
  "message": "Transaction failed",
  "severity": "Critical",
  "log_level": "ERROR"
}

Properties:
  • Stored in memory (not database)
  • Newest alerts first
  • Max 500 alerts (auto-trim old ones)
  • Thread-safe access with locks
```

### Step 9: Display & Output 📡
**Files**: `app.py`, `templates/alerts.html`

```
Console Output:
  [Critical] PaymentService - Transaction failed

Web API (GET /api/alerts):
  {
    "alerts": [
      {
        "id": 0,
        "service": "PaymentService",
        "severity": "Critical",
        ...
      }
    ],
    "alert_counts": {
      "Critical": 5,
      "High": 3,
      "Medium": 1,
      "Low": 0
    }
  }

Web Dashboard (alerts.html):
  Shows:
  • Alert count cards (5 Critical, 3 High, etc.)
  • Real-time alert list
  • Auto-refreshes every 2 seconds
  • Filter by severity level
```

## ⚙️ Configuration

Configuration can be edited via the web UI or directly in `config.json`.

### Configuration File (config.json)
```json
{
  "log_path": "logs/application.log",
  "log_levels": ["INFO", "WARN", "ERROR"],
  "custom_levels": "",
  "keywords": "failed, timeout, error"
}
```

### Configuration Fields

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `log_path` | string | `"logs/application.log"` | Absolute or relative path to log file |
| `log_levels` | array | `["INFO", "WARN", "ERROR"]` | Predefined levels (used when custom_levels is empty) |
| `custom_levels` | string | `"ERROR,CRITICAL,DEBUG"` | Custom log levels (comma-separated, overrides log_levels when non-empty) |
| `keywords` | string | `"failed, timeout, error"` | Optional keyword filter (empty = no filtering) |

### How Configuration Filtering Works

#### Log Level Filtering

**Method 1: Predefined Levels (Default)**
```
If custom_levels is EMPTY:
  Use the log_levels array from checkboxes
  Example: ["INFO", "WARN", "ERROR"]
```

**Method 2: Custom Levels**
```
If custom_levels is NON-EMPTY:
  Use ONLY custom levels (ignore checkboxes)
  Example: "ERROR" → processes only ERROR logs
  Example: "CRITICAL,ERROR" → processes CRITICAL and ERROR logs
```

#### Keyword Filtering

Applied AFTER log level filtering:
- Empty string = no keyword filtering
- Non-empty = only logs containing a keyword are processed
- Case-insensitive substring match
- Example: keyword "fail" matches "failure", "FAILED", "failed"

### Configuration Examples

**Example 1: Monitor ERROR logs only**
```json
{
  "log_levels": ["INFO", "WARN", "ERROR"],
  "custom_levels": "ERROR",
  "keywords": ""
}
```
Result: Only ERROR level logs are processed

**Example 2: Monitor multiple custom levels**
```json
{
  "log_levels": ["INFO", "WARN", "ERROR"],
  "custom_levels": "CRITICAL,ERROR,HIGH",
  "keywords": ""
}
```
Result: CRITICAL, ERROR, and HIGH level logs are processed

**Example 3: Filter with keywords**
```json
{
  "log_levels": ["INFO", "WARN", "ERROR"],
  "custom_levels": "",
  "keywords": "failed,timeout,error"
}
```
Result: INFO, WARN, ERROR logs containing "failed", "timeout", or "error"

### Changing Configuration

#### ✨ Hot-Reload (NEW): Changes take effect immediately!

**Via Web UI**
1. Go to `http://localhost:5000/`
2. Modify settings (log levels, custom levels, keywords)
3. Click "Save Configuration"
4. **Changes are applied immediately** - no need to stop/restart monitoring!
5. Check Alerts tab to see new logs with updated filters (~1-2 seconds)

**Timeline**:
- `t=0s`: User saves configuration
- `t=0.1s`: Changes written to `config.json`
- `t=1-2s`: LogWatcher reloads config and applies new filters
- `t=3s`: New logs with updated filters appear in Alerts tab

**Direct File Edit**
1. Stop the application
2. Edit `config.json`
3. Restart the application
4. Changes take effect immediately on startup

## 🔔 Browser Notifications (NEW)

### Overview

Receive **automatic browser pop-up alerts** when Critical or High severity anomalies are detected. Notifications work independently of your log level configuration.

### Features

| Severity | Icon | Behavior | Example |
|----------|------|----------|---------|
| **Critical** 🔴 | 🔴 Red dot | Stays on screen, requires interaction | "Payment Service - ERROR" |
| **High** 🟠 | 🟠 Orange dot | Auto-dismisses after ~10 seconds | "Database Service - WARN" |

### How to Enable

1. When you first visit the application, you'll see a browser notification permission prompt
2. Click **"Allow"** to enable notifications
   - If you blocked it, change permissions in browser settings
3. Monitoring must be running and Alerts tab should be loaded

### Notification Behavior

- **Triggered**: Automatically when Critical or High severity alerts are created
- **Independent of configuration**: Notifications appear **regardless** of which log levels you filter by
  - Example: Even if monitoring only "INFO" logs, High/Critical alerts still notify
- **No duplicates**: Each alert notified only once
- **Real-time**: Notifications appear within 1-2 seconds of anomaly detection

### Browser Compatibility

✅ Works on: Chrome, Firefox, Edge, Safari (modern versions)  
❌ May not work: Older browsers, private browsing mode

### Troubleshooting Notifications

**Problem**: No notifications appearing

**Solution checklist**:
1. Ensure you clicked "Allow" when prompted
2. Check browser notification settings
3. Ensure monitoring is running (`/` page shows "Monitoring Active")
4. Visit `/alerts` page (notifications only work when on this page)
5. Wait for Critical/High severity alerts (may take 10-30 seconds with new logs)

**To manually grant permission**:
- **Chrome**: Settings → Privacy → Notifications → Add "localhost:5000"
- **Firefox**: Preferences → Privacy → Permissions → Notifications
- **Edge**: Settings → Privacy → Notifications

## 🔌 API Endpoints

### Web Pages (HTML)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Configuration page (set log path, levels, keywords) |
| `/alerts` | GET | Alert dashboard with real-time display |
| `/logs` | GET | Logs viewer with filtering options |

### Control Endpoints (JSON)

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/configure` | POST | Save configuration from form | HTML page (redirect) |
| `/start_monitoring` | POST | Start log watcher and generator | `{"success": bool, "message": str}` |
| `/stop_monitoring` | POST | Stop monitoring threads | `{"success": bool, "message": str}` |
| `/monitoring_status` | GET | Check if monitoring is running | `{"monitoring": bool}` |

### Data API Endpoints (JSON)

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/alerts` | GET | Get all alerts with counts | `{"alerts": [...], "alert_counts": {...}}` |
| `/api/clear_alerts` | POST | Clear all stored alerts | `{"success": bool}` |
| `/api/logs` | GET | Get parsed logs (newest 500) | `{"logs": [...]}` |

### Example: Get Alerts
```bash
curl http://localhost:5000/api/alerts
```

Response:
```json
{
  "alerts": [
    {
      "id": 0,
      "timestamp": "2026-04-20T10:30:45.123456",
      "log_timestamp": "2026-04-20 10:30:45",
      "service": "PaymentService",
      "message": "Transaction failed",
      "severity": "Critical",
      "log_level": "ERROR"
    }
  ],
  "alert_counts": {
    "Critical": 5,
    "High": 3,
    "Medium": 1,
    "Low": 0
  }
}
```

### Example: Start Monitoring
```bash
curl -X POST http://localhost:5000/start_monitoring
```

Response:
```json
{
  "success": true,
  "message": "Monitoring started"
}
```

## 🆘 Troubleshooting

### 1. Port Already in Use
**Error**: `Address already in use`

**Solution**: Change the port in `app.py` (line 228):
```python
# Change this:
app.run(debug=False, host="127.0.0.1", port=5000, use_reloader=False)

# To this:
app.run(debug=False, host="127.0.0.1", port=5001, use_reloader=False)
```

Then restart the application and access `http://localhost:5001`

---

### 2. Model Training Takes Too Long
**Symptom**: Application hangs on startup

**Explanation**: First run trains a model on dummy data (takes 5-10 seconds)

**Solution**: This only happens once. Subsequent runs load the cached `model.pkl` (~1 second)

**Workaround**: If stuck, delete `model.pkl` and let it retrain with fewer features

---

### 3. No Logs Being Generated
**Symptom**: Empty logs viewer, no alerts

**Possible Causes**:
1. `logs/` directory doesn't exist
2. Directory is not writable
3. Monitoring not started

**Solutions**:
- Create directory: `mkdir logs`
- Check permissions: `ls -la logs/`
- Check web UI: Is "Start Monitoring" button clicked?
- Check console: Look for error messages when starting

---

### 4. Anomalies Not Being Detected
**Symptom**: Monitoring running but no alerts generated

**Explanation**: IsolationForest needs variety in data to detect anomalies

**Solution**: 
1. Let monitoring run for 2-3 minutes to generate enough logs
2. Ensure ERROR logs are being generated (check `/logs` page)
3. Check that anomaly score is sufficiently negative (model calibration)

**Advanced**: Edit `contamination` in `model.py` (line 12):
```python
# Increase to detect more anomalies (expects 15% to be anomalies):
self.model = IsolationForest(contamination=0.15)  # default: 0.1
```

---

### 5. Browser Doesn't Auto-Open
**Symptom**: Console says "Opening browser" but nothing happens

**Solution**: Manually open `http://localhost:5000`

**Note**: Some systems require manual browser launch due to firewall/permissions

---

### 6. Logs Not Matching Pattern
**Symptom**: Logs appear in file but not in logs viewer

**Explanation**: Log line doesn't match expected format

**Check**:
- Date format: `YYYY-MM-DD` (not `MM/DD/YYYY` or `DD-MM-YYYY`)
- Service name: Single word (no spaces)
- Has all 5 required components: date, time, level, service, message

**Example Valid Log**:
```
2026-04-20 10:30:45 ERROR PaymentService Transaction failed
├─ date (✓)
├─ time (✓)
├─ level (✓)
├─ service (✓)
└─ message (✓)
```

---

### 7. High Memory Usage
**Symptom**: Application memory grows over time

**Cause**: Default limits keep 500 alerts and 500 logs in memory

**Solution**: Reduce limits in storage classes:
```python
# In alerts_storage.py, line 10:
self.max_alerts = 250  # reduced from 500

# In logs_storage.py, line 10:
self.max_logs = 250    # reduced from 500
```

---

### 8. Performance Issues
**Symptom**: CPU high, slow dashboard refresh

**Solution**:
1. Reduce log generation frequency in `app.py` (line 150):
   ```python
   demo_generator.start(interval=5)  # increased from 2 seconds
   ```

2. Reduce log watcher polling frequency in `log_watcher.py` (line 37):
   ```python
   log_watcher.start(check_interval=2)  # increased from 1 second
   ```

3. Reduce dashboard refresh rate in `templates/alerts.html`:
   ```javascript
   // Change polling interval (currently 1000ms = 1 second)
   setInterval(fetchAlerts, 5000);  // slower: 5 seconds
   ```

---

### 9. Configuration Changes Not Taking Effect

**Symptom**: Changed configuration but alerts still show old logs/levels

**Solution**:
- Configuration changes are automatically applied within 1-2 seconds
- Wait a moment and refresh the page
- Check that you clicked **"Save Configuration"** button
- Verify monitoring is still running (status shows "Monitoring Active")

**If changes still not working**:
1. Stop monitoring (click "Stop Monitoring")
2. Verify config.json was saved: Check file modification time
3. Start monitoring again

---

### 10. Custom Log Levels Not Filtering

**Symptom**: Added custom levels but seeing all log levels

**Solution**:
- If Custom Log Levels field is **empty**: Uses predefined checkboxes
- If Custom Log Levels field has content: **Only** those levels are monitored
- Make sure you **left Custom Log Levels empty** OR **provided the exact level names**

**Example**:
- ✅ Correct: Type `ERROR` in custom field → only ERROR logs shown
- ✅ Correct: Leave custom field empty, check INFO checkbox → only INFO logs shown
- ❌ Wrong: Have both custom field filled AND checkboxes checked (custom takes priority!)

---

### Getting Help

If issues persist:
1. Check `application.log` for error messages
2. Review console output when starting app
3. Ensure Python version is 3.8+: `python --version`
4. Verify all dependencies installed: `pip list | grep -E 'Flask|scikit|numpy'`

## 📦 Dependencies

All dependencies are listed in `requirements.txt`:

```
Flask==3.0.0
scikit-learn==1.4.0
numpy==1.26.0
```

### Dependency Purposes

| Package | Version | Purpose |
|---------|---------|---------|
| **Flask** | 3.0.0+ | Web framework for HTTP server and routes |
| **scikit-learn** | 1.4.0+ | Machine learning library (IsolationForest algorithm) |
| **NumPy** | 1.26.0+ | Numerical computing (array operations) |

### Installation Details

**Install everything at once:**
```bash
pip install -r requirements.txt
```

**Install individually (if needed):**
```bash
pip install Flask==3.0.0
pip install scikit-learn==1.4.0
pip install numpy==1.26.0
```

**Check installed versions:**
```bash
pip list | grep -E 'Flask|scikit-learn|numpy'
```

### Version Compatibility

- **Python**: 3.8 or higher (tested on 3.9+)
- **pip**: Should auto-resolve dependency chains
- **Virtual Environment**: Recommended (avoid conflicts)

**Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 📚 Architecture & Design

The system uses a **pipeline architecture** where data flows through specialized modules:

```
Logs Generated
    ↓
File Monitored (log_watcher.py)
    ↓
Parsed (parser.py)
    ↓
Filtered (keywords, log levels)
    ↓
Features Extracted (feature_engineering.py)
    ↓
ML Model Predictions (model.py)
    ↓
Severity Calculated (model.py)
    ↓
Alerts Created (alerts_storage.py)
    ↓
Web Dashboard (Flask + HTML)
```

### Key Design Patterns

1. **Thread Safety**: RLock in storage classes prevents race conditions
2. **File Polling**: Efficient incremental reading using file position tracking
3. **Background Workers**: DemoLogGenerator and LogWatcher run in separate threads
4. **Stateless Parsing**: Each log parsed independently
5. **Feature Normalization**: Raw logs converted to numerical features for ML
6. **Risk Scoring**: Multi-factor approach for severity classification

### Thread Model

- **Main Thread**: Flask web server
- **LogWatcher Thread**: Monitors log file, processes logs
- **DemoLogGenerator Thread**: Generates test logs
- **All threads**: Daemon mode (exit with main process)

### Memory Architecture

- **alerts_storage**: In-memory list (max 500, thread-safe)
- **logs_storage**: In-memory list (max 500, thread-safe)
- **No database**: All data volatile (resets on restart)
- **Persistent**: Only `config.json` and `model.pkl` saved to disk

---

## 🎓 About This Project

This is an intelligent anomaly detection system for log monitoring, created as a final year project. It demonstrates:

- **Real-time data processing** with file I/O and polling
- **Machine learning** with scikit-learn (IsolationForest)
- **Web development** with Flask and REST APIs
- **Concurrent programming** with Python threading
- **Data engineering** (feature extraction, normalization)
- **Risk scoring** with multi-factor algorithms

### Use Cases

- **IT Operations**: Monitor application logs for anomalies
- **System Administration**: Detect unusual patterns in system logs
- **Security**: Identify suspicious log patterns
- **DevOps**: Alert on anomalous service behavior
- **Educational**: Learn ML, Flask, threading, and data pipelines

---

## 📝 License

Demo project for educational purposes.

---

**Last Updated**: April 27, 2026  
**Version**: 1.1  
**Author**: Final Year Project

### Version History

**v1.1 (April 27, 2026)** - Enhanced Monitoring Features
- ✨ Added browser notifications for Critical/High severity alerts
- ✨ Added custom log level filtering
- ✨ Implemented hot-reload configuration (changes apply without restart)
- 📝 Updated documentation with new features

**v1.0 (April 22, 2026)** - Initial Release
- Core log monitoring and anomaly detection
- Web dashboard with real-time alerts
- ML-based severity classification
