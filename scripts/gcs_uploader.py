from google.cloud import storage
from pathlib import Path
from datetime import date

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent


class GCSUploader:
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def subir_archivo(self, ruta_local: Path, ruta_remota: str) -> None:
        blob = self.bucket.blob(ruta_remota)
        blob.upload_from_filename(str(ruta_local))
        print(f"Subido: {ruta_local.name} -> gs://{self.bucket.name}/{ruta_remota}")

    def subir_carpeta_particionada(self, carpeta_local: Path, prefijo_base: str, fecha_ingesta: str = None) -> None:
        fecha_ingesta = fecha_ingesta or date.today().isoformat()
        for archivo in sorted(carpeta_local.glob("*")):
            if archivo.is_file():
                ruta_remota = f"{prefijo_base}/fecha_ingesta={fecha_ingesta}/{archivo.name}"
                self.subir_archivo(archivo, ruta_remota)


if __name__ == "__main__":
    uploader = GCSUploader(bucket_name="clima-el-nino-devops-datalake")
    uploader.subir_carpeta_particionada(RAIZ_PROYECTO / "data" / "raw", "bronze/raw")
    uploader.subir_carpeta_particionada(RAIZ_PROYECTO / "data" / "processed", "bronze/silver")
    print("\nSubida particionada completa.")