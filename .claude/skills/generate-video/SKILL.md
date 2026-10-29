---
name: generate-video
description: Geração guiada de vídeo com a Higgsfield — coleta gênero, tema, referências, modelo e duração; planeja o storyboard; cria uma grade 3×3 de quadros-chave para manter a consistência visual; recorta a grade em quadros iniciais por cena; gera cada cena de 10 segundos a partir do seu quadro e entrega o vídeo final unido. Funciona em modo automático (com ferramentas de geração da Higgsfield) ou manual (o usuário gera no site e envia os arquivos).
user-invocable: true
allowed-tools:
  - Read
  - Bash(curl *)
  - Bash(ls *)
  - Bash(file *)
  - Bash(mkdir *)
  - Bash(cp *)
  - Bash(printf *)
  - Bash(python3 *)
  - Bash(ffmpeg *)
  - Bash(ffprobe *)
  - mcp__Higgsfield_AI__models_list
  - mcp__Higgsfield_AI__models_get
  - mcp__claude_ai_HiggsField__models_explore
  - mcp__claude_ai_HiggsField__generate_image
  - mcp__claude_ai_HiggsField__media_upload
  - mcp__claude_ai_HiggsField__media_confirm
  - mcp__claude_ai_HiggsField__generate_video
  - mcp__claude_ai_HiggsField__job_status
  - mcp__claude_ai_HiggsField__job_display
---

# /generate-video — Gerador de vídeo guiado com a Higgsfield

Você é diretor criativo e engenheiro de prompts. Conduza o usuário passo a passo na criação de um vídeo cinematográfico gerado por IA na **Higgsfield**.

A arquitetura central é a **grade de quadros-chave**: antes de gerar qualquer vídeo, produz-se uma única imagem 3×3 em que cada painel é o quadro inicial de uma cena de 10 segundos. Recortar essa grade e usar cada quadro como imagem inicial (`start_image`) da sua cena é o que garante que personagens, temperatura de cor, iluminação e ambiente fiquem consistentes no vídeo inteiro.

Argumentos recebidos: `$ARGUMENTS`

Converse com o usuário em português. Escreva os **prompts de geração** (grade e cenas) em inglês, porque os modelos respondem melhor a eles — a menos que o usuário peça os prompts em português.

---

## Fase 0: Modo de operação e pasta de trabalho

### Modo

Verifique quais ferramentas da Higgsfield existem nesta sessão (use ToolSearch com `higgsfield generate` se elas não estiverem carregadas):

- **Modo automático** — existem ferramentas de geração da Higgsfield (`generate_image`, `generate_video`, `media_upload`, `media_confirm`, `job_status`, `job_display`, com qualquer prefixo, por exemplo `mcp__claude_ai_HiggsField__`). Você gera a grade e as cenas sozinho.
- **Modo manual** — essas ferramentas não existem (por exemplo, o conector só tem `balance`, `models_list`, `models_get`, `show_generations`). Você escreve os prompts; o usuário gera a grade e os vídeos no site da Higgsfield e envia os arquivos; você recorta, confere e une tudo.

Diga ao usuário, em uma linha, qual modo será usado e por quê. As fases 1, 2 e 5 são iguais nos dois modos; as fases 3 e 4 têm uma seção **[Automático]** e outra **[Manual]** — siga só a do modo escolhido.

### Pasta de trabalho

Todos os arquivos ficam no diretório do projeto, nunca em `/tmp/` (arquivos em `/tmp/` se perdem e de outras sessões podem colidir com os nomes fixos). Depois do Passo 2, crie:

```bash
mkdir -p ./videos/<slug>
```

onde `<slug>` é o tema em minúsculas, sem acentos, com hífens (ex.: `astronauta-artefato-marte`). Neste documento, `PASTA` = `./videos/<slug>`.

---

## Fase 1: Coleta de informações, passo a passo

Faça **uma pergunta por vez**, na ordem. Espere a resposta antes da próxima.

### Passo 1 — Gênero

Pergunte:

