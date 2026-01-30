# NextEnergy
Home Assistant integration NextEnergy (Dutch Energy supplier)

> ⚠️ **WORK IN PROGRESS**
>
> This project is currently under active development.
> The solution is **not stable**, **not complete**, and **not ready for production use**.
>
> ....and....just doesn't work yet ...
> 
![Status](https://img.shields.io/badge/status-work_in_progress-orange)
![Stability](https://img.shields.io/badge/stability-unstable-red)

Validation status:
[![Type Checking](https://github.com/clousberg/NextEnergy/actions/workflows/type_checking.yaml/badge.svg)](https://github.com/clousberg/NextEnergy/actions/workflows/type_checking.yaml)
[![Validate](https://github.com/clousberg/NextEnergy/actions/workflows/validate.yaml/badge.svg)](https://github.com/clousberg/NextEnergy/actions/workflows/validate.yaml)
[![Validate with hassfest](https://github.com/clousberg/NextEnergy/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/clousberg/NextEnergy/actions/workflows/hassfest.yaml)
[![Validate with Ruff Lint](https://github.com/clousberg/NextEnergy/actions/workflows/Ruff%20Lint.yaml/badge.svg)](https://github.com/clousberg/NextEnergy/actions/workflows/Ruff%20Lint.yaml)


# NextEnergy Home Assistant Integration

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Version](https://img.shields.io/github/v/release/clousberg/NextEnergy)](https://github.com/clousberg/NextEnergy/releases)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Issues](https://img.shields.io/github/issues/clousberg/NextEnergy)](https://github.com/clousberg/NextEnergy/issues)
[![Quality Scale](https://img.shields.io/badge/Quality-Bronze-yellow)](https://developers.home-assistant.io/docs/quality_scale/)

## Description
NextEnergy API integration for Home Assistant. Provides current and next hour electricity prices via sensors.
Currently supporting  Market and Market+ rates.

## Sensors
- `sensor.nextenergy_current_market`
- `sensor.nextenergy_current_market_plus`
- `sensor.nextenergy_next_market`
- `sensor.nextenergy_next_market_plus`

## Notes
- Market = raw exchange price.
- Market+ = all-in price (market price + energy tax + VAT).

## Installation
1. Add this repo as a [custom repository in HACS](https://hacs.xyz/docs/faq/custom_repositories/).
2. Install via HACS.
3. Restart Home Assistant.
4. Add the integration via the UI and provide your credentials (or use `secrets.yaml`).

## Configuration
1. Go to Settings → Devices & Services → Add Integration → NextEnergy
2. Enter your username and password.
3. Finish setup and sensors will appear.

## Debugging
Add the following to configuration.yaml.

``
  logs:
    custom_components.nextenergy: debug
``

## License
This project is licensed under the MIT License - see the LICENSE file for details.
