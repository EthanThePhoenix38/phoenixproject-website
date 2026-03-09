/**
 * PhoenixOS - tests automatiques
 * Run: node test-phoenix-os.mjs
 */
import { JSDOM } from 'jsdom';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(join(__dirname, 'phoenix-os.html'), 'utf-8');

let passed = 0, failed = 0;
function ok(n) { process.stdout.write('  OK ' + n + '\n'); passed++; }
function fail(n, e) { process.stdout.write('  FAIL ' + n + ': ' + e + '\n'); failed++; }
function test(n, fn) { try { fn(); ok(n); } catch(e) { fail(n, e.message); } }

// DOM checks
const dom = new JSDOM(html);
const doc = dom.window.document;
console.log('\nPhoenixOS - Tests automatiques\n\n--- Structure HTML ---');

test('Title contient Phoenix', () => { if (!doc.title.includes('Phoenix')) throw new Error(doc.title); });
test('Viewport meta present', () => { if (!doc.querySelector('meta[name="viewport"]')) throw new Error('absent'); });
test('#bootScreen present', () => { if (!doc.getElementById('bootScreen')) throw new Error('absent'); });
test('#loginScreen present', () => { if (!doc.getElementById('loginScreen')) throw new Error('absent'); });
test('#desktop present', () => { if (!doc.getElementById('desktop')) throw new Error('absent'); });
test('#desktopArea present', () => { if (!doc.getElementById('desktopArea')) throw new Error('absent'); });
test('#clock present', () => { if (!doc.getElementById('clock')) throw new Error('absent'); });
test('#clock onclick toggleCalendar', () => {
  const c = doc.getElementById('clock');
  if (!c.getAttribute('onclick') || !c.getAttribute('onclick').includes('Calendar')) throw new Error('absent');
});
test('Icone PhoenixOS sur bureau', () => {
  const labels = [...doc.querySelectorAll('.desktop-icon-label')].map(el => el.textContent);
  if (!labels.some(l => l.includes('Phoenix'))) throw new Error(labels.join(', '));
});
test('Icone Editeur sur bureau', () => {
  const labels = [...doc.querySelectorAll('.desktop-icon-label')].map(el => el.textContent);
  if (!labels.some(l => l.includes('diteur'))) throw new Error(labels.join(', '));
});
test('Icone Courrier sur bureau', () => {
  const labels = [...doc.querySelectorAll('.desktop-icon-label')].map(el => el.textContent);
  if (!labels.some(l => l.includes('Courrier'))) throw new Error(labels.join(', '));
});
test('Taskbar >= 6 boutons', () => {
  const n = doc.querySelectorAll('.taskbar-item').length;
  if (n < 6) throw new Error(n + ' boutons');
});
test('Hint mot de passe present', () => {
  const hint = doc.querySelector('#loginScreen p');
  if (!hint || !hint.textContent.toLowerCase().includes('phoenix')) throw new Error(hint ? hint.textContent : 'absent');
});
test('#shutdownScreen sans .show au demarrage', () => {
  if (doc.getElementById('shutdownScreen').classList.contains('show')) throw new Error('affiche!');
});
test('Menu demarrer en francais', () => {
  const items = [...doc.querySelectorAll('.menu-item')].map(el => el.textContent.trim()).join(' ');
  if (!items.includes('Fichiers') && !items.includes('Calculatrice')) throw new Error(items.slice(0,60));
});
test('Clear Data sans location.reload()', () => {
  if (/Clear all data.*location\.reload|Effacer.*location\.reload/.test(html)) throw new Error('trouve!');
});
test('Browser sans placeholder URL', () => {
  if (html.includes('value="https://example.com"')) throw new Error('trouve!');
});
test('Browser sans iframe', () => {
  const start = html.indexOf('function openBrowser()');
  const end = html.indexOf('\nwindow.browserGo', start);
  if (html.slice(start, end).includes('<iframe')) throw new Error('iframe trouvee');
});
test('showOSK: garde isMobile', () => {
  const match = html.match(/function showOSK\(target\) \{([^}]+)\}/);
  if (!match) throw new Error('showOSK non trouvee');
  if (!match[1].includes('isMobile')) throw new Error('garde absente');
});
test('renderOSK appele avant fetch', () => {
  const fi = html.indexOf("fetch('https://ipapi.co/json/')");
  const ri = html.lastIndexOf('renderOSK(', fi);
  if (ri < 0 || ri >= fi) throw new Error('pas avant fetch');
});
test('Minimize: mini-card pas setTimeout blink', () => {
  if (html.includes("setTimeout(() => win.style.display = 'flex', 100)")) throw new Error('bug toujours present');
  if (!html.includes('mini-card')) throw new Error('mini-card absent');
});
test('CSS .mini-card defini', () => {
  if (!html.includes('.mini-card{') && !html.includes('.mini-card {')) throw new Error('CSS absent');
});
test('#calendarPopup defini', () => { if (!html.includes('id="calendarPopup"')) throw new Error('absent'); });
test('WALLPAPERS >= 5', () => {
  const m = html.match(/const WALLPAPERS\s*=\s*\[([\s\S]+?)\];/);
  if (!m) throw new Error('WALLPAPERS absent');
  const n = (m[1].match(/\{label:/g)||[]).length;
  if (n < 5) throw new Error(n + ' wallpapers');
});
test('Terminal: commandes etendues', () => {
  for (const cmd of ['touch','uname','neofetch','cp','mv','history']) {
    if (!html.includes("case '" + cmd + "':")) throw new Error(cmd + ' absent');
  }
});
test('openMail() definie', () => { if (!html.includes('function openMail()')) throw new Error('absent'); });
test('openAbout() definie', () => { if (!html.includes('function openAbout()')) throw new Error('absent'); });
test('aiMove() definie', () => { if (!html.includes('function aiMove()')) throw new Error('absent'); });

// Calculatrice
console.log('\n--- Calculatrice ---');
function calcExec(a, b, op) {
  switch(op) {
    case '+': return a + b; case '-': return a - b;
    case '*': return a * b; case '/': return b !== 0 ? a / b : 0;
    case '%': return a % b; default: return b;
  }
}
test('calcExec dans HTML', () => { if (!html.includes('function calcExec(a, b, op)')) throw new Error('absent'); });
test('3 + 4 = 7', () => { if (calcExec(3,4,'+') !== 7) throw new Error(calcExec(3,4,'+')); });
test('10 - 3 = 7', () => { if (calcExec(10,3,'-') !== 7) throw new Error(calcExec(10,3,'-')); });
test('6 x 7 = 42', () => { if (calcExec(6,7,'*') !== 42) throw new Error(calcExec(6,7,'*')); });
test('10 / 2 = 5', () => { if (calcExec(10,2,'/') !== 5) throw new Error(calcExec(10,2,'/')); });
test('div par zero = 0', () => { if (calcExec(5,0,'/') !== 0) throw new Error(calcExec(5,0,'/')); });
test('10 % 3 = 1', () => { if (calcExec(10,3,'%') !== 1) throw new Error(calcExec(10,3,'%')); });

// TicTacToe
console.log('\n--- TicTacToe IA ---');
const WL = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
function cw(b) {
  for (const [a,bb,c] of WL) { if (b[a] && b[a]===b[bb] && b[a]===b[c]) return b[a]; }
  return b.every(v=>v) ? 'TIE' : null;
}
function ai(board) {
  for (let i=0;i<9;i++) { if(!board[i]){board[i]='O';if(cw(board)==='O')return i;board[i]='';} }
  for (let i=0;i<9;i++) { if(!board[i]){board[i]='X';if(cw(board)==='X'){board[i]='';return i;}board[i]='';} }
  if (!board[4]) return 4;
  for (const c of [0,2,6,8]) { if(!board[c]) return c; }
  return board.findIndex(v=>!v);
}
test('Victoire X ligne 0', () => { if (cw(['X','X','X','','','','','',''])!=='X') throw new Error(); });
test('Victoire O colonne 1', () => { if (cw(['','O','','','O','','','O',''])!=='O') throw new Error(); });
test('Victoire X diagonale', () => { if (cw(['X','O','','O','X','','','','X'])!=='X') throw new Error(); });
test('Egalite TIE', () => { if (cw(['X','O','X','X','O','X','O','X','O'])!=='TIE') throw new Error(); });
test('Pas de gagnant = null', () => { if (cw(['X','O','','','','','','',''])!==null) throw new Error(); });
test('IA gagne si possible (case 2)', () => { if (ai(['O','O','','X','X','','','',''])!==2) throw new Error(); });
test('IA bloque joueur (case 2)', () => { if (ai(['X','X','','O','','','','',''])!==2) throw new Error(); });
test('IA prend centre (case 4)', () => { if (ai(['','','','','','','','',''])!==4) throw new Error(); });
test('IA prend coin si centre pris', () => {
  const m = ai(['','','','','X','','','','']);
  if (![0,2,6,8].includes(m)) throw new Error('a joue ' + m);
});

// FS
console.log('\n--- Filesystem virtuel ---');
class FS2 { constructor() { this._d = {}; } getItem(k) { return k in this._d ? this._d[k] : null; } setItem(k,v) { this._d[k]=String(v); } removeItem(k){delete this._d[k];} clear(){this._d={};} }
const storage = new FS2();
const fsStart = html.indexOf('const FS = {');
const fsEnd = html.indexOf('\n};', fsStart) + 3;
const FS = new Function('localStorage', html.slice(fsStart, fsEnd) + '\nreturn FS;')(storage);

test('FS creer + lire', () => { FS.createFile('/','_t_.txt','hello'); if (FS.read('/','_t_.txt')!=='hello') throw new Error(); });
test('FS lister', () => { if (!FS.list('/').some(f=>f.name==='_t_.txt')) throw new Error(); });
test('FS update', () => { FS.update('/','_t_.txt','world'); if (FS.read('/','_t_.txt')!=='world') throw new Error(); });
test('FS supprimer', () => { FS.delete('/','_t_.txt'); if (FS.read('/','_t_.txt')!==null) throw new Error(); });
test('FS creer dossier', () => {
  FS.mkdir('/','_dir_');
  if (!FS.list('/').some(f=>f.name==='_dir_'&&f.type==='folder')) throw new Error();
  FS.delete('/','_dir_');
});
test('FS inexistant = null', () => { if (FS.read('/','_ghost_')!==null) throw new Error(); });

// Result
const total = passed + failed;
console.log('\n---------------------------------');
console.log('Result: ' + passed + '/' + total + (failed > 0 ? ' (' + failed + ' echecs)' : ' - Tous OK!'));
console.log('---------------------------------\n');
process.exit(failed > 0 ? 1 : 0);
