## models.py

This module is used to read in the main dataframe and to initialise the master and anomaly detection models for the Plot.ly dashboard.

---

### `master: Amodely`

This is the Amodely class for the master dashboard. The selected measure & dimension are the defaults (see `/src/lib/lib.py`).

### `anomaly: Amodely`

This is the Amodely class for the anomaly detection dashboard. The selected measure & dimension are the defaults (see `/src/lib/lib.py`).