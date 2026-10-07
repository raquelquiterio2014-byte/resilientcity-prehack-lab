import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from pydantic import ValidationError
from resilientcity.graph import build_graph
from resilientcity.models import Incident
from resilientcity.evaluation import evaluate_all

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"

class ResilientCityGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ResilientCity AI — V3 Pre-Hackathon Multi-Agent Lab")
        self.geometry("1380x900")
        self.minsize(1180,760)
        self.configure(bg="#071a2b")
        self.images={}
        self.app=build_graph()
        self._style()
        self._ui()

    def _style(self):
        s=ttk.Style(self)
        try: s.theme_use("clam")
        except tk.TclError: pass
        s.configure("Card.TLabelframe",background="#ffffff",relief="solid",borderwidth=1)
        s.configure("Card.TLabelframe.Label",font=("Segoe UI",11,"bold"),foreground="#0b3558",background="#ffffff")
        s.configure("TLabel",font=("Segoe UI",10))
        s.configure("TButton",font=("Segoe UI",10,"bold"),padding=8)

    def _load(self,name):
        p=ASSET_DIR/name
        if not p.exists(): return None
        im=tk.PhotoImage(file=str(p)); self.images[name]=im; return im

    def _ui(self):
        header=tk.Frame(self,bg="#071a2b"); header.pack(fill="x",padx=18,pady=(12,8))
        hero=self._load("resilientcity_hero.png")
        if hero: tk.Label(header,image=hero,bg="#071a2b").pack(side="left")
        title=tk.Frame(header,bg="#071a2b"); title.pack(side="left",fill="both",expand=True,padx=18)
        tk.Label(title,text="ResilientCity AI — V3",bg="#071a2b",fg="white",font=("Segoe UI",25,"bold")).pack(anchor="w",pady=(14,0))
        tk.Label(title,text="Explainable Multi-Agent System for Urban Flood Incident Response",bg="#071a2b",fg="#47c7ff",font=("Segoe UI",11,"bold")).pack(anchor="w",pady=(4,8))
        tk.Label(title,text="Planner • Evidence • Risk • Decision • Critic • Safety • Reporter",bg="#071a2b",fg="#c8d9e8",font=("Segoe UI",9)).pack(anchor="w")

        main=tk.Frame(self,bg="#eaf2f7"); main.pack(fill="both",expand=True,padx=24,pady=10)
        main.grid_columnconfigure(0,weight=1); main.grid_columnconfigure(1,weight=2); main.grid_columnconfigure(2,weight=1); main.grid_rowconfigure(0,weight=1)
        left=ttk.LabelFrame(main,text="Incident Input",style="Card.TLabelframe",padding=16); left.grid(row=0,column=0,sticky="nsew",padx=(0,10))
        right=ttk.LabelFrame(main,text="Multi-Agent Analysis",style="Card.TLabelframe",padding=16); right.grid(row=0,column=1,sticky="nsew",padx=10)
        visual=ttk.LabelFrame(main,text="Agent Architecture",style="Card.TLabelframe",padding=10); visual.grid(row=0,column=2,sticky="nsew")

        self.incident_id=tk.StringVar(value="LAB-001"); self.location=tk.StringVar(value="Central Avenue"); self.rainfall=tk.StringVar(value="72.0"); self.road_status=tk.StringVar(value="unknown")
        self._field(left,"Incident ID",self.incident_id,0); self._field(left,"Location",self.location,1); self._field(left,"Rainfall (mm)",self.rainfall,2)
        ttk.Label(left,text="Road status").grid(row=6,column=0,sticky="w",pady=(10,4))
        ttk.Combobox(left,textvariable=self.road_status,values=["unknown","open","closed","flooded"],state="readonly").grid(row=7,column=0,sticky="ew")
        ttk.Label(left,text="Incident description").grid(row=8,column=0,sticky="w",pady=(12,4))
        self.description=tk.Text(left,height=7,wrap="word",font=("Segoe UI",10)); self.description.grid(row=9,column=0,sticky="nsew")
        self.description.insert("1.0","Heavy rainfall and reported street flooding near an intersection.")
        buttons=tk.Frame(left,bg="#ffffff"); buttons.grid(row=10,column=0,sticky="ew",pady=(16,0))
        ttk.Button(buttons,text="Run Multi-Agent Analysis",command=self.run_analysis).pack(fill="x")
        ttk.Button(buttons,text="Run Pilot Evaluation",command=self.run_evaluation).pack(fill="x",pady=(8,0))
        ttk.Button(buttons,text="Clear Results",command=self.clear_results).pack(fill="x",pady=(8,0))
        ops=self._load("operations_reference.png")
        if ops: tk.Label(left,image=ops,bg="#ffffff").grid(row=11,column=0,pady=(12,0))
        left.grid_columnconfigure(0,weight=1); left.grid_rowconfigure(9,weight=1)

        summary=tk.Frame(right,bg="#ffffff"); summary.pack(fill="x")
        self.priority=self._metric(summary,"Priority",0); self.confidence=self._metric(summary,"Evidence Strength",1); self.safety=self._metric(summary,"Safety / Human Gate",2)
        nb=ttk.Notebook(right); nb.pack(fill="both",expand=True,pady=(14,0))
        tabs=[tk.Frame(nb,bg="#ffffff") for _ in range(4)]
        for tab,name in zip(tabs,["Explainable Report","Agent Trace","Shared State","Pilot Evaluation"]): nb.add(tab,text=name)
        self.report=self._text(tabs[0]); self.trace=self._text(tabs[1]); self.state=self._text(tabs[2]); self.evaluation=self._text(tabs[3])

        agent=self._load("agent_reference.png")
        if agent: tk.Label(visual,image=agent,bg="#ffffff").pack(anchor="n")
        tk.Label(visual,text="Operational lab flow",bg="#ffffff",fg="#0b3558",font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(10,3))
        tk.Label(visual,text="Planner → Evidence → Risk → Decision → Critic\n↳ Revision when evidence is insufficient\n→ Safety → Reporter → Human decision",bg="#ffffff",fg="#49657a",font=("Segoe UI",9),justify="left",wraplength=250).pack(anchor="w")
        tk.Label(self,text="AI recommends. AI explains. Humans decide. | Educational pre-hackathon lab — no autonomous emergency actions.",bg="#0b3558",fg="white",font=("Segoe UI",9),pady=8).pack(fill="x",side="bottom")

    def _field(self,p,label,var,row):
        ttk.Label(p,text=label).grid(row=row*2,column=0,sticky="w",pady=(8 if row else 0,4)); ttk.Entry(p,textvariable=var).grid(row=row*2+1,column=0,sticky="ew")
    def _metric(self,p,label,col):
        c=tk.Frame(p,bg="#f5f9fc",highlightbackground="#cbd9e4",highlightthickness=1); c.grid(row=0,column=col,sticky="nsew",padx=(0 if col==0 else 6,0)); p.grid_columnconfigure(col,weight=1)
        tk.Label(c,text=label,bg="#f5f9fc",fg="#49657a",font=("Segoe UI",9)).pack(anchor="w",padx=10,pady=(8,2)); v=tk.Label(c,text="—",bg="#f5f9fc",fg="#0b3558",font=("Segoe UI",12,"bold"),wraplength=190,justify="left"); v.pack(anchor="w",padx=10,pady=(0,8)); return v
    def _text(self,p):
        t=tk.Text(p,wrap="word",font=("Consolas",10),bg="#fbfdff",relief="flat",padx=12,pady=12); s=ttk.Scrollbar(p,orient="vertical",command=t.yview); t.configure(yscrollcommand=s.set); t.pack(side="left",fill="both",expand=True); s.pack(side="right",fill="y"); return t
    def _replace(self,w,v): w.delete("1.0","end"); w.insert("1.0",v)

    def run_analysis(self):
        try:
            i=Incident(incident_id=self.incident_id.get().strip(),location=self.location.get().strip(),description=self.description.get("1.0","end").strip(),rainfall_mm=float(self.rainfall.get()),road_status=self.road_status.get())
            r=self.app.invoke({"incident":i.model_dump(),"revision_count":0,"trace":[]})
        except (ValidationError,ValueError) as e: messagebox.showerror("Invalid incident data",str(e)); return
        except Exception as e: messagebox.showerror("Execution error",f"The multi-agent workflow could not run:\n\n{e}"); return
        d=r.get("decision",{}); s=r.get("safety",{}); self.priority.config(text=d.get("priority","—")); e=r.get("evidence",{}); score=e.get("evidence_score"); label=e.get("score_label","—"); self.confidence.config(text=f"{label} — {score}/100\nRule-based, not probability" if isinstance(score,(int,float)) else "—"); self.safety.config(text=s.get("status","—"))
        self._replace(self.report,r.get("final_report","No report generated.")); self._replace(self.trace,"\n".join(f"{n+1:02d}. {x}" for n,x in enumerate(r.get("trace",[]))))
        self._replace(self.state,"\n".join(f"[{k.upper()}]\n{r[k]}\n" for k in ("incident","evidence","risk","decision","critic","safety","revision_count") if k in r))
    def run_evaluation(self):
        try:
            results, metrics = evaluate_all()
        except Exception as e:
            messagebox.showerror("Evaluation error", f"The supervised pilot evaluation could not run:\n\n{e}")
            return

        lines = [
            "SUPERVISED PILOT EVALUATION",
            "=" * 56,
            f"Scenarios evaluated       : {metrics['scenarios']}",
            f"Decision agreement        : {metrics['decision_agreement']:.0%}",
            f"Manual baseline agreement : {metrics['baseline_agreement']:.0%}",
            f"Evidence traceability     : {metrics['evidence_traceability']:.0%}",
            f"Missed escalations        : {metrics['missed_escalations']}",
            f"Unnecessary escalations   : {metrics['unnecessary_escalations']}",
            f"Average review time       : {metrics['avg_review_time_ms']:.2f} ms",
            f"Reproducibility           : {metrics['reproducibility']:.0%}",
            "",
            "SCENARIO RESULTS",
            "-" * 56,
        ]
        for result in results:
            escalation = "HUMAN" if result.predicted_escalation else "NO ESCALATION"
            lines.extend([
                f"{result.scenario_id}: expected={result.expected_priority} | "
                f"multi-agent={result.predicted_priority} | baseline={result.baseline_priority}",
                f"  escalation={escalation} | traceability={result.evidence_traceability:.0%} | "
                f"reproducible={'YES' if result.reproducible else 'NO'}",
            ])

        lines.extend([
            "",
            "Interpretation",
            "-" * 56,
            "Decision Agreement compares the multi-agent priority with the labelled expected result.",
            "Baseline Agreement compares a simple deterministic manual rule with the same expected result.",
            "Evidence Traceability checks whether key evidence fields are preserved.",
            "Missed Escalations are safety-critical cases that should have reached a human but did not.",
            "Unnecessary Escalations are cases sent to a human when the labelled scenario did not require it.",
            "Reproducibility checks whether repeated deterministic runs return the same core decision.",
            "",
            "NOTE: These are synthetic labelled scenarios for a supervised learning/evaluation lab.",
            "They are not a validated emergency-response benchmark or production pilot.",
        ])
        self._replace(self.evaluation, "\n".join(lines))

    def clear_results(self):
        for x in (self.priority,self.confidence,self.safety): x.config(text="—")
        for x in (self.report,self.trace,self.state,self.evaluation): self._replace(x,"")

if __name__=="__main__":
    ResilientCityGUI().mainloop()
