# Grocy Filament Inventory

A custom Home Assistant integration to track 3D printer filament from your [Grocy](https://grocy.info/) inventory. Each filament product in the specified group is exposed as a separate sensor, showing the aggregated amount in grams. The sensor icon can also reflect the filament color if provided in Grocy.

## Features

- Fetches all filament products from a specified product group in Grocy.
- Each filament becomes a separate sensor with:
  - Name: `Filament <Product Name>`
  - Unit: grams (`g`)
  - Optional color icon based on Grocy userfields
- Automatic updates using a DataUpdateCoordinator.
- Full GUI configuration via Home Assistant config flow.

## Configuration

1. Go to **Settings > Devices & Services > Integrations** in Home Assistant.
2. Click **Add Integration** and choose **Grocy Filament Inventory**.
3. Enter your Grocy server URL and API key.
4. The integration will fetch product groups and automatically use the `Filament` group (or prompt to retry if not found).

## Requirements

- Home Assistant 2024.12 or later.
- A running Grocy instance with API access.
- Filament products assigned to a product group in Grocy.

## Installation

1. Copy the `custom_components/grocy_filament_inventory` folder to your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Add the integration via the UI.

## Notes

- The filament color is optional and is read from the `userfields.filament_color` field in Grocy. Default color is white (`#FFFFFF`) if not set.
- The sensor values automatically update according to the coordinator's update interval (default: 60 seconds).

