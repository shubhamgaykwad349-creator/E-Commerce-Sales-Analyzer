import os
import pandas as pd
import matplotlib.pyplot as plt

EXPECTED_COLUMNS = ["Order_ID", "Product", "Category", "Quantity", "Price"]


def format_number(value):
    """Format whole floats as integers (e.g., 32500.0 -> 32500) for clean output."""
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}"


def load_and_clean_data(file_path):
    """
    Read CSV using Pandas, clean invalid or duplicate rows,
    and compute Revenue = Quantity * Price.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return pd.DataFrame(columns=EXPECTED_COLUMNS + ["Revenue"])
    raw_df = pd.read_csv(file_path, header=None, dtype=str, keep_default_na=False)

    if raw_df.empty:
        return pd.DataFrame(columns=EXPECTED_COLUMNS + ["Revenue"])

    
    first_row = [str(cell).strip().lower() for cell in raw_df.iloc[0].tolist()]
    if first_row[:5] == ["order_id", "product", "category", "quantity", "price"]:
        raw_df = raw_df.iloc[1:].reset_index(drop=True)

    valid_rows = []
    seen_order_ids = set()

    for idx, row in raw_df.iterrows():
        row_num = idx + 1  

        if len(row) < 5:
            print(f"Row {row_num} skipped: missing columns")
            continue

        order_id = str(row[0]).strip()
        product = str(row[1]).strip()
        category = str(row[2]).strip()
        raw_qty = str(row[3]).strip()
        raw_price = str(row[4]).strip()

        
        if not order_id or not product or not category:
            print(f"Row {row_num} skipped: missing Order_ID, Product, or Category")
            continue

        
        if order_id in seen_order_ids:
            print(f"Row {row_num} skipped: duplicate Order_ID '{order_id}'")
            continue

        
        try:
            qty_val = float(raw_qty)
            if not qty_val.is_integer():
                print(f"Row {row_num} skipped: invalid Quantity '{raw_qty}'")
                continue
            qty = int(qty_val)
        except ValueError:
            print(f"Row {row_num} skipped: invalid Quantity '{raw_qty}'")
            continue

        if qty <= 0:
            print(f"Row {row_num} skipped: Quantity must be positive")
            continue

    
        try:
            price = float(raw_price)
        except ValueError:
            print(f"Row {row_num} skipped: invalid Price '{raw_price}'")
            continue

        if price <= 0:
            print(f"Row {row_num} skipped: Price must be positive")
            continue

        seen_order_ids.add(order_id)
        valid_rows.append({
            "Order_ID": order_id,
            "Product": product,
            "Category": category,
            "Quantity": qty,
            "Price": price
        })

    clean_df = pd.DataFrame(valid_rows, columns=EXPECTED_COLUMNS)

    if not clean_df.empty:
        clean_df["Quantity"] = pd.to_numeric(clean_df["Quantity"])
        clean_df["Price"] = pd.to_numeric(clean_df["Price"])
        clean_df["Revenue"] = clean_df["Quantity"] * clean_df["Price"]
    else:
        clean_df["Revenue"] = pd.Series(dtype=float)

    return clean_df


def show_summary(df):
    """Menu Option 1: Display overall revenue, orders, units sold, and top product."""
    if df.empty:
        print("Total Revenue: 0 | Orders: 0")
        print("Units sold: 0 | Top product: N/A")
        return

    total_revenue = df["Revenue"].sum()
    total_orders = len(df)
    total_units = int(df["Quantity"].sum())

    
    product_sales = (
        df.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values(by="Revenue", ascending=False)
    )
    top_product = product_sales.iloc[0]["Product"]
    top_revenue = product_sales.iloc[0]["Revenue"]

    print(f"Total Revenue: {format_number(total_revenue)} | Orders: {total_orders}")
    print(f"Units sold: {total_units} | Top product: {top_product} ({format_number(top_revenue)})")


def show_category_revenue(df):
    """Menu Option 2: Display category-wise revenue breakdown and Pie Chart."""
    if df.empty:
        print("No valid data available for category analysis.")
        return

    total_revenue = df["Revenue"].sum()
    category_sales = (
        df.groupby("Category", as_index=False)["Revenue"]
        .sum()
        .sort_values(by="Revenue", ascending=False)
    )

    for _, row in category_sales.iterrows():
        cat = row["Category"]
        rev = row["Revenue"]
        pct = (rev / total_revenue) * 100
        print(f"{cat}: {format_number(rev)} ({pct:.2f}%)")

    plt.figure(figsize=(7, 5))
    plt.pie(
        category_sales["Revenue"],
        labels=category_sales["Category"],
        autopct="%1.2f%%",
        startangle=140
    )
    plt.title("Category-wise Revenue")
    plt.axis("equal")
    plt.tight_layout()
    print("Pie chart 'Category-wise Revenue' displayed")
    plt.show()


def show_top_products(df):
    """Menu Option 3: Display Top 5 selling products by revenue and Bar Chart."""
    if df.empty:
        print("No valid data available for product analysis.")
        return

    top_5 = (
        df.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values(by="Revenue", ascending=False)
        .head(5)
    )

    print("\n--- Top 5 Selling Products by Revenue ---")
    for rank, (_, row) in enumerate(top_5.iterrows(), start=1):
        print(f"{rank}. {row['Product']}: {format_number(row['Revenue'])}")

    plt.figure(figsize=(8, 5))
    bars = plt.bar(top_5["Product"], top_5["Revenue"], color="#2b6cb0")
    plt.title("Top 5 Selling Products by Revenue")
    plt.xlabel("Product")
    plt.ylabel("Revenue")

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            format_number(height),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    print("Bar chart 'Top 5 Selling Products by Revenue' displayed")
    plt.show()


def main():
    file_path = input("Enter CSV file path (default: orders.csv): ").strip()
    if not file_path:
        file_path = "orders.csv"

    df = load_and_clean_data(file_path)

    while True:
        print("\n=== E-Commerce Sales Analyzer ===")
        print("1. Summary (Total Revenue, Orders, Units Sold, Top Product)")
        print("2. Category-wise Revenue (with Pie Chart)")
        print("3. Top 5 Selling Products by Revenue (with Bar Chart)")
        print("4. Exit")

        choice = input("Select menu option (1-4): ").strip()

        if choice == "1":
            show_summary(df)
        elif choice == "2":
            show_category_revenue(df)
        elif choice == "3":
            show_top_products(df)
        elif choice == "4":
            print("Exiting E-Commerce Sales Analyzer.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()