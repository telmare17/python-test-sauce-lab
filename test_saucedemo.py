import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


TEMPO_ANTES_DO_CLIQUE = 1.5     # Tempo que a luz fica piscando no botão ANTES de clicar
TEMPO_APOS_ACAO = 1.3           # Pausa DEPOIS do clique para ver a tela mudar
VELOCIDADE_DIGITACAO = 0.10     # Tempo entre cada letra digitada nos campos
PAUSA_ENTRE_TESTES = 2.0        # Pausa no final de cada caso de teste


_click_original = WebElement.click
_send_keys_original = WebElement.send_keys


def mostrar_luz_no_elemento(driver, elemento, texto_etiqueta="CLICANDO AQUI", cor="#ff0055"):
    """Injeta um brilho neon, um pulso laser central e uma etiqueta no elemento."""
    try:
        driver.execute_script(
            """
            const el = arguments[0].tagName === 'OPTION' ? arguments[0].parentElement : arguments[0];
            const labelText = arguments[1];
            const color = arguments[2];

            el.scrollIntoView({behavior: 'smooth', block: 'center'});

            if (!el.hasAttribute('data-old-style')) {
                el.setAttribute('data-old-style', el.getAttribute('style') || '');
            }

            // Brilho neon ao redor do elemento
            el.style.transition = 'all 0.2s ease-in-out';
            el.style.outline = `4px solid ${color}`;
            el.style.outlineOffset = '3px';
            el.style.boxShadow = `0 0 25px 8px ${color}, inset 0 0 10px ${color}`;
            el.style.backgroundColor = 'rgba(255, 235, 59, 0.35)';

            // Remove efeitos anteriores se existirem
            const oldBadge = document.getElementById('qa-laser-badge');
            if (oldBadge) oldBadge.remove();
            const oldPulse = document.getElementById('qa-laser-pulse');
            if (oldPulse) oldPulse.remove();

            const rect = el.getBoundingClientRect();

            // Cria o ponto de luz (laser pulsante) no centro do clique
            const pulse = document.createElement('div');
            pulse.id = 'qa-laser-pulse';
            pulse.style.cssText = `
                position: fixed;
                left: ${rect.left + rect.width / 2 - 22}px;
                top: ${rect.top + rect.height / 2 - 22}px;
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: radial-gradient(circle, #ffff00 0%, ${color} 65%, transparent 100%);
                box-shadow: 0 0 30px 12px ${color};
                pointer-events: none;
                z-index: 999998;
                animation: qaLaserPulse 0.45s infinite alternate;
            `;

            // Cria a etiqueta indicando a ação acima do elemento
            const badge = document.createElement('div');
            badge.id = 'qa-laser-badge';
            badge.innerText = labelText;
            badge.style.cssText = `
                position: fixed;
                left: ${Math.max(10, rect.left)}px;
                top: ${Math.max(45, rect.top - 38)}px;
                background: ${color};
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding: 5px 12px;
                border-radius: 6px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.45);
                pointer-events: none;
                z-index: 999999;
            `;

            if (!document.getElementById('qa-laser-style')) {
                const style = document.createElement('style');
                style.id = 'qa-laser-style';
                style.innerHTML = `
                    @keyframes qaLaserPulse {
                        from { transform: scale(0.65); opacity: 1; }
                        to { transform: scale(1.45); opacity: 0.35; }
                    }
                `;
                document.head.appendChild(style);
            }

            document.body.appendChild(pulse);
            document.body.appendChild(badge);
            """,
            elemento,
            texto_etiqueta,
            cor,
        )
    except Exception:
        pass


def remover_luz_do_elemento(driver, elemento):
    """Remove o brilho neon após a ação para limpar a tela."""
    try:
        driver.execute_script(
            """
            const el = arguments[0].tagName === 'OPTION' ? arguments[0].parentElement : arguments[0];
            if (el && el.hasAttribute('data-old-style')) {
                el.setAttribute('style', el.getAttribute('data-old-style'));
                el.removeAttribute('data-old-style');
            }
            const badge = document.getElementById('qa-laser-badge');
            if (badge) badge.remove();
            const pulse = document.getElementById('qa-laser-pulse');
            if (pulse) pulse.remove();
            """,
            elemento,
        )
    except Exception:
        pass


