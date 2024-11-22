import yaml
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from scraper import scrape_books_from_page, save_books_to_file

app = Flask(__name__)

# Cargar la configuración de la API desde auth.yaml
archivo_configuracion = 'config/auth.yaml'
with open(archivo_configuracion, 'r') as archivo:
    configuracion = yaml.safe_load(archivo)

clave_api = configuracion['moviedb']['api_key']
token_acceso = configuracion['moviedb']['access_token']

# Función para obtener las películas y guardar en un archivo JSON
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

# Ruta principal con formulario para elegir entre libros o películas
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

# Ruta para obtener películas
@app.route('/peliculas/<pagina>', methods=['GET'])
def obtener_peliculas(pagina):
    datos_peliculas = obtener_peliculas_tendencia(pagina)
    if datos_peliculas:
        return redirect(url_for('mostrar_peliculas'))
    return "Error al obtener películas."

# Ruta para mostrar películas
@app.route('/peliculas')
def mostrar_peliculas():
    try:
        with open('peliculas.json', 'r') as json_file:
            peliculas = json.load(json_file)
        return render_template('peliculas.html', peliculas=peliculas['results'])
    except FileNotFoundError:
        return "No se encontraron datos de películas."

# Ruta para scrapear libros
@app.route('/scrape/<int:page>', methods=['GET'])
def scrape(page):
    books = scrape_books_from_page(page)
    save_books_to_file(books)
    return render_template('libros.html', books=books, page=page)

# Ruta para mostrar libros
@app.route('/libros')
def mostrar_libros():
    try:
        with open('libros.txt', 'r') as file:
            books = json.load(file)
    except FileNotFoundError:
        books = []
    return render_template('libros.html', books=books)

if __name__ == '__main__':
    app.run(debug=True)
