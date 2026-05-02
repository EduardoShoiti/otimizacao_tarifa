const form = document.getElementById("simulation-form");
const statusElement = document.getElementById("simulation-status");
const currentContext = document.getElementById("current-context");
const proposalContext = document.getElementById("proposal-context");
const premiseBox = document.getElementById("premise-box");
const resultsSection = document.getElementById("results-section");

let currentChart;
let proposalChart;

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: "nearest",
    intersect: false,
  },
  plugins: {
    legend: {
      position: "top",
      labels: {
        usePointStyle: true,
        boxWidth: 10,
        font: {
          family: "Manrope",
          size: 12,
          weight: "700",
        },
      },
    },
    tooltip: {
      callbacks: {
        label(context) {
          const datasetLabel = context.dataset.label || "";
          const value = `${context.parsed.y.toFixed(0)}%`;
          const tarifa = context.raw.tarifa_nova;
          const receita = context.raw.receita_nova_total;

          return datasetLabel === "Margem"
            ? `${datasetLabel}: ${value} | receita nova R$ ${receita.toFixed(2)}`
            : `${datasetLabel}: ${value} | tarifa nova R$ ${tarifa.toFixed(2)}`;
        },
      },
    },
    datalabels: {
      align(context) {
        return context.dataset.key === "desconto" ? "bottom" : "top";
        // return "top";
      },
      anchor: "end",
      offset: 6,
      clamp: true,
      textAlign: "right",
      color(context) {
        return context.dataset.borderColor;
      },
      formatter(value, context) {
        const percentual = `${value.y.toFixed(0)}%`;
        const tarifa = `R$ ${value.tarifa_nova.toFixed(2)}`;
        const receita = `R$ ${value.receita_nova_total.toFixed(2)}`;

        return context.dataset.key === "desconto"
          ? `${percentual}\n${tarifa}`
          : `${percentual}\n${receita}`;
      },
      font: {
        family: "IBM Plex Sans",
        size: 10,
        weight: "700",
      },
    },
  },
  scales: {
    x: {
      title: {
        display: true,
        text: "Quantidade nova de boletos",
        color: "#4f6480",
        font: {
          family: "Manrope",
          size: 13,
          weight: "700",
        },
      },
      ticks: {
        color: "#385170",
        font: {
          family: "IBM Plex Sans",
          size: 11,
        },
      },
      grid: {
        display: false,
      },
    },
    y: {
      ticks: {
        callback(value) {
          return `${value}%`;
        },
        color: "#385170",
        font: {
          family: "IBM Plex Sans",
          size: 11,
        },
      },
      grid: {
        color: "rgba(56, 81, 112, 0.15)",
      },
    },
  },
};

function formatScenarioLabel(item) {
  return item.qtd_boleto_nova.toLocaleString("pt-BR");
}

function buildDatasets(results) {
  return [
    {
      label: "Desconto",
      key: "desconto",
      data: results.map((item) => ({
        x: formatScenarioLabel(item),
        y: Number((-item.desconto * 100).toFixed(0)),
        tarifa_nova: item.tarifa_nova,
        receita_nova_total: item.receita_nova_total,
      })),
      borderColor: "#e64b4b",
      backgroundColor: "#e64b4b",
      borderWidth: 2,
      tension: 0.3,
      pointRadius: 4,
      pointHoverRadius: 5,
    },
    {
      label: "Margem",
      key: "margem",
      data: results.map((item) => ({
        x: formatScenarioLabel(item),
        y: Number((item.margem_exigida * 100).toFixed(0)),
        tarifa_nova: item.tarifa_nova,
        receita_nova_total: item.receita_nova_total,
      })),
      borderColor: "#7ea04d",
      backgroundColor: "#7ea04d",
      borderWidth: 2,
      tension: 0.3,
      pointRadius: 4,
      pointHoverRadius: 5,
    },
  ];
}

function computeSharedYScale(currentResults, proposalResults) {
  const values = [...currentResults, ...proposalResults].flatMap((item) => [
    Number((-item.desconto * 100).toFixed(0)),
    Number((item.margem_exigida * 100).toFixed(0)),
  ]);

  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const amplitude = Math.max(maxValue - minValue, 20);
  const padding = Math.max(10, Math.ceil(amplitude * 0.12));

  return {
    min: Math.floor((minValue - padding) / 10) * 10,
    max: Math.ceil((maxValue + padding) / 10) * 10,
  };
}

