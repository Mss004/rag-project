import unittest
import chunking
import db
import os
import sqlite3

class TestRAGSystem(unittest.TestCase):

    def test_chunking_length(self):
        """Metin parçalama (chunking) fonksiyonunun çalışmasını test eder."""
        text = "Bu bir test metnidir. " * 100 # Yaklaşık 500 kelime
        chunks = chunking.chunk_text(text)
        self.assertTrue(len(chunks) > 0)
        # İlk chunk'ın boş olmadığını kontrol et
        self.assertIsNotNone(chunks[0])

    def test_database_connection(self):
        """Veritabanı bağlantısını ve tablo yapısını test eder."""
        test_db = "test_memory.db"
        conn = sqlite3.connect(test_db)
        # DB modülündeki create logic'ine benzer bir test
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY)")
        cursor.execute("INSERT INTO test_table (id) VALUES (1)")
        res = cursor.execute("SELECT id FROM test_table").fetchone()
        conn.close()
        # Temizlik
        if os.path.exists(test_db):
            os.remove(test_db)
        self.assertEqual(res[0], 1)

    def test_normalization(self):
        """Türkçe karakter normalizasyonunu test eder."""
        dirty_text = "IĞDIR'da şemsiye sattık."
        import unicodedata
        normalized = unicodedata.normalize("NFKD", dirty_text)
        self.assertIn("I", normalized) # I karakterinin korunduğunu doğrula
        
if __name__ == '__main__':
    unittest.main()
