# Sistema de Gestão para Oficina Mecânica

Este é um sistema de gerenciamento para oficinas mecânicas desenvolvido com **Flask** e **MySQL**, com o objetivo de organizar clientes, veículos, ordens de serviço e mecânicos, além de gerenciar as atividades de cada área do sistema. Com este sistema, é possível realizar operações de cadastro, edição, exclusão e visualização.

## Funcionalidades

- **Autenticação de Usuário**: Login seguro com senha.
- **Dashboard**: Tela inicial com visão geral e a exibição da data e hora atuais.
- **Gestão de Clientes**: Adicionar, editar e remover dados de clientes.
- **Gestão de Carros**: Cadastrar, editar e excluir veículos, com vinculação a clientes.
- **Gestão de Mecânicos**: Registrar, editar e excluir mecânicos.
- **Ordens de Serviço**: Criar, editar, finalizar e excluir ordens de serviço, com detalhes sobre o problema, peças utilizadas e mecânico responsável.

## Estrutura do Projeto

- `app.py`: Arquivo principal que define as rotas e lógica de backend do Flask.
- `templates/`: Pasta com os templates HTML para as páginas de interface.
  - `base.html`: Layout principal para as páginas do sistema, incluindo a barra de navegação lateral.
  - `dashboard.html`: Página de boas-vindas e visão geral.
  - `clientes.html`, `carros.html`, `mecanicos.html`, `ordens_servico.html`: Páginas principais para gestão de clientes, carros, mecânicos e ordens de serviço.
  - `editar_cliente.html`, `editar_carro.html`, `editar_mecanico.html`, `editar_ordem_servico.html`: Formulários para editar registros específicos.
  - `login.html`, `register.html`: Páginas de autenticação para login e registro de usuários.
- `static/`: Pasta com arquivos CSS e JavaScript personalizados.
- `config.py`: Configuração de banco de dados e outras variáveis sensíveis.

## Tecnologias Utilizadas

- **Flask** - Framework para desenvolvimento web em Python.
- **MySQL** - Banco de dados relacional para armazenar os dados.
- **HTML5, CSS3 e JavaScript** - Estrutura e estilo das páginas.
- **Bootstrap** - Framework CSS para layout responsivo.
- **Font Awesome** - Biblioteca de ícones.

## Como Usar

### Navegação

- **Dashboard**: Tela inicial com data e hora.
- **Clientes**: Visualize, adicione, edite e remova clientes.
- **Carros**: Gerencie os carros cadastrados, associando-os a clientes.
- **Mecânicos**: Cadastre mecânicos para atender ordens de serviço.
- **Ordens de Serviço**: Crie, edite e finalize ordens de serviço.

### Ações

- **Adicionar**: Acesse a página de cada seção e use o formulário para cadastrar novos dados.
- **Editar**: Use os botões de edição para modificar registros existentes.
- **Excluir**: Clique em excluir para remover um registro.
- **Autenticação**: Use a página de login para entrar no sistema e a página de cadastro para criar novos usuários.

## Estrutura das Páginas

### `clientes.html` e `editar_cliente.html`
- Permitem cadastrar novos clientes e editar informações como nome, contato e endereço.

### `carros.html` e `editar_carro.html`
- Permitem o cadastro de veículos com placa, modelo, ano e vínculo com um cliente existente.

### `mecanicos.html` e `editar_mecanico.html`
- Permitem a adição de mecânicos e a edição de dados como nome do mecânico.

### `ordens_servico.html` e `editar_ordem_servico.html`
- Exibem uma lista das ordens de serviço em aberto e finalizadas, com a possibilidade de editar as ordens e vincular a um mecânico e veículo específico.