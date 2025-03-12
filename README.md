# Sistema de Monitoramento por Câmera

Este repositório contém um sistema completo para monitoramento de câmeras, com componentes para captura, sincronização em nuvem e visualização de vídeos.

## Estrutura do Projeto

O projeto está organizado em duas pastas principais:

### 1. `sync_video_s3`

Esta pasta contém a aplicação responsável pela captura e sincronização dos vídeos da câmera com o Amazon S3.

**Principais características:**
- Captura de vídeo a partir de uma fonte RTSP
- Armazenamento temporário em segmentos de vídeo
- Upload automático dos segmentos para o Amazon S3
- Tratamento de falhas e reconexão
- Configuração via arquivo .env para maior segurança

**Principais arquivos:**
- `sync2.py`: Script principal que captura vídeo e sincroniza com o S3
- `.env`: Arquivo de configuração com variáveis sensíveis
- `requirements.txt`: Lista de dependências Python

**Como usar:**
- Veja o README específico na pasta para instruções detalhadas

### 2. `visualizacao_camera`

Esta pasta contém uma aplicação baseada em Docker para visualização de câmeras através do iSpy Agent DVR.

**Principais características:**
- Interface web para visualização de câmeras
- Armazenamento de gravações em diretório local
- Configuração via arquivo compose.yaml
- Detecção de movimento e outras funcionalidades avançadas

**Principais arquivos e diretórios:**
- `compose.yaml`: Configuração do contêiner Docker
- `config/`: Arquivos de configuração do iSpy
- `recordings/`: Diretório onde as gravações são armazenadas
- `commands/`: Scripts e comandos personalizados

**Como usar:**
- Inicie o contêiner Docker com `docker-compose up -d`
- Acesse a interface web na porta 8090

## Requisitos Gerais

- Python 3.6 ou superior
- Docker e Docker Compose (para o componente de visualização)
- Conexão com a internet para sincronização com S3
- Credenciais AWS configuradas
- Câmera IP compatível com RTSP

## Desenvolvimento

Este projeto utiliza:
- Python com ffmpeg para processamento de vídeo
- Docker para isolamento da aplicação de visualização
- AWS S3 para armazenamento em nuvem

Para mais informações sobre cada componente, consulte os READMEs específicos em cada pasta. 