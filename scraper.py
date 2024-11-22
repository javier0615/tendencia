import requests
from bs4 import BeautifulSoup
import json

def scrape_books_from_page(page):
    url = f"http://books.toscrape.com/catalogue/page-{page}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    books = []
    for book_item in soup.find_all('article', class_='product_pod'):
        title = book_item.h3.a['title']
        image_url = "http://books.toscrape.com/" + book_item.find('img')['src']
        price = book_item.find('p', class_='price_color').text.strip()
        availability = book_item.find('p', class_='instock availability').text.strip()
        
        # Calificación (rating)
        rating_class = book_item.find('p')['class']
        rating = rating_class[1] if len(rating_class) > 1 else 'No rating'
        
        books.append({
            'title': title,
            'image_url': image_url,
            'price': price,
            'availability': availability,
            'rating': rating
        })
    
    return books

def save_books_to_file(books, filename='libros.txt'):
    with open(filename, 'w') as file:
        json.dump(books, file, indent=4)
