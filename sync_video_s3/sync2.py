import ffmpeg
import argparse
import time
import os
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import dotenv
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações
RTSP_URL = os.getenv("RTSP_URL")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
S3_BUCKET = os.getenv("S3_BUCKET")
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 60))  # segundos

# Configuração de logging
logging.basicConfig(
    filename=os.getenv("LOG_FILE", 'app_metrics.log'),
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(message)s'
)

class S3UploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        
        # Aguarda o arquivo estar completo (120 segundos + margem de segurança)
        time.sleep(125)  
        
        try:
            # Verifica duração do vídeo usando ffmpeg
            probe = ffmpeg.probe(file_path)
            duration = float(probe['format']['duration'])
            
            # Verifica se o vídeo tem aproximadamente 2 minutos (entre 115 e 125 segundos)
            if 115 <= duration <= 125:
                self.upload_to_s3(file_path)
            else:
                logging.error(f"Arquivo com duração incorreta: {duration} segundos - {file_path}")
            
        except Exception as e:
            logging.error(f"Erro ao verificar arquivo: {str(e)} - {file_path}")

    def upload_to_s3(self, file_path):
        try:
            # Verifica novamente o tamanho antes do upload
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                logging.error(f"Arquivo vazio antes do upload: {file_path}")
                return

            # Prepara o ambiente com credenciais AWS se fornecidas no .env
            env = os.environ.copy()
            aws_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_region = os.getenv("AWS_DEFAULT_REGION")
            
            if aws_key and aws_secret:
                env["AWS_ACCESS_KEY_ID"] = aws_key
                env["AWS_SECRET_ACCESS_KEY"] = aws_secret
                if aws_region:
                    env["AWS_DEFAULT_REGION"] = aws_region

            # Comando AWS CLI modificado
            cmd = f"aws s3 cp {file_path} {S3_BUCKET}/{os.path.basename(file_path)} --no-progress"
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, env=env)
            
            # Verifica se o upload foi bem sucedido
            if result.returncode == 0:
                # Verifica se o arquivo existe no S3 antes de deletar
                check_cmd = f"aws s3 ls {S3_BUCKET}/{os.path.basename(file_path)}"
                check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, env=env)
                
                if check_result.returncode == 0:
                    logging.info(f"Upload OK: {file_path} (Tamanho: {file_size} bytes)")
                    os.remove(file_path)
                else:
                    logging.error(f"Arquivo não encontrado no S3 após upload: {file_path}")
        except Exception as e:
            logging.error(f"Erro no upload: {str(e)} - Arquivo: {file_path}")

class VideoRecorder:
    def __init__(self):
        self.process = None
        self.output_template = os.path.join(OUTPUT_DIR, "%Y-%m-%d_%H-%M-%S.mp4")

    def start_recording(self):
        try:
            self.process = (
                ffmpeg
                .input(RTSP_URL)
                .output(
                    self.output_template,
                    vcodec='copy',
                    f='segment',
                    segment_time=120,
                    strftime=1,
                    reset_timestamps=1,
                    r=2
                )
                .global_args('-loglevel', 'error')
                .run_async()
            )
            return True
        except ffmpeg.Error as e:
            logging.error(f"Erro FFmpeg: {e.stderr.decode('utf-8')}")
            return False

def main():
    parser = argparse.ArgumentParser(description="RTSP to S3 Service")
    parser.add_argument("--start", action="store_true", help="Iniciar serviço")
    args = parser.parse_args()

    if not args.start:
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    observer = Observer()
    event_handler = S3UploadHandler()
    observer.schedule(event_handler, OUTPUT_DIR, recursive=False)
    observer.start()

    recorder = VideoRecorder()

    while True:
        try:
            if recorder.start_recording():
                logging.info("Gravação iniciada com sucesso")
                recorder.process.wait()
            else:
                logging.error("Falha ao iniciar gravação")
            
            logging.error("Reconectando...")
            time.sleep(RETRY_DELAY)

        except KeyboardInterrupt:
            logging.info("Serviço interrompido pelo usuário")
            observer.stop()
            break
        except Exception as e:
            logging.error(f"Erro não tratado: {str(e)}")
            time.sleep(RETRY_DELAY)

    observer.join()

if __name__ == "__main__":
    main()