"""
Estruturas de Dados
Tema 2: Plataforma de Comércio Eletrônico
Aluno: Victor Gabriel Marques (252-000599)

Estruturas e seus papéis no sistema:
  - Lista  (list)  : catálogo geral de produtos ativos
  - Fila   (deque) : ordem de processamento e aprovação de pagamentos (FIFO)
  - Pilha  (list)  : histórico de navegação do cliente (LIFO)
  - Árvore (dict)  : departamentos > categorias > subcategorias (dicionários aninhados)

Persistência: um único arquivo texto (dados_sistema.txt), uma linha por registro,
iniciada pelo identificador da estrutura e com campos separados por "|".
"""

from collections import deque
import os

ARQUIVO = "dados_sistema.txt"
SEP = "|"

# ---------------------------------------------------------------------------
# Estruturas em memória (o sistema inicia totalmente vazio)
# ---------------------------------------------------------------------------
catalogo = []        # LISTA: [{"id", "nome", "preco", "estoque", "categoria"}]
pagamentos = deque() # FILA:  [{"id", "cliente", "valor", "metodo"}]
historico = []       # PILHA: topo = último elemento [{"id", "nome"}]
arvore = {}          # ÁRVORE: {"Departamento": {"Categoria": {"Subcategoria": {}}}}

# Contador de pagamentos (evita reutilizar códigos de pagamentos já processados)
contadores = {"pagamento": 0}


# ---------------------------------------------------------------------------
# Funções utilitárias de entrada
# ---------------------------------------------------------------------------
def limpar(texto):
    """Remove o delimitador e quebras de linha para não corromper o arquivo."""
    return texto.replace(SEP, "/").replace("\n", " ").replace("\r", " ").strip()


def ler_texto(msg, obrigatorio=True, atual=None):
    """Lê texto. Se 'atual' for informado, Enter mantém o valor atual."""
    while True:
        sufixo = f" [{atual}]" if atual is not None else ""
        valor = limpar(input(f"{msg}{sufixo}: "))
        if valor:
            return valor
        if atual is not None:
            return atual
        if not obrigatorio:
            return ""
        print("  Valor obrigatório.")


def ler_int(msg, atual=None, minimo=0):
    while True:
        sufixo = f" [{atual}]" if atual is not None else ""
        bruto = input(f"{msg}{sufixo}: ").strip()
        if not bruto and atual is not None:
            return atual
        try:
            valor = int(bruto)
            if valor < minimo:
                print(f"  Informe um número inteiro >= {minimo}.")
                continue
            return valor
        except ValueError:
            print("  Informe um número inteiro válido.")


def ler_float(msg, atual=None):
    while True:
        sufixo = f" [{atual:.2f}]" if atual is not None else ""
        bruto = input(f"{msg}{sufixo}: ").strip().replace(",", ".")
        if not bruto and atual is not None:
            return atual
        try:
            valor = float(bruto)
            if valor < 0:
                print("  O valor não pode ser negativo.")
                continue
            return valor
        except ValueError:
            print("  Informe um número válido (ex.: 59.90).")


def proximo_id(itens):
    """Gera o próximo código numérico a partir dos itens existentes."""
    return max((i["id"] for i in itens), default=0) + 1


def buscar_por_id(itens, codigo):
    for item in itens:
        if item["id"] == codigo:
            return item
    return None


# ---------------------------------------------------------------------------
# LISTA - Catálogo de produtos (acesso por chave/índice)
# ---------------------------------------------------------------------------
def cadastrar_produto():
    produto = {
        "id": proximo_id(catalogo),
        "nome": ler_texto("Nome do produto"),
        "preco": ler_float("Preço (R$)"),
        "estoque": ler_int("Quantidade em estoque"),
        "categoria": ler_texto("Categoria (ex.: Eletrônicos/Celulares)"),
    }
    catalogo.append(produto)
    print(f"  Produto cadastrado com código {produto['id']}.")


