# Projeto de Câmera com Sincronização para AWS S3

Este projeto captura vídeo de uma câmera RTSP e salva os dados no AWS S3.

## Configuração

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Configure o arquivo `.env` com suas credenciais:
   ```
   RTSP_URL=sua_url_rtsp
   OUTPUT_DIR=diretório_de_saída
   S3_BUCKET=seu_bucket_s3
   RETRY_DELAY=60
   ```

3. Execute o projeto:
   ```
   python sync2.py --start
   ```

## Arquivos Principais

- `sync2.py`: Script principal que captura vídeo e sincroniza com o S3
- `.env`: Arquivo de configuração com variáveis sensíveis 