function createOrUpdateChart(canvasId, chartRef, title, results, yScale) {
  const ctx = document.getElementById(canvasId);

  if (chartRef) {
    chartRef.destroy();
  }

  return new Chart(ctx, {
    type: "line",
    data: {
      labels: results.map(formatScenarioLabel),
      datasets: buildDatasets(results),
    },
    options: {
      ...chartOptions,
      scales: {
        ...chartOptions.scales,
        y: {
          ...chartOptions.scales.y,
          min: yScale.min,
          max: yScale.max,
        },
      },
      plugins: {
        ...chartOptions.plugins,
        title: {
          display: true,
          text: title,
          align: "start",
          color: "#4f6480",
          font: {
            family: "Manrope",
            size: 20,
            weight: "800",
          },
          padding: {
            bottom: 12,
          },
        },
      },
    },
    plugins: [ChartDataLabels],
  });
}

function fillContext(result, element, isCurrent = false) {
  const first = result[0];
  const last = result[result.length - 1];
  const currentComparison = result[1] ?? first;

  const parts = [
    `cenário base: tarifa R$ ${first.tarifa_nova.toFixed(2)}`,
    `último cenário: tarifa R$ ${last.tarifa_nova.toFixed(2)}`,
  ];

  // if (isCurrent) {
  //   parts.push(`melhor contrapartida simulada: ${currentComparison.tipo_contrapartida}`);
  // }

  element.textContent = parts.join(" | ");
}

function formatCurrency(value) {
  return `R$ ${value.toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function fillPremises(payload) {
  premiseBox.innerHTML = `
    <div class="premise-item">
      <span>Qtd atual de boletos</span>
      <strong>${payload.qtd_boleto_atual.toLocaleString("pt-BR")}</strong>
    </div>
    <div class="premise-item">
      <span>Tarifa atual</span>
      <strong>${formatCurrency(payload.tarifa_atual)}</strong>
    </div>
    <div class="premise-item">
      <span>Qtd nova de boletos</span>
      <strong>${payload.qtd_boleto_nova.toLocaleString("pt-BR")}</strong>
    </div>
    <div class="premise-item">
      <span>Invest Fácil extra</span>
      <strong>${formatCurrency(payload.valor_invest_facil_extra)}</strong>
    </div>
  `;
}

function smoothScrollToResults(target) {
  const startY = window.scrollY;
  const targetY = target.getBoundingClientRect().top + window.scrollY - 18;
  const distance = targetY - startY;
  const duration = 1100;

  function easeInOutCubic(progress) {
    return progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - ((-2 * progress + 2) ** 3) / 2;
  }

  function step(startTime, currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = easeInOutCubic(progress);
    window.scrollTo(0, startY + (distance * eased));

    if (progress < 1) {
      window.requestAnimationFrame((nextTime) => step(startTime, nextTime));
    }
  }

  window.requestAnimationFrame((startTime) => step(startTime, startTime));
}

async function waitForPyScript() {
  const maxAttempts = 120;

  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    if (typeof window.runTarifaSimulation === "function") {
      return;
    }

    await new Promise((resolve) => {
      window.setTimeout(resolve, 250);
    });
  }

  throw new Error("PyScript não ficou disponível a tempo.");
}

function getFormData() {
  return {
    qtd_boleto_atual: Number(form.qtd_boleto_atual.value),
    qtd_evento_atual: Number(form.qtd_evento_atual.value),
    tarifa_atual: Number(form.tarifa_atual.value),
    qtd_boleto_nova: Number(form.qtd_boleto_nova.value),
    valor_invest_facil_extra: Number(form.valor_invest_facil_extra.value),
    margem_fixa: Number(form.margem_fixa.value),
    alpha: Number(form.alpha.value),
    beta: Number(form.beta.value),
  };
}

function setStatus(message, isError = false) {
  statusElement.textContent = message;
  statusElement.dataset.state = isError ? "error" : "default";
}

async function runSimulation(event) {
  event.preventDefault();
  setStatus("Calculando cenários e montando os gráficos...");

  try {
    await waitForPyScript();
    const payload = getFormData();
    fillPremises(payload);
    const response = await window.runTarifaSimulation(JSON.stringify(payload));
    const result = JSON.parse(response);
    const sharedYScale = computeSharedYScale(result.atual, result.proposta);

    currentChart = createOrUpdateChart(
      "current-chart",
      currentChart,
      "Desconto e Margem",
      result.atual,
      sharedYScale,
    );

    proposalChart = createOrUpdateChart(
      "proposal-chart",
      proposalChart,
      "Desconto e Margem",
      result.proposta,
      sharedYScale,
    );

    fillContext(result.atual, currentContext, true);
    fillContext(result.proposta, proposalContext);
    setStatus("Simulação concluída com cenário base e cinco cenários comparativos.");
    smoothScrollToResults(resultsSection);
  } catch (error) {
    console.error(error);
    setStatus(`Erro ao calcular a simulação: ${error.message}`, true);
  }
}

form.addEventListener("submit", runSimulation);
window.addEventListener("load", () => {
  form.requestSubmit();
});
