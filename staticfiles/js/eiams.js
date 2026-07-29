/* EIAMS — Main JavaScript  */
'use strict';

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar toggle (mobile) ───────────────────────────────
  const sidebar  = document.getElementById('sidebar');
  const toggle   = document.getElementById('sidebarToggle');
  const overlay  = document.getElementById('sidebarOverlay');

  function openSidebar() {
    if (!sidebar) return;
    sidebar.classList.add('show');
    if (overlay) { overlay.classList.add('show'); overlay.removeAttribute('aria-hidden'); }
    if (toggle) toggle.setAttribute('aria-expanded', 'true');
  }

  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove('show');
    if (overlay) { overlay.classList.remove('show'); overlay.setAttribute('aria-hidden', 'true'); }
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  }

  if (toggle)  toggle.addEventListener('click', openSidebar);
  if (overlay) overlay.addEventListener('click', closeSidebar);

  window.addEventListener('resize', function () {
    if (window.innerWidth >= 992) closeSidebar();
  });

  // ── Topbar scroll shadow via .main-scroll ─────────────────
  // Body never scrolls — the scroll region is #mainScroll
  const mainScroll = document.getElementById('mainScroll');
  const topbar     = document.getElementById('topbar');
  if (mainScroll && topbar) {
    mainScroll.addEventListener('scroll', function () {
      topbar.classList.toggle('scrolled', this.scrollTop > 4);
    }, { passive: true });
  }

  // ── Auto-dismiss success / info alerts ───────────────────
  document.querySelectorAll('.alert.alert-success, .alert.alert-info').forEach(function (el) {
    setTimeout(function () {
      const bsAlert = bootstrap && bootstrap.Alert ? bootstrap.Alert.getOrCreateInstance(el) : null;
      if (bsAlert) bsAlert.close();
    }, 4500);
  });

  // ── Confirm delete / destructive actions ─────────────────
  document.querySelectorAll('[data-confirm]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (!confirm(this.dataset.confirm || 'Are you sure? This cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  // ── Bootstrap tooltips ───────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el, { trigger: 'hover' });
  });

  // ── Preserve filter params in pagination links ────────────
  document.querySelectorAll('.pagination .page-link[href]').forEach(function (link) {
    try {
      const url  = new URL(link.href, window.location.origin);
      const curr = new URLSearchParams(window.location.search);
      curr.forEach(function (val, key) {
        if (key !== 'page') url.searchParams.set(key, val);
      });
      link.href = url.toString();
    } catch (e) { /* ignore */ }
  });

});
