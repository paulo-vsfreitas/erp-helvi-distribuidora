from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Valida o storage de mídia fazendo um round-trip pequeno e removendo o arquivo de diagnóstico."

    def handle(self, *args, **options):
        backend = f"{default_storage.__class__.__module__}.{default_storage.__class__.__name__}"
        self.stdout.write(f"APP_ENV: {getattr(settings, 'APP_ENV', '')}")
        self.stdout.write(f"Storage remoto habilitado: {getattr(settings, 'SUPABASE_STORAGE_ENABLED', False)}")
        self.stdout.write(f"Backend: {backend}")
        if getattr(settings, "SUPABASE_STORAGE_ENABLED", False):
            self.stdout.write(f"Bucket: {settings.SUPABASE_STORAGE_BUCKET}")
            self.stdout.write(f"Endpoint: {settings.SUPABASE_STORAGE_ENDPOINT}")
            self.stdout.write(f"Region: {settings.SUPABASE_STORAGE_REGION}")

        nome = "_diagnosticos/helvi-storage-check.txt"
        salvo = None
        try:
            salvo = default_storage.save(nome, ContentFile(b"helvi-storage-ok"))
            if not default_storage.exists(salvo):
                raise CommandError("O arquivo foi salvo, mas o storage informou que ele nao existe.")

            with default_storage.open(salvo, "rb") as arquivo:
                conteudo = arquivo.read()
            if conteudo != b"helvi-storage-ok":
                raise CommandError("O conteudo lido do storage difere do conteudo gravado.")

            self.stdout.write(self.style.SUCCESS("Storage validado: gravacao, leitura e exists OK."))
        except Exception as exc:
            if isinstance(exc, CommandError):
                raise
            raise CommandError(f"Falha ao validar storage: {exc}") from exc
        finally:
            if salvo:
                try:
                    default_storage.delete(salvo)
                except Exception:
                    self.stderr.write("Aviso: nao foi possivel remover o arquivo temporario de diagnostico.")

        self.stdout.write(self.style.SUCCESS("Arquivo temporario removido. Validacao concluida."))
