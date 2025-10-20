import time, random, re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
# from gsearch.googlesearch import search      # Uso gsearch sin límite
from googlesearch import search               # O googlesearch-python (requiere pip install googlesearch-python)

# Ejemplo: función que transforma un prompt en consultas (usando un LLM hipotético)
def generar_consultas_desde_prompt(prompt):
    # Aquí usaríamos la API de OpenAI para generar queries adecuadas.
    # Por simplicidad devolvemos una lista fija. En producción, reemplazar con openai.Completion.
    return [prompt + " site:.es", prompt + " site:.com"]

# Función para buscar dominios con gsearch/googlesearch
def buscar_dominios(consultas, num_resultados):
    dominios = set()
    for q in consultas:
        print(f"Buscando: {q}")
        for url in search(q, num_results=num_resultados, lang="es", sleep_interval=2):
            if not url: 
                continue
            domain = urlparse(url).netloc
            # Opcional: normalizar dominio (sin subdominio)
            parts = domain.split('.')
            top = parts[-2] + "." + parts[-1] if len(parts) >= 2 else domain
            dominios.add(top)
        time.sleep(random.uniform(2, 5))  # delay aleatorio entre consultas
    return list(dominios)

# Función para extraer correos de una web dado su dominio
def extraer_correos_de_dominio(domain, max_emails):
    correos = set()
    url = f"http://{domain}"
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        r = requests.get(url, headers=headers, timeout=5)
        text = r.text
        # Buscar correos con regex
        correos_encontrados = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,4}", text)
        for email in correos_encontrados:
            correos.add(email.lower())
            if len(correos) >= max_emails:
                break
        # También buscar links mailto
        soup = BeautifulSoup(text, "html.parser")
        for a in soup.find_all("a", href=True):
            if a["href"].startswith("mailto:"):
                correos.add(a["href"].split("mailto:")[1].split("?")[0].lower())
                if len(correos) >= max_emails:
                    break
    except Exception as e:
        print(f"Error al acceder {domain}: {e}")
    return list(correos)[:max_emails]

# Lista de User-Agents para rotar
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    # Agregar más si se desea
]

if __name__ == "__main__":
    prompt = input("Describe la búsqueda: ")
    consultas = generar_consultas_desde_prompt(prompt)
    num_emails = int(input("¿Cuántos correos quieres obtener?: "))
    # Buscar dominios
    dominios = buscar_dominios(consultas, num_resultados=50)
    print(f"Dominios encontrados ({len(dominios)}): {dominios}")
    # Extraer correos
    todos_correos = []
    for dom in dominios:
        if len(todos_correos) >= num_emails:
            break
        mails = extraer_correos_de_dominio(dom, num_emails - len(todos_correos))
        todos_correos.extend(mails)
    print(f"Correos extraídos ({len(todos_correos)}):")
    for email in todos_correos:
        print(email)
