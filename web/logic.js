// Pure browser/Node URL checks. No requests, cookies, storage, eval, or dynamic HTML.
export const REQUIRED = ["utm_source", "utm_medium", "utm_campaign"];
const UTM = new Set([...REQUIRED, "utm_content", "utm_term"]);
const TRACKERS = new Set(["fbclid", "gclid", "gbraid", "wbraid", "msclkid", "ttclid", "twclid", "mc_cid", "mc_eid"]);
const SENSITIVE = new Set(["email", "e_mail", "phone", "mobile", "password", "passwd", "token", "auth", "authorization",
    "api_key", "apikey", "access_token", "refresh_token", "session", "sessionid", "ssn", "dob", "date_of_birth", "idfa", "gaid"]);
const EMAIL = /[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}/i;
const CONTROL = /[\u0000-\u001f\u007f]/;
const BAD_PERCENT = /%(?![a-f\d]{2})/i;
const item = (level, code, message) => ({level, code, message});
function parse(raw) {
  if (typeof raw !== "string" || !raw || raw.length > 8192) throw new Error("URL missing or exceeds 8192 characters");
  if (CONTROL.test(raw) || BAD_PERCENT.test(raw)) throw new Error("Control characters or malformed percent encoding");
  if (!/^https?:\/\//i.test(raw)) throw new Error("Only HTTP and HTTPS links are supported");
  let url;
  try { url = new URL(raw); } catch { throw new Error("URL syntax is invalid"); }
  if (!url.hostname) throw new Error("Hostname is required");
  if (url.username || url.password) throw new Error("Embedded URL credentials are refused");
  return url;
}
function sensitive(key, value) {
  return SENSITIVE.has(key.trim().toLowerCase().replaceAll("-", "_")) || EMAIL.test(value);
}
export function audit(raw) {
  let url;
  try { url = parse(raw); }
  catch (err) { return {parameterCount: 0, findings: [item("error", "CLD001", err.message)]}; }
  const pairs = [...url.searchParams.entries()];
  const keys = pairs.map(([k]) => k.toLowerCase());
  const findings = [];
  if (url.protocol === "http:") findings.push(item("warning", "CLD101", "HTTP link is not encrypted in transit."));
  const counts = new Map();
  for (const key of keys) counts.set(key, (counts.get(key) || 0) + 1);
  if ([...counts].some(([key, n]) => n > 1 && (key.startsWith("utm_") || TRACKERS.has(key))))
    findings.push(item("error", "CLD002", "Duplicate campaign or click-ID query parameters."));
  for (const [key, val] of pairs) {
    const low = key.toLowerCase();
    if (sensitive(key, val)) findings.push(item("error", "CLD003", "Potential PII or credential in query; input value hidden."));
    if (UTM.has(low) && !val.trim()) findings.push(item("error", "CLD004", "Campaign parameter is empty."));
    if (UTM.has(low) && (key !== low || val.trim() !== val))
      findings.push(item("warning", "CLD102", "Campaign casing or whitespace should be normalized."));
    if (TRACKERS.has(low)) findings.push(item("info", "CLD201", "Platform click identifier present; consider before sharing."));
  }
  if (keys.some((k) => k.startsWith("utm_"))) {
    const missing = REQUIRED.filter((key) => !keys.includes(key)).length;
    if (missing) findings.push(item("warning", "CLD103", missing + " recommended campaign parameter(s) absent."));
  }
  if (url.hash.toLowerCase().includes("utm_")) findings.push(item("warning", "CLD104", "Campaign tags inside a URL fragment may not reach analytics."));
  return {parameterCount: pairs.length, findings};
}
export function build(base, fields, replace = false) {
  const url = parse(base);
  for (const [key, val] of url.searchParams) if (sensitive(key, val))
    throw new Error("Base link appears to include PII or credentials in query");
  for (const required of ["source", "medium", "campaign"]) {
    if (!fields[required] || !String(fields[required]).trim() || CONTROL.test(String(fields[required])))
      throw new Error("Source, medium and campaign are required");
  }
  for (const value of Object.values(fields)) {
    if (CONTROL.test(String(value)) || EMAIL.test(String(value))) throw new Error("Campaign values cannot include email or control characters");
  }
  if ([...url.searchParams.keys()].some(k => k.toLowerCase().startsWith("utm_")) && !replace)
    throw new Error("Existing UTMs found. Tick Replace to overwrite them.");
  if (replace) for (const key of [...url.searchParams.keys()]) if (key.toLowerCase().startsWith("utm_")) url.searchParams.delete(key);
  for (const [key, field] of [["utm_source","source"],["utm_medium","medium"],["utm_campaign","campaign"],["utm_content","content"],["utm_term","term"]]) {
    const value = String(fields[field] || "").trim();
    if (value) url.searchParams.set(key, value);
  }
  return url.toString();
}
export function clean(raw) {
  const url = parse(raw);
  let removed = 0;
  for (const key of [...new Set(url.searchParams.keys())]) {
    const vals = url.searchParams.getAll(key);
    if (key.toLowerCase().startsWith("utm_") || TRACKERS.has(key.toLowerCase()) || vals.some(v => sensitive(key, v))) {
      removed += vals.length;
      url.searchParams.delete(key);
    }
  }
  return {url: url.toString(), removed};
}

