# Automacao de Testes E2E - Sauce Demo (Python & Selenium)

Projeto de planejamento, execucao e automacao de testes funcionais End-to-End (E2E) para a aplicacao web **Sauce Demo** ([https://www.saucedemo.com/](https://www.saucedemo.com/)), desenvolvido utilizando **Python**, **Selenium WebDriver** e a biblioteca nativa **unittest**.

* **Autora:** Telma Regina da Silva Reis | QA Leader
* **Sistema Sob Teste (SUT):** Sauce Demo (Swag Labs)
* **Ambiente de Execucao:** Web (Google Chrome) / Windows / VS Code

---

## Estrutura do Repositorio

| Arquivo | Descricao |
| :--- | :--- |
| `test_saucedemo.py` | Script principal contendo os 14 casos de teste automatizados com destaque visual em tempo real e relatorios detalhados de falha no terminal. |
| `Definição de casos de testes - Sauce Demo - Telma Regina da Silva Reis.docx` | Documento de especificacao detalhada dos 14 casos de teste (`CT_001` a `CT_014`), incluindo pre-condicoes, passos do usuario e respostas esperadas do sistema. |
| `Acompanhamento de Bugs - Sauce Demo - Telma Regina da Silva Reis.xlsx` | Planilha de gestao de qualidade contendo o controle de execucao dos testes, metricas de cobertura/sucesso e o registro detalhado dos defeitos encontrados. |

---

## Recursos Visuais e de Diagnostico da Automacao

O script `test_saucedemo.py` foi projetado para facilitar demonstracoes ao vivo e analises de causa raiz:

1. **Destaque Luminoso em Tempo Real (Laser Pointer & Neon Highlight):** Antes de cada clique, digitacao ou validacao (`assert`), a automacao injeta dinamicamente via JavaScript um foco luminoso pulsante e uma etiqueta indicativa (`CLICANDO AQUI`, `DIGITANDO`, `VALIDANDO RESULTADO`, `BUG`) sobre o elemento interagido.
2. **Banner de Execucao Fixo:** Exibe no topo do navegador qual Caso de Teste (`CT_001` a `CT_014`) esta sendo executado no momento.
3. **Sessao Unica Otimizada (`setUpClass`):** O navegador e aberto uma unica vez de forma maximizada e em modo anonimo (`--incognito`), limpando cookies, `localStorage` e `sessionStorage` entre cada teste.
4. **Relatorio de Falha Explicativo no Terminal:** Quando uma assercao falha, o terminal apresenta um quadro completo com o **Resultado Esperado**, o **Resultado Obtido na Tela** (capturado em tempo real) e o **Diagnostico do Problema**.

---

## Catalogo de Casos de Teste (`CT_001` a `CT_014`)

| Codigo | Caso de Teste | Usuario | Modulo | Status |
| :--- | :--- | :--- | :--- | :--- |
| **CT_001** | Login com credenciais validas | `standard_user` | Autenticacao | Passou |
| **CT_002** | Login com senha invalida | `standard_user` | Autenticacao | Passou |
| **CT_003** | Login com usuario bloqueado | `locked_out_user` | Autenticacao | Passou |
| **CT_004** | Login com campos obrigatorios vazios | `standard_user` | Autenticacao | Passou |
| **CT_005** | Logout do sistema pelo menu lateral | `standard_user` | Autenticacao | Passou |
| **CT_006** | Ordenar produtos por preco (menor para maior) | `standard_user` | Catalogo | Passou |
| **CT_007** | Adicionar produto ao carrinho | `standard_user` | Carrinho | Passou |
| **CT_008** | Remover produto do carrinho | `standard_user` | Carrinho | Passou |
| **CT_009** | Finalizar compra com sucesso | `standard_user` | Checkout | Passou |
| **CT_010** | Checkout com campos obrigatorios vazios | `standard_user` | Checkout | Passou |
| **CT_011** | Ordenar produtos por preco com `problem_user` | `problem_user` | Catalogo | **Falhou (Bug)** |
| **CT_012** | Exibicao das imagens dos produtos com `problem_user` | `problem_user` | Catalogo | **Falhou (Bug)** |
| **CT_013** | Checkout com usuario `problem_user` | `problem_user` | Checkout | **Falhou (Bug)** |
| **CT_014** | Login com usuario `performance_glitch_user` | `performance_glitch_user` | Performance | Passou / Inativo na Planilha |

---

## Resumo de Metricas e Acompanhamento de Bugs

Conforme documentado na planilha de acompanhamento:

* **Total de Casos Mapeados:** 14
* **Casos Ativos Executados:** 13 (100% dos ativos)
* **Testes Aprovados (Passaram):** 10 (76,9%)
* **Testes Reprovados (Falharam):** 3 (23,1%)

### Defeitos Identificados e Reproduzidos pela Automacao

#### 1. `CT_011` - Ordenacao por preco nao funciona para `problem_user`
* **Severidade:** Media
* **Resultado Esperado:** Ao selecionar `Price (low to high)`, a lista deve ser reordenada exibindo `Sauce Labs Onesie` (`$7.99`) no topo.
* **Resultado Obtido:** O sistema ignora a selecao do filtro e mantem a lista na ordem original, exibindo `Sauce Labs Backpack` (`$29.99`) como primeiro item.

#### 2. `CT_012` - Imagens incorretas e repetidas no catalogo para `problem_user`
* **Severidade:** Media
* **Resultado Esperado:** Os 6 produtos listados em `/inventory.html` devem exibir 6 imagens distintas correspondentes a cada item.
* **Resultado Obtido:** Todos os 6 produtos carregam o mesmo arquivo de imagem (`sl-404.168b1cce.jpg` - foto de um cachorro).

#### 3. `CT_013` - Campo "Last Name" bloqueia o checkout para `problem_user`
* **Severidade:** Alta (Bloqueante)
* **Resultado Esperado:** O formulario em `/checkout-step-one.html` deve manter `First Name = Maria`, `Last Name = Silva` e `Postal Code = 01310100`, avancando para `/checkout-step-two.html`.
* **Resultado Obtido:** Os caracteres digitados no campo `Last Name` sobrescrevem o campo `First Name`, deixando o sobrenome vazio e bloqueando o avanco com a mensagem `Error: Last Name is required`.

---

## Como Executar o Projeto

### 1. Pre-requisitos
* **Python 3.x** instalado
* **Google Chrome** instalado
* Biblioteca **Selenium** instalada:

```bash
pip install selenium
```

### 2. Executando pelo Gerenciador Visual do VS Code (Recomendado)
1. Abra a pasta do projeto no **VS Code**.
2. Clique no icone **Testing (Tubo de Ensaio)** na barra lateral esquerda.
3. Clique em **Configure Python Tests** -> selecione **unittest** -> selecione `.` (diretorio raiz) -> selecione `test_*.py`.
4. Utilize o botao **Run Tests** para rodar a bateria completa ou clique no icone de execucao ao lado de cada caso (`test_ct001` a `test_ct014`) individualmente.

### 3. Executando via Terminal
```bash
python test_saucedemo.py
```

### 4. Ajuste de Velocidade para Apresentacao
No topo do arquivo `test_saucedemo.py`, voce pode calibrar a velocidade da demonstracao alterando as constantes:

```python
TEMPO_ANTES_DO_CLIQUE = 1.5     # Tempo que o destaque fica piscando antes do clique
TEMPO_APOS_ACAO = 1.3           # Pausa apos o clique para visualizacao da mudanca de tela
VELOCIDADE_DIGITACAO = 0.10     # Intervalo entre cada letra digitada nos campos
PAUSA_ENTRE_TESTES = 2.0        # Pausa entre o fim de um caso de teste e o inicio do proximo
```