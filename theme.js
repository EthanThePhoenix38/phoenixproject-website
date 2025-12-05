// ===================================
// SYSTÈME DE THÈME & FONCTIONNALITÉS
// ===================================

// DARK MODE WCAG COMPLIANT
const ThemeManager = {
  init() {
    const savedTheme = this.getPreference('theme');
    if (savedTheme) {
      this.applyTheme(savedTheme);
    } else {
      this.applyTheme('light');
    }
    this.createThemeToggle();
  },

  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    this.updateThemeButton(theme);
  },

  toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = current === 'light' ? 'dark' : 'light';
    this.applyTheme(newTheme);
    this.savePreference('theme', newTheme);
  },

  updateThemeButton(theme) {
    const btn = document.getElementById('themeToggle');
    if (btn) {
      btn.textContent = theme === 'light' ? 'Dark' : 'Light';
      btn.setAttribute('aria-label', theme === 'light' ? 'Activer le mode sombre' : 'Activer le mode clair');
    }
  },

  createThemeToggle() {
    const btn = document.createElement('button');
    btn.id = 'themeToggle';
    btn.className = 'theme-toggle';
    btn.setAttribute('aria-label', 'Changer de thème');
    btn.onclick = () => this.toggleTheme();
    document.body.appendChild(btn);

    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    this.updateThemeButton(theme);
  },

  savePreference(key, value) {
    if (CookieManager.hasConsent()) {
      localStorage.setItem(key, value);
    }
  },

  getPreference(key) {
    return localStorage.getItem(key);
  }
};

// MENU DYNAMIQUE ACTIF
const NavigationManager = {
  init() {
    this.observeSections();
    this.setupSmoothScroll();
  },

  observeSections() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('nav a[href^="#"]');

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${entry.target.id}`) {
              link.classList.add('active');
            }
          });
        }
      });
    }, {
      threshold: 0.3,
      rootMargin: '-100px 0px -60% 0px'
    });

    sections.forEach(section => observer.observe(section));
  },

  setupSmoothScroll() {
    document.querySelectorAll('nav a[href^="#"]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        const target = document.getElementById(targetId);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }
};

// GESTION DES COOKIES RGPD
const CookieManager = {
  init() {
    if (!this.hasConsent() && !this.hasDecided()) {
      this.showBanner();
    }
  },

  hasConsent() {
    return this.getCookie('cookieConsent') === 'accepted';
  },

  hasDecided() {
    const decision = this.getCookie('cookieConsent');
    return decision === 'accepted' || decision === 'rejected';
  },

  accept() {
    this.setCookie('cookieConsent', 'accepted', 365);
    this.hideBanner();
    VisitTracker.init();
  },

  reject() {
    this.setCookie('cookieConsent', 'rejected', 365);
    this.hideBanner();
    localStorage.clear();
  },

  showBanner() {
    const banner = document.createElement('div');
    banner.id = 'cookieBanner';
    banner.className = 'cookie-banner';
    banner.innerHTML = `
      <div class="cookie-content">
        <p class="cookie-text">
          <span data-i18n="cookie.message">Nous utilisons des cookies pour améliorer votre expérience et analyser le trafic du site.</span>
        </p>
        <div class="cookie-buttons">
          <button onclick="CookieManager.accept()" class="cookie-btn cookie-accept" data-i18n="cookie.accept">Accepter</button>
          <button onclick="CookieManager.reject()" class="cookie-btn cookie-reject" data-i18n="cookie.reject">Refuser</button>
        </div>
      </div>
    `;
    document.body.appendChild(banner);
  },

  hideBanner() {
    const banner = document.getElementById('cookieBanner');
    if (banner) {
      banner.classList.add('fade-out');
      setTimeout(() => banner.remove(), 300);
    }
  },

  setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/;SameSite=Strict`;
  },

  getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }
};

