import json
import os
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# ---------- Config ----------
STORAGE_FILE = "articles.json"
TARGET_URL = "https://www.nasa.gov/news/recently-published/"
DELAY_SECONDS = 1

# ---------- Charger les anciens articles ----------
if os.path.exists(STORAGE_FILE):
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        stored_articles = json.load(f)
else:
    stored_articles = []

stored_urls = [a["url"] for a in stored_articles]

# ---------- Setup Selenium ----------
options = Options()
options.add_experimental_option("detach", False)
driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
driver.get(TARGET_URL)
time.sleep(DELAY_SECONDS)

# ---------- Scraper les liens ----------
article_links = driver.find_elements(By.CSS_SELECTOR, 'a.hds-content-item-heading')
urls = [link.get_attribute("href") for link in article_links if link.get_attribute("href")]

# ---------- Scraper les nouveaux articles (dans l'ordre inverse) ----------
new_articles = []

for url in reversed(urls):  # Du plus ancien au plus récent
    if url in stored_urls:
        continue  # Déjà connu

    driver.get(url)
    time.sleep(DELAY_SECONDS)

    try:
        title = driver.find_element(By.CSS_SELECTOR, 'h1.display-48.margin-bottom-2').text
    except:
        title = "Titre non trouvé"

    try:
        content_div = driver.find_element(By.CLASS_NAME, "entry-content")
        paragraphs = content_div.find_elements(By.TAG_NAME, "p")
        content = "\n".join([p.text for p in paragraphs if p.text.strip()])
    except:
        content = "Contenu non trouvé"
    new_articles.append({
        "title": title,
        "url": url,
        "date_inserted": datetime.now().isoformat(),
        "content": content
    })

# ---------- Ajouter les nouveaux articles à la liste ----------
if new_articles:
    # Charger les anciens articles
    if os.path.exists(STORAGE_FILE) and os.path.getsize(STORAGE_FILE) > 0:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            try:
                stored_articles = json.load(f)
            except json.JSONDecodeError:
                print(" Fichier JSON corrompu ou vide")
    else:
        stored_articles = []

    # Ajouter les nouveaux articles
    stored_articles.extend(new_articles[::-1])

    # Enregistrer dans le fichier
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(stored_articles, f, ensure_ascii=False, indent=2)

    print(f"{len(new_articles)} nouveaux articles ajoutés.")
else:
    print("Aucun nouvel article à ajouter.")

driver.quit()