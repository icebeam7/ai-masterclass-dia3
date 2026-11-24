"""Fuente de ingesta: blobs Markdown/UTF-8 existentes en Azure Storage."""
from rag_clase2.app.documents import Chunk, chunk_text


def parse_blob_text(raw: bytes, blob_name: str) -> str:
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError(f'Blob no está codificado en UTF-8: {blob_name}') from exc
    if not text.strip():
        raise ValueError(f'Blob vacío: {blob_name}')
    return text


def list_source_names(container, prefix: str = '') -> list[str]:
    """Lista únicamente Markdown; respeta subcarpetas y prefijo de nombres."""
    names = [blob.name for blob in container.list_blobs(name_starts_with=prefix)
             if blob.name.lower().endswith('.md')]
    return sorted(names)


def load_blob_chunks(settings, max_chars: int = 1000, overlap: int = 120) -> list[Chunk]:
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobServiceClient
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
    client = BlobServiceClient(account_url=settings.storage_account_url, credential=credential)
    container = client.get_container_client(settings.storage_container)
    names = list_source_names(container, settings.storage_prefix)
    if not names:
        raise ValueError(f'No hay archivos .md en el contenedor {settings.storage_container} '
                         f'con prefijo {settings.storage_prefix!r}. Sube archivos con scripts.upload_samples.')
    chunks = []
    for name in names:
        blob = container.get_blob_client(name)
        data = blob.download_blob().readall()
        content = parse_blob_text(data, name)
        source = f'blob://{settings.storage_container}/{name}'
        doc_chunks = chunk_text(content, source, max_chars=max_chars, overlap=overlap)
        chunks.extend(doc_chunks)
        print(f'  Blob: {name} -> {len(doc_chunks)} fragmentos')
    return chunks
