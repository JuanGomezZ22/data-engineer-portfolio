from google.cloud import secretmanager


class SecretManagerClient:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = secretmanager.SecretManagerServiceClient()

    def obtener_secreto(self, secret_id: str, version: str = "latest") -> str:
        nombre = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
        respuesta = self.client.access_secret_version(request={"name": nombre})
        return respuesta.payload.data.decode("UTF-8")


if __name__ == "__main__":
    cliente = SecretManagerClient(project_id="clima-el-nino-devops")
    password = cliente.obtener_secreto("postgres-db-password")
    print(f"Password obtenida (longitud: {len(password)} caracteres, no la imprimimos completa por seguridad)")