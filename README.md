# Xbox Lifetime Review

Gerador de retrospectiva Xbox via API.

## Estrutura

```
year_review/
├── src/
│   ├── config.py          # Configurações
│   ├── utils.py           # Utilitários
│   ├── api.py             # Cliente Xbox API
│   ├── auth.py            # Autenticação
│   ├── snapshot.py        # Gerador de snapshot
│   ├── html_generator.py  # Gerador HTML
│   └── svg_generator.py   # Gerador SVG para compartilhamento
├── tests/
│   ├── test_utils.py
│   ├── test_api.py
│   ├── test_html_generator.py
│   ├── test_snapshot.py
│   └── test_svg_generator.py
├── authenticate.py        # Entry point: autenticação
├── get_snapshot.py        # Entry point: gerar snapshot
├── generate_html.py       # Entry point: gerar HTML
└── docker-compose.yml
```

## Uso

### Autenticar

```bash
docker-compose run --rm -p 8080:8080 xbox python authenticate.py
```

### Gerar Snapshot

```bash
docker-compose run --rm xbox python get_snapshot.py
docker-compose run --rm xbox python get_snapshot.py "Gamertag"
```

### Gerar HTML e SVG

```bash
docker-compose run --rm xbox python generate_html.py achievements_snapshot_Gamertag_latest.json
```

Gera dois arquivos:
- `lifetime_review_Gamertag.html` - Página HTML completa
- `share_Gamertag.svg` - Imagem 1200x600 para compartilhamento

## Outputs

| Arquivo | Descrição |
|---------|-----------|
| `achievements_snapshot_*.json` | Dados brutos da conta |
| `lifetime_review_*.html` | Página HTML com estatísticas |
| `share_*.svg` | Imagem para redes sociais |

## SEO e Compartilhamento

O HTML gerado inclui:
- Meta tags Open Graph (Facebook)
- Meta tags Twitter Card
- Botão de compartilhar (Web Share API + fallback Twitter)
- Referência ao SVG nas meta tags de imagem

## Testes

```bash
docker-compose run --rm test
```

## Configuração

Variáveis de ambiente:
- `XBOX_CLIENT_ID` - Client ID do Azure AD
- `XBOX_CLIENT_SECRET` - Client Secret do Azure AD

## APIs

| Endpoint | Uso |
|----------|-----|
| profile.xboxlive.com | Perfil |
| titlehub.xboxlive.com | Jogos |
| userstats.xboxlive.com | Horas |
| achievements.xboxlive.com | Conquistas + raridade |
