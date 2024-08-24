import subprocess
import sys


def run_command(command, check=True):
    """Ejecuta un comando y muestra la salida en tiempo real."""
    print(f"Ejecutando: {command}")
    result = subprocess.run(command, shell=True, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)


def main():
    try:
        # Actualizar el repositorio
        run_command("git pull origin main")

        # Activar el entorno virtual
        run_command("source ../venv/bin/activate", check=False)

        # Instalar dependencias
        run_command("pip install -r requirements.txt")

        # Aplicar migraciones
        run_command("python3 manage.py makemigrations")
        run_command("python3 manage.py migrate")

        # Cargar datos en fixtures
        run_command("python3 manage.py loaddata */fixtures/*")

        # Recolectar archivos estáticos
        run_command("python3 manage.py collectstatic --noinput")

        # Reiniciar Gunicorn
        run_command("sudo systemctl restart gunicorn_bank")

        # Reiniciar Nginx (si es necesario)
        run_command("sudo systemctl restart nginx")

        print("Despliegue completado exitosamente.")

    except subprocess.CalledProcessError as e:
        print(f"Error durante el despliegue: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
