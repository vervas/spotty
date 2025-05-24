#!/usr/bin/with-contenv bashio
# ==============================================================================
# Start the Spotty NFC Bridge service
# ==============================================================================

# Get config values
CONFIG_PATH=/data/options.json
DEVICE=$(bashio::config 'device')
SCAN_INTERVAL=$(bashio::config 'scan_interval')
LOG_LEVEL=$(bashio::config 'log_level')

# Convert log level to Python format
case $LOG_LEVEL in
  "trace" | "debug")
    PYTHON_LOG_LEVEL="DEBUG"
    ;;
  "info" | "notice")
    PYTHON_LOG_LEVEL="INFO"
    ;;
  "warning")
    PYTHON_LOG_LEVEL="WARNING"
    ;;
  "error")
    PYTHON_LOG_LEVEL="ERROR"
    ;;
  "fatal")
    PYTHON_LOG_LEVEL="CRITICAL"
    ;;
  *)
    PYTHON_LOG_LEVEL="INFO"
    ;;
esac

# Create runtime config
cat > /tmp/spotty_config.yaml << EOF
device: ${DEVICE}
scan_interval: ${SCAN_INTERVAL}
log_level: ${PYTHON_LOG_LEVEL}
# No token needed - using Home Assistant API access
ha_url: http://supervisor/core
EOF

bashio::log.info "Starting Spotty NFC Bridge..."
bashio::log.info "Device: ${DEVICE}"
bashio::log.info "Scan interval: ${SCAN_INTERVAL}"
bashio::log.info "Log level: ${LOG_LEVEL}"

# Run the application
python3 -m spotty.main --config /tmp/spotty_config.yaml