def listar_produtos():
    if not catalogo:
        print("  Catálogo vazio.")
        return
    print(f"  {'COD':<5}{'NOME':<28}{'PREÇO':>10}{'ESTOQUE':>9}  CATEGORIA")
    for i, p in enumerate(catalogo):
        print(f"  {p['id']:<5}{p['nome']:<28}{p['preco']:>10.2f}{p['estoque']:>9}  {p['categoria']}")
    print(f"  Total: {len(catalogo)} produto(s).")


def buscar_produto():
    termo = input("Código ou parte do nome: ").strip().lower()
    achados = [p for p in catalogo if termo == str(p["id"]) or termo in p["nome"].lower()]
    if not achados:
        print("  Nenhum produto encontrado.")
        return
    for p in achados:
        print(f"  [{p['id']}] {p['nome']} - R$ {p['preco']:.2f} - estoque {p['estoque']} - {p['categoria']}")


def atualizar_produto():
    produto = buscar_por_id(catalogo, ler_int("Código do produto a atualizar", minimo=1))
    if produto is None:
        print("  Produto não encontrado.")
        return
    print("  (Enter mantém o valor atual)")
    produto["nome"] = ler_texto("Nome", atual=produto["nome"])
    produto["preco"] = ler_float("Preço (R$)", atual=produto["preco"])
    produto["estoque"] = ler_int("Estoque", atual=produto["estoque"])
    produto["categoria"] = ler_texto("Categoria", atual=produto["categoria"])
    print("  Produto atualizado.")


def remover_produto():
    produto = buscar_por_id(catalogo, ler_int("Código do produto a remover", minimo=1))
    if produto is None:
        print("  Produto não encontrado.")
        return
    catalogo.remove(produto)
    print(f"  Produto '{produto['nome']}' removido do catálogo.")


def menu_catalogo():
    opcoes = {
        "1": ("Cadastrar produto", cadastrar_produto),
        "2": ("Listar produtos", listar_produtos),
        "3": ("Buscar produto", buscar_produto),
        "4": ("Atualizar produto", atualizar_produto),
        "5": ("Remover produto", remover_produto),
    }
    submenu("CATÁLOGO DE PRODUTOS (LISTA)", opcoes)


# ---------------------------------------------------------------------------
# FILA - Pagamentos (FIFO: entra no fim, sai do início)
# ---------------------------------------------------------------------------
def enfileirar_pagamento():
    contadores["pagamento"] += 1
    pagamento = {
        "id": contadores["pagamento"],
        "cliente": ler_texto("Nome do cliente"),
        "valor": ler_float("Valor do pagamento (R$)"),
        "metodo": ler_texto("Método (Cartão/Pix/Boleto)"),
    }
    pagamentos.append(pagamento)  # inserção sempre no FIM da fila
    print(f"  Pagamento {pagamento['id']} na fila (posição {len(pagamentos)}).")


def listar_pagamentos():
    if not pagamentos:
        print("  Fila de pagamentos vazia.")
        return
    print(f"  {'POS':<5}{'COD':<6}{'CLIENTE':<24}{'VALOR':>10}  MÉTODO")
    for pos, p in enumerate(pagamentos, start=1):
        print(f"  {pos:<5}{p['id']:<6}{p['cliente']:<24}{p['valor']:>10.2f}  {p['metodo']}")


def ver_proximo_pagamento():
    if not pagamentos:
        print("  Fila de pagamentos vazia.")
        return
    p = pagamentos[0]  # consulta o início sem remover
    print(f"  Próximo a processar: [{p['id']}] {p['cliente']} - R$ {p['valor']:.2f} ({p['metodo']})")


