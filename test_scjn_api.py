import unittest
from scjn_api import SJFAPI

class TestSJFAPI(unittest.TestCase):
    def setUp(self):
        self.api = SJFAPI()

    def test_buscar_amparo(self):
        resultados = self.api.buscar_tesis("amparo directo", page=0, size=1)
        
        self.assertIsNotNone(resultados, "La respuesta no debe ser None")
        self.assertIn('documents', resultados, "La respuesta debe contener la llave 'documents'")
        self.assertGreater(len(resultados['documents']), 0, "Debería haber al menos un resultado para esta búsqueda tan común")
        
        primer_resultado = resultados['documents'][0]
        self.assertIn('ius', primer_resultado, "Debe incluir el ius (registro digital)")

if __name__ == '__main__':
    unittest.main()
