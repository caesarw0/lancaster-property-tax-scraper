# Lancaster County Tax Delinquency Scraper

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Playwright](https://img.shields.io/badge/playwright-1.41+-green.svg)](https://playwright.dev/)

An automated Python script to extract delinquent tax information from Lancaster County, PA's public parcel viewer system.

## How It Works

### Overall Workflow
```mermaid
graph LR
    A["Input Parcel List"] --> B["Initialize Scraper"]
    B --> C["Process Each Parcel"]
    C --> D["Check for<br/>Delinquent Taxes"]
    D --> E{"Has Delinquent<br/>Taxes?"}
    E -->|"Yes"| F["Extract Data"]
    E -->|"No"| G["Skip Parcel"]
    F --> H["Add to Results"]
    G --> C
    H --> C
    C --> I["Export to CSV"]
```

### Data Extraction Process
```mermaid
graph TD
    A["Parcel Page"] --> B["Basic Info"]
    A --> C["Tax Info"]
    B --> D["Parcel Number"]
    B --> E["Property Address"]
    B --> F["Owner Details"]
    C --> G["Tax Year<br/>2022-2024"]
    C --> H["Amount Due"]
    C --> I["Amount Paid"]
    C --> J["Total Due"]
    G & H & I & J --> K["CSV Record"]
```

### Error Handling & Rate Limiting
```mermaid
sequenceDiagram
    participant S as Scraper
    participant W as Web Server
    participant D as Database
    S->>W: Request Parcel Page
    Note over S,W: 2-5 second delay
    W->>S: Return Page
    S->>S: Extract Data
    alt Success
        S->>D: Store Results
    else Network Timeout
        S->>S: Retry Request
    else No Data Found
        S->>S: Log & Skip
    end
```

## Features

- Automated scraping of delinquent tax data from Lancaster County's parcel viewer
- Handles multiple parcel numbers in batch
- Extracts data for tax years 2022-2024
- Collects property address and owner information
- Outputs results to CSV format
- Built-in rate limiting to prevent server overload
- Only captures parcels with actual delinquent taxes

## Data Extracted

For each parcel with delinquent taxes, the script collects:
- Parcel number
- Property address
- Owner information
- Tax year (2022-2024)
- Amount due
- Amount paid
- Total due
- Scrape date

## Prerequisites

- Python 3.7+
- Playwright
- Pandas

## Installation

1. Clone this repository:
```bash
git clone https://github.com/caesarw0/lancaster-property-tax-scraper.git
cd lancaster-property-tax-scraper
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

## Usage

1. Prepare a list of parcel numbers in the script or import them from a file.

2. Run the script:
```bash
python src/property_scraper.py
```

The script will:
- Process each parcel number
- Extract delinquent tax information if available
- Save results to `output/delinquent_taxes.csv`

### Example Code

```python
from property_scraper import scrape_multiple_parcels

parcel_numbers = [
    "5408465600000",
    "1200794700000",
]

df = scrape_multiple_parcels(parcel_numbers)
```

## Rate Limiting

The script includes built-in delays between requests (2-5 seconds) to avoid overwhelming the server. This helps ensure:
- Ethical scraping practices
- Reduced likelihood of IP blocking
- Server resource conservation

## Output Format

The script generates a CSV file with the following columns:
- parcel_number
- address
- owner
- scrape_date
- tax_year
- amount_due
- amount_paid
- total_due

## Error Handling

The script includes robust error handling for:
- Network timeouts
- Missing data
- Invalid parcel numbers
- Server errors

## Legal Notice

This tool is designed for legitimate data collection from publicly available information. Users should:
- Review and comply with Lancaster County's terms of service
- Use reasonable request rates
- Respect the public resource

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)