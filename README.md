# MS Teams Push Notification using the GTA API

This repository contains a script that fetches intervention data from the Global Trade Alert (GTA) API and sends it as a formatted message to a Microsoft Teams channel using webhooks.

## Setup Guide

Follow these steps to set up and run the MS Teams Push notification system:

### 1. Clone the Repository

```
git clone git@github.com:global-trade-alert/ms-teams-push.git
cd ms-teams-push
```

### 2. Set up a webhook in Microsoft Teams

1. Open Microsoft Teams and navigate to the channel where you want to receive notifications
2. Click on the three dots (...) next to the channel name and select "Manage channel"
3. Click on "Connectors" in the right panel
4. Search for "Incoming Webhook" and click "Configure"
5. Provide a name for your webhook (e.g., "GTA Notifications")
6. Optionally, upload an icon for the webhook
7. Click "Create"
8. Copy the webhook URL that is generated - you'll need this for the .env file
9. Click "Done" to finish the setup

### 3. Create a GTA API Key

1. Go to the Global Trade Alert website: https://globaltradealert.org/account/api-keys
2. Log in to your account (or create one if you don't have it)
3. Navigate to your account settings or API section
4. Generate a new API key
5. Copy the API key - you'll need this for the .env file

### 4. Configure Environment Variables

1. In the root directory of this repository, create a file named `.env`
2. Add the following lines to the file:
   ```
   WEBHOOK_URL=your_teams_webhook_url_here
   GTA_API_KEY=your_gta_api_key_here
   ```
3. Replace `your_teams_webhook_url_here` with the webhook URL you copied from Teams
4. Replace `your_gta_api_key_here` with the API key you generated from the GTA website

### 5. Install Requirements

1. Make sure you have Python 3.6 or higher installed
2. Open a terminal/command prompt
3. Navigate to the repository directory
4. Run the following command to install the required packages:
   ```
   pip install -r requirements.txt
   ```

### 6. Run the Script

1. In the terminal/command prompt, make sure you're in the repository directory
2. Run the script with the following command:
   ```
   python main.py
   ```
3. If everything is set up correctly, you should see a message in your Teams channel with the latest intervention data from GTA

## Customizing Intervention Retrieval

By default, the script retrieves only one intervention from the United States (country code 840). You might want to customize the `get_interventions` method in `main.py` to retrieve different interventions based on your needs.

### Common Customizations

Open `main.py` and locate the `get_interventions` function (around line 45). You can modify the payload parameters:

```python
payload = json.dumps({
    "limit": 1,        
    "offset": 0,       
    "request_data": {
        "implementer": [
            840        
        ]
    }
})
```


For more details on available filter options, refer to the [GTA API documentation](https://github.com/global-trade-alert/docs/blob/main/.api/gta-data.md).

## Troubleshooting

- If you see an error about missing environment variables, make sure your `.env` file is correctly set up with both the WEBHOOK_URL and GTA_API_KEY
- If the script runs but no message appears in Teams, check that your webhook URL is correct and that the webhook is properly configured in your Teams channel
- If you see an error related to the GTA API, verify that your API key is valid and correctly entered in the `.env` file

For any other issues, check the error messages in the terminal for more information.
