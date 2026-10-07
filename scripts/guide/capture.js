// Captures d'écran du guide : parcourt l'interface d'Odoo 18 (en français) sur une base où sont installées les
// deux sociétés de démonstration, et enregistre une image PNG par écran.
//
// Prérequis : base préparée par scripts/guide/prepare_db.sh (langue française, données de démonstration,
// administrateur « admin » / « admin »), serveur Odoo démarré sur cette base ; Node.js et Playwright
// (npm install playwright ; navigateur Chromium, chemin dans CHROMIUM si besoin).
// Usage : node scripts/guide/capture.js http://127.0.0.1:8069 docs/guide/captures [nom de capture…]
'use strict';
const path = require('path');
const { chromium } = require('playwright');

const [BASE = 'http://127.0.0.1:8069', OUT = 'docs/guide/captures', ...ONLY] = process.argv.slice(2);
const BAR = 'Bar-Hôtel Démo AITE';
const IT = 'Services Informatiques Démo AITE';

async function main() {
  const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'fr-FR' });
  const page = await context.newPage();
  const host = new URL(BASE).hostname;

  // ------------------------------------------------------------------ outils
  async function settle(extra = 900) {
    await page.waitForSelector('.o_action_manager .o_action, .o_action_manager .o_view_controller',
      { timeout: 30000 }).catch(() => {});
    await page.waitForFunction(() => !document.querySelector('.o_blockUI, .o_loading_indicator'), null,
      { timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(extra);
  }
  async function rpc(model, method, args, kwargs = {}) {
    return page.evaluate(async ({ model, method, args, kwargs }) => {
      const response = await fetch(`/web/dataset/call_kw/${model}/${method}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: { model, method, args, kwargs } }),
      });
      const data = await response.json();
      if (data.error) throw new Error(JSON.stringify(data.error));
      return data.result;
    }, { model, method, args, kwargs });
  }
  async function useCompany(name) {
    const [company] = await rpc('res.company', 'search_read', [[['name', '=', name]]], { fields: ['id'] });
    await context.addCookies([{ name: 'cids', value: String(company.id), domain: host, path: '/' }]);
    return company.id;
  }
  async function open(url, extra) {
    await page.goto(BASE + url);
    await settle(extra);
  }
  async function menu(section, item) {
    await page.click(`.o_menu_sections button:has-text("${section}"), .o_menu_sections a:has-text("${section}")`);
    await page.waitForTimeout(500);
    if (item) {
      await page.click(`.o-dropdown--menu .dropdown-item:has-text("${item}")`);
      await settle(1500);
    }
  }
  async function search(text) {
    await page.click('.o_searchview_input');
    await page.fill('.o_searchview_input', text);
    await page.keyboard.press('Enter');
    await settle();
  }
  async function moveId(company, ref) {
    const [move] = await rpc('account.move', 'search_read', [[['company_id', '=', company], ['ref', '=', ref]]],
      { fields: ['id'], limit: 1 });
    return move.id;
  }
  async function declarationId(company, dateFrom) {
    const [decl] = await rpc('aite.cm.vat.declaration', 'search_read',
      [[['company_id', '=', company], ['date_from', '=', dateFrom]]], { fields: ['id', 'move_id'], limit: 1 });
    return decl;
  }
  async function tab(label) {
    await page.click(`.o_notebook .nav-link:has-text("${label}")`);
    await page.waitForTimeout(700);
  }
  async function setDate(field, value) {
    const input = page.locator(`div[name="${field}"] input`);
    await input.click();
    await input.fill(value);
    await page.keyboard.press('Enter');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);
  }
  async function mis(statement) {
    await open('/odoo/accounting');
    await menu('Analyse', statement);
    await page.waitForSelector('table.mis_builder tbody tr', { timeout: 60000 });
    await page.waitForTimeout(800);
  }
  async function onlyRows(first, last) {  // extrait d'une liste de lignes du formulaire : de « first » à « last »
    await page.evaluate(({ first, last }) => {
      const number = code => parseInt(code.replace(/^L/, ''), 10);
      document.querySelectorAll('div[name="itvair_line_ids"] tbody tr.o_data_row').forEach(row => {
        const code = row.querySelector('td[name="code"]')?.textContent.trim() || '';
        if (!/^L\d+$/.test(code) || number(code) < number(first) || number(code) > number(last)) row.style.display = 'none';
      });
    }, { first, last });
    await page.waitForTimeout(300);
  }
  async function shot(name, options = {}) {
    await page.mouse.move(1430, 890);
    await page.screenshot({ path: path.join(OUT, `${name}.png`), ...options });
    console.log('capture', name);
  }

  // ------------------------------------------------------------------ connexion
  await page.goto(BASE + '/web/login');
  await page.fill('input[name=login]', 'admin');
  await page.fill('input[name=password]', 'admin');
  await Promise.all([page.waitForURL(/\/odoo/), page.click('button[type=submit]')]);
  await settle();
  const bar = await useCompany(BAR);

  const SHOTS = {
    async '01-applications'() {
      await open('/odoo/apps');
      await page.click('.o_searchview_facet .o_facet_remove').catch(() => {});
      await search('SYSCOHADA');
      await shot('01-applications');
    },
    async '02-tableau-de-bord'() {
      await open('/odoo/accounting');
      await shot('02-tableau-de-bord');
    },
    async '03-menu-syscohada'() {
      await open('/odoo/accounting');
      await menu('Analyse');
      await shot('03-menu-syscohada');
      await page.keyboard.press('Escape');
    },
    async '04-etats-controles'() {
      await open('/odoo/accounting');
      await menu('Analyse', 'États et contrôles (AITE)');
      await setDate('date_from', '01/01/2025');
      await setDate('date_to', '31/12/2025');
      await page.click('button[name="action_compute"]');
      await settle(1500);
      await shot('04-etats-controles');
      await tab('Bilan actif');
      await shot('05-etats-bilan-actif');
    },
    async '06-bilan-actif'() {
      await mis('Bilan actif');
      await shot('06-bilan-actif');
    },
    async '07-bilan-passif'() {
      await mis('Bilan passif');
      await shot('07-bilan-passif');
    },
    async '08-compte-de-resultat'() {
      await mis('Compte de résultat');
      await shot('08-compte-de-resultat');
    },
    async '09-flux-de-tresorerie'() {
      await mis('Tableau des flux de trésorerie');
      await shot('09-flux-de-tresorerie');
    },
    async '10-declarations'() {
      await open('/odoo/accounting');
      await menu('Analyse', 'Déclarations de TVA (Cameroun)');
      await shot('10-declarations');
    },
    async '11-declaration-tva'() {
      const decl = await declarationId(bar, '2026-09-01');
      await open(`/odoo/action-aite_syscohada_community.action_aite_cm_vat_declaration/${decl.id}`);
      await shot('11-declaration-tva');
      await tab('Retenues, acomptes, IRCM, salaires');
      await shot('12-declaration-retenues');
      await onlyRows('L36', 'L55');
      await page.locator('div[name="itvair_line_ids"]').scrollIntoViewIfNeeded();
      await shot('13-declaration-recapitulatif');
    },
    async '14-declaration-imprimee'() {
      const decl = await declarationId(bar, '2026-09-01');
      await page.goto(`${BASE}/report/html/aite_syscohada_community.report_itvair/${decl.id}`);
      await page.waitForTimeout(1500);
      await shot('14-declaration-imprimee');
    },
    async '15-liquidation'() {
      const decl = await declarationId(bar, '2026-08-01');
      await open(`/odoo/account.move/${decl.move_id[0]}`);
      await shot('15-liquidation');
    },
    async '16-facture-nuitees'() {
      await open(`/odoo/account.move/${await moveId(bar, 'HEB-2026-09')}`);
      await shot('16-facture-nuitees');
    },
    async '17-facture-loyer'() {
      await open(`/odoo/account.move/${await moveId(bar, 'LOY-2026-09')}`);
      await shot('17-facture-loyer');
    },
    async '18-logiciel-etranger'() {
      await open(`/odoo/account.move/${await moveId(bar, 'LOG-2026-07')}`);
      await tab('Écritures comptables');
      await shot('18-logiciel-etranger');
    },
    async '19-paie'() {
      await open(`/odoo/account.move/${await moveId(bar, 'Paie 09/2026')}`);
      await shot('19-paie');
    },
    async '20-plan-comptable'() {
      await open('/odoo/action-account.action_account_form');
      await search('447');
      await shot('20-plan-comptable');
    },
    async '21-taxes'() {
      await open('/odoo/action-account.action_tax_form');
      await search('valider');
      await shot('21-taxes');
    },
    async '22-configuration'() {
      await page.setViewportSize({ width: 1440, height: 1180 });  // menu entier, section Syscohada comprise
      await open('/odoo/accounting');
      await menu('Configuration');
      await shot('22-configuration');
      await page.keyboard.press('Escape');
      await page.setViewportSize({ width: 1440, height: 900 });
    },
    async '23-rubriques'() {
      await open('/odoo/action-aite_syscohada_base.action_aite_syscohada_rubrique');
      await page.click('.o_group_header:has-text("Bilan actif")');
      await settle(800);
      await shot('23-rubriques');
    },
    async '24-societes'() {
      await open('/odoo/accounting');
      await page.click('.o_switch_company_menu button, .o_switch_company_menu .dropdown-toggle');
      await page.waitForTimeout(700);
      await shot('24-societes');
      await page.keyboard.press('Escape');
    },
    async '25-informatique-infogerance'() {
      const it = await useCompany(IT);
      await open(`/odoo/account.move/${await moveId(it, 'INF-2026-09')}`);
      await shot('25-informatique-infogerance');
      await useCompany(BAR);
    },
    async '26-informatique-resultat'() {
      await useCompany(IT);
      await mis('Compte de résultat');
      await shot('26-informatique-resultat');
      await useCompany(BAR);
    },
    async '27-informatique-credit-acompte'() {
      const it = await useCompany(IT);
      const decl = await declarationId(it, '2025-02-01');
      await open(`/odoo/action-aite_syscohada_community.action_aite_cm_vat_declaration/${decl.id}`);
      await tab('Retenues, acomptes, IRCM, salaires');
      await onlyRows('L45', 'L55');
      await page.locator('div[name="itvair_line_ids"]').scrollIntoViewIfNeeded();
      await shot('27-informatique-credit-acompte');
      await useCompany(BAR);
    },
  };

  for (const [name, run] of Object.entries(SHOTS)) {
    if (ONLY.length && !ONLY.includes(name)) continue;
    try {
      await run();
    } catch (error) {
      console.log('ÉCHEC', name, error.message.split('\n')[0]);
    }
  }
  await browser.close();
}

main();
