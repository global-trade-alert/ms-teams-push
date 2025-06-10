#!/usr/bin/env python3
import os
import sys
import json
import logging
import requests

from typing import Optional, Dict, Any
from dotenv import load_dotenv


logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s'
)


def send_teams_message(webhook_url: str, message_payload: Dict[str, Any]) -> Optional[requests.Response]:
	"""
	Sends a message payload to a Microsoft Teams Incoming Webhook.

	Args:
		webhook_url: The URL of the Teams Incoming Webhook.
		message_payload: The JSON payload for the message (e.g., simple text or an Adaptive Card).

	Returns:
		A requests.Response object on success, or None on failure.
	"""

	headers = {"Content-Type": "application/json"}

	try:
		response = requests.post(
			webhook_url,
			headers=headers,
			data=json.dumps(message_payload)
		)
		response.raise_for_status()
		return response
	except requests.exceptions.RequestException as e:
		logging.error(f"Error sending message to Teams: {e}")
		return None


def get_interventions(api_key: str) -> list:
	_url = "https://api.globaltradealert.org/api/v1/data/"

	payload = json.dumps({
		"limit": 1,
		"offset": 0,
		"request_data": {
			"implementer": [
				840
			]
		}
	})
	headers = {
		'Content-Type': 'application/json',
		'Authorization': f'APIKey {api_key}'
	}

	response = requests.request("POST", _url, headers=headers, data=payload)
	if response.status_code != 200:
		logging.error(f"Error retrieving interventions: {response.text}")
		return []
	return response.json()


def _generate_adaptive_card(data: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Creates an Adaptive Card payload from a single intervention data dictionary.

	Args:
		data: The dictionary containing intervention details.

	Returns:
		The complete JSON payload for the Adaptive Card to be sent to Teams.
	"""
	title = data.get('state_act_title', 'N/A')
	intervention_url = data.get('intervention_url', '#')
	evaluation = data.get('gta_evaluation', 'N/A')
	affected_list = data.get('affected_jurisdictions', [])
	implementers_list = data.get('implementing_jurisdictions', [])
	intervention_type = data.get('intervention_type', 'N/A')
	mast_chapter = data.get('mast_chapter', 'N/A')
	date_implemented = data.get('date_implemented', 'N/A')

	is_in_force = data.get('is_in_force', 0)
	implementation_level = data.get('implementation_level', 'N/A')
	affected_products = data.get('affected_products', [])
	affected_sectors = data.get('affected_sectors', [])

	implementer_names = [i.get('name', 'N/A') for i in implementers_list]
	affected_names = [j.get('name', 'N/A') for j in affected_list]

	if len(implementer_names) > 5:
		display_implementer = ", ".join(implementer_names[:5]) + f", and {len(implementer_names) - 5} more."
	else:
		display_implementer = ", ".join(implementer_names) if implementer_names else "N/A"

	if len(affected_names) > 5:
		display_affected = ", ".join(affected_names[:5]) + f", and {len(affected_names) - 5} more."
	else:
		display_affected = ", ".join(affected_names) if affected_names else "N/A"

	color_map = {
		"Red": "attention",
		"Amber": "warning",
		"Green": "good"
	}
	status_color = color_map.get(evaluation, "default")

	force_status = "In Force" if is_in_force else "Not In Force"
	force_color = "good" if is_in_force else "attention"

	num_products = len(affected_products)
	num_sectors = len(affected_sectors)

	card = {
		"type": "AdaptiveCard",
		"$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
		"version": "1.5",
		"body": [
			{
				"type": "TextBlock",
				"text": title,
				"weight": "bolder",
				"size": "medium",
				"wrap": True,
				"horizontalAlignment": "Center",
				"style": "heading",
			},
			{
				"type": "ColumnSet",
				"columns": [
					{
						"type": "Column",
						"width": "stretch",
						"items": [
							{
								"type": "TextBlock",
								"text": f"GTA Evaluation: {evaluation}",
								"weight": "bolder",
								"color": status_color,
								"spacing": "small"
							}
						]
					},
					{
						"type": "Column",
						"width": "stretch",
						"items": [
							{
								"type": "TextBlock",
								"text": f"Status: {force_status}",
								"weight": "bolder",
								"color": force_color,
								"spacing": "small",
								"horizontalAlignment": "right"
							}
						]
					}
				]
			},
			{
				"type": "Container",
				"style": "emphasis",
				"spacing": "medium",
				"items": [
					{
						"type": "FactSet",
						"spacing": "medium",
						"facts": [
							{"title": "Intervention Type", "value": intervention_type},
							{"title": "MAST Chapter", "value": mast_chapter},
							{"title": "Implementation Level", "value": implementation_level},
							{"title": "Date Implemented", "value": date_implemented},
							{"title": "Affected Products", "value": f"{num_products} product(s)"},
							{"title": "Affected Sectors", "value": f"{num_sectors} sector(s)"}
						]
					}
				]
			},
			{
				"type": "Container",
				"spacing": "medium",
				"items": [
					{
						"type": "TextBlock",
						"text": "**Implementing Jurisdictions:**",
						"wrap": True,
						"weight": "bolder",
						"spacing": "medium"
					},
					{
						"type": "TextBlock",
						"text": display_implementer,
						"wrap": True,
						"spacing": "small"
					}
				]
			},
			{
				"type": "Container",
				"spacing": "medium",
				"items": [
					{
						"type": "TextBlock",
						"text": "**Affected Jurisdictions:**",
						"wrap": True,
						"weight": "bolder",
						"spacing": "medium"
					},
					{
						"type": "TextBlock",
						"text": display_affected,
						"wrap": True,
						"spacing": "small"
					}
				]
			},
			{
				"type": "Container",
				"spacing": "medium",
				"items": [
					{
						"type": "ActionSet",
						"actions": [
							{
								"type": "Action.OpenUrl",
								"title": "View Full Intervention Details",
								"url": intervention_url,
								"style": "positive"
							}
						]
					}
				]
			}
		]
	}

	return {
		"type": "message",
		"attachments": [{
			"contentType": "application/vnd.microsoft.card.adaptive",
			"content": card
		}]
	}


if __name__ == "__main__":
	load_dotenv()

	WEBHOOK_URL = os.getenv("WEBHOOK_URL")
	GTA_API_KEY = os.getenv("GTA_API_KEY")

	if not WEBHOOK_URL:
		logging.error("FATAL: The 'WEBHOOK_URL' environment variable is not set.")
		logging.error("Set the environment variable in your .env file and try again.")
		sys.exit(1)


	if not GTA_API_KEY:
		logging.error("FATAL: The 'GTA_API_KEY' environment variable is not set.")
		logging.error("Set the environment variable in your .env file and try again.")
		sys.exit(1)


	interventions = get_interventions(GTA_API_KEY)

	if len(interventions):
		payload = _generate_adaptive_card(interventions[0])
		print(json.dumps(payload, indent=2))

		response = send_teams_message(WEBHOOK_URL, payload)

		if response:
			logging.info("Message sent successfully!")
			logging.debug(f"Response Text: {response.text}")
		else:
			logging.error("Failed to send message. Check the logs above for details.")
	else:
		logging.info("No interventions found.")
