# Plataforma de Comércio Eletrônico (Estruturas de Dados)

**Aluno:** Victor Gabriel Marques (252-000599)
**Tema sorteado:** Tema 2: Plataforma de Comércio Eletrônico
**Linguagem:** Python 3 (somente biblioteca padrão)

Sistema de terminal (CLI) que integra quatro estruturas de dados (Lista, Fila, Pilha e Árvore) e persiste o estado em um arquivo texto.

## 1. Como executar

Requisitos: Python 3.8 ou superior. Não há dependências externas.

1. Coloque o arquivo `main.py` em uma pasta.
2. Abra o terminal nessa pasta.
3. Execute:

```bash
python main.py
```

O sistema inicia **totalmente vazio**. Navegue pelo menu digitando o número da opção e pressionando Enter.

### Fluxo sugerido (caminho feliz)

1. Menu **4**: crie departamentos e categorias (ex.: raiz `Eletrônicos`, depois pai `Eletrônicos` com filho `Celulares`).
2. Menu **1**: cadastre produtos no catálogo.
3. Menu **3**: registre visitas a produtos (histórico de navegação).
4. Menu **2**: enfileire pagamentos e processe o próximo da fila.
5. Menu **5**: **Salvar dados** (gera `dados_sistema.txt` na mesma pasta).
6. Feche e abra novamente o programa, depois use o menu **6**: **Carregar dados**.

Observação: os dados só vão para o disco ao escolher **Salvar dados**. Sair sem salvar descarta o que está em memória.

## 2. Menu e operações

| Menu | Estrutura | Operações |
|---|---|---|
| 1 | Lista (catálogo) | cadastrar, listar, buscar, atualizar e remover produto por código |
| 2 | Fila (pagamentos) | enfileirar (fim), listar, ver próximo, atualizar dados, processar/aprovar (remove do início) |
| 3 | Pilha (histórico) | registrar visita (push), listar, ver topo, atualizar topo, voltar (pop) |
| 4 | Árvore (departamentos) | adicionar nó, exibir hierarquia, renomear, remover |
| 5 | Persistência | salvar dados |
| 6 | Persistência | carregar dados |

Na árvore, os nós são indicados por caminho separado por barra, por exemplo `Eletrônicos/Celulares`.

## 3. Justificativa técnica das estruturas

### Lista: catálogo geral de produtos

O catálogo precisa de inclusão, consulta, alteração e remoção de qualquer item, a qualquer momento, sem ordem de acesso imposta. A `list` do Python é dinâmica (cresce e encolhe conforme os produtos entram e saem) e permite percorrer e localizar elementos por código ou índice, o que atende o acesso arbitrário que um catálogo exige. Uma fila ou pilha seriam inadequadas aqui, pois só permitem acesso às extremidades.

### Fila: processamento e aprovação de pagamentos

Pagamentos devem ser tratados na ordem em que chegam, sem furar a vez de ninguém, o que é exatamente a política FIFO. O sistema usa `collections.deque`: `append` insere no fim e `popleft` remove do início, ambos em tempo O(1). Uma `list` comum teria custo O(n) na remoção do primeiro elemento, porque todos os demais precisariam ser deslocados. A fila garante justiça e previsibilidade no processamento.

### Pilha: histórico de navegação do cliente

O botão "voltar" de uma loja online sempre retorna à página mais recente, depois à anterior, e assim por diante, comportamento LIFO. A pilha é implementada com `list`: `append` empilha no topo e `pop` desempilha do topo, ambos O(1). Só o topo é acessível, o que reflete o uso real do histórico. Por isso a atualização na pilha altera apenas o item do topo.

### Árvore: departamentos, categorias e subcategorias

A organização de uma loja é naturalmente hierárquica (departamento contém categorias, que contêm subcategorias), com profundidade variável. Como o Python não tem árvore nativa, ela é representada por **dicionários aninhados**, em que cada chave é um nó e seu valor é o dicionário dos filhos:

```python
{"Eletrônicos": {"Celulares": {"Smartphones": {}}, "Notebooks": {}}}
```

Essa representação permite descer diretamente a um nó pelo caminho, inserir filhos em qualquer nível e remover um ramo inteiro com uma única operação. Uma lista simples não expressaria a relação pai e filho sem duplicar informação.

## 4. Formato do arquivo de persistência (`dados_sistema.txt`)

Arquivo texto único, uma linha por registro, iniciada pelo identificador da estrutura e com campos separados por `|`. O caractere `|` digitado pelo usuário é substituído por `/` para não corromper o arquivo. Não há uso de JSON, CSV, pickle ou banco de dados.

```
LISTA|codigo|nome|preco|estoque|categoria
FILA|codigo|cliente|valor|metodo
PILHA|codigo_produto|nome_produto
ARVORE|Departamento|Categoria|Subcategoria
```

Exemplo:

```
LISTA|1|Smartphone X|1999.90|15|Eletrônicos/Celulares
LISTA|2|Notebook Y|3499.00|7|Eletrônicos/Notebooks
FILA|1|Maria Souza|1999.90|Pix
FILA|2|João Lima|3499.00|Cartão
PILHA|1|Smartphone X
PILHA|2|Notebook Y
ARVORE|Eletrônicos
ARVORE|Eletrônicos|Celulares
ARVORE|Eletrônicos|Notebooks
```

Regras de gravação e leitura:

- **Fila:** gravada do início para o fim, para que a ordem de atendimento seja restaurada.
- **Pilha:** gravada da base para o topo, de modo que o último registro lido volte a ser o topo.
- **Árvore:** cada nó é gravado com seu caminho completo (pais antes dos filhos), o que preserva até nós sem filhos.
- **Carregar dados** substitui todo o estado em memória pelo conteúdo do arquivo e ignora, com aviso, linhas malformadas.

## 5. Estrutura do código (`main.py`)

O projeto está em arquivo único, dividido em blocos de funções: utilitários de entrada, operações de cada estrutura (Lista, Fila, Pilha e Árvore), persistência (`salvar_dados` e `carregar_dados`) e menus (`submenu` e `menu_principal`).
