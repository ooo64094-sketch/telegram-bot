import os
import io
import logging
import requests
from PIL import Image
import pytesseract
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ALLOWED_USERS = {127859316, 781782960, 78539704, 736810149, 806135538, 763153242, 7734083418, 8126651104}

PRICE_TABLE = {
    950: """950 ليره
👜 جنط: تحميل الف دينار = 32 الف
👟 حذاء: تحميل الف دينار = 32 الف
👕 ملابس: تحميل 3 الاف = 34 الف""",

    990: """990 ليره
👜 جنط: تحميل الف دينار = 33 الف
👟 حذاء: تحميل الف دينار = 33 الف
👕 ملابس: تحميل 3 الاف = 35 الف""",

    1090: """1090 ليره
👜 جنط: تحميل الف ونص = 37 الف
👟 حذاء: تحميل الف ونص = 37 الف
👕 ملابس: تحميل 3 ونص = 39 الف""",

    1190: """1190 ليره
👜 جنط: تحميل الف وربع = 40 الف
👟 حذاء: تحميل الف وربع = 40 الف
👕 ملابس: تحميل 5 وربع = 44 الف""",

    1250: """1250 ليره
👜 جنط: تحميل الف وربع = 42 الف
👟 حذاء: تحميل الف وربع = 42 الف
👕 ملابس: تحميل 6 وربع = 47 الف""",

    1290: """1290 ليره
👜 جنط: تحميل الف دينار = 43 الف
👟 حذاء: تحميل الف دينار = 43 الف
👕 ملابس: تحميل 7 الاف = 49 الف""",

    1490: """1490 ليره
👜 جنط: تحميل 500 دينار = 49 الف
👟 حذاء: تحميل 500 دينار = 49 الف
👕 ملابس: تحميل 3 ونص = 52 الف""",

    1590: """1590 ليره
👜 جنط: تحميل الف وربع = 53 الف
👟 حذاء: تحميل الف وربع = 53 الف
👕 ملابس: تحميل 3 وربع = 55 الف""",

    1690: """1690 ليره
👜 جنط: بدون تحميل = 55 الف
👟 حذاء: بدون تحميل = 55 الف
👕 ملابس: تحميل 7 الاف = 62 الف""",

    1790: """1790 ليره
👜 جنط: تحميل 750 دينار = 59 الف
👟 حذاء: تحميل 750 دينار = 59 الف
👕 ملابس: تحميل 8 و750 دينار = 67 الف""",

    1890: """1890 ليره
👜 جنط: تحميل 3 ونص = 65 الف
👟 حذاء: تحميل 3 ونص = 65 الف
👕 ملابس: تحميل 9 ونص = 71 الف""",

    1990: """1990 ليره
👜 جنط: تحميل 3 وربع = 68 الف
👟 حذاء: تحميل 3 وربع = 68 الف
👕 ملابس: تحميل 9 وربع = 74 الف""",

    2290: """2290 ليره
👜 جنط: تحميل 3 ونص = 78 الف
👟 حذاء: تحميل 3 ونص = 78 الف
👕 ملابس: تحميل 7 ونص = 82 الف""",

    2490: """2490 ليره
👜 جنط: تحميل 3 الف = 84 الف
👟 حذاء: تحميل 3 الف = 84 الف
👕 ملابس: تحميل 9 الف = 90 الف""",

    2690: """2690 ليره
👜 جنط: تحميل 3 ونص = 91 الف
👟 حذاء: تحميل 3 ونص = 91 الف
👕 ملابس: تحميل 10 ونص = 98 الف""",

    2790: """2790 ليره
👜 جنط: تحميل 3 وربع = 94 الف
👟 حذاء: تحميل 3 وربع = 94 الف
👕 ملابس: تحميل 9 وربع = 100 الف""",

    2990: """2990 ليره
👜 جنط: تحميل 3 و750 = 101 الف
👟 حذاء: تحميل 3 و750 = 101 الف
👕 ملابس: تحميل 10 و750 = 108 الف""",

    3290: """3290 ليره
👜 جنط: تحميل 4 الف = 111 الف
👟 حذاء: تحميل 4 الف = 111 الف
👕 ملابس: تحميل 12 الف = 119 الف""",

    3490: """3490 ليره
👜 جنط: تحميل 5 ونص = 119 الف
👟 حذاء: تحميل 5 ونص = 119 الف
👕 ملابس: تحميل 12 ونص = 126 الف""",

    3690: """3690 ليره
👜 جنط: تحميل 10 الف = 130 الف
👟 حذاء: تحميل 10 الف = 130 الف
👕 ملابس: تحميل 15 الف = 135 الف""",

    3790: """3790 ليره
👜 جنط: تحميل 10 ونص = 134 الف
👟 حذاء: تحميل 10 ونص = 134 الف
👕 ملابس: تحميل 15 ونص = 139 الف""",

    4490: """4490 ليره
👜 جنط: تحميل 11 الف = 157 الف
👟 حذاء: تحميل 11 الف = 157 الف
👕 ملابس: تحميل 15 الف = 161 الف""",

    4990: """4990 ليره
👜 جنط: تحميل 11 ونص = 174 الف
👟 حذاء: تحميل 11 ونص = 174 الف
👕 ملابس: تحميل 14 ونص = 177 الف""",

    5690: """5690 ليره
👜 جنط: تحميل 11 و750 = 197 الف
👟 حذاء: تحميل 11 و750 = 197 الف
👕 ملابس: تحميل 15 و750 = 201 الف""",

    6290: """6290 ليره
👜 جنط: تحميل 11 وربع = 216 الف
👟 حذاء: تحميل 11 وربع = 216 الف
👕 ملابس: تحميل 20 وربع = 225 الف""",

    6690: """6690 ليره
👜 جنط: تحميل 11 وربع = 229 الف
👟 حذاء: تحميل 11 وربع = 229 الف
👕 ملابس: تحميل 25 وربع = 243 الف""",

    7290: """7290 ليره
👜 جنط: تحميل 27 و750 = 265 الف
👟 حذاء: تحميل 27 و750 = 265 الف
👕 ملابس: تحميل 27 و750 = 265 الف""",

    7990: """7990 ليره
👜 جنط: تحميل 30 الف = 290 الف
👟 حذاء: تحميل 30 الف = 290 الف
👕 ملابس: تحميل 40 الف = 300 الف""",

    8690: """8690 ليره
👜 جنط: تحميل 20 الف = 303 الف
👟 حذاء: تحميل 20 الف = 303 الف
👕 ملابس: تحميل 37 الف = 320 الف""",

    8990: """8990 ليره
👜 جنط: تحميل 20 وربع = 313 الف
👟 حذاء: تحميل 20 وربع = 313 الف
👕 ملابس: تحميل 40 وربع = 333 الف""",

    9590: """9590 ليره
👜 جنط: تحميل 38 و750 = 351 الف
👟 حذاء: تحميل 38 و750 = 351 الف
👕 ملابس: تحميل 48 و750 = 361 الف""",

    11990: """11990 ليره
👜 جنط: تحميل 40 و750 = 431 الف
👟 حذاء: تحميل 40 و750 = 431 الف
👕 ملابس: تحميل 60 و750 = 451 الف""",
}


