// API configuration - works when served directly or via separate port
const API_BASE = window.location.port === "8000" ? "/api/v1" : "http://localhost:8000/api/v1";

let currentUser = null;
let currentBrowsePage = 1;
let currentLostReportForMatches = null;

// Initial Setup
document.addEventListener("DOMContentLoaded", () => {
  checkAuth();
  loadDashboard();
  setDefaultDate();
});

function setDefaultDate() {
  const today = new Date().toISOString().split("T")[0];
  const dateInput = document.getElementById("approximate_date");
  if (dateInput) dateInput.value = today;
}

// Toast Notifications
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Authentication
function getToken() {
  return localStorage.getItem("access_token");
}

function setToken(token) {
  localStorage.setItem("access_token", token);
}

function removeToken() {
  localStorage.removeItem("access_token");
}

function authHeaders(isJson = true) {
  const headers = {};
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (isJson) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

async function checkAuth() {
  const token = getToken();
  if (!token) {
    updateAuthUI(null);
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/auth/me`, { headers: authHeaders() });
    if (res.ok) {
      currentUser = await res.json();
      updateAuthUI(currentUser);
    } else {
      removeToken();
      updateAuthUI(null);
    }
  } catch (err) {
    console.error("Auth check failed:", err);
    updateAuthUI(null);
  }
}

function updateAuthUI(user) {
  const userDisplay = document.getElementById("user-display");
  const authBtn = document.getElementById("auth-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const authRequiredNavs = document.querySelectorAll(".auth-required");
  const authWarning = document.getElementById("auth-warning-report");

  if (user) {
    userDisplay.textContent = `👤 ${user.name} (${user.email})`;
    userDisplay.style.display = "block";
    authBtn.style.display = "none";
    logoutBtn.style.display = "inline-block";
    authRequiredNavs.forEach(nav => nav.style.display = "inline-block");
    if (authWarning) authWarning.style.display = "none";
  } else {
    userDisplay.textContent = "";
    userDisplay.style.display = "none";
    authBtn.style.display = "inline-block";
    logoutBtn.style.display = "none";
    authRequiredNavs.forEach(nav => nav.style.display = "none");
    if (authWarning) authWarning.style.display = "block";
  }
}

function openAuthModal() {
  document.getElementById("auth-modal").classList.add("active");
}

function closeAuthModal() {
  document.getElementById("auth-modal").classList.remove("active");
}

function switchAuthTab(tab) {
  const loginForm = document.getElementById("login-form");
  const regForm = document.getElementById("register-form");
  const tabLogin = document.getElementById("modal-tab-login");
  const tabReg = document.getElementById("modal-tab-register");

  if (tab === "login") {
    loginForm.style.display = "block";
    regForm.style.display = "none";
    tabLogin.classList.add("active");
    tabReg.classList.remove("active");
  } else {
    loginForm.style.display = "none";
    regForm.style.display = "block";
    tabLogin.classList.remove("active");
    tabReg.classList.add("active");
  }
}

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.message || "Invalid credentials", "error");
      return;
    }
    setToken(data.access_token);
    currentUser = data.user;
    updateAuthUI(currentUser);
    closeAuthModal();
    showToast(`Welcome back, ${currentUser.name}!`, "success");
    loadDashboard();
  } catch (err) {
    showToast("Network error logging in", "error");
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const name = document.getElementById("reg-name").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;

  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.message || "Registration failed", "error");
      return;
    }
    showToast("Registration successful! Logging in...", "success");
    // Automatically log in
    const loginRes = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const loginData = await loginRes.json();
    if (loginRes.ok) {
      setToken(loginData.access_token);
      currentUser = loginData.user;
      updateAuthUI(currentUser);
      closeAuthModal();
      loadDashboard();
    }
  } catch (err) {
    showToast("Network error registering", "error");
  }
}

function logout() {
  removeToken();
  currentUser = null;
  updateAuthUI(null);
  showToast("Logged out successfully", "info");
  navigate("dashboard");
}

// Navigation Tabs
function navigate(tabName) {
  document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));

  const targetPane = document.getElementById(`pane-${tabName}`);
  const targetBtn = document.querySelector(`.nav-btn[data-tab="${tabName}"]`);

  if (targetPane) targetPane.classList.add("active");
  if (targetBtn) targetBtn.classList.add("active");

  if (tabName === "dashboard") loadDashboard();
  if (tabName === "browse") applySearch(1);
  if (tabName === "my-reports") loadMyReports();
  if (tabName === "my-claims") loadMyClaims();
}

// Dashboard
async function loadDashboard() {
  try {
    const [lostRes, foundRes] = await Promise.all([
      fetch(`${API_BASE}/reports/search?report_type=LOST&page=1&page_size=4`),
      fetch(`${API_BASE}/reports/search?report_type=FOUND&page=1&page_size=4`)
    ]);

    const lostData = await lostRes.json();
    const foundData = await foundRes.json();

    renderDashboardList("recent-lost-list", lostData.items || [], "LOST");
    renderDashboardList("recent-found-list", foundData.items || [], "FOUND");
  } catch (err) {
    console.error("Error loading dashboard:", err);
  }
}

function renderDashboardList(containerId, items, type) {
  const container = document.getElementById(containerId);
  if (!items || items.length === 0) {
    container.innerHTML = `<div style="grid-column: 1/-1; padding: 1rem; color: var(--text-muted); text-align: center;">No ${type.toLowerCase()} items reported recently.</div>`;
    return;
  }

  container.innerHTML = items.map(item => createReportCardHTML(item)).join("");
}

// Report Card HTML generator
function createReportCardHTML(item, options = {}) {
  const isOwner = currentUser && item.user_id === currentUser.id;
  const isFound = item.report_type === "FOUND";
  const isLost = item.report_type === "LOST";

  const imgHTML = item.image_path
    ? `<img src="/${item.image_path}" class="report-img" alt="${escapeHTML(item.item_name)}">`
    : `<div class="report-img-placeholder">📷 No image attached</div>`;

  const badgeClass = item.report_type === "LOST" ? "badge-lost" : "badge-found";
  const statusClass = `badge-status-${item.status.toLowerCase().replace('_', '-')}`;

  let actionBtns = "";

  if (isLost && (isOwner || options.showMatches)) {
    actionBtns += `<button class="btn btn-sm btn-primary" onclick="viewMatchesForReport(${item.id}, '${escapeHTML(item.item_name)}')">🎯 View Matches</button>`;
  }

  if (isFound && currentUser && !isOwner && item.status === "ACTIVE") {
    actionBtns += `<button class="btn btn-sm btn-success" onclick="openClaimModal(${item.id}, '${escapeHTML(item.item_name)}')">🛡️ Claim This Item</button>`;
  }

  if (options.isMyReport) {
    if (item.status === "ACTIVE") {
      actionBtns += `<button class="btn btn-sm btn-danger" onclick="closeReport(${item.id})">Close</button>`;
    }
  }

  return `
    <div class="report-card">
      ${imgHTML}
      <div class="report-body">
        <div class="report-header">
          <span class="badge ${badgeClass}">${item.report_type}</span>
          <span class="badge ${statusClass}">${item.status}</span>
        </div>
        <div class="report-title">${escapeHTML(item.item_name)}</div>
        <div class="report-meta">
          <span>📁 Category: <strong>${escapeHTML(item.category)}</strong></span>
          <span>📍 Location: <strong>${escapeHTML(item.location)}</strong></span>
          <span>📅 Date: <strong>${item.approximate_date}</strong></span>
        </div>
        <div class="report-desc">${escapeHTML(item.description)}</div>
        ${actionBtns ? `<div class="report-actions">${actionBtns}</div>` : ""}
      </div>
    </div>
  `;
}

// Browse & Search
function filterBrowse(type) {
  document.getElementById("search-type").value = type;
  navigate("browse");
}

function resetSearch() {
  document.getElementById("search-keyword").value = "";
  document.getElementById("search-category").value = "";
  document.getElementById("search-type").value = "";
  document.getElementById("search-location").value = "";
  document.getElementById("search-date-from").value = "";
  document.getElementById("search-date-to").value = "";
  applySearch(1);
}

async function applySearch(page = 1) {
  currentBrowsePage = page;
  const keyword = document.getElementById("search-keyword").value.trim();
  const category = document.getElementById("search-category").value;
  const report_type = document.getElementById("search-type").value;
  const location = document.getElementById("search-location").value.trim();
  const date_from = document.getElementById("search-date-from").value;
  const date_to = document.getElementById("search-date-to").value;

  const params = new URLSearchParams({
    page: page,
    page_size: 9
  });
  if (keyword) params.append("keyword", keyword);
  if (category) params.append("category", category);
  if (report_type) params.append("report_type", report_type);
  if (location) params.append("location", location);
  if (date_from) params.append("date_from", date_from);
  if (date_to) params.append("date_to", date_to);

  const container = document.getElementById("browse-cards-container");
  container.innerHTML = "<div>Loading reports...</div>";

  try {
    const res = await fetch(`${API_BASE}/reports/search?${params.toString()}`);
    const data = await res.json();
    
    document.getElementById("browse-results-count").textContent = `Found ${data.total} reports (Page ${data.page} of ${data.total_pages || 1})`;
    
    if (!data.items || data.items.length === 0) {
      container.innerHTML = `<div style="grid-column: 1/-1; padding: 2rem; text-align: center; color: var(--text-muted);">No reports match your search criteria.</div>`;
    } else {
      container.innerHTML = data.items.map(item => createReportCardHTML(item, { showMatches: true })).join("");
    }

    renderPagination(data.page, data.total_pages);
  } catch (err) {
    container.innerHTML = `<div style="color:red;">Error loading reports.</div>`;
  }
}

function renderPagination(currentPage, totalPages) {
  const container = document.getElementById("pagination-controls");
  if (!totalPages || totalPages <= 1) {
    container.innerHTML = "";
    return;
  }

  let html = "";
  if (currentPage > 1) {
    html += `<button class="btn btn-sm btn-secondary" onclick="applySearch(${currentPage - 1})">Prev</button>`;
  }
  html += `<span style="font-size: 0.85rem; font-weight: 500;">${currentPage} / ${totalPages}</span>`;
  if (currentPage < totalPages) {
    html += `<button class="btn btn-sm btn-secondary" onclick="applySearch(${currentPage + 1})">Next</button>`;
  }
  container.innerHTML = html;
}

// Create Report
async function handleCreateReport(e) {
  e.preventDefault();
  if (!currentUser) {
    showToast("Please login or register to submit a report", "error");
    openAuthModal();
    return;
  }

  const reportType = document.querySelector('input[name="report_type"]:checked').value;
  const itemName = document.getElementById("item_name").value.trim();
  const category = document.getElementById("category").value;
  const approximateDate = document.getElementById("approximate_date").value;
  const location = document.getElementById("location").value.trim();
  const description = document.getElementById("description").value.trim();
  const imageFile = document.getElementById("image_file").files[0];

  const submitBtn = document.getElementById("submit-report-btn");
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting...";

  try {
    let res;
    if (imageFile) {
      const formData = new FormData();
      formData.append("item_name", itemName);
      formData.append("category", category);
      formData.append("approximate_date", approximateDate);
      formData.append("location", location);
      formData.append("description", description);
      formData.append("report_type", reportType);
      formData.append("image", imageFile);

      res = await fetch(`${API_BASE}/reports/upload`, {
        method: "POST",
        headers: authHeaders(false),
        body: formData
      });
    } else {
      res = await fetch(`${API_BASE}/reports`, {
        method: "POST",
        headers: authHeaders(true),
        body: JSON.stringify({
          item_name: itemName,
          category,
          approximate_date: approximateDate,
          location,
          description,
          report_type: reportType
        })
      });
    }

    const data = await res.json();
    if (!res.ok) {
      showToast(data.message || "Failed to create report", "error");
      return;
    }

    showToast(`Successfully created ${reportType} report!`, "success");
    document.getElementById("create-report-form").reset();
    setDefaultDate();

    // If it was a LOST report, automatically view matches
    if (reportType === "LOST") {
      viewMatchesForReport(data.id, data.item_name);
    } else {
      navigate("browse");
    }
  } catch (err) {
    showToast("Network error submitting report", "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit Report";
  }
}

// Matching Engine View
async function viewMatchesForReport(lostId, lostTitle) {
  currentLostReportForMatches = lostId;
  navigate("matches");

  document.getElementById("matches-lost-title").textContent = `Matches for: ${lostTitle}`;
  const container = document.getElementById("matches-container");
  container.innerHTML = "<div>Running matching algorithm against active FOUND items...</div>";

  try {
    const res = await fetch(`${API_BASE}/reports/${lostId}/matches`, {
      headers: authHeaders()
    });
    const data = await res.json();

    if (!res.ok) {
      container.innerHTML = `<div style="color:red;">${data.message || "Could not retrieve matches."}</div>`;
      return;
    }

    const matches = data.matches;
    if (!matches || matches.length === 0) {
      container.innerHTML = `
        <div class="card" style="grid-column: 1/-1; text-align: center; padding: 2rem;">
          <h3>No Strong Candidates Found Yet</h3>
          <p class="text-muted" style="margin-top: 0.5rem;">
            The deterministic matching engine found no active FOUND items scoring above the matching threshold.
            Check back later as new found items are reported!
          </p>
        </div>
      `;
      return;
    }

    container.innerHTML = matches.map(m => `
      <div class="card" style="border-left: 4px solid var(--primary);">
        <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom: 0.5rem;">
          <div>
            <h3 style="font-size: 1.1rem;">${escapeHTML(m.item_name)}</h3>
            <span class="badge badge-found" style="margin-top: 0.25rem;">FOUND ITEM #${m.found_report_id}</span>
          </div>
          <div class="score-badge">${m.similarity_score}% Match</div>
        </div>

        <div class="report-meta" style="margin-top:0.5rem;">
          <span>📍 Found at: <strong>${escapeHTML(m.location)}</strong></span>
          <span>📅 Date: <strong>${m.approximate_date}</strong></span>
          <span>📁 Category: <strong>${escapeHTML(m.category)}</strong></span>
        </div>
        <p style="font-size:0.875rem; margin-bottom:0.75rem;">${escapeHTML(m.description)}</p>

        <!-- Explainable Attribute Breakdown -->
        <div class="meter-group">
          <div style="display:flex; justify-content:space-between;"><span>Category Similarity (30%)</span><span>${m.score_breakdown.category}%</span></div>
          <div class="meter-bar"><div class="meter-fill" style="width: ${m.score_breakdown.category}%;"></div></div>

          <div style="display:flex; justify-content:space-between;"><span>Item Name Similarity (30%)</span><span>${m.score_breakdown.item_name}%</span></div>
          <div class="meter-bar"><div class="meter-fill" style="width: ${m.score_breakdown.item_name}%;"></div></div>

          <div style="display:flex; justify-content:space-between;"><span>Description Similarity (20%)</span><span>${m.score_breakdown.description}%</span></div>
          <div class="meter-bar"><div class="meter-fill" style="width: ${m.score_breakdown.description}%;"></div></div>

          <div style="display:flex; justify-content:space-between;"><span>Location Similarity (10%)</span><span>${m.score_breakdown.location}%</span></div>
          <div class="meter-bar"><div class="meter-fill" style="width: ${m.score_breakdown.location}%;"></div></div>

          <div style="display:flex; justify-content:space-between;"><span>Date Proximity (10%)</span><span>${m.score_breakdown.date}%</span></div>
          <div class="meter-bar"><div class="meter-fill" style="width: ${m.score_breakdown.date}%;"></div></div>
        </div>

        <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--border); display: flex; justify-content: flex-end;">
          <button class="btn btn-success" onclick="openClaimModal(${m.found_report_id}, '${escapeHTML(m.item_name)}', ${lostId})">🛡️ Submit Claim For This Item</button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div style="color:red;">Error fetching potential matches.</div>`;
  }
}

// My Reports
async function loadMyReports() {
  const container = document.getElementById("my-reports-list");
  container.innerHTML = "<div>Loading your reports...</div>";

  try {
    const res = await fetch(`${API_BASE}/reports/my`, { headers: authHeaders() });
    const reports = await res.json();

    if (!reports || reports.length === 0) {
      container.innerHTML = `<div style="grid-column: 1/-1; padding: 2rem; text-align: center; color: var(--text-muted);">You have not reported any items yet.</div>`;
      return;
    }

    container.innerHTML = reports.map(r => createReportCardHTML(r, { isMyReport: true })).join("");
  } catch (err) {
    container.innerHTML = `<div style="color:red;">Error loading your reports.</div>`;
  }
}

async function closeReport(reportId) {
  if (!confirm("Are you sure you want to close this report? It will no longer appear in active searches or matching.")) return;

  try {
    const res = await fetch(`${API_BASE}/reports/${reportId}`, {
      method: "DELETE",
      headers: authHeaders()
    });
    if (res.ok) {
      showToast("Report successfully closed.", "success");
      loadMyReports();
    } else {
      const data = await res.json();
      showToast(data.message || "Failed to close report", "error");
    }
  } catch (err) {
    showToast("Network error closing report", "error");
  }
}

// Claims Management
async function openClaimModal(foundReportId, itemName, linkedLostId = null) {
  if (!currentUser) {
    showToast("Please login or register to submit a claim", "error");
    openAuthModal();
    return;
  }

  document.getElementById("claim-found-report-id").value = foundReportId;
  document.getElementById("claim-target-info").innerHTML = `Claiming: <strong>${escapeHTML(itemName)}</strong> (Found Report #${foundReportId})`;
  document.getElementById("claim-verification-details").value = "";

  // Populate claimant's lost reports in dropdown
  const select = document.getElementById("claim-lost-report-select");
  select.innerHTML = `<option value="">None (Claim without linking report)</option>`;

  try {
    const res = await fetch(`${API_BASE}/reports/my`, { headers: authHeaders() });
    const reports = await res.json();
    const lostReports = reports.filter(r => r.report_type === "LOST" && r.status === "ACTIVE");

    lostReports.forEach(r => {
      const opt = document.createElement("option");
      opt.value = r.id;
      opt.textContent = `#${r.id}: ${r.item_name} (${r.approximate_date})`;
      if (linkedLostId && r.id === linkedLostId) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });
  } catch (err) {
    console.error("Could not load lost reports for claim dropdown:", err);
  }

  document.getElementById("claim-modal").classList.add("active");
}

function closeClaimModal() {
  document.getElementById("claim-modal").classList.remove("active");
}

async function handleSubmitClaim(e) {
  e.preventDefault();
  const reportId = parseInt(document.getElementById("claim-found-report-id").value);
  const lostSelect = document.getElementById("claim-lost-report-select").value;
  const lostReportId = lostSelect ? parseInt(lostSelect) : null;
  const verificationDetails = document.getElementById("claim-verification-details").value.trim();

  try {
    const res = await fetch(`${API_BASE}/claims`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        report_id: reportId,
        lost_report_id: lostReportId,
        verification_details: verificationDetails
      })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.message || "Failed to submit claim", "error");
      return;
    }

    showToast("Claim successfully filed! Status: PENDING", "success");
    closeClaimModal();
    navigate("my-claims");
  } catch (err) {
    showToast("Network error submitting claim", "error");
  }
}

