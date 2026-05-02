def calcular_tarifa_boleto_logica_atual(
    qtd_evento_atual: float,
    qtd_boleto_atual: float,
    tarifa_atual: float,

    # Contrapartida 1: nova quantidade de boletos
    qtd_boleto_nova: float = 0.0,

    # Contrapartida 2: Invest Fácil
    valor_invest_facil_extra: float = 0.0,
    rentabilidade_if: float = 0.0074,

    tarifa_minima: float = 0.1,
    margem_fixa: float = 0.20,
):
    """
    Calcula a nova tarifa de boleto pela lógica atual.

    Características da lógica atual:
    - considera uma única tarifa sendo negociada;
    - usa margem fixa;
    - não usa margem dinâmica;
    - não combina contrapartidas;
    - avalia boleto OU Invest Fácil;
    - escolhe automaticamente a contrapartida que gera o maior desconto;
    - calcula a tarifa por fórmula, sem loop.

    Fórmula geral:

        receita_alvo = receita_atual_boleto * (1 + margem_fixa)

    Para boleto:

        tarifa_nova = receita_alvo / qtd_evento_novo

    Para Invest Fácil:

        tarifa_nova = (receita_alvo - receita_incremental_if) / qtd_evento_atual
    """

    # -----------------------------
    # 0) Validações básicas
    # -----------------------------
    if qtd_evento_atual < 0:
        raise ValueError("qtd_evento_atual deve ser >= 0.")

    if qtd_boleto_atual < 0:
        raise ValueError("qtd_boleto_atual deve ser >= 0.")

    if qtd_boleto_atual == 0:
        raise ValueError("qtd_boleto_atual não pode ser 0 para calcular o fator_evento.")

    if tarifa_atual <= 0:
        raise ValueError("tarifa_atual deve ser > 0.")

    if qtd_boleto_nova < 0:
        raise ValueError("qtd_boleto_nova deve ser >= 0.")

    if valor_invest_facil_extra < 0:
        raise ValueError("valor_invest_facil_extra deve ser >= 0.")

    if rentabilidade_if < 0:
        raise ValueError("rentabilidade_if deve ser >= 0.")

    if tarifa_minima <= 0:
        raise ValueError("tarifa_minima deve ser > 0.")

    if margem_fixa < 0:
        raise ValueError("margem_fixa deve ser >= 0.")

    # -----------------------------
    # 1) Receita atual e receita alvo
    # -----------------------------
    receita_atual_boleto = qtd_evento_atual * tarifa_atual

    receita_alvo = receita_atual_boleto * (1 + margem_fixa)

    # -----------------------------
    # 2) Fator histórico boleto -> evento
    # -----------------------------
    fator_evento = min(1.0, qtd_evento_atual / qtd_boleto_atual)

    # =========================================================
    # Cenário A: contrapartida por quantidade de boleto
    # =========================================================
    qtd_evento_novo_boleto = qtd_boleto_nova * fator_evento

    tarifa_nova_boleto = receita_alvo / qtd_evento_novo_boleto

    tarifa_nova_boleto = max(tarifa_minima, tarifa_nova_boleto)
    tarifa_nova_boleto = min(tarifa_atual, tarifa_nova_boleto)

    desconto_boleto = 1 - (tarifa_nova_boleto / tarifa_atual)

    receita_nova_boleto = qtd_evento_novo_boleto * tarifa_nova_boleto

    resultado_boleto = {
        "tipo_contrapartida": "boleto",

        "tarifa_nova": tarifa_nova_boleto,
        "desconto": desconto_boleto,

        "qtd_boleto_nova": qtd_boleto_nova,
        "qtd_evento_novo": qtd_evento_novo_boleto,

        "valor_invest_facil_extra": 0.0,
        "receita_incremental_if": 0.0,

        "receita_nova_total": receita_nova_boleto,
    }

    # =========================================================
    # Cenário B: contrapartida por Invest Fácil
    # =========================================================
    receita_incremental_if = valor_invest_facil_extra * rentabilidade_if

    receita_alvo_liquida_if = receita_alvo - receita_incremental_if

    tarifa_nova_if = receita_alvo_liquida_if / qtd_evento_atual

    tarifa_nova_if = max(tarifa_minima, tarifa_nova_if)
    tarifa_nova_if = min(tarifa_atual, tarifa_nova_if)

    desconto_if = 1 - (tarifa_nova_if / tarifa_atual)

    receita_boleto_nova_if = qtd_evento_atual * tarifa_nova_if

    receita_nova_total_if = receita_boleto_nova_if + receita_incremental_if

    resultado_if = {
        "tipo_contrapartida": "invest_facil",

        "tarifa_nova": tarifa_nova_if,
        "desconto": desconto_if,

        "qtd_boleto_nova": 0.0,
        "qtd_evento_novo": qtd_evento_atual,

        "valor_invest_facil_extra": valor_invest_facil_extra,
        "receita_incremental_if": receita_incremental_if,

        "receita_nova_total": receita_nova_total_if,
    }

    # -----------------------------
    # 3) Escolher a melhor contrapartida
    # -----------------------------
    if resultado_boleto["desconto"] >= resultado_if["desconto"]:
        melhor_resultado = resultado_boleto
    else:
        melhor_resultado = resultado_if

    # -----------------------------
    # 4) Resultado final
    # -----------------------------
    return {
        "tipo_logica": "atual_margem_fixa",

        "tipo_contrapartida_escolhida": melhor_resultado["tipo_contrapartida"],

        "tarifa_atual": tarifa_atual,
        "tarifa_nova": round(float(melhor_resultado["tarifa_nova"]), 2),
        "desconto": round(float(melhor_resultado["desconto"]), 2),
        "margem_exigida": round(float(margem_fixa), 2),

        "qtd_evento_atual": qtd_evento_atual,
        "qtd_boleto_atual": qtd_boleto_atual,
        "fator_evento": fator_evento,

        "qtd_boleto_nova": melhor_resultado["qtd_boleto_nova"],
        "qtd_evento_novo": melhor_resultado["qtd_evento_novo"],

        "valor_invest_facil_extra": melhor_resultado["valor_invest_facil_extra"],
        "rentabilidade_if": rentabilidade_if,
        "receita_incremental_if": round(float(melhor_resultado["receita_incremental_if"]), 2),

        "receita_atual_boleto": round(float(receita_atual_boleto), 2),
        "receita_alvo": round(float(receita_alvo), 2),
        "receita_nova_total": round(float(melhor_resultado["receita_nova_total"]), 2),

        "resultado_boleto": {
            "tarifa_nova": round(float(resultado_boleto["tarifa_nova"]), 2),
            "desconto": round(float(resultado_boleto["desconto"]), 2),
            "receita_nova_total": round(float(resultado_boleto["receita_nova_total"]), 2),
        },

        "resultado_invest_facil": {
            "tarifa_nova": round(float(resultado_if["tarifa_nova"]), 2),
            "desconto": round(float(resultado_if["desconto"]), 2),
            "receita_nova_total": round(float(resultado_if["receita_nova_total"]), 2),
        },
    }


if __name__ == "__main__":
    resultado = calcular_tarifa_boleto_logica_atual(
        qtd_evento_atual=100,
        qtd_boleto_atual=100,
        tarifa_atual=5,
        qtd_boleto_nova=200,
        valor_invest_facil_extra=8_000,
        margem_fixa=0.20
    )

    print(resultado)