def round_price(value):
    value = int(value)
    remainder = value % 1000
    if remainder == 0 or remainder == 500:
        return value
    elif remainder < 500:
        return value + (500 - remainder)
    else:
        return value + (1000 - remainder)


def format_number(n):
    return f"{int(n):,}".replace(",", "،")


TURKISH_DOMAINS = {
    "trendyol.com", "hepsiburada.com", "n11.com", "amazon.com.tr",
    "pazarama.com", "lcwaikiki.com", "zara.com", "mavi.com",
    "koton.com", "boyner.com.tr", "morhipo.com", "migros.com.tr",
    "defacto.com.tr", "bershka.com", "pullandbear.com",
    "stradivarius.com", "massimodutti.com", "adidas.com.tr",
    "nike.com.tr", "puma.com", "mango.com", "beymen.com", "hm.com",
    "markafoni.com", "gittigidiyor.com", "sahibinden.com",
    "fashionfriends.com", "modanisa.com", "ebebek.com",
}

BRAND_MAP = {
    "zara": "Zara", "زارا": "Zara",
    "bershka": "Bershka", "بيرشكا": "Bershka",
    "mango": "Mango", "مانكو": "Mango",
    "adidas": "Adidas", "اديداس": "Adidas",
    "nike": "Nike", "نايك": "Nike",
    "puma": "Puma", "بوما": "Puma",
    "lcwaikiki": "LC Waikiki", "lc waikiki": "LC Waikiki",
    "defacto": "DeFacto", "ديفاكتو": "DeFacto",
    "koton": "Koton", "كوتون": "Koton",
    "pullandbear": "Pull&Bear", "pull&bear": "Pull&Bear", "pull and bear": "Pull&Bear",
    "stradivarius": "Stradivarius",
    "massimodutti": "Massimo Dutti", "massimo dutti": "Massimo Dutti",
    "hm": "H&M", "h&m": "H&M",
    "boyner": "Boyner",
    "beymen": "Beymen",
    "mavi": "Mavi",
    "lacoste": "Lacoste",
    "tommy": "Tommy Hilfiger", "tommy hilfiger": "Tommy Hilfiger",
    "calvin klein": "Calvin Klein",
    "gucci": "Gucci",
    "louis vuitton": "Louis Vuitton",
    "versace": "Versace",
    "balenciaga": "Balenciaga",
    "shein": "Shein",
    "temu": "Temu",
}


