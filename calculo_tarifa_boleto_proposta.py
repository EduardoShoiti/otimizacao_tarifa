def margem_dinamica(
    desconto: float,
    margem_base: float = 0.10,
    alpha: float = 0.30,
    beta: float = 1.70,
):
    d = max(0.0, min(1.0, desconto))

    margem = margem_base + alpha * d + beta * (d ** 2)

    return margem


def calcular_tarifa_boleto_com_contrapartida(
    qtd_evento_atual: float,
    qtd_boleto_atual: float,
    tarifa_atual: float,

    # Contrapartida 1: boletos extras
    qtd_boleto_nova: float = 0.0,

    # Contrapartida 2: Invest Fácil
    valor_invest_facil_extra: float = 0.0,
    rentabilidade_if: float = 0.0074,

    tarifa_minima: float = 0.1,

    margem_base: float = 0.20,
    alpha: float = 0.20,
    beta: float = 1.50,

    num_passos_busca: int = 5000,
):
    """
    Calcula a nova tarifa de boleto considerando uma única tarifa negociada,
    mas permitindo contrapartida por:

    1. Quantidade extra de boletos
    2. Aporte extra em Invest Fácil
    3. Combinação dos dois

    A lógica econômica é:

        receita_nova_total >= receita_alvo

    Onde:

        receita_nova_total =
            receita_boleto_nova
            + receita_incremental_invest_facil

        receita_alvo =
            receita_atual * (1 + margem_dinamica(desconto))
    """

    # -----------------------------
    # 0) Validações básicas
    # -----------------------------
    if qtd_evento_atual < 0:
        raise ValueError("qtd_evento_atual deve ser >= 0.")

    if qtd_boleto_atual < 0:
        raise ValueError("qtd_boleto_atual deve ser >= 0.")

    if tarifa_atual <= 0:
        raise ValueError("tarifa_atual deve ser > 0.")

    if qtd_boleto_nova < 0:
        raise ValueError("qtd_boleto_nova deve ser >= 0.")

    if valor_invest_facil_extra < 0:
        raise ValueError("valor_invest_facil_extra deve ser >= 0.")

    if rentabilidade_if < 0:
        raise ValueError("rentabilidade_if deve ser >= 0.")

    if qtd_boleto_atual == 0:
        raise ValueError("qtd_boleto_atual não pode ser 0 para calcular o fator_evento.")

    if tarifa_minima <= 0:
        raise ValueError("tarifa_minima deve ser > 0.")

    # -----------------------------
    # 1) Receita atual de boletos
    # -----------------------------
    receita_atual_boleto = qtd_evento_atual * tarifa_atual

    # -----------------------------
    # 2) Converter boletos extras em eventos extras
    # -----------------------------
    fator_evento = min(1.0, qtd_evento_atual / qtd_boleto_atual)

    qtd_evento_extra = qtd_boleto_nova * fator_evento

    # -----------------------------
    # 3) Receita incremental do Invest Fácil
    # -----------------------------
    receita_incremental_if = valor_invest_facil_extra * rentabilidade_if

    # -----------------------------
    # 4) Buscar menor tarifa viável
    # -----------------------------
    if num_passos_busca < 2:
        tarifas_candidatas = [tarifa_minima, tarifa_atual]
    else:
        passo = (tarifa_atual - tarifa_minima) / (num_passos_busca - 1)
        tarifas_candidatas = [
            tarifa_minima + (passo * indice)
            for indice in range(num_passos_busca)
        ]

    melhor_resultado = None

    for tarifa_candidata in tarifas_candidatas:
        desconto = 1 - (tarifa_candidata / tarifa_atual)

        margem_exigida = margem_dinamica(
            desconto=desconto,
            margem_base=margem_base,
            alpha=alpha,
            beta=beta,
        )

        receita_alvo = receita_atual_boleto * (1 + margem_exigida)

        receita_boleto_nova = qtd_evento_extra * tarifa_candidata

        receita_nova_total = (
            receita_boleto_nova
            + receita_incremental_if
        )

        if receita_nova_total >= receita_alvo:
            melhor_resultado = {
                "tarifa_atual": tarifa_atual,
                "tarifa_nova": round(float(tarifa_candidata), 2),
                "desconto": round(float(desconto), 2),
                "margem_exigida": round(float(margem_exigida), 2),

                "qtd_evento_atual": qtd_evento_atual,
                "qtd_boleto_atual": qtd_boleto_atual,
                "fator_evento": fator_evento,

                "qtd_boleto_nova": qtd_boleto_nova,
                "qtd_evento_extra": qtd_evento_extra,

                "valor_invest_facil_extra": valor_invest_facil_extra,

                "receita_atual_boleto": round(float(receita_atual_boleto), 2),
                "receita_nova_total": round(float(receita_nova_total), 2),
            }

            break

    # -----------------------------
    # 5) Caso nenhum desconto seja viável
    # -----------------------------
    if melhor_resultado is None:
        desconto = 0.0

        margem_exigida = margem_dinamica(
            desconto=desconto,
            margem_base=margem_base,
            alpha=alpha,
            beta=beta,
        )

        receita_alvo = receita_atual_boleto * (1 + margem_exigida)

        receita_boleto_nova = qtd_evento_extra * tarifa_atual

        receita_nova_total = (
            receita_boleto_nova
            + receita_incremental_if
        )

        return {
            "tarifa_atual": tarifa_atual,
            "tarifa_nova": tarifa_atual,
            "desconto": 0.0,
            "margem_exigida": round(float(margem_exigida), 2),

            "qtd_evento_atual": qtd_evento_atual,
            "qtd_boleto_atual": qtd_boleto_atual,
            "fator_evento": fator_evento,

            "qtd_boleto_nova": qtd_boleto_nova,
            "qtd_evento_extra": qtd_evento_extra,

            "valor_invest_facil_extra": valor_invest_facil_extra,

            "receita_atual_boleto": round(float(receita_atual_boleto), 2),
            "receita_nova_total": round(float(receita_nova_total), 2),
        }

    return melhor_resultado


if __name__ == "__main__":
    resultado = calcular_tarifa_boleto_com_contrapartida(
        qtd_evento_atual=100,
        qtd_boleto_atual=100,
        tarifa_atual=5,

        qtd_boleto_nova=200,

        valor_invest_facil_extra=8_000,
        rentabilidade_if=0.0074,

        margem_base=0.20,
        alpha=0.20,
        beta=1.50,
    )

    print(resultado)
