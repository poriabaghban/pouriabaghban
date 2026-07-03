(function () {
    "use strict";

    const shell = document.querySelector(".chat-shell");
    if (!shell) return;

    const roomId = shell.dataset.roomId;
    const userId = Number(shell.dataset.userId);
    const uploadUrl = shell.dataset.uploadUrl;
    const messagesUrl = shell.dataset.messagesUrl;
    const chunkSize = Number(shell.dataset.chunkSize || 1048576);
    const maxFileSize = Number(shell.dataset.maxFileSize || 314572800);
    const messagesEl = document.getElementById("messages");
    const typingLine = document.getElementById("typingLine");
    const onlineCount = document.getElementById("onlineCount");
    const statusEl = document.getElementById("connectionStatus");
    const form = document.getElementById("composerForm");
    const input = document.getElementById("messageInput");
    const fileInput = document.getElementById("fileInput");
    const uploadQueue = document.getElementById("uploadQueue");
    const emojiPicker = document.getElementById("emojiPicker");
    const emojiToggle = document.getElementById("emojiToggle");
    const themeToggle = document.getElementById("themeToggle");
    const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
    const blockedChars = ["<", ">", "}", "/", "\"", "'"];
    const emojiVariation = "\uFE0F";
    const emojiJoiner = "\u200D";
    const emojiKeycaps = ["#️⃣", "*️⃣", "0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"];
    const emojiSkinTones = ["🏻", "🏼", "🏽", "🏾", "🏿"];
    const emojiManualGroups = {
        recent: ["😀", "😂", "🤣", "😍", "😘", "😊", "😎", "🥰", "🙏", "👍", "👏", "❤️", "🔥", "✨", "🎉", "✅", "❌", "💯", "🚀", "📎", "📌", "💬", "☕", "🌙"],
        smileys: ["☺️", "☹️", "☠️", "👁️‍🗨️", "❤️‍🔥", "❤️‍🩹"],
        people: ["👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤌", "🤏", "✌️", "🤞", "🫰", "🤟", "🤘", "🤙", "👈", "👉", "👆", "🖕", "👇", "☝️", "🫵", "👍", "👎", "✊", "👊", "🤛", "🤜", "👏", "🙌", "🫶", "👐", "🤲", "🤝", "🙏", "✍️", "💅", "🤳", "💪", "🦾", "🦿", "🦵", "🦶", "👂", "🦻", "👃", "🧠", "🫀", "🫁", "🦷", "🦴", "👀", "👁️", "👅", "👄"],
        symbols: ["❤️", "🩷", "🧡", "💛", "💚", "💙", "🩵", "💜", "🤎", "🖤", "🩶", "🤍", "💔", "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "☮️", "✝️", "☪️", "🕉️", "☸️", "✡️", "🔯", "🕎", "☯️", "☦️", "🛐", "⛎", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓", "⚛️", "🆔", "⚕️", "☢️", "☣️", "📴", "📳", "🈶", "🈚", "🈸", "🈺", "🈷️", "✴️", "🆚", "💮", "🉐", "㊙️", "㊗️", "🈴", "🈵", "🈹", "🈲", "🅰️", "🅱️", "🆎", "🆑", "🅾️", "🆘", "❌", "⭕", "🛑", "⛔", "📛", "🚫", "💯", "💢", "♨️", "🚷", "🚯", "🚳", "🚱", "🔞", "📵", "🚭", "❗", "❕", "❓", "❔", "‼️", "⁉️", "🔅", "🔆", "〽️", "⚠️", "🚸", "🔱", "⚜️", "🔰", "♻️", "✅", "🈯", "💹", "❇️", "✳️", "❎", "🌐", "💠", "Ⓜ️", "🌀", "💤", "🏧", "🚾", "♿", "🅿️", "🈳", "🈂️", "🛂", "🛃", "🛄", "🛅", "🚹", "🚺", "🚼", "⚧️", "🚻", "🚮", "🎦", "📶", "🈁", "🔣", "ℹ️", "🔤", "🔡", "🔠", "🆖", "🆗", "🆙", "🆒", "🆕", "🆓", "0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "🔢", "#️⃣", "*️⃣", "⏏️", "▶️", "⏸️", "⏯️", "⏹️", "⏺️", "⏭️", "⏮️", "⏩", "⏪", "⏫", "⏬", "◀️", "🔼", "🔽", "➡️", "⬅️", "⬆️", "⬇️", "↗️", "↘️", "↙️", "↖️", "↕️", "↔️", "↪️", "↩️", "⤴️", "⤵️", "🔀", "🔁", "🔂", "🔄", "🔃", "🎵", "🎶", "➕", "➖", "➗", "✖️", "🟰", "♾️", "💲", "💱", "™️", "©️", "®️", "〰️", "➰", "➿", "🔚", "🔙", "🔛", "🔝", "🔜", "✔️", "☑️", "🔘", "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "⚫", "⚪", "🟤", "🔺", "🔻", "🔸", "🔹", "🔶", "🔷", "🔳", "🔲", "▪️", "▫️", "◾", "◽", "◼️", "◻️", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "⬛", "⬜", "🟫"],
        flags: []
    };

    function charsFromRange(start, end, withVariation) {
        const items = [];
        for (let code = start; code <= end; code += 1) {
            items.push(String.fromCodePoint(code) + (withVariation ? emojiVariation : ""));
        }
        return items;
    }

    function regionalFlag(first, second) {
        const base = 0x1F1E6;
        return String.fromCodePoint(base + first.charCodeAt(0) - 65) + String.fromCodePoint(base + second.charCodeAt(0) - 65);
    }

    function uniqueEmojis(items) {
        return Array.from(new Set(items));
    }

    function addSkinToneVariants(items) {
        const withVariants = [];
        items.forEach((emoji) => {
            withVariants.push(emoji);
            if (!/[\u{1F3FB}-\u{1F3FF}]/u.test(emoji)) {
                emojiSkinTones.forEach((tone) => withVariants.push(emoji + tone));
            }
        });
        return withVariants;
    }

    const countryCodes = "AC AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CP CR CU CV CW CX CY CZ DE DG DJ DK DM DO DZ EA EC EE EG EH ER ES ET EU FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU IC ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TA TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM UN US UY UZ VA VC VE VG VI VN VU WF WS XK YE YT ZA ZM ZW".split(" ");
    emojiManualGroups.flags = countryCodes.map((code) => regionalFlag(code[0], code[1]));

    const emojiCategories = [
        {key: "recent", icon: "🕘", title: "پرکاربرد", items: emojiManualGroups.recent},
        {key: "smileys", icon: "😊", title: "صورتک‌ها", items: uniqueEmojis([...charsFromRange(0x1F600, 0x1F64F), ...emojiManualGroups.smileys])},
        {key: "people", icon: "👋", title: "آدم‌ها", items: uniqueEmojis(addSkinToneVariants([...emojiManualGroups.people, ...charsFromRange(0x1F466, 0x1F487), ...charsFromRange(0x1F9D0, 0x1F9FF), ...charsFromRange(0x1FAF0, 0x1FAF8)]))},
        {key: "nature", icon: "🌿", title: "طبیعت", items: uniqueEmojis([...charsFromRange(0x1F300, 0x1F3FF), ...charsFromRange(0x1F980, 0x1F9AE), ...charsFromRange(0x1FAB0, 0x1FABF), ...charsFromRange(0x2600, 0x26FF, true)])},
        {key: "food", icon: "🍔", title: "غذا", items: uniqueEmojis([...charsFromRange(0x1F32D, 0x1F37F), ...charsFromRange(0x1F950, 0x1F96F), ...charsFromRange(0x1FAD0, 0x1FAD9)])},
        {key: "activity", icon: "⚽", title: "فعالیت", items: uniqueEmojis([...charsFromRange(0x1F380, 0x1F3C4), ...charsFromRange(0x1F3C5, 0x1F3FF), ...charsFromRange(0x1F93A, 0x1F945), ...charsFromRange(0x1F947, 0x1F94F)])},
        {key: "travel", icon: "🚀", title: "سفر", items: uniqueEmojis([...charsFromRange(0x1F680, 0x1F6FF), ...charsFromRange(0x1F5FA, 0x1F5FF, true), ...charsFromRange(0x2708, 0x27BF, true)])},
        {key: "objects", icon: "💡", title: "اشیا", items: uniqueEmojis([...charsFromRange(0x1F4A0, 0x1F5FF), ...charsFromRange(0x1F900, 0x1F97F), ...charsFromRange(0x1FA70, 0x1FAFF)])},
        {key: "symbols", icon: "❤️", title: "نمادها", items: uniqueEmojis([...emojiKeycaps, ...emojiManualGroups.symbols])},
        {key: "flags", icon: "🏳️", title: "پرچم‌ها", items: uniqueEmojis(["🏁", "🚩", "🎌", "🏴", "🏳️", "🏳️‍🌈", "🏳️‍⚧️", "🏴‍☠️", ...emojiManualGroups.flags])}
    ];

    let socket = null;
    let page = 1;
    let hasNextPage = true;
    let loadingMessages = false;
    let selectedFiles = [];
    let typingTimer = null;
    let reconnectAttempts = 0;
    const pendingUploads = new Map();
    const messageAttachments = new Map();

    function applyTheme(theme) {
        const nextTheme = theme === "night" ? "night" : "day";
        document.body.dataset.chatTheme = nextTheme;
        if (themeToggle) themeToggle.textContent = nextTheme === "night" ? "☾" : "☀";
        window.localStorage.setItem("adminChatTheme", nextTheme);
    }

    function escapeHtml(value) {
        return String(value || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function setStatus(state) {
        statusEl.classList.remove("connected", "disconnected", "waiting");
        if (state === "connected") {
            statusEl.textContent = "وصل";
            statusEl.classList.add("connected");
        } else if (state === "disconnected") {
            statusEl.textContent = "قطع اتصال";
            statusEl.classList.add("disconnected");
        } else {
            statusEl.textContent = "درحال انتظار";
            statusEl.classList.add("waiting");
        }
    }

    function hasBlockedChars(value) {
        return blockedChars.some((char) => String(value || "").includes(char));
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

    function isImageAttachment(attachment) {
        const contentType = String(attachment.content_type || "").toLowerCase();
        if (contentType.startsWith("image/")) return true;
        return /\.(avif|apng|bmp|gif|heic|heif|ico|jfif|jpe?g|pjpeg|pjp|png|svg|tif|tiff|webp)$/i.test(attachment.filename || attachment.url || "");
    }

    function buildImageHtml(images) {
        if (!images.length) return "";
        if (images.length === 1) {
            const image = images[0];
            return `<a href="${escapeHtml(image.url)}" target="_blank" rel="noopener">
                <img class="image-single" src="${escapeHtml(image.url)}" alt="${escapeHtml(image.filename)}" loading="lazy">
            </a>`;
        }
        const slides = images.map((image, index) => {
            return `<a class="image-slide ${index === 0 ? "active" : ""}" href="${escapeHtml(image.url)}" target="_blank" rel="noopener" data-slide-index="${index}">
                <img src="${escapeHtml(image.url)}" alt="${escapeHtml(image.filename)}" loading="lazy">
            </a>`;
        }).join("");
        return `<div class="image-slider" data-active-slide="0" data-slide-count="${images.length}">
            ${slides}
            <button class="image-slider-control prev" type="button" data-slider-action="prev" title="قبلی">‹</button>
            <button class="image-slider-control next" type="button" data-slider-action="next" title="بعدی">›</button>
            <span class="image-slider-count">1 / ${images.length}</span>
        </div>`;
    }

    function buildAttachmentHtml(attachments) {
        if (!attachments || !attachments.length) return "";
        const images = attachments.filter(isImageAttachment);
        const files = attachments.filter((attachment) => !isImageAttachment(attachment));
        const imageHtml = buildImageHtml(images);
        const links = files.map((attachment) => {
            return `<a class="attachment-link" href="${escapeHtml(attachment.url)}" target="_blank" rel="noopener">
                <span>${escapeHtml(attachment.filename)}</span>
                <small>${formatBytes(Number(attachment.size || 0))}</small>
            </a>`;
        }).join("");
        return `<div class="attachment-area">${imageHtml}${links ? `<div class="attachment-list">${links}</div>` : ""}</div>`;
    }

    function updateAttachmentArea(messageId, bubble) {
        let area = bubble.querySelector(".attachment-area");
        const html = buildAttachmentHtml(messageAttachments.get(String(messageId)) || []);
        if (!html) {
            if (area) area.remove();
            return;
        }
        if (!area) {
            area = document.createElement("div");
            area.className = "attachment-area";
            bubble.appendChild(area);
        }
        const wrapper = document.createElement("div");
        wrapper.innerHTML = html;
        area.replaceWith(wrapper.firstElementChild);
    }

    function renderMessage(message, prepend) {
        if (document.querySelector(`[data-message-id="${message.id}"]`)) return;
        const row = document.createElement("div");
        row.className = "message-row " + (Number(message.sender_id) === userId ? "mine" : "theirs");
        row.dataset.messageId = message.id;
        messageAttachments.set(String(message.id), message.attachments || []);
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
        if (prepend) messagesEl.prepend(row); else messagesEl.appendChild(row);
        if (Number(message.sender_id) !== userId && socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({type: "read", message_id: message.id}));
        }
    }

    function appendAttachment(messageId, attachment) {
        const row = document.querySelector(`[data-message-id="${messageId}"] .message-bubble`);
        if (!row) return;
        const key = String(messageId);
        const attachments = messageAttachments.get(key) || [];
        if (!attachments.some((item) => Number(item.id) === Number(attachment.id))) {
            attachments.push(attachment);
        }
        messageAttachments.set(key, attachments);
        updateAttachmentArea(key, row);
    }

    function moveImageSlider(slider, direction) {
        const slides = Array.from(slider.querySelectorAll(".image-slide"));
        if (!slides.length) return;
        const current = Number(slider.dataset.activeSlide || 0);
        const next = (current + direction + slides.length) % slides.length;
        slides.forEach((slide, index) => slide.classList.toggle("active", index === next));
        slider.dataset.activeSlide = String(next);
        const count = slider.querySelector(".image-slider-count");
        if (count) count.textContent = `${next + 1} / ${slides.length}`;
    }

    async function loadMessages(prepend) {
        if (loadingMessages || !hasNextPage) return;
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
            if (prepend) messagesEl.scrollTop = messagesEl.scrollHeight - oldHeight; else scrollToBottom();
        }
        loadingMessages = false;
    }

    function reconnectDelay() {
        return Math.min(12000, 1200 * Math.max(1, reconnectAttempts));
    }

    function connectSocket() {
        if (!navigator.onLine) {
            setStatus("waiting");
            window.setTimeout(connectSocket, reconnectDelay());
            return;
        }
        setStatus("waiting");
        const scheme = window.location.protocol === "https:" ? "wss" : "ws";
        socket = new WebSocket(`${scheme}://${window.location.host}/ws/chat/${roomId}/`);

        socket.onopen = function () {
            reconnectAttempts = 0;
            setStatus("connected");
        };

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
                if (files && files.length) uploadFiles(data.message.id, files);
            }
            if (data.type === "attachment_added") {
                appendAttachment(data.message_id, data.attachment);
                if (isNearBottom()) scrollToBottom();
            }
            if (data.type === "typing") {
                typingLine.textContent = data.is_typing ? `${data.username} در حال تایپ است...` : "";
                if (data.is_typing) {
                    window.clearTimeout(typingTimer);
                    typingTimer = window.setTimeout(() => typingLine.textContent = "", 1800);
                }
            }
            if (data.type === "online_count") onlineCount.textContent = data.online_count;
            if (data.type === "error") {
                if (data.message === "قطع اتصال") setStatus("disconnected");
                window.alert(data.message);
            }
        };

        socket.onclose = function () {
            reconnectAttempts += 1;
            setStatus(navigator.onLine ? "disconnected" : "waiting");
            window.setTimeout(connectSocket, reconnectDelay());
        };

        socket.onerror = function () {
            setStatus(navigator.onLine ? "disconnected" : "waiting");
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
                formData.append("file_type", file.type || "");
                formData.append("file_size", file.size);
                formData.append("chunk_index", chunkIndex);
                formData.append("total_chunks", totalChunks);
                formData.append("chunk", file.slice(start, end, file.type || "application/octet-stream"), file.name);

                const response = await fetch(uploadUrl, {
                    method: "POST",
                    headers: {"X-CSRFToken": csrfToken, "X-Requested-With": "XMLHttpRequest"},
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

    function insertEmoji(emoji) {
        input.setRangeText(emoji, input.selectionStart, input.selectionEnd, "end");
        input.focus();
    }

    function renderEmojiPicker() {
        const search = document.createElement("input");
        search.className = "emoji-search";
        search.type = "search";
        search.placeholder = "جستجوی ایموجی";
        search.autocomplete = "off";

        const tabs = document.createElement("div");
        tabs.className = "emoji-tabs";
        tabs.setAttribute("role", "tablist");

        const grid = document.createElement("div");
        grid.className = "emoji-grid";

        let activeCategory = emojiCategories[0].key;

        function drawButtons(items) {
            grid.innerHTML = "";
            items.forEach((emoji) => {
                const button = document.createElement("button");
                button.className = "emoji-button";
                button.type = "button";
                button.textContent = emoji;
                button.title = emoji;
                button.addEventListener("click", function () {
                    insertEmoji(emoji);
                });
                grid.appendChild(button);
            });
        }

        function selectCategory(categoryKey) {
            activeCategory = categoryKey;
            search.value = "";
            tabs.querySelectorAll(".emoji-tab").forEach((tab) => {
                tab.classList.toggle("active", tab.dataset.category === activeCategory);
            });
            const category = emojiCategories.find((item) => item.key === activeCategory) || emojiCategories[0];
            drawButtons(category.items);
            grid.scrollTop = 0;
        }

        emojiCategories.forEach((category) => {
            const tab = document.createElement("button");
            tab.className = "emoji-tab";
            tab.type = "button";
            tab.textContent = category.icon;
            tab.title = category.title;
            tab.dataset.category = category.key;
            tab.addEventListener("click", function () {
                selectCategory(category.key);
            });
            tabs.appendChild(tab);
        });

        search.addEventListener("input", function () {
            const query = search.value.trim().toLowerCase();
            if (!query) {
                const category = emojiCategories.find((item) => item.key === activeCategory) || emojiCategories[0];
                drawButtons(category.items);
                return;
            }
            const results = uniqueEmojis(emojiCategories.flatMap((category) => {
                const categoryText = `${category.key} ${category.title}`.toLowerCase();
                return categoryText.includes(query) ? category.items : [];
            }));
            drawButtons(results);
        });

        emojiPicker.appendChild(search);
        emojiPicker.appendChild(tabs);
        emojiPicker.appendChild(grid);
        selectCategory(activeCategory);
    }

    renderEmojiPicker();

    applyTheme(window.localStorage.getItem("adminChatTheme") || "day");

    if (themeToggle) {
        themeToggle.addEventListener("click", function () {
            applyTheme(document.body.dataset.chatTheme === "night" ? "day" : "night");
        });
    }

    emojiToggle.addEventListener("click", function () {
        emojiPicker.classList.toggle("show");
    });

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
        if (!text && !files.length) return;
        if (hasBlockedChars(text)) {
            window.alert("Input contains forbidden characters: < > } / \" '.");
            return;
        }
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            setStatus("disconnected");
            window.alert("اتصال چت برقرار نیست.");
            return;
        }
        const clientMessageId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
        if (files.length) pendingUploads.set(clientMessageId, files);
        try {
            socket.send(JSON.stringify({type: "message", text: text, client_message_id: clientMessageId}));
        } catch (error) {
            pendingUploads.delete(clientMessageId);
            setStatus("disconnected");
            window.alert("قطع اتصال");
            return;
        }
        input.value = "";
        fileInput.value = "";
        emojiPicker.classList.remove("show");
    });

    messagesEl.addEventListener("scroll", function () {
        if (messagesEl.scrollTop < 80) loadMessages(true);
    });

    messagesEl.addEventListener("click", function (event) {
        const button = event.target.closest("[data-slider-action]");
        if (!button) return;
        event.preventDefault();
        const slider = button.closest(".image-slider");
        if (!slider) return;
        moveImageSlider(slider, button.dataset.sliderAction === "next" ? 1 : -1);
    });

    window.addEventListener("offline", function () {
        setStatus("waiting");
    });

    window.addEventListener("online", function () {
        setStatus("waiting");
        if (!socket || socket.readyState === WebSocket.CLOSED) connectSocket();
    });

    loadMessages(false);
    connectSocket();
})();
