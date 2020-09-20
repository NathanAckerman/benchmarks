import pandas as pd
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.model_selection import train_test_split # Import train_test_split function
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation

from sklearn.tree import export_graphviz
from sklearn.externals.six import StringIO  
from IPython.display import Image  
import pydotplus

#col_names = ['freq', 'core_num', 'cluster', 'ipc', 'instructions', 'cycles', 'cache_misses', 'wall', 'user', 'sys', 'mapping_label']
#col_names = ['freq', 'cluster', 'ipc', 'cache_per_cycle', 'cache_per_wall', 'cache_per_cpu', 'mapping_label']
col_names = ['freq', 'cluster', 'instr', 'cycles', 'cache_misses', 'mapping_label']

mappings = pd.read_csv("edp_mappings.csv", header=None, names=col_names)

#print(mappings.head())

feature_cols = col_names[:-1]
X = mappings[feature_cols]
y = mappings.mapping_label

#skipping test/train but need to come back to this when there is more data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1) # 70% training and 30% test
#X_train = X_test = X
#y_train = y_test = y

# Create Decision Tree classifer object
#can apply a max depth if needed for runtime performance
clf = DecisionTreeClassifier()

# Train Decision Tree Classifer
clf = clf.fit(X_train,y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)

print("Accuracy:",metrics.accuracy_score(y_test, y_pred))


dot_data = StringIO()
export_graphviz(clf, out_file=dot_data,  
                filled=True, rounded=True,
                #special_characters=True,feature_names = feature_cols,class_names=['0','1'])
                special_characters=True,feature_names = feature_cols,class_names=col_names[-1])
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())  
graph.write_png('edp_dec_tree.png')
Image(graph.create_png())
