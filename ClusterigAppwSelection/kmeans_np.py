"""KMeans μόνο με NumPy — αντικαθιστά το sklearn.cluster.KMeans.

Το scikit-learn χρειάζεται το SciPy, του οποίου τα αρχεία .pyd δεν είναι υπογεγραμμένα
και τα μπλοκάρει το Smart App Control των Windows. Η κλάση έχει το ίδιο API με του
sklearn (fit, predict, labels_, cluster_centers_, inertia_), οπότε ο υπόλοιπος κώδικας
δεν αλλάζει.
"""
import numpy as np


class KMeans:
    def __init__(self, n_clusters=8, n_init=10, max_iter=300, tol=1e-4, random_state=None):
        self.n_clusters = n_clusters
        self.n_init = n_init
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state

    @staticmethod
    def _sq_dist(X, centers):
        # τετράγωνο της ευκλείδειας απόστασης κάθε σημείου από κάθε κέντρο, σχήμα (n, k):
        # |x - c|^2 = |x|^2 - 2 x·c + |c|^2  (γρήγορο, με πολλαπλασιασμό πινάκων)
        d = (X ** 2).sum(axis=1)[:, None] - 2 * X @ centers.T + (centers ** 2).sum(axis=1)[None, :]
        return np.maximum(d, 0)  # αποκοπή μικρών αρνητικών από σφάλματα στρογγυλοποίησης

    def _init_centers(self, X, rng):
        # k-means++: κάθε νέο κέντρο επιλέγεται με πιθανότητα ανάλογη της απόστασης^2
        # από το πλησιέστερο ήδη επιλεγμένο κέντρο
        n = X.shape[0]
        centers = [X[rng.integers(n)]]
        closest = self._sq_dist(X, np.array(centers))[:, 0]
        for _ in range(1, self.n_clusters):
            total = closest.sum()
            idx = rng.choice(n, p=closest / total) if total > 0 else rng.integers(n)
            centers.append(X[idx])
            closest = np.minimum(closest, self._sq_dist(X, X[idx:idx + 1])[:, 0])
        return np.array(centers)

    def _single_run(self, X, rng):
        centers = self._init_centers(X, rng)
        # ανοχή σχετική με τη διασπορά των δεδομένων, όπως στο sklearn
        tol = self.tol * X.var(axis=0).mean()
        for _ in range(self.max_iter):
            labels = self._sq_dist(X, centers).argmin(axis=1)
            new_centers = centers.copy()
            for j in range(self.n_clusters):
                members = X[labels == j]
                if len(members):  # μια άδεια συστάδα κρατά το παλιό της κέντρο
                    new_centers[j] = members.mean(axis=0)
            shift = ((new_centers - centers) ** 2).sum()
            centers = new_centers
            if shift <= tol:
                break
        d = self._sq_dist(X, centers)
        labels = d.argmin(axis=1)
        inertia = d[np.arange(len(X)), labels].sum()
        return labels, centers, inertia

    def fit(self, X):
        X = np.asarray(X, dtype=float)
        if X.shape[0] < self.n_clusters:
            raise ValueError(f"n_samples={X.shape[0]} πρέπει να είναι >= n_clusters={self.n_clusters}")
        rng = np.random.default_rng(self.random_state)
        best = None
        for _ in range(self.n_init):  # κρατάμε την εκτέλεση με τη μικρότερη inertia
            run = self._single_run(X, rng)
            if best is None or run[2] < best[2]:
                best = run
        self.labels_, self.cluster_centers_, self.inertia_ = best
        return self

    def predict(self, X):
        return self._sq_dist(np.asarray(X, dtype=float), self.cluster_centers_).argmin(axis=1)

    def fit_predict(self, X):
        return self.fit(X).labels_
