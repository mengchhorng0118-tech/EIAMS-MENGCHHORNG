"""
Management command: add_phone_images
Usage: python manage.py add_phone_images

Sets official Apple CDN image URLs for all iPhone inventory items and assets.
No files are downloaded — images are served directly from store.storeimages.cdn-apple.com
"""

from django.core.management.base import BaseCommand


# Official Apple Store CDN image URLs for each iPhone model
# These are the same images shown on apple.com product pages
IPHONE_IMAGES = {
    # iPhone 12
    'Apple iPhone 12 (128GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone12-black-select-2020?wid=940&hei=1112&fmt=png-alpha&.v=1604343704000',
    'Apple iPhone 12 (256GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone12-black-select-2020?wid=940&hei=1112&fmt=png-alpha&.v=1604343704000',

    # iPhone 13
    'Apple iPhone 13 (128GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone13-black-select-2021?wid=940&hei=1112&fmt=png-alpha&.v=1629842709000',
    'Apple iPhone 13 (256GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone13-black-select-2021?wid=940&hei=1112&fmt=png-alpha&.v=1629842709000',

    # iPhone 14
    'Apple iPhone 14 (128GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone14-black-select-202209?wid=940&hei=1112&fmt=png-alpha&.v=1660753619946',
    'Apple iPhone 14 (256GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone14-black-select-202209?wid=940&hei=1112&fmt=png-alpha&.v=1660753619946',
    'Apple iPhone 14 Pro (256GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone14pro-deeppurple-select?wid=940&hei=1112&fmt=png-alpha&.v=1663703841896',

    # iPhone 15
    'Apple iPhone 15 (128GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone15-black-select-202309?wid=940&hei=1112&fmt=png-alpha&.v=1693086369688',
    'Apple iPhone 15 (256GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone15-black-select-202309?wid=940&hei=1112&fmt=png-alpha&.v=1693086369688',
    'Apple iPhone 15 Pro (256GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone15pro-blacktitanium-select?wid=940&hei=1112&fmt=png-alpha&.v=1693060286192',
    'Apple iPhone 15 Pro Max (512GB)':
        'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone15pro-blacktitanium-select?wid=940&hei=1112&fmt=png-alpha&.v=1693060286192',

    # iPhone 16
    'Apple iPhone 16 (128GB)':
        'https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone16-black-select-202409?wid=940&hei=1112&fmt=png-alpha&.v=1723814059648',
    'Apple iPhone 16 (256GB)':
        'https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone16-black-select-202409?wid=940&hei=1112&fmt=png-alpha&.v=1723814059648',
    'Apple iPhone 16 Pro (256GB)':
        'https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone16pro-blacktitanium-select-202409?wid=940&hei=1112&fmt=png-alpha&.v=1723821319778',
    'Apple iPhone 16 Pro Max (512GB)':
        'https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone16pro-blacktitanium-select-202409?wid=940&hei=1112&fmt=png-alpha&.v=1723821319778',

    # iPhone 17  (using iPhone 16 images as 17 not yet on CDN)
    'Apple iPhone 17 (256GB)':
        'https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone16-black-select-202409?wid=940&hei=1112&fmt=png-alpha&.v=1723814059648',
    'Apple iPhone 17 (512GB)':
        'https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone16-black-select-202409?wid=940&hei=1112&fmt=png-alpha&.v=1723814059648',
    'Apple iPhone 17 Pro (256GB)':
        'https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone16pro-blacktitanium-select-202409?wid=940&hei=1112&fmt=png-alpha&.v=1723821319778',
    'Apple iPhone 17 Pro (512GB)':
        'https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone16pro-blacktitanium-select-202409?wid=940&hei=1112&fmt=png-alpha&.v=1723821319778',
    'Apple iPhone 17 Pro Max (512GB)':
        'https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone16pro-blacktitanium-select-202409?wid=940&hei=1112&fmt=png-alpha&.v=1723821319778',
}


class Command(BaseCommand):
    help = 'Set Apple CDN image URLs for all iPhone inventory items and assets'

    def handle(self, *args, **options):
        from apps.inventory.models import InventoryItem
        from apps.assets.models import Asset

        self.stdout.write(self.style.SUCCESS('=== Setting iPhone Product Images ==='))

        # ── Inventory items ────────────────────────────────────
        updated_items = 0
        for item in InventoryItem.objects.filter(category__category_name='Mobile Phones'):
            # Match by name prefix (strip storage size for fallback)
            url = IPHONE_IMAGES.get(item.item_name)
            if not url:
                # fallback: match by model base (e.g. "Apple iPhone 16 Pro")
                for key, val in IPHONE_IMAGES.items():
                    if item.item_name.startswith(key.rsplit(' ', 1)[0]):
                        url = val
                        break
            if url and item.image_url != url:
                item.image_url = url
                item.save(update_fields=['image_url'])
                self.stdout.write(f'  ✔ Item image set: {item.item_name}')
                updated_items += 1

        # ── Assets ─────────────────────────────────────────────
        updated_assets = 0
        for asset in Asset.objects.filter(category__category_name='Mobile Devices'):
            url = IPHONE_IMAGES.get(asset.asset_name)
            if not url:
                for key, val in IPHONE_IMAGES.items():
                    if asset.asset_name.startswith(key.rsplit(' ', 1)[0]):
                        url = val
                        break
            if url and asset.image_url != url:
                asset.image_url = url
                asset.save(update_fields=['image_url'])
                updated_assets += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Done: {updated_items} inventory items + {updated_assets} assets updated with images.'
        ))