def detect_brand(text: str) -> str | None:
    if not text:
        return None
    lower = text.strip().lower()
    for keyword, brand in BRAND_MAP.items():
        if keyword in lower:
            return brand
    return None


def extract_ocr_text(image_bytes: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img, lang="eng+tur+ara", timeout=10)
        cleaned = " ".join(text.split())
        return cleaned[:300]
    except Exception as e:
        logger.warning(f"OCR failed: {e}")
        return ""


def is_turkish_url(url: str) -> bool:
    url_lower = url.lower()
    if ".com.tr" in url_lower or url_lower.endswith(".tr") or "/.tr/" in url_lower:
        return True
    for domain in TURKISH_DOMAINS:
        if domain in url_lower:
            return True
    return False


def is_product_page(url: str) -> bool:
    indicators = ["/p/", "/product/", "/urun/", "/item/", "-p-", "productid", "pid=", "/pd/", "/dp/"]
    url_lower = url.lower()
    return any(ind in url_lower for ind in indicators)


def serpapi_lens(image_url: str, brand: str | None, serpapi_key: str) -> list:
    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": serpapi_key,
        "hl": "tr",
        "gl": "tr",
    }
    if brand:
        params["query"] = brand
    resp = requests.get("https://serpapi.com/search", params=params, timeout=25)
    data = resp.json()
    results = []
    for item in data.get("visual_matches", []):
        link = item.get("link", "")
        if link:
            results.append(link)
    return results


def serpapi_text_search(query: str, serpapi_key: str) -> list:
    params = {
        "engine": "google",
        "q": query,
        "api_key": serpapi_key,
        "hl": "tr",
        "gl": "tr",
        "num": 10,
    }
    resp = requests.get("https://serpapi.com/search", params=params, timeout=20)
    data = resp.json()
    results = []
    for item in data.get("organic_results", []):
        link = item.get("link", "")
        if link:
            results.append(link)
    return results


