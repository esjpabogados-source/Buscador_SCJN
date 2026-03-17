import requests
import json

class SJFAPI:
    def __init__(self):
        self.base_url = "https://sjf2.scjn.gob.mx/services/sjftesismicroservice/api/public"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0"
        }

    def buscar_tesis(self, termino, page=0, size=20):
        url = f"{self.base_url}/tesis?page={page}&size={size}"
        
        payload = {
            "classifiers": [
                {
                    "name": "tipoDocumento",
                    "value": ["1"], # 1 usually means Jurisprudencia/Tesis
                     "allSelected": False, "visible": False, "isMatrix": False
                }
            ],
            "searchTerms": [
                {
                    "expression": termino,
                    "fields": ["localizacionBusqueda", "rubro", "texto"],
                    "fieldsUser": "Localización: \\nRubro: \\nTexto: \\n",
                    "fieldsText": "Localización, Rubro, Texto",
                    "operator": 0,
                    "operatorUser": "Y",
                    "operatorText": "Y",
                    "lsFields": [],
                    "esInicial": True,
                    "esNRD": False
                }
            ],
            "bFacet": True,
            "ius": [],
            "idApp": "SJFAPP2020",
            "lbSearch": [],
            "filterExpression": ""
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con la API de la SCJN: {e}")
            return None

if __name__ == "__main__":
    api = SJFAPI()
    print("Testing search for: amparo directo")
    resultados = api.buscar_tesis("amparo directo", page=0, size=1)
    if resultados and "documents" in resultados:
        print(f"Se encontraron {resultados.get('total', 0)} resultados!")
        for item in resultados['documents']:
            print(f" - [{item.get('ius')}] {item.get('rubro')[:150]}...")
    else:
        print("No se obtuvieron resultados o hubo un error:")
        print(resultados)
