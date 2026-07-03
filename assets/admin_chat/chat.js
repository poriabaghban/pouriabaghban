(function () {
    "use strict";

    const shell = document.querySelector(".chat-shell");
    if (!shell) {
        return;
    }

    const roomId = shell.dataset.roomId;
    const userId = Number(shell.dataset.userId);
    const uploadUrl = shell.dataset.uploadUrl;
    const messagesUrl = shell.dataset.messagesUrl;
    const chunkSize = Number(shell.dataset.chunkSize || 1048576);
    const maxFileSize = Number(shell.dataset.maxFileSize || 314572800);
    const messagesEl = document.getElementById("messages");
    const typingLine = document.getElementById("typingLine");
    const onlineCount = document.getElementById("onlineCount");
    const form = document.getElementById("composerForm");
    const input = document.getElementById("messageInput");
    const fileInput = document.getElementById("fileInput");
    const uploadQueue = document.getElementById("uploadQueue");
    const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;

    let socket = null;
    let page = 1;
    let hasNextPage = true;
    let loadingMessages = false;
    let selectedFiles = [];
    let typingTimer = null;
    const pendingUploads = new Map();

    function escapeHtml(value) {
        return String(value || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatBytes(bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    }

    function formatTime(isoValue) {
        try {
            return new Intl.DateTimeFormat("fa-IR", {
                hour: "2-digit",
                minute: "2-digit",
                year: "numeric",
                month: "2-digit",
                day: "2-digit"
            }).format(new Date(isoValue));
        } catch (error) {
            return "";
        }
    }

    function scrollToBottom() {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function isNearBottom() {
        return messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 120;
    }

    function buildAttachmentHtml(attachments) {
        if (!attachments || !attachments.length) {
            return "";
        }
        const links = attachments.map((attachment) => {
            return `<a class="attachment-link" href="${escapeHtml(attachment.url)}" target="_blank" rel="noopener">
                <span>${escapeHtml(attachment.filename)}</span>
                <small>${formatBytes(Number(attachment.size || 0))}</small>
            </a>`;
        }).join("");
        return `<div class="attachment-list">${links}</div>`;
    }

    function renderMessage(message, prepend) {
        if (document.querySelector(`[data-message-id="${message.id}"]`)) {
            return;
        }
        const row = document.createElement("div");
        row.className = "message-row " + (Number(message.sender_id) === userId ? "mine" : "theirs");
        row.dataset.messageId = message.id;
        row.innerHTML = `
            <article class="message-bubble">
                <div class="message-meta">
                    <strong>${escapeHtml(message.sender_username)}</strong>
                    <span>${formatTime(message.timestamp)}</span>
                </div>
                ${message.text ? `<div class="message-text">${escapeHtml(message.text)}</div>` : ""}
                ${buildAttachmentHtml(message.attachments)}
            </article>
        `;
        if (prepend) {
            messagesEl.prepend(row);
        } else {
            messagesEl.appendChild(row);
        }
        if (Number(message.sender_id) !== userId && socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({type: "read", message_id: message.id}));
        }
    }

    function appendAttachment(messageId, attachment) {
        const row = document.querySelector(`[data-message-id="${messageId}"] .message-bubble`);
        if (!row) {
            return;
        }
        let list = row.querySelector(".attachment-list");
        if (!list) {
            list = document.createElement("div");
            list.className = "attachment-list";
            row.appendChild(list);
        }
        const link = document.createElement("a");
        link.className = "attachment-link";
        link.href = attachment.url;
        link.target = "_blank";
        link.rel = "noopener";
        link.innerHTML = `<span>${escapeHtml(attachment.filename)}</span><small>${formatBytes(Number(attachment.size || 0))}</small>`;
        list.appendChild(link);
    }

    async function loadMessages(prepend) {
        if (loadingMessages || !hasNextPage) {
            return;
        }
        loadingMessages = true;
        const oldHeight = messagesEl.scrollHeight;
        const response = await fetch(`${messagesUrl}?page=${page}&page_size=30`, {
            headers: {"X-Requested-With": "XMLHttpRequest"}
        });
        if (response.ok) {
            const data = await response.json();
            data.messages.forEach((message) => renderMessage(message, prepend));
            hasNextPage = data.has_next;
            page += 1;
            if (prepend) {
                messagesEl.scrollTop = messagesEl.scrollHeight - oldHeight;
            } else {
                scrollToBottom();
            }
        }
        loadingMessages = false;
    }

    function connectSocket() {
        const scheme = window.location.protocol === "https:" ? "wss" : "ws";
        socket = new WebSocket(`${scheme}://${window.location.host}/ws/chat/${roomId}/`);

        socket.onmessage = function (event) {
            const data = JSON.parse(event.data);
            if (data.type === "message") {
                const bottom = isNearBottom();
                renderMessage(data.message, false);
                if (bottom) scrollToBottom();
            }
            if (data.type === "message_ack") {
                const files = pendingUploads.get(data.client_message_id);
                pendingUploads.delete(data.client_message_id);
                if (files && files.length) {
                    uploadFiles(data.message.id, files);
                }
            }
            if (data.type === "attachment_added") {
                appendAttachment(data.message_id, data.attachment);
                if (isNearBottom()) scrollToBottom();
            }
            if (data.type === "typing") {
                typingLine.textContent = data.is_typing ? `${data.username} در حال نوشتن است...` : "";
                if (data.is_typing) {
                    window.clearTimeout(typingTimer);
                    typingTimer = window.setTimeout(() => typingLine.textContent = "", 1800);
                }
            }
            if (data.type === "online_count") {
                onlineCount.textContent = data.online_count;
            }
            if (data.type === "error") {
                window.alert(data.message);
            }
        };

        socket.onclose = function () {
            window.setTimeout(connectSocket, 2500);
        };
    }

    function renderUploadQueue() {
        uploadQueue.innerHTML = "";
        selectedFiles.forEach((file, index) => {
            const item = document.createElement("div");
            item.className = "upload-item";
            item.dataset.fileIndex = index;
            item.innerHTML = `
                <div class="d-flex justify-content-between small mb-1">
                    <span>${escapeHtml(file.name)}</span>
                    <span>${formatBytes(file.size)}</span>
                </div>
                <div class="progress" role="progressbar" aria-valuemin="0" aria-valuemax="100">
                    <div class="progress-bar" style="width:0%">0%</div>
                </div>
            `;
            uploadQueue.appendChild(item);
        });
    }

    function updateProgress(index, percent) {
        const bar = uploadQueue.querySelector(`[data-file-index="${index}"] .progress-bar`);
        if (bar) {
            bar.style.width = `${percent}%`;
            bar.textContent = `${percent}%`;
        }
    }

    async function uploadFiles(messageId, files) {
        for (let fileIndex = 0; fileIndex < files.length; fileIndex += 1) {
            const file = files[fileIndex];
            if (file.size > maxFileSize) {
                window.alert(`حجم ${file.name} بیشتر از حد مجاز است.`);
                continue;
            }
            const uploadId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
            const totalChunks = Math.ceil(file.size / chunkSize);
            for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex += 1) {
                const start = chunkIndex * chunkSize;
                const end = Math.min(start + chunkSize, file.size);
                const formData = new FormData();
                formData.append("room_id", roomId);
                formData.append("message_id", messageId);
                formData.append("upload_id", uploadId);
                formData.append("file_name", file.name);
                formData.append("file_size", file.size);
                formData.append("chunk_index", chunkIndex);
                formData.append("total_chunks", totalChunks);
                formData.append("chunk", file.slice(start, end), file.name);

                const response = await fetch(uploadUrl, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: formData
                });
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    window.alert(errorData.error || "آپلود فایل ناموفق بود.");
                    break;
                }
                updateProgress(fileIndex, Math.round(((chunkIndex + 1) / totalChunks) * 100));
            }
        }
        selectedFiles = [];
        window.setTimeout(() => uploadQueue.innerHTML = "", 800);
    }

    fileInput.addEventListener("change", function () {
        selectedFiles = Array.from(fileInput.files || []);
        renderUploadQueue();
    });

    input.addEventListener("input", function () {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({type: "typing", is_typing: true}));
            window.clearTimeout(typingTimer);
            typingTimer = window.setTimeout(() => {
                socket.send(JSON.stringify({type: "typing", is_typing: false}));
            }, 900);
        }
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        const text = input.value.trim();
        const files = selectedFiles.slice();
        if (!text && !files.length) {
            return;
        }
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            window.alert("اتصال چت برقرار نیست.");
            return;
        }
        const clientMessageId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
        if (files.length) {
            pendingUploads.set(clientMessageId, files);
        }
        socket.send(JSON.stringify({type: "message", text: text, client_message_id: clientMessageId}));
        input.value = "";
        fileInput.value = "";
    });

    messagesEl.addEventListener("scroll", function () {
        if (messagesEl.scrollTop < 80) {
            loadMessages(true);
        }
    });

    loadMessages(false);
    connectSocket();
})();