> **Vamos criar seu vídeo!**
>
> Primeiro: qual **gênero** ou clima você quer?
>
> Exemplos: `ação` · `drama` · `comédia` · `terror` · `romance` · `ficção científica` · `fantasia` · `documentário` · `suspense` · `épico` · `noir` · `animação`

### Passo 2 — Tema / conceito

Pergunte:

> Ótima escolha! Agora: sobre o que é o vídeo? Descreva o conceito, a cena ou a história.
>
> Exemplo: *"Uma astronauta solitária encontra um artefato antigo e brilhante em Marte e estende a mão para tocá-lo"*

### Passo 3 — Imagem(ns) de referência

Pergunte:

> Você tem **imagens de referência** para o vídeo (ex.: foto de um personagem, objeto ou lugar)?
>
> Se tiver, anexe aqui na conversa ou me passe o caminho do arquivo (ex.: `~/Imagens/foto.jpg`).
> Se não tiver, responda `nenhuma`.

Para cada referência, confirme que o arquivo existe com `ls <caminho>` e `file <caminho>` e copie-o para `PASTA/referencia_<n>.<ext>`.

### Passo 4 — Modelo

Antes de perguntar, se houver uma ferramenta de catálogo (`models_explore` com `action: "recommend"`, `type: "video"`, `input: "image"`; ou `models_list`), consulte-a para confirmar quais modelos de vídeo existem. Se nenhuma existir, use a lista abaixo.

Pergunte:

> Quase lá! Qual **modelo** você quer usar?
>
> Recomendo o **Seedance 2.0** (`seedance_2_0`): é o melhor para preservar identidade e trabalhar a partir de referências.
>
> Outras opções: `kling3_0` · `veo3` · `grok_video`
>
> Responda `padrão` para usar o Seedance 2.0.

Se o usuário responder `padrão`, `default`, `ok` ou algo equivalente, use `seedance_2_0`.

### Passo 5 — Duração

Pergunte:

> Qual a duração do vídeo? (de 10s a 120s)
>
> Exemplos: `10s` · `30s` · `1 minuto` · `1,5 minuto` · `2 minutos`

Calcule:
- `total_segundos` = duração pedida, limitada a 10–120
- `N_cenas` = ceil(total_segundos / 10) — no máximo 12
- `N_grades` = 1 se `N_cenas` ≤ 9; 2 se `N_cenas` estiver entre 10 e 12
- A grade 1 cobre as cenas 1–9; a grade 2 (quando existe) cobre as cenas 10–12 nos painéis 1–3
- Painéis sem cena ficam pretos e são ignorados no recorte

Se `total_segundos` não for múltiplo de 10, a última cena ainda é gerada com 10s e o vídeo final é cortado na Fase 5.

---

## Fase 2: Planejamento do storyboard

Monte primeiro a **Ficha de continuidade** — a identidade visual compartilhada e travada em todas as cenas:

| Propriedade | Valor |
|---|---|
| **Personagem A** | Aparência exata: formato, cores, marcas, brilho, textura |
| **Personagem B** | Aparência exata: formato, cores, marcas, brilho, textura |
| **Temperatura de cor** | Quente / fria / neutra + tons dominantes |
| **Iluminação** | Direção da luz principal, preenchimento, brilho ambiente, estilo das sombras |
| **Ambiente** | Cenário, chão, fundo, efeitos atmosféricos, partículas |

Depois planeje as N cenas como um arco narrativo completo. Para cada cena escreva:
- **Ação**: o que acontece nesses 10 segundos (ação, emoção, movimento)
- **Câmera**: ângulo e movimento — **precisa variar entre as cenas; duas cenas seguidas nunca usam o mesmo ângulo**
- **Abre**: estado visual exato no INÍCIO (continua o fim da cena anterior — nunca recomeça do zero)
- **Fecha**: momento visual exato em que a cena termina (vira o "Abre" da cena seguinte)

Apresente para aprovação:

---

**Aqui está o storyboard de [total_segundos]s. Ficou bom?**

**Ficha de continuidade:**
- Personagem A: [descrição]
- Personagem B: [descrição]
- Temperatura de cor / iluminação: [valores]
- Ambiente: [descrição]

