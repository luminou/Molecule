"""
@author: clementine.garoche
Visualiser les donnees all molecules all ligands, fichier "FULL_DATABASE"
"""
# Importer les librairies
import numpy as np
import pandas as pd
import bokeh
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, HoverTool, Whisker, NumeralTickFormatter, Button, CustomJS
from bokeh.models.widgets import CheckboxGroup, DataTable, TableColumn, Div
from bokeh.layouts import row, WidgetBox, column, gridplot

# Importer les donnees depuis Excel dans un dataframe pandas
# Depuis la maison :
df = pd.read_excel (r'C:\Users\cgaro\Desktop\TRAVAIL\FULL_DATABASE.xlsx', sheet_name='Data', index_col='Molecule')
# Depuis le taf :
#df = pd.read_excel (r'C:\Users\clementine.garoche\Desktop\TRAVAIL\FULL_DATABASE.xlsx', sheet_name='Data', index_col='Molecule')

# Transformer le df en pivot table avec calcul des mean et std
df_pivot_table = pd.pivot_table(df, 'moy', ['Molecule', 'Cell_line', 'Color', 'Mode', 'Serum', 'ConcM'], aggfunc= [np.mean, np.std])
# Reset les index de toutes les colonnes
df2 = df_pivot_table.reset_index()
# Remplacer valeurs max par nan (pour avoir gap dans lines)
df2 = df2.replace(50, np.nan)
# Creer une liste des concentrations sans duplicats, les ordonner puis les changer en objets
Conc = df2['ConcM'].tolist()
Conc2 = list(dict.fromkeys(Conc))
Conc2.sort()
Concentrations = list(map(str, Conc2))
# Remplacer le type de data des conc par du texte au lieu des nombres a cause de log scale qui deforme ss bars.
df2['ConcM'] = df2['ConcM'].astype('str')
# Pour les barres d'erreur, ajouter 1 col mean + sd et 1 col mean - sd.
df2['sd_upper'] = (df2['mean', 'moy'] + df2['std', 'moy'])
df2['sd_lower'] = (df2['mean', 'moy'] - df2['std', 'moy'])
# Arrondir a 3 decimales
df2 = df2.round(3)

# Convert dataframe to column data source
# Une df sans donnees pour afficher un graph vide a l'ouverture de l'appli
source = ColumnDataSource(df2.head(0))
#source.data.keys()
# Pour chaque filtre, creer une serie de la longueur de df2 mais rempli de False.
# Ce dataframe sera remplace via la fonction correspondante a chaque filtre, par True pour les lignes selectionnees.
cl_selection = pd.Series(np.full(len(df2.index), False))
mol_selection = pd.Series(np.full(len(df2.index), False))
mode_selection = pd.Series(np.full(len(df2.index), False))
serum_selection = pd.Series(np.full(len(df2.index), False))


# Implementer la fonction cell_line_change
def cell_line_change(attr, old, new):
    global cl_selection
    cl_selection = pd.Series(np.full(len(df2.index), False))
    for selected in new:
        cl_selection |= (df2['Cell_line'] == Cell_lines[selected])
    by_Cell_line = df2.loc[cl_selection & mol_selection & mode_selection & serum_selection]
    new_source = ColumnDataSource(by_Cell_line)
    source.data.update(new_source.data)

# Implementer la fonction molecule_change
def Molecule_change(attr, old, new):
    global mol_selection
    mol_selection = pd.Series(np.full(len(df2.index), False))
    for selected in new:
        mol_selection |= (df2['Molecule'] == Molecules[selected])
    by_Molecule = df2.loc[cl_selection & mol_selection & mode_selection & serum_selection]
    new_source = ColumnDataSource(by_Molecule)
    source.data.update(new_source.data)

# Implementer la fonction mode_change
def Mode_change(attr, old, new):
    global mode_selection
    mode_selection = pd.Series(np.full(len(df2.index), False))
    for selected in new:
        mode_selection |= (df2['Mode'] == Modes[selected])
    by_Mode = df2.loc[cl_selection & mol_selection & mode_selection & serum_selection]
    new_source = ColumnDataSource(by_Mode)
    source.data.update(new_source.data)

