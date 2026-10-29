<?php
/* Kontaktformular „Kostenlose Probestunde“ – verschickt die Anfrage per E-Mail an Pascal. */
declare(strict_types=1);

const EMPFAENGER = 'info@der-sports-freund.de';
date_default_timezone_set('Europe/Berlin');

$json = stripos($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json') !== false;

function antwort(bool $ok, string $text, int $status = 200): void {
  global $json;
  http_response_code($status);
  if ($json) {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['ok' => $ok, 'message' => $text], JSON_UNESCAPED_UNICODE);
  } else {
    // Fallback ohne JavaScript: kleine Bestätigungsseite
    header('Content-Type: text/html; charset=utf-8');
    $t = htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
    echo '<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
      . '<title>Der Sportsfreund</title><body style="font-family:system-ui,sans-serif;background:#f5f3ee;color:#0f1b2d;display:grid;place-items:center;min-height:100vh;margin:0;padding:16px">'
      . '<div style="max-width:480px;background:#fff;border:2px solid #0f1b2d;box-shadow:10px 10px 0 #2456e8;padding:28px">'
      . '<p style="font-size:1.15rem;margin:0 0 1.2rem">' . $t . '</p><a href="index.html#kontakt" style="color:#2456e8;font-weight:700">Zurück zur Seite</a></div></body></html>';
  }
  exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
  antwort(false, 'Bitte nutze das Formular auf der Seite.', 405);
}

// Spam-Falle: dieses Feld ist für Menschen unsichtbar
if (trim((string)($_POST['website'] ?? '')) !== '') {
  antwort(true, 'Danke! Ich melde mich innerhalb von 48 Stunden bei dir.');
}

function feld(string $name, int $max = 200): string {
  $v = trim(strip_tags((string)($_POST[$name] ?? '')));
  $v = preg_replace('/[\r\n]+/', ' ', $v); // keine Zeilenumbrüche in einzeiligen Feldern
  return mb_substr($v, 0, $max);
}

$vorname  = feld('vorname', 80);
$nachname = feld('nachname', 80);
$email    = feld('email', 160);
$telefon  = feld('telefon', 40);
$strasse  = feld('strasse', 120);
$plz      = feld('plz', 10);
$ort      = feld('ort', 80);
$interesse = feld('interesse', 60);
$quelle   = feld('quelle', 60);
$quelle_text = feld('quelle_text', 120);
$ueber    = mb_substr(trim(strip_tags((string)($_POST['ueber'] ?? ''))), 0, 4000);
$ds       = isset($_POST['datenschutz']);

if ($vorname === '' || $nachname === '' || $strasse === '' || $plz === '' || $ort === '') {
  antwort(false, 'Bitte fülle alle Pflichtfelder aus.', 422);
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
  antwort(false, 'Bitte gib eine gültige E-Mail-Adresse an.', 422);
}
if (!$ds) {
  antwort(false, 'Bitte stimme der Verarbeitung deiner Daten zu.', 422);
}

$wie = $quelle . ($quelle_text !== '' ? ' – ' . $quelle_text : '');
$text = "Neue Anfrage für eine kostenlose Probestunde\n"
  . "============================================\n\n"
  . "Name:      $vorname $nachname\n"
  . "E-Mail:    $email\n"
  . "Telefon:   " . ($telefon !== '' ? $telefon : '–') . "\n"
  . "Adresse:   $strasse, $plz $ort\n\n"
  . "Interesse: " . ($interesse !== '' ? $interesse : '–') . "\n"
  . "Aufmerksam geworden durch: " . ($wie !== '' ? $wie : '–') . "\n\n"
  . "Über mich:\n" . ($ueber !== '' ? $ueber : '–') . "\n\n"
  . "--\nGesendet über das Kontaktformular auf der Website am " . date('d.m.Y \u\m H:i') . " Uhr.\n"
  . "Einfach auf diese E-Mail antworten, um $vorname zu schreiben.\n";

$betreff = mb_encode_mimeheader("Probestunde: $vorname $nachname", 'UTF-8', 'Q');
$kopf = implode("\r\n", [
  'From: ' . mb_encode_mimeheader('Der Sportsfreund Website', 'UTF-8', 'Q') . ' <' . EMPFAENGER . '>',
  'Reply-To: ' . mb_encode_mimeheader("$vorname $nachname", 'UTF-8', 'Q') . " <$email>",
  'MIME-Version: 1.0',
  'Content-Type: text/plain; charset=UTF-8',
  'Content-Transfer-Encoding: 8bit',
]);

if (!@mail(EMPFAENGER, $betreff, $text, $kopf, '-f' . EMPFAENGER)) {
  antwort(false, 'Das hat leider nicht geklappt. Schreib mir gern direkt an ' . EMPFAENGER . ' oder ruf mich an.', 500);
}

antwort(true, "Danke, $vorname! Ich melde mich innerhalb von 48 Stunden bei dir.");
