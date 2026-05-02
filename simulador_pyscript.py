import json

from js import window
from pyodide.ffi import create_proxy

from calculo_tarifa_boleto_atual import calcular_tarifa_boleto_logica_atual
from calculo_tarifa_boleto_proposta import calcular_tarifa_boleto_com_contrapartida


def gerar_cenarios(payload: dict) -> list[dict]:
    cenarios = []
    qtd_boleto_nova = float(payload["qtd_boleto_nova"])

    for indice in range(5):
        fator = 2 ** indice
        cenario = payload.copy()
        cenario["cenario"] = indice + 1
        cenario["qtd_boleto_nova"] = qtd_boleto_nova * fator
        cenarios.append(cenario)

    return cenarios


def simular_cenarios(payload_json: str) -> str:
    payload = json.loads(payload_json)
    cenarios = gerar_cenarios(payload)

    resultados_atual = []
    resultados_proposta = []

    for cenario in cenarios:
        base_atual = calcular_tarifa_boleto_logica_atual(
            qtd_evento_atual=cenario["qtd_evento_atual"],
            qtd_boleto_atual=cenario["qtd_boleto_atual"],
            tarifa_atual=cenario["tarifa_atual"],
            qtd_boleto_nova=cenario["qtd_boleto_nova"],
            valor_invest_facil_extra=cenario["valor_invest_facil_extra"],
            margem_fixa=cenario["margem_fixa"],
        )

        base_proposta = calcular_tarifa_boleto_com_contrapartida(
            qtd_evento_atual=cenario["qtd_evento_atual"],
            qtd_boleto_atual=cenario["qtd_boleto_atual"],
            tarifa_atual=cenario["tarifa_atual"],
            qtd_boleto_nova=cenario["qtd_boleto_nova"],
            valor_invest_facil_extra=cenario["valor_invest_facil_extra"],
            margem_base=cenario["margem_fixa"],
            alpha=cenario["alpha"],
            beta=cenario["beta"],
        )

        resultados_atual.append(
            {
                "cenario": cenario["cenario"],
                "qtd_boleto_nova": cenario["qtd_boleto_nova"],
                "tarifa_nova": base_atual["tarifa_nova"],
                "desconto": base_atual["desconto"],
                "margem_exigida": base_atual["margem_exigida"],
                "tipo_contrapartida": base_atual["tipo_contrapartida_escolhida"],
            }
        )

        resultados_proposta.append(
            {
                "cenario": cenario["cenario"],
                "qtd_boleto_nova": cenario["qtd_boleto_nova"],
                "tarifa_nova": base_proposta["tarifa_nova"],
                "desconto": base_proposta["desconto"],
                "margem_exigida": base_proposta["margem_exigida"],
            }
        )

    return json.dumps(
        {
            "cenarios": cenarios,
            "atual": resultados_atual,
            "proposta": resultados_proposta,
        }
    )


window.runTarifaSimulation = create_proxy(simular_cenarios)
