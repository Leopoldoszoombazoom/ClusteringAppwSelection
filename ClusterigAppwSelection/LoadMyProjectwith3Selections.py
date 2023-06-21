
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
#from matplotlib.backend_bases import key_press_handler
from tkinter import messagebox
from tkinter import simpledialog
from mpl_toolkits import mplot3d
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import os
import openpyxl
import xlrd




class ClusteringApp():
    def __init__(self, master):
        self.master = master
        self.master.title("Εφαρμογή συσταδοποίησης με Kmeans")
        self.master.iconbitmap('python.ico')
        self.master.geometry("1000x1400")
        self.data = None
        
        ##___________________filename_combo_________________________________________1
        #επιλογή συνόλου δεδομένων απο το filename_combo
        self.filename_combo = ttk.Combobox(self.master, width=20)
        self.filename_combo.pack(pady=5)
        self.filename_combo['values'] = ['winequality-red.csv', 'winequality-white.csv', 'HTRU_2.csv',
                                         'ecoli.data', 'yeast.data', 'abalone.data', 'iris.data',
                                         'Data_Cortex_Nuclear.xls', 'BreastTissue.xls', 'CTG 2.xls']
        self.filename_combo.set('Επιλέξτε σύνολο δεδομένων')
        self.filename_combo.bind('<<ComboboxSelected>>', self.load_data)
        
        ##___________________num_clustersc_combo_________________________________________1
        ##επιλογή αριθμου συστάδων απο το num_clustersc_combo
        self.num_clusters = ttk.Combobox(self.master, width=20)
        self.num_clusters.pack(pady=7)
        self.num_clusters['values'] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.num_clusters.set('Επιλέξτε αριθμό συστάδων')
        self.num_clusters.bind('<<ComboboxSelected>>', self.cluster_data)
        
        
        ##___________________feature_combo_________________________________________3
        ##επιλογή χαρακτηριστικών απο τα feature_combo
        self.feature_combos = [] ##Δημιουργιά κενής λίστας για αποθηκευση Combobox (3)
        feature_frame = tk.Frame(self.master)# Frame(feature_frame) που περιέχει τα Comboboxes
        feature_frame.pack()# τοποθέτηση του feature_frame στο GUI
        
        for i in range(3):#Δημιουργία 3 Comboboxes(feature_combo)
            feature_combo = ttk.Combobox(feature_frame, width=17)# κοινά χαρακτηριστικά και για τα 2 Comboboxes
            feature_combo.pack(side=tk.LEFT, padx=5, pady=5)#τοποθέτηση στο feture_frame
            feature_combo['values'] = []# δημιουργία κενής λίστας values 
            feature_combo.set(f'Χαρακτηριστικό {i+1}')# προεπιλεγμένο κείμενο για το Combobox
            feature_combo.bind('<<ComboboxSelected>>', self.cluster_data)# διαχείριση του συμβάντος όταν ο χρήστης επιλέγει μια επιλογή από οποιοδήποτε από τα τρία γραφικά στοιχεία Combobox.
            self.feature_combos.append(feature_combo)# αποθήκευση των Comboboxes 
        
 
        ##___________________text_widget_________________________________________
        self.text = tk.Text(self.master) # Δημιουργία Text widget
        self.text.pack(fill=tk.BOTH, expand=True) # Τοποθέτηση Text widget στο GUI
        ##___________________load_button_________________________________________
        self.load_button = tk.Button(self.master, text="Φόρτωση δεδομένων", command=self.load_data)# Δημιουργία load_button
        self.load_button.pack(pady=10) # Τοποθέτηση load_button στο GUI
        ##___________________load_button_________________________________________
        self.cluster_button = tk.Button(self.master, text="Συσταδοποιήση", command=self.cluster_data, state=tk.DISABLED)# Δημιουργία cluster_button
        self.cluster_button.pack(pady=10) # Τοποθέτηση cluster_button στο GUI
        ##___________________colormap_label_________________________________________
        self.colormap_label = tk.Label(self.master, text="Επιλογή colormap:")# Δημιουργία colormap_label
        self.colormap_label.pack(pady=7) #Τοποθέτηση colormap_label στο GUI

        self.colormap_var = tk.StringVar() # δημιουργία μεταβλητής τύπου StringVar 
        # Η StringVar χρησιμοποιείται για την αποθήκευση μιας μεταβλητής συμβολοσειράς που σχετίζεται με ένα γραφικό στοιχείο,
        #  όπως ένα πλαίσιο κειμένου ή μια ετικέτα.
        #  Αυτό επιτρέπει τη συγχρονισμένη ενημέρωση του γραφικού στοιχείου όταν η τιμή της μεταβλητής αλλάζει.
        # ################################################
        #Συνολικά, η γραμμή κώδικα που δίνεται δημιουργεί μια μεταβλητή colormap_var τύπου StringVar
        # που μπορεί να χρησιμοποιηθεί για να αποθηκεύσει μια τιμή επιλογής χρωματικού χάρτη.
        
        
        ##___________________colormap_________________________________________
        self.colormap_dropdown = ttk.Combobox(self.master, textvariable=self.colormap_var)
        self.colormap_dropdown['values'] = ('viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues',
                                              'Greens', 'Oranges', 'Reds', 'coolwarm', 'bwr', 'seismic', 'Pastel1', 'Pastel2',
                                                'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b',
                                                  'tab20c', 'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
                                                    'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv', 'gist_rainbow',
                                                      'rainbow', 'jet', 'nipy_spectral', 'gist_ncar')
        
        self.colormap_dropdown.current(22)  # προεπιλεγμένη επιλογή
        self.colormap_dropdown.pack()
        ##___________________Label_________________________________________
        self.label = tk.Label(self.master, text="")# δημιουργία ετικέτας
        self.label.pack(pady=10)
        ##___________________figure_________________________________________
        self.fig = plt.figure()# δημιουργία γραφικής παράστασης
        self.ax = self.fig.add_subplot(projection='3d')
        self.ax.set_axis_off() #απενεργοποιήσει τους άξονες του γραφήματος
        self.ax.xaxis.set_ticklabels([])# απενεργοποιήσει τις ετικέτες των σημάνσεων του άξονα x στο γράφημα
        self.ax.yaxis.set_ticklabels([])# απενεργοποιήσει τις ετικέτες των σημάνσεων του άξονα y στο γράφημα
        self.ax.zaxis.set_ticklabels([])# απενεργοποιήσει τις ετικέτες των σημάνσεων του άξονα z στο γράφημα
        ##___________________FigureCanvasTkAgg!!!!!!!!!!!_________________________________________
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)# δημιουργία ενός αντικειμένου FigureCanvasTkAgg και απεικόνιση του γραφήματος (self.fig) σε αυτόν τον καμβά.
        self.canvas.draw()# απεικονίζει το γράφημα στον καμβά.
        self.canvas.get_tk_widget().pack(fill = tk.BOTH,expand = True)# τοποθέτηση του καμβά στο γραφικό περιβάλλον Tkinter.
        ##_________________________NavigationToolbar2Tk___________________________________
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=False)# τοποθέτηση του NavigationToolbar2Tk στον καμβά.
        self.toolbar.update()#Η κλήση της μεθόδου update() εξασφαλίζει ότι η γραμμή εργαλείων
        #  θα αντικατοπτρίζει τις τρέχουσες αλλαγές και θα είναι ενημερωμένη για να παρέχει τις σωστές λειτουργίες και επιλογές στον χρήστη.
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    
    def load_data(self):
        filename = self.filename_combo.get()# επιλογή συνόλου δεδομένων απο το filename_combo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        print(f'base_dir:{base_dir}')   
        # base_dir: /Users/leopoldoszoombazoom/Documents/myProject2
        if filename == 'winequality-red.csv':
            self.data = pd.read_csv(os.path.join(base_dir, filename), delimiter=';')
            
        elif filename == 'winequality-white.csv':
            self.data = pd.read_csv(os.path.join(base_dir, filename), delimiter=';')
        
        elif filename == 'HTRU_2.csv':
            self.data = pd.read_csv(os.path.join(base_dir, filename), names=['Mean','Std', 'kurtosis',
                                                                              'skewness', 'mean curve',
                                                                                'Std dm','exess kurtosis','Skewness DM-SNR' ,'dm'])
        
        elif filename == 'ecoli.data':
            self.data = pd.read_fwf(os.path.join(base_dir, filename), names=['Sequence Name', 'mcg',
                                                                              'gvh', 'lip', 'chg', 'aac', 'alm1', 'alm2','Class'])
        
        elif filename == 'yeast.data':
            self.data = pd.read_fwf(os.path.join(base_dir, filename), names=['Sequence Name','mcg',
                                                                              'gvh','alm', 'mit', 'erl','pox','vac','nuc',
                                                                              "Class Distribution"])
        
        elif filename == 'abalone.data':
            self.data = pd.read_csv(os.path.join(base_dir, filename), names=['Sex', 'Length', 'Diameter',
                                                                              'Height', 'Whole weight', 'Shucked weight',
                                                                                'Viscera weight', 'Shell weight','Rings'])
            self.data = self.data.select_dtypes(include=np.number)
        
        elif filename == 'iris.data':
            self.data = pd.read_fwf(os.path.join(base_dir, filename), names= ['sepal length','sepal width',
                                                                               'petal length','petal width','class'], delimiter=',')
        
        elif filename == 'Data_Cortex_Nuclear.xls':
            self.data = pd.read_excel(os.path.join(base_dir, filename), engine='xlrd')
            self.data = self.data.select_dtypes(include=np.number)
            self.data = self.data.dropna(axis=1)
        
        elif filename == 'BreastTissue.xls':
            self.data = pd.read_excel(os.path.join(base_dir, filename), sheet_name='Data', engine='xlrd')
        
        elif filename == 'CTG 2.xls':
            header_row = 1
            self.data = pd.read_excel(os.path.join(base_dir, filename), sheet_name='Data', skiprows=header_row, engine='xlrd')
            columns_to_keep = list(range(0, 21)) + [22]
            self.data = self.data.iloc[:, columns_to_keep]
            self.data = self.data.drop("Unnamed: 9", axis=1)
            self.data = self.data.dropna()
    
   
    
        print(filename)
        
        ## μετατροπή των column names σε λίστα
        feature_values = self.data.columns.tolist()
        for combo in self.feature_combos:
            combo['values'] = feature_values
            combo.set('Επιλέξτε χαρακτηριστικό')
        self.cluster_button.config(state=tk.NORMAL)# Ενεργοποίηση του κουμπιού cluster_button
        
        
        data_str = self.data.to_string()# Μετατροπή του αντικειμένου self.data σε μια συμβολοσειρά χρησιμοποιώντας τη μέθοδο to_string().
        
        self.cluster_button.config(state=tk.NORMAL)# Ενεργοποίηση του κουμπιού cluster_button
        
        data_filename = os.path.basename(filename)# Ανάκτηση του ονόματος του αρχείου (filename) χρησιμοποιώντας τη συνάρτηση os.path.basename()
        self.label.config(text=f"Το dataset:{data_filename} φορτώθηκε επιτυχώς!.")#Ενημέρωση της ετικέτας label ότι το σύνολο δεδομένων με όνομα data_filename φορτώθηκε επιτυχώς.
        
        # επαναφορά των οπτικών στοιχείων και των δεδομένων της εφαρμογής 
        self.ax.clear()#Απαλοιφή όλων των ετικετών (x, y, z) του διαγράμματος
        self.ax.set_xlabel('')
        self.ax.set_ylabel('')
        self.ax.set_zlabel('')
        self.ax.grid(True)# ενεργοποιεί το πλέγμα στον άξονα ax
        self.canvas.draw()# επανασχεδιάζει τον καμβά 
        self.text.delete('1.0', tk.END) # άδειασμα του πλαίσιου κειμένου text 
        self.text.insert(tk.END, data_str) # προβολή  data_str στο πλαίσιο κειμένου text widget
            
        


    def select_colormap(self):
        self.colormap = self.colormap_var.get()
        #λήψη της τρέχουσας επιλογής του χρήστη από το combobox colormap_dropdown και αποθήκευση στη μεταβλητή colormap
    
    
    def cluster_data(self,event=None):
            # Εισαγωγή ακεραίου αριθμού συστάδων μέσω της συνάρτησης simpledialog.askinteger((title, prompt, **options))
        selected_num_clusters = int(self.num_clusters.get())
            
        
        # Εμφανιση μυνήματος σε περίπτωση μη επιλογής δεδομένων
        if self.data.empty:
            self.label.config(text="Παρακαλώ φορτώστε πρώτα τα δεδομένα!.")
            return

        # Επιλογή 3 χαρακτηριστικών απο το χρήστη
       
        selected_features = []
        for combo in self.feature_combos:
            feature = combo.get()
            if feature:
                selected_features.append(feature)
                combo['values'] = [x for x in combo['values'] if x != feature]
    
        print(selected_features)
        
        # Αρχικοποίηση μοντέλου KMeans
        kmeans = KMeans(n_clusters=selected_num_clusters)
        # δημιουργία αντικείμενου K-Means clustering με τον αριθμό των συστάδων (n_clusters) που έχει οριστεί στη μεταβλητή self.num_clusters
        # Εκπαίδευση μοντέλου στα επιλεγμένα χαρακτηριστικά
        kmeans.fit(self.data[selected_features])
        self.data["cluster"] = kmeans.labels_# προσθέτει μία νέα στήλη με όνομα "cluster" στο DataFrame self.data
        self.text.delete('1.0', tk.END)  # Απαλοιφή του προηγούμενου κειμένου
        self.text.insert(tk.END, self.data.to_string())#  ενημέρωση του text widget
        self.label.config(text="Επιτυχής συσταδοποιήση!!.")#  ενημέρωση του label 
        self.ax.clear()# απαλοιφή τυχόν προηγούμενης γραφικής παράστασης
        
        if len(selected_features) == 3:
            # Δεδομένα χρωματισμένα ανάλογα με την ομάδα
            self.ax.scatter(self.data[selected_features[0]],
                            self.data[selected_features[1]],
                            self.data[selected_features[2]],
                            c=self.data["cluster"],# το αριθμιτικό αναγνωριστικό καθε γραμμής αντιστοιχεί και σε διαφορετικό χρώμα
                            cmap=self.colormap_var.get(),#  Η τιμή αυτή αντλείται από τη μεταβλητή colormap_var.
                            alpha=0.3,#  Η διαφάνεια των σημείων. Ορίζει πόσο διάφανα είναι τα σημεία, με τιμή από 0 (πλήρης διαφάνεια) έως 1 (αδιαφάνεια).
                             s=10#  Το μέγεθος των σημείων
                            )
            # Κεντροειδή κάθε ομάδας
            self.ax.scatter(kmeans.cluster_centers_[:, 0], 
                    kmeans.cluster_centers_[:, 1], 
                    kmeans.cluster_centers_[:, 2],
                    c='black', 
                    marker='*', 
                    s=60
                    )
            
            
            self.ax.set_title(f'Αριθμός συστάδων:{selected_num_clusters}',fontsize=6)
            
            self.ax.set_xlabel(selected_features[0])# ετικέτα του άξονα x.
            self.ax.set_ylabel(selected_features[1])# ετικέτα του άξονα y.
            self.ax.set_zlabel(selected_features[2])# ετικέτα του άξονα z.                
        
        
        else:
            for cluster in range(self.num_clusters):
                self.ax.scatter(self.data[self.data["cluster"] == cluster][selected_features[0]], 
                                self.data[self.data["cluster"] == cluster][selected_features[1]],
                                c=self.data[self.data["cluster"] == cluster]["cluster"])
        
        self.canvas.draw()



if __name__ == "__main__":
    root = tk.Tk()
    app = ClusteringApp(root)
    root.mainloop()









