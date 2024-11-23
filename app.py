import yaml
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from bs4 import BeautifulSoup  # Asegúrate de que BeautifulSoup esté instalado.
import os

app = Flask(__name__)

# --- Configuración de la API ---
archivo_configuracion = 'config/auth.yaml'
with open(archivo_configuracion, 'r') as archivo:
    configuracion = yaml.safe_load(archivo)

clave_api = configuracion['moviedb']['api_key']
token_acceso = configuracion['moviedb']['access_token']

# --- Funciones de scraping para libros ---
def scrape_books_from_page(page):
    url = f"http://books.toscrape.com/catalogue/page-{page}.html"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
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

def save_books_to_file(books):
    with open('libros.json', 'w') as file:
        json.dump(books, file, indent=4)

# --- Funciones para obtener películas ---
def obtener_peliculas_tendencia(pagina):
    url = f'https://api.themoviedb.org/3/trending/movie/week?api_key={clave_api}&language=es-CO&page={pagina}'
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'Bearer {token_acceso}'
    }
    
    respuesta = requests.get(url, headers=headers)
    
    if respuesta.status_code == 200:
        datos_peliculas = respuesta.json()
        with open('peliculas.json', 'w') as json_file:
            json.dump(datos_peliculas, json_file, indent=4)
        return datos_peliculas
    else:
        return None

# --- Rutas de la aplicación ---
@app.route('/', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        opcion = request.form.get('opcion')
        if opcion == 'peliculas':
            pagina = request.form.get('pagina', 1)
            return redirect(url_for('obtener_peliculas', pagina=pagina))
        elif opcion == 'libros':
            pagina = request.form.get('pagina', 1)
            return redirect(url_for('scrape', page=pagina))
    return render_template('inicio.html')

@app.route('/peliculas/<pagina>', methods=['GET'])
def obtener_peliculas(pagina):
    datos_peliculas = obtener_peliculas_tendencia(pagina)
    if datos_peliculas:
        return redirect(url_for('mostrar_peliculas'))
    return "Error al obtener películas."

@app.route('/peliculas')
def mostrar_peliculas():
    try:
        with open('peliculas.json', 'r') as json_file:
            peliculas = json.load(json_file)
        return render_template('peliculas.html', peliculas=peliculas['results'])
    except FileNotFoundError:
        return "No se encontraron datos de películas."

@app.route('/scrape/<int:page>', methods=['GET'])
def scrape(page):
    books = scrape_books_from_page(page)
    save_books_to_file(books)
    return render_template('libros.html', books=books, page=page)

@app.route('/libros')
def mostrar_libros():
    try:
        with open('libros.json', 'r') as file:
            books = json.load(file)
    except FileNotFoundError:
        books = []
    return render_template('libros.html', books=books)

if __name__ == '__main__':
    app.run(debug=True)
