/* Render a small, safe subset of Markdown: paragraphs, lists, bold, italic, code.
   Text is inserted with textContent, so model output cannot become HTML. */
function renderMarkdown(host, source) {
  host.replaceChildren();
  const lines = String(source || "").replace(/\r\n/g, "\n").split("\n");
  let index = 0;
  while (index < lines.length) {
    if (!lines[index].trim()) {
      index += 1;
      continue;
    }
    if (isListItem(lines[index])) {
      const ordered = /^\d+\. /.test(lines[index]);
      const list = document.createElement(ordered ? "ol" : "ul");
      while (index < lines.length && isListItem(lines[index])) {
        const item = document.createElement("li");
        appendInline(item, lines[index].replace(/^([-*]|\d+\.) /, ""));
        list.appendChild(item);
        index += 1;
      }
      host.appendChild(list);
      continue;
    }
    const paragraph = [];
    while (index < lines.length && lines[index].trim() && !isListItem(lines[index])) {
      paragraph.push(lines[index].trim());
      index += 1;
    }
    const block = document.createElement("p");
    appendInline(block, paragraph.join(" "));
    host.appendChild(block);
  }
}

function isListItem(line) {
  return /^[-*] /.test(line) || /^\d+\. /.test(line);
}

function appendInline(parent, text) {
  const pattern = /\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`/g;
  let last = 0;
  for (const match of text.matchAll(pattern)) {
    if (match.index > last) {
      parent.appendChild(document.createTextNode(text.slice(last, match.index)));
    }
    const node = document.createElement(match[1] != null ? "strong" : match[2] != null ? "em" : "code");
    node.textContent = match[1] || match[2] || match[3];
    parent.appendChild(node);
    last = match.index + match[0].length;
  }
  if (last < text.length) parent.appendChild(document.createTextNode(text.slice(last)));
}
