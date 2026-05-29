from html import escape


def blocked_page(domain: str) -> str:
    safe_domain = escape(domain)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dominio bloqueado</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #f4f6f1;
      color: #1f2933;
      font-family: Arial, Helvetica, sans-serif;
    }}
    main {{
      width: min(640px, 92vw);
      border: 1px solid #c8d2c1;
      background: #ffffff;
      padding: 34px;
      box-shadow: 0 16px 40px rgba(31, 41, 51, 0.14);
    }}
    .label {{
      color: #536b45;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 12px 0;
      font-size: 30px;
    }}
    p {{
      line-height: 1.55;
      margin-bottom: 22px;
    }}
    code {{
      display: block;
      padding: 12px;
      background: #eef2ea;
      border-left: 5px solid #8b3a3a;
      word-break: break-all;
      font-size: 16px;
    }}
  </style>
</head>
<body>
  <main>
    <div class="label">SI2 Content Proxy</div>
    <h1>Acesso bloqueado</h1>
    <p>O dominio solicitado aparece na lista local de restricoes deste proxy.</p>
    <code>{safe_domain}</code>
  </main>
</body>
</html>"""


def error_page(title: str, message: str) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>{escape(title)}</title></head>
<body style="font-family:Arial,sans-serif;margin:40px">
  <h1>{escape(title)}</h1>
  <p>{escape(message)}</p>
</body>
</html>"""
