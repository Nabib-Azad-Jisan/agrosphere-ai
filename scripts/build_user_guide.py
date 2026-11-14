"""Create the illustrated, print-ready end-user tutorial (no external assets)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = []


def note(title, text, amber=False):
    return f'<aside class="note {"amber" if amber else ""}"><b>{title}</b><p>{text}</p></aside>'


def steps(items):
    return '<ol class="steps">' + ''.join(f'<li><div>{item}</div></li>' for item in items) + '</ol>'


def table(headers, rows):
    return '<table><thead><tr>' + ''.join(f'<th>{x}</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>' for row in rows) + '</tbody></table>'


def page(kicker, title, lead, body):
    PAGES.append((kicker, title, lead, body))


page('WELCOME / USER TUTORIAL', 'A clearer picture.<br>A more thoughtful way to grow.',
     'Your step-by-step guide to using ZYNTRIX AgroSphere AI.', '''
<div class="cover-hero"><img src="previews/landing.png" alt="AgroSphere landing page"/></div>
<div class="three"><div class="mini"><span>01</span><h3>Observe</h3><p>See soil readings, their source and their age.</p></div><div class="mini"><span>02</span><h3>Understand</h3><p>Review weather and an explained 24-hour outlook.</p></div><div class="mini"><span>03</span><h3>Inspect</h3><p>Check the field and record what you find.</p></div></div>
''' + note('Start here', 'New user? Read pages 2–4, then try the drying-to-irrigation demonstration on page 3.') + '''
<p class="small">This guide describes the current local software-first application. Screenshots show example simulation data; the values on your screen will change. No physical sensors are needed to try it.</p>
<div class="contents"><b>Inside this guide</b><p>2 Start &amp; stop · 3 First demonstration · 4 Dashboard · 5 RootSense · 6 AquaMind · 7 Weather · 8 Farms &amp; plots · 9 Sensors &amp; scenarios · 10 Reports &amp; notifications · 11 Language, theme &amp; mobile · 12 Troubleshooting</p></div>
''')

page('01 / OPEN THE APPLICATION', 'Start in the correct folder.',
     'For the application already set up on your Windows computer.',
     steps([
         '<b>Open Docker Desktop.</b><br>Wait until its engine is running. You do not need to open an administrator PowerShell window.',
         '<b>Open PowerShell and paste these two lines.</b><pre>cd "D:\\bracu mail\\Ai contest 2026\\agrosphere-ai"\ndocker compose up -d</pre>',
         '<b>Open your browser.</b><br>Enter <a href="http://127.0.0.1:3000">http://127.0.0.1:3000</a>. Select <b>Open workspace</b> or <b>Explore the live demo</b>.',
         '<b>Leave the services running while you use the app.</b><br>The <code>-d</code> option runs them in the background; closing PowerShell does not stop them.',
     ]) + note('Why your earlier “cd” command failed', 'PowerShell opened in <code>C:\\Windows\\System32</code>. Typing only <code>cd agrosphere-ai</code> searches inside that folder. The quoted, full path above works from any starting folder.', True) + '''
<h2>Stop and restart later</h2><p>From the same project folder, stop the application with:</p><pre>docker compose stop</pre><p>Restart it with <code>docker compose up -d</code>. Normal stopping preserves your saved data. You do not need to repeat installation or generate new passwords.</p>
''' + note('Using a different or newly installed computer?', 'The folder path above belongs to this computer. Follow the project README for first-time setup and use the actual project folder on the new computer. This tutorial is for operating the application, not installing its development tools.'))

page('02 / YOUR FIRST FIVE-MINUTE DEMO', 'Watch the soil story change.',
     'Try a complete demonstration without connecting hardware.', '''
<img class="screen controls" src="previews/devices.png" alt="Sensor center and simulation controls"/>
''' + steps([
         '<b>Choose a plot.</b><br>Use the plot selector in the top bar. For your first try, choose <b>North Tomato Plot</b> in the seeded Demo Tomato Farm.',
         '<b>Open Sensor center.</b><br>In the Simulation control panel, choose <b>Gradually drying soil</b>, set speed to <b>15×</b>, and click <b>Start simulation</b>.',
         '<b>Open Overview or RootSense.</b><br>Wait about 15 seconds for the next dashboard refresh, or click <b>Refresh</b>. Check that the source says <b>Simulation</b> and the observation time is recent.',
         '<b>Try an irrigation response.</b><br>Return to Sensor center, select <b>Irrigation event</b>, and click <b>Start simulation</b> again to apply the new scenario. Return to Overview and refresh to see the moisture rise.',
         '<b>Read the explanation, then pause.</b><br>Open AquaMind to review the recalculated outlook. Return to Sensor center and click <b>Pause</b> when finished.',
     ]) + note('What this demonstration means', 'It tests the real application flow with synthetic observations. The irrigation scenario does not start a pump or create a real farmer irrigation record. Simulated changes are accelerated and do not prove how quickly real soil will change.', True))

page('03 / MAIN DASHBOARD', 'Read the whole picture first.',
     'Overview brings observations, weather and guidance together.', '''
<img class="screen overview" src="previews/dashboard.png" alt="Overview dashboard with labeled simulation observations"/>
<div class="two"><div><h3>1. Plot, source and time</h3><p>Check the selected plot, the source badge and the updated time before interpreting any number.</p><h3>2. Observation cards</h3><p>Read soil moisture, soil temperature and humidity. A dash means the measurement is unavailable, not zero.</p></div><div><h3>3. Trend and outlook</h3><p>Use the moisture chart to see change over time. The AquaMind card summarizes what to consider next.</p><h3>4. Context and updates</h3><p>Weather, crop/soil details and notifications add context. Use their links to open the detailed pages.</p></div></div>
''' + note('No observations yet?', 'Open Sensor center and start a simulation. Refresh only retrieves the latest information; it does not generate a reading by itself.'))

page('04 / ROOTSENSE', 'Inspect the observations.',
     'Use RootSense for history, measurement quality and field feedback.',
     steps([
         '<b>Open RootSense and confirm the selected plot.</b><br>The latest moisture value and reading age belong to the plot shown in the top bar.',
         '<b>Choose a chart range.</b><br>Select <b>24 hours</b>, <b>7 days</b>, <b>30 days</b>, or <b>Custom range</b>. For Custom range, enter the From and To dates/times.',
         '<b>Check Observation quality.</b><br>Review the status, reading age, quality flags and threshold notes. Chart labels identify measurement sources.',
         '<b>Record an inspection.</b><br>In <b>What did you observe?</b>, select adequate, dry, wet or sensor issue; enter notes and click <b>Save field observation</b>.',
     ]) + table(['Status or signal', 'What it means for you'], [
         ['Adequate / low / excessive', 'The reading is compared with the plot’s configured limits. Simulation limits are illustrative.'],
         ['Monitoring', 'Observations can be displayed, but reviewed limits may not be available. Do not infer a validated risk category.'],
         ['Stale / unavailable', 'A recent usable observation is missing. Check the station or simulation before relying on the outlook.'],
         ['Uncalibrated / review required', 'The moisture value or its calibration needs attention. Ask the person managing the sensor.'],
     ]) + note('Understand the unit', 'Moisture charts display VWC as a percentage, derived from a value in m³/m³. Raw sensor ADC counts are a different measurement and are not automatically a moisture percentage. A displayed percentage is not a universal irrigation target.', True))

page('05 / AQUAMIND', 'Read the outlook and its reasons.',
     'AquaMind estimates conditions about 24 hours ahead; it does not measure the future.', '''
<div class="flow"><div>Latest valid<br>soil observation</div><span>+</span><div>Available<br>weather context</div><span>→</span><div>Explained<br>24-hour estimate</div></div>
''' + steps([
         '<b>Open AquaMind.</b><br>Check the source and validation label, then compare Current VWC, Persistence +24h and Water balance +24h.',
         '<b>Read the recommendation.</b><br>The guidance is intended to support inspection and judgement. It is not an instruction to apply a fixed amount of water.',
         '<b>Read “Why this outlook?”</b><br>Review the listed evidence, such as declining moisture, forecast rain or weather being unavailable.',
         '<b>Check limitations.</b><br>Look at the active method, model version and validation status. The baseline comparison shows estimates, not accuracy scores.',
     ]) + table(['Method', 'Plain-language meaning'], [
         ['Persistence baseline', 'Assumes moisture stays at the latest valid observed value. It can work without usable weather.'],
         ['Water-balance baseline', 'Uses a simplified estimate of rain and crop water demand with the plot’s soil/root-depth settings.'],
         ['Validated ML', 'Not currently established. A credible measured dataset and a proper evaluation are needed before making this claim.'],
     ]) + note('“Low risk” is not “low moisture”', 'Low moisture describes the current soil condition. Low risk describes an estimated future risk category. Unknown risk means the available evidence is insufficient; it does not mean the field is safe.', True) + '''
<p class="bengali"><b>Example Bengali guidance:</b><br>সেচের সিদ্ধান্ত নেওয়ার আগে শিকড়ের এলাকার মাটি পরীক্ষা করুন এবং সেন্সরের পাঠ যাচাই করুন।</p>
''')

page('06 / WEATHER CENTER', 'Add the weather context.',
     'Weather forecasts are linked to the farm of your selected plot.',
     steps([
         '<b>Open Weather center.</b><br>Confirm the location name. If it is wrong, check which plot is selected and edit the associated farm’s coordinates in Farms & plots.',
         '<b>Review the current summary.</b><br>Read temperature, wind, humidity and precipitation alongside the provider and last-update information.',
         '<b>Scroll through the next 24 hours.</b><br>Hourly cards show forecast temperature, rain, rain probability where available, and ET0.',
         '<b>Review the week ahead.</b><br>Daily cards summarize high/low temperature, rainfall and reference evapotranspiration.',
     ]) + table(['Label', 'How to interpret it'], [
         ['Rain forecast / probability', 'Expected rainfall and its forecast probability; these are not observations from a soil sensor.'],
         ['ET0', 'A reference signal of atmospheric water demand used as one input to the simplified estimate. It is not an amount you should automatically irrigate.'],
         ['Updated / cached / outdated', 'Weather may be served from a saved forecast. Check its age rather than assuming every refresh downloads a new forecast.'],
         ['Weather unavailable', 'The app may use a sufficiently recent saved forecast, or continue with persistence-only estimates. It does not invent replacement weather.'],
     ]) + note('Rainfall simulation and weather are separate', 'Choosing “Rainfall event” in Sensor center simulates a soil-moisture response. It does not change the actual Open-Meteo weather forecast.', True))

page('07 / FARMS & PLOTS', 'Keep the field context correct.',
     'Farm records determine location. Plot records describe the crop and soil.',
     steps([
         '<b>Create or edit a farm.</b><br>Open <b>Farms & plots</b>. Enter a farm name, location label, latitude and longitude. Click <b>Save farm</b>. Use <b>Edit farm</b> to update an existing record.',
         '<b>Create or edit a plot.</b><br>Choose its farm, enter its name, crop, growth stage, soil type and planting date. Review the rooting-depth, Kc, VWC-limit and field-capacity fields; click <b>Save plot</b>.',
         '<b>Select the plot in the top bar.</b><br>This selection determines which observations, weather, advisories and records you see elsewhere.',
         '<b>Record irrigation that actually happened.</b><br>In <b>Irrigation records · selected plot</b>, enter the time, applied amount in mm, and notes. Click <b>Record irrigation</b>. Review the table underneath.',
     ]) + note('When you are only trying the demo', 'Use the supplied Demo Tomato Farm and North Tomato Plot. You can leave the illustrative plot settings unchanged while exploring the software.') + note('When preparing a real field', 'Ask an appropriately qualified person to review soil/crop limits, field capacity, rooting depth, Kc and calibration evidence. Do not mark thresholds as reviewed merely to remove a warning. Demo values are not universal recommendations.', True) + '''
<h2>Three records that should not be confused</h2><div class="three"><div class="mini"><h3>Simulation event</h3><p>An artificial change used to test the app.</p></div><div class="mini"><h3>Irrigation record</h3><p>Your report of water actually applied.</p></div><div class="mini"><h3>Field observation</h3><p>Your inspection note about soil or a sensor issue.</p></div></div>
''')

page('08 / SENSOR CENTER', 'Choose the situation to test.',
     'The simulation panel works before physical sensors are installed.',
     table(['Scenario', 'Expected software behaviour'], [
         ['Gradually drying soil', 'Successive synthetic moisture readings decline.'],
         ['Normal variation', 'Moisture varies gently around a demo level.'],
         ['Rainfall event', 'Synthetic moisture increases; the weather forecast is unchanged.'],
         ['Irrigation event', 'Synthetic moisture increases; no pump is activated.'],
         ['Persistently wet soil', 'High illustrative moisture tests excessive-moisture handling.'],
         ['Sensor disconnection', 'No new readings arrive. Existing observations remain visible and eventually become stale.'],
         ['Stale sensor readings', 'Old timestamps test stale-data messages.'],
         ['Invalid readings (rejected)', 'Out-of-range values are rejected. An ingestion-error message is expected for this test.'],
     ]) + '''
<h2>Use the controls</h2><p><b>Start simulation</b> applies your selected scenario and speed. <b>Pause</b> stops generation. <b>15×</b> produces events faster, but does not move timestamps into the future. Dashboard refresh is a separate action.</p>
''' + note('Reset synthetic data', 'Reset pauses the simulation and clears its synthetic observations for the selected plot. It preserves actual/historical observations and farmer-entered irrigation records. The synthetic chart can become empty until you start again.', True) + '''
<h2>Adding real equipment later</h2><p>Device cards show identity, source, connection state and observation age. <b>Register a future device</b> creates a station and shows its private token once. Give that token only to the person provisioning the device. Calibration profiles need physical soil measurements; saving a profile does not validate a sensor.</p><p class="small">Hardware/historical/hybrid source-mode changes are installer settings. Hardware mode must not replace missing sensor data with a hidden simulation.</p>
''')

page('09 / ANALYTICS & NOTIFICATIONS', 'Keep a record you can review.',
     'Use observations and feedback to explain what happened.', '''
<div class="two"><div class="mini"><span>ANALYTICS & REPORTS</span><h2>Review and export</h2><p>Open Analytics & reports for moisture trends, source counts, available evaluation results and recorded irrigation.</p><p>Select <b>Export CSV</b> to download observation records for the selected plot. The export retains source and unit information.</p><p>Model comparison metrics appear only after a measured-data evaluation is available. An empty report is not zero error or perfect accuracy.</p></div><div class="mini"><span>NOTIFICATIONS</span><h2>Read the updates</h2><p>Open Notifications to review soil, missing-data and available weather warnings. Confirm that the selected plot is correct.</p><p>Use <b>Read</b> to acknowledge an unread notification. Marking it read does not repair a sensor or change soil conditions.</p><p>Warnings can reflect the time they were created. Recheck current status before acting.</p></div></div>
<h2>After inspecting the field</h2>
''' + steps([
         '<b>Record what you saw in RootSense.</b><br>Use the feedback form for dry/wet/adequate soil or a sensor issue.',
         '<b>Record actual irrigation separately.</b><br>Use Farms & plots for the selected plot’s irrigation history.',
         '<b>Return to Overview.</b><br>Refresh and check the latest reading time, source and advice instead of relying on an old notification.',
     ]) + note('No invented results', 'Synthetic data can demonstrate charts and warnings. It cannot establish measured prediction accuracy, water savings or yield improvements. The current application does not claim those field results.', True))

page('10 / PREFERENCES & MOBILE', 'Use a workspace that suits you.',
     'Language, appearance and plot preferences are saved in your browser.', '''
<div class="phone-layout"><div class="phone-frame"><img src="previews/mobile.png" alt="Mobile dashboard showing the compact navigation and observation cards"/></div><div>
<h2>English / Bengali</h2><p>Use the language icon in the top bar, or open <b>Settings → Language</b>. Navigation, page headings and key advisories switch between English and Bengali. Some technical and administrative form text remains in English.</p>
<h2>Light / dark appearance</h2><p>Use the moon/sun icon in the top bar, or <b>Settings → Appearance</b>. The choice is remembered on this browser.</p>
<h2>Notification summaries</h2><p>In Settings, toggle <b>Show notification summaries</b> to show or hide the dashboard summary. This does not switch off background monitoring or erase saved notifications.</p>
<h2>Smaller screens</h2><p>Use the menu icon at the top left to open navigation. Select a page, then use the plot selector to confirm which plot you are viewing.</p>
</div></div>
''' + note('Using a phone with this local installation', '<code>127.0.0.1</code> always refers to the device on which you type it. A phone cannot reach the PC’s local app using that address. The responsive layout supports small screens, but access from another device requires a separately configured secure deployment.'))

page('11 / TROUBLESHOOTING & QUICK REFERENCE', 'When something does not look right.',
     'Check location, services, source and freshness before changing settings.',
     table(['Problem', 'What to try'], [
         ['PowerShell cannot find agrosphere-ai', 'Use the full quoted folder path from page 2, not a relative folder name from System32.'],
         ['Docker reports engine/daemon unavailable', 'Open Docker Desktop, wait for the engine, then run docker compose up -d again from the project folder.'],
         ['Browser cannot open the app', 'Use http://127.0.0.1:3000 on this PC. Check that Docker services are running.'],
         ['No readings or no new chart points', 'Choose the right plot, open Sensor center, start a valid scenario and refresh. Paused/disconnected/invalid scenarios may not add usable points.'],
         ['An old reading remains after “stale” starts', 'The newest existing reading can remain current until an older injected timestamp is no longer competing with it. For an isolated demo, reset synthetic data first, then start the stale scenario.'],
         ['Source is Hardware but nothing appears', 'Real readings are required in hardware mode. Ask the installer to check registration, credentials, connection and calibration.'],
         ['Weather missing / risk unknown', 'Review freshness and calibration messages. The app can fall back to persistence or withhold a risk judgement; inspect the field.'],
         ['No ML accuracy numbers', 'Expected until credible measured data has been evaluated. Simulation is not validation evidence.'],
     ]) + '''
<h2>Commands to keep</h2><pre>cd "D:\\bracu mail\\Ai contest 2026\\agrosphere-ai"\ndocker compose up -d       # Start / restart\ndocker compose ps          # View service status\ndocker compose stop        # Stop; keep saved data</pre>
<p class="small">If the problem continues, save the exact error text and ask the person maintaining the application. Never share a device token, administrator token or the contents of your .env file.</p>
''' + note('Your everyday routine', 'Choose plot → check source and reading age → review soil trend and weather → read the AquaMind reasons → inspect the field → record your observation or actual irrigation.'))

CSS = '''
@page { size:A4; margin:0; }
* { box-sizing:border-box; }
html,body { margin:0; padding:0; background:#e7ece6; }
body { font-family:"Segoe UI","Nirmala UI",Arial,sans-serif; color:#172a22; font-size:10.5pt; line-height:1.52; }
.page { width:210mm; height:297mm; padding:15mm 17mm 18mm; position:relative; background:#fff; break-after:page; margin:0 auto; }
.page:last-child { break-after:auto; }
.header { display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #dfe9df; padding-bottom:4mm; margin-bottom:7mm; }
.brand { font-size:15pt; font-weight:700; letter-spacing:-.6px; color:#103d2e; }.brand span { color:#168b5d; font-weight:400; }
.header small { font-size:7pt; letter-spacing:1.2px; color:#64776b; }
.kicker { font-size:8pt; letter-spacing:1.5px; color:#168b5d; font-weight:650; margin:0 0 3mm; }
h1 { font-size:28pt; line-height:1.1; letter-spacing:-1px; font-weight:650; color:#103d2e; margin:0 0 4mm; }
.lead { font-size:12pt; color:#64776b; margin:0 0 6mm; line-height:1.5; }
h2 { font-size:14pt; color:#103d2e; line-height:1.25; margin:5mm 0 3mm; }
h3 { font-size:11pt; color:#103d2e; margin:3mm 0 2mm; line-height:1.3; }
p { margin:0 0 3mm; } b { font-weight:650; }
.footer { position:absolute; bottom:9mm; left:17mm; right:17mm; display:flex; justify-content:space-between; border-top:1px solid #dfe9df; padding-top:3mm; color:#64776b; font-size:7.5pt; }
.steps { padding:0; margin:0 0 4mm; list-style:none; counter-reset:step; }
.steps li { counter-increment:step; display:flex; gap:3mm; align-items:flex-start; margin:0 0 4mm; }
.steps li:before { content:counter(step); background:#eaf5ee; color:#168b5d; border-radius:50%; width:7mm; height:7mm; display:grid; place-items:center; flex-shrink:0; font-weight:700; font-size:9pt; }
.steps li>div { flex:1; padding-top:.4mm; }
.note { padding:3.5mm 4mm; margin:4mm 0; background:#edf7ef; border-left:3px solid #168b5d; border-radius:0 6px 6px 0; font-size:9.7pt; }
.note p { margin:1.3mm 0 0; }.note.amber { background:#fff6e6; border-color:#c79b4f; }
pre { font-family:Consolas,"Courier New",monospace; font-size:9.2pt; line-height:1.75; white-space:pre-wrap; background:#103d2e; color:#f3faee; border-radius:6px; padding:3.5mm 4mm; margin:3mm 0; }
code { font-family:Consolas,"Courier New",monospace; font-size:.92em; overflow-wrap:anywhere; }
a { color:#168b5d; font-weight:650; }
table { width:100%; border-collapse:collapse; font-size:9.5pt; margin:4mm 0; }
th { background:#103d2e; color:#fff; text-align:left; padding:2.7mm 3mm; font-weight:550; }
td { border-bottom:1px solid #dfe9df; padding:2.8mm 3mm; vertical-align:top; }
td:first-child { width:32%; color:#103d2e; font-weight:600; } tr:nth-child(even) td { background:#f6f9f5; }
.two,.three { display:grid; grid-template-columns:1fr 1fr; gap:5mm; }.three { grid-template-columns:repeat(3,1fr); gap:3mm; }
.mini { border:1px solid #e0e9df; background:#f6faf5; border-radius:8px; padding:4mm; }
.mini span { font-size:8pt; font-weight:650; letter-spacing:1px; color:#168b5d; }.mini p { font-size:9.5pt; }
.mini h2,.mini h3 { margin-top:2mm; }.small { font-size:9pt; color:#64776b; }
.screen { display:block; max-width:100%; width:100%; object-fit:contain; object-position:top; border:1px solid #e1e9de; border-radius:7px; margin:0 0 5mm; }
.overview { height:120mm; }.controls { height:70mm; object-fit:cover; }
#page-3 .steps li { margin-bottom:2.7mm; }
#page-9 td { padding-top:2.5mm; padding-bottom:2.5mm; }
#page-12 table { font-size:9pt; line-height:1.4; }
#page-12 td { padding-top:2.3mm; padding-bottom:2.3mm; }
#page-12 pre { line-height:1.6; }
.cover-hero { width:100%; height:71mm; overflow:hidden; border:1px solid #e0e9df; border-radius:9px; margin-bottom:5mm; }
.cover-hero img { display:block; width:100%; height:100%; object-fit:cover; object-position:top; }
.cover h1 { font-size:31pt; }.cover .lead { font-size:13pt; }
.contents { border-top:1px solid #e0e9df; padding-top:3mm; font-size:9pt; color:#64776b; }.contents p { margin-top:2mm; }
.flow { display:flex; align-items:center; gap:2mm; padding:4mm; border-radius:9px; background:#edf7ef; margin-bottom:5mm; }
.flow div { flex:1; text-align:center; font-size:10pt; font-weight:600; color:#103d2e; }.flow>span { color:#168b5d; font-size:16pt; }
.bengali { font-family:"Nirmala UI","Segoe UI",sans-serif; padding-top:3mm; font-size:11pt; color:#103d2e; }
.phone-layout { display:grid; grid-template-columns:62mm 1fr; gap:7mm; align-items:start; }
.phone-frame { height:151mm; overflow:hidden; border:1px solid #dae4d7; border-radius:13px; background:#f5f9f4; }
.phone-frame img { width:100%; display:block; }
.phone-layout h2:first-child { margin-top:0; }
@media screen { .page { margin-bottom:12px; box-shadow:0 3px 16px #0001; } }
'''

parts = []
for i, (kicker, title, lead, body) in enumerate(PAGES, 1):
    parts.append(f'''<section class="page {"cover" if i == 1 else ""}" id="page-{i}">
    <div class="content"><header class="header"><div class="brand">AgroSphere <span>AI</span></div><small>ZYNTRIX / USER GUIDE</small></header>
    <p class="kicker">{kicker}</p><h1>{title}</h1><p class="lead">{lead}</p>{body}</div>
    <footer class="footer"><span>Intelligence Beyond Boundaries · Software-first user tutorial</span><span>{i:02d} / {len(PAGES):02d}</span></footer></section>''')
output = ROOT / 'docs/user-tutorial.html'
output.write_text('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>ZYNTRIX AgroSphere AI — User Tutorial</title><style>' + CSS + '</style></head><body>' + ''.join(parts) + '</body></html>', encoding='utf-8')
print(f'Created {len(PAGES)} tutorial pages: {output}')