# Implementer la fonction serum_change
def Serum_change(attr, old, new):
    global serum_selection
    serum_selection = pd.Series(np.full(len(df2.index), False))
    for selected in new:
        serum_selection |= (df2['Serum'] == Serums[selected])
    by_Serum = df2.loc[cl_selection & mol_selection & mode_selection & serum_selection]
    new_source = ColumnDataSource(by_Serum)
    source.data.update(new_source.data)
    

# Implementer la fonction make_plot1 pour les barres
def make_plot1(source) :
    #Creer graph vide
    p1 = figure(plot_height = 400, plot_width = 600, 
           title = 'Bars',
           x_axis_label = 'Conc (M)', x_range=(Concentrations),
           y_axis_label = 'Luciferase activity', y_range=(0,1.2))
    #Creer les barres
    p1.vbar(top='mean_moy', x='ConcM_', width=1, color='Color_', source=source, legend= 'Cell_line_',
            fill_alpha=0.4, hover_fill_color = 'Color_', hover_fill_alpha = 1.0, line_color = 'black')
    p1.legend.location = "top_left"
    p1.xaxis.major_label_orientation = "vertical"
    p1.yaxis.formatter = NumeralTickFormatter(format='0 %')
    p1.add_layout(Whisker(source=source, base ='ConcM_', lower = 'mean_moy', upper = 'sd_upper_', line_width=0.7))
    p1.xgrid.visible = False
    p1.ygrid.visible = False
    # Add a hover tool referring to the formatted columns
    hover = HoverTool(tooltips =[('Cell_line', '@Cell_line_'),
                             ('Molecule', '@Molecule_'),
                             ('Mode', '@Mode_'),
                             ('Serum', '@Serum_'),
                             ('ConcM', '@ConcM_'),
                             ('Mean', '@mean_moy{%F}'),
                             ('sd', '@std_moy{%F}')])
    # Add the hover tool to the graph
    p1.add_tools(hover)
    return p1
p1 = make_plot1(source)

# Implementer la fonction make_plot2 pour les lignes
def make_plot2(source) :
    #Creer graph vide
    p2 = figure(plot_height = 400, plot_width = 600, 
           title = 'Lines',
           x_axis_label = 'Conc (M)', x_range=(Concentrations),
           y_axis_label = 'Luciferase activity', y_range=(0,1.2))
    #Creer les lignes
    p2.line(y='mean_moy', x='ConcM_', line_width=1, source=source, color='black')
    p2.circle(y='mean_moy', x='ConcM_', source=source, legend= 'Molecule_', color='Color_', size=6)
    p2.legend.location = "top_left"
    p2.xaxis.major_label_orientation = "vertical"
    p2.yaxis.formatter = NumeralTickFormatter(format='0 %')
    p2.add_layout(Whisker(source=source, base ='ConcM_', lower ='sd_lower_', upper = 'sd_upper_', line_width=0.7))
    p2.xgrid.visible = False
    p2.ygrid.visible = False
    # Add a hover tool referring to the formatted columns
    hover = HoverTool(tooltips =[('Cell_line', '@Cell_line_'),
                             ('Molecule', '@Molecule_'),
                             ('Mode', '@Mode_'),
                             ('Serum', '@Serum_'),
                             ('ConcM', '@ConcM_'),
                             ('Mean', '@mean_moy{%F}'),
                             ('sd', '@std_moy{%F}')])
    # Add the hover tool to the graph
    p2.add_tools(hover)
    return p2
p2 = make_plot2(source)

def make_table(source):
    table_columns = [TableColumn(field='Molecule_', title='Molecule', width=100),
					 TableColumn(field='Cell_line_', title='Cell line', width=100),
					 TableColumn(field='Mode_', title='Mode', width=50),
					 TableColumn(field='Serum_', title='Serum', width=50),
					 TableColumn(field='ConcM_', title='Conc (M)', width=60),
					 TableColumn(field='mean_moy', title='mean', width=50, formatter=percentformat),
                     TableColumn(field='std_moy', title='sd', width=50, formatter=percentformat)]
    
    Data_table = DataTable(source=source, columns=table_columns, fit_columns=False, height = 800, width = 510)
    return Data_table