// STATISTIQUES DES VISITES
const VisitTracker = {
  async init() {
    if (!CookieManager.hasConsent()) return;

    try {
      const response = await fetch('https://ipapi.co/json/');
      const data = await response.json();

      this.trackVisit({
        country: data.country_name,
        countryCode: data.country_code,
        page: 'home',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.log('Visit tracking unavailable');
    }
  },

  trackVisit(data) {
    const visits = JSON.parse(localStorage.getItem('visits') || '[]');
    visits.push(data);

    if (visits.length > 100) {
      visits.shift();
    }

    localStorage.setItem('visits', JSON.stringify(visits));
    this.updateStats();
  },

  updateStats() {
    const visits = JSON.parse(localStorage.getItem('visits') || '[]');
    const stats = {
      total: visits.length,
      byCountry: {}
    };

    visits.forEach(visit => {
      if (stats.byCountry[visit.country]) {
        stats.byCountry[visit.country]++;
      } else {
        stats.byCountry[visit.country] = 1;
      }
    });

    localStorage.setItem('visitStats', JSON.stringify(stats));
  },

  getStats() {
    return JSON.parse(localStorage.getItem('visitStats') || '{"total":0,"byCountry":{}}');
  }
};

// GESTION DES TEMPLATES
const TemplateManager = {
  templates: ['moderne', 'professionnel', 'fluide', 'epure'],

  init() {
    const savedTemplate = this.getPreference('template') || 'moderne';
    this.applyTemplate(savedTemplate);
    this.createTemplateSelector();
  },

  applyTemplate(template) {
    document.documentElement.setAttribute('data-template', template);
    this.updateTemplateButtons(template);
    this.savePreference('template', template);
  },

  updateTemplateButtons(activeTemplate) {
    document.querySelectorAll('.template-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.template === activeTemplate);
    });
  },

  createTemplateSelector() {
    const selector = document.createElement('div');
    selector.className = 'template-selector';
    selector.innerHTML = `
      <button class="template-btn" data-template="moderne" onclick="TemplateManager.applyTemplate('moderne')">
        Moderne
      </button>
      <button class="template-btn" data-template="professionnel" onclick="TemplateManager.applyTemplate('professionnel')">
        Professionnel
      </button>
      <button class="template-btn" data-template="fluide" onclick="TemplateManager.applyTemplate('fluide')">
        Fluide
      </button>
      <button class="template-btn" data-template="epure" onclick="TemplateManager.applyTemplate('epure')">
        Épuré
      </button>
    `;
    document.body.appendChild(selector);

    const savedTemplate = this.getPreference('template') || 'moderne';
    this.updateTemplateButtons(savedTemplate);
  },

  savePreference(key, value) {
    if (CookieManager.hasConsent()) {
      localStorage.setItem(key, value);
    }
  },

  getPreference(key) {
    return localStorage.getItem(key);
  }
};

// MENU À ONGLETS FLUIDE
const TabMenuManager = {
  tabs: [
    { id: 'home', label: 'Accueil', section: 'home' },
    { id: 'services', label: 'Services', section: 'services' },
    { id: 'expertise', label: 'Expertise', section: 'expertise' },
    { id: 'contact', label: 'Contact', section: 'contact' }
  ],

  init() {
    this.createTabMenu();
    this.setupTabInteractions();
  },

  createTabMenu() {
    const menu = document.createElement('div');
    menu.className = 'tab-menu';
    menu.id = 'tabMenu';

    this.tabs.forEach(tab => {
      const tabEl = document.createElement('div');
      tabEl.className = 'tab-item';
      tabEl.dataset.tab = tab.id;
      tabEl.innerHTML = `
        <span>${tab.label}</span>
        <span class="tab-close" onclick="TabMenuManager.closeTab('${tab.id}', event)">×</span>
      `;
      tabEl.addEventListener('click', (e) => {
        if (!e.target.classList.contains('tab-close')) {
          this.scrollToSection(tab.section);
        }
      });
      menu.appendChild(tabEl);
    });

    document.body.appendChild(menu);
  },

  setupTabInteractions() {
    const sections = document.querySelectorAll('section[id]');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.setActiveTab(entry.target.id);
        }
      });
    }, {
      threshold: 0.5,
      rootMargin: '-100px 0px -40% 0px'
    });

    sections.forEach(section => observer.observe(section));
  },

  setActiveTab(sectionId) {
    document.querySelectorAll('.tab-item').forEach(tab => {
      tab.classList.toggle('active', tab.dataset.tab === sectionId);
    });
  },

  scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  },

  closeTab(tabId, event) {
    event.stopPropagation();
    const tabEl = document.querySelector(`[data-tab="${tabId}"]`);
    if (tabEl) {
      tabEl.style.animation = 'fadeOutTab 0.3s ease-out';
      setTimeout(() => {
        tabEl.remove();
        this.tabs = this.tabs.filter(t => t.id !== tabId);
      }, 300);
    }
  }
};

// INITIALISATION GLOBALE
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  TemplateManager.init();
  NavigationManager.init();
  TabMenuManager.init();
  CookieManager.init();

  if (CookieManager.hasConsent()) {
    VisitTracker.init();
  }
});
