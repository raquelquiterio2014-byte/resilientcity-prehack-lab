import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from pydantic import ValidationError

from resilientcity.graph import build_graph
from resilientcity.models import Incident
from resilientcity.evaluation import evaluate_all


class ResilientCityGUI(tk.Tk):
    NAVY = "#071a2b"
    BLUE = "#0b3558"
    LIGHT = "#eaf2f7"
    CARD = "#ffffff"
    SOFT = "#f5f9fc"
    TEXT = "#17354d"
    MUTED = "#60798c"

    def __init__(self):
        super().__init__()
        self.title("ResilientCity AI — V6 Final Pre-Hackathon Research Prototype | PyCharm Local Demo")
        self.geometry("1200x760")
        self.minsize(900, 620)
        self.configure(bg=self.NAVY)
        self.app = build_graph()
        self.scenarios = self._load_scenarios()
        self._style()
        self._build_ui()

    def _style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Card.TLabelframe", background=self.CARD)
        style.configure("Card.TLabelframe.Label", background=self.CARD, foreground=self.BLUE,
                        font=("Segoe UI", 11, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("TLabel", font=("Segoe UI", 10))

    def _build_ui(self):
        header = tk.Frame(self, bg=self.NAVY)
        header.pack(fill="x", padx=24, pady=(14, 10))
        tk.Label(header, text="ResilientCity AI — V6 Final Pre-Hackathon Research Prototype", bg=self.NAVY, fg="white",
                 font=("Segoe UI", 25, "bold")).pack(anchor="w")
        tk.Label(header, text="Explainable Multi-Agent System for Urban Flood Incident Response",
                 bg=self.NAVY, fg="#47c7ff", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(header,
                 text="Incident → Planner → Evidence → Risk → Decision → Critic/Revision → Safety → Human Gate → Reporter",
                 bg=self.NAVY, fg="#c8d9e8", font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))

        body_host = tk.Frame(self, bg=self.LIGHT)
        body_host.pack(fill="both", expand=True, padx=24, pady=(0, 10))
        canvas = tk.Canvas(body_host, bg=self.LIGHT, highlightthickness=0)
        vscroll = ttk.Scrollbar(body_host, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        body = tk.Frame(canvas, bg=self.LIGHT)
        body_window = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(body_window, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=3)
        body.grid_rowconfigure(0, weight=1)

        left = ttk.LabelFrame(body, text="Incident", style="Card.TLabelframe", padding=16)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = ttk.LabelFrame(body, text="Multi-Agent Analysis", style="Card.TLabelframe", padding=14)
        right.grid(row=0, column=1, sticky="nsew")

        self.incident_id = tk.StringVar(value="LAB-001")
        self.location = tk.StringVar(value="Central Avenue")
        self.rainfall = tk.StringVar(value="72.0")
        self.road_status = tk.StringVar(value="unknown")
        self.scenario_choice = tk.StringVar(value="Custom Incident")
        self.reasoning_mode = tk.StringVar(value="deterministic")
        # Optional local Gemini key for PyCharm testing.
        # Leave blank in GitHub. Paste your key only in your local copy if desired.
        self.gemini_api_key = ""
        self.evaluation_mode = tk.StringVar(value="standard")
        self.dry_days=tk.StringVar(value=""); self.soil_saturation=tk.StringVar(value=""); self.impervious=tk.StringVar(value=""); self.drainage=tk.StringVar(value="unknown"); self.terrain_slope=tk.StringVar(value=""); self.land_use=tk.StringVar(value="")
        self.selected_scenario_incident = {}

        ttk.Label(left, text="Scenario").grid(row=0, column=0, sticky="w", pady=(2, 4))
        scenario_values = ["Custom Incident"] + [
            f"{item['scenario_id']} — {item['incident']['location']}" for item in self.scenarios
        ]
        self.scenario_combo = ttk.Combobox(
            left, textvariable=self.scenario_choice, values=scenario_values, state="readonly"
        )
        self.scenario_combo.grid(row=1, column=0, sticky="ew")
        self.scenario_combo.bind("<<ComboboxSelected>>", self._on_scenario_selected)

        self._field(left, "Incident ID", self.incident_id, 2)
        self._field(left, "Location", self.location, 4)
        self._field(left, "Rainfall (mm)", self.rainfall, 6)
        ttk.Label(left, text="Road status").grid(row=8, column=0, sticky="w", pady=(10, 4))
        ttk.Combobox(left, textvariable=self.road_status,
                     values=["unknown", "open", "closed", "flooded"],
                     state="readonly").grid(row=9, column=0, sticky="ew")
        ttk.Label(left, text="Incident description").grid(row=10, column=0, sticky="w", pady=(12, 4))
        self.description = tk.Text(left, height=6, wrap="word", font=("Segoe UI", 10))
        self.description.grid(row=11, column=0, sticky="nsew")
        self.description.insert("1.0", "Heavy rainfall and reported street flooding near an intersection.")

        physical=ttk.LabelFrame(left,text="Physical / Contextual Evidence",padding=8); physical.grid(row=12,column=0,sticky="ew",pady=4)
        for c in range(2): physical.grid_columnconfigure(c,weight=1)
        for label,var,row,col in [("Dry days",self.dry_days,0,0),("Soil saturation %",self.soil_saturation,0,1),("Impervious %",self.impervious,2,0),("Terrain slope %",self.terrain_slope,2,1),("Land use",self.land_use,4,0)]:
            ttk.Label(physical,text=label).grid(row=row,column=col,sticky="w"); ttk.Entry(physical,textvariable=var).grid(row=row+1,column=col,sticky="ew",padx=3)
        ttk.Label(physical,text="Drainage").grid(row=4,column=1,sticky="w"); ttk.Combobox(physical,textvariable=self.drainage,values=["unknown","clear","partially_blocked","clogged"],state="readonly").grid(row=5,column=1,sticky="ew")

        mode_box = ttk.LabelFrame(left, text="Reasoning Mode", padding=8)
        mode_box.grid(row=13, column=0, sticky="ew", pady=(12, 4))
        ttk.Radiobutton(mode_box, text="Deterministic", variable=self.reasoning_mode,
                        value="deterministic").pack(anchor="w")
        ttk.Radiobutton(mode_box, text="LLM-Assisted (Gemini 2.5 Flash)", variable=self.reasoning_mode,
                        value="llm_assisted").pack(anchor="w")
        ttk.Button(left, text="Run Multi-Agent Analysis",
                   command=self.run_analysis).grid(row=14, column=0, sticky="ew", pady=(8, 4))
        eval_box=ttk.LabelFrame(left,text="Evaluation Mode",padding=8); eval_box.grid(row=15,column=0,sticky="ew",pady=4)
        ttk.Radiobutton(eval_box,text="Standard",variable=self.evaluation_mode,value="standard").pack(anchor="w"); ttk.Radiobutton(eval_box,text="Historical Shadow Mode",variable=self.evaluation_mode,value="shadow").pack(anchor="w")
        ttk.Button(left, text="Run Evaluation",
                   command=self.run_evaluation).grid(row=16, column=0, sticky="ew", pady=4)
        ttk.Button(left, text="Clear Results",
                   command=self.clear_results).grid(row=17, column=0, sticky="ew", pady=4)

        tk.Label(left, text="AI recommends. AI explains.\nHumans decide.",
                 bg=self.CARD, fg=self.BLUE, font=("Segoe UI", 11, "bold"),
                 justify="left").grid(row=17, column=0, sticky="w", pady=(14, 4))
        tk.Label(left, text="Educational pre-hackathon lab.\nNo autonomous emergency actions.",
                 bg=self.CARD, fg=self.MUTED, font=("Segoe UI", 9),
                 justify="left").grid(row=16, column=0, sticky="w")
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(11, weight=1)

        summary = tk.Frame(right, bg=self.CARD)
        summary.pack(fill="x")
        self.priority = self._summary_card(summary, "Priority", 0)
        self.evidence_strength = self._summary_card(summary, "Evidence Strength", 1)
        self.safety = self._summary_card(summary, "Safety / Human Gate", 2)

        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill="both", expand=True, pady=(12, 0))

        report_tab = tk.Frame(self.notebook, bg=self.CARD)
        trace_tab = tk.Frame(self.notebook, bg=self.CARD)
        state_tab = tk.Frame(self.notebook, bg=self.CARD)
        evaluation_tab = tk.Frame(self.notebook, bg=self.CARD)

        self.notebook.add(report_tab, text="Explainable Report")
        self.notebook.add(trace_tab, text="Agent Trace")
        self.notebook.add(state_tab, text="Shared State")
        self.notebook.add(evaluation_tab, text="Pilot Evaluation")

        self.report_text = self._text_area(report_tab)
        self.trace_text = self._text_area(trace_tab)
        self.state_text = self._text_area(state_tab)
        self._build_evaluation_dashboard(evaluation_tab)

        footer = tk.Label(
            self,
            text="V6 Final Pre-Hackathon Research Prototype | Deterministic or Gemini-assisted Evidence/Critic | Safety remains deterministic.",
            bg=self.BLUE, fg="white", font=("Segoe UI", 9), pady=7
        )
        footer.pack(fill="x", side="bottom")

    def _load_scenarios(self):
        path = Path(__file__).resolve().parent / "evaluation" / "scenarios.json"
        try:
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showwarning(
                "Scenario list unavailable",
                f"Could not load evaluation/scenarios.json:\n\n{exc}\n\n"
                "Custom Incident remains available."
            )
            return []

    def _on_scenario_selected(self, _event=None):
        selected = self.scenario_choice.get()
        if selected == "Custom Incident":
            return

        scenario_id = selected.split(" — ", 1)[0]
        scenario = next(
            (item for item in self.scenarios if item.get("scenario_id") == scenario_id),
            None
        )
        if not scenario:
            return

        incident = scenario["incident"]
        self.selected_scenario_incident = dict(incident)
        self.incident_id.set(incident["incident_id"])
        self.location.set(incident["location"])
        self.rainfall.set("" if incident["rainfall_mm"] is None else str(incident["rainfall_mm"]))
        self.road_status.set(incident["road_status"])
        self.description.delete("1.0", "end")
        self.description.insert("1.0", incident["description"])
        self.dry_days.set("" if incident.get("antecedent_dry_days") is None else str(incident.get("antecedent_dry_days")))
        self.soil_saturation.set("" if incident.get("soil_saturation_pct") is None else str(incident.get("soil_saturation_pct")))
        self.impervious.set("" if incident.get("impervious_surface_pct") is None else str(incident.get("impervious_surface_pct")))
        self.drainage.set(incident.get("drainage_status") or "unknown")
        self.terrain_slope.set("" if incident.get("terrain_slope_pct") is None else str(incident.get("terrain_slope_pct")))
        self.land_use.set(incident.get("land_use") or "")
        self.clear_results()

    def _field(self, parent, label, variable, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=(8, 4))
        ttk.Entry(parent, textvariable=variable).grid(row=row + 1, column=0, sticky="ew")

    def _summary_card(self, parent, title, column):
        card = tk.Frame(parent, bg=self.SOFT, highlightbackground="#cbd9e4", highlightthickness=1)
        card.grid(row=0, column=column, sticky="nsew", padx=4)
        parent.grid_columnconfigure(column, weight=1)
        tk.Label(card, text=title, bg=self.SOFT, fg=self.MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=(8, 2))
        value = tk.Label(card, text="—", bg=self.SOFT, fg=self.BLUE,
                         font=("Segoe UI", 12, "bold"), wraplength=230, justify="left")
        value.pack(anchor="w", padx=10, pady=(0, 9))
        return value

    def _text_area(self, parent):
        frame = tk.Frame(parent, bg=self.CARD)
        frame.pack(fill="both", expand=True)
        text = tk.Text(frame, wrap="word", font=("Consolas", 10),
                       bg="#fbfdff", relief="flat", padx=12, pady=12)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return text

    def _build_evaluation_dashboard(self, parent):
        intro = tk.Frame(parent, bg=self.CARD)
        intro.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(intro, text="Supervised Pilot Evaluation", bg=self.CARD, fg=self.BLUE,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.eval_statement = tk.Label(
            intro,
            text="Standard Evaluation runs deterministic labelled synthetic scenarios only. Historical Shadow Mode uses paired timestamped case/human files.",
            bg=self.CARD, fg=self.MUTED, font=("Segoe UI", 10), justify="left"
        )
        self.eval_statement.pack(anchor="w", pady=(3, 8))

        cards = tk.Frame(parent, bg=self.CARD)
        cards.pack(fill="x", padx=6)
        for c in range(5):
            cards.grid_columnconfigure(c, weight=1)

        self.eval_decision = self._eval_card(cards, "Decision Agreement", 0)
        self.eval_baseline = self._eval_card(cards, "Manual Baseline", 1)
        self.eval_traceability = self._eval_card(cards, "Evidence Traceability", 2)
        self.eval_escalations = self._eval_card(cards, "Escalations", 3)
        self.eval_repro = self._eval_card(cards, "Reproducibility", 4)

        meta = tk.Frame(parent, bg=self.CARD)
        meta.pack(fill="x", padx=8, pady=(8, 5))
        self.eval_execution_time = tk.Label(
            meta, text="Average Workflow Execution Time: —",
            bg=self.CARD, fg=self.TEXT, font=("Segoe UI", 10, "bold")
        )
        self.eval_execution_time.pack(side="left")
        self.eval_scenarios = tk.Label(
            meta, text="Scenarios: —", bg=self.CARD, fg=self.TEXT, font=("Segoe UI", 10)
        )
        self.eval_scenarios.pack(side="right")

        tk.Label(parent, text="Scenario Results", bg=self.CARD, fg=self.BLUE,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=(5, 3))
        self.eval_results = self._text_area(parent)

    def _eval_card(self, parent, title, column):
        card = tk.Frame(parent, bg=self.SOFT, highlightbackground="#cbd9e4", highlightthickness=1)
        card.grid(row=0, column=column, sticky="nsew", padx=3)
        tk.Label(card, text=title, bg=self.SOFT, fg=self.MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=8, pady=(7, 2))
        value = tk.Label(card, text="—", bg=self.SOFT, fg=self.BLUE,
                         font=("Segoe UI", 11, "bold"), justify="left", wraplength=155)
        value.pack(anchor="w", padx=8, pady=(0, 8))
        return value

    def _replace(self, widget, value):
        widget.delete("1.0", "end")
        widget.insert("1.0", value)

    def run_analysis(self):
        if self.gemini_api_key.strip():
            os.environ["GEMINI_API_KEY"] = self.gemini_api_key.strip()
        try:
            base = dict(self.selected_scenario_incident) if self.scenario_choice.get() != "Custom Incident" else {}
            base.update({
                "incident_id": self.incident_id.get().strip(),
                "location": self.location.get().strip(),
                "description": self.description.get("1.0", "end").strip(),
                "rainfall_mm": float(self.rainfall.get()) if self.rainfall.get().strip() else None,
                "road_status": self.road_status.get(),
                "antecedent_dry_days": int(self.dry_days.get()) if self.dry_days.get().strip() else None,
                "soil_saturation_pct": float(self.soil_saturation.get()) if self.soil_saturation.get().strip() else None,
                "impervious_surface_pct": float(self.impervious.get()) if self.impervious.get().strip() else None,
                "drainage_status": self.drainage.get(),
                "terrain_slope_pct": float(self.terrain_slope.get()) if self.terrain_slope.get().strip() else None,
                "land_use": self.land_use.get().strip() or None,
            })
            incident = Incident.model_validate(base)
            result = self.app.invoke({
                "incident": incident.model_dump(),
                "revision_count": 0,
                "trace": [],
                "reasoning_mode": self.reasoning_mode.get(),
                "llm_status": {},
            })
        except (ValidationError, ValueError) as exc:
            messagebox.showerror("Invalid incident data", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Execution error", f"The multi-agent workflow could not run:\n\n{exc}")
            return

        decision = result.get("decision", {})
        evidence = result.get("evidence", {})
        safety = result.get("safety", {})

        self.priority.config(text=decision.get("priority", "—"))
        score = evidence.get("evidence_score")
        label = evidence.get("score_label", "—")
        self.evidence_strength.config(
            text=f"{label} — {score}/100\nRule-based, not probability"
            if isinstance(score, (int, float)) else "—"
        )
        self.safety.config(text=safety.get("status", "—"))

        self._replace(self.report_text, result.get("final_report", ""))
        self._replace(
            self.trace_text,
            "\n".join(f"{index:02d}. {event}"
                      for index, event in enumerate(result.get("trace", []), start=1))
        )
        state_lines = []
        for key in ("reasoning_mode", "incident", "evidence", "llm_evidence", "risk", "decision", "critic", "llm_critic", "llm_status", "safety", "human_gate", "revision_count"):
            if key in result:
                state_lines.append(f"[{key.upper()}]\n{result[key]}\n")
        self._replace(self.state_text, "\n".join(state_lines))

    def run_evaluation(self):
        if self.evaluation_mode.get()=="shadow":
            messagebox.showinfo("Historical Shadow Mode","Uses timestamped FieldCase evidence and an independent outcome-blinded HumanBaseline. The GUI will not invent a human baseline; use resilientcity.shadow_mode.evaluate_pair for paired files.")
            return
        try:
            results, metrics = evaluate_all()
        except Exception as exc:
            messagebox.showerror(
                "Evaluation error",
                f"The supervised pilot evaluation could not run:\n\n{exc}"
            )
            return

        matched = sum(1 for result in results if result.decision_agreement)
        total = metrics["scenarios"]

        self.eval_statement.config(
            text=f"Adversarial workflow evaluation: {matched}/{total} synthetic scenarios matched the expected outcome.\n"
                 "Workflow validation ≠ real-world readiness. These cases test uncertainty, conflict, escalation and reproducibility."
        )
        self.eval_decision.config(text=f"{matched}/{total}\n({metrics['decision_agreement']:.0%})")
        self.eval_baseline.config(text=f"{metrics['baseline_agreement']:.0%}")
        self.eval_traceability.config(text=f"{metrics['evidence_traceability']:.0%}")
        self.eval_escalations.config(
            text=f"Missed: {metrics['missed_escalations']}\n"
                 f"Unnecessary: {metrics['unnecessary_escalations']}"
        )
        self.eval_repro.config(text=f"{metrics['reproducibility']:.0%}")
        self.eval_execution_time.config(
            text=f"Average Workflow Execution Time: {metrics['avg_workflow_time_ms']:.2f} ms"
        )
        self.eval_scenarios.config(text=f"Scenarios: {total}")

        lines = []
        for result in results:
            agreement = "MATCH" if result.decision_agreement else "DIFFERENT"
            escalation = "HUMAN REVIEW" if result.predicted_escalation else "NO ESCALATION"
            lines.append(
                f"{result.scenario_id} | expected={result.expected_priority} | "
                f"multi-agent={result.predicted_priority} | baseline={result.baseline_priority} | {agreement}\n"
                f"    escalation={escalation} | traceability={result.evidence_traceability:.0%} | "
                f"reproducible={'YES' if result.reproducible else 'NO'}"
            )

        lines.extend([
            "",
            "Methodological note:",
            "A good outcome is not always a classification. Missing, contradictory, or out-of-scope evidence should be escalated rather than forced into LOW/MEDIUM/HIGH.",
            "These controlled scenarios evaluate architecture behaviour, traceability, escalation and reproducibility.",
            "Workflow validation ≠ real-world readiness. Historical cases will require independent review before any operational pilot.",
            "Any future operational pilot begins in SHADOW MODE: people make every decision.",
            "The timing above measures workflow execution time, not human review time.",
        ])
        self._replace(self.eval_results, "\n\n".join(lines))
        self.notebook.select(3)

    def clear_results(self):
        for label in (self.priority, self.evidence_strength, self.safety):
            label.config(text="—")
        for text in (self.report_text, self.trace_text, self.state_text, self.eval_results):
            self._replace(text, "")
        for label in (self.eval_decision, self.eval_baseline, self.eval_traceability,
                      self.eval_escalations, self.eval_repro):
            label.config(text="—")
        self.eval_execution_time.config(text="Average Workflow Execution Time: —")
        self.eval_scenarios.config(text="Scenarios: —")
        self.eval_statement.config(
            text="Standard Evaluation runs deterministic labelled synthetic scenarios only. Historical Shadow Mode uses paired timestamped case/human files."
        )


if __name__ == "__main__":
    ResilientCityGUI().mainloop()