def click_com_luz(self):
    """Substitui o clique padrão por um clique iluminado e pausado."""
    driver = self._parent
    mostrar_luz_no_elemento(driver, self, "CLICANDO AQUI", "#ff0055")
    time.sleep(TEMPO_ANTES_DO_CLIQUE)
    remover_luz_do_elemento(driver, self)
    _click_original(self)
    time.sleep(TEMPO_APOS_ACAO)


def send_keys_com_luz(self, *value):
    """Substitui a digitação padrão por digitação letra a letra iluminada."""
    driver = self._parent
    texto = "".join(str(v) for v in value)
    mostrar_luz_no_elemento(driver, self, f"DIGITANDO: {texto}", "#ff7700")
    time.sleep(0.6)
    for letra in texto:
        _send_keys_original(self, letra)
        time.sleep(VELOCIDADE_DIGITACAO)
    time.sleep(TEMPO_APOS_ACAO * 0.7)
    remover_luz_do_elemento(driver, self)


WebElement.click = click_com_luz
WebElement.send_keys = send_keys_com_luz


class TestSauceDemo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--start-maximized")
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(5)
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.base_url = "https://www.saucedemo.com/"

    @classmethod
    def tearDownClass(cls):
        time.sleep(2)
        cls.driver.quit()

    def setUp(self):
        # Desativa a mensagem técnica curta do Python para exibir apenas a nossa explicação detalhada
        self.longMessage = False
        self.driver.get(self.base_url)
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        self.driver.refresh()
        self.exibir_banner_teste()

    def tearDown(self):
        time.sleep(PAUSA_ENTRE_TESTES)

    def relatorio_falha(self, codigo_ct, cenario, esperado, obtido, diagnostico):
        """Gera um bloco explicativo detalhado no terminal quando um teste falha."""
        return (
            f"\n\n{'=' * 70}\n"
            f"RELATORIO DE FALHA - {codigo_ct}: {cenario}\n"
            f"{'-' * 70}\n"
            f"[RESULTADO ESPERADO]:\n  {esperado}\n\n"
            f"[RESULTADO OBTIDO NA TELA]:\n  {obtido}\n\n"
            f"[DIAGNOSTICO DO PROBLEMA]:\n  {diagnostico}\n"
            f"{'=' * 70}"
        )

    def exibir_banner_teste(self):
        """Mostra uma barra fixa no topo do navegador com o nome do teste atual."""
        nome_teste = self._testMethodName.upper()
        try:
            self.driver.execute_script(
                """
                let banner = document.getElementById('qa-test-banner');
                if (!banner) {
                    banner = document.createElement('div');
                    banner.id = 'qa-test-banner';
                    banner.style.cssText = `
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        background: rgba(15, 23, 42, 0.92);
                        color: #38bdf8;
                        font-family: Consolas, monospace;
                        font-size: 15px;
                        font-weight: bold;
                        text-align: center;
                        padding: 8px 0;
                        z-index: 999997;
                        border-bottom: 2px solid #38bdf8;
                        pointer-events: none;
                    `;
                    document.body.appendChild(banner);
                }
                banner.innerText = 'EXECUTANDO AGORA: ' + arguments[0];
                """,
                nome_teste,
            )
        except Exception:
            pass

    def destacar_validacao(self, elemento, mensagem="VALIDANDO RESULTADO"):
        """Destaca em azul o elemento que está sendo conferido pelo assert."""
        self.exibir_banner_teste()
        mostrar_luz_no_elemento(self.driver, elemento, mensagem, "#00b4d8")
        time.sleep(TEMPO_ANTES_DO_CLIQUE)
        remover_luz_do_elemento(self.driver, elemento)

    def fazer_login(self, usuario, senha="secret_sauce"):
        self.driver.find_element(By.ID, "user-name").send_keys(usuario)
        self.driver.find_element(By.ID, "password").send_keys(senha)
        self.driver.find_element(By.ID, "login-button").click()
        self.exibir_banner_teste()

    # CT_001 - Login com credenciais válidas
    def test_ct001_login_credenciais_validas(self):
        self.fazer_login("standard_user", "secret_sauce")
        self.assertIn(
            "/inventory.html",
            self.driver.current_url,
            self.relatorio_falha(
                "CT_001",
                "Login com credenciais validas",
                "Redirecionar o usuario para a pagina '/inventory.html'.",
                f"O navegador permaneceu na URL '{self.driver.current_url}'.",
                "O login com o usuario padrao 'standard_user' nao redirecionou para o catalogo.",
            ),
        )
        titulo = self.driver.find_element(By.CLASS_NAME, "title")
        self.destacar_validacao(titulo, "VALIDANDO TITULO: Products")
        self.assertEqual(
            titulo.text,
            "Products",
            self.relatorio_falha(
                "CT_001",
                "Login com credenciais validas",
                "Exibir o titulo 'Products' no topo da pagina.",
                f"Foi exibido o titulo '{titulo.text}'.",
                "O cabecalho da pagina de produtos nao corresponde ao esperado.",
            ),
        )
        qtd_produtos = len(self.driver.find_elements(By.CLASS_NAME, "inventory_item"))
        self.assertEqual(
            qtd_produtos,
            6,
            self.relatorio_falha(
                "CT_001",
                "Login com credenciais validas",
                "Listar exatamente 6 produtos no catalogo.",
                f"Foram encontrados {qtd_produtos} produtos na tela.",
                "A quantidade de itens carregados no inventario esta incorreta.",
            ),
        )

    # CT_002 - Login com senha inválida
    def test_ct002_login_senha_invalida(self):
        self.fazer_login("standard_user", "senha_errada")
        erro_el = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        self.destacar_validacao(erro_el, "VALIDANDO MENSAGEM DE ERRO")
        esperado = "Epic sadface: Username and password do not match any user in this service"
        self.assertEqual(
            erro_el.text,
            esperado,
            self.relatorio_falha(
                "CT_002",
                "Login com senha invalida",
                f"Exibir a mensagem de erro: '{esperado}'.",
                f"Mensagem exibida na tela: '{erro_el.text}'.",
                "A validacao de senha incorreta nao exibiu o alerta esperado.",
            ),
        )

    # CT_003 - Login com usuário bloqueado
    def test_ct003_login_usuario_bloqueado(self):
        self.fazer_login("locked_out_user", "secret_sauce")
        erro_el = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        self.destacar_validacao(erro_el, "VALIDANDO BLOQUEIO DE USUARIO")
        esperado = "Epic sadface: Sorry, this user has been locked out."
        self.assertEqual(
            erro_el.text,
            esperado,
            self.relatorio_falha(
                "CT_003",
                "Login com usuario bloqueado",
                f"Impedir o login e exibir: '{esperado}'.",
                f"Mensagem exibida na tela: '{erro_el.text}'.",
                "O sistema nao exibiu a mensagem correta de bloqueio para 'locked_out_user'.",
            ),
        )

    # CT_004 - Login com campos obrigatórios vazios
    def test_ct004_login_campos_obrigatorios_vazios(self):
        self.driver.find_element(By.ID, "login-button").click()
        erro_user = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        self.destacar_validacao(erro_user, "ERRO: USERNAME OBRIGATORIO")
        self.assertEqual(
            erro_user.text,
            "Epic sadface: Username is required",
            self.relatorio_falha(
                "CT_004",
                "Login com campos obrigatorios vazios (Sem Usuario)",
                "Exibir 'Epic sadface: Username is required'.",
                f"Exibiu '{erro_user.text}'.",
                "Falha na validacao de campo Username vazio.",
            ),
        )

        self.driver.find_element(By.ID, "user-name").send_keys("standard_user")
        self.driver.find_element(By.ID, "login-button").click()
        erro_pass = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        self.destacar_validacao(erro_pass, "ERRO: PASSWORD OBRIGATORIO")
        self.assertEqual(
            erro_pass.text,
            "Epic sadface: Password is required",
            self.relatorio_falha(
                "CT_004",
                "Login com campos obrigatorios vazios (Sem Senha)",
                "Exibir 'Epic sadface: Password is required'.",
                f"Exibiu '{erro_pass.text}'.",
                "Falha na validacao de campo Password vazio.",
            ),
        )

    # CT_005 - Logout do sistema
    def test_ct005_logout_sistema(self):
        self.fazer_login("standard_user")
        self.driver.find_element(By.ID, "react-burger-menu-btn").click()
        logout_link = self.wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link")))
        logout_link.click()
        self.assertEqual(
            self.driver.current_url,
            self.base_url,
            self.relatorio_falha(
                "CT_005",
                "Logout do sistema pelo menu lateral",
                f"Retornar para a tela inicial de login ('{self.base_url}').",
                f"Permaneceu na URL '{self.driver.current_url}'.",
                "O clique em Logout nao encerrou a sessao corretamente.",
            ),
        )

    # CT_006 - Ordenar produtos por preço (menor para maior)
    def test_ct006_ordenar_produtos_preco(self):
        self.fazer_login("standard_user")
        seletor = Select(self.driver.find_element(By.CLASS_NAME, "product_sort_container"))
        seletor.select_by_visible_text("Price (low to high)")

        itens = self.driver.find_elements(By.CLASS_NAME, "inventory_item_name")
        precos = self.driver.find_elements(By.CLASS_NAME, "inventory_item_price")
        self.destacar_validacao(itens[0], "MENOR PRECO: $7.99")
        self.destacar_validacao(itens[-1], "MAIOR PRECO: $49.99")

        self.assertEqual(
            itens[0].text,
            "Sauce Labs Onesie",
            self.relatorio_falha(
                "CT_006",
                "Ordenar produtos por preco (menor para maior)",
                "Primeiro item da lista deveria ser 'Sauce Labs Onesie ($7.99)'.",
                f"Primeiro item encontrado foi '{itens[0].text} ({precos[0].text})'.",
                "A ordenacao crescente por preco nao colocou o produto mais barato no topo.",
            ),
        )
        self.assertEqual(precos[0].text, "$7.99")
        self.assertEqual(itens[-1].text, "Sauce Labs Fleece Jacket")
        self.assertEqual(precos[-1].text, "$49.99")

    # CT_007 - Adicionar produto ao carrinho
    def test_ct007_adicionar_produto_carrinho(self):
        self.fazer_login("standard_user")
        self.driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
        badge = self.driver.find_element(By.CLASS_NAME, "shopping_cart_badge")
        self.destacar_validacao(badge, "CONTADOR DO CARRINHO = 1")
        self.assertEqual(
            badge.text,
            "1",
            self.relatorio_falha(
                "CT_007",
                "Adicionar produto ao carrinho",
                "O icone do carrinho deveria exibir o contador '1'.",
                f"O contador exibiu '{badge.text}'.",
                "O contador do carrinho nao atualizou corretamente apos adicionar o produto.",
            ),
        )

        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        item_carrinho = self.driver.find_element(By.CLASS_NAME, "inventory_item_name")
        self.destacar_validacao(item_carrinho, "PRODUTO NO CARRINHO")
        self.assertEqual(
            item_carrinho.text,
            "Sauce Labs Backpack",
            self.relatorio_falha(
                "CT_007",
                "Adicionar produto ao carrinho",
                "Exibir o produto 'Sauce Labs Backpack' dentro de /cart.html.",
                f"Produto encontrado: '{item_carrinho.text}'.",
                "O item adicionado nao corresponde ao produto listado no carrinho.",
            ),
        )

    # CT_008 - Remover produto do carrinho
    def test_ct008_remover_produto_carrinho(self):
        self.fazer_login("standard_user")
        self.driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.driver.find_element(By.ID, "remove-sauce-labs-backpack").click()
        qtd_itens = len(self.driver.find_elements(By.CLASS_NAME, "cart_item"))
        self.assertEqual(
            qtd_itens,
            0,
            self.relatorio_falha(
                "CT_008",
                "Remover produto do carrinho",
                "O carrinho deveria ficar vazio (0 itens) apos clicar em Remove.",
                f"Ainda restaram {qtd_itens} item(ns) no carrinho.",
                "O produto nao foi removido da lista do carrinho.",
            ),
        )

    # CT_009 - Finalizar compra com sucesso
    def test_ct009_finalizar_compra_sucesso(self):
        self.fazer_login("standard_user")
        self.driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.driver.find_element(By.ID, "checkout").click()

        self.driver.find_element(By.ID, "first-name").send_keys("Maria")
        self.driver.find_element(By.ID, "last-name").send_keys("Silva")
        self.driver.find_element(By.ID, "postal-code").send_keys("01310100")
        self.driver.find_element(By.ID, "continue").click()

        total_el = self.driver.find_element(By.CLASS_NAME, "summary_total_label")
        self.destacar_validacao(total_el, "CONFERINDO TOTAL: $32.39")
        self.assertIn(
            "$32.39",
            total_el.text,
            self.relatorio_falha(
                "CT_009",
                "Finalizar compra com sucesso (Resumo de Valores)",
                "Exibir o valor total de 'Total: $32.39' ($29.99 + $2.40 de taxa).",
                f"Valor exibido na tela: '{total_el.text}'.",
                "O calculo do valor total no resumo do pedido esta incorreto.",
            ),
        )

        self.driver.find_element(By.ID, "finish").click()
        header_final = self.driver.find_element(By.CLASS_NAME, "complete-header")
        self.destacar_validacao(header_final, "PEDIDO CONFIRMADO!")
        self.assertEqual(
            header_final.text,
            "Thank you for your order!",
            self.relatorio_falha(
                "CT_009",
                "Finalizar compra com sucesso (Confirmacao)",
                "Exibir a mensagem 'Thank you for your order!'.",
                f"Mensagem exibida: '{header_final.text}'.",
                "A tela final de confirmacao do pedido nao exibiu a mensagem esperada.",
            ),
        )
        self.driver.find_element(By.ID, "back-to-products").click()

    # CT_010 - Checkout com campos obrigatórios vazios
    def test_ct010_checkout_campos_vazios(self):
        self.fazer_login("standard_user")
        self.driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.driver.find_element(By.ID, "checkout").click()

        self.driver.find_element(By.ID, "continue").click()
        erro1 = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        self.destacar_validacao(erro1, "ERRO: FIRST NAME OBRIGATORIO")
        self.assertEqual(
            erro1.text,
            "Error: First Name is required",
            self.relatorio_falha(
                "CT_010",
                "Checkout com campos obrigatorios vazios (First Name)",
                "Exibir 'Error: First Name is required'.",
                f"Exibiu '{erro1.text}'.",
                "Nao validou a obrigatoriedade do campo First Name.",
            ),
        )

        self.driver.find_element(By.ID, "first-name").send_keys("Maria")
        self.driver.find_element(By.ID, "continue").click()
        erro2 = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        self.destacar_validacao(erro2, "ERRO: LAST NAME OBRIGATORIO")
        self.assertEqual(
            erro2.text,
            "Error: Last Name is required",
            self.relatorio_falha(
                "CT_010",
                "Checkout com campos obrigatorios vazios (Last Name)",
                "Exibir 'Error: Last Name is required'.",
                f"Exibiu '{erro2.text}'.",
                "Nao validou a obrigatoriedade do campo Last Name.",
            ),
        )

        self.driver.find_element(By.ID, "last-name").send_keys("Silva")
        self.driver.find_element(By.ID, "continue").click()
        erro3 = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        self.destacar_validacao(erro3, "ERRO: POSTAL CODE OBRIGATORIO")
        self.assertEqual(
            erro3.text,
            "Error: Postal Code is required",
            self.relatorio_falha(
                "CT_010",
                "Checkout com campos obrigatorios vazios (Postal Code)",
                "Exibir 'Error: Postal Code is required'.",
                f"Exibiu '{erro3.text}'.",
                "Nao validou a obrigatoriedade do campo Postal Code.",
            ),
        )

    # CT_011 - Ordenar produtos por preço com problem_user (Bug esperado)
    def test_ct011_ordenar_preco_problem_user(self):
        self.fazer_login("problem_user")
        seletor = Select(self.driver.find_element(By.CLASS_NAME, "product_sort_container"))
        seletor.select_by_visible_text("Price (low to high)")
        primeiro_item = self.driver.find_elements(By.CLASS_NAME, "inventory_item_name")[0]
        primeiro_preco = self.driver.find_elements(By.CLASS_NAME, "inventory_item_price")[0]
        self.destacar_validacao(primeiro_item, "BUG: LISTA NAO ORDENOU!")

        self.assertEqual(
            primeiro_item.text,
            "Sauce Labs Onesie",
            self.relatorio_falha(
                "CT_011",
                "Ordenar produtos por preco (menor para maior) com problem_user",
                "O 1o produto da lista deveria ser 'Sauce Labs Onesie' custando '$7.99'.",
                f"O 1o produto da lista continuou sendo '{primeiro_item.text}' custando '{primeiro_preco.text}'.",
                "Ao selecionar 'Price (low to high)', a lista nao e reordenada e permanece na ordem original. A ordenacao por preco nao funciona para o usuario 'problem_user'.",
            ),
        )

    # CT_012 - Exibição das imagens com problem_user (Bug esperado)
    def test_ct012_imagens_problem_user(self):
        self.fazer_login("problem_user")
        elementos_img = self.driver.find_elements(By.CSS_SELECTOR, "img.inventory_item_img")
        for i, img in enumerate(elementos_img[:3], start=1):
            self.destacar_validacao(img, f"BUG: IMAGEM REPETIDA ({i})")

        imagens = [img.get_attribute("src") for img in elementos_img]
        qtd_imagens_unicas = len(set(imagens))
        exemplo_src = imagens[0].split("/")[-1] if imagens else "N/A"

        self.assertEqual(
            qtd_imagens_unicas,
            6,
            self.relatorio_falha(
                "CT_012",
                "Exibicao das imagens dos produtos com problem_user",
                "Os 6 produtos do catalogo deveriam exibir 6 imagens distintas (uma correspondente a cada item).",
                f"Foram encontradas apenas {qtd_imagens_unicas} imagem(ns) unica(s) para todos os 6 produtos (arquivo repetido: '{exemplo_src}').",
                "Todos os 6 produtos exibem exatamente a mesma foto (imagem de um cachorro) no lugar das fotos reais de cada produto para o usuario 'problem_user'.",
            ),
        )

    # CT_013 - Checkout com problem_user (Bug esperado)
    def test_ct013_checkout_problem_user(self):
        self.fazer_login("problem_user")
        self.driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.driver.find_element(By.ID, "checkout").click()

        self.driver.find_element(By.ID, "first-name").send_keys("Maria")
        self.driver.find_element(By.ID, "last-name").send_keys("Silva")
        self.driver.find_element(By.ID, "postal-code").send_keys("01310100")

        campo_nome = self.driver.find_element(By.ID, "first-name")
        campo_sobrenome = self.driver.find_element(By.ID, "last-name")
        valor_nome = campo_nome.get_attribute("value")
        valor_sobrenome = campo_sobrenome.get_attribute("value")

        self.destacar_validacao(campo_sobrenome, "BUG: SOBRENOME FICOU VAZIO!")
        self.driver.find_element(By.ID, "continue").click()

        erros_tela = self.driver.find_elements(By.CSS_SELECTOR, "[data-test='error']")
        msg_erro_tela = erros_tela[0].text if erros_tela else "Sem mensagem de erro"

        self.assertIn(
            "/checkout-step-two.html",
            self.driver.current_url,
            self.relatorio_falha(
                "CT_013",
                "Checkout com usuario problem_user",
                "Manter First Name='Maria' e Last Name='Silva', e avancar para '/checkout-step-two.html'.",
                f"First Name ficou com '{valor_nome}', Last Name ficou '{valor_sobrenome}' (vazio), a URL permaneceu em '{self.driver.current_url}' e exibiu o erro '{msg_erro_tela}'.",
                "O campo Last Name nao aceita digitacao no usuario 'problem_user' (o sobrenome digitado sobrescreve o campo First Name), impedindo o avanco para o resumo do pedido.",
            ),
        )

    # CT_014 - Login com performance_glitch_user
    def test_ct014_login_performance_glitch_user(self):
        self.fazer_login("performance_glitch_user")
        self.assertIn(
            "/inventory.html",
            self.driver.current_url,
            self.relatorio_falha(
                "CT_014",
                "Login com usuario performance_glitch_user",
                "Concluir o login (mesmo com atraso de resposta) e redirecionar para '/inventory.html'.",
                f"O navegador permaneceu em '{self.driver.current_url}'.",
                "O atraso de resposta do usuario 'performance_glitch_user' impediu o carregamento da lista de produtos.",
            ),
        )
        self.assertEqual(len(self.driver.find_elements(By.CLASS_NAME, "inventory_item")), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)