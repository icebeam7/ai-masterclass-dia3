"""Sube documentos ficticios del repositorio a Azure Blob Storage (paso previo a ingest)."""
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings
from rag_clase2.app.config import Settings


def main():
    cfg = Settings.from_env()
    folder = Path(__file__).resolve().parents[1] / 'data' / 'documents'
    files = sorted(folder.glob('*.md'))
    if not files:
        raise ValueError('No existen documentos Markdown de ejemplo en data/documents')
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
    client = BlobServiceClient(account_url=cfg.storage_account_url, credential=credential)
    container = client.get_container_client(cfg.storage_container)
    # El contenedor se crea desde Bicep o Azure Portal; el script no requiere rol sobre el plano de administración.
    if not container.exists():
        raise ValueError(f'El contenedor {cfg.storage_container!r} no existe. Despliega infra/storage.bicep primero.')
    for file in files:
        name = f'{cfg.storage_prefix}{file.name}'
        container.upload_blob(name=name, data=file.read_bytes(), overwrite=True,
                              content_settings=ContentSettings(content_type='text/markdown; charset=utf-8'))
        print(f'Cargado: {cfg.storage_container}/{name}')
    print(f'Total: {len(files)} documentos. Ejecuta python -m scripts.ingest.')


if __name__ == '__main__':
    main()