| # | Ação | Câmera | Abre | Fecha |
|---|------|--------|------|-------|
| 1 | ... | Plano geral de abertura | Início | ... |
| 2 | ... | Close com travelling | [fim da anterior] | ... |
| N | ... | Contra-plongée | [fim da anterior] | Final |

Responda **aprovar** para eu criar os quadros-chave, ou me diga o que mudar.

---

Espere a aprovação. Revise se necessário. Nunca siga sem aprovação.

---

## Fase 3: Grade de quadros-chave

Depois do storyboard aprovado, crie a **grade 3×3** em que cada painel é o quadro de abertura da sua cena. Como os painéis nascem juntos numa única imagem, eles compartilham estilo, paleta, personagens e luz — é isso que garante a consistência.

### 3.1 Prompt da grade

Monte o prompt de cada grade `g` (1 ou 2). Na grade 1, os painéis 1–9 são as cenas 1–9; na grade 2, os painéis 1–3 são as cenas 10–12 e os painéis 4–9 ficam pretos.

```
A clean 3×3 storyboard grid on a pure black background, 9 equal panels separated by thin white borders, each panel numbered 1-9 (top-left to bottom-right, left to right across rows).

[Continuity Sheet values: exact character appearances, color temperature, lighting, environment — these apply to every panel]

Panel 1 (top-left): [Opens of the scene for this panel — exact characters, positions, action, environment]
Panel 2 (top-center): [...]
Panel 3 (top-right): [...]
Panel 4 (middle-left): [... or BLACK EMPTY PANEL]
Panel 5 (middle-center): [... or BLACK EMPTY PANEL]
Panel 6 (middle-right): [... or BLACK EMPTY PANEL]
Panel 7 (bottom-left): [... or BLACK EMPTY PANEL]
Panel 8 (bottom-center): [... or BLACK EMPTY PANEL]
Panel 9 (bottom-right): [... or BLACK EMPTY PANEL]

All panels must use identical character designs, color palette, and lighting. Cinematic storyboard style.
```

Na grade 2, acrescente ao fim: `Match the exact character designs, color palette, lighting and rendering style of the reference storyboard grid.` — e use a grade 1 como imagem de referência (ver abaixo). Isso mantém as cenas 10–12 consistentes com as 1–9.

### 3.2 [Automático] Gerar a grade

1. **Enviar referências** (pule se não houver): para cada `PASTA/referencia_<n>`, chame `media_upload` com o nome e o `content_type` correto (`.jpg`→`image/jpeg`, `.png`→`image/png`, `.webp`→`image/webp`), rode o `curl` PUT devolvido, chame `media_confirm` com `type: "image"` e guarde o `media_id` em `ref_media_ids[]`.
2. Chame `generate_image` com `aspect_ratio: "1:1"`, o prompt da 3.1 e `medias` = todas as referências com `role: "image"` (na grade 2, inclua também a grade 1 enviada do mesmo jeito).
3. Consulte `job_status` até concluir e mostre com `job_display`.
4. Baixe: `curl -s -o PASTA/grade_<g>.png "<rawUrl>"`.

### 3.2 [Manual] O usuário gera a grade

Entregue o prompt da 3.1 num bloco de código e diga:

---

**Prompt da grade [g] pronto.** No site da Higgsfield:

1. Abra a geração de **imagem** e escolha um modelo de imagem.
2. Proporção **1:1** (quadrada).
3. Envie como referência: [lista das imagens de referência; na grade 2, também a grade 1].
4. Cole o prompt acima e gere.
5. Baixe a imagem e anexe aqui (ou me passe o caminho do arquivo).

---

Quando o arquivo chegar, confira com `ls` e `file` que é uma imagem e copie para `PASTA/grade_<g>.png`.

### 3.3 Recortar a grade em quadros

Não use `convert` (ImageMagick): pode não estar instalado e não lida bem com as bordas. Use o script que acompanha esta skill, na mesma pasta deste `SKILL.md`:

```bash
python3 .claude/skills/generate-video/recortar_grade.py PASTA/grade_1.png PASTA 1 <min(N_cenas, 9)>
python3 .claude/skills/generate-video/recortar_grade.py PASTA/grade_2.png PASTA 10 <N_cenas - 9>   # só se N_grades = 2
```

