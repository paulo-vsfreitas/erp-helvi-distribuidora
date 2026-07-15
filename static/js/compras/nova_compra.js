{% extends "core/base.html" %}
{% load static %}

{% block title %}Nova Compra | ERP Helvi{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/compras.css' %}">
{% endblock %}

{% block content %}

<div class="page-header">
    <div>
        <h1>Nova Compra</h1>
        <p>Cadastre uma nova compra de produtos.</p>
    </div>

    <a href="{% url 'compras:lista' %}" class="btn btn-outline-secondary">
        Voltar
    </a>
</div>

<form id="form-compra" method="post">
    {% csrf_token %}

    <div class="row">
        <div class="col-lg-8">
            {% include "compras/components/dados_compra.html" %}
            {% include "compras/components/tabela_itens.html" %}
        </div>

        <div class="col-lg-4">
            {% include "compras/components/resumo_compra.html" %}
        </div>
    </div>

    <div class="card mt-3">
        <div class="card-body d-flex justify-content-end gap-2">
            <a href="{% url 'compras:lista' %}" class="btn btn-outline-secondary">
                Cancelar
            </a>

            <button type="submit" class="btn btn-primary">
                Salvar Compra
            </button>
        </div>
    </div>
</form>

{% block extra_js %}
<script src="{% static 'js/compras/form_compra.js' %}?v=1"></script>
<script src="{% static 'js/compras/tabela_itens.js' %}?v=17"></script>
{% endblock %}