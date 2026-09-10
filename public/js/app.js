// API 설정
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : (window.API_BASE_URL || 'https://m1-2-2pob.onrender.com');

// 상태 관리
const state = {
    currentConversation: null,
    conversations: [],
    dataList: [],
};

// DOM 요소
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');
const loadingIndicator = document.getElementById('loading-indicator');
const summaryContent = document.getElementById('summary-content');
const dataForm = document.getElementById('data-form');
const dataList = document.getElementById('data-list');
const conversationsList = document.getElementById('conversations-list');
const conversationMessages = document.getElementById('conversation-messages');
const conversationTitle = document.getElementById('conversation-title');
const statisticsContent = document.getElementById('statistics-content');
const trendChart = document.getElementById('trend-chart');
const themeToggle = document.getElementById('theme-toggle');
const exportCsvBtn = document.getElementById('export-csv');
const exportJsonBtn = document.getElementById('export-json');

// ===== 탭 전환 =====
tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;

        // 버튼 상태 업데이트
        tabButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // 콘텐츠 표시
        tabContents.forEach(content => content.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');

        // 탭별 초기화
        if (tabName === 'data') {
            loadDataList();
        } else if (tabName === 'conversations') {
            loadConversationsList();
        }
    });
});

// ===== API 호출 함수 =====
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    try {
        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            if (response.status === 503) {
                throw new Error('서버 환경 설정 필요: Firebase/OpenAI 키를 확인하세요');
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API 호출 실패:', error);
        throw error;
    }
}

// ===== 채팅 기능 =====
async function loadSummary() {
    try {
        const summary = await apiCall('/api/data/summary');

        let summaryHtml = '';
        if (summary.period) {
            summaryHtml = `
                <p><strong>기간:</strong> ${summary.period}</p>
                <p><strong>레코드:</strong> ${summary.count}개</p>
                <p><strong>평균:</strong> ${formatNumber(summary.metrics?.average || 0)}</p>
                <p><strong>최대/최소:</strong> ${formatNumber(summary.metrics?.max || 0)} / ${formatNumber(summary.metrics?.min || 0)}</p>
                <p><strong>트렌드:</strong> ${summary.trend || '분석 중'}</p>
            `;
        } else {
            summaryHtml = '<p>아직 데이터가 없습니다. 데이터를 추가해주세요.</p>';
        }

        summaryContent.innerHTML = summaryHtml;
    } catch (error) {
        summaryContent.innerHTML = `<p style="color: #f44336;">데이터 요약을 불러올 수 없습니다: ${error.message}</p>`;
    }
}

// ===== 추가 지표 (보너스) =====
async function loadStatistics() {
    try {
        const stats = await apiCall('/api/data/statistics');
        statisticsContent.innerHTML = `
            <p><strong>중앙값:</strong> ${formatNumber(stats.median)}</p>
            <p><strong>표준편차:</strong> ${formatNumber(Math.round(stats.std_dev))}</p>
            <p><strong>최근 12개월 평균:</strong> ${formatNumber(Math.round(stats.recent_12m_average))}</p>
            <p><strong>전년 대비:</strong> ${stats.yoy_change_pct === null ? '데이터 부족(24개월 미만)' : `${stats.yoy_change_pct > 0 ? '+' : ''}${stats.yoy_change_pct.toFixed(1)}%`}</p>
        `;
    } catch (error) {
        statisticsContent.innerHTML = '';
    }
}

