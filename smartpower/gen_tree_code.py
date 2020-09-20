import pandas as pd
import math
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.model_selection import train_test_split # Import train_test_split function
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation

from sklearn.tree import export_graphviz
from sklearn.externals.six import StringIO  
from IPython.display import Image  
import pydotplus

import numpy as np

#col_names = ['freq', 'core_num', 'cluster', 'ipc', 'instructions', 'cycles', 'cache_misses', 'wall', 'user', 'sys', 'mapping_label']
col_names = ['freq', 'cluster', 'instr', 'cycles', 'cache_misses', 'mapping_label']

mappings = pd.read_csv("edp_mappings.csv", header=None, names=col_names)

#print(mappings.head())

feature_cols = col_names[:-1]
X = mappings[feature_cols]
y = mappings.mapping_label

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1) # 70% training and 30% test

# Create Decision Tree classifer object
#can apply a max depth if needed for runtime performance
clf = DecisionTreeClassifier()

# Train Decision Tree Classifer
clf = clf.fit(X_train,y_train)

n_nodes = clf.tree_.node_count
children_left = clf.tree_.children_left
children_right = clf.tree_.children_right
feature = clf.tree_.feature
threshold = clf.tree_.threshold
value = clf.tree_.value

#classes = clf.classes_
#print(classes)

#classes = clf.classes_
#print(classes)
#print(feature)

node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
is_leaves = np.zeros(shape=n_nodes, dtype=bool)
stack = [(0, -1)]  # seed is the root node id and its parent depth
while len(stack) > 0:
    node_id, parent_depth = stack.pop()
    node_depth[node_id] = parent_depth + 1

    # If we have a test node
    if (children_left[node_id] != children_right[node_id]):
        stack.append((children_left[node_id], parent_depth + 1))
        stack.append((children_right[node_id], parent_depth + 1))
    else:
        is_leaves[node_id] = True


for i in range(n_nodes):
    if is_leaves[i]:
        the_value = value[i]
        the_label = clf.classes_[np.argmax(the_value)]
        #print("%snode=%s leaf node of value %s" % (node_depth[i] * "\t", i, the_label))

        print("NODE_"+str(i)+":")
        #print("%s%s%s%s" % ("return ", "\"",the_label, "\";"))
        print("%s%s%s%s" % ("return ", "\"",the_label, "\";"))

    else:
        #print("%snode=%s test node: go to node %s if X[:, %s] aka %s <= %s else to "
        #      "node %s."
        #      % (node_depth[i] * "\t",
        #         i,
        #         children_left[i],
        #         feature[i],
        #         str(feature_cols[feature[i]]),
        #         threshold[i],
        #         children_right[i],
        #         ))

        feat_name = str(feature_cols[feature[i]])
        print("NODE_"+str(i)+":")
        print("%s%s%s%s%s" % ("if (", feat_name, " <= ", math.floor(threshold[i]), ") {"))
        print("\tgoto NODE_"+str(children_left[i])+";")
        print("} else {")
        print("\t goto NODE_"+str(children_right[i])+";")
        print("}")


print("EXIT_LABEL:\nreturn \"-1\";")#this should never happen

#Predict the response for test dataset
#y_pred = clf.predict(X_test)


#print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
#dot_data = StringIO()
#export_graphviz(clf, out_file=dot_data,  
#                filled=True, rounded=True,
#                special_characters=True,feature_names = feature_cols,class_names=col_names[-1])
#graph = pydotplus.graph_from_dot_data(dot_data.getvalue())  
#graph.write_png('edp_dec_tree.png')
#Image(graph.create_png())
