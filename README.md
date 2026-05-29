# Web Proxy HTTP com Controle de Conteudo

Projeto da disciplina Sistemas para Internet 2. A aplicacao implementa um proxy HTTP didatico em Python/Flask: o navegador envia uma URL para o servidor local, o proxy decide se deve bloquear, buscar ou filtrar o conteudo e entao devolve uma resposta ao cliente.

## Funcionalidades

- Repasse de paginas HTTP permitidas.
- Bloqueio de dominios configurados em `settings/blocked.json`.
- Substituicao de termos em HTML usando `settings/words.json`.
- Registro de acessos em `storage/access_log.jsonl`.
- Pagina de bloqueio propria, gerada pelo codigo.
- Testes unitarios para politica de bloqueio, reescrita de texto e validacao de URL.

## Tecnologia escolhida

Usei Python 3 com Flask. O Flask deixa a entrada HTTP simples e permite concentrar o trabalho na logica do proxy. A biblioteca `requests` faz a conexao com o servidor de origem, com timeout, redirecionamento e leitura de cabecalhos.

A implementacao foi organizada em camadas:

```text
Navegador -> Flask -> politica de conteudo -> cliente HTTP -> filtro HTML -> auditoria -> resposta
```

## Estrutura

```text
run.py
src/
  app_factory.py
  proxy_controller.py
  origin_client.py
  content_policy.py
  text_rewriter.py
  access_audit.py
  html_pages.py
settings/
  blocked.json
  words.json
  http_test_sites.json
storage/
  access_log.jsonl
tests/
docs/
  relatorio_tecnico.tex
  relatorio_tecnico.pdf
```

## Instalacao

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux ou WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execucao

```bash
python run.py
```

Servidor:

```text
http://localhost:5000
```

## Como usar

URL completa:

```text
http://localhost:5000/http://neverssl.com
```

URL sem esquema, assumindo HTTP:

```text
http://localhost:5000/neverssl.com
```

Dominio bloqueado:

```text
http://localhost:5000/http://instagram.com
```

URL com query string:

```text
http://localhost:5000/http://httpbin.org/get?curso=si2
```

O arquivo `settings/http_test_sites.json` contem uma lista de sites HTTP para testes manuais.

## Usando como proxy no navegador

Tambem e possivel configurar o navegador para usar este servidor como proxy HTTP:

```text
Host: 127.0.0.1
Porta: 5000
Tipo: HTTP
```

No Windows, esse caminho e:

```text
Settings > Network & internet > Proxy > Manual proxy setup > Use a proxy server > Set up
```

Ative a opcao, coloque `127.0.0.1` em Address e `5000` em Port.

Depois disso, acesse sites HTTP, por exemplo:

```text
http://neverssl.com
http://example.com
http://info.cern.ch
```

Esta configuracao atende navegacao HTTP normal. Ela nao atende HTTPS porque o navegador usa o metodo `CONNECT` para abrir tuneis TLS, e esta versao do projeto nao implementa esse metodo. A limitacao e explicada no relatorio tecnico.

## Configuracao

`settings/blocked.json`:

```json
{
  "bloqueados": ["instagram.com", "tiktok.com"]
}
```

`settings/words.json`:

```json
{
  "merda": "droga",
  "idiota": "ingenuo"
}
```

O bloqueio normaliza o dominio para comparar sem porta e sem `www.`. O filtro e aplicado apenas quando a resposta tem `Content-Type` HTML.

## Log

Cada acesso gera uma linha JSON em `storage/access_log.jsonl`:

```json
{"timestamp":"2026-05-29T00:00:00+00:00","url":"http://example.local/demo","domain":"example.local","action":"allowed","status_code":200,"filtered_terms_count":0}
```

Acoes possiveis:

- `allowed`: pagina permitida sem alteracao.
- `blocked`: dominio barrado pela lista.
- `filtered`: HTML recebido e alterado pelo filtro.
- `error`: erro ao acessar o servidor de origem.

## HTTPS

O filtro funciona apenas com HTTP em texto claro. Em HTTPS, o conteudo e cifrado com TLS. Um proxy comum so cria ou encaminha um tunel e nao consegue ler o HTML para substituir palavras.

Para filtrar HTTPS seria necessario um proxy MITM com uma autoridade certificadora local instalada no navegador. Isso foge do escopo desta entrega.

## Testes

```bash
python -m pytest -q
```

## Checklist do enunciado

- Codigo-fonte completo do proxy: sim.
- Arquivos `blocked.json` e `words.json`: sim, em `settings/`.
- README com instalacao, configuracao e execucao: sim.
- Log gerado por sessao de teste: sim, em `storage/access_log.jsonl`.
- Relatorio tecnico em PDF: sim, em `docs/relatorio_tecnico.pdf`.
- Explicacao sobre HTTPS: sim, no README e no relatorio.

## Autoria e uso de IA

Autores: Andrey Vinicius Santos Souza - 164402.

Uso de IA: usei inteligencia artificial como apoio para organizar a estrutura do projeto, revisar textos do README e do relatorio, escrever testes simples e entender como adaptar o proxy para funcionar tambem quando configurado no navegador pelo proxy manual do Windows.