def atualizar_pagamento():
    """Altera os dados de um pagamento pendente sem mudar sua posição na fila."""
    p = buscar_por_id(pagamentos, ler_int("Código do pagamento a atualizar", minimo=1))
    if p is None:
        print("  Pagamento não encontrado na fila.")
        return
    print("  (Enter mantém o valor atual)")
    p["cliente"] = ler_texto("Cliente", atual=p["cliente"])
    p["valor"] = ler_float("Valor (R$)", atual=p["valor"])
    p["metodo"] = ler_texto("Método", atual=p["metodo"])
    print("  Pagamento atualizado (posição na fila mantida).")


def processar_pagamento():
    if not pagamentos:
        print("  Fila de pagamentos vazia.")
        return
    p = pagamentos.popleft()  # remoção sempre no INÍCIO da fila
    print(f"  Pagamento {p['id']} de {p['cliente']} (R$ {p['valor']:.2f}) APROVADO e removido da fila.")


def menu_pagamentos():
    opcoes = {
        "1": ("Enfileirar novo pagamento", enfileirar_pagamento),
        "2": ("Listar fila de pagamentos", listar_pagamentos),
        "3": ("Ver próximo pagamento", ver_proximo_pagamento),
        "4": ("Atualizar dados de um pagamento", atualizar_pagamento),
        "5": ("Processar/aprovar próximo (remove do início)", processar_pagamento),
    }
    submenu("PAGAMENTOS (FILA)", opcoes)


# ---------------------------------------------------------------------------
# PILHA - Histórico de navegação (LIFO: empilha e desempilha no topo)
# ---------------------------------------------------------------------------
def registrar_visita():
    produto = buscar_por_id(catalogo, ler_int("Código do produto visitado", minimo=1))
    if produto is None:
        print("  Produto não encontrado no catálogo.")
        return
    historico.append({"id": produto["id"], "nome": produto["nome"]})  # push no topo
    print(f"  Visita a '{produto['nome']}' registrada no topo do histórico.")


def listar_historico():
    if not historico:
        print("  Histórico vazio.")
        return
    print("  Do topo (mais recente) para a base:")
    for pos, item in enumerate(reversed(historico), start=1):
        marca = "  <- topo" if pos == 1 else ""
        print(f"  {pos}. [{item['id']}] {item['nome']}{marca}")


def ver_topo_historico():
    if not historico:
        print("  Histórico vazio.")
        return
    topo = historico[-1]
    print(f"  Topo: [{topo['id']}] {topo['nome']}")


def atualizar_topo_historico():
    """Na pilha só o topo é acessível: atualiza o item do topo por outro produto."""
    if not historico:
        print("  Histórico vazio.")
        return
    produto = buscar_por_id(catalogo, ler_int("Código do novo produto para o topo", minimo=1))
    if produto is None:
        print("  Produto não encontrado no catálogo.")
        return
    historico[-1] = {"id": produto["id"], "nome": produto["nome"]}
    print("  Topo do histórico atualizado.")


def voltar_pagina():
    if not historico:
        print("  Histórico vazio.")
        return
    removido = historico.pop()  # pop do topo
    print(f"  Voltou: '{removido['nome']}' saiu do topo do histórico.")


def menu_historico():
    opcoes = {
        "1": ("Registrar visita a produto (empilhar)", registrar_visita),
        "2": ("Listar histórico", listar_historico),
        "3": ("Ver topo", ver_topo_historico),
        "4": ("Atualizar topo", atualizar_topo_historico),
        "5": ("Voltar (desempilhar topo)", voltar_pagina),
    }
    submenu("HISTÓRICO DE NAVEGAÇÃO (PILHA)", opcoes)


# ---------------------------------------------------------------------------
# ÁRVORE - Departamentos, categorias e subcategorias (dicionários aninhados)
# ---------------------------------------------------------------------------
def ler_caminho(msg, permitir_vazio=False):
    """Converte 'A/B/C' em ['A', 'B', 'C']."""
    bruto = input(f"{msg}: ").strip()
    partes = [limpar(p) for p in bruto.split("/") if p.strip()]
    if not partes and not permitir_vazio:
        print("  Caminho obrigatório.")
    return partes