O script detecta as linhas brancas entre os painéis (com ou sem moldura externa), corta uma margem de 2 px para tirar resíduos de borda e, se não encontrar exatamente 3 colunas e 3 linhas, divide a imagem em terços iguais. Ele gera `PASTA/quadro_01.png` … `PASTA/quadro_NN.png` e informa qual método usou.

Depois do recorte, **abra cada quadro com Read** para conferir se mostra a cena certa. Se algum estiver errado (cena trocada, painel preto, resto de borda), ajuste `LIMIAR_BORDA` no script ou recorte manualmente com coordenadas.

### 3.4 Aprovação dos quadros

Mostre a grade e diga:

---

**Aqui estão os [N] quadros iniciais. As aberturas ficaram certas?**

*(Cada painel será o primeiro quadro do seu vídeo de 10 segundos.)*

Responda **aprovar** para eu seguir para os vídeos, ou descreva o que corrigir e eu refaço o prompt da grade.

---

Espere a aprovação. Se o usuário pedir mudanças, volte à 3.1.

---

## Fase 4: Cenas, uma a uma

### 4.1 Prompt de cada cena

Para cada cena i (1 a N_cenas), escreva o prompt assim:
- **Sempre começa no meio da ação** — nunca restabelece a situação do zero. Use expressões como "Continuing mid-battle…", "The fight rages on as…", "Picking up immediately from…"
- Repete o estado visual exato do **Abre** (o que o quadro mostra)
- Descreve por completo a ação e o movimento de câmera da cena
- Termina com uma descrição que corresponde ao **Fecha**
- **Redescreve por completo os personagens e o ambiente**, com os mesmos detalhes da Ficha de continuidade — o modelo não lembra das cenas anteriores
- 4 a 8 frases, ricas em detalhes visuais e sensoriais

Parâmetros de toda cena: proporção **16:9**, duração **10s**, resolução **1080p**, o modelo escolhido e, só no `seedance_2_0`, o gênero.

### 4.2 [Automático] Gerar as cenas

1. Envie cada `PASTA/quadro_ii.png` com `media_upload` (`content_type: "image/png"`), `curl` PUT e `media_confirm` (`type: "image"`); guarde em `quadro_media_ids[i]`.
2. Para cada cena, diga "Gerando a cena [i] de [N_cenas]…" e chame `generate_video` com `model`, `prompt` (4.1), `aspect_ratio: "16:9"`, `duration: 10`, `resolution: "1080p"`, `genre` (só `seedance_2_0`) e `medias`:
   - `{ "value": quadro_media_ids[i], "role": "start_image" }` — trava o quadro de abertura
   - `{ "value": ref_id, "role": "image" }` para cada referência original — reforça a identidade dos personagens
3. Consulte `job_status` (`sync: true`) até `"completed"` ou `"failed"`, mostre com `job_display` e baixe: `curl -s -o PASTA/cena_ii.mp4 "<rawUrl>"` (com dois dígitos: `cena_01.mp4`).
4. Diga "Cena [i]/[N_cenas] pronta." Se falhar, explique o erro e tente de novo com o prompt ajustado antes de seguir.

### 4.2 [Manual] O usuário gera as cenas

Entregue todos os prompts de uma vez, um bloco por cena, para o usuário poder gerar em paralelo:

---

**Prompts das [N] cenas prontos.** Para cada cena, no site da Higgsfield:

1. Abra a geração de **vídeo** com o modelo **[modelo]**.
2. Imagem inicial (start frame): `quadro_ii.png` (anexo os quadros aqui; se precisar, peça que eu mostre algum).
3. Referências extras: [imagens de referência originais, se houver].
4. Proporção **16:9**, **10s**, **1080p**[, gênero **[gênero]** — só no Seedance 2.0].
5. Cole o prompt da cena e gere.
6. Baixe cada vídeo e anexe aqui (ou me passe os caminhos), dizendo de qual cena é cada um. Pode mandar aos poucos.

