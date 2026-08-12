import json
import mimetypes
import posixpath
import tempfile
import uuid
from http.client import HTTPSConnection
from pathlib import PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from django.core.files import File
from django.core.files.storage import Storage
from django.core.exceptions import SuspiciousFileOperation
from django.utils.deconstruct import deconstructible


class SupabaseStorageError(IOError):
    def __init__(self, message, *, status=None, body=None):
        super().__init__(message)
        self.status = status
        self.body = body


@deconstructible
class SupabaseRESTStorage(Storage):
    """Storage Django para bucket privado do Supabase via API REST nativa.

    Esta implementação não usa o endpoint S3. As operações passam por
    ``/storage/v1/object`` com uma Secret API Key mantida apenas no backend.
    """

    querystring_auth = True

    def __init__(
        self,
        *,
        project_url,
        secret_key,
        bucket_name,
        signed_url_expire=3600,
        cache_control=3600,
        timeout=60,
    ):
        self.project_url = project_url.rstrip("/")
        self.secret_key = secret_key.strip()
        self.bucket_name = bucket_name.strip()
        self.signed_url_expire = int(signed_url_expire)
        self.cache_control = int(cache_control)
        self.timeout = int(timeout)
        self.api_url = f"{self.project_url}/storage/v1"

    def _headers(self, **extra):
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "apikey": self.secret_key,
        }
        headers.update(extra)
        return headers

    @staticmethod
    def _clean_name(name):
        name = str(PurePosixPath(str(name).replace("\\", "/"))).lstrip("/")
        if not name or name == "." or name.startswith("../") or "/../" in f"/{name}":
            raise SuspiciousFileOperation(f"Nome de arquivo inválido: {name!r}")
        return name

    def _object_path(self, name):
        name = self._clean_name(name)
        return f"{quote(self.bucket_name, safe='')}/{quote(name, safe='/')}"

    def _object_url(self, name):
        return f"{self.api_url}/object/{self._object_path(name)}"

    def _request_json(self, method, url, *, payload=None, headers=None, allow_missing=False):
        data = None
        request_headers = self._headers(**(headers or {}))
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            request_headers["Content-Type"] = "application/json"

        req = Request(url, data=data, method=method, headers=request_headers)
        try:
            with urlopen(req, timeout=self.timeout) as response:
                raw = response.read()
                return json.loads(raw.decode("utf-8")) if raw else {}
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            if allow_missing and exc.code in (400, 404):
                return None
            raise SupabaseStorageError(
                f"Supabase Storage respondeu HTTP {exc.code}: {raw or exc.reason}",
                status=exc.code,
                body=raw,
            ) from exc
        except URLError as exc:
            raise SupabaseStorageError(f"Falha de conexão com Supabase Storage: {exc.reason}") from exc

    def get_available_name(self, name, max_length=None):
        """Evita consulta remota e nunca sobrescreve um upload anterior."""
        name = self._clean_name(name)
        diretorio, arquivo = posixpath.split(name)
        raiz, extensao = posixpath.splitext(arquivo)
        sufixo = f"_{uuid.uuid4().hex[:12]}{extensao}"

        if max_length is not None:
            prefixo = f"{diretorio}/" if diretorio else ""
            limite = max_length - len(prefixo) - len(sufixo)
            if limite < 1:
                raise SuspiciousFileOperation(
                    f"O nome '{name}' não pode ser ajustado ao limite de {max_length} caracteres."
                )
            raiz = raiz[:limite]

        return posixpath.join(diretorio, f"{raiz}{sufixo}")

    def _save(self, name, content):
        name = self._clean_name(name)
        content_type = (
            getattr(content, "content_type", None)
            or mimetypes.guess_type(name)[0]
            or "application/octet-stream"
        )

        try:
            content.seek(0)
        except (AttributeError, OSError):
            pass

        parsed = urlsplit(self._object_url(name))
        conn = HTTPSConnection(parsed.hostname, parsed.port or 443, timeout=self.timeout)
        headers = self._headers(
            **{
                "Content-Type": content_type,
                "Cache-Control": f"max-age={self.cache_control}",
                "x-upsert": "false",
            }
        )

        tamanho = getattr(content, "size", None)
        if tamanho is not None:
            headers["Content-Length"] = str(tamanho)

        try:
            conn.request("POST", parsed.path, body=content, headers=headers, encode_chunked=tamanho is None)
            response = conn.getresponse()
            raw = response.read().decode("utf-8", errors="replace")
            if response.status not in (200, 201):
                raise SupabaseStorageError(
                    f"Falha ao gravar no Supabase Storage (HTTP {response.status}): {raw or response.reason}",
                    status=response.status,
                    body=raw,
                )
        finally:
            conn.close()

        return name

    def _open(self, name, mode="rb"):
        if "r" not in mode:
            raise ValueError("SupabaseRESTStorage suporta abertura apenas para leitura.")

        req = Request(self._object_url(name), method="GET", headers=self._headers())
        arquivo = tempfile.SpooledTemporaryFile(max_size=8 * 1024 * 1024, mode="w+b")
        try:
            with urlopen(req, timeout=self.timeout) as response:
                while True:
                    bloco = response.read(1024 * 1024)
                    if not bloco:
                        break
                    arquivo.write(bloco)
        except HTTPError as exc:
            arquivo.close()
            raw = exc.read().decode("utf-8", errors="replace")
            if exc.code == 404:
                raise FileNotFoundError(name) from exc
            raise SupabaseStorageError(
                f"Falha ao ler do Supabase Storage (HTTP {exc.code}): {raw or exc.reason}",
                status=exc.code,
                body=raw,
            ) from exc
        except URLError as exc:
            arquivo.close()
            raise SupabaseStorageError(f"Falha de conexão com Supabase Storage: {exc.reason}") from exc

        arquivo.seek(0)
        return File(arquivo, name=name)

    def exists(self, name):
        req = Request(self._object_url(name), method="HEAD", headers=self._headers())
        try:
            with urlopen(req, timeout=self.timeout):
                return True
        except HTTPError as exc:
            if exc.code in (400, 404):
                return False
            raw = exc.read().decode("utf-8", errors="replace")
            raise SupabaseStorageError(
                f"Falha ao consultar Supabase Storage (HTTP {exc.code}): {raw or exc.reason}",
                status=exc.code,
                body=raw,
            ) from exc
        except URLError as exc:
            raise SupabaseStorageError(f"Falha de conexão com Supabase Storage: {exc.reason}") from exc

    def delete(self, name):
        name = self._clean_name(name)
        self._request_json(
            "DELETE",
            f"{self.api_url}/object/{quote(self.bucket_name, safe='')}",
            payload={"prefixes": [name]},
        )

    def size(self, name):
        req = Request(self._object_url(name), method="HEAD", headers=self._headers())
        try:
            with urlopen(req, timeout=self.timeout) as response:
                tamanho = response.headers.get("Content-Length")
                return int(tamanho) if tamanho is not None else 0
        except HTTPError as exc:
            if exc.code == 404:
                raise FileNotFoundError(name) from exc
            raw = exc.read().decode("utf-8", errors="replace")
            raise SupabaseStorageError(
                f"Falha ao consultar tamanho no Supabase Storage (HTTP {exc.code}): {raw or exc.reason}",
                status=exc.code,
                body=raw,
            ) from exc

    def url(self, name):
        name = self._clean_name(name)
        data = self._request_json(
            "POST",
            f"{self.api_url}/object/sign/{self._object_path(name)}",
            payload={"expiresIn": self.signed_url_expire},
        )
        signed = data.get("signedURL") or data.get("signedUrl")
        if not signed:
            raise SupabaseStorageError("Supabase Storage não retornou uma URL assinada.")
        if signed.startswith("http://") or signed.startswith("https://"):
            return signed
        return f"{self.api_url}{signed if signed.startswith('/') else '/' + signed}"