def obter_no(caminho):
    """Desce na árvore seguindo o caminho; devolve o dicionário do nó ou None."""
    no = arvore
    for nome in caminho:
        if nome not in no:
            return None
        no = no[nome]
    return no


def adicionar_no():
    pai = ler_caminho("Caminho do nó pai (vazio = criar departamento na raiz)", permitir_vazio=True)
    destino = obter_no(pai)
    if destino is None:
        print("  Caminho do pai não existe.")
        return
    nome = ler_texto("Nome do novo nó")
    if nome in destino:
        print("  Já existe um nó com esse nome nesse nível.")
        return
    destino[nome] = {}
    print(f"  Nó '{nome}' inserido em '{'/'.join(pai) if pai else 'raiz'}'.")


def exibir_arvore_rec(no, nivel=0):
    for nome, filhos in no.items():
        print("  " + "    " * nivel + ("└── " if nivel else "") + nome)
        exibir_arvore_rec(filhos, nivel + 1)


def exibir_arvore():
    if not arvore:
        print("  Árvore de departamentos vazia.")
        return
    print("  [Loja]")
    exibir_arvore_rec(arvore, 1)


def renomear_no():
    caminho = ler_caminho("Caminho do nó a renomear (ex.: Eletrônicos/Celulares)")
    if not caminho:
        return
    pai = obter_no(caminho[:-1])
    if pai is None or caminho[-1] not in pai:
        print("  Nó não encontrado.")
        return
    antigo = caminho[-1]
    novo = ler_texto("Novo nome")
    if novo != antigo and novo in pai:
        print("  Já existe um nó com esse nome nesse nível.")
        return
    itens = list(pai.items())  # reconstrói mantendo a ordem dos irmãos
    pai.clear()
    for chave, valor in itens:
        pai[novo if chave == antigo else chave] = valor
    print(f"  '{antigo}' renomeado para '{novo}'.")


def remover_no():
    caminho = ler_caminho("Caminho do nó a remover")
    if not caminho:
        return
    pai = obter_no(caminho[:-1])
    if pai is None or caminho[-1] not in pai:
        print("  Nó não encontrado.")
        return
    if pai[caminho[-1]]:
        conf = input("  O nó possui subcategorias que também serão removidas. Confirmar (s/n)? ").strip().lower()
        if conf != "s":
            print("  Operação cancelada.")
            return
    del pai[caminho[-1]]
    print(f"  Nó '{caminho[-1]}' removido.")


def menu_arvore():
    opcoes = {
        "1": ("Adicionar departamento/categoria/subcategoria", adicionar_no),
        "2": ("Exibir hierarquia", exibir_arvore),
        "3": ("Renomear nó", renomear_no),
        "4": ("Remover nó", remover_no),
    }
    submenu("DEPARTAMENTOS E CATEGORIAS (ÁRVORE)", opcoes)


# ---------------------------------------------------------------------------
# PERSISTÊNCIA em arquivo texto (LISTA|..., FILA|..., PILHA|..., ARVORE|...)
# ---------------------------------------------------------------------------
def caminhos_da_arvore(no, prefixo=()):
    """Gera o caminho completo de cada nó (pais antes dos filhos)."""
    for nome, filhos in no.items():
        caminho = prefixo + (nome,)
        yield caminho
        yield from caminhos_da_arvore(filhos, caminho)