// ===== 추세 그래프 (보너스, 바닐라 Canvas) =====
function drawTrendChart(data) {
    if (!trendChart || !data || data.length === 0) return;

    const ctx = trendChart.getContext('2d');
    const width = trendChart.width;
    const height = trendChart.height;
    const padding = 24;

    ctx.clearRect(0, 0, width, height);

    const values = data.map(d => d.value);
    const maxV = Math.max(...values);
    const minV = Math.min(...values);
    const range = maxV - minV || 1;

    const isDark = document.body.getAttribute('data-theme') === 'dark';
    const lineColor = '#667eea';
    const fillColor = isDark ? 'rgba(102, 126, 234, 0.15)' : 'rgba(102, 126, 234, 0.1)';
    const axisColor = isDark ? '#3a3a55' : '#e0e0e0';

    const stepX = (width - padding * 2) / Math.max(values.length - 1, 1);
    const points = values.map((v, i) => {
        const x = padding + i * stepX;
        const y = height - padding - ((v - minV) / range) * (height - padding * 2);
        return [x, y];
    });

    // 기준선
    ctx.strokeStyle = axisColor;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    // 영역 채우기
    ctx.beginPath();
    ctx.moveTo(points[0][0], height - padding);
    points.forEach(([x, y]) => ctx.lineTo(x, y));
    ctx.lineTo(points[points.length - 1][0], height - padding);
    ctx.closePath();
    ctx.fillStyle = fillColor;
    ctx.fill();

    // 선 그리기
    ctx.beginPath();
    points.forEach(([x, y], i) => {
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = lineColor;
    ctx.lineWidth = 2;
    ctx.stroke();
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    // 사용자 메시지 표시
    addMessage(userMessage, 'user');
    chatInput.value = '';

    // 로딩 표시
    loadingIndicator.style.display = 'flex';

    try {
        // AI 응답 요청
        const response = await apiCall('/api/chat', {
            method: 'POST',
            body: JSON.stringify({ message: userMessage }),
        });

        // AI 응답 표시
        addMessage(response.reply, 'assistant');

        // 대화 저장 (자동)
        // 백엔드에서 /api/chat이 conversations에 자동 저장하므로 별도 호출 불필요

    } catch (error) {
        addMessage(`오류: ${error.message}`, 'assistant');
    } finally {
        loadingIndicator.style.display = 'none';
    }
});

function addMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ===== 데이터 관리 =====
dataForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const date = document.getElementById('data-date').value;
    const value = parseInt(document.getElementById('data-value').value);
    const memo = document.getElementById('data-memo').value || null;

    try {
        await apiCall('/api/data', {
            method: 'POST',
            body: JSON.stringify({ date, value, memo }),
        });

        // 폼 초기화 및 목록 새로고침
        dataForm.reset();
        await loadDataList();
        await loadSummary(); // 데이터가 추가되었으니 요약도 갱신

        showNotification('데이터가 추가되었습니다!');
    } catch (error) {
        showNotification(`오류: ${error.message}`, 'error');
    }
});

