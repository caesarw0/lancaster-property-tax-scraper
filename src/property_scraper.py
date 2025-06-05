from playwright.sync_api import sync_playwright, TimeoutError
import pandas as pd
import time
import random
from datetime import datetime

class LancasterTaxScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with browser settings."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            viewport={"width": 1280, "height": 800}
        )
        self.page = self.context.new_page()
        
    def close(self):
        """Close browser and playwright."""
        self.browser.close()
        self.playwright.stop()

    def navigate_to_parcel(self, parcel_number, tax_year="2025", timeout=60000):
        """Navigate to a specific parcel page."""
        url = f"https://lancasterpa.devnetwedge.com/parcel/view/{parcel_number}/{tax_year}"
        print(f"Visiting parcel: {parcel_number}")
        try:
            self.page.goto(url, timeout=timeout)
            self.page.wait_for_load_state('networkidle')
            # Add random delay between 2-5 seconds to avoid rate limiting
            time.sleep(random.uniform(2, 5))
            return True
        except TimeoutError:
            print(f"Error: Failed to navigate to parcel {parcel_number}")
            return False

    def get_text_after_label(self, label_text):
        """Extract text value following a label."""
        try:
            elements = self.page.query_selector_all(f'div.row:has-text("{label_text}")')
            for element in elements:
                label = element.query_selector('div.col-sm-5')
                if label and label_text in label.inner_text():
                    value = element.query_selector('div.col-sm-7')
                    if value:
                        return value.inner_text().strip()
        except Exception as e:
            print(f"Error getting {label_text}: {e}")
        return None

    def extract_delinquent_taxes(self):
        """Extract delinquent tax information from the page."""
        try:
            # Try different possible table selectors
            tax_table = None
            selectors = [
                'table:has-text("Delinquent Taxes")',
                'h3:has-text("Delinquent Taxes") + table',
                'div:has-text("Delinquent Taxes") > table',
                'div.table-responsive:has-text("Delinquent Taxes") table'
            ]
            
            for selector in selectors:
                tax_table = self.page.query_selector(selector)
                if tax_table:
                    break
            
            if not tax_table:
                print("No delinquent taxes table found")
                return None
            
            data = []
            rows = tax_table.query_selector_all('tr')
            
            # Skip header row
            for row in rows[1:]:
                cells = row.query_selector_all('td')
                if len(cells) >= 3:
                    try:
                        tax_year = cells[0].inner_text().strip()
                        due_amount = cells[1].inner_text().strip().replace('$', '').replace(',', '')
                        paid_amount = cells[2].inner_text().strip().replace('$', '').replace(',', '')
                        total_due = cells[3].inner_text().strip().replace('$', '').replace(',', '')
                        
                        # Convert to float and handle empty strings
                        due_amount = float(due_amount) if due_amount else 0.0
                        paid_amount = float(paid_amount) if paid_amount else 0.0
                        total_due = float(total_due) if total_due else 0.0
                        
                        # Only include years 2022-2024 with amounts due
                        if tax_year in ['2022', '2023', '2024'] and total_due > 0:
                            data.append({
                                'tax_year': tax_year,
                                'amount_due': due_amount,
                                'amount_paid': paid_amount,
                                'total_due': total_due
                            })
                    except ValueError as e:
                        print(f"Error parsing amounts for year {tax_year}: {e}")
                        continue
            
            return data if data else None
        except Exception as e:
            print(f"Error extracting delinquent taxes: {e}")
            return None

    def get_owner_info(self):
        """Extract complete owner information from Related Names section."""
        try:
            # Find the Related Names section
            related_section = self.page.query_selector('div:has-text("Related Names")')
            if related_section:
                # Find the specific row containing Parcel Owner
                owner_row = related_section.query_selector('div.row:has-text("Parcel Owner")')
                if owner_row:
                    # Get the value column (col-sm-8) which contains the owner info
                    value_col = owner_row.query_selector('div.col-sm-8')
                    if value_col:
                        # Get the complete text including name and address
                        return value_col.inner_text().rstrip(',').strip()
            
            return "Owner information not found"
            
        except Exception as e:
            print(f"Error getting owner info: {e}")
            return "Error retrieving owner information"

    def scrape_parcel(self, parcel_number):
        """Scrape data for a single parcel."""
        if not self.navigate_to_parcel(parcel_number):
            return None

        # Get basic parcel info
        parcel_data = {
            'parcel_number': parcel_number,
            'address': self.get_text_after_label("Site Address"),
            'owner': self.get_owner_info(),
            'scrape_date': datetime.now().strftime("%Y-%m-%d")
        }

        # Get delinquent tax data
        tax_data = self.extract_delinquent_taxes()
        if not tax_data:
            print(f"No delinquent taxes found for parcel {parcel_number}")
            return None

        # Create rows for each tax year
        rows = []
        for tax_info in tax_data:
            row = parcel_data.copy()
            row.update(tax_info)
            rows.append(row)

        return rows

def scrape_multiple_parcels(parcel_numbers, output_file="output/delinquent_taxes.csv"):
    """Scrape multiple parcels and save to CSV."""
    all_data = []
    scraper = LancasterTaxScraper(headless=False)

    try:
        for parcel in parcel_numbers:
            parcel_data = scraper.scrape_parcel(parcel)
            if parcel_data:
                all_data.extend(parcel_data)
    finally:
        scraper.close()

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(output_file, index=False)
        print(f"\nData saved to {output_file}")
        print("\nSample of scraped data:")
        print(df.head())
        return df
    else:
        print("No delinquent tax data found for any parcels.")
        return None

if __name__ == "__main__":
    # Test parcel numbers
    test_parcels = [
        "5408465600000",
        "1200794700000",
    ]
    
    print("Starting Lancaster County Tax Delinquency Scraper...")
    print(f"Parcels to process: {len(test_parcels)}")
    
    df = scrape_multiple_parcels(test_parcels) 