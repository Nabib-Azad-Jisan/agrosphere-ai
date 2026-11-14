from pathlib import Path

p = Path("frontend/components/workspace-page.tsx")
s = p.read_text(encoding="utf-8")
s = s.replace("ArrowUpRight, ArrowDownRight,", "ArrowUpRight,").replace("Leaf, CalendarDays,", "Leaf,")
s = s.replace("const [days,setDays]=useState('1');", "const [days,setDays]=useState('1'); const [now]=useState(()=>new Date().getTime());")
s = s.replace("Date.now()-Number(days)", "now-Number(days)")
s = s.replace("const {t}=useApp(); if(error)", "const {t}=useApp(); const [now]=useState(()=>new Date().getTime()); if(error)")
s = s.replace("const data=weather.data; const now=Date.now();", "const data=weather.data;")
p.write_text(s, encoding="utf-8")
