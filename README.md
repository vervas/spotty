# Spotty - Home Assistant NFC Bridge

A bridge between a PN532 NFC reader connected to a Raspberry Pi and Home Assistant's native tag system. This project runs as a Home Assistant add-on, making it easy to manage NFC tags directly from your Home Assistant interface.

## Features

- Reads NFC/RFID tags using a PN532 reader connected via UART
- Integrates with Home Assistant's native tag system
- Automatically registers scanned tags with Home Assistant
- Runs as a Home Assistant add-on for seamless integration
- No token or authentication setup required
- Uses uv for Python dependency management

## Hardware Requirements

- Raspberry Pi (running Home Assistant OS)
- PN532 NFC/RFID reader connected via UART to `/dev/ttyAMA0`

## Installation

### Option 1: Install as a Home Assistant Add-on

1. In Home Assistant, go to **Settings** → **Add-ons** → **Add-on Store**
2. Click the three dots menu in the upper right corner and select **Repositories**
3. Add this repository URL
4. Find the "Spotty NFC Bridge" add-on in the list and click **Install**

### Option 2: Create a Custom Add-on Repository

The recommended way to install custom add-ons is through a repository:

1. Create a GitHub repository with this structure:
   ```
   my-addons-repo/
   ├── spotty/
   │   ├── config.json
   │   ├── Dockerfile
   │   └── ... (all other files)
   └── repository.json
   ```

2. Create a `repository.json` file:
   ```json
   {
     "name": "My NFC Add-ons Repository",
     "url": "https://github.com/yourusername/my-addons-repo",
     "maintainer": "Your Name <your.email@example.com>"
   }
   ```

3. In Home Assistant, go to **Settings** → **Add-ons** → **Add-on Store** → ⋮ → **Repositories**
4. Add your repository URL
5. The Spotty add-on will appear in the add-on store

## Configuration

After installing the add-on, you can configure it directly from the Home Assistant UI:

1. Go to the add-on page
2. Click on **Configuration** tab
3. Set the following options:
   - **device**: The path to your NFC reader (default: `/dev/ttyAMA0`)
   - **scan_interval**: Time between scans in seconds (default: `0.5`)
   - **log_level**: The logging level (default: `info`)

## Usage

The add-on will automatically start after installation. When an NFC tag is scanned, it will be registered with Home Assistant and can be used in automations.

To manage your tags:
1. Go to Home Assistant → **Settings** → **Tags**
2. You'll see your scanned tags appear here automatically
3. Click on a tag to create automations for it

## Troubleshooting

Check the add-on logs for any issues:

1. Go to the add-on page
2. Click on the **Logs** tab

Or check the logs from SSH:

```bash
ha addons logs spotty
```
