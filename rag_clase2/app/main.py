"""Laboratorio Clase 2: comparación sin RAG, RAG keyword y RAG híbrido."""
import streamlit as st
from rag_clase2.app.config import Settings
from rag_clase2.app.foundry import FoundryService
from rag_clase2.app.search import KnowledgeSearch

st.set_page_config(page_title='AI Enterprise | Laboratorio RAG',page_icon='📚',layout='wide')
st.title('📚 AI Fundamentals for Enterprise · Clase 2')
st.caption('Laboratorio real: Microsoft Foundry + Azure AI Search · Documentos 100 % ficticios')

@st.cache_resource(show_spinner=False)
def clients():
    config=Settings.from_env()
    return config,FoundryService(config),KnowledgeSearch(config)

try:
    config,model,search=clients()
except Exception as exc:
    st.error('Configuración o inicialización incorrecta. Consulta README.md y docs/ERRORES.md.')
    st.code(str(exc))
    st.stop()

with st.sidebar:
    st.header('Panel del laboratorio')
    st.success('Configuración local cargada; la conexión real se verifica al consultar.')
    st.write('Índice:',config.search_index)
    st.write('Modelo:',config.chat_model)
    st.write('Embeddings:',config.embedding_model)
    mode=st.radio('Modo de recuperación',['hybrid','keyword'],index=0,
                  format_func=lambda x:'Híbrido (texto + vectores)' if x=='hybrid' else 'Palabras clave')
    show_chunks=st.checkbox('Mostrar evidencia recuperada',value=True)
    st.info('Los documentos son un caso ficticio. El modo sin RAG ilustra una comparación: no obtiene datos del índice.')

examples=[
    '¿Cuándo se debe escalar un incidente crítico y a quién se notifica?',
    '¿Cuántos días se conservan los registros de acceso?',
    '¿Qué se hace ante una solicitud de reembolso y cuál es el plazo?',
    '¿Cuál es el salario del director financiero?',
]
question=st.selectbox('Selecciona una pregunta de ejemplo',examples+['Escribir mi propia pregunta'])
if question=='Escribir mi propia pregunta':
    question=st.text_input('Pregunta empresarial','')

col1,col2,col3=st.columns(3)
with col1: no_rag=st.button('1 · Preguntar sin RAG',use_container_width=True)
with col2: retrieve=st.button('2 · Recuperar evidencia',use_container_width=True)
with col3: rag=st.button('3 · Responder con RAG',type='primary',use_container_width=True)

if 'history' not in st.session_state: st.session_state.history=[]
if not question.strip() and (no_rag or retrieve or rag):
    st.warning('Escribe una pregunta antes de ejecutar.')
elif no_rag or retrieve or rag:
    try:
        snippets=[]
        if retrieve or rag:
            with st.spinner('Consultando Azure AI Search...'):
                vector=model.embed([question])[0] if mode=='hybrid' else None
                snippets=search.retrieve(question,vector,mode,config.top_k)
            st.session_state.last_evidence=snippets
        if no_rag or rag:
            with st.spinner('Generando respuesta en Microsoft Foundry...'):
                response=model.answer(question,snippets,grounded=rag)
            st.session_state.history.insert(0,{'question':question,'mode':'RAG '+mode if rag else 'Sin RAG',
                                               'response':response,'evidence':snippets})
            st.session_state.history=st.session_state.history[:15]
            st.success('Respuesta obtenida del modelo real')
            st.markdown(response['answer'])
            st.caption(f"Tokens entrada: {response['input_tokens']}; salida: {response['output_tokens']}")
        if retrieve: st.success(f'{len(snippets)} fragmentos recuperados')
    except Exception as exc:
        st.error('Error durante la llamada a Azure. Revisa configuración, roles, deployments e índice.')
        st.code(str(exc))

if show_chunks and st.session_state.get('last_evidence'):
    st.subheader('🔎 Evidencia recuperada')
    for i,chunk in enumerate(st.session_state.last_evidence,1):
        with st.expander(f"[F{i}] {chunk['source']} · relevancia {chunk['score']}"):
            st.write(chunk['content'])

if st.session_state.history:
    st.subheader('🧪 Historial de ejecuciones (sesión local)')
    for item in st.session_state.history:
        with st.expander(f"{item['mode']} · {item['question'][:85]}"):
            st.write(item['response']['answer'])
            st.caption(f"Fragmentos enviados: {len(item['evidence'])}")
    import json
    st.download_button('Exportar historial JSON',data=json.dumps(st.session_state.history,ensure_ascii=False,indent=2),
                       file_name='resultados_clase2.json',mime='application/json')

st.divider()
st.caption('Advertencia educativa: las citas [F#] son referencias al contexto enviado al modelo, no una garantía de veracidad. Verifica la información original.')
