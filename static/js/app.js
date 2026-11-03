const form = document.getElementById("chatForm");
const input = document.getElementById("question");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");
const clearButton = document.getElementById("clearChat");
let history = [];

function scrollToBottom() { messages.scrollTop = messages.scrollHeight; }

function addMessage(role, content, sources = []) {
  const welcome = messages.querySelector(".welcome");
  if (welcome) welcome.remove();

  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = role === "user" ? "Y" : "A";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;

  if (sources.length) {
    const sourceBox = document.createElement("div");
    sourceBox.className = "sources";
    const title = document.createElement("div");
    title.className = "sources-title";
    title.textContent = "SOURCES USED";
    sourceBox.appendChild(title);
    sources.forEach(source => {
      const item = document.createElement("div");
      item.className = "source-item";
      const name = document.createElement("strong");
      name.textContent = source.name;
      const excerpt = document.createElement("span");
      excerpt.textContent = source.excerpt ? ` — ${source.excerpt}` : "";
      item.append(name, excerpt);
      sourceBox.appendChild(item);
    });
    bubble.appendChild(sourceBox);
  }

  wrapper.append(avatar, bubble);
  messages.appendChild(wrapper);
  scrollToBottom();
}

function addTyping() {
  const el = document.createElement("div");
  el.className = "typing";
  el.id = "typing";
  el.textContent = "AskCampus is searching the knowledge base…";
  messages.appendChild(el);
  scrollToBottom();
}
function removeTyping() { document.getElementById("typing")?.remove(); }

async function sendQuestion(question) {
  if (!question.trim() || sendButton.disabled) return;
  addMessage("user", question);
  history.push({ role: "user", content: question });
  input.value = "";
  input.style.height = "auto";
  sendButton.disabled = true;
  addTyping();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, history: history.slice(-6, -1) })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Unable to get an answer.");
    removeTyping();
    addMessage("assistant", data.answer, data.sources || []);
    history.push({ role: "assistant", content: data.answer });
  } catch (error) {
    removeTyping();
    addMessage("assistant", error.message || "Something went wrong. Please try again.");
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", event => {
  event.preventDefault();
  sendQuestion(input.value);
});
input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
});
input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
document.querySelectorAll("[data-question]").forEach(button => {
  button.addEventListener("click", () => sendQuestion(button.dataset.question));
});
clearButton.addEventListener("click", () => {
  history = [];
  messages.innerHTML = `<div class="welcome">
    <div class="welcome-icon">✦</div><h2>Hi! What would you like to know?</h2>
    <p>I can help you explore campus information. Ask a question or choose a suggested topic to get started.</p>
    <div class="starter-prompts">
      <button data-question="How can I find information about admissions?">How do admissions work? <span>→</span></button>
      <button data-question="Where can I find details about academic programmes?">Explore academic programmes <span>→</span></button>
    </div></div>`;
  messages.querySelectorAll("[data-question]").forEach(button =>
    button.addEventListener("click", () => sendQuestion(button.dataset.question))
  );
});
