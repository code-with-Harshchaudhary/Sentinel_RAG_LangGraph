"""Build a privacy-safe portfolio report from documented project observations.

Design: standard_business_brief + editorial_cover. Named overrides: cover title
32 pt navy; teal kicker; 9.5 pt comparison tables; 8.5 pt monospace code; compact
9 pt references. No project state, credentials, or private documents are read.
"""
from pathlib import Path
import json
import re
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'portfolio-report'
OUT = ROOT / 'output' / 'docx'
PDFOUT = ROOT / 'output' / 'pdf'
QA = WORK / 'qa'
for path in (WORK, OUT, PDFOUT, QA):
    path.mkdir(parents=True, exist_ok=True)
NAVY = '0B2545'
BLUE = '2E74B5'
TEAL = '0A6B70'
MUTED = '596779'
FONTDIR = Path('C:/Windows/Fonts')


def figure_font(size, bold=False):
    return ImageFont.truetype(str(FONTDIR / ('calibrib.ttf' if bold else 'calibri.ttf')), size)


def architecture_image():
    im = Image.new('RGB', (1560, 590), '#FFFFFF')
    d = ImageDraw.Draw(im)
    boxes = [
        (15, 90, 475, 260, 'DOCUMENT OPERATIONS', ['React + TypeScript console', 'Upload / pipeline / graph / retrieval']),
        (550, 90, 1010, 260, 'API + ORCHESTRATION', ['FastAPI + LightRAG engine', 'Parse / extract / index / query']),
        (1085, 90, 1545, 260, 'MODEL SERVICES', ['Gemini Flash-Lite', 'Gemini Embedding 001']),
        (550, 365, 1010, 545, 'LOCAL PERSISTENCE', ['NetworkX + NanoVectorDB', 'JSON state, chunks and provenance']),
    ]
    for x1, y1, x2, y2, title, lines in boxes:
        d.rounded_rectangle((x1,y1,x2,y2),radius=18,fill='#F2F6FA',outline='#B9C9D7',width=3)
        d.text((x1+22,y1+22),title,font=figure_font(29,True),fill='#'+NAVY)
        for n,line in enumerate(lines):
            d.text((x1+22,y1+80+n*34),line,font=figure_font(27),fill='#34475C')
    def arrow(x1,y1,x2,y2):
        d.line((x1,y1,x2,y2),fill='#'+TEAL,width=5)
        if x2>x1:
            d.polygon([(x2,y2),(x2-15,y2-9),(x2-15,y2+9)],fill='#'+TEAL)
        else:
            d.polygon([(x2,y2),(x2-9,y2-15),(x2+9,y2-15)],fill='#'+TEAL)
    arrow(475,175,542,175)
    arrow(1010,175,1077,175)
    arrow(780,260,780,356)
    d.text((35,20),'LOCAL BROWSER',font=figure_font(25,True),fill='#'+MUTED)
    d.text((575,20),'LOCAL BACKEND',font=figure_font(25,True),fill='#'+MUTED)
    d.text((1110,20),'GOOGLE CLOUD API',font=figure_font(25,True),fill='#'+MUTED)
    d.text((25,435),'Files stay local; extracted content\ncan be sent to the configured provider.',font=figure_font(25),fill='#'+MUTED)
    im.save(WORK/'architecture.png')


