"""
Generate a synthetic, deliberately-messy UrbanCart product catalog.

Mimics a raw export from a PIM (Product Information Management) system where
thousands of sellers self-entered listings in inconsistent formats.
Run:  python src/generate_catalog.py
Output: data/raw/urbancart_product_catalog_raw.csv  (~5000 rows)
"""

import random
import pandas as pd
from faker import Faker

# Seeds make randomness REPRODUCIBLE: same seed -> same "random" data every run.
# Critical for a shareable project — a teammate running this gets an identical dataset.
fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

N_PRODUCTS = 5000

# --- Messiness menus: real catalogs contain all these variants for the SAME concept ---
CATEGORY_VARIANTS = [
    "Fashion", "fashion", "Apparel", "Clothing", "Men Fashion", "Women Fashion", "Ethnic Wear",
    "Electronics", "electronics", "Mobiles & Accessories", "Gadgets", "Audio",
    "Home & Kitchen", "home", "Home Decor", "Kitchen Appliances",
    "Footwear", "Shoes", "Sandals",
    None,   # some sellers leave category blank
]

STOCK_STATUS_VARIANTS = [
    "In Stock", "in stock", "IN STOCK", "Available", "available", "3 left", "1 left",
    "Out of Stock", "OOS", "out of stock", "Sold Out", "Coming Soon", None,
]

RATING_VARIANTS = (
    [str(round(r, 1)) for r in [x * 0.1 for x in range(10, 51)]]  # "1.0".."5.0" as text
    + ["Good", "Excellent", "Poor", "NA", "N/A", "Not Rated", "4.5 stars", "---", None]
)

PRODUCT_NAME_TEMPLATES = [
    "{adj} Cotton Kurti", "{adj} Silk Saree", "Wireless Earbuds {model}",
    "{adj} Bluetooth Speaker", "Men's {adj} Kurta Pajama Set", "{adj} Nighty",
    "Smart Watch {model}", "{adj} Steel Tiffin Box", "Women's {adj} Leggings",
]
ADJECTIVES = ["Premium", "Soft", "Elegant", "Designer", "Classic", "Trendy", "Handloom"]
CATEGORY_CODES = {"Fashion": "FAS", "Electronics": "ELE", "Home & Kitchen": "HOM", "Footwear": "FOO"}

def make_messy_price(base_price: int) -> str:
    """
    Render an integer price in ONE of 5 messy real-world string formats.
    This is what the Stage 5.8 clean_price() function will later have to reverse.
    """
    fmt = random.choice(["numeric", "rupee_symbol", "comma_format", "k_suffix", "text_slash"])
    if fmt == "numeric":
        return str(base_price)                       # "1999"
    if fmt == "rupee_symbol":
        return f"₹{base_price:,}"                     # "₹1,999"
    if fmt == "comma_format":
        return f"{base_price:,}"                      # "1,999"
    if fmt == "k_suffix":
        return f"{round(base_price / 1000, 1)}k"      # "2.0k"
    if fmt == "text_slash":
        return f"Rs {base_price}/-"                   # "Rs 1999/-"
    
def generate_messy_product_record(record_id: int) -> dict:
    """Build ONE realistic, messy product catalog record (a dict of ~19 fields)."""
    true_category = random.choice(["Fashion", "Electronics", "Home & Kitchen", "Footwear"])
    cat_code = CATEGORY_CODES[true_category]
    base_price = random.randint(199, 49999)

    record = {
        "sku": f"UC-{cat_code}-{record_id:06d}",
        "product_name": random.choice(PRODUCT_NAME_TEMPLATES).format(
            adj=random.choice(ADJECTIVES), model=f"X{random.randint(1, 99)}"
        ),
        "category": random.choice(CATEGORY_VARIANTS),      # messy variant, not true_category
        "brand": fake.company(),
        "seller_name": fake.company(),
        "price": make_messy_price(base_price),
        "mrp": base_price + random.randint(-200, 3000),    # sometimes < price (a violation)
        "discount_pct": random.choice([5, 10, 15, 20, 30, 50, 70, 90]),  # 90 is out-of-range
        "stock_quantity": random.randint(-2, 200),         # negative is impossible (a violation)
        "stock_status": random.choice(STOCK_STATUS_VARIANTS),
        "cod_available": random.choice([True, False]),
        "pincode_serviceable_sample_count": random.randint(100, 20000),
        "rating": random.choice(RATING_VARIANTS),
        "num_reviews": random.randint(0, 5000),
        "sizes_available": random.choice(["S,M,L,XL", "Free Size", "6,7,8,9,10", None]),
        "color": random.choice(["Red", "Blue", "Black", "Green", "Multicolor", None]),
        "warranty_months": random.choice([0, 6, 12, 24, None]),
        "return_window_days": random.choice([7, 14, 30, 45, None]),  # 45 exceeds policy
        "description": fake.sentence(nb_words=8),
        "last_updated": fake.date_time_this_year().isoformat(),
    }

    # Inject ~10% missing values into a random non-critical field (real seller sloppiness)
    if random.random() < 0.10:
        field = random.choice(["brand", "color", "warranty_months", "num_reviews", "seller_name"])
        record[field] = None

    return record


def main():
    records = [generate_messy_product_record(i) for i in range(N_PRODUCTS)]

    # Inject ~3% duplicate SKUs (re-listings): copy an existing SKU onto some later rows
    for _ in range(int(N_PRODUCTS * 0.03)):
        i, j = random.randint(0, N_PRODUCTS - 1), random.randint(0, N_PRODUCTS - 1)
        records[j]["sku"] = records[i]["sku"]

    df = pd.DataFrame(records)
    df.to_csv("data/raw/urbancart_product_catalog_raw.csv", index=False)
    print(f"Generated {len(df)} products -> data/raw/urbancart_product_catalog_raw.csv")
    print(f"Columns ({len(df.columns)}): {list(df.columns)}")
    print(df.head())


if __name__ == "__main__":
    main()    