# Formater mean et sd de la table
percentformat = bokeh.models.NumberFormatter(format='0%')

#Creer les controles et leur interactivite
# Cell_lines is a list of all cell lines in the data
Cell_lines = ['HG5LN', 'HG5LN-hPPARa', 'HG5LN-mPPARa', 'HG5LN-hPPARg', 'HG5LN-mPPARg', 'HG5LN-zfPPARg', 'HELN-xPPARg', 'HG5LN-hPXR', 'HG5LN-mPXR', 'HG5LN-zfPXR', 'ZFL-zfPXR']
#Cell_lines = list(df2['Cell_line'].unique())
Cell_line_selection = CheckboxGroup(labels=Cell_lines)
Cell_line_selection.on_change('active', cell_line_change)

# Modes is a list of all modes in the data
Modes = list(df2['Mode'].unique())
Mode_selection = CheckboxGroup(labels=Modes)
Mode_selection.on_change('active', Mode_change)

# Modes is a list of all modes in the data
Serums = list(df2['Serum'].unique())
Serum_selection = CheckboxGroup(labels=Serums)
Serum_selection.on_change('active', Serum_change)

# Molecules is a list of all molecules in the data
Molecules = list(df2['Molecule'].unique())
Molecule_selection = CheckboxGroup(labels=Molecules)
Molecule_selection.on_change('active', Molecule_change)

# Titre des controles
Cell_line_title = Div(text="""<b>Cell line</b>""")
Mode_title = Div(text="""<b>Mode</b>""")
Serum_title = Div(text="""<b>Serum</b>""")
Molecule_title = Div(text="""<b>Molecule</b>""")

# Creer widgetbox des controles
Box1 = WidgetBox(Cell_line_title, Cell_line_selection, Mode_title, Mode_selection, Serum_title, Serum_selection)
Box2 = WidgetBox(Molecule_title, Molecule_selection)

# Creer bouton pour dl les donnees de DataTable
callback = CustomJS(args=dict(source=source), code="""
var data = source.data;
var filetext = 'Molecule_, Cell_line_, Mode_, Serum_, ConcM_, mean_moy, std_moy\\n';

for (i=0; i < data['Molecule_'].length; i++) {
	var currRow = [data['Molecule_'][i].toString(),
                    data['Cell_line_'][i].toString(),
                    data['Mode_'][i].toString(),
                    data['Serum_'][i].toString(),
                    data['ConcM_'][i].toString(),
                    data['mean_moy'][i].toString(),
                    data['std_moy'][i].toString().concat('\\n')];
	var joined = currRow.join();
	filetext = filetext.concat(joined);
}	

var filename = 'data.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

//addresses IE
if (navigator.msSaveBlob) {
	navigator.msSaveBlob(blob, filename);
}

else {
	var link = document.createElement("a");
	link = document.createElement('a')
	link.href = URL.createObjectURL(blob);
	link.download = filename
	link.target = "_blank";
	link.style.visibility = 'hidden';
	link.dispatchEvent(new MouseEvent('click'))
}
""")

button = Button(label='Download', button_type='success', callback=callback)

# Arranger les widgets et plots
Col1 = column(Box1, width = 150)    
Col2 = column(Box2, width = 200, height = 800, css_classes=['scrollable'])
Col4 = column(button, make_table(source))
grid = gridplot([[p1], [p2]], toolbar_location='left')
grid.children[1].css_classes = ['scrollable']
grid.children[1].height = 800
grid.children[1].width = 600
grid.children[1].sizing_mode = 'fixed'

# Mettre dans current doc
curdoc().add_root(row(Col1, Col2, grid, Col4))
curdoc().title = "Molecules"

# POSSIBLE IMPROVEMENTS:
# Resoudre pb des lines, p.multi_lines ?
# Ou plutot, a chaque fois qu'un nouveau source est cree, le transformer en df :
# avec ce type de cmd :
# print(max(source.data['mean_moy']))
# print(source.data['ConcM_'])
# faire groupby, passer en columndatasource, les plot en multi line ?

# Pouvoir cocher/decocher tout

# Add model Hill Algorithme de Levenberg-Marquardt : SciPy ?