import google.generativeai as genai
import json

def configurar_gemini(api_key):
    genai.configure(api_key=api_key)

def procesar_busqueda_ia(consulta_natural):
    """
    Toma una consulta en lenguaje natural y devuelve términos de búsqueda óptimos
    para la API del SJF usando Gemini.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Eres un experto abogado postulante en México y especialista en búsqueda de jurisprudencia en el Semanario Judicial de la Federación (SCJN).
    El usuario va a ingresar una duda legal en lenguaje natural. Tu objetivo es extraer los conceptos clave de esa búsqueda
    y transformarlos en una ORACIÓN DE BÚSQUEDA BOOLEANA OPTIMIZADA que el buscador de la corte entienda perfectamente.
    
    Reglas para la búsqueda:
    1. Usa comillas dobles para frases exactas (ej. "pensión alimenticia", "despido injustificado").
    2. Usa operadores como AND, OR, o simplemente espacios (que actúan como AND implícito en muchos sistemas) para unir conceptos.
    3. Elimina palabras vacías, verbos irrelevantes o frases como "Busca jurisprudencias de...".
    4. Si hay restricciones geográficas (ej. "en Oaxaca", "del Estado de México"), inclúyelas como términos clave.
    
    Consulta original del usuario: "{consulta_natural}"
    
    Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
    {{
        "terminos_optimizados": "el string final de búsqueda (ej. \\"pensión alimenticia\\" Oaxaca)",
        "explicacion": "Una breve explicación de 1 línea dirigida al abogado sobre por qué elegiste esos términos."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Parse the JSON response. Strip markdown code blocks if present.
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        
        resultado = json.loads(text.strip())
        return resultado
    except Exception as e:
        print(f"Error en IA: {e}")
        return None
