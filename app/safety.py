"""Azure AI Content Safety / Prompt Shields. Opcional, REQUIERE recurso real."""
import os
import requests

class SafetyViolation(ValueError): pass

def safety_configured():
    return bool(os.getenv('CONTENT_SAFETY_ENDPOINT') and os.getenv('CONTENT_SAFETY_KEY'))

def check_prompt_and_documents(prompt: str, documents: list[str] | None=None):
    """Detecta ataques contra el prompt y documentos. Fail-closed si está activado."""
    if not safety_configured():
        return {'enabled':False,'blocked':False,'reason':'No configurado: no se ha realizado análisis de Prompt Shields'}
    url=os.environ['CONTENT_SAFETY_ENDPOINT'].rstrip('/')+'/contentsafety/text:shieldPrompt?api-version=2024-09-01'
    response=requests.post(url,json={'userPrompt':prompt,'documents':(documents or [])[:10]},
                           headers={'Ocp-Apim-Subscription-Key':os.environ['CONTENT_SAFETY_KEY']},timeout=20)
    response.raise_for_status()
    body=response.json()
    detected=bool(body.get('userPromptAnalysis',{}).get('attackDetected',False)) or any(
        x.get('attackDetected',False) for x in body.get('documentsAnalysis',[]))
    print(f"Prompt Shields analysis result: {detected}")
    if detected: 
        print(f"Prompt Shields detected attack: {body}")
        raise SafetyViolation('Prompt Shields detectó posible inyección; operación bloqueada')
    return {'enabled':True,'blocked':False,'reason':'Sin ataques detectados por Prompt Shields'}

def check_harmful_content(text: str):
    """Moderación de las categorías Hate, SelfHarm, Sexual y Violence."""
    if not safety_configured(): return {'enabled':False,'reason':'Content Safety no configurado'}
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.ai.contentsafety.models import AnalyzeTextOptions
    from azure.core.credentials import AzureKeyCredential
    client=ContentSafetyClient(os.environ['CONTENT_SAFETY_ENDPOINT'],AzureKeyCredential(os.environ['CONTENT_SAFETY_KEY']))
    result=client.analyze_text(AnalyzeTextOptions(text=text[:9000]))
    severities={str(c.category):c.severity for c in result.categories_analysis}
    limit=int(os.getenv('CONTENT_SAFETY_THRESHOLD','4'))
    if any(value is not None and value>=limit for value in severities.values()):
        print(f"Content Safety detected severities above threshold: {severities}")
        raise SafetyViolation('Content Safety detectó una categoría por encima del umbral')
    return {'enabled':True,'severities':severities,'threshold':limit}
