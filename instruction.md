## Simulador - Calculdo de tarifa para apresentação

Tenho meu projeto de otimização de desconto de tarifa com base em contrapartida, quero montar uma página web simples para apresentar para o time de negócio, para que a explicação fique clara e de forma visual.

Tenho duas funções python, uma representa a lógica atual do projeto "calculo_tarifa_boleto_atual.py" e a outra a minha proposta "calculo_tarifa_boleto_proposta.py".

Quero que você desenvolva uma página frontend simples com HTML, CSS, JS e PyScript, seguindo o esboço "template_frontend.png". O objetivo dessa página é mostrar como funciona a lógica atual vs a proposta. E deve conter a seguinte lógica:

- Ter um formulário com campos para preencher: Qtd atual de boleto, qtd evento tarifado histórico, tarifa atual, qtd nova boleto, invest fácil extra, margem fixa, alpha e beta.
- Ao enviar os dados, esses dados vão ser "duplicados" para simular cenários, imagine armazer cada cenário em um array. Como o usuário só irá passar um cenário, os outros 4 cenários serão gerados de forma dinâmica: onde todos os campos vão continuar iguais, apenas a qtd nova boleto será multiplicada por 2.
- Depois disso todos os cenários devem passar pelas funções de calculo (atual e proposta), e armazaer o resultado de cada um.
- Com os resultados, deve ser gerado um gráfico a esqueda para mostrar os cenários atuais e um a direita com os cenários da proposta
- Os gráficos vão ser de linhas (uma linha para representar o desconto e outro a margem), transforme o desconto em negativo para ficar melhor visualmente. O eixo X vai ser cada simulação, onde será exibido a qtd nova boleto e o eixo Y o desconto e margem em porcentagem. As linhas devem contem labels com o valor exato delas (exibindo o valor do desconto e da margem), junto com o valor do desconto coloque o valor da tarifa nova.


Utilize o PyScript para conseguir calcular a tarifa, igual faço nas minhas funções Python.
Para gerar os gráficos, fica a seu critério, o que achar que terá melhor resultado usar Python ou JS.