# Setup

Este documento descreve os passos necessários para executar o sistema.


## Instalar o Docker e Docker-compose

Nos links abaixo são descritos os passos necessários para baixar os dois para
diferentes sistemas operacionais.

* https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce
* https://docs.docker.com/compose/install/


## Configurar API de geolocation

A API utilizada no projeto foi a API do Google.
Para utilizá-la é preciso configurar um token de utilização, para isso execute
os seguintes passos:

1. Acessar o seguinte link: https://console.developers.google.com/apis/dashboard;
2. Criar um projeto;
3. Acessar o projeto;
4. Clicar na opção do menu "Painel";
5. Clicar em "ATIVAR APIS E SERVIÇOS";
6. Buscar por "Geocoding API" e ativá-la;
7. Acessar a Geocoding API que foi adicionada e clicar na aba "Credenciais";
8. Cadastrar uma nova chave;
9. Modificar a configuração `GEO_LOCATION_API_KEY` no arquivo
`/processor/settings.py` para utilizar o token gerado.

> OBS: Para fins de teste, foi implementada uma forma de não conectar à API
quando a variável `GEO_LOCATION_SERVICE_ENABLED` estiver como `False`.
A variável encontra-se no arquivo `/processor/settings.py`.

## Configurações gerais

Algumas configurações precisam ser definidas no momento em que o serviço é
executado (`docker-compose.yml`) e outras quando o client do serviço vai ser
criado(`settings.py`).


# Como executar o projeto

## Iniciar o sistema

Para iniciar o sistema é preciso executar o seguinte comando:

`docker-compose up --build`


## Acessar as filas do RabbitMQ

No admin do Rabbitmq é possível ver a quantidade de logs produzidos, a
quantida de logs processados e a quantidade de logs que foi produzido e ainda
não foi processado.

1. Entrar no seguinte link: `localhost:15672`
2. Clicar na aba "Queues"
3. Escolher a fila de nome "logs"


## Acessar as informações armazenadas

As inforamções estão sendo armazenadas no MySQL do serviço `storage`.
O serviço `storage-adminer` fornece uma interface WEB para acessar o banco de dados.
Para isso, podemos utilizar os seguintes passos:

1. Acessar a URL: `localhost:8080`
2. Inserir as seguintes informações na tela de login:
    - Sistema: MySQL
    - Servidor: storage
    - Usuário: root
    - Senha: 12345
    - Base de Dados: db

> OBS: As credenciais de acesso ao banco podem ser configuradas no arquivo
`docker-compose.yml`


# Como escalar o processamento

O projeto foi criado utilizando a arquitetura de containers visando facilitar
a escalabilidade desejada.
Para isso, quando necessário podemos criar mais instâncias dos serviços através
do seguinte comando:

`docker-compose scale collector=5 processor=10`


# Análises que podem ser feitas

## Métricas

* Quantidade logs gerados por minuto/segundo
* Total de logs gerados
* Quantidade de logs processados por minuto/segundo
* Total de logs processados
* Tempo que leva desde a coleta do log até ele ser armazenado (latência)
* Quantidade de logs que estão esperando serem processados no RabbitMQ (lag)
* Uptime dos serviços

## Análises

* Regiões com maior quantidade de acessos
* Frequência que os dispositivos constumam se conectar