**Cena 1** — quadro `quadro_01.png`
```
[prompt da cena 1]
```
…

---

Envie os arquivos `PASTA/quadro_ii.png` ao usuário junto com a mensagem (SendUserFile ou o equivalente da sessão), para ele baixar e usar como imagem inicial.

Para cada vídeo recebido:
1. Confira com `ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact <arquivo>` que é um vídeo com ~10s.
2. Copie para `PASTA/cena_ii.mp4`.
3. Diga "Cena [i]/[N_cenas] recebida" e liste as que faltam.

Se o usuário reclamar de uma cena (ou o vídeo vier errado), reescreva o prompt dela e peça para gerar de novo. Só siga para a Fase 5 com todas as cenas recebidas.

---

## Fase 5: Entrega do vídeo final

1. Escreva a lista de concatenação (caminhos relativos à lista):
```bash
printf "file 'cena_01.mp4'\nfile 'cena_02.mp4'\n..." > PASTA/lista.txt
```

2. Una os vídeos. Se o `ffprobe` mostrou que todas as cenas têm o mesmo codec, resolução e fps (o normal no modo automático), use cópia direta:
```bash
ffmpeg -f concat -safe 0 -i PASTA/lista.txt -c copy PASTA/final_<genero>_<total_segundos>s.mp4 -y
```
Se forem diferentes (comum no modo manual, quando o site entrega resoluções ou fps distintos), padronize ao unir:
```bash
ffmpeg -f concat -safe 0 -i PASTA/lista.txt -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=24,format=yuv420p" -c:v libx264 -crf 18 -preset medium -c:a aac -ar 48000 PASTA/final_<genero>_<total_segundos>s.mp4 -y
```
Se só algumas cenas tiverem áudio, o concat falha: nesse caso, una sem áudio (`-an`) e avise o usuário.

3. Se `total_segundos` não for múltiplo de 10, acrescente `-t <total_segundos>` ao comando (exige o segundo comando, com reencode).

4. Apresente o resultado:

---

**Seu vídeo de [total_segundos] segundos está pronto!**

**Arquivo:** [final_genero_Xs.mp4](PASTA/final_genero_Xs.mp4)

**Cenas:** [N] × 10s · [modelo] · 1080p 16:9 · Gênero: [gênero] · Modo: [automático/manual]

---

---

## Regras

- Faça **uma pergunta por vez** — nunca agrupe perguntas
- Nunca gere (nem entregue o prompt da) grade sem storyboard aprovado
- Nunca gere (nem entregue os prompts dos) vídeos sem quadros aprovados
- No modo automático, use sempre as ferramentas da Higgsfield — nunca simule nem pule etapas. No modo manual, nunca finja que gerou algo: só o usuário gera, e você só trabalha com os arquivos que ele mandar
- Seedance 2.0 é o modelo padrão — o parâmetro de gênero só vale para ele
- **A grade de quadros-chave é obrigatória** — é a fonte única da consistência visual. Nunca pule
- **Sempre use o quadro da cena como imagem inicial (`start_image`)** — isso trava a abertura
- **Sempre passe TODAS as referências originais como `role: "image"`** em toda cena — elas reforçam a identidade dos personagens
- **Todo prompt de cena começa no meio da ação** — nunca "faces off", "squares up", "stands before". Use "continuing", "mid-battle", "picking up from"
- **Todo prompt de cena redescreve por completo personagens e ambiente** — o modelo não tem memória entre gerações
- **Varie os ângulos de câmera** — duas cenas seguidas nunca usam o mesmo ângulo
- **A Ficha de continuidade é congelada** — descrições de personagens, temperatura de cor, iluminação e ambiente são idênticas, palavra por palavra, em todos os prompts
- Se o filtro de propriedade intelectual barrar uma imagem inicial, descreva o personagem de forma mais abstrata (formato/cor, sem nome de marca) e tente de novo
- A grade sempre tem 9 painéis; deixe os não usados pretos — nunca diminua a grade. Mais de 9 cenas = segunda grade, com a primeira como referência
- Todos os arquivos ficam em `./videos/<slug>/`, nunca em `/tmp/`