async function loadDataList() {
    try {
        const data = await apiCall('/api/data');
        state.dataList = data;
        drawTrendChart(data);

        if (!data || data.length === 0) {
            dataList.innerHTML = '<p class="empty-state">데이터가 없습니다. 추가해주세요.</p>';
            return;
        }

        dataList.innerHTML = data.map(item => `
            <div class="data-item">
                <div class="data-item-info">
                    <div class="data-item-date">${item.date}</div>
                    <div class="data-item-value">${formatNumber(item.value)}명</div>
                    ${item.memo ? `<div class="data-item-memo">${item.memo}</div>` : ''}
                </div>
                <div class="data-item-actions">
                    <button class="btn-sm btn-edit" onclick="editData('${item.id}')">수정</button>
                    <button class="btn-sm btn-delete" onclick="deleteData('${item.id}')">삭제</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        dataList.innerHTML = `<p class="empty-state" style="color: #f44336;">로드 실패: ${error.message}</p>`;
    }
}

async function deleteData(id) {
    if (!confirm('이 데이터를 삭제하시겠습니까?')) return;

    try {
        await apiCall(`/api/data/${id}`, { method: 'DELETE' });
        await loadDataList();
        await loadSummary();
        showNotification('데이터가 삭제되었습니다!');
    } catch (error) {
        showNotification(`오류: ${error.message}`, 'error');
    }
}

function editData(id) {
    const item = state.dataList.find(d => d.id === id);
    if (item) {
        document.getElementById('data-date').value = item.date;
        document.getElementById('data-value').value = item.value;
        document.getElementById('data-memo').value = item.memo || '';

        // TODO: PUT 요청 구현 (선택 사항)
        showNotification('수정 기능은 준비 중입니다. (삭제 후 재추가하세요)', 'info');
    }
}

// ===== 대화 기록 =====
async function loadConversationsList() {
    try {
        const conversations = await apiCall('/api/conversations');
        state.conversations = conversations;

        if (!conversations || conversations.length === 0) {
            conversationsList.innerHTML = '<p class="empty-state">대화 기록이 없습니다.</p>';
            return;
        }

        conversationsList.innerHTML = conversations.map(conv => `
            <div class="conversation-item" onclick="loadConversation('${conv.id}', event)">
                <div>${conv.title || '(빈 대화)'} <span style="opacity:0.6;font-size:12px;">(${conv.message_count}개 메시지)</span></div>
                <div class="conversation-date">${new Date(conv.created_at).toLocaleString('ko-KR')}</div>
            </div>
        `).join('');
    } catch (error) {
        conversationsList.innerHTML = `<p class="empty-state" style="color: #f44336;">로드 실패: ${error.message}</p>`;
    }
}

async function loadConversation(id, clickEvent) {
    try {
        const conv = await apiCall(`/api/conversations/${id}`);
        state.currentConversation = conv;

        // 선택 상태 표시
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        clickEvent?.target?.closest('.conversation-item')?.classList.add('active');

        // 메시지 표시
        conversationTitle.textContent = `대화 (${new Date(conv.created_at).toLocaleString('ko-KR')})`;
        conversationMessages.innerHTML = (conv.messages || []).map(msg => `
            <div class="message ${msg.role}">
                ${msg.content}
            </div>
        `).join('');

        if (!conv.messages || conv.messages.length === 0) {
            conversationMessages.innerHTML = '<p class="empty-state">메시지가 없습니다.</p>';
        }
    } catch (error) {
        conversationMessages.innerHTML = `<p class="empty-state" style="color: #f44336;">로드 실패: ${error.message}</p>`;
    }
}

// ===== 데이터 내보내기 (보너스) =====
function downloadBlob(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

exportCsvBtn?.addEventListener('click', () => {
    if (!state.dataList.length) {
        showNotification('내보낼 데이터가 없습니다.', 'info');
        return;
    }
    const header = 'date,value,memo';
    const rows = state.dataList.map(d => `${d.date},${d.value},"${(d.memo || '').replace(/"/g, '""')}"`);
    downloadBlob([header, ...rows].join('\n'), 'foreign_visitors_data.csv', 'text/csv;charset=utf-8');
});

exportJsonBtn?.addEventListener('click', () => {
    if (!state.dataList.length) {
        showNotification('내보낼 데이터가 없습니다.', 'info');
        return;
    }
    downloadBlob(JSON.stringify(state.dataList, null, 2), 'foreign_visitors_data.json', 'application/json');
});

// ===== 다크 모드 토글 (보너스) =====
function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    localStorage.setItem('theme', theme);
    if (state.dataList.length) drawTrendChart(state.dataList);
}

themeToggle?.addEventListener('click', () => {
    const current = document.body.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
});

// ===== 유틸리티 =====
function formatNumber(num) {
    if (typeof num !== 'number') return '0';
    return num.toLocaleString('ko-KR');
}

function showNotification(message, type = 'success') {
    // 간단한 알림 (필요시 toast 라이브러리 추가)
    console.log(`[${type.toUpperCase()}] ${message}`);
    alert(message);
}

// ===== 초기화 =====
document.addEventListener('DOMContentLoaded', async () => {
    // 저장된 테마 복원 (기본: light)
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    // 채팅 탭에서 시작
    await loadSummary();
    await loadStatistics();
    await loadDataList();
});
