function clearTerminal(terminalId) {
    const terminalDiv = document.getElementById(terminalId);
    terminalDiv.innerHTML = '';
}

function addTerminalLine(terminalId, line) {
    const terminal = document.getElementById(terminalId);
    const lineElement = document.createElement('div');
    lineElement.className = 'line';

    const lineNumber = terminal.childNodes.length + 1;
    const lineNoSpan = document.createElement('span');
    lineNoSpan.className = 'line-no';
    lineNoSpan.textContent = lineNumber + ':';
    lineElement.appendChild(lineNoSpan);

    const lineContentSpan = document.createElement('span');
    lineContentSpan.className = 'line-content';
    lineContentSpan.textContent = line;
    lineElement.appendChild(lineContentSpan);

    terminal.appendChild(lineElement);
    terminal.scrollTop = terminal.scrollHeight;
}

function getFormData(form) {
    const formData = {};
    for (const input of form.elements) {
        if (!input.name || input.type === 'submit') continue;
        if (input.type === 'checkbox') {
            formData[input.name] = input.checked;
        } else if (input.type !== 'radio' || input.checked) {
            formData[input.name] = input.value;
        }
    }
    return formData;
}

function makeQueryParams(formData) {
    return Object.entries(formData)
        .filter(([_, value]) => value !== null && value !== undefined && String(value).trim() !== '')
        .map(([key, value]) => encodeURIComponent(key) + '=' + encodeURIComponent(value))
        .join('&');
}

function registerEventSource(formId, terminalId, endpoint) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        clearTerminal(terminalId);

        const formData = getFormData(form);
        console.log(`formData: ${JSON.stringify(formData)}`);
        const queryParams = makeQueryParams(formData);
        console.log(`queryParams: ${queryParams}`);

        const eventSource = new EventSource(`${endpoint}?${queryParams}`);
        eventSource.addEventListener('message', (event) => {
            addTerminalLine(terminalId, event.data);
        });
        eventSource.addEventListener('error', (event) => {
            addTerminalLine(terminalId, 'Error!');
            eventSource.close();
        });
        eventSource.addEventListener('done', (event) => {
            addTerminalLine(terminalId, event.data);
            addTerminalLine(terminalId, 'Done!');
            eventSource.close();
        });
        window.addEventListener('beforeunload', (event) => {
            eventSource.close();
        });
    });
}

