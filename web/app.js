import { audit, build, clean } from "./logic.js";

const el = (id) => document.getElementById(id);
const tabs = Array.from(document.querySelectorAll(".mode-tab"));
const modes = ["check", "build", "clean"];

function node(tag, cls, content) {
  const result = document.createElement(tag);
  if (cls) result.className = cls;
  if (content !== undefined && content !== null) result.textContent = String(content);
  return result;
}

function switchMode(mode, focus = false) {
  for (const tab of tabs) {
    const selected = tab.dataset.mode === mode;
    tab.classList.toggle("active", selected);
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
    if (selected && focus) tab.focus();
  }
  for (const name of modes) el("panel-" + name).hidden = name !== mode;
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => switchMode(tab.dataset.mode));
  tab.addEventListener("keydown", (event) => {
    const index = modes.indexOf(tab.dataset.mode);
    let next = index;
    if (event.key === "ArrowRight") next = (index + 1) % modes.length;
    else if (event.key === "ArrowLeft") next = (index - 1 + modes.length) % modes.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = modes.length - 1;
    else return;
    event.preventDefault();
    switchMode(modes[next], true);
  });
});

function showError(id, message) {
  const container = el(id);
  container.replaceChildren(node("p", "message-error", message));
  container.hidden = false;
}

function addCopyButton(parent, text) {
  const button = node("button", "copy-btn", "Copy link");
  button.type = "button";
  button.addEventListener("click", async () => {
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText)
        throw new Error("Clipboard not supported");
      await navigator.clipboard.writeText(text);
      button.textContent = "Copied ✓";
    } catch {
      button.textContent = "Select the text above to copy";
    }
  });
  parent.append(button);
}

function showOutput(id, title, url, note) {
  const root = el(id);
  root.replaceChildren();
  root.hidden = false;
  root.append(node("h3", "", title));
  root.append(node("p", "result-note", note));
  const wrapper = node("div", "output-wrap");
  wrapper.append(node("code", "output-url", url));
  addCopyButton(wrapper, url);
  root.append(wrapper);
}

el("check-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const urls = el("check-input").value.split(/\r?\n/).map((x) => x.trim()).filter(Boolean);
  if (!urls.length) return showError("check-results", "Enter at least one link.");
  if (urls.length > 5000) return showError("check-results", "Please check 5,000 links or fewer at a time.");
  const reports = urls.map(audit);
  const errors = reports.reduce((n, r) => n + r.findings.filter((f) => f.level === "error").length, 0);
  const warnings = reports.reduce((n, r) => n + r.findings.filter((f) => f.level === "warning").length, 0);
  const root = el("check-results");
  root.replaceChildren();
  root.hidden = false;
  root.append(node("h3", "", errors ? "Some links need attention." : warnings ? "A few things to double-check." : "Looking good."));
  root.append(node("p", "result-note", urls.length + " links checked · " + errors + " errors · " + warnings + " warnings. Input URLs are never displayed here."));
  reports.forEach((report, index) => {
    const card = node("article", "result-card");
    const top = node("div", "result-top");
    top.append(node("strong", "result-index", "Link " + (index + 1)));
    top.append(node("span", "count", report.parameterCount + " query params"));
    card.append(top);
    if (report.findings.length === 0) {
      card.append(node("p", "all-clear", "✓ No problems detected by this checker."));
    } else {
      for (const finding of report.findings) {
        const row = node("div", "finding " + finding.level);
        row.append(node("span", "finding-icon", finding.level.toUpperCase()));
        row.append(node("span", "", finding.code + ": " + finding.message));
        card.append(row);
      }
    }
    root.append(card);
  });
});

el("build-form").addEventListener("submit", (event) => {
  event.preventDefault();
  try {
    const url = build(el("build-base").value.trim(), {
      source: el("build-source").value,
      medium: el("build-medium").value,
      campaign: el("build-campaign").value,
      content: el("build-content").value,
      term: el("build-term").value
    }, el("build-replace").checked);
    showOutput("build-results", "Ready to go.", url, "Your new campaign link, generated entirely in this tab. Review before publishing.");
  } catch (err) {
    showError("build-results", String(err.message || "Cannot build this link."));
  }
});

el("clean-form").addEventListener("submit", (event) => {
  event.preventDefault();
  try {
    const result = clean(el("clean-input").value.trim());
    showOutput("clean-results", "A little lighter.", result.url,
      "Removed " + result.removed + " tracking or sensitive query parameter(s). Some links rely on parameters; review carefully.");
  } catch (err) {
    showError("clean-results", String(err.message || "Cannot clean this link."));
  }
});