def rank_and_deduplicate(links: list, limit: int = 10) -> list:
    seen = set()
    turkish_product = []
    turkish_general = []
    global_product = []
    global_general = []

    for url in links:
        if url in seen:
            continue
        seen.add(url)
        is_tr = is_turkish_url(url)
        is_prod = is_product_page(url)
        if is_tr and is_prod:
            turkish_product.append(url)
        elif is_tr:
            turkish_general.append(url)
        elif is_prod:
            global_product.append(url)
        else:
            global_general.append(url)

    ordered = turkish_product + turkish_general + global_product + global_general
    return ordered[:limit]


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ALLOWED_USERS:
        return

    serpapi_key = os.environ.get("SERPAPI_KEY", "")
    if not serpapi_key:
        await update.message.reply_text("❌ مفتاح البحث غير متوفر")
        return

    caption = update.message.caption or ""
    brand_from_caption = detect_brand(caption)

    photo = update.message.photo[-1]
    tg_file = await context.bot.get_file(photo.file_id)
    image_url = tg_file.file_path

    await update.message.reply_text("🔍 جاري البحث...")

    all_links = []

    try:
        image_bytes = requests.get(image_url, timeout=15).content
        ocr_text = extract_ocr_text(image_bytes)
    except Exception as e:
        logger.warning(f"Image download failed: {e}")
        image_bytes = b""
        ocr_text = ""

    brand = brand_from_caption or detect_brand(ocr_text)

    try:
        lens_links = serpapi_lens(image_url, brand, serpapi_key)
        all_links.extend(lens_links)
    except Exception as e:
        logger.error(f"Google Lens error: {e}")

    if brand:
        try:
            query = f"{brand} site:trendyol.com OR site:hepsiburada.com OR site:lcwaikiki.com OR site:n11.com"
            text_links = serpapi_text_search(query, serpapi_key)
            all_links.extend(text_links)
        except Exception as e:
            logger.error(f"Text search error: {e}")

    if ocr_text and len(ocr_text) > 5:
        try:
            ocr_brand = detect_brand(ocr_text)
            q = f"{ocr_brand + ' ' if ocr_brand else ''}{ocr_text[:80]} Türkiye"
            ocr_links = serpapi_text_search(q, serpapi_key)
            all_links.extend(ocr_links)
        except Exception as e:
            logger.error(f"OCR search error: {e}")

    ranked = rank_and_deduplicate(all_links, limit=10)

    if not ranked:
        await update.message.reply_text(
            "لم أجد رابطاً واضحاً لهذه الصورة، جرّب صورة أوضح أو اكتب اسم البراند مع الصورة"
        )
        return

    brand_line = f"البراند المرجح: {brand}\n\n" if brand else ""
    best = f"أفضل نتيجة:\n1. {ranked[0]}"
    rest_lines = "\n".join(f"{i+2}. {url}" for i, url in enumerate(ranked[1:]))
    extra = f"\nروابط إضافية:\n{rest_lines}" if rest_lines else ""
    reply = f"نتائج البحث عن القطعة\n\n{brand_line}{best}{extra}"
    await update.message.reply_text(reply)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ALLOWED_USERS:
        return

    text = update.message.text.strip().replace(" ", "")

    if text.startswith("ح"):
        raw = text[1:]
        extra_profit = 0

        if "+" in raw:
            parts = raw.split("+", 1)
            price_part = parts[0]
            try:
                extra_profit = int(parts[1])
            except ValueError:
                await update.message.reply_text("❌ صيغة غير صحيحة. مثال: ح1590 أو ح1590+10")
                return
        else:
            price_part = raw

        try:
            price = float(price_part)
        except ValueError:
            await update.message.reply_text("❌ صيغة غير صحيحة. مثال: ح1590 أو ح1590+10")
            return

        iraqi_price = (price / 4300) * 140000
        target_price = (price / 4300) * 160000 + 7000 + (extra_profit * 1000)
        rounded_final_price = round_price(target_price)
        loading = rounded_final_price - iraqi_price

        reply = (
            f"تحميل ترينديول والمواقع الخارجية\n\n"
            f"السعر بالعراقي: {format_number(iraqi_price)}\n"
            f"التحميل الذي تضيفه للسستم: {format_number(loading)}\n"
            f"السعر النهائي للزبون: {format_number(rounded_final_price)}"
        )
        await update.message.reply_text(reply)
        return

    if not text.isdigit():
        return

    number = int(text)

    if number in PRICE_TABLE:
        await update.message.reply_text(PRICE_TABLE[number])
    else:
        await update.message.reply_text("❌ الرقم غير موجود في جدول الأسعار")


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
