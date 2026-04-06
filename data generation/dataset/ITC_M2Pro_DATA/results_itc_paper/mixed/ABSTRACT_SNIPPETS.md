Detection headline (recommended strict):
On the released trace set, the mixed-profile final head achieves ROC-AUC/AUC-PR of 0.8500/0.9592 on the base run score.

Holdout robustness (strict base score):
Under workload holdout, the same head reaches mean AUC-PR 0.8742, worst-case AUC-PR 0.8100, and pooled ROC-AUC/AUC-PR 0.3625/0.8065.

Holdout robustness (workload-conditioned option):
With workload-conditioned scoring, the same holdout evaluation reaches mean AUC-PR 1.0000, worst-case AUC-PR 1.0000, and pooled ROC-AUC/AUC-PR 1.0000/1.0000.

Full-profile upper-bound comparison (use only if it helps):
Switching Tier-1 and Tier-2 from core to full changes base ROC-AUC/AUC-PR to 0.9500/0.9897, strict holdout pooled ROC-AUC/AUC-PR to 0.2375/0.7504, and workload-conditioned holdout pooled ROC-AUC/AUC-PR to 1.0000/1.0000.
