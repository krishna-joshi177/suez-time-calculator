# Suez Canal Toll Calculator

A Flask-based web app that computes an optimal, time-varying toll for ships entering the Suez Canal, based on queue-theory equilibrium and vessel characteristics.  Features:

- **Equilibrium window** \([t_q,t_{q'}]\) and cost \(TC_e\) calculation  
- **Core time-varying toll** \(\tau_{\rm core}(t)\) to eliminate waiting  
- **Final billed toll** scaled by vessel type & deadweight  
- **Search history** persisted in SQLite, with a “View History” page  
- Responsive, three-column layout with formulas & glossary sidebar  
- Modern UI: Montserrat font, FontAwesome icons, hover/focus effects, blurred ship background

---

## 🛠️ Installation

1. **Clone** the repo  
   ```bash
   git clone https://github.com/<your-username>/suez-toll-calculator.git
   cd suez-toll-calculator
