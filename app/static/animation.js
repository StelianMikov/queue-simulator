// Изчисленията са направени на сървъра. Тук само се показва резултатът:
// всеки клиент е [пристигане, каса, начало на обслужване, край].
const data = JSON.parse(document.getElementById("animation-data").textContent);
const customers = data.customers;
const lastExit = customers.reduce((max, c) => Math.max(max, c[3]), data.duration);

const canvas = document.getElementById("animation");
const ctx = canvas.getContext("2d");
const playButton = document.getElementById("play");
const speedSelect = document.getElementById("speed");
const slider = document.getElementById("time");
const clock = document.getElementById("clock");
const counters = document.getElementById("counters");

const HEIGHT = 230;
const DOT = 6;
const STEP = 16;
const QUEUE_TOP = 104;

let time = 0;
let playing = false;
let lastFrame = null;

slider.max = Math.ceil(lastExit);

function clockText(minutes) {
  const total = 8 * 60 + Math.floor(minutes);
  const hours = String(Math.floor(total / 60) % 24).padStart(2, "0");
  return hours + ":" + String(total % 60).padStart(2, "0");
}

function dot(x, y, color) {
  ctx.beginPath();
  ctx.arc(x, y, DOT, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();
}

function countCustomers() {
  const serving = new Array(data.cashiers).fill(false);
  const lines = new Array(data.cashiers).fill(0);
  let waiting = 0;
  let done = 0;

  for (const [arrival, cashier, start, end] of customers) {
    if (arrival > time) break;
    if (time >= end) done++;
    else if (time >= start) serving[cashier] = true;
    else { waiting++; lines[cashier]++; }
  }
  return { serving, lines, waiting, done };
}

function drawCashiers(width, serving) {
  const column = width / data.cashiers;
  const boxWidth = Math.min(column - 10, 96);
  for (let i = 0; i < data.cashiers; i++) {
    const center = column * (i + 0.5);
    ctx.strokeStyle = "#111";
    ctx.lineWidth = 1;
    ctx.strokeRect(center - boxWidth / 2 + 0.5, 12.5, boxWidth, 34);
    ctx.fillStyle = "#111";
    ctx.fillText(boxWidth > 70 ? "Каса " + (i + 1) : String(i + 1), center, 30);
    if (serving[i]) dot(center, 64, "#2a78d6");
  }
}

function drawCommonQueue(width, waiting) {
  const perRow = Math.max(1, Math.floor((width - 24) / STEP));
  const rows = Math.floor((HEIGHT - QUEUE_TOP - 20) / STEP);
  const shown = Math.min(waiting, perRow * rows);
  for (let n = 0; n < shown; n++) {
    dot(12 + DOT + (n % perRow) * STEP, QUEUE_TOP + Math.floor(n / perRow) * STEP, "#444");
  }
  if (waiting > shown) ctx.fillText("+ още " + (waiting - shown), width / 2, HEIGHT - 10);
}

function drawSeparateQueues(width, lines) {
  const column = width / data.cashiers;
  const rows = Math.floor((HEIGHT - QUEUE_TOP - 20) / STEP);
  for (let i = 0; i < data.cashiers; i++) {
    const center = column * (i + 0.5);
    const shown = Math.min(lines[i], rows);
    for (let n = 0; n < shown; n++) dot(center, QUEUE_TOP + n * STEP, "#444");
    if (lines[i] > shown) ctx.fillText("+" + (lines[i] - shown), center, HEIGHT - 10);
  }
}

function draw() {
  const width = canvas.clientWidth;
  const scale = window.devicePixelRatio || 1;
  canvas.width = width * scale;
  canvas.height = HEIGHT * scale;
  ctx.setTransform(scale, 0, 0, scale, 0, 0);
  ctx.clearRect(0, 0, width, HEIGHT);
  ctx.font = "13px Arial, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  const { serving, lines, waiting, done } = countCustomers();
  drawCashiers(width, serving);
  ctx.fillStyle = "#111";
  if (data.common) drawCommonQueue(width, waiting);
  else drawSeparateQueues(width, lines);

  clock.textContent = clockText(time);
  slider.value = time;
  counters.textContent =
    "Чакат: " + waiting + ", на каса: " + serving.filter(Boolean).length + ", обслужени: " + done +
    (time >= data.duration ? " (нови клиенти вече не влизат)" : "");
}

function frame(now) {
  if (!playing) return;
  if (lastFrame !== null) {
    time += ((now - lastFrame) / 1000) * Number(speedSelect.value);
  }
  lastFrame = now;
  if (time >= lastExit) {
    time = lastExit;
    setPlaying(false);
  }
  draw();
  if (playing) requestAnimationFrame(frame);
}

function setPlaying(value) {
  playing = value;
  lastFrame = null;
  playButton.textContent = playing ? "Пауза" : "Пусни";
  if (playing) requestAnimationFrame(frame);
}

playButton.addEventListener("click", () => {
  if (!playing && time >= lastExit) time = 0;
  setPlaying(!playing);
});

slider.addEventListener("input", () => {
  time = Number(slider.value);
  draw();
});

window.addEventListener("resize", draw);

draw();
