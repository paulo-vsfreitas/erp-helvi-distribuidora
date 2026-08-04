from django.conf import settings
from django.core.mail import EmailMessage


def enviar_email_com_anexo(
    *,
    destinatario,
    assunto,
    mensagem,
    nome_arquivo,
    arquivo,
    content_type="application/pdf",
):
    """
    Envia um e-mail com um arquivo anexado.

    Retorna a quantidade de mensagens confirmadas
    pelo backend de e-mail do Django.
    """
    destinatario = (destinatario or "").strip()
    assunto = (assunto or "").strip()
    mensagem = (mensagem or "").strip()

    if not destinatario:
        raise ValueError(
            "O e-mail do destinatário não foi informado."
        )

    if not assunto:
        raise ValueError(
            "O assunto do e-mail não foi informado."
        )

    email = EmailMessage(
        subject=assunto,
        body=mensagem,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[destinatario],
    )

    email.attach(
        nome_arquivo,
        arquivo,
        content_type,
    )

    quantidade_enviada = email.send(
        fail_silently=False,
    )

    if quantidade_enviada != 1:
        raise RuntimeError(
            "O servidor não confirmou o envio do e-mail."
        )

    return quantidade_enviada