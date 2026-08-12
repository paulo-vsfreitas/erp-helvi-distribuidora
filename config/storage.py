import posixpath
import uuid

from django.core.exceptions import SuspiciousFileOperation
from storages.backends.s3 import S3Storage
from storages.utils import clean_name


class SupabaseS3Storage(S3Storage):
    """
    Backend S3 compatível com o Supabase Storage.

    Evita o HeadObject usado pelo django-storages para descobrir nomes
    disponíveis. Em alguns cenários S3 compatíveis esse HEAD pode responder
    400 para uma chave ainda inexistente, interrompendo o upload antes do PUT.

    Para preservar a regra de não sobrescrever arquivos, cada novo upload
    recebe um sufixo aleatório sem consultar o storage remoto.
    """

    def get_available_name(self, name, max_length=None):
        name = clean_name(name).replace("\\", "/")
        diretorio, arquivo = posixpath.split(name)
        raiz, extensao = posixpath.splitext(arquivo)

        sufixo = f"_{uuid.uuid4().hex[:12]}{extensao}"

        if max_length is not None:
            prefixo = f"{diretorio}/" if diretorio else ""
            limite_raiz = max_length - len(prefixo) - len(sufixo)
            if limite_raiz < 1:
                raise SuspiciousFileOperation(
                    f"O nome '{name}' não pode ser reduzido para o limite de {max_length} caracteres."
                )
            raiz = raiz[:limite_raiz]

        return posixpath.join(diretorio, f"{raiz}{sufixo}")

    def exists(self, name):
        """
        Usa ListObjectsV2 em vez de HeadObject.

        O Supabase implementa ListObjectsV2 e essa abordagem também mantém
        compatibilidade com pontos do ERP que consultam default_storage.exists().
        """
        name = self._normalize_name(clean_name(name))
        resposta = self.connection.meta.client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=name,
            MaxKeys=1,
        )
        return any(
            objeto.get("Key") == name
            for objeto in resposta.get("Contents", [])
        )
