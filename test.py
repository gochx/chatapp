from google.cloud import storage

def read_file_from_bucket(bucket_name, file_name):
    """
    Liest den Inhalt einer Datei aus einem Google Cloud Storage Bucket und gibt ihn aus.
    
    :param bucket_name: Name des Buckets
    :param file_name: Name der Datei im Bucket
    """
    try:
        # Google Cloud Storage Client initialisieren
        client = storage.Client()
        
        # Bucket abrufen
        bucket = client.get_bucket(bucket_name)
        
        # Datei (Blob) abrufen
        blob = bucket.blob(file_name)
        
        # Inhalt der Datei lesen
        content = blob.download_as_text()
        
        print(f"Inhalt der Datei '{file_name}' aus dem Bucket '{bucket_name}':")
        print(content)
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")

# Beispielaufruf
bucket_name = "rac_bucket"
file_name = "Blaustern-Kohlenstoff-Formel.txt"


read_file_from_bucket(bucket_name, file_name)
