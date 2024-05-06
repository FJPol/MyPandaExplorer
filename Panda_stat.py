"""Erstellt im Rahmes des Python Kurses bei Alphatraining Nov 2023.
Abschlussprojekt Abgabe 01.12.2023

Author: Friedhelm Pol
Python 3.9 Anaconda Umgebung

Einfaches Daten-Exploration Tool mit Plotfunktion über Panda und Seaborn.

Für alle nicht durch andere Lizenzrechte betroffenen Teile des Projektes gilt die MIT Lizenz.

The MIT License (MIT)
Copyright © 2023 Friedhelm Pol

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

from io import StringIO
import csv
import chardet

import matplotlib as mpl
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

mpl.use('TkAgg')

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class DataWindow(tk.Toplevel):
    """Klasse für die Erstellung eines separaten einfachen Daten-Viewers für die eingeladenen Daten.
     Die Darstellung ist statisch. Sollten sich die Daten ändern muss das Fenster neu erstellt werden.
     TKinter hat kein nativen Spreadsheet Windget. Als Workaround wird das tkk Treeview Widget verwendet.
     Nicht optimal aber bessere Libraries ist nicht aktualisiert worden und nicht Teil von Anaconda"""

    def __init__(self, dataframe):
        super().__init__()

        # Frame für TreeView. Da einfaches Layout mit Packmanager.
        frame1 = tk.LabelFrame(self)
        frame1.pack(fill="both", expand=True)
        frame1.pack_propagate(False)

        # Feste Größe für Fenster.
        self.geometry("600x800")
        self.resizable(False, False)
        self.title("Daten Fenster")

        # Icon
        photo = tk.PhotoImage(file=r"pandaface.png")
        self.iconphoto(False, photo)

        # Treeview widget erstellen und Frame füllen.
        tv1 = ttk.Treeview(frame1)
        tv1.place(relheight=1, relwidth=1)

        # Scrollbar erstellen
        treescrolly = tk.Scrollbar(frame1, orient="vertical", command=tv1.yview)
        treescrollx = tk.Scrollbar(frame1, orient="horizontal", command=tv1.xview)
        tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        treescrollx.pack(side="bottom", fill="x")
        treescrolly.pack(side="right", fill="y")

        # Die Daten in die Treemap einfügen
        tv1["column"] = list(dataframe.columns)
        tv1["show"] = "headings"
        # Schreibt die Spaltenbeschriftung
        for column in tv1["columns"]:
            tv1.heading(column, text=column)

        # Erstelle geschachtelte Liste (über eine Numpy Matrix) und füge jede Liste als Zeile ein
        df_rows = dataframe.to_numpy().tolist()
        for row in df_rows:
            tv1.insert("", "end", values=row)


class App(tk.Tk):
    """Hauptklasse. Die App ist ein einfaches Data Exploration Tool für CSV und EXCEL Daten die hinreichend sauber sind.
    Es bietet eine vielzahl an statistischen Betrachtungen und Plot Möglichkeiten im Panda und Seaborn Plot Style.
    Nicht alle optionen sind für alle Daten geeignet. Eine Prüfung darauf, ob die Plots und Statistiken Sinn machen
    muss durch den Anwender erfolgen."""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Erstellen des Mainframes. Die Dimensionen werden durch den Grid Manager bestimmt und sind statisch.
        self.title("Panda Data Tester")
        self.resizable(False, False)
        self.mainframe = ttk.Frame(self, relief="groove", borderwidth=2)
        self.mainframe.grid(row=0, column=1)

        # Icon
        photo = tk.PhotoImage(file=r"pandaface.png")
        self.iconphoto(False, photo)

        # Einige Variablen vordefinieren
        self.filename = ''
        self.df = None
        self.df_temp = None
        self.c_list = []
        self.l_text = ""
        self.s = StringIO()

        # Seaborn Style initiiren
        sns.set_theme()

        # Die Widgets des Hauptfensters erstellen
        self.createWidgets()

        # Die App starten
        self.mainloop()

    def createWidgets(self):
        """Erstellen der Widgets für das Hauptfenster. Unterteilt in zwei individuellen Frames. buttonframe für die
        Menüoptionen und showframe für die darstellenden Elemente"""

        buttonframe = ttk.Frame(self)
        buttonframe.grid(row=0, column=0, sticky='nw')
        # Load Menü aufrufen
        self.b_l = tk.Button(buttonframe, text="Laden", command=self.loaddata)
        self.b_l.grid(row=0, column=0, sticky="nsew")

        # App beenden
        self.b_q = tk.Button(buttonframe, text="Exit", command=self.quit)
        self.b_q.grid(row=1, column=0, sticky="nsew")

        # Drei Spalten für die weitere Betrachtung auswählen
        self.lab_1 = tk.Label(buttonframe, text="X1 | X2 | C")
        self.lab_1.grid(row=2, column=0, sticky="nsew")
        self.box_value = tk.StringVar()
        self.box = ttk.Combobox(buttonframe, textvariable=self.box_value, values=self.c_list, state="readonly",
                                width=15)
        self.box.grid(row=3, column=0, sticky="nsew")
        self.box2_value = tk.StringVar()
        self.box2 = ttk.Combobox(buttonframe, textvariable=self.box2_value, values=self.c_list, state="readonly",
                                 width=15)
        self.box2.grid(row=4, column=0, sticky="nsew")
        self.box3_value = tk.StringVar()
        self.box3 = ttk.Combobox(buttonframe, textvariable=self.box3_value, values=self.c_list, state="readonly",
                                 width=15)
        self.box3.grid(row=5, column=0, sticky="nsew")

        # Verschiedene Statistiken abfragen. Diese werden in der Textbox dargestellt.
        self.b_i = tk.Button(buttonframe, text="Info", command=self.info)
        self.b_i.grid(row=6, column=0, sticky="nsew")
        self.b_h = tk.Button(buttonframe, text="Ersten 10", command=self.head)
        self.b_h.grid(row=7, column=0, sticky="nsew")
        self.b_v = tk.Button(buttonframe, text="X1 Auswertung", command=self.varexplo)
        self.b_v.grid(row=8, column=0, sticky="nsew")

        # Groupby Statistiken
        self.b_g = tk.Button(buttonframe, text="X1 Gruppe", command=self.vargroup)
        self.b_g.grid(row=9, column=0, sticky="nsew")
        self.b_g_dd = tk.Button(buttonframe, text="X1 & X2 Gruppe", command=self.vargroup_dd)
        self.b_g_dd.grid(row=10, column=0, sticky="nsew")
        self.b_g_dd = tk.Button(buttonframe, text="X1 & X2 & C Gruppe", command=self.vargroup_c)
        self.b_g_dd.grid(row=11, column=0, sticky="nsew")

        # Darstellungsoptionen für die Plots.
        self.lab_2 = tk.Label(buttonframe,
                              text="Plot Optionen\nACHTUNG!\nBei ungeeigneten Daten\nkann sehr viel Speicher"
                                   "\nund Rechenzeit\nverbraucht werden:\nVorsicht bei Bar und \nHistogram")
        self.lab_2.grid(row=14, column=0, sticky="nsew")

        # Auswahl der Plotart
        tkoptionlist = ["Lines Panda", "Lines X1/X2", "Bar Panda", "Bar X1/X2", "Hist Panda",
                        "Hist X1", "Box Panda", "Box X1", "Area Panda", "Area Transp",
                        "Scatter X1/X2", "Scatter Heat C", "Hexbin X1/X2", "KDE Panda", "SNS Treppe",
                        "SNS Strip X1", "SNS Violin", "SNS Point X1/X2", "SNS Regresion X1/X2",
                        "SNS Residuals X1/X2", "SNS Heat", "Test"]
        self.box_value_plot = tk.StringVar()
        self.box_p = ttk.Combobox(buttonframe, textvariable=self.box_value_plot, values=tkoptionlist, state="readonly",
                                  width=15)
        self.box_p.grid(row=15, column=0, sticky="nsew")
        self.box_p.current(0)

        # Auswahl der verschiedenen SNS Optionen
        sns_styles = ["darkgrid", "whitegrid", "dark", "white", "ticks"]
        self.box_value_sns_st = tk.StringVar()
        self.box_p = ttk.Combobox(buttonframe, textvariable=self.box_value_sns_st, values=sns_styles, state="readonly",
                                  width=15)
        self.box_p.grid(row=16, column=0, sticky="nsew")
        self.box_p.current(0)
        sns_context = ["notebook", "paper", "talk", "poster"]
        self.box_value_sns_co = tk.StringVar()
        self.box_p = ttk.Combobox(buttonframe, textvariable=self.box_value_sns_co, values=sns_context, state="readonly",
                                  width=15)
        self.box_p.grid(row=17, column=0, sticky="nsew")
        self.box_p.current(0)
        sns_palette = ["deep", "muted", "bright", "pastel", "dark", "colorblind"]
        self.box_value_sns_pa = tk.StringVar()
        self.box_p = ttk.Combobox(buttonframe, textvariable=self.box_value_sns_pa, values=sns_palette, state="readonly",
                                  width=15)
        self.box_p.grid(row=18, column=0, sticky="nsew")
        self.box_p.current(0)

        # Plot plotten
        self.b_2d = tk.Button(buttonframe, text="2D Plot", command=self.plot_2d)
        self.b_2d.grid(row=19, column=0, sticky="nsew")

        # Andere Statistik Option. Wird wo anders plaziert durch den Grid Manager
        self.b_adv = tk.Button(buttonframe, text="Adv. Stat", command=self.adv_stat)
        self.b_adv.grid(row=12, column=0, sticky="nsew")

        # Duplicate
        self.b_adv = tk.Button(buttonframe, text="Duplicate", command=self.duplicates)
        self.b_adv.grid(row=13, column=0, sticky="nsew")

        # Grid Box um Koordinatennetz zu zeichnen, SNS Style um eine Alternative Darstellung zu ermöglichen.
        self.c1_var = tk.IntVar()
        self.c1 = tk.Checkbutton(buttonframe, text="Grid", variable=self.c1_var, onvalue=1, offvalue=0)
        self.c1.grid(row=20, column=0, sticky="nw")
        self.c_sns_v = tk.IntVar()
        self.c_sns = tk.Checkbutton(buttonframe, text="Seaborn", variable=self.c_sns_v, onvalue=1, offvalue=0)
        self.c_sns.grid(row=21, column=0, sticky="nw")

        # Das Datenfenster erneut darstellen
        self.b_show = tk.Button(buttonframe, text="Reopen Data", command=self.data_show)
        self.b_show.grid(row=22, column=0, sticky="nsew")

        # Frame für die Datenvisualisierung und Ausgabe der Statistik
        self.showframe = ttk.Frame(self)
        self.showframe.grid(row=0, column=1, sticky="n")

        # Text Widget um die Ausgabe der Statistik-Funktionen darzustellen
        self.l_i = tk.Text(self.showframe, width=120)
        self.l_i.grid(row=0, column=0, sticky="nsw")

        # Erstellen der Scrollbar für die Textbox. X-Achse eventuell ohne Funktion?
        scrollbar = ttk.Scrollbar(self.showframe, orient='vertical', command=self.l_i.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        scrollbar2 = ttk.Scrollbar(self.showframe, orient='horizontal', command=self.l_i.xview)
        scrollbar2.grid(row=1, column=0, sticky=tk.EW)
        self.l_i['yscrollcommand'] = scrollbar.set
        self.l_i['xscrollcommand'] = scrollbar2.set

        # Löscht den Text im Fenster
        self.b_cls = tk.Button(self.showframe, text="Text löschen", command=self.cls_text)
        self.b_cls.grid(row=2, column=0, sticky=tk.EW)

        # Erstellen des Plotframes und Canvas für die Plots
        self.figure = plt.Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.showframe)
        self.canvas.get_tk_widget().grid(row=3, column=0, sticky="nsew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.showframe, pack_toolbar=False)
        self.toolbar.grid(column=0, row=4, sticky="nsew")

        # Button um Manuell den Plot zu löschen. Nicht mehr so nötig wie in der ersten Version.
        self.b_clp = tk.Button(self.showframe, text="Lösche Plot", command=self.clearplot)
        self.b_clp.grid(row=5, column=0, columnspan=2, sticky="nsew")

    def loaddata(self):
        """Ermöglicht der App CSV und EXCEL Daten in einen Panda Datenframe einzulesen.
        Dabei wird versucht den CSV Dialekt und Encoding automatisch zu bestimmen, um eine
        besser Kompatibilität zu erreichen.

        Danach werden die Spaltenbeschriftungen für die Combo-Boxen herausgelesen und das
        Datenfenster gefüllt."""

        # Steuervariablen
        dialect = None
        encoding = None
        loadin = False

        # Öffnen des Datei-Laden Fenster
        try:
            self.filename = filedialog.askopenfilename(
                filetypes=[("csv files", "*.csv"), ("Excel file", "*.xlsx"), ("All files", "*.*")],
                initialdir=r"C:\Users\alfa\PycharmProjects\pythonProject", title="Select Datafile:")
            print(self.filename, type(self.filename))
        except:
            messagebox.showerror("Fehler", "Beim Laden der Datei ist ein Fehler aufgetreten")

        # Routine für das Einlesen der CSV Daten
        if self.filename.split(".")[-1] == "csv":
            # Autodetect des Dialektes mithilfe von Sniffer
            try:
                with open(self.filename, 'r', newline='') as csv_file:
                    dialect = csv.Sniffer().sniff(csv_file.read(2048))
                    print("Sniff: ", dialect.delimiter, dialect.doublequote, repr(dialect.lineterminator),
                          dialect.quotechar)
            except:
                pass
            # Autodetect des Encodings mithilfe der Library Chardet
            try:
                with open(self.filename, 'rb') as f:
                    data = f.read(1024)  # or a chunk, f.read(1000000)
                encoding = chardet.detect(data).get("encoding")
                print(encoding)
            except:
                pass

            # Einlesen der CSV Daten anhand der vorhandenen Informationen. Inkl. eines Failsave-Versuches mit Default.
            if dialect and encoding:
                try:
                    self.df = pd.read_csv(self.filename, on_bad_lines="warn", dialect=dialect, encoding=encoding)
                    print("Dialect + Encoding import")
                    loadin = True
                except:
                    try:
                        self.df = pd.read_csv(self.filename, on_bad_lines="warn")
                        print("FAILBACK Dialect + Encoding")
                        loadin = True
                    except:
                        messagebox.showerror("Fehler", "Beim Einlesen der CSV-Daten ist ein Fehler aufgetreten")

            elif dialect:
                try:
                    self.df = pd.read_csv(self.filename, on_bad_lines="warn", dialect=dialect)
                    loadin = True
                except:
                    try:
                        self.df = pd.read_csv(self.filename, on_bad_lines="warn")
                        print("FAILBACK Dialect")
                        loadin = True
                    except:
                        messagebox.showerror("Fehler", "Beim Einlesen der CSV-Daten ist ein Fehler aufgetreten")


            elif encoding:
                try:
                    self.df = pd.read_csv(self.filename, on_bad_lines="warn", encoding=encoding)
                    loadin = True
                except:
                    try:
                        self.df = pd.read_csv(self.filename, on_bad_lines="warn")
                        print("FAILBACK Encoding")
                        loadin = True
                    except:
                        messagebox.showerror("Fehler", "Beim Einlesen der CSV-Daten ist ein Fehler aufgetreten")

            else:
                try:
                    self.df = pd.read_csv(self.filename, on_bad_lines="warn")
                    print("Autoimport CSV")
                    loadin = True
                except:
                    messagebox.showerror("Fehler", "Beim Einlesen der CSV-Daten ist ein Fehler aufgetreten")

        # Einlesen der Exceldaten
        elif self.filename.split(".")[-1] == "xlsx":
            try:
                self.df = pd.read_excel(self.filename)
                loadin = True
            except:
                messagebox.showerror("Fehler", "Beim Einlesen der XLSX-Daten ist ein Fehler aufgetreten")

        # Befüllen der Combofenster Listen für die Spaltenauswahl
        if loadin:
            print(self.df, type(self.df))
            self.c_list = self.df.columns.tolist()
            print(self.c_list)
            self.box["values"] = self.c_list
            self.box.current(0)
            self.box2["values"] = self.c_list
            self.box2.current(0)
            self.box3["values"] = self.c_list
            self.box3.current(0)

            # Starten des Datenfensters
            self.data_show()

    def info(self):
        """Ausgabe des Pandas df.info. Dies wir dadurch erschwert, dass die Ausgabe direkt innerhalb der
        Methode erfolgt. Deshalb muss an dieser Stelle StdIO in einen Daten-Stream mithilfe von
        StrinIO umgeleitet werden. Das Ergebnis wird in die Texbox eingefügt."""

        self.df.info(verbose=True, buf=self.s)
        self.l_text = "\n\n" + str(self.s.getvalue())
        self.s = StringIO()
        self.l_i.insert(tk.END, self.l_text)

    def head(self):
        """Ausgabe von df.head() in die Textbox. Legacy da mit dem Datenfenster eine bessere Lösung zur darstellung
        da ist. Ist aber immer noch zum überblick bekommen sinnvoll"""

        self.l_text = self.df.head(10)
        self.l_i.insert(tk.END, self.l_text)

    def duplicates(self):
        self.df_temp = self.df[self.df.duplicated(keep=False)]
        self.l_text = f"\n\nDuplicates:\n"
        self.l_text = self.l_text + str(self.df_temp.sort_values(by=self.box_value.get()))
        self.df_temp = self.df[self.df.duplicated(subset=[self.box_value.get()], keep=False)]
        self.l_text = self.l_text + f"\n\nDuplicates for X1:\n"
        self.l_text = self.l_text + str(self.df_temp.sort_values(by=self.box_value.get()))

        self.l_i.insert(tk.END, self.l_text)

    def varexplo(self):
        """Darstellung verschiedener Panda Statistiken in der Textbox"""
        try:
            self.l_text = f"\n\nFür {self.box_value.get()}:\n"
            self.l_text = self.l_text + "Size: " + str(self.df[self.box_value.get()].size) + "\n"
            self.l_text = self.l_text + "Not NaN: " + str(self.df[self.box_value.get()].count()) + "\n\n"
            self.l_text = self.l_text + "Min: " + str((self.df[self.box_value.get()]).min()) + "\n"
            self.l_text = self.l_text + "Max: " + str((self.df[self.box_value.get()]).max()) + "\n"
            self.l_text = self.l_text + "Mean: " + str((self.df[self.box_value.get()]).mean()) + "\n"
            self.l_text = self.l_text + "Median: " + str((self.df[self.box_value.get()]).median()) + "\n\n"
            self.l_text = self.l_text + "Q 25%/75%:\n" + str((self.df[self.box_value.get()]).quantile([.25, .75])) \
                          + "\n\n"
            self.l_text = self.l_text + "Summe: " + str((self.df[self.box_value.get()]).sum()) + "\n\n"
            self.l_text = self.l_text + "Std. Abw: " + str((self.df[self.box_value.get()]).std()) + "\n"
            self.l_text = self.l_text + "Varianz: " + str((self.df[self.box_value.get()]).var()) + "\n"

            self.l_i.insert(tk.END, self.l_text)
        except:
            messagebox.showerror("Fehler", "Beim Auswerten der Spalte ist ein Fehler aufgetreten")

    def vargroup(self):
        """Darstellung verschiedener Panda Statistiken mit einem Groupby in der Textbox. Da die Quartalsdarstellung
        empfindlicher gegenüber den Eingangsdaten ist, habe ich sie erstmal herausgenommen."""
        try:
            self.l_text = f"\n\nFür Gruppen in {self.box_value.get()}:\n"
            self.l_text = self.l_text + "Not NaN:\n " + str(self.df.groupby([self.box_value.get()]).count()) + "\n\n"
            self.l_text = self.l_text + "Min: \n" + str(self.df.groupby([self.box_value.get()]).min()) + "\n\n"
            self.l_text = self.l_text + "Max: \n" + str(self.df.groupby([self.box_value.get()]).max()) + "\n\n"
            self.l_text = self.l_text + "Mean: \n" + str(self.df.groupby([self.box_value.get()]).mean()) + "\n\n"
            self.l_text = self.l_text + "Median: \n" + str(self.df.groupby([self.box_value.get()]).median()) + "\n\n"
            # self.l_text = self.l_text + "Q 25%/75%:\n" + str(self.df.groupby([self.box_value.get()]).quantile([.25, .75])) + "\n\n"
            self.l_text = self.l_text + "Summe: \n" + str(self.df.groupby([self.box_value.get()]).sum()) + "\n\n"
            self.l_text = self.l_text + "Std. Abw: \n" + str(self.df.groupby([self.box_value.get()]).std()) + "\n\n"
            self.l_text = self.l_text + "Varianz: \n" + str(self.df.groupby([self.box_value.get()]).var()) + "\n\n"
            self.l_i.insert(tk.END, self.l_text)
        except:
            messagebox.showerror("Fehler", "Beim Auswerten der Spalte ist ein Fehler aufgetreten")

    def vargroup_dd(self):
        """Darstellung verschiedener Panda Statistiken mit zwei Groupby in der Textbox. Da die Quartalsdarstellung
        empfindlicher gegenüber den Eingangsdaten ist, habe ich sie erstmal herausgenommen."""
        try:
            local_list = [self.box_value.get(), self.box2_value.get()]
            self.l_text = f"\n\nFür Gruppen in {local_list}:\n"
            self.l_text = self.l_text + "Not NaN: \n" + str(self.df.groupby(local_list).count()) + "\n\n"
            self.l_text = self.l_text + "Min: \n" + str(self.df.groupby(local_list).min()) + "\n\n"
            self.l_text = self.l_text + "Max: \n" + str(self.df.groupby(local_list).max()) + "\n\n"
            self.l_text = self.l_text + "Mean: \n" + str(self.df.groupby(local_list).mean()) + "\n\n"
            self.l_text = self.l_text + "Median: \n" + str(self.df.groupby(local_list).median()) + "\n\n"
            # self.l_text = self.l_text + "Q 25%/75%:\n" + str(self.df.groupby(local_list).quantile([.25, .75])) + "\n\n"
            self.l_text = self.l_text + "Summe: \n" + str(self.df.groupby(local_list).sum()) + "\n\n"
            self.l_text = self.l_text + "Std. Abw: \n" + str(self.df.groupby(local_list).std()) + "\n\n"
            self.l_text = self.l_text + "Varianz: \n" + str(self.df.groupby(local_list).var()) + "\n\n"
            self.l_i.insert(tk.END, self.l_text)
        except:
            messagebox.showerror("Fehler", "Beim Auswerten der Spalte ist ein Fehler aufgetreten")

    def vargroup_c(self):
        """Darstellung verschiedener Panda Statistiken mit drei Groupby in der Textbox. Da die Quartalsdarstellung
        empfindlicher gegenüber den Eingangsdaten ist, habe ich sie erstmal herausgenommen."""
        try:
            local_list = [self.box_value.get(), self.box2_value.get(), self.box3_value.get()]
            self.l_text = f"\n\nFür Gruppen in {local_list}:\n"
            self.l_text = self.l_text + "Not NaN: \n" + str(self.df.groupby(local_list).count()) + "\n\n"
            self.l_text = self.l_text + "Min: \n" + str(self.df.groupby(local_list).min()) + "\n\n"
            self.l_text = self.l_text + "Max: \n" + str(self.df.groupby(local_list).max()) + "\n\n"
            self.l_text = self.l_text + "Mean: \n" + str(self.df.groupby(local_list).mean()) + "\n\n"
            self.l_text = self.l_text + "Median: \n" + str(self.df.groupby(local_list).median()) + "\n\n"
            # self.l_text = self.l_text + "Q 25%/75%:\n" + str(self.df.groupby(local_list).quantile([.25, .75])) + "\n\n"
            self.l_text = self.l_text + "Summe: \n" + str(self.df.groupby(local_list).sum()) + "\n\n"
            self.l_text = self.l_text + "Std. Abw: \n" + str(self.df.groupby(local_list).std()) + "\n\n"
            self.l_text = self.l_text + "Varianz: \n" + str(self.df.groupby(local_list).var()) + "\n\n"
            self.l_i.insert(tk.END, self.l_text)
        except:
            messagebox.showerror("Fehler", "Beim Auswerten der Spalte ist ein Fehler aufgetreten")

    def adv_stat(self):
        """Darstellung von Statistiken die etwas mehr Interpretation und Wissen durch den Anwender erfolgen.
        Die Berechnung erfolg mithilfe von NumPy Datentypen und SciPy."""

        # Erstelle eine Slice der ausgewählten Daten in ein temporäres Panda Dataframe.
        local_list = [self.box_value.get(), self.box2_value.get(), self.box3_value.get()]
        tmp_df = self.df.loc[:, local_list]
        print(tmp_df)

        # Darstellung der Korrelationskoifizientmatrix des Dataslices in Panda.
        self.l_text = f"\n\nPerson paarweiser Korrelationskoifizient 2 Seitig 95%\n\n"
        self.l_text = self.l_text + str(tmp_df.corr(method="pearson")) + "\n\n"
        self.l_text = self.l_text + f"\n\nSpearman paarweiser Korrelationskoifizient 2 Seitig 95%\n\n"
        self.l_text = self.l_text + str(tmp_df.corr(method="spearman")) + "\n\n"

        # Vorbereitung der Daten in NumPy Arrays
        x = np.array(self.df.loc[:, self.box_value.get()])
        y = np.array(self.df.loc[:, self.box2_value.get()])
        z = np.array(self.df.loc[:, self.box3_value.get()])

        # Shapiro - Wilk und Anderson Normalverteilungstest mithilfe von SciPy.
        self.l_text = self.l_text + f"Describe {self.box_value.get()} mit SciPy:\n" + str(stats.describe(x)) + "\n\n"
        self.l_text = self.l_text + f"{self.box_value.get()} hat {len(x)} Werte. Unter 10 Werten ist Anderson" \
                                    f" eventuell nicht geeignet. Für n >> als 30 sind die Tests nicht geeignet.\n\n"
        print(x, type(x))
        res = stats.shapiro(x)
        self.l_text = self.l_text + f"Shapiro-Wilk Test auf Normalverteilung für {self.box_value.get()}\n"
        self.l_text = self.l_text + f"Statistik: {res.statistic}, p-Wert(95%): {res.pvalue}\n\n"
        res = stats.anderson(x)
        self.l_text = self.l_text + f"Anderson-Darling Test auf Normalverteilung für {self.box_value.get()}\n"
        self.l_text = self.l_text + f"Statistik: {res.statistic}\nKritische Werte: {res.critical_values}\n" \
                                    f"Signifikanzlevel: {res.significance_level}\n"
        self.l_text = self.l_text + "Wenn die Teststatistik kleiner ist als die kritischen Werte gilt H0(Normalverteilt)" \
                                    " für das Signifikanzlevel.\n\n"

        # Varianzanalysen mithilfe von SciPy
        self.l_text = self.l_text + f"T-Test: {self.box_value.get()} / {self.box2_value.get()} unabhängig 95% H0: " \
                                    f"gleiche Population:\n"
        self.l_text = self.l_text + str(stats.ttest_ind(x, y)) + "\n\n"
        self.l_text = self.l_text + f"T-Test: {self.box_value.get()} / {self.box2_value.get()} abhängig 95% H0: " \
                                    f"gleiche Population:\n"
        self.l_text = self.l_text + str(stats.ttest_rel(x, y)) + "\n\n"
        self.l_text = self.l_text + f"F - Varianztest (One Way ANOVA like) {self.box_value.get()} / " \
                                    f"{self.box2_value.get()}:\n" + str(stats.f_oneway(x, y)) + "\n\n"
        self.l_text = self.l_text + f"F - Varianztest (One Way ANOVA like) {self.box_value.get()} / " \
                                    f"{self.box2_value.get()} / {self.box3_value.get()}:\n" \
                      + str(stats.f_oneway(x, y, z)) + "\n\n"
        self.l_text = self.l_text + f"H - Varianztest (Kruskal-Wallis) {self.box_value.get()} / " \
                                    f"{self.box2_value.get()}:\n" + str(stats.kruskal(x, y)) + "\n\n"
        self.l_text = self.l_text + f"H - Varianztest (Kruskal-Wallis) {self.box_value.get()} / " \
                                    f"{self.box2_value.get()} / {self.box3_value.get()}:\n" \
                      + str(stats.kruskal(x, y, z)) + "\n\n"
        self.l_i.insert(tk.END, self.l_text)

    def cls_text(self):
        """Löschen des Textfeldes"""
        self.l_i.delete('1.0', tk.END)

    def plot_2d(self):
        """Plotfunktion um die Ausgewählten Plotoptionen im unteren Canvas darzustellen. Der Anwender kann dabei
        aus einer vielzahl an Optionen wählen. Die Darstellung erfolgt über Panda.polt und Seaborn. Die Themen sind
        die in Seaborn vordefinierten Themen."""
        # Individuelle Seaborn themen initiiren
        sns.set_theme(context=self.box_value_sns_co.get(), style=self.box_value_sns_st.get(),
                      palette=self.box_value_sns_pa.get())

        self.clearplot()

        # Individuelle Seaborn themen initiiren
        sns.set_theme(context=self.box_value_sns_co.get(), style=self.box_value_sns_st.get(),
                      palette=self.box_value_sns_pa.get())

        # Daten aus den Auswahlboxen und in temp Variablen übergeben.
        tmp_x = self.box_value.get()
        tmp_y = self.box2_value.get()
        tmp_c = self.box3_value.get()
        tmp_g = self.c1_var.get()

        # Titel ist Filename
        self.axes.set_title(f"{self.filename.split('/')[-1]}")

        # Grid Checkbox für Seaborn. Das ist nicht ohne Eigenheiten da einige Seaborn Themen eigentlich kein
        # Grid haben wollen. Weshalb manchmal die Checkbox ohne Wirkung ist und mehrfach geplottet werden muss.
        if not self.c1_var.get():
            self.axes.grid()

        # Auswahl der richtigen Plotfunktion anhand der Anwenderauswahl
        # Linien Plot
        if self.box_value_plot.get() == "Lines Panda":
            if not self.c_sns_v.get():
                self.df.plot(kind="line", grid=tmp_g, ax=self.axes)
            else:
                sns.lineplot(data=self.df, ax=self.axes)

        elif self.box_value_plot.get() == "Lines X1/X2":
            if not self.c_sns_v.get():
                self.df.plot(kind="line", x=f"{tmp_x}", y=f"{tmp_y}", grid=tmp_g, ax=self.axes)
            else:
                sns.lineplot(data=self.df, x=f"{tmp_x}", y=f"{tmp_y}", ax=self.axes)
        # Bar Plot
        elif self.box_value_plot.get() == "Bar Panda":
            if not self.c_sns_v.get():
                self.df.plot(kind="bar", grid=tmp_g, ax=self.axes)
            else:
                sns.barplot(data=self.df, ax=self.axes)

        elif self.box_value_plot.get() == "Bar X1/X2":
            if not self.c_sns_v.get():
                self.df.plot(kind="bar", x=f"{tmp_x}", y=f"{tmp_y}", grid=tmp_g, ax=self.axes)
            else:
                sns.barplot(data=self.df, x=f"{tmp_x}", y=f"{tmp_y}", ax=self.axes)

        # Histogram
        elif self.box_value_plot.get() == "Hist Panda":
            if not self.c_sns_v.get():
                self.df.plot(kind="hist", grid=tmp_g, ax=self.axes)
            else:
                sns.histplot(data=self.df, ax=self.axes)

        elif self.box_value_plot.get() == "Hist X1":
            if not self.c_sns_v.get():
                self.df.plot(kind="hist", y=f"{tmp_x}", grid=tmp_g, ax=self.axes)
            else:
                sns.histplot(data=self.df, y=f"{tmp_x}", ax=self.axes)

        # Boxplot
        elif self.box_value_plot.get() == "Box Panda":
            if not self.c_sns_v.get():
                self.df.plot(kind="box", grid=tmp_g, ax=self.axes)
            else:
                sns.boxplot(data=self.df, ax=self.axes)

        elif self.box_value_plot.get() == "Box X1":
            if not self.c_sns_v.get():
                self.df.plot(kind="box", y=f"{tmp_x}", grid=tmp_g, ax=self.axes)
            else:
                sns.boxplot(data=self.df, y=f"{tmp_x}", ax=self.axes)

        # Flächen-Linien-Plot
        elif self.box_value_plot.get() == "Area Panda":
            if not self.c_sns_v.get():
                self.df.plot(kind="area", grid=tmp_g, ax=self.axes)
            else:
                messagebox.showinfo(message="Nicht direkt in Seaborn implementiert")

        elif self.box_value_plot.get() == "Area Transp":
            if not self.c_sns_v.get():
                self.df.plot(kind="area", grid=tmp_g, stacked=False, ax=self.axes)
            else:
                messagebox.showinfo(message="Nicht direkt in Seaborn implementiert")

        # Scatterplot
        elif self.box_value_plot.get() == "Scatter X1/X2":
            if not self.c_sns_v.get():
                self.df.plot(kind="scatter", x=f"{tmp_x}", y=f"{tmp_y}", grid=tmp_g, ax=self.axes)
            else:
                sns.scatterplot(data=self.df, x=f"{tmp_x}", y=f"{tmp_y}", ax=self.axes)

        elif self.box_value_plot.get() == "Scatter Heat C":
            if not self.c_sns_v.get():
                self.df.plot(kind="scatter", x=f"{tmp_x}", y=f"{tmp_y}", c=f"{tmp_c}", grid=tmp_g, ax=self.axes)
            else:
                sns.scatterplot(data=self.df, x=f"{tmp_x}", y=f"{tmp_y}", hue=f"{tmp_c}",
                                size=f"{tmp_c}", ax=self.axes)
                sns.rugplot(data=self.df, x=f"{tmp_x}", y=f"{tmp_y}", ax=self.axes)

        # Hexbin Plot (Kombiniert Heatmap und Histogram in Hexagon Darstellung)
        elif self.box_value_plot.get() == "Hexbin X1/X2":
            if not self.c_sns_v.get():
                self.df.plot(kind="hexbin", x=f"{tmp_x}", y=f"{tmp_y}", gridsize=25, grid=tmp_g, ax=self.axes)
            else:
                messagebox.showinfo(message="Nicht direkt in Seaborn implementiert")

        # Verteilung / Dichteplot
        elif self.box_value_plot.get() == "KDE Panda":
            if not self.c_sns_v.get():
                self.df.plot(kind="kde", grid=tmp_g, ax=self.axes)
            else:
                sns.kdeplot(data=self.df, ax=self.axes)

        # SNS Treppenplot
        elif self.box_value_plot.get() == "SNS Treppe":
            sns.ecdfplot(data=self.df, ax=self.axes)

        # SNS Stripplot
        elif self.box_value_plot.get() == "SNS Strip X1":
            sns.stripplot(data=self.df, x=f"{tmp_x}", ax=self.axes)

        # SNS Violin Plot
        elif self.box_value_plot.get() == "SNS Violin":
            sns.violinplot(data=self.df, ax=self.axes)

        # SNS Pointplot
        elif self.box_value_plot.get() == "SNS Point X1/X2":
            sns.pointplot(data=self.df, x=f"{tmp_x}", y=f"{tmp_y}", ax=self.axes)

        # SNS Regression
        elif self.box_value_plot.get() == "SNS Regresion X1/X2":
            sns.regplot(data=self.df, x=f"{tmp_x}", y=f"{tmp_y}", ax=self.axes)

        # SNS Residuals
        elif self.box_value_plot.get() == "SNS Residuals X1/X2":
            sns.residplot(data=self.df, x=f"{tmp_x}", y=f"{tmp_y}", ax=self.axes)

        # SNS Heatmap
        elif self.box_value_plot.get() == "SNS Heat":
            sns.heatmap(data=self.df, ax=self.axes)

        # Zum Testen
        elif self.box_value_plot.get() == "Test":
            self.df.plot(table=self.df, ax=self.axes)

        # Zeichnet den Plot im Canvas
        self.canvas.draw()

    def clearplot(self):
        """Erstellt den Canvas komplett neu, da ansonsten einige Elemente nicht gelöscht werden"""
        try:
            self.axes.cla()
            self.figure.clf()
            self.figure = plt.Figure()
            self.axes = self.figure.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.showframe)
            self.canvas.get_tk_widget().grid(row=3, column=0, sticky="nsew")
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.showframe, pack_toolbar=False)
            # matplotlib navigation toolbar; "pack_toolbar = False" necessary for .grid() geometry manager
            self.toolbar.grid(column=0, row=4, sticky="nsew")
        except:
            pass
        self.canvas.draw()

    def data_show(self):
        """Öffnet das Datenfenster"""
        DataWindow(self.df)


if __name__ == "__main__":
    #    print("Testloop")
    app = App()