def graph_image():
    im = Image.new('RGB',(1560,500),'white')
    d=ImageDraw.Draw(im)
    nodes={'Document assistant':(235,245),'FastAPI':(820,90),'Docker':(820,245),'Knowledge graph':(820,400),'Python':(1320,90)}
    for target,label in [('FastAPI','exposes API via'),('Docker','packaged with'),('Knowledge graph','retrieves from')]:
        a=nodes['Document assistant']; b=nodes[target]
        d.line((a[0]+160,a[1],b[0]-158,b[1]),fill='#8BA9B9',width=4)
        mid=((a[0]+b[0])//2,(a[1]+b[1])//2)
        label_offset = -70 if target == 'FastAPI' else (70 if target == 'Knowledge graph' else -28)
        d.text((mid[0],mid[1]+label_offset),label,font=figure_font(24),fill='#'+TEAL,anchor='mm')
    d.line((978,90,1162,90),fill='#8BA9B9',width=4)
    d.text((1070,60),'implemented in',font=figure_font(24),fill='#'+TEAL,anchor='mm')
    for name,(x,y) in nodes.items():
        fill='#'+NAVY if name=='Document assistant' else '#EAF2F7'
        d.rounded_rectangle((x-160,y-46,x+160,y+46),radius=24,fill=fill,outline='#B9C9D7',width=2)
        d.text((x,y),name,font=figure_font(29,True),fill='white' if name=='Document assistant' else '#'+NAVY,anchor='mm')
    im.save(WORK/'graph_example.png')


# Content is an explanatory engineering report, not invented benchmark results.
PAGES = [
    ('Project overview', [
        ('h2','The problem: documents contain facts, but not a usable knowledge interface'),
        ('p','A document folder is easy to create and difficult to interrogate. Information may be distributed across paragraphs, tables and multiple files. A user often knows the question they want to ask but not the exact phrase or document location that contains the answer. Plain keyword search can miss paraphrases, while a general-purpose language model may answer without seeing the relevant private source.'),
        ('p','Sentinel RAG Ops brings these steps into one local application: ingest a document, inspect processing status, create searchable representations, explore extracted relationships and retrieve evidence for a question. The intended experience is operational rather than conversational alone: users should be able to see whether a document was accepted, whether it finished processing, and whether its information reached the index.'),
        ('h2','What RAG means in this project'),
        ('p','Retrieval-augmented generation supplies a language model with information selected from an external collection. It separates the stored document collection from the model parameters; adding a file changes the searchable knowledge base rather than training a new model. The original RAG literature formalized the combination of retrieval and generation [1]. This project uses a graph-and-vector implementation derived from LightRAG [2].'),
        ('h2','Scope and contribution'),
        ('p','The case study covers product customization, local configuration, provider integration, document ingestion, graph inspection and functional verification. The existing LightRAG engine supplies the core extraction, graph construction and retrieval mechanisms. Sentinel RAG Ops presents a customized interface and operational setup around that foundation. The contribution described here is engineering integration and diagnosis, not a newly invented RAG algorithm.'),
        ('p','The demonstrated deployment is a local prototype with cloud model calls. It is not an offline-only system, a public production deployment, or a completed comparison of retrieval methods. This distinction keeps the portfolio claim proportional to the available evidence.'),
        ('callout','Practical outcome: a document can move from upload to indexed knowledge, while its processing status and extracted relationships remain inspectable.'),
    ]),
    ('System architecture', [
        ('p','The application has four main boundaries: the browser interface, the Python API, external model services and local storage. Keeping these responsibilities separate makes it easier to diagnose whether a failure belongs to the file parser, model provider, indexing stage or visualization.'),
        ('figure',('architecture.png','Figure 1. Logical architecture of the demonstrated configuration. Arrows indicate interaction, not an exhaustive network trace.')),
        ('table',(['Layer','Technology','Responsibility'],[
            ['Web console','React, TypeScript, Vite','Document status, graph exploration and retrieval controls'],
            ['HTTP API','FastAPI','Accept uploads, expose status and serve query endpoints'],
            ['RAG engine','LightRAG Python package','Coordinate parsing, extraction, graph and vector retrieval'],
            ['Model services','Google Gemini API','Generate text and compute embeddings'],
            ['Graph / vectors','NetworkX / NanoVectorDB','Persist entity relationships and similarity indexes'],
            ['Operational state','JSON-backed storage','Track documents, chunks, cache and provenance'],
        ],[1850,2450,5060])),
        ('h2','Why the separation matters'),
        ('p','A healthy API only proves that the server is reachable. It does not prove that credentials work, that every model is available, or that a document has been indexed. Likewise, a rendered graph is evidence of stored nodes and edges, not proof that every relationship is accurate. Each boundary therefore needs its own check.'),
        ('p','The source retains the lightrag Python namespace and established configuration prefixes for compatibility. Branding changes do not require rewriting the functioning engine. The repository retains the upstream license and third-party notice [2, 6].'),
    ]),
    ('From upload to searchable knowledge', [
        ('p','Uploading is the start of a pipeline, not its final success condition. The server can accept a file before a downstream provider request fails. Users should therefore look for a completed processing status rather than treating an HTTP upload response as proof of a usable index.'),
        ('step',('Accept and track','The API records the document and schedules processing. A document identifier and status make the background work visible to the interface.')),
        ('step',('Parse','The selected parser extracts usable content. The documented test used native DOCX parsing. Other extensions are exposed by the active parser configuration, but were not all tested for this report.')),
        ('step',('Chunk and extract','Content is divided into retrieval units. The extraction model identifies entities and relationships associated with source chunks. Tables and parsing options can affect the resulting chunk structure.')),
        ('step',('Persist and index','The pipeline writes graph data, vector representations and source mappings. Embedding calls turn content into numerical representations for similarity search [3].')),
        ('step',('Complete or record an error','A successful run is marked processed. A failure records a cause and can be retried through the supported pipeline action rather than by manually editing storage files.')),
        ('h2','Model roles in the demonstrated configuration'),
        ('table',(['Role','Configuration'],[
            ['Extraction, keywords and answers','gemini-3.1-flash-lite'],
            ['Text embeddings','gemini-embedding-001; 1,536 dimensions'],
            ['Vision-language processing','Disabled in the documented test'],
            ['Separate reranking model','Not configured'],
        ],[3700,5660])),
        ('p','These are configured roles, not four independently trained models. The same generation model can serve several roles. Credentials grant access to the provider API; they do not give Google direct access to arbitrary local files. The application chooses which extracted content to send.'),
    ]),
    ('Why the knowledge graph is useful', [
        ('p','Vector retrieval finds semantically similar content. A knowledge graph adds an explicit representation of entities and the relationships extracted between them. This can help organize questions involving several connected facts, although the benefit must be measured rather than assumed.'),
        ('figure',('graph_example.png','Figure 2. Illustrative entity relationships, not an export of the private test document.')),
        ('p','In this example, a question about how an assistant is implemented can connect the application, its framework and its language. The graph is a map of extracted knowledge; the original source chunks remain necessary for checking evidence. An incorrect extraction can still produce a plausible-looking node or edge.'),
        ('table',(['Mode','Evidence selection','Useful starting point'],[
            ['naive','Direct chunk-vector retrieval','Specific facts and source passages'],
            ['local','Entity-focused graph context','Questions about a named entity'],
            ['global','High-level relationship context','Broad themes and connections'],
            ['hybrid','Local and global graph context','Entity detail plus wider relationships'],
            ['mix','Graph context plus vector retrieval','Questions needing both evidence types'],
        ],[1250,4230,3880])),
        ('p','Hybrid and Mix are not synonyms: Hybrid combines local and global graph retrieval, while Mix integrates graph and vector retrieval. These descriptions explain the available mechanisms; no winning mode is established by the single-document functional test.'),
        ('callout','The Knowledge Graph screen is an inspection tool. The Retrieval screen uses indexed evidence to support a response. Neither screen replaces source verification.'),
    ]),
    ('Engineering case study: diagnosing failures', [
        ('p','The development session exposed several failures that initially looked like an upload problem. Inspecting the failed document record isolated the actual stage and avoided unnecessary changes to the parser or document. The following is a chronological engineering account, not a controlled experiment.'),
        ('h2','Provider setup and connection failures'),
        ('p','The initial configuration still contained placeholder provider credentials and used an OpenAI-compatible setup. The file was accepted and parsed, but subsequent model calls could not complete. A socket-access restriction also affected an isolated diagnostic environment; permitting network access for that diagnostic allowed the provider check to run. Server availability and provider connectivity were separate questions.'),
        ('h2','Model availability: HTTP 404'),
        ('p','After Gemini was configured, the provider rejected gemini-2.5-flash for the account, returning a model-unavailable response. Updating the generation model removed that specific blocker. A valid key does not guarantee access to every model name, and model availability can change independently of the application.'),
        ('h2','Account quota: HTTP 429'),
        ('p','The next failure was RESOURCE_EXHAUSTED. The recorded response identified a free-tier limit of five generation requests per minute for gemini-3.6-flash in that project and suggested a delay of roughly 58 seconds. The document had reached seven processing chunks; several extraction calls were competing for the quota. That response concerned request rate, not the resume word count [4].'),
        ('h2','Configuration change and successful retry'),
        ('p','A minimal Flash-Lite generation test succeeded, and a separate embedding check returned a vector with 1,536 values. The configuration was changed to gemini-3.1-flash-lite, with MAX_ASYNC_LLM=1 and MAX_PARALLEL_INSERT=1. Old local server instances were stopped, one server was restarted, and the supported failed-document retry completed successfully.'),
        ('callout','Concurrency is not rate limiting. One request at a time can still exceed a per-minute or daily quota. The successful retry does not prove that concurrency alone solved the problem: the model and execution conditions also changed.'),
    ]),
    ('What was verified', [
        ('p','This report uses the dated development-session evidence from 29 August 2026. The application log was inspected again during report preparation on 30 August. The server was offline at that later inspection and the default index no longer contained the sample, so these measurements are historical observations, not a claim about a currently populated live deployment.'),
        ('table',(['Check','Observed result','What it establishes'],[
            ['Document ingestion','One DOCX reached processed','The tested ingestion path completed'],
            ['Final chunk count','1 consolidated chunk','Final pipeline output for this retry'],
            ['Graph write','16 nodes; 15 edges','Graph construction and persistence occurred'],
            ['Embedding diagnostic','1 vector; 1,536 values','Configured embedding API returned data'],
            ['Generation diagnostic','Minimal prompt returned OK','The selected generation model responded'],
            ['Context-only retrieval','4,556 characters; 1 reference','Source-backed context was returned'],
            ['Graph interface','16 nodes; 15 edges displayed','UI counts matched the recorded graph'],
        ],[2550,2790,4020])),
        ('h2','Interpretation of the evidence'),
        ('p','The retrieval check used a context-only request. It demonstrated retrieval of non-empty evidence with a document reference; it did not grade a final generated answer. The separate generation diagnostic established provider access, not answer faithfulness. Likewise, the graph counts describe the output size, not a manual audit of the extracted relationships.'),
        ('p','The failed run showed seven chunks, whereas the completed retry showed one. That difference is another reason not to treat the before-and-after sequence as an isolated performance comparison. The report does not claim an accuracy improvement, speedup, lower cost percentage or statistically significant result.'),
        ('h2','What remains untested'),
        ('p','There is no completed multi-document benchmark, systematic retrieval-mode comparison, answer-quality score, exhaustive format test or public deployment load test. A single successful document is a useful functional milestone, but not evidence of production reliability across arbitrary documents.'),
    ]),
    ('Using the application', [
        ('h2','Start the installed local environment'),
        ('p','From the repository folder, the following PowerShell command runs the already-installed environment. A fresh clone still requires the dependency and frontend build steps documented in the README. This report does not certify a fresh-clone installation on every operating system.'),
        ('code','.\\.venv\\Scripts\\sentinel-rag-server.exe --host 127.0.0.1 --port 9621'),
        ('p','Open http://127.0.0.1:9621/webui/ and keep the server process running. Restart the server after changing .env because the running process may otherwise retain old provider settings. Avoid launching multiple instances against the same default storage directory.'),
        ('h2','Upload, inspect and query'),
        ('step',('Documents','Upload a supported file and wait for Completed. If it fails, inspect the document error or pipeline detail before retrying. A larger word count is not automatically the cause.')),
        ('step',('Knowledge Graph','Use the refresh control and select * for an overview. Search for an entity, select a node and inspect its properties and connections. Reset zoom if the graph is outside the visible area.')),
        ('step',('Retrieval','Choose a mode, ask a question and check the supporting references. With no reranker configured, leave reranking disabled in the query settings.')),
        ('h2','Questions that expose useful behavior'),
        ('p','A factual question: "Which technologies are explicitly listed in this document?" A relationship question: "Which technologies are connected to each project?" A boundary question: "Does the document provide deployment costs? If not, say that the information is unavailable." These are demonstration prompts, not scored results.'),
        ('h2','Understand the status before acting'),
        ('p','No graph change may mean the document is still processing, the view needs refreshing, the current filter hides new entities, or matching entities were merged rather than duplicated. Distinguish an empty graph from a stale visualization by checking document completion and graph counts.'),
        ('callout','An API key for Gemini is different from LIGHTRAG_API_KEY. The first authorizes model calls; the second protects access to this application.'),
    ]),
    ('Configuration and operational choices', [
        ('p','The tested setup favors a small local deployment with straightforward persistence. The following settings describe the successful configuration, with all credentials intentionally omitted. Model availability and quota allowances should be checked for the account at the time of use.'),
        ('code','LLM_BINDING=gemini\nLLM_BINDING_HOST=DEFAULT_GEMINI_ENDPOINT\nLLM_MODEL=gemini-3.1-flash-lite\nMAX_ASYNC_LLM=1\n\nEMBEDDING_BINDING=gemini\nEMBEDDING_BINDING_HOST=DEFAULT_GEMINI_ENDPOINT\nEMBEDDING_MODEL=gemini-embedding-001\nEMBEDDING_DIM=1536\n\nMAX_PARALLEL_INSERT=1\nRERANK_BINDING=null'),
        ('h2','Why use separate generation and embedding models?'),
        ('p','A generation model produces language and structured extraction output. An embedding model produces vectors used to rank semantically related content. One is not a replacement for the other. Matching vector dimensions is necessary, but dimensions alone do not define compatibility: changing the embedding model requires a separately rebuilt index in the new vector space [3].'),
        ('h2','Why start with local file-backed storage?'),
        ('p','NetworkX, NanoVectorDB and JSON-backed stores keep the initial deployment understandable and avoid requiring a separate database cluster. Their simplicity is useful for demonstration and diagnosis. It is not a claim that a file-backed single-process configuration is the right choice for every workload or many concurrent users.'),
        ('h2','Why keep concurrency conservative?'),
        ('p','A document can cause more than one provider call through extraction, follow-up extraction, keyword generation and final answering. Lower concurrency reduces bursts, but a robust quota strategy also needs pacing, provider-directed retry delays and explicit handling of daily exhaustion. Google documents request, token and daily limits separately, with limits applied at project level [4].'),
    ]),
    ('Security, privacy and limitations', [
        ('h2','Local hosting does not mean local inference'),
        ('p','The browser and storage can run on the same computer while the backend sends extracted text to a cloud provider. Private resumes, internal reports and personal identifiers therefore need deliberate handling. The source document used during development is not reproduced here; the figures are conceptual and the measurements are sanitized.'),
        ('p','Google lists different data-use terms for free and paid Gemini API tiers. Users should review the applicable terms before sending personal or confidential material [5]. A local model is an architectural alternative, not an offline configuration verified by this report.'),
        ('h2','Protect credentials and exposure'),
        ('p','Keep .env out of version control and do not show key values in screenshots, demos or logs. A key exposed during development should be revoked and replaced; this report contains no credentials and does not certify that account-level rotation has occurred. For a shared deployment, configure authentication before exposing the API beyond loopback, add HTTPS and limit origins as appropriate.'),
        ('h2','Documents are evidence, not trusted instructions'),
        ('p','Uploaded text may contain misleading claims or prompt-injection instructions. Retrieving a passage does not make it authoritative. Generated answers should remain grounded in the source, and the application should not treat document text as permission to execute commands, reveal credentials or take external actions. A systematic prompt-injection defense evaluation remains future work.'),
        ('h2','Quality and deployment boundaries'),
        ('p','Entity extraction can omit important facts, create duplicates or infer a relationship that is not supported. Parser behavior can vary across scanned PDFs, complex tables and image-heavy files. Provider quota and availability can interrupt otherwise valid requests. These risks motivate source inspection, explicit uncertainty and failure reporting rather than an unconditional promise of correct answers.'),
        ('p','Public production readiness is not established. Before deployment, verify authentication, backups and restore, storage isolation, upload limits, dependency security, observability and workload-specific tests. A successful local demonstration does not replace these checks.'),
    ]),
    ('Lessons learned and next steps', [
        ('h2','What this project demonstrates'),
        ('p','The project connects a document-management interface, an asynchronous Python service, generation and embedding APIs, graph construction and evidence retrieval. More importantly, the case study shows how to diagnose across those boundaries: inspect the failing stage, read the provider error, test components independently, then verify the pipeline after changing configuration.'),
        ('p','Several lessons are transferable. An accepted upload can still fail downstream. A valid key can target an unavailable model. Concurrency controls do not guarantee compliance with rate limits. A graph view can be stale even when graph data exists. A retrieval response can be non-empty without proving that a final answer is correct.'),
        ('h2','A practical improvement sequence'),
        ('step',('Measure retrieval quality','Create a public document collection and question set with expected answers and evidence. Compare naive, hybrid and mix under the same model and context budget. Report errors and latency alongside correctness.')),
        ('step',('Make quota handling explicit','Add request pacing and respect provider retry guidance. Keep retry attempts bounded and distinguish temporary throttling from daily quota exhaustion. This controller is proposed work, not an implemented result.')),
        ('step',('Strengthen traceability','Capture sanitized per-stage timing, provider errors and source references. Use separate research and private-data workspaces so public experiments cannot leak personal content.')),
        ('step',('Validate deployment','Test authentication, persistence after restart, backup recovery and representative file formats before exposing the system publicly.')),
        ('h2','Conclusion'),
        ('p','Sentinel RAG Ops is a practical engineering case study in making document knowledge accessible and inspectable. The documented milestone is successful DOCX ingestion, graph creation, embedding integration and source-backed context retrieval in a local setup. Its portfolio value lies in explaining the architecture and the diagnosis clearly, preserving upstream credit, and setting measurable next steps without overstating what one successful example proves.'),
        ('callout','Portfolio summary: customized and configured a LightRAG-based document knowledge application; investigated provider and quota failures; verified graph creation and evidence retrieval in a documented local case study.'),
    ]),
    ('References and evidence notes', [
        ('ref',('[1] Lewis, P. et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.','https://arxiv.org/abs/2005.11401')),
        ('ref',('[2] Guo, Z., Xia, L., Yu, Y., Ao, T. and Huang, C. (2024; revised 2025). LightRAG: Simple and Fast Retrieval-Augmented Generation.','https://arxiv.org/abs/2410.05779')),
        ('ref',('[3] Google AI for Developers. Gemini API: Embeddings. Accessed 30 August 2026.','https://ai.google.dev/gemini-api/docs/embeddings')),
        ('ref',('[4] Google AI for Developers. Gemini API: Rate limits. Accessed 30 August 2026.','https://ai.google.dev/gemini-api/docs/rate-limits')),
        ('ref',('[5] Google AI for Developers. Gemini Developer API pricing and tier data-use information. Accessed 30 August 2026.','https://ai.google.dev/gemini-api/docs/pricing')),
        ('ref',('[6] HKUDS. LightRAG source repository; see also LICENSE and THIRD_PARTY_NOTICES.md in the customized project.','https://github.com/HKUDS/LightRAG')),
        ('h2','Project evidence register'),
        ('small','Source inspection: README.md, AGENTS.md, pyproject.toml, lightrag_webui/package.json, lightrag/api/lightrag_server.py, lightrag/llm/gemini.py and the graph/retrieval UI components. These establish documented architecture and available configuration, not exhaustive runtime validation.'),
        ('small','Development evidence: provider diagnostic outputs and API/UI checks recorded on 29 August 2026. The application log at 20:27:27 records a graph with 16 nodes and 15 edges; at 20:27:29 it records processing completion. Context-only retrieval returned 4,556 characters and one reference. These are historical functional observations.'),
        ('small','Preparation check: on 30 August the configured model identifiers were rechecked without printing credentials. The server was not reachable and the default document-status store was empty. No data was restored, re-uploaded or regenerated to create the report. Raw logs and the private source document are deliberately excluded.'),
        ('h2','Attribution and report status'),
        ('small','Project owner: Harsh Chaudhary. This is a portfolio technical report prepared with AI-assisted documentation, not a peer-reviewed publication. Core graph-RAG functionality is attributed to LightRAG and its contributors. Diagrams are explanatory illustrations. Future-work statements are not implementation claims.'),
    ]),
]


def set_style(doc,name,size,color='25354A',before=0,after=6,line=1.1,bold=False):
    st=doc.styles[name] if name in doc.styles else doc.styles.add_style(name,1)
    st.font.name='Calibri'; st.font.size=Pt(size); st.font.bold=bold
    st.font.color.rgb=RGBColor.from_string(color)
    st._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:ascii'),'Calibri')
    st._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:hAnsi'),'Calibri')
    pf=st.paragraph_format; pf.space_before=Pt(before); pf.space_after=Pt(after); pf.line_spacing=line
    pf.widow_control=True
    return st


def xml_prop(parent,tag,attrs):
    element=parent.find(qn(tag))
    if element is None: element=OxmlElement(tag); parent.append(element)
    for key,value in attrs.items(): element.set(qn(key),str(value))
    return element


def hyperlink(p,text,url):
    rid=p.part.relate_to(url,RT.HYPERLINK,is_external=True)
    link=OxmlElement('w:hyperlink'); link.set(qn('r:id'),rid)
    run=OxmlElement('w:r'); props=OxmlElement('w:rPr')
    xml_prop(props,'w:color',{'w:val':TEAL}); run.append(props)
    txt=OxmlElement('w:t'); txt.text=text; run.append(txt); link.append(run); p._p.append(link)


def number_definition(doc):
    numbering=doc.part.numbering_part.element
    aid=max([int(e.get(qn('w:abstractNumId'))) for e in numbering.findall(qn('w:abstractNum'))]+[0])+1
    abstract=OxmlElement('w:abstractNum'); abstract.set(qn('w:abstractNumId'),str(aid))
    lvl=OxmlElement('w:lvl'); lvl.set(qn('w:ilvl'),'0')
    for tag,val in [('w:start','1'),('w:numFmt','decimal'),('w:lvlText','%1.'),('w:lvlJc','left')]: xml_prop(lvl,tag,{'w:val':val})
    pp=OxmlElement('w:pPr'); xml_prop(pp,'w:ind',{'w:left':720,'w:hanging':360})
    tabs=OxmlElement('w:tabs'); xml_prop(tabs,'w:tab',{'w:val':'num','w:pos':720}); pp.append(tabs)
    xml_prop(pp,'w:spacing',{'w:before':0,'w:after':160,'w:line':280,'w:lineRule':'auto'})
    lvl.append(pp); abstract.append(lvl); numbering.append(abstract)
    def new_id():
        nid=max([int(e.get(qn('w:numId'))) for e in numbering.findall(qn('w:num'))]+[0])+1
        num=OxmlElement('w:num');num.set(qn('w:numId'),str(nid));xml_prop(num,'w:abstractNumId',{'w:val':aid})
        override=xml_prop(num,'w:lvlOverride',{'w:ilvl':0})
        xml_prop(override,'w:startOverride',{'w:val':1})
        numbering.append(num)
        return nid
    return new_id


def add_table(doc,headers,rows,widths):
    assert sum(widths)==9360
    table=doc.add_table(rows=1,cols=len(headers)); table.autofit=False
    table.style='Table Grid'
    for cell,text in zip(table.rows[0].cells,headers):cell.text=text
    for row in rows:
        for cell,text in zip(table.add_row().cells,row):cell.text=text
    pr=table._tbl.tblPr
    xml_prop(pr,'w:tblW',{'w:w':9360,'w:type':'dxa'});xml_prop(pr,'w:tblInd',{'w:w':120,'w:type':'dxa'})
    margins=xml_prop(pr,'w:tblCellMar',{})
    for side,val in [('top',80),('bottom',80),('start',120),('end',120)]:xml_prop(margins,'w:'+side,{'w:w':val,'w:type':'dxa'})
    for col,w in zip(table._tbl.tblGrid.gridCol_lst,widths):col.set(qn('w:w'),str(w))
    borders=xml_prop(pr,'w:tblBorders',{})
    for side in ('top','left','bottom','right','insideH','insideV'):xml_prop(borders,'w:'+side,{'w:val':'single','w:sz':4,'w:color':'D6DEE7'})
    for ri,row in enumerate(table.rows):
        rp=row._tr.get_or_add_trPr();xml_prop(rp,'w:cantSplit',{})
        if ri==0:xml_prop(rp,'w:tblHeader',{})
        for ci,cell in enumerate(row.cells):
            cell.width=Inches(widths[ci]/1440)
            xml_prop(cell._tc.get_or_add_tcPr(),'w:tcW',{'w:w':widths[ci],'w:type':'dxa'})
            if ri==0:xml_prop(cell._tc.get_or_add_tcPr(),'w:shd',{'w:fill':'F2F4F7'})
            for p in cell.paragraphs:
                p.style=doc.styles['Table Text']
                for run in p.runs:run.bold=(ri==0)
    doc.add_paragraph('',style='Table Gap')
    return table


def build():
    architecture_image();graph_image()
    doc=Document();s=doc.sections[0]
    s.page_width=Inches(8.5);s.page_height=Inches(11)
    s.top_margin=s.bottom_margin=s.left_margin=s.right_margin=Inches(1)
    s.header_distance=s.footer_distance=Inches(.492);s.different_first_page_header_footer=True
    set_style(doc,'Normal',11)
    set_style(doc,'Title',32,NAVY,0,12,1.05,True)
    set_style(doc,'Subtitle',16,MUTED,0,12,1.15)
    for name,size,before,after,col in [('Heading 1',16,16,8,BLUE),('Heading 2',13,12,6,BLUE),('Heading 3',12,8,4,'1F4D78')]:
        st=set_style(doc,name,size,col,before,after,1.1,True);st.paragraph_format.keep_with_next=True
    set_style(doc,'Kicker',10,TEAL,0,10,1.1,True)
    set_style(doc,'Caption',9,MUTED,4,8,1.1)
    set_style(doc,'Table Text',9.5,'25354A',0,3,1.1)
    set_style(doc,'Table Gap',2,'25354A',0,3,1)
    set_style(doc,'Small',9.5,MUTED,0,7,1.1)
    set_style(doc,'Reference',9,MUTED,0,8,1.1)
    set_style(doc,'Callout',11,NAVY,8,8,1.15)
    set_style(doc,'Code',8.5,'25354A',5,8,1.1)
    doc.styles['Code'].font.name='Consolas'
    doc.styles['Code']._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:ascii'),'Consolas')
    doc.styles['Code']._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:hAnsi'),'Consolas')
    set_style(doc,'List Number',11,'25354A',0,8,280/240)
    doc.styles['List Number'].paragraph_format.left_indent=Inches(.5)
    doc.styles['List Number'].paragraph_format.first_line_indent=Inches(-.25)
    for name in ('Header','Footer'):set_style(doc,name,8.5,MUTED,0,0,1.0)
    doc.styles['Footer'].paragraph_format.tab_stops.clear_all()
    header=s.header.paragraphs[0];header.style='Header';header.text='SENTINEL RAG OPS  /  ENGINEERING CASE STUDY'
    footer=s.footer.paragraphs[0];footer.style='Footer'
    footer.paragraph_format.tab_stops.add_tab_stop(Inches(6.5),WD_ALIGN_PARAGRAPH.RIGHT)
    footer.add_run('Harsh Chaudhary  |  Portfolio report\t')
    f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');footer._p.append(f)
    cp=doc.core_properties;cp.title='Sentinel RAG Ops: From Documents to Connected Knowledge';cp.author='Harsh Chaudhary'
    cp.subject='Portfolio engineering case study';cp.keywords='RAG, knowledge graph, Gemini, LightRAG, technical portfolio'
    cp.comments='Privacy-safe report. Historical development verification; not a comparative research benchmark.'

    p=doc.add_paragraph('PORTFOLIO TECHNICAL REPORT',style='Kicker');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(68)
    p=doc.add_paragraph('Sentinel RAG Ops',style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p=doc.add_paragraph('From Documents to\nConnected Knowledge',style='Subtitle');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p=doc.add_paragraph('Architecture, model integration and practical lessons\nfrom a local graph-based RAG deployment',style='Normal');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(24)
    p=doc.add_paragraph('Harsh Chaudhary\n30 August 2026',style='Small');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(28)
    doc.add_heading('Executive summary',level=2)
    doc.add_paragraph('Sentinel RAG Ops is a customized, LightRAG-based application for uploading documents, turning their content into a graph and vector indexes, and retrieving evidence for questions. A React console makes document processing and graph relationships visible, while a FastAPI backend coordinates parsing, model calls and persistent storage.')
    doc.add_paragraph('This report explains the system in practical terms and documents a local engineering case study. The recorded run completed DOCX ingestion, wrote a 16-node, 15-edge graph and returned source-backed retrieval context. Provider configuration, model availability and quota limits were diagnosed as separate failure classes. The report describes these observations without inventing benchmark accuracy or claiming a new algorithm.')
    p=doc.add_paragraph('DOCUMENTS  /  KNOWLEDGE GRAPH  /  EVIDENCE RETRIEVAL',style='Kicker');p.paragraph_format.space_before=Pt(18)
    doc.add_paragraph('Reading guide: architecture and ingestion (pages 2-4); graph retrieval and diagnosis (5-6); verification and operation (7-9); limitations, lessons and sources (10-12).',style='Small')
    new_num=number_definition(doc)
    markdown=['# Sentinel RAG Ops: From Documents to Connected Knowledge','Harsh Chaudhary | 30 August 2026','Portfolio technical report. Historical functional verification; not a comparative benchmark.']
    for index,(title,blocks) in enumerate(PAGES,1):
        section_kicker = doc.add_paragraph(f'{index:02d}  /  TECHNICAL CASE STUDY',style='Kicker')
        section_kicker.paragraph_format.page_break_before = True
        section_kicker.paragraph_format.keep_with_next = True
        doc.add_heading(title,level=1)
        nid=new_num()
        markdown.append('\n## '+title)
        for kind,data in blocks:
            if kind=='h2':doc.add_heading(data,level=2);markdown.append('\n### '+data)
            elif kind in ('p','small','callout','code'):
                style={'p':'Normal','small':'Small','callout':'Callout','code':'Code'}[kind]
                p=doc.add_paragraph(data,style=style)
                if kind in ('callout','code'):
                    xml_prop(p._p.get_or_add_pPr(),'w:shd',{'w:fill':'F4F6F9'})
                    p.paragraph_format.left_indent=Inches(.1);p.paragraph_format.right_indent=Inches(.1)
                    p.paragraph_format.keep_together=True
                markdown.append(('```text\n'+data+'\n```') if kind=='code' else data)
            elif kind=='step':
                p=doc.add_paragraph(style='List Number');p.add_run(data[0]+'. ').bold=True;p.add_run(data[1])
                np=xml_prop(p._p.get_or_add_pPr(),'w:numPr',{});xml_prop(np,'w:ilvl',{'w:val':0});xml_prop(np,'w:numId',{'w:val':nid})
                markdown.append('- **'+data[0]+'**: '+data[1])
            elif kind=='table':
                add_table(doc,*data)
                heads,rows,_=data;markdown.append('| '+' | '.join(heads)+' |');markdown.append('| '+' | '.join(['---']*len(heads))+' |')
                markdown.extend('| '+' | '.join(row)+' |' for row in rows)
            elif kind=='figure':
                p=doc.add_paragraph();p.paragraph_format.space_after=Pt(0);p.paragraph_format.keep_with_next=True
                run=p.add_run();run.add_picture(str(WORK/data[0]),width=Inches(6.5))
                inline=run._r.xpath('.//wp:docPr')[0];inline.set('descr',data[1])
                doc.add_paragraph(data[1],style='Caption');markdown.append('![Illustration]('+data[0]+')\n'+data[1])
            elif kind=='ref':
                p=doc.add_paragraph(data[0],style='Reference');p.add_run('\n');hyperlink(p,data[1],data[1]);markdown.append(data[0]+' '+data[1])
    doc.save(OUT/'Sentinel_RAG_Ops_Portfolio_Report.docx')
    (WORK/'Sentinel_RAG_Ops_Portfolio_Report.md').write_text('\n\n'.join(markdown),encoding='utf-8')
    (QA/'build_summary.json').write_text(json.dumps({'intended_pages':12,'section_count':len(PAGES),'word_count':len(re.findall(r'\b\S+\b',' '.join(markdown))),'preset':'standard_business_brief','header_pattern':'editorial_cover','named_overrides':['cover-title-32pt-navy','teal-kicker','9.5pt-table-text','8.5pt-code','9pt-references']},indent=2),encoding='utf-8')
    print('Created',OUT/'Sentinel_RAG_Ops_Portfolio_Report.docx')
    print((QA/'build_summary.json').read_text())


if __name__=='__main__':build()
