function addTerminalLine(terminalId, line) {
    const terminalDiv = document.getElementById(terminalId);
    const lineElement = document.createElement('div');
    lineElement.className = 'line';

    const lineNumber = terminalDiv.childNodes.length + 1;
    const lineNoSpan = document.createElement('span');
    lineNoSpan.className = 'line-no';
    lineNoSpan.textContent = lineNumber + ':';
    lineElement.appendChild(lineNoSpan);

    const lineContentSpan = document.createElement('span');
    lineContentSpan.className = 'line-content';
    lineContentSpan.textContent = line;
    lineElement.appendChild(lineContentSpan);

    terminalDiv.appendChild(lineElement);
    terminalDiv.scrollTop = terminalDiv.scrollHeight;
}

function getFormData(form) {
    const formData = {};
    const inputs = form.elements;
    for (let i = 0; i < inputs.length; i++) {
        const input = inputs[i];
        if (input.name && input.type !== 'submit' && input.type !== 'button' && input.type !== 'reset') {
            formData[input.name] = input.value; // 设置对象的 key/value
        }
    }
    return formData;
}

function makeQueryParams(formData) {
    return Object.entries(formData)
        .filter(([_, value]) => value && value.trim() !== '')
        .map(([key, value]) => encodeURIComponent(key) + '=' + encodeURIComponent(value))
        .join('&');
}

function registerEventSource(formId, terminalId, endpoint) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', (event) => {
        event.preventDefault();

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
            addTerminalLine(terminalId, 'Done!');
            eventSource.close();
        });
        window.addEventListener('beforeunload', (event) => {
            eventSource.close();
        });
    });
}