def salvar_dados():
    try:
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            for p in catalogo:
                f.write(SEP.join(["LISTA", str(p["id"]), p["nome"], f"{p['preco']:.2f}",
                                  str(p["estoque"]), p["categoria"]]) + "\n")
            for p in pagamentos:  # do início para o fim da fila
                f.write(SEP.join(["FILA", str(p["id"]), p["cliente"], f"{p['valor']:.2f}",
                                  p["metodo"]]) + "\n")
            for item in historico:  # da base para o topo da pilha
                f.write(SEP.join(["PILHA", str(item["id"]), item["nome"]]) + "\n")
            for caminho in caminhos_da_arvore(arvore):
                f.write(SEP.join(["ARVORE"] + list(caminho)) + "\n")
        print(f"  Dados salvos em '{ARQUIVO}'.")
    except OSError as erro:
        print(f"  Erro ao salvar: {erro}")


def carregar_dados():
    if not os.path.exists(ARQUIVO):
        print(f"  Arquivo '{ARQUIVO}' não encontrado. Salve os dados primeiro.")
        return
    novo_catalogo, nova_fila, nova_pilha, nova_arvore = [], deque(), [], {}
    ignoradas = 0
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            for linha in f:
                campos = linha.rstrip("\n").split(SEP)
                tipo = campos[0]
                try:
                    if tipo == "LISTA" and len(campos) == 6:
                        novo_catalogo.append({"id": int(campos[1]), "nome": campos[2],
                                              "preco": float(campos[3]),
                                              "estoque": int(campos[4]), "categoria": campos[5]})
                    elif tipo == "FILA" and len(campos) == 5:
                        nova_fila.append({"id": int(campos[1]), "cliente": campos[2],
                                          "valor": float(campos[3]), "metodo": campos[4]})
                    elif tipo == "PILHA" and len(campos) == 3:
                        nova_pilha.append({"id": int(campos[1]), "nome": campos[2]})
                    elif tipo == "ARVORE" and len(campos) >= 2:
                        no = nova_arvore
                        for nome in campos[1:]:
                            no = no.setdefault(nome, {})
                    elif linha.strip():
                        ignoradas += 1
                except ValueError:
                    ignoradas += 1
    except OSError as erro:
        print(f"  Erro ao carregar: {erro}")
        return

    # Substitui o estado em memória pelo estado lido do disco
    catalogo[:] = novo_catalogo
    pagamentos.clear()
    pagamentos.extend(nova_fila)
    historico[:] = nova_pilha
    arvore.clear()
    arvore.update(nova_arvore)
    contadores["pagamento"] = max((p["id"] for p in pagamentos), default=0)
    print(f"  Dados carregados de '{ARQUIVO}'.")
    if ignoradas:
        print(f"  Atenção: {ignoradas} linha(s) inválida(s) foram ignoradas.")


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------
def submenu(titulo, opcoes):
    while True:
        print(f"\n=== {titulo} ===")
        for chave, (rotulo, _) in opcoes.items():
            print(f"  {chave} - {rotulo}")
        print("  0 - Voltar ao menu principal")
        escolha = input("Opção: ").strip()
        if escolha == "0":
            return
        if escolha in opcoes:
            print()
            opcoes[escolha][1]()
        else:
            print("  Opção inválida.")


def menu_principal():
    opcoes = {
        "1": ("Catálogo de produtos (Lista)", menu_catalogo),
        "2": ("Pagamentos (Fila)", menu_pagamentos),
        "3": ("Histórico de navegação (Pilha)", menu_historico),
        "4": ("Departamentos e categorias (Árvore)", menu_arvore),
        "5": ("Salvar dados", salvar_dados),
        "6": ("Carregar dados", carregar_dados),
    }
    while True:
        print("\n===== PLATAFORMA DE COMÉRCIO ELETRÔNICO =====")
        for chave, (rotulo, _) in opcoes.items():
            print(f"  {chave} - {rotulo}")
        print("  0 - Sair")
        escolha = input("Opção: ").strip()
        if escolha == "0":
            print("Encerrando. Dados não salvos serão perdidos.")
            break
        if escolha in opcoes:
            opcoes[escolha][1]()
        else:
            print("  Opção inválida.")


if __name__ == "__main__":
    menu_principal()
