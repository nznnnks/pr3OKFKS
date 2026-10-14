import csv
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python course_skateshop/import_products_csv.py <path-to-products.csv>")
        return 2

    csv_path = sys.argv[1]

    # Import the existing app module to reuse DB session + helpers.
    sys.path.insert(0, "course_skateshop")
    import app as violentdeck_app  # noqa: E402

    try:
        violentdeck_app.ensure_db_initialized()
    except Exception as exc:
        print(f"Database is unavailable: {exc}")
        return 1

    imported = 0
    created = 0
    updated = 0
    skipped = 0

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        with violentdeck_app.SessionLocal() as db_session:
            for row in reader:
                if not isinstance(row, dict):
                    skipped += 1
                    continue

                category_slug = str(row.get("category_slug", "")).strip().lower()
                name = str(row.get("name", "")).strip()
                description = str(row.get("description", "")).strip()
                image_url = str(row.get("image_url", "")).strip()
                price_raw = str(row.get("price", "")).strip()

                if not category_slug or not name or not description or not price_raw:
                    skipped += 1
                    continue

                if (
                    len(category_slug) > 50
                    or len(name) > violentdeck_app.PRODUCT_NAME_MAX_LENGTH
                    or len(description) > violentdeck_app.DESCRIPTION_MAX_LENGTH
                    or len(image_url) > violentdeck_app.IMAGE_URL_MAX_LENGTH
                ):
                    skipped += 1
                    continue

                price = violentdeck_app.parse_product_price(price_raw)
                if price is None:
                    skipped += 1
                    continue

                category = violentdeck_app.ensure_category_for_import(db_session, category_slug)

                product = None
                raw_id = row.get("id")
                if raw_id is not None and str(raw_id).strip():
                    try:
                        product = db_session.scalar(
                            violentdeck_app.select(violentdeck_app.Product).where(
                                violentdeck_app.Product.id == int(str(raw_id).strip())
                            )
                        )
                    except (TypeError, ValueError):
                        product = None

                if product is None:
                    product = db_session.scalar(
                        violentdeck_app.select(violentdeck_app.Product).where(
                            violentdeck_app.Product.name == name,
                            violentdeck_app.Product.category_slug == category.slug,
                        )
                    )

                created_at = violentdeck_app.parse_datetime_value(row.get("created_at"))

                if product is None:
                    product = violentdeck_app.Product(
                        category_slug=category.slug,
                        name=name,
                        description=description,
                        image_url=image_url or category.image,
                        price=price,
                    )
                    if created_at is not None:
                        product.created_at = created_at
                    db_session.add(product)
                    created += 1
                else:
                    product.category_slug = category.slug
                    product.name = name
                    product.description = description
                    product.image_url = image_url or category.image
                    product.price = price
                    if created_at is not None:
                        product.created_at = created_at
                    updated += 1

                imported += 1

            db_session.commit()

    print(
        f"Imported rows: {imported}. Created: {created}. Updated: {updated}. Skipped: {skipped}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