async function loadMyClaims() {
  const container = document.getElementById("my-claims-list");
  container.innerHTML = "<div>Loading your claims...</div>";

  try {
    const res = await fetch(`${API_BASE}/claims/my`, { headers: authHeaders() });
    const claims = await res.json();

    if (!claims || claims.length === 0) {
      container.innerHTML = `<div style="grid-column: 1/-1; padding: 2rem; text-align: center; color: var(--text-muted);">You have not submitted any claims yet.</div>`;
      return;
    }

    container.innerHTML = claims.map(c => `
      <div class="card" style="border-left: 4px solid var(--secondary);">
        <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom: 0.5rem;">
          <div>
            <h3 style="font-size: 1.05rem;">Claim #${c.id} for Found Item #${c.report_id}</h3>
            ${c.lost_report_id ? `<span style="font-size:0.75rem; color:var(--text-muted);">Linked to your Lost Report #${c.lost_report_id}</span>` : ""}
          </div>
          <span class="badge badge-status-${c.status.toLowerCase()}">${c.status}</span>
        </div>
        <div style="background:#f8fafc; padding:0.75rem; border-radius:4px; font-size:0.85rem; margin: 0.5rem 0;">
          <strong>Your Private Verification Details:</strong><br>
          ${escapeHTML(c.verification_details)}
        </div>
        <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom: 0.5rem;">
          Submitted: ${new Date(c.created_at).toLocaleString()}
        </div>
        ${c.status === "PENDING" ? `
          <div style="display:flex; justify-content:flex-end;">
            <button class="btn btn-sm btn-danger" onclick="withdrawClaim(${c.id})">Withdraw Claim</button>
          </div>
        ` : ""}
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div style="color:red;">Error loading claims.</div>`;
  }
}

async function withdrawClaim(claimId) {
  if (!confirm("Are you sure you want to withdraw this claim? Withdrawn claims cannot be reactivated.")) return;

  try {
    const res = await fetch(`${API_BASE}/claims/${claimId}/withdraw`, {
      method: "POST",
      headers: authHeaders()
    });
    if (res.ok) {
      showToast("Claim successfully withdrawn.", "success");
      loadMyClaims();
    } else {
      const data = await res.json();
      showToast(data.message || "Failed to withdraw claim", "error");
    }
  } catch (err) {
    showToast("Network error withdrawing claim", "error");
  }
}

function escapeHTML(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
